from uuid import UUID
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    supabase_configured: bool
    openai_configured: bool


class MessageResponse(BaseModel):
    message: str


class UUIDPath(BaseModel):
    id: UUID
