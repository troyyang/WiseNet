from fastapi import APIRouter
from schemas.result import ok
from ai.llm import Llm
from ai.embedding import EmbeddingFactory

router = APIRouter()

@router.get("/all")
def available_llms():
    return ok({"llms": Llm.all_llms(), "embeddings": EmbeddingFactory.all_embeddings()})