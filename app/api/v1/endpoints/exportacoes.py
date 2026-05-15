from uuid import UUID
from fastapi import APIRouter
from app.schemas.exportacoes import ExportacaoGerarRequest
from app.services.exportacoes_service import ExportacoesService

router = APIRouter(prefix="/exportacoes", tags=["exportacoes"])


@router.post('/gerar')
def gerar_exportacao(payload: ExportacaoGerarRequest):
    return ExportacoesService.gerar_exportacao(payload)


@router.get('/{exportacao_id}/status')
def status_exportacao(exportacao_id: UUID):
    return ExportacoesService.status_exportacao(str(exportacao_id))
