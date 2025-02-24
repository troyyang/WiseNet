import json
import os
import shutil
import uuid
from typing import Optional, AsyncGenerator

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends
from starlette.responses import FileResponse, StreamingResponse

import core.config as config
from core.extends_logger import logger
from core.i18n import _
from graph.document import Document
from graph.webpage import WebPage
from schemas.graph import GraphConditionView, GraphGenerateConditionView, GraphNodeView, GraphRelationshipView, \
    GraphWebPageView, ChatConditionView, GraphAnalyzeConditionView
from schemas.result import ok, failed
from services.graph_query_service import KnowledgeQueryResult
from services.graph_service import GraphService
from services.knowledge_lib_service import KnowledgeLibService

router = APIRouter()

def get_knowledge_lib_service():
    return KnowledgeLibService()

def get_graph_service():
    return GraphService()

@router.get("/initialize")
async def initialize_graph(graph_service: GraphService = Depends(get_graph_service)):
    try:
        await graph_service.initialize_graph()
        result = {
            "success": True
        }
        return ok(result)
    except Exception as e:
        logger.error(f"initialize_graph error: {e}")
        return failed(data=None, msg=str(e))


@router.post("/query/{lib_id}")
async def query_graph(lib_id: int, 
                            condition: GraphConditionView, 
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        logger.debug(f"query_graph lib_id: {lib_id}, condition: {condition}")
        nodes, node_overviews, links, link_overviews, status = await graph_service.query_graph(lib_id, condition)

        result = {
            "nodes": [node.to_dict() for node in nodes],
            "links": [link.to_dict() for link in links],
            "overview": {"nodes" : [overview.to_dict() for overview in node_overviews],
                            "links": [overview.to_dict() for overview in link_overviews]},
            "status": status
        }
        return ok(result)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"query_graph error: {e}")
        return failed(data=None, msg=str(e))


@router.post("/generate")
async def generate_knowledge_graph(generate_data: GraphGenerateConditionView, 
                                    background_tasks: BackgroundTasks,
                                    knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service),
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        lib_id = generate_data.lib_id
        subject_id = generate_data.subject_id
        llm_name = generate_data.llm_name
        embedding_model = generate_data.embedding_model
        max_depth = generate_data.max_depth

        if not lib_id or not subject_id:
            return failed(data=None, msg=_("lib_id and subject_id are required"))

        knowledge_lib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if not knowledge_lib:
            return failed(data=None, msg=_("Knowledge lib not found"))

        if knowledge_lib.status == 'GENERATING' or knowledge_lib.status == 'ANALYZING':
            logger.warning(f"Graph generation or analysis is already in progress for library ID: {lib_id}.")
            return failed(data=None, msg=_("Graph generation or analysis is already in progress."))

        if knowledge_lib.status == 'PUBLISHED':
            logger.warning(f"Library is published. Please unpublish the library first.")
            return failed(data=None, msg=_("Library is published. Please unpublish the library first."))

        knowledge_subject = await knowledge_lib_service.find_knowledge_lib_subject_by_id(subject_id)
        if not knowledge_subject:
            return failed(data=None, msg=_("Knowledge subject not found"))

        background_tasks.add_task(graph_service.generate_graph, lib_id, subject_id, llm_name, max_depth, embedding_model)

        return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"generate_knowledge_graph error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/analyze")
async def analyze_knowledge_graph(analyze_data: GraphAnalyzeConditionView, 
                                    knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service),
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        lib_id = analyze_data.lib_id
        subject_ids = analyze_data.subject_ids
        llm_name = analyze_data.llm_name
        embedding_model = analyze_data.embedding_model
        max_tokens_each_chunk = analyze_data.max_tokens_each_chunk

        if not lib_id or not subject_ids:
            return failed(data=None, msg=_("lib_id and subject_id are required"))

        knowledge_lib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if not knowledge_lib:
            return failed(data=None, msg=_("Knowledge lib not found"))

        if knowledge_lib.status == 'GENERATING' or knowledge_lib.status == 'ANALYZING':
            return failed(data=None, msg=_("Knowledge lib is generating or analyzing"))

        # background_tasks.add_task(graph_service.analyze_graph, lib_id, subject_ids, llm_name, embedding_model, max_tokens_each_chunk)
        await graph_service.analyze_graph(lib_id, subject_ids, llm_name, embedding_model, max_tokens_each_chunk)

        return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"analyze_knowledge_graph error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/cancel/{lib_id}")
async def cancel_graph(lib_id: int, 
                        graph_service: GraphService = Depends(get_graph_service)):
    try:
        await graph_service.cancel_generate_graph(lib_id)
        return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"cancel_generate_graph error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/node/{node_element_id}")
