import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import core.config as config
from core.error_handle import register_exception
from core.extends_logger import logger
from core.i18n import LanguageMiddleware
from core.middleware import NamingConventionMiddleware
from routers import register_router


# Add lifespan function to manage Redis client lifecycle and database session
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Application startup")
        yield
    finally:
        logger.info("Application shutdown")

def create_app():
    current_app = FastAPI(
        title="WiseNet",
        description="WiseNet is an intelligent knowledge base construction tool based on large language models (LLMs). By inputting a question, the system utilizes the reasoning capabilities of LLMs to automatically generate related sub-questions and progressively explore the depth and breadth of the question, forming a web-like domain knowledge base.",
        version="0.1.0",
        contact={
            "name": "Troy Yang",
            "email": "troy.yang2@gmail.com",
        },
        license_info={
            "name": "GPL-3.0",
        },
        lifespan=lifespan
    )

    # Configure CORS
    current_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    current_app.add_middleware(LanguageMiddleware)
    # the json key in request and response data will be converted to camelCase
    if config.IS_CAMEL_CASE:
        current_app.add_middleware(NamingConventionMiddleware)

    # Include routers
    register_router(current_app)

    register_exception(current_app)

    @current_app.get("/")
    async def read_root():
        return {"message": "Welcome to FastAPI!"}

    return current_app

app = create_app()

if __name__ == '__main__':
    # Add the current directory to the Python path
    root_path = os.getcwd()
    sys.path.append(root_path)
    # Run the FastAPI app
    uvicorn.run("main:app", host=config.API_HOST, port=int(config.API_PORT), reload=False, log_level='info', workers=4)