from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    file_name: Mapped[str] = mapped_column(String(240))
    document_type: Mapped[str] = mapped_column(String(80), default="supporting_document")
    processing_status: Mapped[str] = mapped_column(String(40), default="processed")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    embedding_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    page: Mapped[str | None] = mapped_column(String(40), nullable=True)
    section: Mapped[str | None] = mapped_column(String(120), nullable=True)

    document: Mapped[Document] = relationship(back_populates="chunks")
