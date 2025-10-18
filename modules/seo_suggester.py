import os

# Example with OpenAI (replace with your provider)
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def suggest_improvements(title: str, meta: str, h1: str) -> dict:
    """Generate improved SEO suggestions for title, meta, and H1."""
    prompt = f"""
    You are an SEO expert. Improve the following elements for better SEO:
    - Title: {title}
    - Meta description: {meta}
    - H1: {h1}

    Rules:
    - Title: 30–60 characters, compelling, keyword-rich.
    - Meta: 80–160 characters, clear and engaging.
    - H1: concise, keyword-focused.

    Return suggestions in plain text.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or your chosen model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    text = response.choices[0].message.content.strip()

    # Simple parsing: split into lines
    lines = text.splitlines()
    suggestions = {"title": "", "meta": "", "h1": ""}
    for line in lines:
        if line.lower().startswith("title"):
            suggestions["title"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("meta"):
            suggestions["meta"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("h1"):
            suggestions["h1"] = line.split(":", 1)[-1].strip()

    return suggestions
