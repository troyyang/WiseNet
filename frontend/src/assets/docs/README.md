# WiseNet
## **WiseNet: Intelligent Knowledge Base Construction Tool**

---

## **1. Project Introduction**

**WiseNet** is an intelligent knowledge management tool powered by **Large Language Models (LLMs)**. It automates the generation of related sub-questions and constructs a **networked knowledge graph**, offering an **efficient and intuitive** knowledge management experience. The system enables **full-process automation from problem input to knowledge network construction**, significantly enhancing knowledge organization and retrieval efficiency.

### **Core Capabilities**
- **Intelligent Knowledge Expansion**: Automatically generates sub-questions to build a clear, hierarchical knowledge graph.
- **Multilingual Support**: Utilizes the **SBERT high-accuracy vector model** for cross-language Q&A and knowledge construction.
- **Multi-Data Source Integration**: Supports **document uploads (txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON)** and **webpage parsing**, with automatic content vectorization.
- **Powerful Search Capabilities**: Combines **Neo4j** and **Milvus** for **efficient vector retrieval** and **semantic matching**, optimizing knowledge discovery.
- **Retrieval-Augmented Generation (RAG)**: Enhances LLM responses by retrieving relevant knowledge from structured graphs and vector databases, ensuring accurate and contextually relevant answers.
- **Modular Architecture**: Flexible and extensible, supporting integration of various LLM models and custom function modules.

WiseNet integrates cutting-edge technologies like **Neo4j, Milvus, and D3.js**, delivering **intelligent, one-stop knowledge management solutions** for industries such as **logistics scheduling, customer service knowledge bases, and enterprise knowledge management**.

---

## **2. Project Features**

### **📌 Intelligent Knowledge Construction**
- **Automated Knowledge Network Expansion**: Uses LLMs to generate relevant sub-questions, enhancing knowledge completeness and usability.
- **Knowledge Graph Storage**: Leverages **Neo4j** for structured knowledge storage, supporting hierarchical relationships and node association analysis.
- **NLP Entity Extraction**: Automatically extracts key entities (e.g., names, organizations, concepts) from text, enriching the knowledge network.

### **🎯 Efficient Search & Vector Retrieval**
- **Vector Search**:
  - Current Solution: **Neo4j HNSW Vector Index**, enabling semantic-level similarity matching.
  - Future Solution: Integration with **Milvus** for more efficient vector retrieval in large-scale knowledge queries.
- **Semantic Retrieval & Association Matching**: Combines **Neo4j + LLM** for **precise semantic search** and **intelligent recommendations**.

### **📊 Visualization & Knowledge Analysis**
- **D3.js Knowledge Graph**: Provides interactive visualization of the knowledge network, supporting **dynamic updates, node dragging, and relationship editing**.
- **Multidimensional Analysis**:
  - **Overall Knowledge Network Analysis**: Insights into knowledge structure and key nodes.
  - **Single Node Analysis**: Deep dive into knowledge points and their relationships.
  - **Document & Webpage Single-Point Analysis**: Personalized knowledge analysis and association discovery.

### **🌍 Multilingual Support & Document Parsing**
- **Multilingual Capabilities**: Utilizes **SBERT multilingual vector model**, enabling cross-language Q&A and knowledge management.
- **Document Parsing & Webpage Processing**:
  - Supports multiple formats (**txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON**).
  - Parses and vectorizes web content, with **future support for automatic website update tracking** to maintain real-time knowledge base updates.

### **🤖 LLM Support & Extensibility**
- **Local LLM Support**: Compatible with **Ollama**, supporting local LLMs like **WizardLM2** and **Llama3**.
- **API LLM Integration**: Supports **OpenAI, Anthropic, Tongyi, Doubao, DeepSeek**, and other mainstream LLMs.
- **Modular Architecture**: **Highly extensible and compatible**, allowing integration of new AI models, databases, and business modules for diverse application scenarios.

---

## **3. Application Scenarios**

WiseNet’s intelligent knowledge management capabilities are applicable across various fields:

### 🚚 **Logistics Scheduling Optimization**
- **Intelligent Dispatching Decisions**: Constructs logistics scheduling knowledge networks, automatically generating optimal routing and resource allocation sub-questions.
- **Real-Time Information Integration**: Supports automatic parsing and integration of multiple data sources (e.g., weather, traffic, orders) for dynamic dispatch recommendations.
- **Anomaly Handling**: Quickly locates problem nodes in the knowledge graph and generates solutions to minimize logistics disruptions.

### 📞 **Customer Service Knowledge Base**
- **Intelligent Q&A System**: Automatically generates FAQs and sub-questions to build a multi-tiered customer service knowledge base, improving response speed and accuracy.
- **Multilingual Support**: Enables cross-language customer service Q&A for global business operations.
- **Knowledge Updates**: Automatically parses the latest documents or web content to maintain real-time and accurate knowledge bases.

