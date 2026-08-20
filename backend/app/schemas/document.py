from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    company_id: int
    file_name: str
    document_type: str
    processing_status: str

    model_config = {"from_attributes": True}


class RetrievedContext(BaseModel):
    document_id: int
    document_name: str
    chunk_id: int
    content: str
    score: float
    page: str | None = None
    section: str | None = None


class AnalystQuestion(BaseModel):
    company_id: int
    question: str


class AnalystAnswer(BaseModel):
    answer: str
    ai_enabled: bool
    structured_findings: list[dict] = []
    sources: list[RetrievedContext] = []


class SupportingContextRequest(BaseModel):
    anomaly_id: int
