from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from fastapi import HTTPException
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
    def _validar_cliente(cliente_id: str) -> None:
        response = get_supabase_client().table("clientes").select("id").eq("id", cliente_id).limit(1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} não encontrado.")

    @staticmethod
    def _metodo_json(tipo_arquivo: str) -> str:
        if tipo_arquivo == "xml":
            return "local_xml"
        if tipo_arquivo == "pdf_texto":
            return "local_pdf_texto"
        return "nao_processado"

    @staticmethod
    def _metodo_upload(tipo_arquivo: str) -> str:
        if tipo_arquivo in {"imagem", "pdf_imagem"}:
            return "ia_multimodal"
        return "nao_processado"

    @staticmethod
    def _float_or_zero(value: Decimal | float | None) -> float:
        return float(value) if value is not None else 0.0

    @staticmethod
    def _insert_nota(documento_id: str, cliente_id: str, tipo_documento: str, nota: NotaPayload, metodo_extracao: str) -> None:
        payload = {
            "documento_id": documento_id,
            "cliente_id": cliente_id,
            "tipo_documento": (nota.tipo_documento.value if nota.tipo_documento else tipo_documento),
            "numero_nota": nota.numero_nota,
            "serie": nota.serie,
            "data_emissao": nota.data_emissao.isoformat() if nota.data_emissao else None,
            "prestador_nome": nota.prestador_nome,
            "prestador_cnpj": nota.prestador_cnpj,
            "tomador_nome": nota.tomador_nome,
            "tomador_cnpj": nota.tomador_cnpj,
            "valor_bruto": DocumentosService._float_or_zero(nota.valor_bruto),
            "valor_servico": DocumentosService._float_or_zero(nota.valor_servico),
            "iss": DocumentosService._float_or_zero(nota.iss),
            "irrf": DocumentosService._float_or_zero(nota.irrf),
            "pis": DocumentosService._float_or_zero(nota.pis),
            "cofins": DocumentosService._float_or_zero(nota.cofins),
            "csll": DocumentosService._float_or_zero(nota.csll),
            "inss": DocumentosService._float_or_zero(nota.inss),
            "valor_liquido": DocumentosService._float_or_zero(nota.valor_liquido),
            "status_validacao": "pendente",
            "confianca_ia": None,
            "metodo_extracao": metodo_extracao,
            "precisa_revisao": True,
            "json_extraido": nota.model_dump(mode="json"),
        }
        get_supabase_client().table("notas_extraidas").insert(payload).execute()

    @staticmethod
    def criar_documento_json(payload: DocumentoJsonRequest) -> dict[str, Any]:
        cliente_id = str(payload.cliente_id)
        DocumentosService._validar_cliente(cliente_id)
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

        metodo_extracao = DocumentosService._metodo_json(payload.tipo_arquivo.value)
        has_nota = payload.nota is not None
        status_ia = "nao_necessario"
        status_processamento = "pendente_revisao" if has_nota else "processado"

        doc_payload = {
            "cliente_id": cliente_id,
            "nome_arquivo": payload.nome_arquivo,
            "tipo_arquivo": payload.tipo_arquivo.value,
            "tipo_documento": payload.tipo_documento.value,
            "origem": payload.origem,
            "hash_arquivo": payload.hash_arquivo,
            "storage_path": None,
            "tamanho_arquivo": None,
            "status_processamento": status_processamento,
            "metodo_extracao": metodo_extracao,
            "status_ia": status_ia,
            "texto_extraido": payload.texto_extraido,
            "json_recebido_robo": payload.model_dump(mode="json"),
            "json_extraido_ia": None,
            "json_final": payload.json_final,
            "confianca_ia": None,
            "precisa_revisao": True,
            "mensagem_erro": None,
            "data_recebimento": datetime.now(timezone.utc).isoformat(),
            "data_processamento": None,
        }
        created = get_supabase_client().table("documentos").insert(doc_payload).execute().data[0]
        documento_id = created["id"]

        if payload.nota:
            DocumentosService._insert_nota(documento_id, cliente_id, payload.tipo_documento.value, payload.nota, metodo_extracao)

        LogsService.log_event(documento_id=documento_id, cliente_id=cliente_id, origem="backend_python", tipo_evento="documento_json_recebido", mensagem="Documento recebido via JSON", detalhes_json={"nome_arquivo": payload.nome_arquivo})
        return {
            "documento_id": documento_id,
            "duplicated": False,
            "status_processamento": status_processamento,
            "status_ia": status_ia,
            "mensagem": "Documento criado com sucesso.",
        }