async def delete_graph_node(node_element_id: str,
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node(node_element_id)
        return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_groph_node error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/relationship/{relationship_element_id}")
async def delete_graph_relationship(relationship_element_id: str,
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_relationship(relationship_element_id)
        return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_relationship error: {e}")
        return failed(data=None, msg=str(e))


@router.post("/node")
async def add_graph_node(node: GraphNodeView,
                         graph_service: GraphService = Depends(get_graph_service)):
    try:
        node, relationship = graph_service.add_node_by_human(node)
        return ok({"node": node.to_dict(), "relationship": relationship.to_dict() if relationship else None} if node else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"add_groph_node error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/relationship")
async def add_graph_relationship(relationship: GraphRelationshipView,
                                 graph_service: GraphService = Depends(get_graph_service)):
    try:
        relationship = graph_service.add_relationship_by_human(relationship)
        return ok(relationship.to_dict() if relationship else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"add_groph_relationship error: {e}")
        return failed(data=None, msg=str(e))

@router.put("/node")
async def update_graph_node(node: GraphNodeView,
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        result = graph_service.update_graph_node(node)
        return ok(result.to_dict() if result else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"update_graph_node error: {e}")
        return failed(data=None, msg=str(e))

@router.put("/relationship/info")
async def update_graph_relationship_info(relationship: GraphRelationshipView,
                                         graph_service: GraphService = Depends(get_graph_service)):
    try:
        result = graph_service.update_relationship_info(relationship)
        return ok(result.to_dict())
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"update_graph_relationship_info error: {e}")
        return failed(data=None, msg=str(e))

@router.get("/node/{node_element_id}")
async def get_graph_node_detail(node_element_id: str,
                                graph_service: GraphService = Depends(get_graph_service)):
    try:
        result = graph_service.get_graph_node_detail(node_element_id)
        return ok(result.to_dict() if result else None)
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"get_graph_node_detail error: {e}")
        return failed(data=None, msg=str(e))

@router.get("/relationship/{relationship_element_id}")
async def get_graph_relationship_detail(relationship_element_id: str,
                                        graph_service: GraphService = Depends(get_graph_service)):
    try:
        result = graph_service.get_graph_relationship_detail(relationship_element_id)
        return ok(result.to_dict() if result else None)
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"get_graph_relationship_detail error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/overview/{lib_id}")
async def query_graph_overview(lib_id: int, condition:GraphConditionView,
                                graph_service: GraphService = Depends(get_graph_service)):
    try:
        node_overviews, link_overviews = graph_service.query_graph_overview(lib_id, condition)
        return ok({"nodes": [node_overview.to_dict() for node_overview in node_overviews],
        "links": [link_overview.to_dict() for link_overview in link_overviews]})

    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"query_graph_overview error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/generate/answer")
async def generate_answer(data: GraphGenerateConditionView,
                         graph_service: GraphService = Depends(get_graph_service)):
    try:
        node, relationship = graph_service.generate_answer(data)
        return ok({"node": node.to_dict(), "relationship": relationship.to_dict()})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"generate_answer error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/generate/prompts")
async def generate_prompts(data: GraphGenerateConditionView,
                           graph_service: GraphService = Depends(get_graph_service)):
    try:
        nodes, relationships = graph_service.generate_prompts(data)
        return ok({"nodes": [node.to_dict() for node in nodes],
                    "relationships": [relationships.to_dict() for relationships in relationships]})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"generate_prompts error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/generate/questions")
async def generate_questions(data: GraphGenerateConditionView,
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        nodes, relationships = graph_service.generate_questions(data)
        return ok({"nodes": [node.to_dict() for node in nodes],
                    "relationships": [relationships.to_dict() for relationships in relationships]})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"generate_questions error: {e}")
        return failed(data=None, msg=str(e))

