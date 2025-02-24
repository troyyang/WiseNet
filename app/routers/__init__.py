
from fastapi import FastAPI, Depends

from routers.router import api
from core.middleware import login_required


# register_router
def register_router(app: FastAPI):
    # router collection
    app.include_router(
        api,
        prefix="/api",
        tags=["Wisenet"],
        # depend
        dependencies=[Depends(login_required)],
    )
