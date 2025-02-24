- [English](README.md) | [中文](README_zh.md) | [Français](README_fr.md) | [日本語](README_ja.md)

# WiseNet
## **Herramienta Inteligente para la Construcción de Bases de Conocimiento**

---

## **1. Introducción del Proyecto**

**WiseNet** es una herramienta inteligente de gestión de conocimiento impulsada por **Modelos de Lenguaje de Gran Escala (LLMs)**. Automatiza la generación de subpreguntas relacionadas y construye un **gráfico de conocimiento en red**, ofreciendo una experiencia de gestión de conocimiento **eficiente e intuitiva**. El sistema permite la **automatización completa desde la entrada de problemas hasta la construcción de la red de conocimiento**, mejorando significativamente la organización y eficiencia de recuperación del conocimiento.

### **Capacidades Principales**
- **Expansión Inteligente del Conocimiento**: Genera automáticamente subpreguntas para construir un gráfico de conocimiento claro y jerárquico.
- **Soporte Multilingüe**: Utiliza el **modelo vectorial de alta precisión SBERT** para preguntas y respuestas (Q&A) y construcción de conocimiento en múltiples idiomas.
- **Integración de Múltiples Fuentes de Datos**: Soporta **carga de documentos (txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON)** y **análisis de páginas web**, con vectorización automática del contenido.
- **Capacidades de Búsqueda Potentes**: Combina **Neo4j** y **Milvus** para una **recuperación vectorial eficiente** y **coincidencia semántica**, optimizando el descubrimiento de conocimiento.
- **Generación Aumentada por Recuperación (RAG)**: Mejora las respuestas de los LLMs recuperando conocimiento relevante de gráficos estructurados y bases de datos vectoriales, asegurando respuestas precisas y contextualmente relevantes.
- **Arquitectura Modular**: Flexible y extensible, soporta la integración de varios modelos LLM y módulos de funciones personalizadas.

WiseNet integra tecnologías de vanguardia como **Neo4j, Milvus y D3.js**, ofreciendo **soluciones inteligentes y completas de gestión de conocimiento** para industrias como **logística, bases de conocimiento de servicio al cliente y gestión de conocimiento empresarial**.

---

## **2. Características del Proyecto**

### **📌 Construcción Inteligente de Conocimiento**
- **Expansión Automatizada de la Red de Conocimiento**: Utiliza LLMs para generar subpreguntas relevantes, mejorando la completitud y usabilidad del conocimiento.
- **Almacenamiento del Gráfico de Conocimiento**: Aprovecha **Neo4j** para almacenar conocimiento estructurado, soportando relaciones jerárquicas y análisis de asociación de nodos.
- **Extracción de Entidades NLP**: Extrae automáticamente entidades clave (nombres, organizaciones, conceptos) de textos, enriqueciendo la red de conocimiento.

### **🎯 Búsqueda Eficiente y Recuperación Vectorial**
- **Búsqueda Vectorial**:
  - Solución Actual: **Índice Vectorial Neo4j HNSW**, permitiendo coincidencia semántica.
  - Solución Futura: Integración con **Milvus** para una recuperación vectorial más eficiente en consultas de conocimiento a gran escala.
- **Recuperación Semántica y Coincidencia de Asociaciones**: Combina **Neo4j + LLM** para **búsqueda semántica precisa** y **recomendaciones inteligentes**.

### **📊 Visualización y Análisis de Conocimiento**
- **Gráfico de Conocimiento con D3.js**: Ofrece visualización interactiva de la red de conocimiento, soportando **actualizaciones dinámicas, arrastre de nodos y edición de relaciones**.
- **Análisis Multidimensional**:
  - **Análisis General de la Red de Conocimiento**: Proporciona información sobre la estructura del conocimiento y nodos clave.
  - **Análisis de Nodo Individual**: Explora en profundidad puntos de conocimiento y sus relaciones.
  - **Análisis de Documentos y Páginas Web**: Descubre asociaciones personalizadas y análisis de conocimiento.

