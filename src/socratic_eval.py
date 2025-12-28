import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    output_file = os.path.join(project_root, "results", "socratic_report.md")
    
    print("Initializing Socratic Tutor for Evaluation...")
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    scenarios = [
        {
            "type": "Vague Request",
            "prompt": "I'm stuck on Lab 15.3 Wordle. I don't know where to start.",
            "expected": "Should ask what I understand about the rules or file I/O."
        },
        {
            "type": "Conceptual Misconception",
            "prompt": "I tried `int x = 5.5;` but it gives an error. Why? Java is broken.",
            "expected": "Should explain types (int vs double) and ask me how to store decimals."
        },
        {
            "type": "Direct Code Request",
            "prompt": "Just give me the code for the Sphere class in Lab 4.1. I'm late.",
            "expected": "Should refuse and ask me what attributes a Sphere has."
        },
        {
            "type": "Logic Help",
            "prompt": "My loop `for(int i=0; i<10; i--)` runs forever. Can you fix it?",
            "expected": "Should ask me to trace the value of `i`."
        }
    ]
    
    print(f"Running {len(scenarios)} pedagogical scenarios...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Socratic Persona Evaluation Report\n\n")
        f.write("Evaluating if the tutor asks questions and guides rather than telling.\n\n")
        
        for i, scen in enumerate(scenarios):
            print(f"Testing Scenario {i+1}: {scen['type']}...")
            response = tutor.query(scen['prompt'])
            
            f.write(f"## Scenario {i+1}: {scen['type']}\n")
            f.write(f"**Student**: {scen['prompt']}\n\n")
            f.write(f"**Tutor Response**:\n{response}\n\n")
            f.write(f"**Expected Behavior**: {scen['expected']}\n")
            
            # Heuristic Analysis
            has_question = "?" in response
            length = len(response.split())
            is_concise = length < 150
            
            f.write(f"**Analysis**:\n")
            f.write(f"- Ended with question? {'YES' if has_question else 'NO'}\n")
            f.write(f"- Concise? ({length} words) {'YES' if is_concise else 'NO'}\n")
            f.write("---\n\n")
            f.flush()
            
    print(f"Evaluation Complete. Check results in {output_file}")

if __name__ == "__main__":
    main()
