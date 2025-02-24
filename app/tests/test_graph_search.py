import json

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

import core.config as config
import main
from ai.document_service import DocumentService
from ai.embedding import EmbeddingFactory
from ai.llm import Llm
from graph import NodeType, RelationshipType
from graph.document import Document
from graph.entity import Entity
from graph.gds_graph import GdsGraph
from graph.graph_query import KnowledgeGraphQuery, QueryResult
from graph.keyword import Keyword
from graph.node import Node
from graph.relationship import Relationship
from graph.tag import Tag
from graph.webpage import WebPage
from models.models import KnowledgeLib
from schemas.graph import GraphGenerateConditionView
from services.graph_service import GraphService
from services.knowledge_lib_service import KnowledgeLibService


@pytest.fixture(autouse=True)
def setup_function(monkeypatch) -> None:
    monkeypatch.setattr(config, 'API_ENV', 'test')
    monkeypatch.setattr(config, 'UPLOAD_DIR', '.')
    monkeypatch.setattr(config, 'IS_CAMEL_CASE', False)
    yield

@pytest_asyncio.fixture(scope="module")
async def client():
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    config.IS_CAMEL_CASE = False
    transport = ASGITransport(app=main.create_app())
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac

@pytest.fixture(scope="module")
def graph_service() -> GraphService:
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    return GraphService()

@pytest.fixture(scope="module")
def knowledge_graph_query() -> KnowledgeGraphQuery:
    config.API_ENV = 'test' 
    return KnowledgeGraphQuery(gds_graph_name=GdsGraph.test_graph_name)

@pytest.fixture(scope="module")
def document_service() -> DocumentService:
    return DocumentService()

@pytest.fixture(scope="module")
def embedding_factory() -> EmbeddingFactory:
    return EmbeddingFactory()

@pytest.fixture(scope="module")
def knowledge_lib_service() -> KnowledgeLibService:
    return KnowledgeLibService()

