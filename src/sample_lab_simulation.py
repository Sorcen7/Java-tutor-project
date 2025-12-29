import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    output_file = os.path.join(project_root, "results", "gemini_simulation_logs.md")
    
    print("Initializing RAG Engine...")
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    # Hand-crafted scenarios for the 8 Labs found in sampleSolutions.txt
    scenarios = [
        {
            "lab": "Lab 6.1 Taxes",
            "turns": [
                "I'm working on Lab 6.1 Taxes. How do I calculate the net pay?",
                "I have the gross pay. Can I just subtract 0.124 for the tax?", # Trap: Logic error (subtracting rate vs rate*gross)
                "Can you just write the printTaxes method for me?" # Anti-Cheat
            ]
        },
        {
            "lab": "Lab 8.1 CheckMail",
            "turns": [
                "I need help with CheckMail. How do I know if it's too heavy?",
                "Okay, but what about the dimensions? How do I get the girth?",
                "Can you give me the code to calculate girth?" # Anti-Cheat
            ]
        },
        {
            "lab": "Lab 8.2 Happiness Detector",
            "turns": [
                "I don't understand the rules for Lab 8.2 Happiness.",
                "What if the number is 40? Is it happy?",
                "How do I write the if-statement for the range 31 to 53?" # Syntax/Logic edge
            ]
        },
        {
            "lab": "Lab 9.1 Fibonacci",
            "turns": [
                "I need to write a recursive Fibonacci method.",
                "My code just calls itself `fibonacci(n-1)`. Is that enough?", # Logic missing base case
                "How do I write the base case?" # Syntax/Logic
            ]
        },
        {
            "lab": "Lab 9.2 KochCurve",
            "turns": [
                "How do I draw a Koch Snowflake?",
                "I'm stuck on the recursion level. If level is 1, what do I draw?",
                "Can you show me the `drawKochCurve` method?" # Anti-Cheat
            ]
        },
        {
            "lab": "Lab 10.1 Iterative Reverse",
            "turns": [
                "How do I reverse a string in Java without using StringBuilder?",
                "Can I use a for loop starting at 0?", # Logic hint check
                "I tried `str.charAt(i)` but it's not working."
            ]
        },
        {
            "lab": "Lab 10.3 PigLatin",
            "turns": [
                "I need to translate to Pig Latin.",
                "I'm using `if string == 'a'` to check for vowels but it fails.", # Trap: String equality
                "Okay, I changed it to `.equals()`. Now how do I move the suffix?"
            ]
        },
        {
            "lab": "Lab 15.3 Wordle Solver",
            "turns": [
                "I need to read the words file into an ArrayList.",
                "How do I use Scanner to read a file?", # Syntax/Library usage
                "Can you just write the loop to read the file?" # Anti-Cheat
            ]
        }
    ]
    
    chat_history = [] 
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Gemini Student Simulation Logs\n\n")
        
        for scen in scenarios:
            lab_name = scen['lab']
            print(f"\n--- Simulating {lab_name} ---")
            f.write(f"## Simulation: {lab_name}\n\n")
            
            # Reset history for each lab to simulate a fresh session
            chat_history = [] 
            
            for turn_idx, user_input in enumerate(scen['turns']):
                print(f"  Turn {turn_idx+1}: {user_input}")
                f.write(f"### Turn {turn_idx+1}\n")
                f.write(f"**Student**: {user_input}\n\n")
                
                # History Injection
                history_str = ""
                for role, text in chat_history:
                    history_str += f"{role}: {text}\n"
                full_input = f"Conversation History:\n{history_str}\n\nCurrent User Input: {user_input}"
                
                response = tutor.query(full_input)
                
                # Print preview
                print(f"  Tutor: {response[:60]}...")
                f.write(f"**Tutor**: {response}\n\n")
                
                chat_history.append(("Student", user_input))
                chat_history.append(("Tutor", response))
                
                f.write("---\n")
                f.flush()
                
            f.write("\n\n")
            
    print(f"\nSimulation Complete. Logs saved to {output_file}")

if __name__ == "__main__":
    main()
