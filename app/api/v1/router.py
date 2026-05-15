from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.documentos import router as documentos_router
from app.api.v1.endpoints.exportacoes import router as exportacoes_router

router = APIRouter(prefix='/api/v1')
router.include_router(health_router)
router.include_router(documentos_router)
router.include_router(exportacoes_router)
