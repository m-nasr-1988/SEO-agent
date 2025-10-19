import streamlit as st

# Try to import OpenAI client
try:
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False


def suggest_improvements(title: str, meta: str, h1: str, method: str = "Mock") -> dict:
    """
    Suggest SEO improvements.
    method: "Mock" or "OpenAI"
    """

    # --- Mock mode ---
    if method == "Mock" or not HAS_OPENAI:
        return {
            "title": (title or "Untitled") + " | Mock Improved",
            "meta": (meta or "No meta description") + " (mock optimized)",
            "h1": (h1 or "Missing H1") + " [Mock Better H1]"
        }

    # --- OpenAI mode ---
    prompt = f"""
    You are an SEO expert. Improve the following elements:
    - Title: {title}
    - Meta description: {meta}
    - H1: {h1}

    Rules:
    - Title: 30–60 characters, compelling, keyword-rich.
    - Meta: 80–160 characters, clear and engaging.
    - H1: concise, keyword-focused.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or gpt-4o-mini if available
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        text = response.choices[0].message.content.strip()

        # Simple parsing: return the whole text in all fields
        return {"title": text, "meta": text, "h1": text}

    except Exception as e:
        # Fallback to mock if API fails
        return {
            "title": (title or "Untitled") + " | Mock Fallback",
            "meta": (meta or "No meta description") + " (mock fallback)",
            "h1": (h1 or "Missing H1") + " [Mock Fallback H1]"
        }
