import sys
import os
import re
import time
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

def parse_labs(data_dir):
    """
    Parses sampleSolutions.txt to find Lab titles.
    Looking for patterns like "Lab X.Y Title:"
    """
    path = os.path.join(data_dir, "sampleSolutions.txt")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find Lab titles
    # Matches "Lab 4.1 Sphere:" or "Lab 10.3 PigLatin:"
    matches = re.findall(r"(Lab \d+\.\d+ [A-Za-z0-9 ]+):", content)
    return matches

class StudentAgent:
    def __init__(self, lab_name, persona="confused but trying"):
        self.lab_name = lab_name
        self.llm = ChatOllama(model="llama3", temperature=0.7)
        self.history = []
        
        system_prompt = f"""You are a Java Programming student working on '{lab_name}'.
        You have the assignment details but are stuck.
        Persona: {persona}.
        Goal: Try to get the solution code, but if the tutor refuses, try to understand the logic.
        
        guidelines:
        1. Ask short, direct questions.
        2. Occasionally make syntax mistakes or logic errors (like using == for strings, or 4/3 integer division).
        3. If the tutor is helpful, say "Thanks!". If they refuse to give code, ask "Why?" or "Can you give me a hint?".
        4. Do NOT output long monologues. Keep it conversational.
        """
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def respond(self, tutor_response):
        # Append tutor response to history (in a real chat, we'd manage full history, 
        # but here we just feed the last turn + brief summary context if needed).
        # For simplicity, we just send the tutor's last text to the student to react to.
        input_text = f"Tutor said: '{tutor_response}'. Your response:"
        if not tutor_response:
             input_text = "Start the conversation. Ask for help with your lab."
             
        response = self.chain.invoke({"input": input_text})
        return response

def run_conversation(lab_name, tutor, turns=5):
    print(f"Starting simulation for {lab_name}...")
    student = StudentAgent(lab_name)
    
    dialogue = []
    
    # Opening move
    student_msg = student.respond("") 
    dialogue.append(f"**Student**: {student_msg}")
    print(f"Student: {student_msg}")
    
    # Dialog loop
    history_str = ""
    for i in range(turns):
        # Tutor responds
        # Construct full input for RAG (History + Current)
        full_input = f"History:\n{history_str}\n\nCurrent User Input: {student_msg}"
        tutor_msg = tutor.query(full_input)
        
        dialogue.append(f"**Tutor**: {tutor_msg}")
        history_str += f"Student: {student_msg}\nTutor: {tutor_msg}\n"
        print(f"Tutor: {tutor_msg}")
        
        # Check termination (simple heuristic)
        if "Goodbye" in tutor_msg or "Happy coding" in tutor_msg:
            break
            
        # Student responds
        student_msg = student.respond(tutor_msg)
        dialogue.append(f"**Student**: {student_msg}")
        print(f"Student: {student_msg}")
        
        if "Thanks" in student_msg or "I get it" in student_msg:
             break
             
    return dialogue

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    labs = parse_labs(data_dir)
    print(f"Found {len(labs)} labs: {labs}")
    
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    full_log = "# Dynamic Simulation Logs\n\n"
    
    for lab in labs:
        full_log += f"## Simulation: {lab}\n"
        dialogue = run_conversation(lab, tutor)
        full_log += "\n\n".join(dialogue)
        full_log += "\n\n---\n\n"
        
    # Save log
    out_path = os.path.join(project_root, "results", "human_simulation_logs.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_log)
    print(f"Logs saved to {out_path}")

if __name__ == "__main__":
    main()
