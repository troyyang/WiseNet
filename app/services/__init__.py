import os
import datetime
from typing import Optional

from sqlalchemy.orm import make_transient

from core import config as config
from core.database import get_async_session
from sqlalchemy import select
from core.extends_logger import logger
from graph.document import Document
from graph.graph_query import KnowledgeGraphQuery
from models.models import KnowledgeLib, KnowledgeLibSubject


class BaseService:
    def __init__(self):
        self.knowledge_graph_query = KnowledgeGraphQuery()

    async def find_knowledge_lib_by_id(self, knowledge_lib_id: int, expunge: bool = True) -> Optional[KnowledgeLib]:
        """
        Finds a knowledge library by its ID.

        Args:
            knowledge_lib_id (int): The ID of the knowledge library.
            expunge (bool): Whether to expunge (detach) the object from the session.

        Returns:
            Optional[KnowledgeLib]: The knowledge library if found, otherwise None.
        """
        async with get_async_session() as session:  # ✅ Always create a new session
            try:
                result = await session.execute(
                    select(KnowledgeLib).filter(KnowledgeLib.id == knowledge_lib_id)
                )
                knowledge_lib = result.scalar_one_or_none()

                if knowledge_lib and expunge:
                    make_transient(knowledge_lib)  # ✅ Properly detach

                return knowledge_lib

            except Exception as e:
                logger.error(f"Failed to find knowledge library by ID {knowledge_lib_id}: {e}")
                raise RuntimeError(f"Failed to find knowledge library: {e}") from e

    async def update_knowledge_lib_status(self, lib_id: int, status: str) -> Optional[KnowledgeLib]:
        """
        Updates the status of a knowledge library.

        Args:
            lib_id (int): The ID of the knowledge library.
            status (str): The new status value.

        Returns:
            Optional[KnowledgeLib]: The updated knowledge library if found, otherwise None.
        """
        async with get_async_session() as session:
            result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == lib_id))
            entry = result.scalar_one_or_none()
            if not entry:
                return None

            try:
                entry.status = status
                entry.update_time = datetime.datetime.now()

                await session.commit()
                make_transient(entry)
                logger.debug(f"Updated generation status to '{status}' for library ID: {lib_id}.")
                return entry
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update knowledge library by ID {lib_id}: {e}")
                raise RuntimeError(f"Failed to update knowledge library: {e}")

    async def find_knowledge_lib_subject_by_id(self, subject_id: int, expunge: bool = True) -> Optional[KnowledgeLibSubject]:
        """
        Retrieves a specific knowledge library subject by its ID.

        Args:
            subject_id (int): The ID of the subject.
            expunge (bool): Whether to expunge the object from the session.

        Returns:
            Optional[KnowledgeLibSubject]: The KnowledgeLibSubject object if found, otherwise None.
        """
        async with get_async_session() as session:
            result = await session.execute(select(KnowledgeLibSubject).filter(KnowledgeLibSubject.id==subject_id))
            knowledge_lib_subject = result.scalar_one_or_none()
            if knowledge_lib_subject and expunge:
                # Detach the object from the session
                make_transient(knowledge_lib_subject)

        return knowledge_lib_subject

    def delete_graph_node_document_files_by_subject(self, lib_id: int, subject_id: int) -> None:
        """
        Deletes all document files associated with a knowledge library subject.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_id (int): The ID of the knowledge library subject.

        Returns:
            None
        """
        logger.info(f"Deleting document files for library with ID: {lib_id} and subject with ID: {subject_id}")
        try:
            documents = Document.get_documents_by_subject(lib_id, subject_id)
            if documents:
                for document in documents:
                    file_path = os.path.join(config.UPLOAD_DIR, document.saved_at)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.debug(f"Deleted document file: {file_path}")
                    else:
                        logger.warning(f"Document file not found: {file_path}")
            logger.info(
                f"Successfully deleted document files for library with ID: {lib_id} and subject with ID: {subject_id}")
        except Exception as e:
            logger.error(
                f"Failed to delete document files for library with ID {lib_id} and subject with ID {subject_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete document files: {e}") from e