### 🏢 **Enterprise Knowledge Management**
- **Knowledge Accumulation & Sharing**: Converts internal documents and meeting records into structured knowledge networks for easy retrieval and learning.
- **Intelligent Search & Recommendations**: Uses semantic search to locate relevant knowledge and recommend related content.
- **Knowledge Analysis**: Analyzes enterprise knowledge networks to identify key nodes and gaps, optimizing knowledge management strategies.

### 🏭 **Manufacturing & Industry**
- **Equipment Maintenance & Fault Diagnosis**: Predicts failures based on historical data and maintenance records, optimizing maintenance schedules.
- **Supply Chain Optimization**: Builds supply chain knowledge networks to optimize inventory management and production scheduling.
- **Quality Management**: Analyzes production data to identify quality issues and improve product pass rates.

### ⚖️ **Legal & Compliance**
- **Legal Document Parsing**: Builds regulatory knowledge graphs to enhance legal research and compliance management.
- **Case Analysis & Reasoning**: Provides intelligent recommendations based on legal precedents and regulations.
- **Contract Review Automation**: Identifies contract clause risks and suggests modifications to improve contract management efficiency.

---

## **4. System Architecture**

```
+--------------------------------------------------------+
|                     User Interface (Frontend)          |
|         - Input Queries        - Knowledge Graph UI    |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                 Q&A and Expansion Engine (Backend)   |
|   - LLM API Calls        - Sub-question Generation   |
|   - Data Storage Mgmt    - Knowledge Retrieval       |
|   - NLP Entity Extraction - Document Parsing         |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                   Data Storage Layer                 |
|   - Graph Database (Neo4j) - Structured Knowledge    |
|   - Vector Search (Neo4j) - Current Retrieval       |
|   - Vector Database (Milvus) - Future Expansion     |
+--------------------------------------------------------+
```

## **Basic Concepts**
### **Knowledge Base**
A collection of knowledge related to a specific domain, such as **logistics scheduling** or **customer service knowledge bases**.

### **Knowledge Base Topic**
Different topics within a knowledge base, each representing an independent knowledge network.

### **Nodes**
The core data units in the knowledge network:
- **Node (General Nodes)**
  - **ROOT**: The root node of the knowledge base.
  - **SUBJECT**: The root node of a topic.
  - **QUESTION**: Nodes used for retrieval, generated by AI.
  - **PROMPT**: A question or hint node.
  - **INFO**: AI-generated information nodes (text, documents, websites, etc.).
  - **HUMAN**: Manually created knowledge nodes.

### **Relationships**
- **HAS_CHILD**: Represents a parent-child relationship.
- **RELATED_TO**: Represents a link between nodes.

## **Database Structure**
### **Relational Database (PostgreSQL)**
- **Knowledge Base Table**: Stores basic knowledge base information.
- **Knowledge Base Topic Table**: Stores different knowledge topics.
- **User Data Table**: Manages user data for multi-user isolation.

### **Graph Database (Neo4j)**
- **Nodes**: Each node has **lib_id** and **subject_id** for data isolation.
- **Relationships**: Define hierarchical and associative relationships.
- **Vector Storage**:
  - **Text Embedding**: Each text node contains an `embedding` attribute.
  - **Neo4j HNSW Vector Index**: Enables efficient similarity searches.

### **Milvus (Future Vector Database)**
- Plans to store embeddings for questions/answers to enhance similarity search efficiency.

### **Database structure description**
#### **Relational database (PostgreSQL)**
- **Knowledge Base**: used to store basic information of the knowledge base
- **Knowledge Base Topic**: used to store information of each topic
- **User Data**: used to manage user data and implement user isolation of the knowledge base

#### **Graph database (Neo4j)**
- **Nodes**
- **ROOT**: root node related to the knowledge base
- **SUBJECT**: topic node related to the knowledge base
- **QUESTION**: question node, used to store questions raised by users
- **PROMPT**: prompt node, used to store user prompt information
- **INFO**: information node, used to store knowledge point content (text, file, URL, etc.)
- **HUMAN**: manually input information node, used to store manually input knowledge point content (text, file, URL, etc.)
- **Entity**, **Keyword**, **Tag**, **DocumentPage**, **Document**, **WebPage**, these auxiliary nodes are not displayed in the network diagram, but can be viewed and maintained in the node properties
- All nodes contain **lib_id** and **subject_id** to ensure the isolation and maintenance of data between different knowledge bases

- **Relationships**
- Used to represent the hierarchy (HAS_CHILD) and association (RELATED_TO) between nodes
- All relationships contain **lib_id** and **subject_id** to ensure the isolation and maintenance of data between different knowledge bases

- **Vector storage (current solution)**
- **Text vectorization (Embedding)**: Each text node contains the `embedding` attribute
- **Neo4j HNSW vector index**: used for efficient similarity search

---

## **5. Contribution Guidelines**
### **How to Contribute**
1. Fork the repository.
2. Clone the repository locally:
   ```bash
   git clone https://github.com/troyyang/WiseNet.git
   ```
3. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature
   ```
4. Commit and push changes:
   ```bash
   git commit -m "Add new feature"
   git push origin feature/your-feature
   ```
5. Submit a pull request and await review.

---

## **6. Deployment**

### **6.1 Local Deployment (Using Poetry)**

#### **OS-Specific Deployment Guide**

##### **For Windows**
1. Install [Python](https://www.python.org/downloads/) (ensure it's added to PATH).
2. Install [Poetry](https://python-poetry.org/docs/#installation).
3. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### **For macOS/Linux**
1. Install Python via Homebrew or system package manager.
2. Install Poetry following [official docs](https://python-poetry.org/docs/#installation).
3. Install Docker and Docker Compose.

### **Clone the Repository**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Set Up a Virtual Environment**
```bash
cp .env.example .env
```
Modify the `.env` file with your desired configurations.

### **Start Dependency Services**
Ensure Docker and Docker Compose are installed and running.
```bash
docker compose -f docker-compose-base.yml up -d
```
If use GPU for local model, you can use:
```bash
docker compose -f docker-compose-base-gpu.yml up -d
```

#### **Check Neo4j Installation**
```bash
docker logs neo4j
```
Wait for the output:
```
2025-02-10 02:52:59.873+0000 INFO  Remote interface available at http://localhost:7474/
2025-02-10 02:52:59.875+0000 INFO  Started.
```
If the Neo4j Docker container is starting for the first time, it will install plugins:
```
Installing Plugin 'graph-data-science' from https://graphdatascience.ninja/neo4j-graph-data-science-2.13.2.jar to /var/lib/neo4j/plugins/graph-data-science.jar
```
Please wait for the installation to complete.

#### **Check Ollama Installation**
```bash
docker logs ollama
```
Ensure the output shows:
```
All models pulled successfully.
```
Verify local models:
```bash
docker exec -it ollama ollama list
```
If no models are listed, manually pull them:
```bash
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull wizardlm2
```

#### **Run FastAPI Backend**
Ensure Python 3.10.12 and pip are installed.

Navigate to the backend directory:
```bash
cd app
```
Install Poetry:
```bash
pip install poetry
```
Enter the Poetry environment:
```bash
poetry shell
```
Install dependencies:
```bash
poetry install
```
Install Babel:
```bash
pip install Babel
```
Translate the i18n messages:
```bash
pybabel compile -d translations
```
Run the FastAPI backend:
```bash
python main.py
```

#### **Start Frontend**
Ensure Node.js v18.0.0 and npm v8.6.0 are installed.

Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
npm run dev
```

### **6.2 Docker Deployment**

#### **Clone the Repository**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Set Up a Virtual Environment**
```bash
cp .env.example .env
```
Modify the `.env` file with your desired configurations.
Pay special attention to the modifications: FRONTEND_API_BASE_URL='http://your-domain:8088'

### **Execute install.sh**
```bash
./install.sh
```

Visit [http://localhost:3000/](http://localhost:3000/) to access the frontend. A Windows `.bat` script is also available for Windows users.

---

## **7. Future Plans**
- **Integrate local LLM**: Improve private deployment capabilities and support more local models.
- **Enhance the visual interaction function of the knowledge graph**: Support dynamic updates, node dragging, relationship editing, etc.
- **Gradually transition to Milvus**: Perform more efficient vector search and support large-scale knowledge bases.
- **Provide RESTful API and WebSocket support**: Convenient integration with other systems.
- **Multi-user support**: Support multi-user concurrent access and provide user permission management functions.
- **Knowledge base version control**: Support version management and rollback functions of the knowledge base.
- **Real-time knowledge update**: Support automatic tracking of website updates and synchronize the latest content to the knowledge base in real time.
- **Multimodal support**: Expand to multimodal data such as images and audio to build a richer knowledge network.
- **Enhance analytical capabilities**: Introduce more AI analytical tools (such as causal reasoning and trend prediction) to enhance the insight of the knowledge network.

---

## **8. License**  
This project is licensed under **GPL-3.0**, allowing free use and modification.  

---

## **9. Appendix**  

### **Frequently Asked Questions (FAQ)**  
- **How can I improve the speed of knowledge network construction?**  
  - Increase parallel processing tasks, optimize LLM invocation strategies, and use more efficient vector search algorithms.  
- **How can I extend WiseNet’s functionality?**  
  - WiseNet’s modular architecture allows for expansion through new modules or plugins, such as integrating additional LLM models or supporting new data sources.  

### **Related Resources**  
- [Neo4j Official Documentation](https://neo4j.com/docs/)  
- [Milvus Official Documentation](https://milvus.io/docs/)  
- [D3.js Official Documentation](https://d3js.org/)  
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)  
- [Arco Design Vue Official Documentation](https://arco.design/vue/)

### **Contact Us**  
For questions or suggestions, contact [troy.yang2@gmail.com](mailto:troy.yang2@gmail.com).  

---