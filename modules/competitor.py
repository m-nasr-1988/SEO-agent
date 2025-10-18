import requests
import time
from urllib.parse import urlparse
from modules import seo_analyzer

def normalize_url(u: str) -> str:
    u = u.strip()
    if not u:
        return u
    parsed = urlparse(u)
    if not parsed.scheme:
        u = "https://" + u
    return u

def fetch_page(u: str, timeout: int = 15, ua: str = "seo-agent/0.3"):
    headers = {"User-Agent": ua}
    start = time.perf_counter()
    resp = requests.get(u, headers=headers, timeout=timeout, allow_redirects=True)
    elapsed = time.perf_counter() - start
    return {
        "status_code": resp.status_code,
        "elapsed_ms": int(elapsed * 1000),
        "final_url": resp.url,
        "text": resp.text,
        "ok": resp.ok
    }

def analyze_urls(urls: list, timeout: int = 15, ua: str = "seo-agent/0.3"):
    """Fetch and analyze multiple URLs, return list of records."""
    results = []
    for u in urls:
        norm_url = normalize_url(u)
        try:
            result = fetch_page(norm_url, timeout=timeout, ua=ua)
            if not result["ok"]:
                results.append({
                    "URL": norm_url,
                    "Status": f"Error {result['status_code']}"
                })
                continue

            elements = seo_analyzer.extract_seo_elements(result["text"])
            evaluation = seo_analyzer.evaluate_seo_elements(elements)

            record = {
                "URL": result["final_url"],
                "Status": "OK",
                "Title": elements["title"],
                "Title Length": evaluation["title_length"],
                "Title OK": "✅" if evaluation["title_ok"] else "⚠️",
                "Meta Description": elements["meta_description"],
                "Meta Length": evaluation["meta_length"],
                "Meta OK": "✅" if evaluation["meta_ok"] else "⚠️",
                "H1": elements["h1"],
                "Has H1": "✅" if evaluation["has_h1"] else "⚠️"
            }
            results.append(record)
        except Exception as e:
            results.append({
                "URL": norm_url,
                "Status": f"Error: {e}"
            })
    return results
