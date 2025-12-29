import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

class JavaTutorRAG:
    def __init__(self, data_dir="data", model_name="llama3"):
        self.data_dir = data_dir
        self.model_name = model_name
        self.embedding_model = "all-MiniLM-L6-v2"
        self.rag_chain = None
        self.store = {}  # Store for session histories
        self.build_chain()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def load_documents(self):
        print(f"Loading documents from {self.data_dir}...")
        file_names = ["lessons.txt", "assignments.txt", "sampleSolutions.txt"]
        docs = []
        for name in file_names:
            path = os.path.join(self.data_dir, name)
            if os.path.exists(path):
                try:
                    loader = TextLoader(path, encoding='utf-8')
                    docs.extend(loader.load())
                    print(f"  Loaded {name}")
                except Exception as e:
                    print(f"  Error loading {name}: {e}")
            else:
                print(f"  Warning: {name} NOT found in {self.data_dir}")
        return docs

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def build_chain(self):
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        vector_store_path = os.path.join(self.data_dir, "faiss_index")

        if os.path.exists(vector_store_path):
            print(f"Loading existing vector store from {vector_store_path}...")
            vectorstore = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        else:
            print("Creating new vector store...")
            docs = self.load_documents()
            if not docs:
                raise ValueError("No documents loaded. Please check data directory.")

            print("Splitting documents...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)

            print("Building and saving vector store...")
            vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
            vectorstore.save_local(vector_store_path)

        retriever = vectorstore.as_retriever()
        
        print(f"Initializing LLM ({self.model_name})...")
        llm = ChatOllama(model=self.model_name, temperature=0.1)

        system_prompt = (
            "You are a Socratic Java Tutor. Your goal is to teach the student HOW to think, not just how to code.\n"
            "\n"
            "*** CRITICAL INSTRUCTIONS ***\n"
            "1. **NO CODE DUMPING**: You are FORBIDDEN from generating full method bodies or complete logical solutions. If the context contains the answer, DO NOT COPY IT.\n"
            "2. **USE STUBS**: When showing code structure, you MUST use comments like `// logic goes here` or `// ...` for the critical parts.\n"
            "3. **ANTI-CHEAT**: If the user asks for the answer/code, REFUSE FIRMLY. Say: 'I cannot write the solution for you'.\n"
            "\n"
            "PEDAGOGY GUIDELINES (Deep Scaffolding):\n"
            "1. **ASSESS FIRST (Crucial)**: Before helping, mentally check: 'Does the student understand the basic concept?'. If the question is vague (e.g., 'I'm stuck'), ASK a targeted question to locate the gap BEFORE giving hints.\n"
            "2. **Syntax Help**: If asking for generic syntax (e.g. 'How do I make a loop?'), provide the template IMMEDIATELY.\n"
            "3. **Trap Detection**: If user writes `4/3` or `string == string`, CORRECT IT immediately.\n"
            "4. **Scaffolding**: Once the gap is found, give a **small foothold** (concept or partial snippet). Ask: 'What do you think happens next?'\n"
            "\n"
            "INTERACTION STYLE:\n"
            "- Address user as 'You'.\n"
            "- Be concise but encouraging.\n"
            "\n"
            "Context: {context}"
        )

        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        from operator import itemgetter
        
        # Fix chain to handle dict input from RunnableWithMessageHistory
        chain = (
            {
                "context": itemgetter("input") | retriever | self.format_docs,
                "input": itemgetter("input"),
                "history": itemgetter("history")
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Wrap with message history
        self.rag_chain = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        print("RAG System Ready (Native Memory Enabled).")

    def query(self, user_input, session_id="default_session"):
        if not self.rag_chain:
            return "Error: RAG system not initialized."
        try:
            return self.rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
        except Exception as e:
            return f"Error encountered: {e}"
