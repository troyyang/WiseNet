import os
from typing import Optional, List

import core.database as db
from ai.embedding import EmbeddingFactory
from core import config
from core.extends_logger import logger
from core.i18n import _
from graph import RelationshipType
from graph.document import Document
from graph.document_page import DocumentPage
from graph.entity import Entity
from graph.keyword import Keyword
from graph.node import Node
from graph.relationship import Relationship
from graph.tag import Tag
from graph.webpage import WebPage
from schemas.graph import GraphNodeView, GraphRelationshipView
from services import BaseService


class GraphBaseService(BaseService):
    def __init__(self):
        super(GraphBaseService, self).__init__()
        self.embedding_factory = EmbeddingFactory()

    def delete_graph_node(self, node_element_id: str) -> None:
        """
        Deletes a graph node and all its associated data (documents, webpages, keywords, tags, entities).

        Args:
            node_element_id (str): The unique identifier of the node to delete.

        Returns:
            None
        """
        logger.info(f"Starting delete_graph_node for node_element_id: {node_element_id}")
        try:
            self.delete_graph_node_documents(node_element_id)
            WebPage.delete_webpages_of_node(node_element_id)
            Keyword.delete_keywords_of_node(node_element_id)
            Tag.delete_tags_of_node(node_element_id)
            Entity.delete_entities_of_node(node_element_id)
            Node.delete_node(node_element_id)
            logger.info(f"Successfully deleted node and associated data for node_element_id: {node_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete node with node_element_id: {node_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete node: {e}") from e

    def delete_graph_relationship(self, relationship_element_id: str) -> None:
        """
        Deletes a graph relationship.

        Args:
            relationship_element_id (str): The unique identifier of the relationship to delete.

        Returns:
            None
        """
        logger.info(f"Starting delete_graph_relationship for relationship_element_id: {relationship_element_id}")
        try:
            Relationship.delete_relationship(relationship_element_id)
            logger.info(f"Successfully deleted relationship with relationship_element_id: {relationship_element_id}")
        except Exception as e:
            logger.error(
                f"Failed to delete relationship with relationship_element_id: {relationship_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete relationship: {e}") from e

    def add_node_by_human(self, node: GraphNodeView) -> Node:
        """
        Adds a new node to the graph manually (by a human).

        Args:
            node (GraphNodeView): The data for the new node.

        Returns:
            Node: The newly created node.

        Raises:
            ValueError: If required fields (lib_id, subject_id, content) are missing.
        """
        logger.info(f"Starting add_node_by_human for lib_id: {node.lib_id}, subject_id: {node.subject_id}")
        if node.lib_id is None or node.subject_id is None or node.content is None:
            error_msg = "Lib id, subject id, and content must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            new_node, relationship = Node.add_human_node(
                lib_id=node.lib_id,
                subject_id=node.subject_id,
                content=node.content,
                parent_element_id=node.parent_element_id,
            )
            logger.info(f"Successfully added node with element_id: {new_node.element_id}")
            return new_node, relationship
        except Exception as e:
            logger.error(f"Failed to add node. Error: {e}")
            raise RuntimeError(f"Failed to add node: {e}") from e

    def add_relationship_by_human(self, relationship: GraphRelationshipView) -> Relationship:
        """
        Adds a new relationship to the graph manually (by a human).

        Args:
            relationship (GraphRelationshipView): The data for the new relationship.

        Returns:
            Relationship: The newly created relationship.

        Raises:
            ValueError: If required fields (lib_id, subject_id, source_element_id, target_element_id, type) are missing.
        """
        logger.info(
            f"Starting add_relationship_by_human for lib_id: {relationship.lib_id}, subject_id: {relationship.subject_id}")
        if (
                relationship.lib_id is None
                or relationship.subject_id is None
                or relationship.source_element_id is None
                or relationship.target_element_id is None
                or relationship.type is None
        ):
            error_msg = "Lib id, subject id, source element id, target element id, and relationship type must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            new_relationship = Relationship.add_relationship(
                lib_id=relationship.lib_id,
                subject_id=relationship.subject_id,
                source_element_id=relationship.source_element_id,
                target_element_id=relationship.target_element_id,
                type=RelationshipType(relationship.type),
            )
            logger.info(f"Successfully added relationship with element_id: {new_relationship.element_id}")
            return new_relationship
        except Exception as e:
            logger.error(f"Failed to add relationship. Error: {e}")
            raise RuntimeError(f"Failed to add relationship: {e}") from e


    def update_graph_node(self, data: GraphNodeView) -> Node:
        """
        Updates the content and embedding of a graph node.

        Args:
            data (GraphNodeView): The updated data for the node.

        Returns:
            Node: The updated node.

        Raises:
            ValueError: If required fields (element_id, content) are missing.
        """
        logger.info(f"Starting update_graph_node for element_id: {data.element_id}")
        if data.element_id is None:
            error_msg = "Element id must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))
        if not data.content:
            error_msg = "Content must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            node: Node = Node.find_detail_by_element_id(data.element_id)
            if not node:
                error_msg = f"Node with element_id {data.element_id} not found."
                logger.error(error_msg)
                raise ValueError(_(error_msg))

            node.content = data.content
            node.content_vector = self.embedding_factory.get_embedding(
                text=data.content,
                model_name=data.embedding_model,
                max_tokens_each_chunk=data.max_tokens_each_chunk,
            )
            node.embedding_model = data.embedding_model
            updated_node = node.update()
            logger.info(f"Successfully updated node with element_id: {data.element_id}")
            return updated_node
        except Exception as e:
            logger.error(f"Failed to update node with element_id: {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to update node: {e}") from e

    def update_relationship_info(self, data: GraphRelationshipView) -> Relationship:
        """
        Updates the content and embedding of a graph relationship.

        Args:
            data (GraphRelationshipView): The updated data for the relationship.

        Returns:
            Relationship: The updated relationship.

        Raises:
            ValueError: If required fields (element_id, content) are missing.
        """
        logger.info(f"Starting update_relationship_info for element_id: {data.element_id}")
        if data.element_id is None or data.content is None:
            error_msg = "Element id and content must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            relationship: Relationship = Relationship.find_relationship_detail_by_element_id(data.element_id)
            if not relationship:
                error_msg = f"Relationship with element_id {data.element_id} not found."
                logger.error(error_msg)
                raise ValueError(_(error_msg))

            relationship.content = data.content
            relationship.content_vector = self.embedding_factory.get_embedding(
                text=data.content,
                model_name=data.embedding_model,
                max_tokens_each_chunk=data.max_tokens_each_chunk,
            )
            relationship.embedding_model = data.embedding_model
            updated_relationship = relationship.update()
            logger.info(f"Successfully updated relationship with element_id: {data.element_id}")
            return updated_relationship
        except Exception as e:
            logger.error(f"Failed to update relationship with element_id: {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to update relationship: {e}") from e

    def get_graph_node_detail(self, element_id: str) -> Optional[Node]:
        """
        Retrieves detailed information about a graph node.

        Args:
            element_id (str): The unique identifier of the node.

        Returns:
            Optional[Node]: The node details if found, otherwise None.
        """
        logger.info(f"Fetching graph node detail for element_id: {element_id}")
        try:
            node = Node.find_detail_by_element_id(element_id)
            if node:
                logger.info(f"Successfully fetched node detail for element_id: {element_id}")
            else:
                logger.warning(f"Node with element_id {element_id} not found.")
            return node
        except Exception as e:
            logger.error(f"Failed to fetch node detail for element_id: {element_id}. Error: {e}")
            raise RuntimeError(f"Failed to fetch node detail: {e}") from e

    def get_graph_relationship_detail(self, element_id: str) -> Optional[Relationship]:
        """
        Retrieves detailed information about a graph relationship.

        Args:
            element_id (str): The unique identifier of the relationship.

        Returns:
            Optional[Relationship]: The relationship details if found, otherwise None.
        """
        logger.info(f"Fetching graph relationship detail for element_id: {element_id}")
        try:
            relationship = Relationship.find_relationship_detail_by_element_id(element_id)
            if relationship:
                logger.info(f"Successfully fetched relationship detail for element_id: {element_id}")
            else:
                logger.warning(f"Relationship with element_id {element_id} not found.")
            return relationship
        except Exception as e:
            logger.error(f"Failed to fetch relationship detail for element_id: {element_id}. Error: {e}")
            raise RuntimeError(f"Failed to fetch relationship detail: {e}") from e


    def delete_graph_node_entity(self, entity_element_id: str, node_element_id: str) -> None:
        """
        Deletes an entity associated with a graph node.

        Args:
            entity_element_id (str): The unique identifier of the entity.
            node_element_id (str): The unique identifier of the node.

        Returns:
            None
        """
        logger.info(f"Deleting entity with element_id: {entity_element_id} for node with element_id: {node_element_id}")
        try:
            Entity.delete_entity(entity_element_id, node_element_id)
            logger.info(f"Successfully deleted entity with element_id: {entity_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete entity with element_id: {entity_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete entity: {e}") from e

    def delete_graph_node_keyword(self, keyword_element_id: str, node_element_id: str) -> None:
        """
        Deletes a keyword associated with a graph node.

        Args:
            keyword_element_id (str): The unique identifier of the keyword.
            node_element_id (str): The unique identifier of the node.

        Returns:
            None
        """
        logger.info(
            f"Deleting keyword with element_id: {keyword_element_id} for node with element_id: {node_element_id}")
        try:
            Keyword.delete_keyword(keyword_element_id, node_element_id)
            logger.info(f"Successfully deleted keyword with element_id: {keyword_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete keyword with element_id: {keyword_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete keyword: {e}") from e

    def delete_graph_node_tag(self, tag_element_id: str, node_element_id: str) -> None:
        """
        Deletes a tag associated with a graph node.

        Args:
            tag_element_id (str): The unique identifier of the tag.
            node_element_id (str): The unique identifier of the node.

        Returns:
            None
        """
        logger.info(f"Deleting tag with element_id: {tag_element_id} for node with element_id: {node_element_id}")
        try:
            Tag.delete_tag(tag_element_id, node_element_id)
            logger.info(f"Successfully deleted tag with element_id: {tag_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete tag with element_id: {tag_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete tag: {e}") from e



    def delete_graph_node_documents(self, parent_element_id: str) -> None:
        """
        Deletes all documents and associated files for a given node.

        Args:
            parent_element_id (str): The unique identifier of the parent node.

        Returns:
            None
        """
        logger.info(f"Deleting documents for node with element_id: {parent_element_id}")
        try:
            documents: List[Document] = Document.get_documents_of_node(parent_element_id)
            if documents:
                for document in documents:
                    DocumentPage.delete_document_pages_of_parent(document.element_id)
                    file_path = os.path.join(config.UPLOAD_DIR, document.saved_at)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.debug(f"Deleted document file: {file_path}")
                    else:
                        logger.warning(f"Document file not found: {file_path}")
            DocumentPage.delete_document_pages_of_parent(parent_element_id)
            Document.delete_documents_of_node(parent_element_id)
            logger.info(f"Successfully deleted documents for node with element_id: {parent_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete documents for node with element_id {parent_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete documents: {e}") from e

    def delete_graph_node_document(self, document_element_id: str) -> None:
        """
        Deletes a specific document and its associated file.

        Args:
            document_element_id (str): The unique identifier of the document.

        Returns:
            None
        """
        logger.info(f"Deleting document with element_id: {document_element_id}")
        try:
            document = Document.get_document_by_element_id(document_element_id)
            if document:
                file_path = os.path.join(config.UPLOAD_DIR, document.saved_at)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted document file: {file_path}")
                else:
                    logger.warning(f"Document file not found: {file_path}")
            Document.delete_document(document_element_id)
            logger.info(f"Successfully deleted document with element_id: {document_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete document with element_id {document_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete document: {e}") from e

    def add_graph_node_webpage(self, lib_id: int, subject_id: int, node_element_id: str, url: str) -> WebPage:
        """
        Adds a webpage to a graph node.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_id (int): The ID of the knowledge library subject.
            node_element_id (str): The unique identifier of the node.
            url (str): The URL of the webpage.

        Returns:
            WebPage: The newly created webpage node.
        """
        logger.info(f"Adding webpage to node with element_id: {node_element_id}")
        try:
            webpage = WebPage.add_webpage_node(
                lib_id=lib_id,
                subject_id=subject_id,
                parent_element_id=node_element_id,
                url=url,
            )
            logger.info(f"Successfully added webpage with element_id: {webpage.element_id}")
            return webpage
        except Exception as e:
            logger.error(f"Failed to add webpage to node with element_id {node_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to add webpage: {e}") from e

    def delete_graph_node_webpage(self, webpage_element_id: str) -> None:
        """
        Deletes a webpage associated with a graph node.

        Args:
            webpage_element_id (str): The unique identifier of the webpage.

        Returns:
            None

        Raises:
            RuntimeError: If the deletion fails.
        """
        logger.info(f"Deleting webpage with element_id: {webpage_element_id}")
        try:
            WebPage.delete_webpage(webpage_element_id)
            logger.info(f"Successfully deleted webpage with element_id: {webpage_element_id}")
        except Exception as e:
            logger.error(f"Failed to delete webpage with element_id {webpage_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to delete webpage: {e}") from e

    def get_analyzed_graph_node_webpage(self, webpage_element_id: str) -> Optional[WebPage]:
        """
        Retrieves detailed information about an analyzed webpage.

        Args:
            webpage_element_id (str): The unique identifier of the webpage.

        Returns:
            Optional[WebPage]: The webpage details if found, otherwise None.
        """
        logger.info(f"Fetching analyzed webpage with element_id: {webpage_element_id}")
        try:
            webpage = WebPage.get_webpage_by_element_id(webpage_element_id)
            if webpage:
                logger.info(f"Successfully fetched webpage with element_id: {webpage_element_id}")
            else:
                logger.warning(f"Webpage with element_id {webpage_element_id} not found.")
            return webpage
        except Exception as e:
            logger.error(f"Failed to fetch webpage with element_id {webpage_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to fetch webpage: {e}") from e

    def upload_graph_node_file(
            self,
            lib_id: int,
            subject_id: int,
            node_element_id: str,
            saved_at: str,
            filename: str,
    ) -> Document:
        """
        Uploads a file to a graph node and associates it as a document.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_id (int): The ID of the knowledge library subject.
            node_element_id (str): The unique identifier of the node.
            saved_at (str): The path where the file is saved.
            filename (str): The name of the file.

        Returns:
            Document: The newly created document node.

        Raises:
            ValueError: If required fields are missing.
            RuntimeError: If the upload fails.
        """
        logger.info(f"Uploading file {filename} to node with element_id: {node_element_id}")
        if not lib_id or not subject_id or not node_element_id or not saved_at or not filename:
            error_msg = "Lib id, subject id, node element id, saved_at, and filename must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            document = Document.add_document_node(
                lib_id=lib_id,
                subject_id=subject_id,
                parent_element_id=node_element_id,
                name=filename,
                saved_at=saved_at,
            )
            logger.info(f"Successfully uploaded file {filename} to node with element_id: {node_element_id}")
            return document
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to node with element_id {node_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to upload file: {e}") from e

    def get_document_detail(self, document_element_id: str) -> Optional[Document]:
        """
        Retrieves detailed information about a document.

        Args:
            document_element_id (str): The unique identifier of the document.

        Returns:
            Optional[Document]: The document details if found, otherwise None.
        """
        logger.info(f"Fetching document detail for element_id: {document_element_id}")
        try:
            document = Document.get_document_by_element_id(document_element_id)
            if document:
                logger.info(f"Successfully fetched document detail for element_id: {document_element_id}")
            else:
                logger.warning(f"Document with element_id {document_element_id} not found.")
            return document
        except Exception as e:
            logger.error(f"Failed to fetch document detail for element_id {document_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to fetch document detail: {e}") from e