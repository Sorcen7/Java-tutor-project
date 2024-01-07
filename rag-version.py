from openai import OpenAI
import os
import time
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
    instructions="You are a personal java tutor. When asked a question, guide the student to find the answer for themselves.",
    name="Java Tutor",
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    model="gpt-3.5-turbo-1106",
)
thread = client.beta.threads.create()
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        break
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
        time.sleep(0.5)
    messages = client.beta.threads.messages.list(
        thread_id = thread.id,
    )
    print('Assistant: ' + messages.data[0].content[0].text.value)

