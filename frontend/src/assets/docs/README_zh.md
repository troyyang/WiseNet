# WiseNet
## **智能知识库构建工具**

---

## **1. 项目介绍**

**WiseNet** 是一款基于**大语言模型（LLMs）**的智能知识管理工具。它能够自动生成相关子问题并构建**网络化知识图谱**，提供**高效且直观**的知识管理体验。该系统实现了**从问题输入到知识网络构建的全流程自动化**，显著提升了知识组织和检索效率。

### **核心功能**
- **智能知识扩展**：自动生成子问题，构建清晰、层次化的知识图谱。
- **多语言支持**：使用**SBERT高精度向量模型**，支持跨语言问答和知识构建。
- **多数据源整合**：支持**文档上传（txt、markdown、Word、Excel、PPT、CSV、PDF、HTML、XML、JSON）**和**网页解析**，并自动进行内容向量化。
- **强大的搜索能力**：结合**Neo4j**和**Milvus**，实现**高效向量检索**和**语义匹配**，优化知识发现。
- **检索增强生成 (RAG)**：通过从结构化图和矢量数据库中检索相关知识来增强 LLM 响应，确保答案准确且与上下文相关。
- **模块化架构**：灵活且可扩展，支持集成多种LLM模型和自定义功能模块。

WiseNet集成了**Neo4j、Milvus、D3.js**等前沿技术，为**物流调度、客服知识库、企业知识管理**等行业提供**智能化、一站式知识管理解决方案**。

---

## **2. 项目特点**

### **📌 智能知识构建**
- **自动知识网络扩展**：利用LLM生成相关子问题，提升知识的完整性和可用性。
- **知识图谱存储**：使用**Neo4j**进行结构化知识存储，支持层次关系和节点关联分析。
- **NLP实体提取**：自动从文本中提取关键实体（如人名、组织、概念），丰富知识网络。

### **🎯 高效搜索与向量检索**
- **向量搜索**：
  - 当前方案：**Neo4j HNSW向量索引**，支持语义级别的相似度匹配。
  - 未来方案：集成**Milvus**，提升大规模知识查询的向量检索效率。
- **语义检索与关联匹配**：结合**Neo4j + LLM**，实现**精准语义搜索**和**智能推荐**。

### **📊 可视化与知识分析**
- **D3.js知识图谱**：提供交互式知识网络可视化，支持**动态更新、节点拖拽和关系编辑**。
- **多维度分析**：
  - **整体知识网络分析**：洞察知识结构和关键节点。
  - **单节点分析**：深入分析知识点及其关联关系。
  - **文档与网页单点分析**：个性化知识分析与关联发现。

### **🌍 多语言支持与文档解析**
- **多语言能力**：使用**SBERT多语言向量模型**，支持跨语言问答和知识管理。
- **文档解析与网页处理**：
  - 支持多种格式（**txt、markdown、Word、Excel、PPT、CSV、PDF、HTML、XML、JSON**）。
  - 解析并向量化网页内容，**未来支持自动网站更新跟踪**，保持知识库实时更新。

### **🤖 LLM支持与扩展性**
- **本地LLM支持**：兼容**Ollama**，支持**WizardLM2**和**Llama3**等本地LLM。
- **API LLM集成**：支持**OpenAI、Anthropic、通义、豆包、DeepSeek**等主流LLM。
- **模块化架构**：**高度可扩展和兼容**，允许集成新的AI模型、数据库和业务模块，适用于多种应用场景。

---

## **3. 应用场景**

WiseNet的智能知识管理能力适用于多个领域：

### 🚚 **物流调度优化**
- **智能调度决策**：构建物流调度知识网络，自动生成最优路径和资源分配子问题。
- **实时信息整合**：支持多数据源（如天气、交通、订单）的自动解析与整合，提供动态调度建议。
- **异常处理**：快速定位知识图谱中的问题节点并生成解决方案，减少物流中断。

### 📞 **客服知识库**
- **智能问答系统**：自动生成FAQ和子问题，构建多层次客服知识库，提升响应速度和准确性。
- **多语言支持**：支持跨语言客服问答，适用于全球化业务。
- **知识更新**：自动解析最新文档或网页内容，保持知识库实时准确。

