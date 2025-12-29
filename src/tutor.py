import sys
import os

# Ensure we can import from src regardless of where script is run
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag import JavaTutorRAG

try:
    from rich.console import Console
    from rich.markdown import Markdown
    console = Console()
    print_formatted = True
except ImportError:
    print_formatted = False

def print_response(response):
    if print_formatted:
        md = Markdown(response)
        console.print(md)
        console.print("-" * 50, style="dim")
    else:
        print("\nAssistant:")
        print(response)
        print("-" * 50)

def main():
    print("Welcome to the Interactive Java Tutor!")
    print("Initializing system... please wait.")
    
    # Locate data dir relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    print("\nSystem Loaded! Type '/quit' to exit, '/clear' to clear screen.")
    print("Enter your Java question below:\n")
    
    chat_history = []
    
    # Generate a session ID for this CLI run
    import uuid
    session_id = str(uuid.uuid4())

    while True:
        try:
            if print_formatted:
                user_input = console.input("[bold green]User>[/bold green] ")
            else:
                user_input = input("User> ")
                
            user_input = user_input.strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['/quit', 'exit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == '/clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                # Start a new session on clear
                session_id = str(uuid.uuid4())
                continue

            # Pass session_id to query
            response = tutor.query(user_input, session_id=session_id)
            
            print_response(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
