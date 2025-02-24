Here is the English version of the provided text:

---

# WiseNet

WiseNet is an intelligent knowledge base construction tool based on large language models (LLMs). By inputting a question, the system utilizes the reasoning capabilities of LLMs to automatically generate related sub-questions and progressively explore the depth and breadth of the question, forming a web-like domain knowledge base.

## Features
- **Intelligent Inquiry**  
  Combines LLM question-answering and sub-question generation capabilities to automatically derive related sub-questions.  
  Supports multi-level recursive questioning to gradually build a complete knowledge graph.
- **Web-like Knowledge Structure**  
  Stores questions, answers, and their relationships in a graph database (Neo4j) to form a web-like structure.  
  Intuitively displays the connection paths between questions, facilitating knowledge exploration and querying.
- **Visual Interaction**  
  Uses visualization tools (such as D3.js) to dynamically display the knowledge network.  
  Supports features like node clicking, search filtering, and path tracing.
- **Knowledge Accumulation**  
  Automatically saves questions and answers to achieve continuous accumulation and updating of knowledge.  
  Supports exporting and importing the knowledge base for easy sharing and migration.

## System Architecture
```plaintext
+--------------------------------------------------------+
|                     User Interface (Frontend)         |
|         - Input Questions         - Knowledge Network Visualization |
+------------------------+-------------------------------+
                         | 
+------------------------v-------------------------------+
|                 Q&A and Inquiry Engine (Backend)      |
|   - LLM API Calls       - Sub-question Generation and Depth Control |
|   - Data Storage Management   - Knowledge Retrieval and Update |
+------------------------+-------------------------------+
                         |
+------------------------v-------------------------------+
|                   Data Storage Layer                  |
|   - Graph Database (Neo4j) - Storage of Questions and Relationships |
|   - Document Database (MongoDB) - Storage of Question/Answer Texts |
+--------------------------------------------------------+
```

## Technology Stack
- **Backend**: Python + FastAPI  
- **Frontend**: React.js + D3.js / Cytoscape.js  
- **Databases**: Neo4j (Graph Database), MongoDB (Document Database)  
- **Large Model Interfaces**: OpenAI GPT-4 / Local LLM Models (e.g., LLaMA)  
- **Vector Embeddings**: OpenAI Embeddings / Sentence-BERT

## Installation and Running
1. Clone the project code
   ```bash
   git clone https://github.com/yourusername/wisenet.git 
   cd wisenet
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables
   Create a `.env` file in the project root directory and configure the LLM API Key and database connections:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```
4. Start the backend service
   ```bash
   uvicorn main:app --reload
   ```
5. Start the frontend
   ```bash
   cd frontend  
   npm install  
   npm start
   ```
   The frontend service will start at http://localhost:3000.

## Usage Guide
- **Input Questions**  
  Enter your initial question of interest on the system homepage, for example:  
  "What is machine learning?"
- **Automatic Inquiry**  
  The system will automatically generate related sub-questions, such as:  
  "What are the types of machine learning?" "What is supervised learning?"
- **Knowledge Network Display**  
  View the connections between questions in the visualization panel and explore different paths.
- **Search and Query**  
  Search for specific questions in the knowledge base and view the corresponding answers and associated nodes.

## Future Plans
- Support user-defined prompt templates to improve the accuracy of generated sub-questions.
- Add functionality for deploying local LLM models to reduce API call costs.
- Provide export and sharing capabilities for domain knowledge graphs.

## Contribution and Feedback
Everyone is welcome to submit Issues and Pull Requests to help improve WiseNet!  
For questions, please contact: troy.yang2@gmail.com  
**WiseNet** —— Let questions drive knowledge and let exploration extend infinitely!

---

Regarding the GitHub link, I encountered some issues while trying to parse the webpage. This could be due to the link itself or network issues. Please check the validity of the webpage link and try again if necessary. If you have any other questions or need further assistance, feel free to ask!
