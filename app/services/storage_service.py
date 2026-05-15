from app.core.supabase_client import get_supabase_client


class StorageService:
    BUCKET = "documentos-originais"

    @staticmethod
    def upload_document(cliente_id: str, hash_arquivo: str, nome_arquivo: str, file_bytes: bytes, content_type: str | None) -> str:
        path = f"{cliente_id}/{hash_arquivo}_{nome_arquivo}"
        get_supabase_client().storage.from_(StorageService.BUCKET).upload(
            path,
            file_bytes,
            {"content-type": content_type or "application/octet-stream", "upsert": "false"},
        )
        return path
