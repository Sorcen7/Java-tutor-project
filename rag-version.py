from openai import OpenAI
import os
import time
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
    instructions="""Hello! You are an assistant helping students with Java homework. Your goal is to provide guidance that empowers students to solve problems independently and learn effectively. Always begin by reviewing the attached files using retrieval before answering any questions. Please follow these steps:

    1. First, locate the specific homework lab the student is working on in the `assignments.txt` file. If the lab is not specified, prompt the student to provide this information.

    2. Determine the lesson associated with the identified lab. Lesson numbers are indicated within the lab number (e.g., Lesson 1.1 corresponds to Lab 1 in the format `lesson number.lab number`). Refer to `lessons.txt` for detailed lesson content related to the lab.

    3. If the student hasn't submitted code, assist them with information from the assignment and relevant lesson content. If code is provided, analyze it for errors or misconceptions without directly providing solutions.

    4. If there's a conceptual misunderstanding or lack of a clear plan in the student's code, guide them to understand the underlying concepts. Avoid providing code solutions; instead, offer plans or pseudocode. Plans should not include code.

    5. When solving problems, refer to `sampleSolutions.txt` for sample solution logic. If using sample solutions, inform the student about their source and be transparent about the possibility of mistakes.

    6. If unsure about the student's intention or encountered errors, prompt them to clarify or provide error messages for further assistance.

    Remember, do not provide direct code solutions. Focus on guiding students towards understanding and problem-solving. Your detailed explanations and adherence to these steps will enhance the learning experience for students.""",
    name="Java Homework Assistant",
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
    model="gpt-4-turbo"
)

vector_store = client.beta.vector_stores.create(name="Course Material")

file_paths = ["lessons.txt", "assignments.txt", "sampleSolutions.txt"]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)



def parse_labs_file(file_path):
    with open(file_path, 'r') as file:
        labs = []
        current_lab = {}
        
        for line in file:
            line = line.strip()
            if line.startswith('Lab '):
                if current_lab:
                    # Ensure 'incorrect_solution' key exists, even if it's an empty list
                    if 'incorrect_solution' not in current_lab:
                        current_lab['incorrect_solution'] = []
                    labs.append(current_lab)
                    current_lab = {}
                current_lab['name'] = line.split(':')[0]
            elif line.startswith('Incorrect Solution:'):
                current_lab['incorrect_solution'] = []
            elif current_lab.get('incorrect_solution') is not None:
                current_lab['incorrect_solution'].append(line)
        
        if current_lab:
            # Ensure 'incorrect_solution' key exists in the last lab entry
            if 'incorrect_solution' not in current_lab:
                current_lab['incorrect_solution'] = []
            labs.append(current_lab)
    
    return labs


def generate_prompts(labs):
    prompts = []
    for lab in labs:
        lab_name = lab['name']
        incorrect_solution = '\n'.join(lab['incorrect_solution'])
        
        high_level_plan_prompt = f"Provide a high-level plan for solving the '{lab_name}' lab."
        pseudocode_prompt = f"Write pseudocode for the '{lab_name}' lab."
        debugging_prompt = f"Given the following incorrect solution for the '{lab_name}' lab, identify and fix the errors:\n\n{incorrect_solution}"
        
        prompts.extend([high_level_plan_prompt, pseudocode_prompt, debugging_prompt])
    
    return prompts

# Example usage:
labs_file = 'input.txt'
labs = parse_labs_file(labs_file)
prompts = generate_prompts(labs)



count = 0
with open('output.txt', 'w', encoding='utf-8') as output: 
    for prompt in prompts:
        if count % 3 == 0 : 
            output.write('-' * 50)
            thread = client.beta.threads.create()

        output.write('\nUser: ' + prompt)
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            tool_choice={"type": "file_search"}
        )

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id = thread.id,
                run_id = run.id,
            )
            if run.status == "completed":
                
                break
            time.sleep(2)

        if run.status != "completed":
            continue
        messages = client.beta.threads.messages.list(
            thread_id = thread.id,
        )
        message_content = messages.data[0].content[0].text
        annotations = message_content.annotations
        citations = []

        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f'')

        
        output.write('\nAssistant: ' + message_content.value)
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(20)
        print('.')
        count += 1


        

