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
  "tipo_documento": "nota_servico"
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

## Observação de schema exportacoes
Caso o schema da tabela `exportacoes` ainda não tenha `cliente_id`, o sistema mantém `cliente_id` dentro de `filtros_json`. Recomendado adicionar `cliente_id` na tabela futuramente.
