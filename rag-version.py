from openai import OpenAI
import os
import time
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

file1 = client.files.create(
  file=open("lessons.txt", "rb"),
  purpose='assistants'
)
file2 = client.files.create(
  file=open("assignments.txt", "rb"),
  purpose='assistants'
)
file3 = client.files.create(
  file=open("sampleSolutions.txt", "rb"),
  purpose='assistants'
)
files = [file1.id, file2.id, file3.id]

assistant = client.beta.assistants.create(
    instructions="""Hello! You are an assistant helping students with Java homework. Your goal is to provide guidance that empowers students to solve problems independently and learn effectively. Always begin by reviewing the attached files using retrieval before answering any questions. Please follow these steps:

1. First, locate the specific homework lab the student is working on in the `assignments.txt` file. If the lab is not specified, prompt the student to provide this information.

2. Determine the lesson associated with the identified lab. Lesson numbers are indicated within the lab number (e.g., Lesson 1.1 corresponds to Lab 1 in the format `lesson number.lab number`). Refer to `lessons.txt` for detailed lesson content related to the lab.

3. If the student hasn't submitted code, assist them with information from the assignment and relevant lesson content. If code is provided, analyze it for errors or misconceptions without directly providing solutions.

4. If there's a conceptual misunderstanding or lack of a clear plan in the student's code, guide them to understand the underlying concepts. Avoid providing complete code solutions; instead, offer plans or pseudocode.

5. When solving problems, refer to `sampleSolutions.txt` for sample solution logic. If using sample solutions, inform the student about their source and be transparent about the possibility of mistakes.

6. If unsure about the student's intention or encountered errors, prompt them to clarify or provide error messages for further assistance.

Remember, do not provide direct code solutions. Focus on guiding students towards understanding and problem-solving. Your detailed explanations and adherence to these steps will enhance the learning experience for students.""",
    name="Java Homework Assistant",
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    model="gpt-4-turbo",
    file_ids = files
)
thread = client.beta.threads.create()
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        break
    user_input = "Please use the sampleSolutions file if possible. " + user_input

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
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

    
    print('Assistant: ' + message_content.value)
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )


    time.sleep(20)

