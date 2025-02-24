from fastapi import APIRouter

from api import auth, knowledge_lib, graph, llm, user

# 创建路由
api = APIRouter()

# auth
api.include_router(auth.router, prefix="/auth", tags=["auth"])
api.include_router(user.router, prefix="/user", tags=["user"])
api.include_router(knowledge_lib.router, prefix='/knowledge', tags=["knowledge"])
api.include_router(graph.router, prefix='/graph', tags=["Graph"])
api.include_router(llm.router, prefix='/llm', tags=["llm"])