### 🏢 **企业知识管理**
- **知识积累与共享**：将内部文档和会议记录转化为结构化知识网络，便于检索和学习。
- **智能搜索与推荐**：通过语义搜索定位相关知识并推荐相关内容。
- **知识分析**：分析企业知识网络，识别关键节点和知识缺口，优化知识管理策略。

### 🏭 **制造业与工业**
- **设备维护与故障诊断**：基于历史数据和维护记录预测故障，优化维护计划。
- **供应链优化**：构建供应链知识网络，优化库存管理和生产调度。
- **质量管理**：分析生产数据，识别质量问题，提升产品合格率。

### ⚖️ **法律与合规**
- **法律文档解析**：构建法规知识图谱，提升法律研究和合规管理效率。
- **案例分析与推理**：基于法律案例和法规提供智能建议。
- **合同审查自动化**：识别合同条款风险并建议修改，提升合同管理效率。

---

## **4. 系统架构**

```
+--------------------------------------------------------+
|                     用户界面（前端）                   |
|         - 输入查询        - 知识图谱界面               |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                 问答与扩展引擎（后端）                |
|   - LLM API调用        - 子问题生成                  |
|   - 数据存储管理       - 知识检索                    |
|   - NLP实体提取        - 文档解析                    |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                   数据存储层                         |
|   - 图数据库（Neo4j） - 结构化知识                   |
|   - 向量搜索（Neo4j） - 当前检索方案                 |
|   - 向量数据库（Milvus） - 未来扩展                  |
+--------------------------------------------------------+
```

## **基本概念**
### **知识库**
与特定领域相关的知识集合，如**物流调度**或**客服知识库**。

### **知识库主题**
知识库中的不同主题，每个主题代表一个独立的知识网络。

### **节点**
知识网络中的核心数据单元：
- **节点（通用节点）**
  - **ROOT**：知识库的根节点。
  - **SUBJECT**：主题的根节点。
  - **QUESTION**：用于检索的节点，由AI生成。
  - **PROMPT**：问题或提示节点。
  - **INFO**：AI生成的信息节点（文本、文档、网站等）。
  - **HUMAN**：手动创建的知识节点。

### **关系**
- **HAS_CHILD**：表示父子关系。
- **RELATED_TO**：表示节点之间的关联。

## **数据库结构**
### **关系数据库（PostgreSQL）**
- **知识库表**：存储知识库的基本信息。
- **知识库主题表**：存储不同主题的信息。
- **用户数据表**：管理用户数据，实现多用户隔离。

### **图数据库（Neo4j）**
- **节点**：每个节点包含**lib_id**和**subject_id**，确保数据隔离。
- **关系**：定义层次和关联关系。
- **向量存储**：
  - **文本嵌入**：每个文本节点包含`embedding`属性。
  - **Neo4j HNSW向量索引**：支持高效的相似度搜索。

### **Milvus（未来向量数据库）**
- 计划存储问答的嵌入向量，提升相似度搜索效率。

---

## **5. 贡献指南**
### **如何贡献**
1. Fork 仓库。
2. 克隆仓库到本地：
   ```bash
   git clone https://github.com/troyyang/WiseNet.git
   ```
3. 创建新分支：
   ```bash
   git checkout -b feature/your-feature
   ```
4. 提交并推送更改：
   ```bash
   git commit -m "添加新功能"
   git push origin feature/your-feature
   ```
5. 提交Pull Request并等待审核。

---

## **6. 部署**

### **6.1 本地部署（使用Poetry）**

#### **操作系统特定部署指南**