### **🌍 Soporte Multilingüe y Análisis de Documentos**
- **Capacidades Multilingües**: Utiliza el **modelo vectorial multilingüe SBERT** para Q&A y gestión de conocimiento en múltiples idiomas.
- **Análisis de Documentos y Procesamiento de Páginas Web**:
  - Soporta múltiples formatos (**txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON**).
  - Analiza y vectoriza contenido web, con **soporte futuro para seguimiento automático de actualizaciones de sitios web**.

### **🤖 Soporte LLM y Extensibilidad**
- **Soporte para LLMs Locales**: Compatible con **Ollama**, soporta modelos locales como **WizardLM2** y **Llama3**.
- **Integración de APIs LLM**: Soporta **OpenAI, Anthropic, Tongyi, Doubao, DeepSeek**, y otros LLMs principales.
- **Arquitectura Modular**: **Altamente extensible y compatible**, permitiendo la integración de nuevos modelos de IA, bases de datos y módulos de negocio.

---

## **3. Escenarios de Aplicación**

WiseNet es aplicable en diversos campos:

### 🚚 **Optimización de Logística**
- **Decisiones Inteligentes de Despacho**: Construye redes de conocimiento de logística, generando automáticamente subpreguntas para rutas óptimas y asignación de recursos.
- **Integración de Información en Tiempo Real**: Analiza y integra múltiples fuentes de datos (clima, tráfico, pedidos) para recomendaciones dinámicas.
- **Manejo de Anomalías**: Identifica rápidamente nodos problemáticos y genera soluciones para minimizar interrupciones.

### 📞 **Base de Conocimiento de Servicio al Cliente**
- **Sistema de Q&A Inteligente**: Genera automáticamente preguntas frecuentes y subpreguntas para mejorar la velocidad y precisión de las respuestas.
- **Soporte Multilingüe**: Permite Q&A en múltiples idiomas para operaciones globales.
- **Actualizaciones de Conocimiento**: Analiza documentos o contenido web para mantener la base de conocimiento actualizada.

### 🏢 **Gestión de Conocimiento Empresarial**
- **Acumulación y Compartición de Conocimiento**: Convierte documentos internos en redes de conocimiento estructuradas para fácil acceso.
- **Búsqueda Inteligente y Recomendaciones**: Usa búsqueda semántica para localizar y recomendar contenido relevante.
- **Análisis de Conocimiento**: Identifica nodos clave y brechas para optimizar estrategias de gestión.

### 🏭 **Manufactura e Industria**
- **Mantenimiento Predictivo**: Predice fallas basándose en datos históricos y registros de mantenimiento.
- **Optimización de la Cadena de Suministro**: Construye redes de conocimiento para mejorar la gestión de inventario y la planificación de producción.
- **Gestión de Calidad**: Analiza datos de producción para identificar problemas de calidad y mejorar tasas de aprobación.

### ⚖️ **Legal y Cumplimiento**
- **Análisis de Documentos Legales**: Construye gráficos de conocimiento regulatorio para mejorar la investigación legal.
- **Análisis de Casos y Razonamiento**: Proporciona recomendaciones basadas en precedentes legales.
- **Revisión Automatizada de Contratos**: Identifica riesgos en cláusulas y sugiere modificaciones para mejorar la eficiencia.

---

## **4. Arquitectura del Sistema**

```
+--------------------------------------------------------+
|               Interfaz de Usuario (Frontend)            |
|         - Entrada de Consultas        - UI del Gráfico  |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                 Motor de Q&A y Expansión (Backend)   |
|   - Llamadas a LLM        - Generación de Subpreguntas |
|   - Gestión de Almacenamiento - Recuperación de Conocimiento |
|   - Extracción de Entidades - Análisis de Documentos  |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                   Capa de Almacenamiento             |
|   - Base de Datos de Grafos (Neo4j) - Conocimiento Estructurado |
|   - Búsqueda Vectorial (Neo4j) - Solución Actual     |
|   - Base de Datos Vectorial (Milvus) - Expansión Futura |
+--------------------------------------------------------+
```

