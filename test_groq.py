from config import client

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Write 2 lines about shoes"}
    ]
)

print(response.choices[0].message.content)