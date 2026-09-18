from app.llm.manager import LLMManager
from app.models.chat import ChatRequest, ChatResponse
from app.rag.citations import build_sources
from app.rag.prompts import SYSTEM_PROMPT, format_docs, format_history
from app.rag.vectorstore import VectorStoreService


class RAGService:
    def __init__(
        self,
        vectorstore_service: VectorStoreService,
        llm_manager: LLMManager,
    ):
        self.vectorstore_service = vectorstore_service
        self.llm_manager = llm_manager

    def ask(self, request: ChatRequest) -> ChatResponse:
        retriever = self.vectorstore_service.as_retriever(request.document_id)
        retrieved_docs = retriever.invoke(request.question)

        context = format_docs(retrieved_docs)
        history = format_history([m.model_dump() for m in request.history])

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Conversation history (for reference only — do not override document grounding):\n"
            f"{history}\n\n"
            f"Question:\n{request.question}"
        )

        answer = self.llm_manager.generate(SYSTEM_PROMPT, user_prompt)
        sources = build_sources(retrieved_docs)

        return ChatResponse(answer=answer.strip(), sources=sources)
