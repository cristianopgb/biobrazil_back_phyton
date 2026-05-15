from datetime import date
from uuid import UUID
from pydantic import BaseModel
from app.schemas.documentos import TipoDocumento


class ExportacaoGerarRequest(BaseModel):
    usuario_id: UUID
    cliente_id: UUID
    periodo_inicio: date
    periodo_fim: date
    tipo_documento: TipoDocumento | None = None
    status: str | None = None


class ExportacaoGerarResponse(BaseModel):
    exportacao_id: str
    status_exportacao: str


class ExportacaoStatusResponse(BaseModel):
    exportacao_id: str
    status_exportacao: str
    arquivo_storage_path: str | None = None
    mensagem_erro: str | None = None
