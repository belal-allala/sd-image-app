from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """Route de statut simple."""
    return {"status": "ok", "service": "Visionary V4 API"}
