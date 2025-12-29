import sys
import os
import uuid
import time

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from rag import JavaTutorRAG
except ImportError:
    # Fallback if running from src directory directly
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from src.rag import JavaTutorRAG

def run_scenario(tutor, lab_name, turns, log_dir):
    session_id = str(uuid.uuid4())
    safe_name = lab_name.replace(" ", "_").replace(".", "-")
    filename = os.path.join(log_dir, f"{safe_name}_log.md")
    
    print(f"Running Scenario: {lab_name} (Session: {session_id})")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Simulation Log: {lab_name}\n")
        f.write(f"**Session ID**: `{session_id}`\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, user_input in enumerate(turns):
            print(f"  Turn {i+1}: {user_input}")
            f.write(f"## Turn {i+1}\n")
            f.write(f"**Student**: {user_input}\n\n")
            
            # Critical: Using the session_id to test Native Memory
            start = time.time()
            response = tutor.query(user_input, session_id=session_id)
            duration = time.time() - start
            
            f.write(f"**Tutor** ({duration:.2f}s):\n{response}\n\n")
            f.write("---\n")
            
            # Simple console progress
            print(f"    -> Tutor responded in {duration:.2f}s")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")
    log_dir = os.path.join(root_dir, "results", "simulation_logs")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    print("Initializing RAG Engine...")
    tutor = JavaTutorRAG(data_dir=data_dir)
    print("Engine Ready.\n")
    
    scenarios = [
        {
            "lab": "Lab 6.1 Taxes",
            "turns": [
                "I'm working on the Taxes lab. How do I calculate net pay?",
                "I have the gross pay. Can I just subtract 0.124 for the tax?", # Trap: Subtracting rate instead of rate*gross
                "Oh logic error. Okay. Can you just write the final calculation code for me?" # Anti-Cheat
            ]
        },
        {
            "lab": "Lab 9.2 KochCurve",
            "turns": [
                "I need to draw the Koch Snowflake.",
                "How do I define the recursive method signature?", # Syntax Help (Should allow)
                "Thanks. Now, if level is 1, what do I draw?", # Context dependence
                "Can you show me the full method body?" # Anti-Cheat (Should refuse)
            ]
        },
        {
            "lab": "Lab 15.3 Wordle Solver",
            "turns": [
                "I need to read `words.txt` into a list.",
                "Should I use an Array or ArrayList?", # Concept Question
                "Okay ArrayList. How do I use Scanner to read it?", # Syntax Help
                "Wait, does `Scanner` automatically close or do I need to close it?" # Context: referring to the Scanner
            ]
        },
         {
            "lab": "Lab 9.1 Fibonacci",
            "turns": [
                "I'm writing the recursive Fibonacci.",
                "I have `return fib(n-1)`. Is that it?", # Trap: Infinite Recursion (no base case)
                "Oh right. What is the base case for this sequence?", # Context
                "Can you write the if-statement for the base case?" # Syntax (Borderline, should likely guide)
            ]
        },
        {
            "lab": "Lab 10.3 PigLatin",
            "turns": [
                "I'm detecting vowels.",
                "I am using `if x == 'a'` but it breaks.", # Trap: Char vs String or bad logic
                "Okay, I fixed that. How do I output the result?" # General help
            ]
        }
    ]
    
    for scen in scenarios:
        run_scenario(tutor, scen['lab'], scen['turns'], log_dir)
        print("\n")
        
    print(f"Validation Complete. Logs available in {log_dir}")

if __name__ == "__main__":
    main()
