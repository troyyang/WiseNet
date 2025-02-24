import asyncio
import unittest
import pytest

import core.config as config
from graph import graph, RelationshipType, NodeType
from graph.document import Document
from graph.document_page import DocumentPage
from graph.entity import Entity
from graph.graph_generator import KnowledgeGraphGenerator
from graph.graph_query import KnowledgeGraphQuery
from graph.keyword import Keyword
from graph.node import Node
from graph.relationship import Relationship
from graph.tag import Tag
from graph.webpage import WebPage
from schemas.graph import GraphConditionView
from services.knowledge_lib_service import KnowledgeLibService


class TestKnowledgeGraphGeneration(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_lib_service = KnowledgeLibService()
        self.knowledge_graph_query = KnowledgeGraphQuery()
        self.llm_name = "wizardlm2"
        self.embedding_model = "sbert"
        self.max_tokens_each_chunk = 128

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_knowledge_graph_generation_with_valid_input(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)
        knowledge_graph_generator = KnowledgeGraphGenerator(lib_name="E-commerce customer service outsourcing",
                                                            title="E-commerce customer service outsourcing workflow",
                                                            llm_name="wizardlm2", max_depth=4, lib_id=self.lib_id, subject_id=self.subject_id)
        asyncio.run(knowledge_graph_generator())
        nodes, overviews = Node.query_graph_node(lib_id=self.lib_id, subject_ids=[self.subject_id])

        self.assertGreaterEqual(len(nodes), 3)
        self.assertGreaterEqual(len(overviews), 3)

    def test_knowledge_graph_generation_with_empty_input(self):
        with self.assertRaises(ValueError) as context:
            KnowledgeGraphGenerator(lib_name="E-commerce customer service outsourcing", title=None,
                                    llm_name=config.DEFAULT_LLM_NAME, max_depth=4, lib_id=self.lib_id, subject_id=self.subject_id)
        self.assertEqual(str(context.exception), "title cannot be empty.")

    def test_knowledge_graph_generation_with_min_depth(self):
        with self.assertRaises(ValueError) as context:
            KnowledgeGraphGenerator(lib_name="E-commerce customer service outsourcing",
                                    title="Main application industries of customer service outsourcing",
                                    llm_name=config.DEFAULT_LLM_NAME, max_depth=1, lib_id=self.lib_id, subject_id=self.subject_id)
        self.assertEqual(str(context.exception), "max_depth must be greater than 1.")

    def test_knowledge_graph_generation_with_odd_depth(self):
        with self.assertRaises(ValueError) as context:
            KnowledgeGraphGenerator(lib_name="E-commerce customer service outsourcing",
                                    title="Main application industries of customer service outsourcing",
                                    llm_name=config.DEFAULT_LLM_NAME, max_depth=3, lib_id=self.lib_id, subject_id=self.subject_id)
        self.assertEqual(str(context.exception), "max_depth must be an even number.")

    
    @pytest.mark.asyncio
    async def test_knowledge_graph_generation_with_library(self):
        lib = await self.knowledge_lib_service.find_knowledge_lib_by_id(1)
        subjects = await self.knowledge_lib_service.find_knowledge_lib_subjects(lib.id)

        temp_subject_id = -111
        for subject in subjects:
            temp_lib_id = self.lib_id
            temp_subject_id = temp_subject_id - 1
            knowledge_graph_generator = KnowledgeGraphGenerator(lib_name=lib.title, title=subject.name,
                                                                llm_name="wizardlm2", max_depth=4, lib_id=temp_lib_id,
                                                                subject_id=temp_subject_id)
            asyncio.run(knowledge_graph_generator())
            nodes, overviews = Node.query_graph_node(lib_id=temp_lib_id, subject_ids=[temp_subject_id])

            self.assertIsNotNone(nodes)
            self.assertGreaterEqual(len(nodes), 4)
            self.assertGreaterEqual(len(overviews), 1)

    def test_knowledge_graph_generation_with_max_depth(self):
        with self.assertRaises(ValueError) as context:
            KnowledgeGraphGenerator(lib_name="E-commerce customer service outsourcing",
                                    title="Main application industries of customer service outsourcing",
                                    llm_name=self.llm_name, max_depth=config.DEEP_LIMIT + 2, lib_id=-2, subject_id=-2)
        self.assertEqual(str(context.exception), f"max_depth must be less than {config.DEEP_LIMIT}")


class TestGraphNodeOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        content = "test_message"

        node, relationship = Node.add_human_node(lib_id, subject_id, content)

        self.assertIsNotNone(node)
        self.assertIsNone(relationship)
        self.assertEqual(node.lib_id, lib_id)
        self.assertEqual(node.subject_id, subject_id)
        self.assertEqual(node.content, content)
        self.assertIsNotNone(node.content)

    def test_add_node_with_parent(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        content = "test_message"
        parent_node = Node.add_prompt_node(lib_id, subject_id, "parent node", 1)
        self.assertIsNotNone(parent_node)

        node, relationship = Node.add_human_node(lib_id, subject_id, content, parent_element_id=parent_node.element_id)

        self.assertIsNotNone(node)
        self.assertIsNotNone(relationship)
        self.assertEqual(node.lib_id, lib_id)
        self.assertEqual(node.subject_id, subject_id)
        self.assertEqual(node.content, content)
        self.assertIsNotNone(node.content)

        node_query_result = graph.query(
            "MATCH (n) WHERE elementId(n)=$node_element_id RETURN n",
            {"node_element_id": node.element_id})
        self.assertEqual(len(node_query_result), 1)
        relationship_query_result = graph.query(
            "MATCH (p)-[r]->(c) WHERE elementId(p)=$parent_element_id RETURN r",
            {"parent_element_id": parent_node.element_id})
        self.assertEqual(len(relationship_query_result), 1)

    def test_update_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        node, relationship = Node.add_human_node(lib_id, subject_id, "test_message")
        element_id = node.element_id

        node: Node = Node.find_detail_by_element_id(element_id)
        if node:
            node.content = "updated_message"
            node.title = "updated_title"
            node.title_vector = [1,2,3]
            node.content_vector = [4,5,6]
            result = node.update()

        self.assertEqual(result.content, "updated_message")
        self.assertEqual(result.title, "updated_title")
        updated_node = Node.find_detail_by_element_id(element_id)
        self.assertIsNotNone(updated_node)
        self.assertEqual(updated_node.content, "updated_message")
        self.assertEqual(updated_node.title, "updated_title")

    def test_delete_node(self):
        prompt_node = Node.add_prompt_node(self.lib_id, self.subject_id, "test_message", 1)
        node_element_id = prompt_node.element_id
        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n",
                                                           {"node_element_id": node_element_id})
        self.assertEqual(len(result), 1)

        Node.delete_node(node_element_id)

        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n",
                                                           {"node_element_id": node_element_id})
        self.assertEqual(len(result), 0, "Node was not deleted successfully")

    def test_get_node_details(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        node, relationship = Node.add_human_node(lib_id, subject_id, "test_message")
        Entity.add_entity_node(lib_id, subject_id, node.element_id, "test_entity")
        Document.add_document_node(lib_id, subject_id, node.element_id, "test_document", "file path/url")
        WebPage.add_webpage_node(lib_id, subject_id, node.element_id, "https://example.com")
        Keyword.add_keyword_node(lib_id, subject_id, node.element_id, "test_link")
        Tag.add_tag_node(lib_id, subject_id, node.element_id, "test_tag")
        element_id = node.element_id

        node = Node.find_detail_by_element_id(element_id)

        self.assertEqual(node.element_id, element_id)
        self.assertEqual(node.content, "test_message")
        self.assertEqual(node.lib_id, lib_id)
        self.assertEqual(node.subject_id, subject_id)
        self.assertEqual(len(node.entities), 1)
        self.assertEqual(len(node.documents), 1)
        self.assertEqual(len(node.webpages), 1)
        self.assertEqual(len(node.tags), 1)
        self.assertEqual(len(node.keywords), 1)

    def test_get_node_details_with_no_children(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        node, relationship = Node.add_human_node(lib_id, subject_id, "test_message")
        element_id = node.element_id

        result = Node.find_detail_by_element_id(element_id)

        self.assertEqual(result.element_id, element_id)
        self.assertEqual(result.content, "test_message")
        self.assertEqual(result.lib_id, lib_id)
        self.assertEqual(result.subject_id, subject_id)
        self.assertEqual(result.entities, [])
        self.assertEqual(result.documents, [])
        self.assertEqual(result.webpages, [])
        self.assertEqual(result.tags, [])
        self.assertEqual(result.keywords, [])

    def test_find_human_nodes(self):
        info_node = Node.add_info_node(self.lib_id, self.subject_id, "info message", 1)
        human_node1, r = Node.add_human_node(self.lib_id, self.subject_id, "human message")
        human_node2, r = Node.add_human_node(self.lib_id, self.subject_id, "human message")
        human_node3, r = Node.add_human_node(self.lib_id, self.subject_id, "human message3")
        Relationship.add_relationship(self.lib_id, self.subject_id, info_node.element_id, human_node1.element_id, RelationshipType.RELATED_TO)
        Relationship.add_relationship(self.lib_id, self.subject_id, info_node.element_id, human_node2.element_id, RelationshipType.HAS_CHILD)
        Relationship.add_relationship(self.lib_id, self.subject_id, human_node3.element_id, info_node.element_id, RelationshipType.HAS_CHILD)

        human_nodes = Node.find_human_nodes(info_node.element_id)

        self.assertEqual(len(human_nodes), 3)


class TestGraphRelationshipOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_relationship(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        type = RelationshipType.RELATED_TO

        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "parent_node")
        child_node, relationship = Node.add_human_node(lib_id, subject_id, "child_node")
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id,
                                                                       child_node.element_id, type)

        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.lib_id, lib_id)
        self.assertEqual(relationship.subject_id, subject_id)
        self.assertEqual(relationship.source_element_id, parent_node.element_id)
        self.assertEqual(relationship.target_element_id, child_node.element_id)
        self.assertEqual(relationship.type, type)
        self.assertIsNotNone(relationship.element_id)

    def test_update_relationship_info(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "parent_node")
        child_node, relationship = Node.add_human_node(lib_id, subject_id, "child_node")
        relationship: Relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id,
                                                                       child_node.element_id,
                                                                       RelationshipType.RELATED_TO)
        new_message = "updated_message"
        relationship.content = new_message
        relationship.content_vector = [1, 2, 3]
        relationship.embedding_model = "embedding_model"
        result = relationship.update()

        self.assertEqual(result.content, new_message)

    def test_delete_relationship(self):
        lib_id = self.lib_id
        subject_id = self.lib_id
        parent_node = Node.add_subject_node(lib_id, subject_id, "Parent Node", 1)
        child_node = Node.add_subject_node(lib_id, subject_id, "Child Node", 1)
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id,
                                                                      child_node.element_id,
                                                                      RelationshipType.HAS_CHILD)
        result = graph.query(
            "MATCH ()-[r]->() WHERE elementId(r)=$relationship_element_id RETURN r",
            {"relationship_element_id": relationship.element_id})
        self.assertEqual(len(result), 1)

        Relationship.delete_relationship(relationship.element_id)

        result = graph.query(
            "MATCH ()-[r]->() WHERE elementId(r)=$relationship_element_id RETURN r",
            {"relationship_element_id": relationship.element_id})
        self.assertEqual(len(result), 0, "Relationship was not deleted successfully")
        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n",
                                                           {"node_element_id": parent_node.element_id})
        self.assertEqual(len(result), 1, "Parent node was not deleted successfully")
        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n",
                                                           {"node_element_id": child_node.element_id})
        self.assertEqual(len(result), 1, "Child node was not deleted successfully")
        result = graph.query(
            "MATCH (n) WHERE elementId(n)=$node_element_id DETACH DELETE n",
            {"node_element_id": parent_node.element_id})
        self.assertEqual(len(result), 0, "Parent node was deleted successfully")
        result = graph.query(
            "MATCH (n) WHERE elementId(n)=$node_element_id DETACH DELETE n",
            {"node_element_id": child_node.element_id})
        self.assertEqual(len(result), 0, "Child node was deleted successfully")

    def test_get_relationship_details(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "parent_node")
        child_node, relationship = Node.add_human_node(lib_id, subject_id, "child_node")
        message = "test_message"
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id,
                                                                       child_node.element_id,
                                                                       RelationshipType.RELATED_TO, message)
        relationship_element_id = relationship.element_id

        result = Relationship.find_relationship_detail_by_element_id(relationship_element_id)

        self.assertEqual(result.element_id, relationship_element_id)
        self.assertEqual(result.source_element_id, parent_node.element_id)
        self.assertEqual(result.target_element_id, child_node.element_id)
        self.assertEqual(result.type, RelationshipType.RELATED_TO)
        self.assertEqual(result.content, message)

    def test_query_graph_relationship_overview(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "parent_node")
        child_node, relationship = Node.add_human_node(lib_id, subject_id, "child_node")
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id,
                                                                       child_node.element_id,
                                                                       RelationshipType.RELATED_TO)

        result = Relationship.query_graph_relationship_overviews(lib_id, [subject_id])

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, RelationshipType.RELATED_TO.value)


class TestGraphEntityOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_entity(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        entity = Entity.add_entity_node(lib_id, subject_id, parent_node.element_id,
                                                       "entity",
                                                       [1, 2, 3],
                                                       "sbert")

        self.assertIsNotNone(entity)
        self.assertIsNotNone(entity.element_id)
        self.assertEqual(entity.lib_id, lib_id)
        self.assertEqual(entity.subject_id, subject_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.entities), 1)

    def test_delete_entities_by_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        entity = Entity.add_entity_node(lib_id, subject_id, parent_node.element_id,
                                                       "entity",
                                                       [1, 2, 3])
        entity2 = Entity.add_entity_node(lib_id, subject_id, parent_node.element_id,
                                                       "entity2",
                                                       [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.entities), 2)
        Entity.delete_entities_of_node(parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.entities), 0)

    def test_delete_entity(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        entity = Entity.add_entity_node(lib_id, subject_id, parent_node.element_id,
                                                       "entity",
                                                       [1, 2, 3])
        entity2 = Entity.add_entity_node(lib_id, subject_id, parent_node.element_id,
                                                        "entity2",
                                                        [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.entities), 2)
        Entity.delete_entity(entity2.element_id, parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.entities), 1)


class TestGraphKeywordOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_keyword(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        keyword = Keyword.add_keyword_node(lib_id, subject_id, parent_node.element_id, "keyword",
                                                        [1, 2, 3])

        self.assertIsNotNone(keyword)
        self.assertIsNotNone(keyword.element_id)
        self.assertEqual(keyword.lib_id, lib_id)
        self.assertEqual(keyword.subject_id, subject_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.keywords), 1)

    def test_delete_keywords_by_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        keyword1 = Keyword.add_keyword_node(lib_id, subject_id, parent_node.element_id, "keyword",
                                                        [1, 2, 3])
        keyword2 = Keyword.add_keyword_node(lib_id, subject_id, parent_node.element_id, "keyword2",
                                                        [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.keywords), 2)
        Keyword.delete_keywords_of_node(parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.keywords), 0)

    def test_delete_keyword(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        keyword1 = Keyword.add_keyword_node(lib_id, subject_id, parent_node.element_id, "keyword",
                                                        [1, 2, 3])
        keyword2 = Keyword.add_keyword_node(lib_id, subject_id, parent_node.element_id, "keyword2",
                                                        [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.keywords), 2)
        Keyword.delete_keyword(keyword2.element_id, parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.keywords), 1)


class TestGraphTagOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_tag(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        tag = Tag.add_tag_node(lib_id, 
                                subject_id, 
                                parent_node.element_id, 
                                "tag",
                                [1, 2, 3])

        self.assertIsNotNone(tag)
        self.assertIsNotNone(tag.element_id)
        self.assertEqual(tag.lib_id, lib_id)
        self.assertEqual(tag.subject_id, subject_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.tags), 1)

    def test_delete_tags_by_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        Tag.add_tag_node(lib_id, subject_id, parent_node.element_id, "tag", [1, 2, 3])
        Tag.add_tag_node(lib_id, subject_id, parent_node.element_id, "tag2", [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.tags), 2)
        Tag.delete_tags_of_node(parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.tags), 0)

    def test_delete_tag(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        Tag.add_tag_node(lib_id, subject_id, parent_node.element_id, "tag", [1, 2, 3])
        tag2 = Tag.add_tag_node(lib_id, subject_id, parent_node.element_id, "tag2", [4, 5, 6])
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.tags), 2)
        Tag.delete_tag(tag2.element_id, parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.tags), 1)


class TestGraphDocumentOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_document(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, content="Logistics transportation process")

        document = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document",
                                                         "file path/url",
                                                         "title1",
                                                         "summary1",
                                                         [1, 2, 3],
                                                         [1, 2, 3],
                                                         "sbert")
        self.assertIsNotNone(document)
        self.assertIsNotNone(document.element_id)
        self.assertEqual(document.lib_id, lib_id)
        self.assertEqual(document.subject_id, subject_id)
        node = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(node)
        self.assertEqual(len(node.documents), 1)

    def test_update_document(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        document = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document",
                                                         "file path/url")
        self.assertIsNotNone(document)
        document.title = "new title"
        document.content = "new summary"
        document.title_vector = [1, 2, 3]
        document.content_vector = [4, 5, 6]
        document.embedding_model = "sbert"
        document.update()
        
        queyr_result = graph.query("MATCH (c:Document) where elementId(c)=$element_id return c", params={"element_id": document.element_id})
        self.assertEqual(queyr_result[0].get("c").get("title"), "new title")
        self.assertEqual(queyr_result[0].get("c").get("content"), "new summary")
        self.assertEqual(queyr_result[0].get("c").get("title_vector"), [1, 2, 3])
        self.assertEqual(queyr_result[0].get("c").get("content_vector"), [4, 5, 6])
        self.assertEqual(queyr_result[0].get("c").get("embedding_model"), "sbert")

    def test_delete_documents_by_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document",
                                                         "file path/url",
                                                         "title1",
                                                         "summary1",
                                                         [1, 2, 3],
                                                         [1, 2, 3],
                                                         "sbert")
        document2 = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document2",
                                                         "file path/url2",
                                                         "title2",
                                                         "summary2",
                                                         [4, 5, 6],
                                                         [4, 5, 6],
                                                         "sbert")
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.documents), 2)
        Document.delete_documents_of_node(parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.documents), 0)

    def test_delete_document(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        document1 = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document",
                                                         "file path/url",
                                                         "title1",
                                                         "summary1",
                                                         [1, 2, 3],
                                                         [1, 2, 3],
                                                         "sbert")
        document2 = Document.add_document_node(lib_id, subject_id,
                                                         parent_node.element_id,
                                                         "document2",
                                                         "file path/url2",
                                                         "title2",
                                                         "summary2",
                                                         [4, 5, 6],
                                                         [4, 5, 6],
                                                         "sbert")
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.documents), 2)
        Document.delete_document(document1.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.documents), 1)


class TestGraphWebpageOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_webpage(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.example.com")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.element_id)
        self.assertEqual(result.lib_id, lib_id)
        self.assertEqual(result.subject_id, subject_id)
        node = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(node)
        self.assertEqual(len(node.webpages), 1)

    def test_get_webpage(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.example.com")
        self.assertIsNotNone(result)
        webpage_node = WebPage.get_webpage_by_element_id(result.element_id)
        self.assertIsNotNone(webpage_node)
        self.assertEqual(webpage_node.element_id, result.element_id)
        self.assertEqual(webpage_node.lib_id, lib_id)
        self.assertEqual(webpage_node.subject_id, subject_id)
        self.assertEqual(webpage_node.url, "www.example.com")
        self.assertIsNone(webpage_node.title)

    def test_update_webpage(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.bing.com")
        self.assertIsNone(result.title)
        result.title = "new title"
        result.content = "new summary"
        result.title_vector = [1, 2, 3]
        result.content_vector = [4, 5, 6]
        result.embedding_model = "sbert"
        updated_result = result.update()

        webpage_node = WebPage.get_webpage_by_element_id(result.element_id)
        self.assertIsNotNone(webpage_node)
        self.assertEqual(webpage_node.element_id, updated_result.element_id)
        self.assertEqual(webpage_node.lib_id, lib_id)
        self.assertEqual(webpage_node.subject_id, subject_id)
        self.assertEqual(webpage_node.url, "www.bing.com")
        self.assertEqual(webpage_node.title, "new title")
        self.assertEqual(webpage_node.content, "new summary")
        self.assertEqual(webpage_node.title_vector, [1, 2, 3])
        self.assertEqual(webpage_node.content_vector, [4, 5, 6])
        self.assertEqual(webpage_node.embedding_model, "sbert")

    def test_delete_webpages_by_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.bing.com")
        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.dudutalk.com")
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.webpages), 2)
        WebPage.delete_webpages_of_node(parent_node.element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.webpages), 0)

    def test_delete_webpage(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.bing.com")
        result = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, "www.dudutalk.com")
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.webpages), 2)
        WebPage.delete_webpage(result.webpages[0].element_id)
        result = Node.find_detail_by_element_id(parent_node.element_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.webpages), 1)


