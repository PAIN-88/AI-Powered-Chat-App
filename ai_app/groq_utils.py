from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def get_ai_reply(messages):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content


def call_groq_summarize(chat_text):
    messages = [
        {"role": "system", "content": "Summarize the following chat conversation concisely."},
        {"role": "user", "content": chat_text},
    ]
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message.content