## **Conceptos Básicos**
### **Base de Conocimiento**
Un conjunto de conocimiento relacionado con un dominio específico, como **logística** o **servicio al cliente**.

### **Tema de la Base**
Diferentes temas dentro de una base, cada uno representando una red de conocimiento independiente.

### **Nodos**
Unidades centrales de la red:
- **Nodo General**:
  - **ROOT**: Nodo raíz de la base.
  - **SUBJECT**: Nodo raíz de un tema.
  - **QUESTION**: Nodo de pregunta generado por IA.
  - **PROMPT**: Nodo de pregunta o pista.
  - **INFO**: Nodo de información generado por IA (texto, documentos, URL).
  - **HUMAN**: Nodo creado manualmente.

### **Relaciones**
- **HAS_CHILD**: Relación padre-hijo.
- **RELATED_TO**: Enlace entre nodos.

## **Estructura de la Base de Datos**
### **Base de Datos Relacional (PostgreSQL)**
- **Tabla de Base de Conocimiento**: Almacena información básica.
- **Tabla de Temas**: Almacena diferentes temas.
- **Tabla de Usuarios**: Gestiona datos de usuarios para aislamiento multi-usuario.

### **Base de Datos de Grafos (Neo4j)**
- **Nodos**: Cada nodo tiene **lib_id** y **subject_id** para aislamiento.
- **Relaciones**: Define jerarquías y asociaciones.
- **Almacenamiento Vectorial**:
  - **Embedding de Texto**: Cada nodo de texto tiene un atributo `embedding`.
  - **Índice HNSW de Neo4j**: Permite búsqueda eficiente de similitud.

### **Milvus (Futura Base de Datos Vectorial)**
- Almacenará embeddings para mejorar la eficiencia de búsqueda.

### **Descripción de la Estructura**
#### **Base de Datos Relacional (PostgreSQL)**
- **Base de Conocimiento**: Almacena información básica.
- **Temas**: Almacena información por tema.
- **Usuarios**: Gestiona datos de usuarios para aislamiento.

#### **Base de Datos de Grafos (Neo4j)**
- **Nodos**:
  - **ROOT**, **SUBJECT**, **QUESTION**, **PROMPT**, **INFO**, **HUMAN**.
  - Nodos auxiliares (**Entidad**, **Palabra Clave**, **Etiqueta**, etc.) accesibles en propiedades.
- **Relaciones**: HAS_CHILD y RELATED_TO con **lib_id** y **subject_id**.
- **Almacenamiento Vectorial**: Embeddings almacenados en Neo4j con índice HNSW.

---

## **5. Guía de Contribución**
### **Cómo Contribuir**
1. Haz un fork del repositorio.
2. Clona localmente:
   ```bash
   git clone https://github.com/troyyang/WiseNet.git
   ```
3. Crea una rama:
   ```bash
   git checkout -b feature/tu-funcionalidad
   ```
4. Haz commit y push:
   ```bash
   git commit -m "Añadir nueva funcionalidad"
   git push origin feature/tu-funcionalidad
   ```
5. Envía un pull request y espera la revisión.

---

## **6. Despliegue**

### **6.1 Despliegue Local (Usando Poetry)**

#### **Guía por OS**