class TestGraphDocumentPageOperations(unittest.TestCase):
    def setUp(self):
        config.API_ENV = 'test' 
        config.UPLOAD_DIR = '.'
        config.IS_CAMEL_CASE = False
        self.lib_id = -13
        self.subject_id = -13
        self.knowledge_graph_query = KnowledgeGraphQuery()

    def tearDown(self):
        self.knowledge_graph_query.delete_graph_by_lib(self.lib_id)

    def test_add_document_page(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")

        document = Document.add_document_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")
        self.assertIsNotNone(document)
        self.assertIsNotNone(document.element_id)
        documet_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")
        self.assertIsNotNone(documet_page)
        self.assertIsNotNone(documet_page.element_id)
        self.assertEqual(documet_page.lib_id, lib_id)
        self.assertEqual(documet_page.subject_id, subject_id)
        self.assertEqual(documet_page.source, "source")
        self.assertEqual(documet_page.title, "title")
        self.assertEqual(documet_page.subtitle, "sub title")
        self.assertEqual(documet_page.row, 0)
        self.assertEqual(documet_page.page, 0)
        self.assertEqual(documet_page.content, "page content")
        self.assertEqual(documet_page.content_vector, [1, 2, 3])

        query_node_result = graph.query("MATCH (c:DocumentPage) where elementId(c)=$element_id return c", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_node_result), 1)

        query_reliationship_result = graph.query("MATCH (p)-[r]->(c:DocumentPage) where elementId(c)=$element_id return id(r) as id", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_reliationship_result), 2)

    def test_get_document_page_by_document(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
        document = Document.add_document_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")

        documet_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")

        pages = DocumentPage.get_document_pages_of_parent(document.element_id)
        self.assertEqual(len(pages), 1)

    def test_delete_document_page_by_document(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
        document = Document.add_document_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")

        documet_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")

        DocumentPage.delete_document_pages_of_parent(document.element_id)
        
        query_node_result = graph.query("MATCH (c:DocumentPage) where elementId(c)=$element_id return c", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_node_result), 0)
        query_reliationship_result = graph.query("MATCH (p)-[r]->(c:DocumentPage) where elementId(c)=$element_id return id(r) as id", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_reliationship_result), 0)

    def test_delete_document_page_by_parent_node(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
        document = Document.add_document_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")

        documet_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")

        DocumentPage.delete_document_pages_of_parent(parent_node.element_id)
        
        query_node_result = graph.query("MATCH (c:DocumentPage) where elementId(c)=$element_id return c", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_node_result), 0)
        query_reliationship_result = graph.query("MATCH (p)-[r]->(c:DocumentPage) where elementId(c)=$element_id return id(r) as id", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_reliationship_result), 0)

    def test_delete_document_page_by_page(self):
        lib_id = self.lib_id
        subject_id = self.subject_id
        parent_node, relationship = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
        document = Document.add_document_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")

        documet_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        parent_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")

        DocumentPage.delete_document_page(documet_page.element_id)
        
        query_node_result = graph.query("MATCH (c:DocumentPage) where elementId(c)=$element_id return c", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_node_result), 0)
        query_reliationship_result = graph.query("MATCH (p)-[r]->(c:DocumentPage) where elementId(c)=$element_id return id(r) as id", params={"element_id": documet_page.element_id})
        self.assertEqual(len(query_reliationship_result), 0)


if __name__ == '__main__':
    unittest.main()