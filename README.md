# Java Tutor RAG Project

A local RAG (Retrieval-Augmented Generation) system for helping students with Java homework. It uses LangChain, Ollama (Llama 3), and FAISS.

## Features
- **Local & Private**: Uses Llama 3 running locally via Ollama. No data leaves your machine.
- **RAG Powered**: Retrieves context from `data/lessons.txt`, `data/assignments.txt`, and `data/sampleSolutions.txt`.
- **Persistent Index**: FAISS index is saved to disk for fast startups.
- **Interactive Web App**: Modern chat interface with streaming, powered by Streamlit.
- **Guardrails**: System prompt prevents generating full code solutions (verified via Red Teaming).

## Setup

1.  **Install Ollama**: [Download here](https://ollama.com).
2.  **Pull Model**:
    ```powershell
    ollama pull llama3
    ```
3.  **Install Python Dependencies**:
    ```powershell
    pip install langchain langchain-community langchain-core langchain-huggingface faiss-cpu sentence-transformers rich streamlit
    ```

## Usage

### Web Interface (Recommended)
Run the streaming web app:
```powershell
streamlit run src/app.py
```

### CLI Mode
Chat in the terminal:
```powershell
python src/tutor.py
```

### Batch Evaluation
Process input scenarios:
```powershell
python src/evaluator.py
```

### Safety Testing (Red Teaming)
Verify that the AI refuses to give code solutions:
```powershell
python src/red_team.py
```

## Directory Structure
- `data/`: Course material and FAISS index.
- `src/`:
    - `app.py`: Streamlit web application.
    - `rag.py`: Core RAG logic.
    - `tutor.py`: Terminal CLI.
    - `red_team.py`: Safety verification script.
    - `evaluator.py`: Batch processor.
- `results/`: Reports (`evaluation.md`, `red_team_report.md`).