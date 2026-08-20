from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.models.financial import Company
from app.rag.extraction import chunk_text, extract_text


def upload_document(db: Session, company_id: int, filename: str, content: bytes, document_type: str = "supporting_document") -> dict:
    if not db.get(Company, company_id):
        raise ValueError("Company not found")
    pages = extract_text(content, filename)
    document = Document(company_id=company_id, file_name=filename, document_type=document_type, processing_status="processed")
    db.add(document)
    db.flush()
    count = 0
    for text, page in pages:
        for idx, chunk in enumerate(chunk_text(text), start=1):
            db.add(DocumentChunk(document_id=document.id, content=chunk, page=page, section=f"chunk-{idx}", embedding_reference=f"tfidf:{document.id}:{page or 0}:{idx}"))
            count += 1
    if count == 0:
        document.processing_status = "empty"
    db.commit()
    return {"document_id": document.id, "chunks": count, "processing_status": document.processing_status}


def list_documents(db: Session, company_id: int) -> list[Document]:
    return db.scalars(select(Document).where(Document.company_id == company_id).order_by(Document.uploaded_at.desc())).all()
