



from fastapi import APIRouter
from app.services.groq.connection import test_groq_connection
from app.services.postgres.connection import test_postgres_connection as run_postgres_test

router = APIRouter(prefix="/health",tags=["Health"])




@router.get("")
async def health_check():
    return {"status": "healthy"}

@router.get("/groq")
def test_groq_connections():
    return {
        "groq": test_groq_connection(),
    }

@router.get("/postgres")
def test_postgres_connections():
    return {
        "postgres": run_postgres_test(),
    }
