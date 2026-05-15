from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get('/health')
def health() -> dict:
    s = get_settings()
    return {
        'status': 'ok',
        'service': s.service_name,
        'environment': s.environment,
        'supabase_configured': bool(s.supabase_url and s.supabase_service_role_key),
        'openai_configured': bool(s.openai_api_key),
    }
