from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import AppServices, get_services
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    services: AppServices = Depends(get_services),
) -> ChatResponse:
    if request.document_id:
        services.document_service.get_document(request.document_id)
    return services.rag_service.ask(request)
