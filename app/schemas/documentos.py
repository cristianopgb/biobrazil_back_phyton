from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(extra='allow')

    tipo_documento: TipoDocumento | None = None
    numero_nota: str | None = None
    serie: str | None = None
    data_emissao: date | None = None
    prestador_nome: str | None = None
    prestador_cnpj: str | None = None
    tomador_nome: str | None = None
    tomador_cnpj: str | None = None
    valor_bruto: Decimal | float | None = None
    valor_servico: Decimal | float | None = None
    iss: Decimal | float | None = None
    irrf: Decimal | float | None = None
    pis: Decimal | float | None = None
    cofins: Decimal | float | None = None
    csll: Decimal | float | None = None
    inss: Decimal | float | None = None
    valor_liquido: Decimal | float | None = None


class DocumentoJsonRequest(BaseModel):
    cliente_id: UUID
    nome_arquivo: str
    tipo_arquivo: TipoArquivo
    hash_arquivo: str
    origem: str = "robo_local"
    tipo_documento: TipoDocumento = TipoDocumento.nao_identificado
    texto_extraido: str | None = None
    json_final: dict | None = None
    nota: NotaPayload | None = None


class DocumentoResponse(BaseModel):
    documento_id: str
    duplicated: bool
    status_processamento: str
    status_ia: str
    mensagem: str
    storage_path: str | None = None
