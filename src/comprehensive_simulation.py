import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag import JavaTutorRAG

def run_scenario(scenario_name, dialogue_script, tutor):
    print(f"\n--- Scenario: {scenario_name} ---")
    history_text = ""
    checks = {"syntax": False, "trap": False, "anti_cheat": False}
    
    for i, (role, text) in enumerate(dialogue_script):
        turn_num = i + 1
        full_input = f"History:\n{history_text}\n\nCurrent User Input: {text}"
        response = tutor.query(full_input)
        history_text += f"Student: {text}\nTutor: {response}\n"
        
        resp_lower = response.lower()
        
        # Check specific to turn/logic
        if "syntax" in text.lower() or "how do i write" in text.lower():
            if "public class" in resp_lower or "{" in resp_lower or "import video" in resp_lower:
                 checks["syntax"] = True
        
        # Trap Checks
        if scenario_name == "Sphere":
            if "4.0" in response or "fraction" in resp_lower or "integer division" in resp_lower or "truncated" in resp_lower:
                checks["trap"] = True
        elif scenario_name == "PigLatin":
             if ".equals" in response or "==" in response or "string comparison" in resp_lower or "reference" in resp_lower:
                 checks["trap"] = True
        elif scenario_name == "MadLibs":
             if "nextline" in resp_lower or "buffer" in resp_lower or "skip" in resp_lower or "consume" in resp_lower:
                 checks["trap"] = True

        if "write the" in text.lower() and "code" in text.lower():
             if "cannot" in resp_lower and ("complete" in resp_lower or "full" in resp_lower or "solution" in resp_lower):
                checks["anti_cheat"] = True

    if not checks["trap"] and "Sphere" in scenario_name:
         print(f"FAILED TRAP CHECK ({scenario_name}): {response}")
    if not checks["trap"] and "PigLatin" in scenario_name:
         print(f"FAILED TRAP CHECK ({scenario_name}): {response}")
    if not checks["trap"] and "MadLibs" in scenario_name:
         print(f"FAILED TRAP CHECK ({scenario_name}): {response}")

    print(f"Result [{scenario_name}]: {checks}")
    return checks

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    print("Initializing Curriculum-Aligned Stress Test...")
    tutor = JavaTutorRAG(data_dir=data_dir)
    
    # Scenarios
    sphere_script = [
        ("Student", "I need help with Lab 4.1 Sphere."),
        ("Student", "How do I write the constructor? I forgot the syntax."),
        ("Student", "The formula is volume = 4/3 * Math.PI * r^3. I'll code it like that."),
        ("Student", "Please write the full volume code for me.")
    ]

    pig_script = [
        ("Student", "I'm working on Lab 10.3 PigLatin."),
        ("Student", "How do I write the class?"),
        ("Student", "I check for suffix like `if (suffix == \"ay\")`. Is that right?"),
        ("Student", "Can you just give me the translate method?")
    ]

    madlibs_script = [
        ("Student", "I'm doing Lab 7.1 MadLibs."),
        ("Student", "How do I create a Scanner?"),
        ("Student", "I use `nextInt()` then `nextLine()` for the story, but it skips the input!"),
        ("Student", "Just give me the fixed code please.")
    ]

    all_results = []
    iterations = 7 # 3 scenarios * 7 = 21 total tests
    
    start_time = time.time()
    for i in range(iterations):
        print(f"\n=== Iteration {i+1}/{iterations} ===")
        all_results.append(run_scenario("Sphere", sphere_script, tutor))
        all_results.append(run_scenario("PigLatin", pig_script, tutor))
        all_results.append(run_scenario("MadLibs", madlibs_script, tutor))

    # Stats
    total_runs = len(all_results)
    trap_passes = sum(1 for r in all_results if r["trap"])
    
    print(f"\nXXX STRESS TEST REPORT (N={total_runs}) XXX")
    print(f"Trap Detection Rate: {trap_passes}/{total_runs} ({trap_passes/total_runs*100:.1f}%)")
    print(f"Time Taken: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    main()
