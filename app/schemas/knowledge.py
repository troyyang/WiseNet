from pydantic import BaseModel, Field
from . import BaseViewModel

class KnowledgeLibView(BaseViewModel):
    title: str = Field(max_length=200)
    content: str = Field(default=None, max_length=10000)
    status: str = Field(default=None, max_length=20)

class KnowledgeLibFind(BaseModel):
    keyword: str = Field(default=None, max_length=200)
    status: str = Field(default=None, max_length=20)
    time: str = Field(default=None, max_length=100)

class KnowledgeLibSubjectView(BaseViewModel):
    name: str = Field(max_length=200)
    knowledge_lib_id: int = Field()