from typing import Any
from app.core.supabase_client import get_supabase_client


class LogsService:
    @staticmethod
    def log_event(*, documento_id: str | None, cliente_id: str | None, origem: str, tipo_evento: str, mensagem: str, detalhes_json: dict[str, Any] | None = None, severidade: str = "info") -> None:
        payload = {
            "documento_id": documento_id,
            "cliente_id": cliente_id,
            "origem": origem,
            "tipo_evento": tipo_evento,
            "mensagem": mensagem,
            "detalhes_json": detalhes_json or {},
            "severidade": severidade,
        }
        get_supabase_client().table("logs_processamento").insert(payload).execute()
