from bs4 import BeautifulSoup

def extract_seo_elements(html: str) -> dict:
    """Extract title, meta description, and H1 from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta = meta_tag["content"].strip() if meta_tag and meta_tag.get("content") else ""
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else ""

    return {
        "title": title,
        "meta_description": meta,
        "h1": h1
    }

def evaluate_seo_elements(elements: dict) -> dict:
    """Evaluate SEO elements against best practices."""
    title_len = len(elements["title"])
    meta_len = len(elements["meta_description"])
    has_h1 = bool(elements["h1"])

    return {
        "title_length": title_len,
        "title_ok": 30 <= title_len <= 60,
        "meta_length": meta_len,
        "meta_ok": 80 <= meta_len <= 160,
        "has_h1": has_h1
    }