@router.post("/node/analyze")
async def analyze_graph_node(data: GraphGenerateConditionView,
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        node = await graph_service.analyze_graph_node(data)
        return ok(node.to_dict() if node else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"analyze_graph_node error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/node/entity/{entity_element_id}/{node_element_id}")
async def delete_graph_node_entity(entity_element_id: str, node_element_id: str,
                                   graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node_entity(entity_element_id, node_element_id)
        return ok({"success": True})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_node_entity error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/node/keyword/{keyword_element_id}/{node_element_id}")
async def delete_graph_node_keyword(keyword_element_id: str, node_element_id: str,
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node_keyword(keyword_element_id, node_element_id)
        return ok({"success": True})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_node_keyword error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/node/tag/{tag_element_id}/{node_element_id}")
async def delete_graph_node_tag(tag_element_id: str, node_element_id: str,
                                graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node_tag(tag_element_id, node_element_id)
        return ok({"success": True})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_node_tag error: {e}")
        return failed(data=None, msg=str(e))

@router.delete("/node/document/{document_element_id}")
async def delete_graph_node_document(document_element_id: str,
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node_document(document_element_id)
        return ok({"success": True})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_node_document error: {e}")
        return failed(data=None, msg=str(e))

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
UPLOAD_DIR = os.path.join(BASE_DIR, config.UPLOAD_DIR)
ALLOWED_FILE_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/markdown"}

@router.post("/node/upload/file")
async def upload_document_file(
    file: UploadFile = File(...),
    lib_id: int = Form(...),
    subject_id: int = Form(...),
    element_id: str = Form(...),
    graph_service: GraphService = Depends(get_graph_service),
):
    try:
        # confirm UPLOAD_DIR exists
        # when upload file, check if UPLOAD_DIR exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # when upload file, check file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # read file size bytes from file position and reset
        if file_size > config.MAX_FILE_SIZE:
            return failed(data=None, msg=_("File size exceeds {max_file_size} limit".format(max_file_size=config.MAX_FILE_SIZE)))

        # check file type
        if file.content_type not in ALLOWED_FILE_TYPES:
            return failed(data=None, msg=_("Unsupported file type"))

        # generate a unique file name
        unique_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{unique_id}{file_ext}"
        file_path = os.path.join(config.UPLOAD_DIR, new_filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        document_node = graph_service.upload_graph_node_file(lib_id, subject_id, element_id, new_filename, file.filename)
        return ok(data=document_node.to_dict()) if document_node else failed(data=None, msg=_("Upload directory not found"))
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        return failed(data=None, msg=_("Upload directory not found"))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"upload_file error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))

@router.get("/node/download/file/{filename}")
async def download_document_file(filename: str):
    try:
        file_path = os.path.join(config.UPLOAD_DIR, filename)
        return FileResponse(file_path)
    except HTTPException as e:
        return None
    except Exception as e:
        logger.error(f"download_file error: {e}")
        return None


@router.post("/node/document/analyze")
async def analysis_document(data: GraphGenerateConditionView,
                            graph_service: GraphService = Depends(get_graph_service)):
    try:
        element_id = data.element_id
        if element_id is None:
            return failed(data=None, msg=_("Element id must be provided."))

        document: Document = graph_service.analyze_graph_node_file(element_id, data.llm_name,
                                                                           data.embedding_model,
                                                                           data.max_tokens_each_chunk)
        return ok(document.to_dict())
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"analysis_document error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))



@router.get("/node/document/detail/{document_element_id}")
async def get_document_detail(document_element_id:str,
                              graph_service: GraphService = Depends(get_graph_service)):
    try:
        document: Document = graph_service.get_document_detail(document_element_id)
        if not document:
            return failed(data=None, msg=_("Document not found"))
        return ok(document.to_dict())
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"get_document_detail error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))


@router.post("/node/webpage")
async def add_graph_node_webpage(data: GraphWebPageView,
                                 graph_service: GraphService = Depends(get_graph_service)):
    try:
        lib_id = data.lib_id
        subject_id = data.subject_id
        element_id = data.element_id
        url = str(data.url) if data.url else None
        if not lib_id or not subject_id or not element_id or not url:
            return failed(data=None, msg=_("Lib id, subject id, element id and url must be provided."))

        webpage: WebPage = graph_service.add_graph_node_webpage(lib_id, subject_id, element_id, url)
        return ok(webpage.to_dict())
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"add_graph_node_webpage error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))

@router.post("/node/webpage/analyze")
async def analyze_graph_node_webpage(data: GraphGenerateConditionView,
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        element_id = data.element_id
        if not element_id:
            return failed(data=None, msg=_("Element id must be provided."))

        webpage: WebPage = graph_service.analyze_graph_node_webpage(element_id, data.llm_name,
                                                                            data.embedding_model,
                                                                            data.max_tokens_each_chunk)
        return ok(webpage.to_dict())
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"analyze_graph_node_webpage error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))

@router.get("/node/webpage/{webpage_element_id}")
async def get_graph_node_webpage(webpage_element_id: str,
                                graph_service: GraphService = Depends(get_graph_service)):
    try:
        if not webpage_element_id:
            return failed(data=None, msg=_("Element id must be provided."))

        webpage: WebPage = graph_service.get_analyzed_graph_node_webpage(webpage_element_id)
        return ok(webpage.to_dict())
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"get_analyzed_graph_node_webpage error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))

@router.delete("/node/webpage/{webpage_element_id}")
async def delete_graph_node_webpage(webpage_element_id: str,
                                    graph_service: GraphService = Depends(get_graph_service)):
    try:
        graph_service.delete_graph_node_webpage(webpage_element_id)
        return ok({"success": True})
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"delete_graph_node_webpage error: {e}")
        return failed(data=None, msg=_("An unexpected error occurred"))

@router.post("/search")
async def search_knowledge_graph(
    query_condition: ChatConditionView,
    graph_service: GraphService = Depends(get_graph_service),
):
    """
    Queries the knowledge graph and streams the results incrementally.

    Args:
        query_condition (ChatConditionView): The conditions for querying the knowledge graph.
        graph_service (GraphService): The graph service instance.

    Returns:
        StreamingResponse: A streaming response containing partial results.
    """
    if query_condition.return_method != "stream":
        try:
            # Fallback to synchronous response
            knowledge_query_result: Optional[KnowledgeQueryResult] = await graph_service.search_knowledge_graph(query_condition)
            if not knowledge_query_result:
                return failed(data=None, msg=_("Empty result"))

            # Convert the result to a JSON object
            result_dict = {
                "text": knowledge_query_result.text,
                "main_node": knowledge_query_result.main_node.to_dict(filter=["element_id", "title", "content"]) if knowledge_query_result.main_node else None,
                "entities": [entity.to_dict(filter=["element_id", "content"]) for entity in knowledge_query_result.entities or []],
                "keywords": [keyword.to_dict(filter=["element_id", "content"]) for keyword in knowledge_query_result.keywords or []],
                "tags": [tag.to_dict(filter=["element_id", "content"]) for tag in knowledge_query_result.tags or []],
                "webpage": knowledge_query_result.webpage.to_dict(filter=["element_id", "url", "title", "content"]) if knowledge_query_result.webpage else None,
                "document": knowledge_query_result.document.to_dict(filter=["element_id", "name", "saved_at", "title", "content"]) if knowledge_query_result.document else None,
                "prompts": [prompt.to_dict(filter=["element_id", "content"]) for prompt in knowledge_query_result.prompts or []],
                "related_nodes": [related_node.to_dict(filter=["element_id", "title", "content"]) for related_node in knowledge_query_result.related_nodes or []]
            }

            # Return the JSON object as a response
            return ok(data=result_dict)
        except ValueError as e:
            logger.error(f"query_knowledge_graph error: {e}")
            return failed(data=None, msg=str(e))
        except HTTPException as e:
            logger.error(f"query_knowledge_graph error: {e}")
            return failed(data=None, msg=str(e))
        except Exception as e:
            logger.error(f"query_knowledge_graph error: {e}")
            return failed(data=None, msg=_("An unexpected error occurred"))


    # Streaming response
    async def generate_stream() -> AsyncGenerator[str, None]:
        """
        Generates a stream of JSON objects representing partial results.
        """
        try:
            async for result in await graph_service.search_knowledge_graph(query_condition):
                # Convert the result to a JSON object
                result_dict = {
                    "text": result.text,
                    "main_node": result.main_node.to_dict(filter=["element_id", "title", "content"]) if result.main_node else None,
                    "entities": [entity.to_dict(filter=["element_id", "content"]) for entity in result.entities or []],
                    "keywords": [keyword.to_dict(filter=["element_id", "content"]) for keyword in result.keywords or []],
                    "tags": [tag.to_dict(filter=["element_id", "content"]) for tag in result.tags or []],
                    "webpage": result.webpage.to_dict(filter=["element_id", "url", "title", "content"]) if result.webpage else None,
                    "document": result.document.to_dict(filter=["element_id", "name", "saved_at", "title", "content"]) if result.document else None,
                    "prompts": [prompt.to_dict(filter=["element_id", "content"]) for prompt in result.prompts or []],
                    "related_nodes": [related_node.to_dict(filter=["element_id", "title", "content"]) for related_node in result.related_nodes or []]
                }
                if config.IS_CAMEL_CASE:
                    import core.middleware as middleware
                    transformed_data = middleware.convert_keys(result_dict, middleware.to_camel_case)
                    # Yield the JSON object as a string
                    yield json.dumps(transformed_data) + "\n"
                else:
                    # Yield the JSON object as a string
                    yield json.dumps(result_dict) + "\n"
            # Yield the end of the stream
            yield json.dumps({"end": True}) + "\n"
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield json.dumps({"error": str(e)}) + "\n"

    # Return the streaming response
    streaming_response = StreamingResponse(generate_stream(), media_type="application/x-ndjson")
    streaming_response.headers["X-Streaming-Response"] = "true"
    return streaming_response