##### **Windows**
1. 安装 [Python](https://www.python.org/downloads/)（确保添加到PATH）。
2. 安装 [Poetry](https://python-poetry.org/docs/#installation)。
3. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

#### **macOS/Linux**
1. 通过Homebrew或系统包管理器安装Python。
2. 按照[官方文档](https://python-poetry.org/docs/#installation)安装Poetry。
3. 安装Docker和Docker Compose。

### **克隆仓库**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **设置虚拟环境**
```bash
cp .env.example .env
```
修改`.env`文件中的配置。

### **启动依赖服务**
确保Docker和Docker Compose已安装并运行。
```bash
docker compose -f docker-compose-base.yml up -d
```
如果是使用GPU本地模型，你可以使用:
```bash
docker compose -f docker-compose-base-gpu.yml up -d
```

#### **检查Neo4j安装**
```bash
docker logs neo4j
```
等待输出：
```
2025-02-10 02:52:59.873+0000 INFO  Remote interface available at http://localhost:7474/
2025-02-10 02:52:59.875+0000 INFO  Started.
```
如果是首次启动Neo4j Docker容器，将安装插件：
```
Installing Plugin 'graph-data-science' from https://graphdatascience.ninja/neo4j-graph-data-science-2.13.2.jar to /var/lib/neo4j/plugins/graph-data-science.jar
```
请等待安装完成。

#### **检查Ollama安装**
```bash
docker logs ollama
```
确保输出显示：
```
All models pulled successfully.
```
验证本地模型：
```bash
docker exec -it ollama ollama list
```
如果没有模型，手动拉取：
```bash
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull wizardlm2
```

#### **运行FastAPI后端**
确保已安装Python 3.10.12和pip。

进入后端目录：
```bash
cd app
```
安装Poetry：
```bash
pip install poetry
```
进入Poetry环境：
```bash
poetry shell
```
安装依赖：
```bash
poetry install
```
安装Babel:
```bash
pip install Babel
```
翻译i18n消息:
```bash
pybabel compile -d translations
```
运行FastAPI后端：
```bash
python main.py
```

#### **启动前端**
确保已安装Node.js v18.0.0和npm v8.6.0。

进入前端目录并安装依赖：
```bash
cd frontend
npm install
npm run dev
```

### **6.2 Docker部署**

#### **克隆仓库**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **设置虚拟环境**
```bash
cp .env.example .env
```
修改`.env`文件中的配置。
特别要注意修改： FRONTEND_API_BASE_URL='http://your-domain:8088'.

### **执行install.sh**
```bash
./install.sh
```

访问 [http://localhost:3000/](http://localhost:3000/) 进入前端。Windows用户也可使用`.bat`脚本。

---

## **7. 未来计划**
- **集成本地 LLM**：提高私有部署能力，支持更多本地模型。
- **增强知识图谱的可视化交互功能**：支持动态更新、节点拖拽、关系编辑等。
- **逐步过渡到 Milvus**：进行更高效的向量搜索，支持大规模知识库。
- **提供 RESTful API 与 WebSocket 支持**：方便与其他系统集成。
- **多用户支持**：支持多用户并发访问，提供用户权限管理功能。
- **知识库版本控制**：支持知识库的版本管理和回滚功能。
- **实时知识更新**：支持自动跟踪网站更新，实时同步最新内容至知识库。
- **多模态支持**：扩展至图像、音频等多模态数据，构建更丰富的知识网络。
- **增强分析能力**：引入更多 AI 分析工具（如因果推理、趋势预测），提升知识网络的洞察力。

---

## **8. 许可证**  
本项目采用**GPL-3.0**许可证，允许自由使用和修改。  

---

## **9. 附录**  

### **常见问题（FAQ）**  
- **如何提升知识网络构建速度？**  
  - 增加并行处理任务，优化LLM调用策略，使用更高效的向量搜索算法。  
- **如何扩展WiseNet功能？**  
  - WiseNet的模块化架构允许通过新模块或插件扩展功能，如集成更多LLM模型或支持新数据源。  

### **相关资源**  
- [Neo4j官方文档](https://neo4j.com/docs/)  
- [Milvus官方文档](https://milvus.io/docs/)  
- [D3.js官方文档](https://d3js.org/)  
- [FastAPI官方文档](https://fastapi.tiangolo.com/)  
- [Arco Design Vue官方文档](https://arco.design/vue/)

### **联系我们**  
如有问题或建议，请联系 [troy.yang2@gmail.com](mailto:troy.yang2@gmail.com)。  

---