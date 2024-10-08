from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": prompt},
            {"role": "system", "content" : "You are a Java tutor. All prompts given are assumed to be about Java unless otherwise explicitly stated."}
        ]
    )
    return response.choices[0].message.content.strip()


while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        break
    response = chat_with_gpt(user_input)
    print("Chatbot: " + response)