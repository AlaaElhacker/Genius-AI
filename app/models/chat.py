from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str
    file_name: str
    page: int | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    document_id: str | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
