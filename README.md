# Coletor Contábil API (Fase 1)

## Configuração
Crie `.env` com:

- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- FRONTEND_ORIGIN
- ENVIRONMENT=development
- OPENAI_API_KEY= (opcional, não usado)

## Rodar local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints
- GET `/api/v1/health`
- POST `/api/v1/documentos/json`
- POST `/api/v1/documentos/upload`
- POST `/api/v1/documentos/{documento_id}/reprocessar`
- POST `/api/v1/exportacoes/gerar`
- GET `/api/v1/exportacoes/{exportacao_id}/status`

## Exemplos de payload
### POST /api/v1/documentos/json
```json
{
  "cliente_id": "11111111-1111-1111-1111-111111111111",
  "nome_arquivo": "nota-123.xml",
  "tipo_arquivo": "xml",
  "hash_arquivo": "abc123",
  "origem": "robo_local",
  "tipo_documento": "nota_servico",
  "texto_extraido": "texto já extraído pelo robô",
  "json_final": {"campos": "normalizados"},
  "nota": {
    "tipo_documento": "nota_servico",
    "numero_nota": "123",
    "serie": "A1",
    "data_emissao": "2026-01-10",
    "prestador_nome": "Fornecedor Exemplo",
    "prestador_cnpj": "12345678000199",
    "tomador_nome": "Cliente Exemplo",
    "tomador_cnpj": "99887766000155",
    "valor_bruto": 1500.0,
    "valor_servico": 1400.0,
    "iss": 50.0,
    "irrf": 0,
    "pis": 0,
    "cofins": 0,
    "csll": 0,
    "inss": 0,
    "valor_liquido": 1450.0
  }
}
```

### POST /api/v1/exportacoes/gerar
```json
{
  "usuario_id": "22222222-2222-2222-2222-222222222222",
  "cliente_id": "11111111-1111-1111-1111-111111111111",
  "periodo_inicio": "2026-01-01",
  "periodo_fim": "2026-01-31",
  "tipo_documento": "nota_servico",
  "status": "aprovado"
}
```

## Render
Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Health check path: `/api/v1/health`

