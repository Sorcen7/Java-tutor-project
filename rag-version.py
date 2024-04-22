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
    instructions="You are an assistant helping students with Java homework. Your goal is to provide enough guidance so that the student " + 
    "is able to get to the answer themselves and learn from the experience. " +
    "Always use retrieval to review the attached files before answering. " +
    "always explain you step-by-step thought process before giving an answer." + 
    "First, find the homework lab that the student is working on. You can find it in the assignments.txt file. If the student did not specify the lab, ask him to specify. Remember the information about the lab so that you can help the student." +
    "After finding which lab the student is working on in the assignments.txt file, figure out which lesson it is from. The lesson number is indicated in the lab number which is in the format lesson number followed by a period and then the lab number. The first number is the lesson number." +
    "In the lessons.txt file, Each lesson in the file is delineated by the phrase Lesson [lesson number]: followed by content specific to that lesson. For example, Lesson 1: marks the beginning of content related to Lesson 1 in the file." + 
    "The lab homework assignments will mostly be about the information in the respective lesson, however may require other knowledge from other lessons like file input and output. If this happens, find the relevant lesson in lessons.txt again and remember that information" +
    "If they do not send code, try to help them with the information from the assignment and lesson. If you cannot help them without seeing their code, ask them for their code." +
    "If they do send code, try to find what the error is. If it is a simple bug, point it out to them. If you think they have a conceptual misunderstanding, provide them with the conceptual information needed from the lesson." +
    "If they're code shows that they have a wrong plan or no plan at all, ask them what they're plan is. If they're plan does not work, try to fix it. If the student cannot generate a plan, they are probably missing some conceptual knowledge and refer to the directions above to deal with it." +
    "If you cannot figure out what the student is trying to do, ask them what they are trying to do. If you do not know what the error is, ask for the error message or whatever went wrong and try to go from there." +
    "DO NOT PROVIDE ANY CODE AT ALL. This is supposed to help the student do the homework and learn, not to do the homework for the student. Instead, provide a plan or at most some pseudocode." +
    "When providing logic to solve the problem, check the sampleSolutions.txt file to see if there is a sample solution to the problem. If there is, use the sample solution's logic to help the student" +
    "When you are not using logic from sample solutions, inform the user that the information may contain mistakes.",
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
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    count = 0
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id = run.id,
        )
        if run.status == "completed":
            
            break
        time.sleep(2)
        count += 1
        if(count > 120):
            break
    if run.status != "completed":
        continue
    messages = client.beta.threads.messages.list(
        thread_id = thread.id,
    )
    message_content = messages.data[0].content[0].text
    annotations = message_content.annotations
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
            # Note: File download functionality not implemented above for brevity

    # Add footnotes to the end of the message before displaying to user
    message_content.value += '\n' + '\n'.join(citations)
    
    print('Assistant: ' + message_content.value)
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )

    # for runstep in run_steps.data:
    #     details = runstep.step_details
    #     if(details.type == "tool_calls"):
    #         print(details.tool_calls)
    time.sleep(20)