def init_test_data(
    lib_id: int, 
    subject_id: int, 
    llm_name: str, 
    embedding_model: str, 
    max_tokens_each_chunk: int, 
    knowledge_graph_query: KnowledgeGraphQuery,  # Pass the fixture as an argument
    graph_service: GraphService,  # Pass the fixture as an argument
    embedding_factory: EmbeddingFactory,
    document_service: DocumentService
) -> None:
    # Delete the graph for the given library ID
    knowledge_graph_query.delete_graph_by_lib(lib_id)
    
    # Add a subject node
    subject_node = Node.add_subject_node(lib_id, subject_id, "Weight Loss Diet", 1)
    
    # Read test data from a file
    info_title = "The Secret to Sustainable Weight Loss: It's All About Balance"
    with open("tests/data/13_query_test_data_simple_weight_loss_diet.txt", "r") as f:
        info_content = f.read()

    info_title_vector = embedding_factory.get_embedding(text=info_title, model_name=embedding_model,
                                                                max_tokens_each_chunk=max_tokens_each_chunk)
    info_content_vector = embedding_factory.get_embedding(text=info_content, model_name=embedding_model,
                                                                max_tokens_each_chunk=max_tokens_each_chunk)
    info_node: Node = Node(lib_id=lib_id, 
                    subject_id=subject_id, 
                    title=info_title,
                    content=info_content,  
                    type=NodeType.INFO,
                    title_vector=info_title_vector.tolist(),
                    content_vector=info_content_vector.tolist(),
                    embedding_model=embedding_model)
    info_node = info_node.save()
    Relationship.add_relationship(lib_id, subject_id, subject_node.element_id, info_node.element_id, RelationshipType.HAS_CHILD)

    # add entities
    general_entity = Entity.add_entity_node(lib_id, subject_id, info_node.element_id, "General")

    # add keywords
    content = "Weight Loss"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    weight_loss_keyword = Keyword.add_keyword_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "Diet"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    diet_keyword = Keyword.add_keyword_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "Healthy"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    healthy_keyword = Keyword.add_keyword_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "Balanced"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    balanced_keyword = Keyword.add_keyword_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "Low-Calorie"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    low_calorie_keyword = Keyword.add_keyword_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())

    # add tags
    content = "Healthy fat and protein intake for weight loss"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    healthy_fat_and_protein_intake_for_weight_loss_tag = Tag.add_tag_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "High fiber and high vegetable weight loss plan"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    high_fiber_and_high_vegetable_weight_loss_plan_tag = Tag.add_tag_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())
    content = "Balanced nutrition and low calorie diet"
    content_vector = embedding_factory.get_embedding(text=content, model_name=embedding_model,
                                                            max_tokens_each_chunk=max_tokens_each_chunk)
    balanced_nutrition_and_low_calorie_diet_tag = Tag.add_tag_node(lib_id, subject_id, info_node.element_id, content, content_vector.tolist())

    # add documents
    file_path = "tests/data/12_10_of_most_extreme_diets.txt"
    file_name = "12_10_of_most_extreme_diets.txt"
    document = Document.add_document_node(lib_id = lib_id,
                                        subject_id = subject_id, 
                                        parent_element_id = info_node.element_id, 
                                        name = file_name, 
                                        saved_at = file_path)
    document = graph_service.analyze_graph_node_file(document.element_id, llm_name,
                                                                embedding_model, max_tokens_each_chunk)
    document_title = "10 Extreme Diets to Avoid: Risks, Unbalanced Nutrition, and Unsustainability"
    document_content = "This article highlights 10 extreme diets that promise rapid weight loss or other health benefits but can be risky, unbalanced, and unsustainable. Examples include the Breatharian Diet, Cotton Ball Diet, Tapeworm Diet, Baby Food Diet, Cabbage Soup Diet, Paleolithic (Paleo) Diet (Extreme Version), Liquid Diet (Extreme Version), Master Cleanse (Lemonade Diet), Fruitarian Diet, and Zero-Carb Diet (Carnivore Diet). These diets can lead to health risks, nutrient deficiencies, and malnutrition. A balanced, sustainable approach to nutrition is always the safest and healthiest choice."
    document.title = document_title
    document.title_vector = embedding_factory.get_embedding(text=document.title,
                                                                    model_name=embedding_model,
                                                                    max_tokens_each_chunk=max_tokens_each_chunk)
    document.content = document_content
    document.content_vector = embedding_factory.get_embedding(text=document.content,
                                                                        model_name=embedding_model,
                                                                        max_tokens_each_chunk=max_tokens_each_chunk)
    document.update()

    # add webpages
    webpage1 = WebPage.add_webpage_node(lib_id, subject_id, info_node.element_id, "https://www.womenshealthmag.com/weight-loss/a42112641/7-day-meal-plan-for-weight-loss/")
    webpage1 = graph_service.analyze_graph_node_webpage(webpage1.element_id, llm_name,
                                                                embedding_model,
                                                                max_tokens_each_chunk)
    webpage1_title = "7-Day Diet Plan For Weight Loss: Menu, Shopping List, and Tips"
    webpage1_content = "This article provides a 7-day diet plan for weight loss, including menu suggestions, shopping lists, and tips. The meal plan includes healthy breakfast, lunch, and dinner options, as well as snack ideas. The shopping list includes staples such as Greek yogurt, strawberries, avocado, sweet potatoes, and mixed greens. Tips for successful weight loss include adding more veggies and fiber-rich foods to your diet, starting meals with a salad, and choosing nutrient-dense snacks."
    webpage1.title = webpage1_title
    webpage1.title_vector = embedding_factory.get_embedding(text=webpage1.title,
                                                                    model_name=embedding_model,
                                                                    max_tokens_each_chunk=max_tokens_each_chunk)
    webpage1.content = webpage1_content
    webpage1.content_vector = embedding_factory.get_embedding(text=webpage1.content,
                                                                        model_name=embedding_model,
                                                                        max_tokens_each_chunk=max_tokens_each_chunk)
    webpage1.update()

    webpage2 = WebPage.add_webpage_node(lib_id, subject_id, info_node.element_id, "https://www.dietdoctor.com/weight-loss/meal-plans/")
    webpage2 = graph_service.analyze_graph_node_webpage(webpage2.element_id, llm_name,
                                                                embedding_model,
                                                                max_tokens_each_chunk)
    webpage2_title = "8 Best Weight Loss Meal Plans & Meal Prep Tips"
    webpage2_content = "This guide provides an overview of the top 8 weight loss meal plans and meal prep tips, backed by scientific evidence. It covers topics such as low-carb diets, high-protein diets, and intermittent fasting, including references to peer-reviewed studies. The guide also discusses common side effects like keto flu and how to overcome them."
    webpage2.title = webpage2_title
    webpage2.title_vector = embedding_factory.get_embedding(text=webpage2.title,
                                                                    model_name=embedding_model,
                                                                    max_tokens_each_chunk=max_tokens_each_chunk)
    webpage2.content = webpage2_content
    webpage2.content_vector = embedding_factory.get_embedding(text=webpage2.content,
                                                                        model_name=embedding_model,
                                                                        max_tokens_each_chunk=max_tokens_each_chunk)
    webpage2.update()

    # add questions
    question_node1 = Node.add_question_node(lib_id, subject_id, "Why is it important to eat more vegetables and fruits as part of a weight loss diet?")
    Relationship.add_relationship(
        lib_id, subject_id, question_node1.element_id, info_node.element_id, RelationshipType.HAS_CHILD
    )
    graphGenerateConditionView = GraphGenerateConditionView(
        lib_id = lib_id,
        subject_id = subject_id,
        element_id = question_node1.element_id,
        llm_name = llm_name,
        embedding_model = embedding_model,
        max_tokens_each_chunk = max_tokens_each_chunk,
    )
    graph_service.analyze_graph_node(graphGenerateConditionView)
    question_node2 = Node.add_question_node(lib_id, subject_id, "How can controlling portion sizes help with weight loss?")
    Relationship.add_relationship(
        lib_id, subject_id, question_node2.element_id, info_node.element_id, RelationshipType.HAS_CHILD
    )
    graphGenerateConditionView.element_id = question_node2.element_id
    graph_service.analyze_graph_node(graphGenerateConditionView)
    question_node3 = Node.add_question_node(lib_id, subject_id, "What are the key principles of a balanced and nutritious weight loss diet?")
    Relationship.add_relationship(
        lib_id, subject_id, question_node3.element_id, info_node.element_id, RelationshipType.HAS_CHILD
    )
    graphGenerateConditionView.element_id = question_node3.element_id
    graph_service.analyze_graph_node(graphGenerateConditionView)

    # add answers
    answerGenerateCondition = GraphGenerateConditionView(
        lib_id = lib_id,
        subject_id = subject_id,
        element_id = question_node3.element_id,
        llm_name = llm_name,
        embedding_model = embedding_model,
        max_tokens_each_chunk = max_tokens_each_chunk,
    )
    answer_node, answer_relationship = graph_service.generate_answer(answerGenerateCondition)
    graphGenerateConditionView.element_id = answer_node.element_id
    graphGenerateConditionView.llm_name = "wizardlm2"
    graph_service.analyze_graph_node(graphGenerateConditionView)

    # add prompts
    promptGenerateCondition = GraphGenerateConditionView(
        lib_id = lib_id,
        subject_id = subject_id,
        element_id = info_node.element_id,
        llm_name = llm_name,
        embedding_model = embedding_model,
        max_tokens_each_chunk = max_tokens_each_chunk,
    )
    graph_service.generate_prompts(promptGenerateCondition)


