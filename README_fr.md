- [English](README.md) | [中文](README_zh.md) | [Española](README_es.md) | [日本語](README_ja.md)

# WiseNet
# **Outil Intelligent de Construction de Base de Connaissances**

---

## **1. Introduction du Projet**

**WiseNet** est un outil intelligent de gestion des connaissances basé sur des **modèles de langage de grande taille (LLMs)**. Il automatise la génération de sous-questions liées et construit un **graphe de connaissances en réseau**, offrant une expérience de gestion des connaissances **efficace et intuitive**. Le système permet une **automatisation complète de la saisie des problèmes à la construction du réseau de connaissances**, améliorant significativement l'organisation et l'efficacité de la récupération des connaissances.

### **Fonctionnalités Clés**
- **Expansion Intelligente des Connaissances** : Génère automatiquement des sous-questions pour construire un graphe de connaissances hiérarchique et clair.
- **Support Multilingue** : Utilise le **modèle vectoriel multilingue SBERT** pour des Q&A et une construction de connaissances translinguistiques.
- **Intégration de Sources Multiples** : Prend en charge **l’import de documents (txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON)** et **l’analyse de pages web**, avec vectorisation automatique du contenu.
- **Recherche Puissante** : Combine **Neo4j** et **Milvus** pour une **recherche vectorielle efficace** et un **appariement sémantique**, optimisant la découverte de connaissances.
- **Génération Augmentée par Récupération (RAG)** : Améliore les réponses des LLMs en récupérant des connaissances pertinentes à partir de graphes structurés et de bases de données vectorielles, assurant des réponses précises et contextuelles.
- **Architecture Modulaire** : Flexible et extensible, permettant l’intégration de divers modèles LLM et de modules personnalisés.

WiseNet intègre des technologies de pointe comme **Neo4j, Milvus et D3.js**, offrant des **solutions intelligentes et complètes de gestion des connaissances** pour des secteurs tels que **la logistique, les bases de connaissances client, et la gestion des connaissances d’entreprise**.

---

## **2. Caractéristiques du Projet**

### **📌 Construction Intelligente de Connaissances**
- **Expansion Automatisée du Réseau** : Utilise des LLMs pour générer des sous-questions pertinentes, améliorant la complétude des connaissances.
- **Stockage du Graphe de Connaissances** : Exploite **Neo4j** pour stocker les connaissances de manière structurée, supportant les relations hiérarchiques et l’analyse des associations.
- **Extraction d’Entités NLP** : Extrait automatiquement les entités clés (noms, organisations, concepts) des textes, enrichissant le réseau de connaissances.

### **🎯 Recherche Efficace & Vectorisation**
- **Recherche Vectorielle** :
  - Solution Actuelle : **Index Vectoriel Neo4j HNSW**, permettant un appariement sémantique.
  - Solution Future : Intégration de **Milvus** pour une recherche vectorielle plus efficace à grande échelle.
- **Recherche Sémantique & Recommandations** : Combine **Neo4j + LLM** pour une **recherche précise** et des **recommandations intelligentes**.

### **📊 Visualisation & Analyse**
- **Graphe de Connaissances avec D3.js** : Offre une visualisation interactive du réseau, supportant **mises à jour dynamiques, déplacement des nœuds et édition des relations**.
- **Analyse Multidimensionnelle** :
  - **Analyse Globale** : Aperçu de la structure du réseau et des nœuds clés.
  - **Analyse par Nœud** : Exploration approfondie des points de connaissances et de leurs relations.
  - **Analyse de Documents/Pages Web** : Découverte personnalisée d’associations et d’analyses.

### **🌍 Support Multilingue & Analyse de Documents**
- **Multilinguisme** : Utilise le **modèle vectoriel SBERT multilingue** pour des Q&A translinguistiques.
- **Analyse de Documents & Pages Web** :
  - Supporte plusieurs formats (**txt, markdown, Word, Excel, PPT, CSV, PDF, HTML, XML, JSON**).
  - Analyse et vectorise le contenu web, avec un **support futur pour le suivi automatique des mises à jour de sites web**.

### **🤖 Support LLM & Extensibilité**
- **LLMs Locaux** : Compatible avec **Ollama**, supportant des modèles comme **WizardLM2** et **Llama3**.
- **Intégration d’APIs LLM** : Supporte **OpenAI, Anthropic, Tongyi, Doubao, DeepSeek**, et d’autres LLMs populaires.
- **Architecture Modulaire** : **Extensible et compatible**, permettant l’ajout de nouveaux modèles, bases de données et modules métiers.

---

## **3. Scénarios d’Application**

WiseNet s’applique à divers domaines :

### 🚚 **Optimisation Logistique**
- **Décisions Intelligentes** : Construit des réseaux de connaissances logistiques, générant des itinéraires optimaux et des allocations de ressources.
- **Intégration en Temps Réel** : Analyse et intègre des données multiples (météo, trafic, commandes) pour des recommandations dynamiques.
- **Gestion des Anomalies** : Identifie rapidement les problèmes et génère des solutions pour minimiser les perturbations.

