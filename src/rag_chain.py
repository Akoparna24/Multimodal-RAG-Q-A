import os
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TEXT_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are an intelligent document assistant.
You answer questions based only on the provided context.
The context may contain text, tables, and image descriptions.
If the answer is not in the context, say so clearly.
Always mention which page the information comes from. Do not mention the chunks."""

def answer_question(question: str, chunks: list[dict]) -> str:
    """Generate an answer from retrieved chunks using Groq."""

    # Handle greetings and casual messages
    greetings = ["hi", "hello", "hey", "how are you", "good morning", "good evening"]
    if question.strip().lower() in greetings:
        return "Hi! I'm your document assistant. Ask me anything about your uploaded document — text, tables, charts or images!"

    # Build context from chunks
    context = ""
    for chunk in chunks:
        context += f"\n--- [{chunk['type']}] (page {chunk['page']}) ---\n"
        context += chunk["content"]
        context += "\n"

    # Build prompt
    prompt = f"""Here is the context retrieved from the document:

    {context}

    Question: {question}

    Instructions:
    - Answer based only on the context above
    - Mention page numbers where relevant
    - Do NOT reference "chunks" or "context" in your answer
    - Speak naturally as if you read the document yourself"""
    # Call Groq
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()