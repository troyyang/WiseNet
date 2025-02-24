import datetime
import os
from typing import Optional, List, Any, Coroutine

from sqlalchemy import select, or_
from sqlalchemy.orm import make_transient

import core.config as config
import core.database as db
from ai.llm import Llm
from core.extends_logger import logger
from core.i18n import _
from graph.document import Document
from graph.gds_graph import GdsGraph
from models.models import KnowledgeLib, KnowledgeLibSubject
from schemas.knowledge import KnowledgeLibSubjectView
from schemas.knowledge import KnowledgeLibView, KnowledgeLibFind
from . import BaseService


class KnowledgeLibService(BaseService):
    def __init__(self):
        super(KnowledgeLibService, self).__init__()


    # -------------------- Knowledge Library CRUD --------------------

    async def create_knowledge_lib(self, knowledge_data: KnowledgeLibView) -> KnowledgeLib:
        """
        Creates a new knowledge library entry.

        Args:
            knowledge_data (KnowledgeLibView): The data for the new knowledge library.

        Returns:
            KnowledgeLib: The newly created knowledge library entry.

        Raises:
            ValueError: If the title is not provided.
        """
        if not knowledge_data.title:
            raise ValueError(_("Title must be provided."))

        async with db.get_async_session() as session:
            try:
                template = Llm.get_prompt_template("content")
                knowledge_data.content = Llm.get_ai_response(
                    template.format(input=knowledge_data.title), config.DEFAULT_LLM_NAME
                )

                new_entry = KnowledgeLib(
                    title=knowledge_data.title,
                    content=knowledge_data.content,
                    create_time=datetime.datetime.now(),
                    update_time=datetime.datetime.now()
                )
            
                session.add(new_entry)
                await session.commit()
                await session.refresh(new_entry)

                logger.info(f"Successfully created knowledge library with ID: {new_entry.id}")
                return new_entry

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create knowledge library: {e}")
                raise

    async def find_knowledge_libs_by_condition(
        self, condition: KnowledgeLibFind = KnowledgeLibFind()
    ) -> List[KnowledgeLib]:
        """
        Finds knowledge libraries based on the given conditions.

        Args:
            condition (KnowledgeLibFind): The search conditions.

        Returns:
            List[KnowledgeLib]: A list of matching knowledge libraries.
        """
        async with db.get_async_session() as session:
            # Start building the query
            query = select(KnowledgeLib)
            
            # Apply filters based on the condition
            if condition.keyword:
                query = query.where(
                    or_(
                        KnowledgeLib.title.ilike(f"%{condition.keyword}%"),
                        KnowledgeLib.content.ilike(f"%{condition.keyword}%")
                    )
                )

            if condition.time:
                query = query.where(KnowledgeLib.update_time >= condition.time)

            if condition.status:
                query = query.where(KnowledgeLib.status == condition.status)
            
            # Add ordering and execute the query
            query = query.order_by(KnowledgeLib.update_time.desc())
            result = await session.execute(query)
            
            # Extract the results as a list of KnowledgeLib objects
            knowledge_libs = result.scalars().all()
            for knowledge_lib in knowledge_libs:
                make_transient(knowledge_lib)
            return knowledge_libs


    async def update_knowledge_lib(self, knowledge_data: KnowledgeLibView) -> Coroutine[
                                                                                  Any, Any, KnowledgeLib | None] | None:
        """
        Updates an existing knowledge library.

        Args:
            knowledge_data (KnowledgeLibView): The updated data for the knowledge library.

        Returns:
            Optional[KnowledgeLib]: The updated knowledge library if found, otherwise None.

        Raises:
            ValueError: If the title is not provided.
        """
        if not knowledge_data.title:
            raise ValueError(_("Title must be provided."))

        async with db.get_async_session() as session:
            result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == knowledge_data.id))
            entry = result.scalar_one_or_none()
            if not entry:
                return None

            try:
                template = Llm.get_prompt_template("content")
                knowledge_data.content = Llm.get_ai_response(
                    template.format(input=knowledge_data.title), config.DEFAULT_LLM_NAME
                )
                entry.title = knowledge_data.title
                entry.content = knowledge_data.content
                entry.update_time = datetime.datetime.now()

                await session.commit()
                make_transient(entry)
                return entry

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update knowledge library with ID {knowledge_data.id}: {e}")
                raise

    async def delete_knowledge_lib(self, knowledge_lib_id: int) -> bool:
        """
        Deletes a knowledge library and its associated data.

        Args:
            knowledge_lib_id (int): The ID of the knowledge library.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        async with db.get_async_session() as session:
            try:
                result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == knowledge_lib_id))
                entry = result.scalar_one_or_none()
                if not entry:
                    logger.warning(f"Knowledge library with ID {knowledge_lib_id} not found.")
                    return False
                self.delete_graph_node_document_files_by_lib(knowledge_lib_id)
                self.knowledge_graph_query.delete_graph_by_lib(knowledge_lib_id)
                await self.delete_subjects_by_lib_id(knowledge_lib_id)
                await session.delete(entry)
                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to delete knowledge library with ID {knowledge_lib_id}: {e}")
                return False

    async def toggle_knowledge_lib_publish(self, lib_id: int) -> Optional[KnowledgeLib]:
        """
        Updates the publish status of a knowledge library.

        Args:
            lib_id (int): The ID of the knowledge library.

        Returns:
            Optional[KnowledgeLib]: The updated knowledge library if found, otherwise None.
        """
        async with db.get_async_session() as session:
            result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == lib_id))
            entry = result.scalar_one_or_none()
            if not entry:
                await session.rollback()
                raise RuntimeError(_("Knowledge library not found."))

            print("toggle_knowledge_lib_publish entry.status: ", entry.status)
            if entry.status == 'GENERATING' or entry.status == 'ANALYZING':
                await session.rollback()
                raise RuntimeError(_("Cannot toggle publish status while generating or analyzing."))
            try:
                if entry.status == 'PUBLISHED':
                    entry.status = 'PENDING'
                else:
                    entry.status = 'PUBLISHED'

                entry.update_time = datetime.datetime.now()

                await session.commit()
                make_transient(entry)
                if config.API_ENV.lower() == "test":
                    gds_graph_name = GdsGraph.test_graph_name
                else:
                    gds_graph_name = GdsGraph.graph_name

                # Update the GDS graph
                if GdsGraph.check_gds_graph(gds_graph_name):
                    GdsGraph.delete_gds_graph(gds_graph_name)
                GdsGraph.create_gds_graph(gds_graph_name)
                logger.debug(f"Updated publish status to '{entry.status}' for library ID: {lib_id}.")
                return entry
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update knowledge library publish status by ID {lib_id}: {e}")
                raise RuntimeError(_("Failed to update knowledge library publish status: {e}"))


    # -------------------- Knowledge Library Subjects --------------------

    async def create_knowledge_lib_subject(self, knowledge_lib_subject: KnowledgeLibSubjectView) -> KnowledgeLibSubject:
        """
        Creates a new knowledge library subject.

        Args:
            knowledge_lib_subject (KnowledgeLibSubjectView): The data for the new subject.

        Returns:
            KnowledgeLibSubject: The newly created subject.

        Raises:
            ValueError: If the name is not provided.
        """
        if not knowledge_lib_subject.name:
            raise ValueError(_("Name must be provided."))

    
        async with db.get_async_session() as session:
            subject = KnowledgeLibSubject(
                name=knowledge_lib_subject.name,
                knowledge_lib_id=knowledge_lib_subject.knowledge_lib_id
            )
            print("------subject: ", subject)

            session.add(subject)
            await session.commit()
            await session.refresh(subject)

            return subject

    async def find_knowledge_lib_subjects(self, knowledge_lib_id: int, expunge: bool = True) -> List[KnowledgeLibSubject]:
        """
        Retrieves all subjects associated with a specific knowledge library.

        Args:
            knowledge_lib_id (int): The ID of the knowledge library.
            expunge (bool): Whether to expunge the objects from the session.

        Returns:
            List[KnowledgeLibSubject]: A list of KnowledgeLibSubject objects.
        """
        async with db.get_async_session() as session:
            result = await session.execute(select(KnowledgeLibSubject).filter(KnowledgeLibSubject.knowledge_lib_id==knowledge_lib_id))
            subjects = result.scalars().all()
            if subjects and expunge:
                # Detach the objects from the session
                for subject in subjects:
                    make_transient(subject)

            return subjects

    async def update_knowledge_lib_subject(self, knowledge_lib_subject: KnowledgeLibSubjectView) -> Optional[
        KnowledgeLibSubject]:
        """
        Updates the name of a knowledge library subject.

        Args:
            knowledge_lib_subject (KnowledgeLibSubjectView): The updated subject data.

        Returns:
            Optional[KnowledgeLibSubject]: The updated KnowledgeLibSubject object if successful, otherwise None.

        Raises:
            ValueError: If the subject name is not provided.
        """
        if not knowledge_lib_subject.name:
            raise ValueError(_("Name must be provided."))

        async with db.get_async_session() as session:
            try:
                result = await session.execute(select(KnowledgeLibSubject).filter(KnowledgeLibSubject.id==knowledge_lib_subject.id))
                entry = result.scalar_one_or_none()
                if entry:
                    entry.name = knowledge_lib_subject.name
                    await session.commit()
                    logger.info(f"Successfully updated subject with ID {knowledge_lib_subject.id}.")
                    make_transient(entry)
                    return entry
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update subject with ID {knowledge_lib_subject.id}: {e}")
                raise e

    async def delete_knowledge_lib_subject(self, subject_id: int) -> bool:
        """
        Deletes a knowledge library subject and its associated data.

        Args:
            subject_id (int): The ID of the subject to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        async with db.get_async_session() as session:
            try:
                result = await session.execute(select(KnowledgeLibSubject).filter(KnowledgeLibSubject.id==subject_id))
                subject = result.scalar_one_or_none()
                if not subject:
                    logger.warning(f"Subject with ID {subject_id} not found.")
                    return False
                # Delete associated files and graph data
                self.delete_graph_node_document_files_by_subject(subject.knowledge_lib_id, subject_id)
                self.knowledge_graph_query.delete_graph_by_subject(subject.knowledge_lib_id, subject_id)

                # Delete the subject
                await session.delete(subject)
                await session.commit()
                logger.info(f"Successfully deleted subject with ID {subject_id}.")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to delete subject with ID {subject_id}: {e}")
                return False

    async def delete_subjects_by_lib_id(self, lib_id: int) -> bool:
        """
        Deletes all subjects associated with a knowledge library and its associated data.

        Args:
            lib_id (int): The ID of the library.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        async with db.get_async_session() as session:
            try:
                result = await session.execute(select(KnowledgeLibSubject).filter(KnowledgeLibSubject.knowledge_lib_id==lib_id))
                subjects = result.scalars().all()
                for subject in subjects:
                    # Delete associated files and graph data
                    self.delete_graph_node_document_files_by_subject(subject.knowledge_lib_id, subject.id)
                    self.knowledge_graph_query.delete_graph_by_subject(subject.knowledge_lib_id, subject.id)
                    print('----Deleting subject', subject.id)
                    # Delete the subject
                    await session.delete(subject)
                    await session.commit()
                logger.info(f"Successfully deleted subjects with knowledge library ID {lib_id}.")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to delete subjects with knowledge library ID {lib_id}: {e}")
                return False


    def delete_graph_node_document_files_by_lib(self, lib_id: int) -> None:
        """
        Deletes all document files associated with a knowledge library.

        Args:
            lib_id (int): The ID of the knowledge library.

        Returns:
            None
        """
        logger.info(f"Deleting document files for library with ID: {lib_id}")
        try:
            documents = Document.get_documents_by_lib(lib_id)
            if documents:
                for document in documents:
                    file_path = os.path.join(config.UPLOAD_DIR, document.saved_at)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.debug(f"Deleted document file: {file_path}")
                    else:
                        logger.warning(f"Document file not found: {file_path}")
            logger.info(f"Successfully deleted document files for library with ID: {lib_id}")
        except Exception as e:
            logger.error(f"Failed to delete document files for library with ID {lib_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete document files: {e}") from e
