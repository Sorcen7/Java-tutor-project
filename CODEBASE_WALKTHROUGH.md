# Deep-Dive Codebase Logic Walkthrough

This document explains the codebase line-by-line, focusing on **data flow**, **function specifications**, and **implementation details**. It is designed to help a developer reconstruct this logic or adapt the components for their own RAG system.

---

## Core Engine: `src/rag.py`

This file contains the `JavaTutorRAG` class, which orchestrates the entire Retrieval-Augmented Generation pipeline.

### 1. Initialization (`__init__`)

```python
class JavaTutorRAG:
    def __init__(self, data_dir="data", model_name="llama3"):
        self.data_dir = data_dir
        self.model_name = model_name
        self.embedding_model = "all-MiniLM-L6-v2"
        self.rag_chain = None
        self.build_chain()
```
-   **Inputs**: `data_dir` (path to text files), `model_name` (Ollama model tag).
-   **State**: Sets the embedding model name to `all-MiniLM-L6-v2`. This is a specific HuggingFace model optimized for sentence similarity.
-   **Action**: Calls `self.build_chain()` immediately to set up the system.

### 2. Document Loading (`load_documents`)

```python
def load_documents(self):
    # ... (path construction logic) ...
    loader = TextLoader(path, encoding='utf-8')
    docs.extend(loader.load())
```
-   **Component**: `langchain_community.document_loaders.TextLoader`
-   **Input**: A file path string (e.g., `data/lessons.txt`) and encoding.
-   **Internal Logic**: Opens the file, reads the entire content into a string.
-   **Output**: A list of `Document` objects.
    -   **Structure**: `[Document(page_content="...file text...", metadata={"source": "path"})]`
-   **Why**: We need to wrap raw text in an object that carries metadata (source filename) so we know where the info came from later.

### 3. The Build Process (`build_chain`)

This method constructs the processing pipeline. It handles **Persistence** and **Chaining**.

#### Step A: Embeddings & Persistence Check
```python
embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
vector_store_path = os.path.join(self.data_dir, "faiss_index")
```
-   **Component**: `HuggingFaceEmbeddings`
    -   **Input**: Any string.
    -   **Internal**: Loads a specific pre-trained neural network (MiniLM) from local cache.
    -   **Output**: A vector (list of float32 numbers) representing the semantic meaning of that string.

#### Step B: Vector Store Construction (FAISS)
**Scenario 1: Index Exists (Fast Load)**
```python
if os.path.exists(vector_store_path):
    vectorstore = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
```
-   **Function**: `FAISS.load_local`
-   **Input**: Directory path, the embedding function object.
-   **Internal**: Reads `.faiss` (binary index) and `.pkl` (metadata) files. Reconstructs the search index in RAM.
-   **Output**: A `FAISS` object ready for similarity search.

**Scenario 2: New Index (Build)**
```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
```
-   **Component**: `RecursiveCharacterTextSplitter`
-   **Input**: List of `Document` objects (from `load_documents`).
-   **Internal**:
    1.  Iterates through `page_content`.
    2.  Attempts to break text at semantic boundaries (paragraphs `\n\n`, then sentences `\n`, then spaces).
    3.  Ensures no chunk exceeds `1000` characters.
    4.  Keeps `200` characters of overlap (the end of Chunk A is the start of Chunk B) to preserve context across cuts.
-   **Output**: A much larger list of `Document` objects (e.g., 1 file becomes 50 chunks).

```python
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
vectorstore.save_local(vector_store_path)
```
-   **Function**: `FAISS.from_documents`
-   **Input**: List of split Documents, Embedding Function.
-   **Output**: A generic `VectorStore` interface.

#### Step C: The Retriever
```python
retriever = vectorstore.as_retriever()
```
-   **Input**: The built `vectorstore`.
-   **Internal**: Creates a `VectorStoreRetriever` wrapper.
-   **Specification**: When Invoked, it will:
    1.  Embed the query.
    2.  Perform a "k-Nearest Neighbors" search (default k=4).
    3.  Return the top 4 most similar text chunks.

#### Step D: The LLM & Prompt
```python
llm = ChatOllama(model=self.model_name, temperature=0.7)
```
-   **Component**: `ChatOllama`
-   **Input**: A prompt string.
-   **Internal**: Makes an HTTP POST request to `http://localhost:11434/api/chat`.
-   **Output**: A `AIMessage` object.

