from app.core.supabase_client import get_supabase_client
from app.schemas.exportacoes import ExportacaoGerarRequest
from app.services.logs_service import LogsService


class ExportacoesService:
    @staticmethod
    def gerar_exportacao(payload: ExportacaoGerarRequest) -> dict:
        filtros = payload.model_dump(mode="json")
        insert_payload = {
            "usuario_id": str(payload.usuario_id),
            "filtros_json": filtros,
            "periodo_inicio": payload.periodo_inicio.isoformat(),
            "periodo_fim": payload.periodo_fim.isoformat(),
            "quantidade_notas": 0,
            "quantidade_pendencias": 0,
            "arquivo_storage_path": None,
            "status_exportacao": "solicitado",
            "status_email": "nao_enviado",
            "email_destino": None,
            "mensagem_erro": None,
        }
        response = get_supabase_client().table("exportacoes").insert(insert_payload).execute()
        exportacao = response.data[0]
        exportacao_id = exportacao["id"]

        LogsService.log_event(
            documento_id=None,
            cliente_id=str(payload.cliente_id),
            origem="backend_python",
            tipo_evento="exportacao_solicitada",
            mensagem="Exportação solicitada",
            detalhes_json={"exportacao_id": exportacao_id, "filtros": filtros},
            severidade="info",
        )
        return {"exportacao_id": exportacao_id, "status_exportacao": "solicitado"}

    @staticmethod
    def status_exportacao(exportacao_id: str) -> dict:
        response = get_supabase_client().table("exportacoes").select("id,status_exportacao,arquivo_storage_path,mensagem_erro").eq("id", exportacao_id).limit(1).execute()
        data = response.data[0]
        return {
            "exportacao_id": data["id"],
            "status_exportacao": data.get("status_exportacao"),
            "arquivo_storage_path": data.get("arquivo_storage_path"),
            "mensagem_erro": data.get("mensagem_erro"),
        }
