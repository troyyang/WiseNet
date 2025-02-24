import keyword
from typing import List, Optional
from pydantic import Field, BaseModel, HttpUrl
from core.i18n import _
from core import config

class GraphConditionView(BaseModel):
    subject_ids: List[int] = Field(default_factory=list, description=_("List of subject IDs"))
    type: Optional[str] = Field(default=None, description=_("Type of the node"))
    content: Optional[str] = Field(default=None, description=_("Content of the node"))
    parent_type: Optional[str] = Field(default=None, description=_("Type of the parent node"))
    parent_element_id: Optional[str] = Field(default=None, description=_("Element ID of the parent node"))
    parent_content: Optional[str] = Field(default=None, description=_("Content of the parent node"))
    child_type: Optional[str] = Field(default=None, description=_("Type of the child node"))
    child_element_id: Optional[str] = Field(default=None, description=_("Element ID of the child node"))
    child_content: Optional[str] = Field(default=None, description=_("Content of the child node"))
    relationship_type: Optional[str] = Field(default=None, description=_("Type of the relationship"))

class GraphGenerateConditionView(BaseModel):
    lib_id: Optional[int] = Field(default=None, description=_("The library ID"))
    subject_id: Optional[int] = Field(default=None, description=_("The subject ID"))
    element_id: Optional[str] = Field(default=None, description=_("The element ID"))
    max_depth: int = Field(default=4, description=_("The max depth"))
    llm_name: str = Field(default=config.DEFAULT_LLM_NAME, description=_("The LLM name"))
    embedding_model: str = Field(default="sbert", description=_("The embedding model"))
    max_tokens_each_chunk: int = Field(default=128, description=_("The max tokens each chunk"))

class GraphAnalyzeConditionView(BaseModel):
    lib_id: Optional[int] = Field(default=None, description=_("The library ID"))
    subject_ids: List[int] = Field(default_factory=list, description=_("List of subject IDs"))
    llm_name: str = Field(default=config.DEFAULT_LLM_NAME, description=_("The LLM name"))
    embedding_model: str = Field(default="sbert", description=_("The embedding model"))
    max_tokens_each_chunk: int = Field(default=128, description=_("The max tokens each chunk"))

class ChatConditionView(BaseModel):
    lib_id: int = Field(description=_("The library ID"))
    subject_id: int = Field(default=None, description=_("The subject ID"))
    messages: List[str] = Field(default=None, description=_("The message")) # search node by message
    prompt_element_id: str = Field(default=None, description=_("The prompt element id")) # search node by prompt 
    related_node_element_id: str = Field(default=None, description=_("The related node element id")) # search node by related node
    only_title: bool = Field(default=False, description=_("The only title")) # only search title of node
    limit: int = Field(default=5, description=_("The limit"))
    offset: int = Field(default=0, description=_("The offset"))
    llm_name: str = Field(default=config.DEFAULT_LLM_NAME, description=_("The LLM name"))
    search_type: str = Field(default="vector", description=_("The search type")) # fulltext, vector, hybrid
    search_scope: List[str] = Field(default=["question", "page", "document", "webpage", "node"], description=_("The search scope")) # the order of scope element will effect the priority
    return_method: str = Field(default="sync", description=_("The return method"))  # sync or stream
    is_summary: bool = Field(default=True, description=_("The is summary"))
    chain_type: str = Field(default="stuff", description=_("The chain type")) # stuff, refine, map-reduce
    embedding_model: str = Field(default="sbert", description=_("The embedding model"))
    max_tokens_each_chunk: int = Field(default=128, description=_("The max tokens each chunk"))

class GraphNodeView(BaseModel):
    lib_id: Optional[int] = Field(default=None, description=_("The library ID"))
    subject_id: Optional[int] = Field(default=None, description=_("The subject ID"))
    parent_element_id: Optional[str] = Field(default=None, description=_("The parent element ID"))
    element_id: Optional[str] = Field(default=None, description=_("The element ID"))
    content: str = Field(max_length=8192, description=_("The content"))
    embedding_model: str = Field(default="sbert", description=_("The embedding model"))
    max_tokens_each_chunk: int = Field(default=128, description=_("The max tokens each chunk"))

class GraphRelationshipView(BaseModel):
    lib_id: Optional[int] = Field(default=None, description=_("The library ID"))
    subject_id: Optional[int] = Field(default=None, description=_("The subject ID"))
    element_id: Optional[str] = Field(default=None, description=_("The element ID"))
    source_element_id: Optional[str] = Field(default=None, description=_("The source element ID"))
    target_element_id: Optional[str] = Field(default=None, description=_("The target element ID"))
    type: Optional[str] = Field(default=None, description=_("The type"))
    content: Optional[str] = Field(default=None, description=_("The content"))
    embedding_model: str = Field(default="sbert", description=_("The embedding model"))
    max_tokens_each_chunk: int = Field(default=128, description=_("The max tokens each chunk"))

class GraphWebPageView(BaseModel):
    lib_id: int = Field(description=_("The library ID"))
    subject_id: int = Field(description=_("The subject ID"))
    element_id: str = Field(description=_("The element ID"))
    url: HttpUrl = Field(max_length=2048, description=_("The URL"))