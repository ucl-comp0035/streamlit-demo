from fastapi import APIRouter
from backend.data.database import engine
from backend.services.query_service import QueryService

router = APIRouter(
    prefix="/api/paralympics",
    tags=["Paralympics"]
)

@router.get("/all")
def get_all_paralympics_data():
    qs = QueryService(engine)
    data = qs.get_all_games_data_flattened()
    return data