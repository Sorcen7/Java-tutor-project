import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class JavaTutorRAG:
    def __init__(self, data_dir="data", model_name="llama3"):
        self.data_dir = data_dir
        self.model_name = model_name
        self.embedding_model = "all-MiniLM-L6-v2"
        self.rag_chain = None
        self.build_chain()

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
            # allow_dangerous_deserialization is needed because pickle can be unsafe, 
            # but here we trust our own local file.
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
        llm = ChatOllama(model=self.model_name, temperature=0.7)

        system_prompt = (
            "You are a Socratic Java Tutor. Your goal is to guide the student to the answer, providing support ONLY when needed.\n"
            "PEDAGOGY GUIDELINES:\n"
            "1. **Assess first**: If the user's question is vague, ask clarifying questions to gauge their understanding.\n"
            "2. **Scaffolding**: If the student tries and fails, or admits they are stuck, provide a **small foothold**. Don't just ask another open-ended question. Give them a concrete starting point.\n"
            "3. **Maintain Momentum**: If the student correctly identifies the next step (e.g., \"I need a constructor\"), CONFIRM it and guide them on HOW to do it. Do not force them to brainstorm unrelated features.\n"
            "4. **Syntax vs Logic**: You MAY explain standard Java syntax (e.g., \"A constructor looks like public ClassName() {{ }}\"). You MUST NOT write the specific logic for the lab inside it.\n"
            "5. **No Spoon-feeding**: NEVER provide the full code solution.\n"
            "6. **Validation**: If they get part of it right, praise that specific part before moving to the next hurdle.\n"
            "\n"
            "INTERACTION STYLE:\n"
            "- **Address the user directly as 'You'**. NEVER refer to them as 'the student'.\n"
            "- Be empathetic. Programming is hard.\n"
            "- END EVERY TURN WITH A CONCRETE NEXT STEP OR QUESTION.\n"
            "\n"
            "Context: {context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        self.rag_chain = (
            {"context": retriever | self.format_docs, "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("RAG System Ready.")

    def query(self, user_input):
        if not self.rag_chain:
            return "Error: RAG system not initialized."
        try:
            return self.rag_chain.invoke(user_input)
        except Exception as e:
            return f"Error encountered: {e}"
