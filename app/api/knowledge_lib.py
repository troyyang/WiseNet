from fastapi import APIRouter, HTTPException, Depends
from core.extends_logger import logger
from core.i18n import _
from models.models import KnowledgeLib
from schemas.knowledge import KnowledgeLibView, KnowledgeLibSubjectView, KnowledgeLibFind
from schemas.result import ok, failed
from services.graph_query_service import GraphQueryService
from services.knowledge_lib_service import KnowledgeLibService

router = APIRouter()

# 定义依赖函数来创建 KnowledgeLibService 实例
def get_knowledge_lib_service():
    return KnowledgeLibService()

# 定义依赖函数来创建 GraphQueryService 实例
def get_graph_query_service():
    return GraphQueryService()


@router.post("/lib")
async def create_knowledge_lib(knowledge_data: KnowledgeLibView,
                               knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result: KnowledgeLib = await knowledge_lib_service.create_knowledge_lib(knowledge_data)
        return ok(result.to_dict() if result else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error creating knowledge lib: {e}")
        return failed(data=None, msg=str(e))


@router.get("/lib/{knowledge_id}")
async def read_knowledge_lib(knowledge_id: int,
                             knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.find_knowledge_lib_by_id(knowledge_id)
        if not result:
            return failed(status_code=404, msg=_("Knowledge lib not found"))

        return ok(result.to_dict() if result else None)
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error finding knowledge lib: {e}")
        return failed(data=None, msg=str(e))


@router.post("/lib/find")
async def find_knowledge_libs(condition: KnowledgeLibFind,
                              knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.find_knowledge_libs_by_condition(condition)
        return ok([entry.to_dict() for entry in result])
    except Exception as e:
        logger.error(f"Error finding knowledge lib: {e}")
        return failed(data=None, msg=str(e))

@router.post("/lib/search")
async def search_knowledge_libs(condition: KnowledgeLibFind,
                                knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        condition.status = 'PUBLISHED'
        result = await knowledge_lib_service.find_knowledge_libs_by_condition(condition)
        return ok([entry.to_dict() for entry in result])
    except Exception as e:
        logger.error(f"Error searching knowledge lib: {e}")
        return failed(data=None, msg=str(e))


@router.put("/lib")
async def update_knowledge_lib(knowledge_data: KnowledgeLibView,
                               knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.update_knowledge_lib(knowledge_data)
        if not result:
            return failed(data=None, msg=_("Knowledge not found"))
        return ok(result.to_dict() if result else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error updating knowledge lib: {e}")
        return failed(data=None, msg=str(e))


@router.delete("/lib/{knowledge_id}")
async def delete_knowledge_lib(knowledge_id: int,
                               knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.delete_knowledge_lib(knowledge_id)
        if not result:
            return failed(data=None, msg=_("Knowledge not found"))
        return ok({"success": result})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error deleting knowledge lib: {e}")
        return failed(data=None, msg=str(e))

@router.get("/lib/publish/{knowledge_id}")
async def toggle_knowledge_lib_publish(knowledge_id: int,
                            knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.toggle_knowledge_lib_publish(knowledge_id)
        if not result:
            return failed(data=None, msg=_("Knowledge not found"))
        return ok(result.to_dict() if result else None)
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error deleting knowledge lib: {e}")
        return failed(data=None, msg=str(e))

@router.post("/subject")
async def create_knowledge_lib_subject(subject_data: KnowledgeLibSubjectView,
                                       knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.create_knowledge_lib_subject(subject_data)
        return ok(result.to_dict() if result else None)
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error creating knowledge lib subject: {e}")
        return failed(data=None, msg=str(e))


@router.get("/subject/{subject_id}")
async def read_knowledge_lib_subject(subject_id: int,
                                     knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.find_knowledge_lib_subject_by_id(subject_id)
        if not result:
            return failed(data=None, msg=_("Subject not found"))
        return ok(result.to_dict() if result else None)
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error finding knowledge lib subjects: {e}")
        return failed(data=None, msg=str(e))


@router.get("/subject/find/{knowledge_lib_id}")
async def find_knowledge_subjects(knowledge_lib_id: int,
                                  knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.find_knowledge_lib_subjects(knowledge_lib_id)
        return ok([entry.to_dict() for entry in result])
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error finding knowledge lib subjects: {e}")
        return failed(data=None, msg=str(e))


@router.put("/subject")
async def update_knowledge_lib_subject(subject_data: KnowledgeLibSubjectView,
                                       knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.update_knowledge_lib_subject(subject_data)
        if not result:
            return failed(data=None, msg=_("Knowledge lib subject not found"))
        return ok(result.to_dict())
    except ValueError as e:
        return failed(data=None, msg=str(e))
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error updating knowledge lib subject: {e}")
        return failed(data=None, msg=str(e))


@router.delete("/subject/{subject_id}")
async def delete_knowledge_lib_subject(subject_id: int,
                                       knowledge_lib_service: KnowledgeLibService = Depends(get_knowledge_lib_service)):
    try:
        result = await knowledge_lib_service.delete_knowledge_lib_subject(subject_id)
        if not result:
            return failed(data=None, msg=_("Subject not found"))
        return ok({"success": result})
    except HTTPException as e:
        return failed(data=None, msg=str(e))
    except Exception as e:
        logger.error(f"Error deleting knowledge lib subject: {e}")
        return failed(data=None, msg=str(e))