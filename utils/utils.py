"""All the utilities related to the policy scraping and all"""
from pathlib import Path

# project root (folder where app.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = BASE_DIR / "policies_txt"

POLICY_FILES = {
    1: ("chatgpt", "open_ai.md"),
    2: ("claude", "claude.md"),
    3: ("gemini", "gemini.md"),
    4: ("grok", "grok.md"),
}

def get_policy_doc(policy_id: int, url: str)->dict:
    try:
        provider, filename = POLICY_FILES[policy_id]
    except:
        raise ValueError(f"Unknown policy id: {policy_id}")

    path = POLICIES_DIR / filename

    # Extract policy name from filename (without extension) for vector store matching
    policy_name = filename.replace('.md', '').replace('.txt', '')

    # read the markdown file
    text = path.read_text(encoding="utf-8")

    return {
        "id": policy_id,
        "provider": provider,                     # "chatgpt", "claude", ...
        "policy": policy_name,                    # "open_ai", "claude", ... (matches FAISS index)
        "path": str(path),
        "url": url,                              # you can fill real URL if you want
        "title": f"{provider.capitalize()} Privacy Policy",
        "text": text,                             # main thing run_all_checks will use
    }