from io import BytesIO

from pypdf import PdfReader


def extract_text(content: bytes, filename: str) -> list[tuple[str, str | None]]:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((text, str(index)))
        return pages
    if lower.endswith(".txt") or lower.endswith(".md"):
        return [(content.decode("utf-8", errors="ignore"), None)]
    raise ValueError("Only PDF, TXT, and MD supporting documents are supported.")


def chunk_text(text: str, max_chars: int = 900, overlap: int = 120) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + max_chars, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks
