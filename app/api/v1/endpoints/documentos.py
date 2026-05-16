from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from app.schemas.documentos import DocumentoJsonRequest, DocumentoResponse, TipoArquivo, TipoDocumento
from app.services.documentos_service import DocumentosService
from app.services.logs_service import LogsService
from app.services.storage_service import StorageService
from app.core.supabase_client import get_supabase_client

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post('/json', response_model=DocumentoResponse, status_code=201)
def documentos_json(payload: DocumentoJsonRequest, response: Response):
    result = DocumentosService.criar_documento_json(payload)
    if result.get("duplicated"):
        response.status_code = 200
    return result


@router.post('/upload', response_model=DocumentoResponse, status_code=201)
async def documentos_upload(
    cliente_id: UUID = Form(...),
    tipo_arquivo: TipoArquivo = Form(...),
    origem: str = Form(...),
    hash_arquivo: str = Form(...),
    arquivo: UploadFile = File(...),
    tipo_documento: TipoDocumento = Form(default=TipoDocumento.nao_identificado),
    response: Response = None,
):
    cliente_id_str = str(cliente_id)
    DocumentosService._validar_cliente(cliente_id_str)
    duplicated = DocumentosService._check_duplicate(cliente_id_str, hash_arquivo)
    if duplicated:
        LogsService.log_event(documento_id=duplicated['id'], cliente_id=cliente_id_str, origem='backend_python', tipo_evento='duplicidade_detectada', mensagem='Documento duplicado detectado no upload', detalhes_json={'hash_arquivo': hash_arquivo})
        if response is not None:
            response.status_code = 200
        return {"documento_id": duplicated["id"], "duplicated": True, "status_processamento": duplicated.get("status_processamento") or "desconhecido", "status_ia": duplicated.get("status_ia") or "desconhecido", "mensagem": "Documento já existe para cliente_id + hash_arquivo."}

    metodo_extracao = DocumentosService._metodo_upload(tipo_arquivo.value)
    status_ia = "aguardando" if metodo_extracao == "ia_multimodal" else "nao_necessario"
    status_processamento = "aguardando_ia" if metodo_extracao == "ia_multimodal" else "recebido"

    file_bytes = await arquivo.read()
    path = StorageService.upload_document(cliente_id_str, hash_arquivo, arquivo.filename, file_bytes, arquivo.content_type)
    payload = {
        "cliente_id": cliente_id_str, "nome_arquivo": arquivo.filename, "tipo_arquivo": tipo_arquivo.value,
        "tipo_documento": tipo_documento.value, "origem": origem, "hash_arquivo": hash_arquivo,
        "storage_path": path, "tamanho_arquivo": len(file_bytes), "status_processamento": status_processamento,
        "metodo_extracao": metodo_extracao, "status_ia": status_ia, "texto_extraido": None,
        "json_recebido_robo": None, "json_extraido_ia": None, "json_final": None,
        "confianca_ia": None, "precisa_revisao": True, "mensagem_erro": None,
        "data_recebimento": datetime.now(timezone.utc).isoformat(), "data_processamento": None,
    }
    created = get_supabase_client().table('documentos').insert(payload).execute().data[0]
    LogsService.log_event(documento_id=created['id'], cliente_id=cliente_id_str, origem='backend_python', tipo_evento='upload_realizado', mensagem='Upload de documento realizado', detalhes_json={'storage_path': path})
    return {"documento_id": created['id'], "duplicated": False, "status_processamento": status_processamento, "status_ia": status_ia, "mensagem": "Documento enviado com sucesso.", "storage_path": path}


@router.post('/{documento_id}/reprocessar')
def reprocessar(documento_id: UUID):
    doc_resp = get_supabase_client().table('documentos').select('id,cliente_id,tipo_arquivo').eq('id', str(documento_id)).limit(1).execute()
    if not doc_resp.data:
        raise HTTPException(status_code=404, detail=f"Documento {documento_id} não encontrado.")
    doc = doc_resp.data[0]
    tipo = doc['tipo_arquivo']
    if tipo in {'imagem', 'pdf_imagem'}:
        status_processamento, status_ia, metodo_extracao = 'aguardando_ia', 'aguardando', 'ia_multimodal'
    elif tipo == 'xml':
        status_processamento, status_ia, metodo_extracao = 'recebido', 'nao_necessario', 'local_xml'
    elif tipo == 'pdf_texto':
        status_processamento, status_ia, metodo_extracao = 'recebido', 'nao_necessario', 'local_pdf_texto'
    else:
        status_processamento, status_ia, metodo_extracao = 'recebido', 'nao_necessario', 'nao_processado'

    get_supabase_client().table('documentos').update({'status_processamento': status_processamento, 'status_ia': status_ia, 'metodo_extracao': metodo_extracao}).eq('id', str(documento_id)).execute()
    LogsService.log_event(documento_id=str(documento_id), cliente_id=doc.get('cliente_id'), origem='backend_python', tipo_evento='reprocessamento_solicitado', mensagem='Reprocessamento solicitado', detalhes_json={'tipo_arquivo': tipo})
    return {'message': 'Solicitação de reprocessamento registrada com sucesso.', 'documento_id': str(documento_id), 'status_processamento': status_processamento, 'status_ia': status_ia, 'metodo_extracao': metodo_extracao}
