import streamlit as st
import sys
import os
import time

# Add src to path so we can import rag
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

st.set_page_config(page_title="Java Tutor AI", page_icon="☕")

# Cache the RAG engine so we don't reload FAISS on every interaction
@st.cache_resource
def get_tutor():
    # Helper to find data dir relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    return JavaTutorRAG(data_dir=data_dir)

st.title("☕ Java Tutor AI")
st.markdown("ask me anything about your Java labs! I can help you plan, debug, and understand concepts, but **I won't write the code for you**.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you with your Java assignment?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        tutor = get_tutor()
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Use the chain's stream method
            if tutor.rag_chain:
                # We need to manually invoke the stream. 
                # Note: The 'rag_chain' expects a string input if configured with RunnablePassthrough in previous steps,
                # or a dict if configured differently. Our rag.py uses RunnablePassthrough for 'input'.
                stream = tutor.rag_chain.stream(prompt)
                
                for chunk in stream:
                    # In LCEL, chunk from StrOutputParser is just a string
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                    
                message_placeholder.markdown(full_response)
            else:
                st.error("RAG System not initialized.")
                full_response = "Error: RAG System not initialized."

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")
