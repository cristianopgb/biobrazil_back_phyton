from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, File, Form, UploadFile
from app.schemas.documentos import DocumentoJsonRequest, DocumentoResponse, TipoArquivo, TipoDocumento
from app.services.documentos_service import DocumentosService
from app.services.logs_service import LogsService
from app.services.storage_service import StorageService
from app.core.supabase_client import get_supabase_client

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post('/json', response_model=DocumentoResponse, status_code=201)
def documentos_json(payload: DocumentoJsonRequest):
    result = DocumentosService.criar_documento_json(payload)
    return result


@router.post('/upload', response_model=DocumentoResponse, status_code=201)
async def documentos_upload(
    cliente_id: UUID = Form(...),
    tipo_arquivo: TipoArquivo = Form(...),
    origem: str = Form(...),
    hash_arquivo: str = Form(...),
    arquivo: UploadFile = File(...),
    tipo_documento: TipoDocumento = Form(default=TipoDocumento.nao_identificado),
):
    duplicated = DocumentosService._check_duplicate(str(cliente_id), hash_arquivo)
    if duplicated:
        LogsService.log_event(documento_id=duplicated['id'], cliente_id=str(cliente_id), origem='backend_python', tipo_evento='duplicidade_detectada', mensagem='Documento duplicado detectado no upload', detalhes_json={'hash_arquivo': hash_arquivo})
        return {"documento_id": duplicated["id"], "duplicated": True, "status_processamento": duplicated.get("status_processamento") or "desconhecido", "status_ia": duplicated.get("status_ia") or "desconhecido", "mensagem": "Documento já existe para cliente_id + hash_arquivo."}

    file_bytes = await arquivo.read()
    path = StorageService.upload_document(str(cliente_id), hash_arquivo, arquivo.filename, file_bytes, arquivo.content_type)
    payload = {
        "cliente_id": str(cliente_id), "nome_arquivo": arquivo.filename, "tipo_arquivo": tipo_arquivo.value,
        "tipo_documento": tipo_documento.value, "origem": origem, "hash_arquivo": hash_arquivo,
        "storage_path": path, "tamanho_arquivo": len(file_bytes), "status_processamento": "aguardando_ia",
        "metodo_extracao": "upload", "status_ia": "aguardando", "texto_extraido": None,
        "json_recebido_robo": None, "json_extraido_ia": None, "json_final": None,
        "confianca_ia": None, "precisa_revisao": True, "mensagem_erro": None,
        "data_recebimento": datetime.now(timezone.utc).isoformat(), "data_processamento": None,
    }
    created = get_supabase_client().table('documentos').insert(payload).execute().data[0]
    LogsService.log_event(documento_id=created['id'], cliente_id=str(cliente_id), origem='backend_python', tipo_evento='upload_realizado', mensagem='Upload de documento realizado', detalhes_json={'storage_path': path})
    return {"documento_id": created['id'], "duplicated": False, "status_processamento": "aguardando_ia", "status_ia": "aguardando", "mensagem": "Documento enviado com sucesso.", "storage_path": path}


@router.post('/{documento_id}/reprocessar')
def reprocessar(documento_id: UUID):
    get_supabase_client().table('documentos').update({'status_processamento': 'aguardando_ia', 'status_ia': 'aguardando'}).eq('id', str(documento_id)).execute()
    LogsService.log_event(documento_id=str(documento_id), cliente_id=None, origem='backend_python', tipo_evento='reprocessamento_solicitado', mensagem='Reprocessamento solicitado', detalhes_json={})
    return {'message': 'Solicitação de reprocessamento registrada com sucesso.', 'documento_id': str(documento_id), 'status_processamento': 'aguardando_ia'}