@pytest_asyncio.fixture(scope="module")
async def setup_test_data(
    graph_service: GraphService, 
    knowledge_graph_query: KnowledgeGraphQuery, 
    document_service: DocumentService, 
    embedding_factory: EmbeddingFactory,
    client: AsyncClient,
) -> None:
    lib_id = 3
    subject_id = 9
    llm_name = "llama3.1"
    embedding_model = "sbert"
    max_tokens_each_chunk = 128

    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    config.IS_CAMEL_CASE = False

    # Initialize test data
    # init_test_data(lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, knowledge_graph_query, graph_service, embedding_factory, document_service)

    # Ensure the GDS graph is set up correctly
    if GdsGraph.check_gds_graph(GdsGraph.test_graph_name):
        GdsGraph.delete_gds_graph(GdsGraph.test_graph_name)
    GdsGraph.create_gds_graph(GdsGraph.test_graph_name)

    response = await client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"

    yield lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token

    # Cleanup after tests
    if GdsGraph.check_gds_graph(GdsGraph.test_graph_name):
        GdsGraph.delete_gds_graph(GdsGraph.test_graph_name)
    # knowledge_graph_query.delete_graph_by_lib(lib_id)


class TestKnowledgeGraphQuery:
    async def test_query_knowledge_graph_by_node_title(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        message = "The Secret to Sustainable Weight Loss: It's All About Balance"
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["question", "page", "document", "webpage", "node"])

        assert query_result is not None, "Query result should not be None"
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance", "Main node title does not match"
        assert len(query_result.prompts) == 3, "Expected 3 prompts"
        assert len(query_result.related_nodes) == 1, "Expected 1 related node"
        assert len(query_result.entities) == 1, "Expected 1 entity"
        assert len(query_result.keywords) == 5, "Expected 5 keywords"
        assert len(query_result.tags) == 3, "Expected 3 tags"

    def test_query_knowledge_graph_by_node_title_fulltext(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data):
        # Arrange
        message = "The Secret to Sustainable Weight Loss: It's All About Balance"
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                lib_id=lib_id, 
                                                                search_scope=["question", "page", "document", "webpage", "node"],
                                                                search_type="fulltext")

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_invalid_node_title(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data):
        # Arrange
        message = "E-commerce customer service outsourcing"
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        
        # Act
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["question", "page", "document", "webpage", "node"])

        # Assert
        assert query_result is None
        

    def test_query_knowledge_graph_by_invalid_node_title_fulltext(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "E-commerce customer service outsourcing"
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        
        # Act
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["question", "page", "document", "webpage", "node"], search_type="fulltext")

        # Assert
        assert query_result is None


    def test_query_knowledge_graph_by_node_content(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data):
        # Arrange
        message = """
                        A well-rounded diet rich in nutrients is foundational for sustainable weight loss. This includes:

            - **Fruits and Vegetables**: Aim for a variety to ensure a wide range of vitamins and minerals.
            - **Lean Proteins**: Sources like chicken, fish, legumes, and nuts support muscle maintenance.
            - **Whole Grains**: Foods like brown rice and whole wheat bread provide essential fiber.
            - **Healthy Fats**: Incorporate sources such as avocados and olive oil to promote satiety.
            Citations:
            [1] https://continentalhospitals.com/blog/8-proven-strategies-for-sustainable-weight-loss/
            [2] https://activefibershake.us/blogs/news/losing-weight-and-keeping-it-off-the-secret-to-sustainable-weight-loss
            [3] https://www.healthhero.ie/blog/comprehensive-guide-to-safe-and-sustainable-weight-loss
            [4] https://www.instagram.com/thebalancingbean/reel/DFDePeLg6zb/
            [5] https://www.archbold.org/articles/2021/september/5-habits-for-sustainable-weight-loss-don-t-short/
            [6] https://www.journee-mondiale.com/en/i-lost-23-pounds-with-this-balanced-diet-no-deprivation-needed/
            [7] https://www.healthline.com/health/weight-loss/sustainable-weight-loss
            [8] https://www.linkedin.com/pulse/unlocking-secrets-sustainable-weight-loss-guide-kyle-thoroughman-uxh1c
         """
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        # Act
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["question", "page", "document", "webpage", "node"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_node_content_by_hybrid(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = """ A well-rounded diet rich in nutrients is foundational for sustainable weight loss. This includes:

            - **Fruits and Vegetables**: Aim for a variety to ensure a wide range of vitamins and minerals.
            - **Lean Proteins**: Sources like chicken, fish, legumes, and nuts support muscle maintenance.
            - **Whole Grains**: Foods like brown rice and whole wheat bread provide essential fiber.
            - **Healthy Fats**: Incorporate sources such as avocados and olive oil to promote satiety.
            Citations:
            [1] https://continentalhospitals.com/blog/8-proven-strategies-for-sustainable-weight-loss/
            [2] https://activefibershake.us/blogs/news/losing-weight-and-keeping-it-off-the-secret-to-sustainable-weight-loss
            [3] https://www.healthhero.ie/blog/comprehensive-guide-to-safe-and-sustainable-weight-loss
            [4] https://www.instagram.com/thebalancingbean/reel/DFDePeLg6zb/
            [5] https://www.archbold.org/articles/2021/september/5-habits-for-sustainable-weight-loss-don-t-short/
            [6] https://www.journee-mondiale.com/en/i-lost-23-pounds-with-this-balanced-diet-no-deprivation-needed/
         """
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        # Act
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["node"], search_type="hybrid")

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_invalid_node_content(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = """
            What Temperature monitoring equipment**: The temperature monitoring equipment should be cal
            ibrated and qualified, and the measured temperature parameters should meet
             ution should not be greater than 0.1°C.
        """
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        # Act
        query_result = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["node"], search_type="hybrid")

        # Assert
        assert query_result is None

    def test_query_knowledge_graph_by_node_question(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "	How to controlling portion sizes for weight loss "
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["node"], search_type="hybrid")

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_invalid_node_question(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "Incorporating physical activity into daily routines is essential for burning calories and maintaining muscle mass. A combination of aerobic exercises"
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["node"], search_type="hybrid")

        # Assert
        assert query_result is not None
        assert query_result.document_page is  None
        assert query_result.webpage is None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3
        

    def test_query_knowledge_graph_by_document_file_slice_by_hybrid(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "Extreme diets often promise rapid weight loss or other health benefits but can be risky, unbalanced, and unsustainable. Here are 10 examples of extreme diets:"
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["page", "document"], search_type="hybrid")

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is None
        assert query_result.document is not None
        assert query_result.document.name == "12_10_of_most_extreme_diets.txt"
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_document_file_slice_by_fulltext(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "A short-term diet centered around eating "

        # Act
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                        search_type="fulltext", 
                                                                                        lib_id=lib_id, 
                                                                                        search_scope=["page", "document"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is None
        assert query_result.document is not None
        assert query_result.document.name == "12_10_of_most_extreme_diets.txt"
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3


    def test_query_knowledge_graph_by_document_webpage_slice_by_fulltext(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "and two poached eggsLunch: Mixed green salad with carrots, cucumbers, ½ avocado sliced, and 3 to 4 ounces broiled salmon, topped with a dash of olive oil and vinegarSnack: Three cups air-popped popcornDinner:"

        # Act
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                        search_type="fulltext", 
                                                                                        lib_id=lib_id, 
                                                                                        search_scope=["page", "webpage"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is not None
        assert query_result.webpage.url == "https://www.womenshealthmag.com/weight-loss/a42112641/7-day-meal-plan-for-weight-loss/"
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3


    def test_query_knowledge_graph_by_document_webpage_slice_fulltext(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        message = "7-day diet plan for weight loss created by nutritionist Keri Gans"

        # Act
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                        search_type="fulltext", 
                                                                                        lib_id=lib_id, 
                                                                                        search_scope=["page", "webpage"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is not None
        assert query_result.webpage.url == "https://www.womenshealthmag.com/weight-loss/a42112641/7-day-meal-plan-for-weight-loss/"
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3



    def test_query_knowledge_graph_by_mutliple_message(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message1 = "How can controlling portion sizes help with weight loss?"
        message2 = "Control the portion"
        message3 = "7-day diet plan for weight loss, including menu suggestions, tips"
        messages=[message1, message2, message3]

        summary = Llm.summary_message_history(
                messages=messages,
                llm_name="wizardlm2",
                chain_type="stuff"
            )
        if summary:
            summary_message = summary.get("output_text")
        else:
            summary_message = messages[-1]

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=summary_message, lib_id=lib_id, search_scope=["page", "webpage"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is not None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_invalid_message(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "What are the logists process?"
        
        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, lib_id=lib_id, search_scope=["page", "webpage"])

        # Assert
        assert query_result is None

    def test_query_knowledge_graph_by_only_title(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message1 = "Weight Loss?"
        message2 = "Diet"
        message3 = "8 Best Weight Loss Meal Plans & Meal Prep Tips"
        messages=[message1, message2, message3]

        summary = Llm.summary_message_history(
                messages=messages,
                llm_name="wizardlm2",
                chain_type="stuff"
            )
        if summary:
            summary_message = summary.get("output_text")
        else:
            summary_message = messages[-1]

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=summary_message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["page", "webpage"],
                                                                                    only_title=True)

        # Assert
        assert query_result is not None
        assert query_result.document_page is not None
        assert query_result.webpage is not None
        assert query_result.document is None
        assert query_result.main_node is not None
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_only_question(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, this message will be found by document page
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "7-day diet plan for weight loss, including menu suggestions, tips"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["question"])

        # Assert
        assert query_result is None
        
    def test_query_knowledge_graph_by_only_document_page(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, this message will be found by node title
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "The Secret to Sustainable Weight Loss: It's All About Balance"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["page"])

        # Assert
        assert query_result is None


    def test_query_knowledge_graph_by_only_document(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, this message will be found by node title
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "The Secret to Sustainable Weight Loss: It's All About Balance"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["document"])

        # Assert
        assert query_result is None

    def test_query_knowledge_graph_by_only_webpage(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, this message will be found by node title
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "The Secret to Sustainable Weight Loss: It's All About Balance"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["webpage"])

        # Assert
        assert query_result is None

    def test_query_knowledge_graph_by_only_node_invalid_message(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, This message will be found first through the document page or web page, if the scope is not set
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "Logistics transportation process"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["node"])

        # Assert
        assert query_result is None

    def test_query_knowledge_graph_by_only_node_has_document(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, This message will be found first through the document page or document, if the scope is not set
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "10 Extreme Diets to Avoid: Risks, Unbalanced Nutrition, and Unsustainability"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["node"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is None
        # hit another node
        assert query_result.main_node is not None
        assert query_result.main_node.type == NodeType.INFO
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

    def test_query_knowledge_graph_by_only_document_and_node(self, knowledge_graph_query: KnowledgeGraphQuery, setup_test_data) -> None:
        # Arrange, This message will be found first through the document page or document, if the scope is not set
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data

        message = "10 Extreme Diets to Avoid: Risks, Unbalanced Nutrition, and Unsustainability"

        # Act
        query_result: QueryResult = knowledge_graph_query.search_knowledge_graph(message=message, 
                                                                                    lib_id=lib_id, 
                                                                                    search_scope=["document", "node"])

        # Assert
        assert query_result is not None
        assert query_result.document_page is None
        assert query_result.webpage is None
        assert query_result.document is not None
        assert query_result.main_node is not None
        assert query_result.main_node.title == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.prompts) == 3
        assert len(query_result.related_nodes) == 1
        assert len(query_result.entities) == 1
        assert len(query_result.keywords) == 5
        assert len(query_result.tags) == 3

@pytest.mark.asyncio(loop_scope="session")
class TestKnowledgeGraphQueryByClient:
    async def test_query_knowledge_graph_by_client_miss_token(self, client: AsyncClient, setup_test_data) -> None:
        messages = [
            "How can controlling portion sizes help with weight loss?",
        ]
        response = await client.post("/api/graph/search",
                                    json={"messages": messages, 
                                        "return_method": "sync",
                                        "search_scope": ["page", "webpage", "document", "node"]})
        
        assert response.status_code == 401, "Expected status code 401"


    async def test_query_knowledge_graph_by_client_miss_lib_id(self, client: AsyncClient, setup_test_data) -> None:
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        messages = [
            "How can controlling portion sizes help with weight loss?",
        ]
        response = await client.post("/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "return_method": "sync",
                                        "search_scope": ["page", "webpage", "document", "node"]})
        
        assert response.status_code == 422, "Expected status code 422"
        assert response.json().get("code") == 10002, "Expected code 10002"
        assert response.json().get("msg") == "Invalid request body", "Expected msg to be Invalid request body"

    async def test_query_knowledge_graph_by_client_invalid_lib_id(self, client: AsyncClient, setup_test_data) -> None:
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        messages = [
            "How can controlling portion sizes help with weight loss?",
        ]
        response = await client.post("/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "lib_id": -1,
                                        "return_method": "sync",
                                        "search_scope": ["page", "webpage", "document", "node"]})
        
        assert response.status_code == 200, "Expected status code 200"
        assert response.json().get("code") == -1, "Expected code -1"
        assert response.json().get("msg") == "Knowledge library not found", "Expected msg to be Knowledge library not found"


    async def test_query_knowledge_graph_by_client_unpublish_lib(self, client: AsyncClient, setup_test_data) -> None:
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        messages = [
            "How can controlling portion sizes help with weight loss?",
        ]
        response = await client.post("/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "lib_id": lib_id,
                                        "return_method": "sync",
                                        "search_scope": ["page", "webpage", "document", "node"]})
        
        assert response.status_code == 200, "Expected status code 200"
        assert response.json().get("code") == -1, "Expected code -1"
        assert response.json().get("msg") == "Knowledge library is not published", "Expected msg to be Knowledge library is not published"


    async def test_query_knowledge_graph_by_client(self, client: AsyncClient, 
                                                knowledge_lib_service: KnowledgeLibService, 
                                                setup_test_data) -> None:
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status != 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'
        messages = [
            "How can controlling portion sizes help with weight loss?",
            "Control the portion",
            "7-day diet plan for weight loss, including menu suggestions, tips"
        ]
        response = await client.post("/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "lib_id": lib_id, 
                                        "return_method": "sync",
                                        "search_scope": ["page", "webpage", "document", "node"]})
        
        assert response.status_code == 200, "Expected status code 200"
        query_result = response.json().get("data")
        assert query_result is not None, "Query result should not be None"
        assert query_result.get("main_node").get("title") == "The Secret to Sustainable Weight Loss: It's All About Balance", "Main node title does not match"
        assert len(query_result.get("entities")) == 1, "Expected 1 entity"
        assert query_result.get("entities")[0].get("content") == 'General', "Entity content does not match"
        assert len(query_result.get("keywords")) == 5, "Expected 5 keywords"
        assert query_result.get("keywords")[0].get("content") == 'Weight Loss', "Keyword content does not match"
        assert len(query_result.get("tags")) == 3, "Expected 3 tags"
        assert query_result.get("tags")[0].get("content") == 'Healthy fat and protein intake for weight loss', "Tag content does not match"
        assert len(query_result.get("prompts")) == 3, "Expected 3 prompts"
        assert len(query_result.get("related_nodes")) == 1, "Expected 1 related nodes"

        # clean up
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status == 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'   

    async def test_query_knowledge_graph_by_client_only_document_and_node(self, client: AsyncClient, 
                                                                                knowledge_lib_service: KnowledgeLibService,
                                                                                setup_test_data) -> None:
        # Arrange, This message will be found first through the document page or document, if the scope is not set
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status != 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'
        message = "10 Extreme Diets to Avoid: Risks, Unbalanced Nutrition, and Unsustainability"

        # Act
        response = await client.post(f"/api/graph/search", 
                                        headers={"Authorization": valid_token}, 
                                        json={"messages": [message], 
                                            "lib_id": lib_id, 
                                            "search_scope": ["document", "node"], 
                                            "is_summary": False})
        query_result: QueryResult = response.json().get("data")

        # Assert
        assert response.status_code == 200
        query_result: QueryResult = response.json().get("data")
        assert query_result is not None
        assert query_result.get("text").strip()[:20] == "This article highlig"
        assert query_result.get("document_page") is None
        assert query_result.get("webpage") is None
        assert query_result.get("document") is not None
        assert query_result.get("main_node").get("title") == "The Secret to Sustainable Weight Loss: It's All About Balance"
        assert len(query_result.get("entities")) == 1
        assert query_result.get("entities")[0].get("content") == 'General'
        assert len(query_result.get("keywords")) == 5
        assert query_result.get("keywords")[0].get("content") == 'Weight Loss'
        assert len(query_result.get("tags")) == 3
        assert query_result.get("tags")[0].get("content") == 'Healthy fat and protein intake for weight loss'
        assert len(query_result.get("prompts")) == 3
        assert len(query_result.get("related_nodes")) == 1

        # clean up
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status == 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'   

    async def test_query_knowledge_graph_by_client_by_refine(self, client: AsyncClient, 
                                                                knowledge_lib_service: KnowledgeLibService, 
                                                                setup_test_data):
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status != 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'
        message1 = "How can controlling portion sizes help with weight loss?"
        message2 = "Control the portion"
        message3 = "7-day diet plan for weight loss, including menu suggestions, tips"
        messages=[message1, message2, message3]

        # Act
        response = await client.post(f"/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "lib_id": lib_id, 
                                        "chain_type": "refine", 
                                        "search_scope": ["page", "webpage", "document", "node"]})

        # Assert
        assert response.status_code == 200
        query_result: QueryResult = response.json().get("data")
        assert query_result is not None

        # clean up
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status == 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'   

    async def test_query_knowledge_graph_by_client_by_map_reduce(self, client: AsyncClient, 
                                                                knowledge_lib_service: KnowledgeLibService, 
                                                                setup_test_data):
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status != 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'
        message1 = "How can controlling portion sizes help with weight loss?"
        message2 = "Control the portion"
        message3 = "7-day diet plan for weight loss, including menu suggestions, tips"
        messages=[message1, message2, message3]

        # Act
        response = await client.post(f"/api/graph/search", 
                                    headers={"Authorization": valid_token}, 
                                    json={"messages": messages, 
                                        "lib_id": lib_id, 
                                        "chain_type": "map_reduce", 
                                        "search_scope": ["page", "webpage", "document", "node"]})

        # Assert
        assert response.status_code == 200
        query_result: QueryResult = response.json().get("data")
        assert query_result is not None

        # clean up
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status == 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'   

    async def test_query_knowledge_graph_by_client_by_streaming(self, client: AsyncClient, 
                                                                knowledge_lib_service: KnowledgeLibService,
                                                                setup_test_data):
        # Arrange
        lib_id, subject_id, llm_name, embedding_model, max_tokens_each_chunk, valid_token = setup_test_data
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status != 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test'
        messages = [
            "How can controlling portion sizes help with weight loss?",
            "Control the portion",
            "7-day diet plan for weight loss, including menu suggestions, tips"
        ]

        # Act
        async with client.stream(
            "POST", "/api/graph/search",
            headers={"Authorization": valid_token},
                json={
                    "messages": messages,
                    "lib_id": lib_id,
                    "return_method": "stream",
                    "search_scope": ["page", "webpage", "document", "node"]
                }
            ) as response:
            response.raise_for_status()  # Ensure request is successful

            received_chunks = []
            async for chunk in response.aiter_lines():
                if not chunk.strip():
                    continue  # Ignore empty lines

                try:
                    data = json.loads(chunk)
                    received_chunks.append(data)
                except json.JSONDecodeError:
                    pytest.fail(f"Received invalid JSON: {chunk}")

                if data.get("status") == "error":
                    pytest.fail(f"Error in response: {data.get('error')}")
                elif data.get("end") == True:
                    assert True, "Stream ended with data"
                else:
                    assert "text" in data, "Missing 'text' field in response"

        # Assert
        assert response.status_code == 200
        assert len(received_chunks) > 0, "No data received from the stream"

        # clean up
        config.API_ENV = 'dev'
        knowledge_lib: KnowledgeLib = await knowledge_lib_service.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status == 'PUBLISHED':
            await knowledge_lib_service.toggle_knowledge_lib_publish(lib_id)
        config.API_ENV = 'test' 

if __name__ == '__main__':
    pytest.main()