```python
prompt = ChatPromptTemplate.from_messages(...)
```
-   **Logic**: Defines a template string using `{context}` and `{input}` placeholders.

#### Step E: The Implementation Chain (LCEL)
This is the most critical logic flow, using **LangChain Expression Language**:

```python
self.rag_chain = (
    {"context": retriever | self.format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

**Line-by-Line Execution Flow**:
1.  **Input**: The chain receives a string (e.g., "How do I write a class?").
2.  **Parallel Branching (`{...}`)**:
    -   **Right Branch (`"input"`)**: `RunnablePassthrough()` takes the input string and passes it through unchanged.
    -   **Left Branch (`"context"`)**:
        -   The input string is passed to `retriever`.
        -   `retriever` finds 4 relevant Text Chunks.
        -   `| self.format_docs`: A helper function joins these 4 chunks into one giant string.
3.  **Prompting (`| prompt`)**: The dictionary `{"context": "...", "input": "..."}` is passed to the template.
4.  **Inference (`| llm`)**: The constructed prompt is sent to Ollama.
5.  **Parsing (`| StrOutputParser`)**: Extracts just the text string from the response.

### 4. Query Execution (`query`)

```python
def query(self, user_input):
    return self.rag_chain.invoke(user_input)
```
-   **Function**: `invoke` runs the entire chain synchronously.

---

## User Interface: `src/app.py`

This script handles the web presentation using **Streamlit**.

### 1. Caching Resource
```python
@st.cache_resource
def get_tutor():
    return JavaTutorRAG(data_dir=data_dir)
```
-   **Logic**: `JavaTutorRAG` takes time to load. `@st.cache_resource` ensures this runs **only once** per server start.

### 2. The Stream Loop
```python
if tutor.rag_chain:
    stream = tutor.rag_chain.stream(prompt)
    for chunk in stream:
        full_response += chunk
        message_placeholder.markdown(full_response + "▌")
```
-   **Input**: `prompt` (User question).
-   **Function**: `rag_chain.stream(prompt)`.
    -   Unlike `invoke`, this keeps the HTTP connection to Ollama open.
    -   Ollama sends back partial tokens (e.g., "Hel", "lo").
-   **Loop**: Appends tokens and updates the UI instantly for a "typing" effect.

---

## Command Line Interface: `src/tutor.py`

This script provides a terminal-based way to chat.

### The Loop
```python
while True:
    if print_formatted:
        user_input = console.input("[bold green]User>[/bold green] ")
    else:
        user_input = input("User> ")
    # ...
    response = tutor.query(user_input)
    print_response(response)
```
-   **Logic**: A standard infinite loop.
-   **Dependencies**: Uses `rich` library if installed for colored output.
-   **Exit**: Checks for `/quit`.

---

## Batch Processor: `src/evaluator.py`

This script grades the AI by running it against `data/input.txt`.

### 1. Data Parsing (`parse_labs_file`)
```python
def parse_labs_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('Lab '):
                # Found a new lab
                if current_lab: labs.append(current_lab)
                current_lab = {'name': line.split(':')[0]}
            elif line.startswith('Incorrect Solution:'):
                current_lab['incorrect_solution'] = []
            elif current_lab.get('incorrect_solution') is not None:
                # Capture bad code lines
                current_lab['incorrect_solution'].append(line)
```
-   **Input**: Custom text file format.
-   **Logic**: State machine loop. It reads line-by-line and switches mode when it sees headers like "Lab" or "Incorrect Solution".
-   **Output**: List of dictionaries representing each lab scenario.

### 2. Execution Loop
```python
for i, task in enumerate(tasks):
    answer = tutor.query(task['prompt'])
    f.write(f"## {task['title']}\n\n")
    f.write(f"{answer}\n\n")
    f.flush()
```
-   **Critical**: `f.flush()` forces the OS to write buffer to disk immediately, preventing data loss if the script is interrupted.

---

## Security Verification: `src/red_team.py`

Verifies that "Socratic" guardrails are working.

```python
test_cases = [ "Write the full solution...", "Give me code..." ]
# ...
response = tutor.query(prompt)
# ...
refusal_keywords = ["cannot", "won't", "guide", "plan"]
```
-   **Logic**: Sends adversarial prompts. Heuristically checks if "refusal words" appear in the response.
