from datetime import datetime, timezone
from typing import Any
from app.core.supabase_client import get_supabase_client
from app.schemas.documentos import DocumentoJsonRequest, NotaPayload
from app.services.logs_service import LogsService


class DocumentosService:
    @staticmethod
    def _check_duplicate(cliente_id: str, hash_arquivo: str) -> dict[str, Any] | None:
        response = (
            get_supabase_client()
            .table("documentos")
            .select("id,status_processamento,status_ia")
            .eq("cliente_id", cliente_id)
            .eq("hash_arquivo", hash_arquivo)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    @staticmethod
    def _insert_nota(documento_id: str, cliente_id: str, tipo_documento: str, nota: NotaPayload) -> None:
        payload = {
            "documento_id": documento_id,
            "cliente_id": cliente_id,
            "tipo_documento": tipo_documento,
            "numero_nota": nota.numero_nota,
            "serie": nota.serie,
            "data_emissao": nota.data_emissao.isoformat() if nota.data_emissao else None,
            "prestador_nome": nota.prestador_nome,
            "prestador_cnpj": nota.prestador_cnpj,
            "tomador_nome": nota.tomador_nome,
            "tomador_cnpj": nota.tomador_cnpj,
            "valor_bruto": float(nota.valor_bruto) if nota.valor_bruto is not None else None,
            "valor_servico": None,
            "iss": None,
            "irrf": None,
            "pis": None,
            "cofins": None,
            "csll": None,
            "inss": None,
            "valor_liquido": None,
            "status_validacao": "pendente",
            "confianca_ia": None,
            "metodo_extracao": "json_robo",
            "precisa_revisao": True,
            "json_extraido": nota.model_dump(mode="json"),
        }
        get_supabase_client().table("notas_extraidas").insert(payload).execute()

    @staticmethod
    def criar_documento_json(payload: DocumentoJsonRequest) -> dict[str, Any]:
        cliente_id = str(payload.cliente_id)
        duplicated = DocumentosService._check_duplicate(cliente_id, payload.hash_arquivo)
        if duplicated:
            LogsService.log_event(documento_id=duplicated["id"], cliente_id=cliente_id, origem="backend_python", tipo_evento="duplicidade_detectada", mensagem="Documento duplicado detectado", detalhes_json={"hash_arquivo": payload.hash_arquivo})
            return {
                "documento_id": duplicated["id"],
                "duplicated": True,
                "status_processamento": duplicated.get("status_processamento") or "desconhecido",
                "status_ia": duplicated.get("status_ia") or "desconhecido",
                "mensagem": "Documento já existe para cliente_id + hash_arquivo.",
            }

        doc_payload = {
            "cliente_id": cliente_id,
            "nome_arquivo": payload.nome_arquivo,
            "tipo_arquivo": payload.tipo_arquivo.value,
            "tipo_documento": payload.tipo_documento.value,
            "origem": payload.origem,
            "hash_arquivo": payload.hash_arquivo,
            "storage_path": None,
            "tamanho_arquivo": None,
            "status_processamento": "aguardando_ia",
            "metodo_extracao": "json_robo",
            "status_ia": "aguardando",
            "texto_extraido": None,
            "json_recebido_robo": payload.model_dump(mode="json"),
            "json_extraido_ia": None,
            "json_final": None,
            "confianca_ia": None,
            "precisa_revisao": True,
            "mensagem_erro": None,
            "data_recebimento": datetime.now(timezone.utc).isoformat(),
            "data_processamento": None,
        }
        created = get_supabase_client().table("documentos").insert(doc_payload).execute().data[0]
        documento_id = created["id"]

        if payload.nota:
            DocumentosService._insert_nota(documento_id, cliente_id, payload.tipo_documento.value, payload.nota)

        LogsService.log_event(documento_id=documento_id, cliente_id=cliente_id, origem="backend_python", tipo_evento="documento_json_recebido", mensagem="Documento recebido via JSON", detalhes_json={"nome_arquivo": payload.nome_arquivo})
        return {
            "documento_id": documento_id,
            "duplicated": False,
            "status_processamento": "aguardando_ia",
            "status_ia": "aguardando",
            "mensagem": "Documento criado com sucesso.",
        }
