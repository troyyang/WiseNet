from datetime import datetime
from pydantic import BaseModel, Field

class BaseViewModel(BaseModel):
    __abstract__ = True
    id: int = Field(default=None)
    create_time: datetime = Field(default=None)
    update_time: datetime = Field(default=None)
