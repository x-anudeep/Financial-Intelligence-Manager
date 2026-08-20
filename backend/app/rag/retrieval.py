from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


def search_company_documents(db: Session, company_id: int, query: str, limit: int = 5) -> list[dict]:
    rows = db.execute(
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.company_id == company_id)
    ).all()
    if not rows:
        return []
    corpus = [chunk.content for chunk, _ in rows]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)[:limit]
    results = []
    for index, score in ranked:
        if score <= 0:
            continue
        chunk, document = rows[index]
        results.append({
            "document_id": document.id,
            "document_name": document.file_name,
            "chunk_id": chunk.id,
            "content": chunk.content,
            "score": float(score),
            "page": chunk.page,
            "section": chunk.section,
        })
    return results
