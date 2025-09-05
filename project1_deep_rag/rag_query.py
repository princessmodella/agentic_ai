import openai

def query_gpt(question: str, context: str, api_key: str):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Answer this question based on context:\nContext: {context}\nQuestion: {question}",
        max_tokens=200
    )
    return response.choices[0].text.strip()