### 📞 **Base de Connaissances Client**
- **Q&A Intelligent** : Génère des FAQ et sous-questions pour améliorer la rapidité et la précision des réponses.
- **Support Multilingue** : Permet des Q&A multilingues pour les opérations globales.
- **Mises à Jour Automatiques** : Analyse les nouveaux documents ou pages web pour maintenir la base à jour.

### 🏢 **Gestion des Connaissances d’Entreprise**
- **Partage de Connaissances** : Convertit des documents internes en réseaux structurés pour un accès facile.
- **Recherche Intelligente** : Utilise la recherche sémantique pour localiser et recommander du contenu pertinent.
- **Analyse des Connaissances** : Identifie les points clés et les lacunes pour optimiser les stratégies.

### 🏭 **Industrie & Fabrication**
- **Maintenance Prédictive** : Prédit les pannes et optimise les calendriers de maintenance.
- **Optimisation de la Chaîne d’Approvisionnement** : Améliore la gestion des stocks et la planification.
- **Contrôle Qualité** : Analyse les données de production pour améliorer la qualité.

### ⚖️ **Juridique & Conformité**
- **Analyse de Documents Juridiques** : Construit des graphes de réglementations pour améliorer la recherche juridique.
- **Recommandations Intelligentes** : S’appuie sur des précédents légaux pour des conseils pertinents.
- **Révision Automatisée de Contrats** : Identifie les risques et suggère des modifications.

---

## **4. Architecture du Système**

```
+--------------------------------------------------------+
|               Interface Utilisateur (Frontend)          |
|         - Saisie de requêtes        - UI du graphe      |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                 Moteur Q&A et Expansion (Backend)    |
|   - Appels LLM           - Génération de sous-questions |
|   - Gestion des données  - Récupération des connaissances |
|   - Extraction d’entités - Analyse de documents       |
+------------------------+------------------------------+
                         |
+------------------------v------------------------------+
|                   Couche de Stockage                 |
|   - Base de graphes (Neo4j) - Connaissances structurées |
|   - Recherche vectorielle (Neo4j) - Solution actuelle  |
|   - Base vectorielle (Milvus) - Extension future      |
+--------------------------------------------------------+
```

## **Concepts de Base**
### **Base de Connaissances**
Un ensemble de connaissances liées à un domaine, comme **la logistique** ou **le support client**.

### **Thème de la Base**
Sujets distincts au sein d’une base, chacun représentant un réseau indépendant.

### **Nœuds**
Unités centrales du réseau :
- **Nœud Général** :
  - **ROOT** : Nœud racine de la base.
  - **SUBJECT** : Nœud racine d’un thème.
  - **QUESTION** : Nœud de question généré par l’IA.
  - **PROMPT** : Nœud de question ou d’indice.
  - **INFO** : Nœud d’information généré par l’IA (texte, documents, URL).
  - **HUMAN** : Nœud créé manuellement.

### **Relations**
- **HAS_CHILD** : Relation parent-enfant.
- **RELATED_TO** : Lien entre nœuds.

## **Structure des Bases de Données**
### **Base Relationnelle (PostgreSQL)**
- **Table Base de Connaissances** : Stocke les informations de base.
- **Table Thèmes** : Stocke les différents thèmes.
- **Table Utilisateurs** : Gère l’isolation multi-utilisateurs.

### **Base de Graphes (Neo4j)**
- **Nœuds** : Chaque nœud a **lib_id** et **subject_id** pour l’isolation.
- **Relations** : Définissent les hiérarchies et associations.
- **Stockage Vectoriel** :
  - **Embedding de texte** : Chaque nœud texte a un attribut `embedding`.
  - **Index HNSW Neo4j** : Permet une recherche de similarité efficace.

### **Milvus (Future Base Vectorielle)**
- Stockera les embeddings pour améliorer l’efficacité de la recherche.

### **Description des Bases**
#### **Base Relationnelle (PostgreSQL)**
- **Base de Connaissances** : Informations de base.
- **Thèmes** : Informations par thème.
- **Utilisateurs** : Isolation des données utilisateurs.

#### **Base de Graphes (Neo4j)**
- **Nœuds** :
  - **ROOT**, **SUBJECT**, **QUESTION**, **PROMPT**, **INFO**, **HUMAN**.
  - Nœuds auxiliaires (**Entité**, **Mot-clé**, **Tag**, etc.) accessibles via les propriétés.
- **Relations** : HAS_CHILD et RELATED_TO avec **lib_id** et **subject_id**.
- **Vectorisation** : Embeddings stockés dans Neo4j avec index HNSW.

---

## **5. Guide de Contribution**
### **Comment Contribuer**
1. Forkez le dépôt.
2. Clonez localement :
   ```bash
   git clone https://github.com/troyyang/WiseNet.git
   ```
