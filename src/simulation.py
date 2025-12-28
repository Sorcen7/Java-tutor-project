import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    output_file = os.path.join(project_root, "results", "simulation_report.md")
    
    print("Initializing Scaffolding Simulation...")
    # Initialize RAG
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    # Simulate a conversation where the user is STUCK
    # We can't really "maintain state" easily without a chat history variable in the RAG class 
    # (which we didn't implement fully for single-turn query method, but let's fake it by concatenating).
    # Wait, rag.py's query() calls invoke() on a chain. The chain has memory? No.
    # We need to pass history. Our define chain uses {input} and {context}. 
    # To simulate multi-turn, we can just append previous Q&A to the prompt.
    
    conversation = [
        ("Student", "I'm stuck on Lab 4.1. I don't know how to start the Sphere class."),
        # AI should ask a question
        ("Student", "I really don't know. Maybe it needs a radius?"),
        # AI should validate and give a next step
        ("Student", "Okay, how do I write the constructor?")
        # AI should give a syntax hint but not full code
    ]
    
    history_text = ""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Multi-Turn Scaffolding Simulation\n\n")
        f.write("Testing if the tutor adapts to a struggling student.\n\n")
        
        for role, text in conversation:
            if role == "Student":
                f.write(f"**Student**: {text}\n\n")
                print(f"Student: {text}")
                
                # Append to history for context
                # Ideally we pass this as 'chat_history' but our RAG chain is simple.
                # We'll just prepend it to the input string to hack it in.
                full_input = f"History:\n{history_text}\n\nCurrent User Input: {text}"
                
                response = tutor.query(full_input)
                
                f.write(f"**Tutor**: {response}\n\n")
                print(f"Tutor: {response}")
                
                history_text += f"Student: {text}\nTutor: {response}\n"
                
                f.write("---\n")
                f.flush()

    print(f"Simulation Complete. Check results in {output_file}")

if __name__ == "__main__":
    main()
