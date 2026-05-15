from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class TipoArquivo(str, Enum):
    xml = "xml"
    pdf_texto = "pdf_texto"
    pdf_imagem = "pdf_imagem"
    imagem = "imagem"
    outro = "outro"


class TipoDocumento(str, Enum):
    nota_produto = "nota_produto"
    nota_servico = "nota_servico"
    recibo = "recibo"
    fatura = "fatura"
    boleto = "boleto"
    outro = "outro"
    nao_identificado = "nao_identificado"


class NotaPayload(BaseModel):
    numero_nota: str | None = None
    serie: str | None = None
    data_emissao: date | None = None
    prestador_nome: str | None = None
    prestador_cnpj: str | None = None
    tomador_nome: str | None = None
    tomador_cnpj: str | None = None
    valor_bruto: Decimal | None = None


class DocumentoJsonRequest(BaseModel):
    cliente_id: UUID
    nome_arquivo: str
    tipo_arquivo: TipoArquivo
    hash_arquivo: str
    origem: str = "robo_local"
    tipo_documento: TipoDocumento = TipoDocumento.nao_identificado
    nota: NotaPayload | None = None


class DocumentoResponse(BaseModel):
    documento_id: str
    duplicated: bool
    status_processamento: str
    status_ia: str
    mensagem: str
    storage_path: str | None = None