3. Créez une branche :
   ```bash
   git checkout -b feature/votre-fonctionnalité
   ```
4. Commitez et poussez :
   ```bash
   git commit -m "Ajouter une fonctionnalité"
   git push origin feature/votre-fonctionnalité
   ```
5. Soumettez une pull request et attendez la revue.

---

## **6. Déploiement**

### **6.1 Déploiement Local (avec Poetry)**

#### **Guide par OS**

##### **Windows**
1. Installez [Python](https://www.python.org/downloads/) (ajoutez-le au PATH).
2. Installez [Poetry](https://python-poetry.org/docs/#installation).
3. Installez [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### **macOS/Linux**
1. Installez Python via Homebrew ou le gestionnaire de paquets.
2. Installez Poetry via la [documentation officielle](https://python-poetry.org/docs/#installation).
3. Installez Docker et Docker Compose.

### **Cloner le Dépôt**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Configurer l’Environnement Virtuel**
```bash
cp .env.example .env
```
Modifiez le fichier `.env` selon vos besoins.

### **Démarrer les Services**
Assurez-vous que Docker est en cours d’exécution.
```bash
docker compose -f docker-compose-base.yml up -d
```
Pour utiliser le GPU avec un modèle local :
```bash
docker compose -f docker-compose-base-gpu.yml up -d
```

#### **Vérifier Neo4j**
```bash
docker logs neo4j
```
Attendez la sortie :
```
2025-02-10 02:52:59.873+0000 INFO  Remote interface available at http://localhost:7474/
2025-02-10 02:52:59.875+0000 INFO  Started.
```
Lors du premier démarrage, les plugins seront installés. Patientez.

#### **Vérifier Ollama**
```bash
docker logs ollama
```
Assurez-vous que les modèles sont téléchargés. Sinon :
```bash
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull wizardlm2
```

#### **Lancer le Backend FastAPI**
Installez Python 3.10.12 et pip.

Accédez au dossier `app` :
```bash
cd app
```
Installez Poetry :
```bash
pip install poetry
```
Activez l’environnement :
```bash
poetry shell
```
Installez les dépendances :
```bash
poetry install
```
Installez Babel :
```bash
pip install Babel
```
Compilez les traductions :
```bash
pybabel compile -d translations
```
Lancez le backend :
```bash
python main.py
```

#### **Démarrer le Frontend**
Installez Node.js v18.0.0 et npm v8.6.0.

Accédez au dossier `frontend` :
```bash
cd frontend
npm install
npm run dev
```

### **6.2 Déploiement via Docker**

#### **Cloner le Dépôt**
```bash
git clone https://github.com/troyyang/WiseNet.git
cd WiseNet
```

### **Configurer l’Environnement**
```bash
cp .env.example .env
```
Modifiez `.env`, notamment `FRONTEND_API_BASE_URL='http://votre-domaine:8088'`.

### **Exécuter install.sh**
```bash
./install.sh
```

Accédez à [http://localhost:3000/](http://localhost:3000/). Un script `.bat` est disponible pour Windows.

---

## **7. Plans Futurs**
- **Intégrer des LLMs locaux** : Améliorer le déploiement privé et supporter plus de modèles.
- **Améliorer la visualisation du graphe** : Mises à jour dynamiques, édition des relations, etc.
- **Transition vers Milvus** : Recherche vectorielle plus efficace à grande échelle.
- **API RESTful et WebSocket** : Faciliter l’intégration avec d’autres systèmes.
- **Support Multi-utilisateurs** : Accès concurrent et gestion des permissions.
- **Contrôle de Version** : Gestion des versions et rollback de la base.
- **Mises à Jour en Temps Réel** : Synchronisation automatique des contenus web.
- **Support Multimodal** : Images, audio, etc.
- **Analyses Avancées** : Outils d’IA pour la prédiction et le raisonnement.

---

## **8. Licence**  
Ce projet est sous licence **GPL-3.0**, permettant une utilisation et modification libres.  

---

## **9. Annexes**  

### **FAQ**  
- **Comment accélérer la construction du réseau ?**  
  - Augmentez le parallélisme, optimisez les appels LLM, et utilisez des algorithmes de recherche vectorielle efficaces.  
- **Comment étendre les fonctionnalités ?**  
  - Ajoutez des modules ou plugins via l’architecture modulaire.  

### **Ressources Utiles**  
- [Documentation de Neo4j](https://neo4j.com/docs/)  
- [Documentation de Milvus](https://milvus.io/docs/)  
- [Documentation de D3.js](https://d3js.org/)  
- [Documentation de FastAPI](https://fastapi.tiangolo.com/)  
- [Documentation d’Arco Design Vue](https://arco.design/vue/)

### **Contact**  
Pour des questions ou suggestions : [troy.yang2@gmail.com](mailto:troy.yang2@gmail.com).  

---