##### **Windows**
1. Instala [Python](https://www.python.org/downloads/) (agrega al PATH).
2. Instala [Poetry](https://python-poetry.org/docs/#installation).
3. Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### **macOS/Linux**
1. Instala Python via Homebrew o gestor de paquetes.
2. Instala Poetry siguiendo la [documentación oficial](https://python-poetry.org/docs/#installation).
3. Instala Docker y Docker Compose.

### **Clona el Repositorio**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Configura el Entorno Virtual**
```bash
cp .env.example .env
```
Modifica el archivo `.env` según tus necesidades.

### **Inicia los Servicios**
Asegúrate de que Docker esté en ejecución.
```bash
docker compose -f docker-compose-base.yml up -d
```
Para usar GPU con modelos locales:
```bash
docker compose -f docker-compose-base-gpu.yml up -d
```

#### **Verifica Neo4j**
```bash
docker logs neo4j
```
Espera la salida:
```
2025-02-10 02:52:59.873+0000 INFO  Remote interface available at http://localhost:7474/
2025-02-10 02:52:59.875+0000 INFO  Started.
```
En el primer inicio, se instalarán plugins. Espera a que termine.

#### **Verifica Ollama**
```bash
docker logs ollama
```
Asegúrate de que los modelos estén descargados. Si no:
```bash
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull wizardlm2
```

#### **Ejecuta el Backend FastAPI**
Instala Python 3.10.12 y pip.

Accede a la carpeta `app`:
```bash
cd app
```
Instala Poetry:
```bash
pip install poetry
```
Activa el entorno:
```bash
poetry shell
```
Instala dependencias:
```bash
poetry install
```
Instala Babel:
```bash
pip install Babel
```
Compila las traducciones:
```bash
pybabel compile -d translations
```
Ejecuta el backend:
```bash
python main.py
```

#### **Inicia el Frontend**
Instala Node.js v18.0.0 y npm v8.6.0.

Accede a la carpeta `frontend`:
```bash
cd frontend
npm install
npm run dev
```

### **6.2 Despliegue con Docker**

#### **Clona el Repositorio**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Configura el Entorno**
```bash
cp .env.example .env
```
Modifica `.env`, especialmente `FRONTEND_API_BASE_URL='http://tu-dominio:8088'`.

### **Ejecuta install.sh**
```bash
./install.sh
```

Accede a [http://localhost:3000/](http://localhost:3000/). Un script `.bat` está disponible para Windows.

---

## **7. Planes Futuros**
- **Integrar LLMs locales**: Mejorar capacidades de despliegue privado y soportar más modelos.
- **Mejorar la interacción visual del gráfico**: Soporte para actualizaciones dinámicas, arrastre de nodos, edición de relaciones, etc.
- **Transición a Milvus**: Búsqueda vectorial más eficiente para bases de conocimiento a gran escala.
- **API RESTful y WebSocket**: Facilitar integración con otros sistemas.
- **Soporte multi-usuario**: Acceso concurrente y gestión de permisos.
- **Control de versiones**: Gestión de versiones y rollback de la base.
- **Actualizaciones en tiempo real**: Sincronización automática de contenido web.
- **Soporte multimodal**: Imágenes, audio, etc.
- **Mejoras analíticas**: Herramientas de IA para predicción y razonamiento.

---

## **8. Licencia**  
Este proyecto está bajo la licencia **GPL-3.0**, permitiendo uso y modificación libres.  

---

## **9. Apéndice**  

### **Preguntas Frecuentes (FAQ)**  
- **¿Cómo mejorar la velocidad de construcción de la red?**  
  - Aumenta el paralelismo, optimiza llamadas a LLM y usa algoritmos de búsqueda vectorial más eficientes.  
- **¿Cómo extender las funcionalidades?**  
  - Añade módulos o plugins a través de la arquitectura modular.  

### **Recursos Relacionados**  
- [Documentación de Neo4j](https://neo4j.com/docs/)  
- [Documentación de Milvus](https://milvus.io/docs/)  
- [Documentación de D3.js](https://d3js.org/)  
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)  
- [Documentación de Arco Design Vue](https://arco.design/vue/)

### **Contacto**  
Para preguntas o sugerencias: [troy.yang2@gmail.com](mailto:troy.yang2@gmail.com).  

---