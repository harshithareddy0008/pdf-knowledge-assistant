"""Validation contracts for HTTP responses and questions."""
from pydantic import BaseModel, Field


class Source(BaseModel):
    number: int
    file: str
    page: int
    excerpt: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=800)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    model: str


class DocumentInfo(BaseModel):
    file: str
    file_id: str
    pages: int
    chunks: int


class UploadResult(BaseModel):
    file: str
    status: str
    pages: int
    chunks: int


class UploadResponse(BaseModel):
    results: list[UploadResult]


class DocumentsResponse(BaseModel):
    documents: list[DocumentInfo]
