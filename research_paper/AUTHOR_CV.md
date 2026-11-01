# Curriculum Vitae (Academic CV) & Author Biographies
## For Springer Research Paper Submission

**Paper Title:** *Multiplayer AI Coding Agent with Persistent Project Memory: Architecture, Concurrency Control, and Dual-Tier Knowledge Retention*  
**Affiliation:** Department of Computer Science and Design, Rajalakshmi Engineering College, Chennai, Tamil Nadu, India  

---

## 1. Primary Author & Lead Researcher CV

### **Muhilan S**
- **Affiliation:** Department of Computer Science and Design, Rajalakshmi Engineering College
- **Address:** Rajalakshmi Nagar, Thandalam, Chennai, Tamil Nadu 602105, India
- **Institutional Email:** `muhilan.s.2024.csd@rajalakshmi.edu.in`
- **Research Interests:** Collaborative Software Engineering, Autonomous LLM Coding Agents, Real-Time Distributed Systems, Concurrency Control Protocols, Human-AI Pair Programming.

#### **Academic Background**
- **Bachelor of Engineering / Technology in Computer Science and Design**  
  *Rajalakshmi Engineering College (Affiliated to Anna University), Chennai, India*  
  - Focus Areas: Software Engineering, Distributed Systems, Artificial Intelligence, Database Management Systems, Object-Oriented Design.

#### **Research Contributions & Projects**
- **Lead Architect & Developer – Summit (Multiplayer AI Coding Agent Workspace):**
  - Architected a full-duplex WebSocket presence and event normalization bus (`AppEvent`) coordinating multi-client shared agent streams.
  - Formulated and implemented an Optimistic Concurrency Control (OCC) file versioning protocol intercepting race conditions between autonomous agent writes and distributed human developers.
  - Engineered prompt budgeting and relevance scoring pipelines for dynamic LLM context injection.
  - Designed an offline-first deterministic fallback engine ensuring zero-downtime execution under network or API constraints.
- **Automated Validation Suite:**
  - Implemented 23 comprehensive automated integration and unit test suites covering sandboxed path traversal security, REST API integrity, and concurrency conflict interception.

#### **Technical Proficiencies**
- **Languages:** Python (FastAPI, Asyncio, SQLAlchemy), TypeScript, JavaScript, SQL, C/C++.
- **Frameworks & Libraries:** React 18, Vite, LiteLLM, ChromaDB, PyMuPDF, Pytest, Monaco Editor.
- **Protocols & Systems:** WebSockets, Optimistic Concurrency Control (OCC), RESTful APIs, Git Porcelain API, ChromaDB Vector Stores, SQLite.

---

## 2. Co-Author CV

### **Dhanesh SK**
- **Affiliation:** Department of Computer Science and Design, Rajalakshmi Engineering College
- **Address:** Rajalakshmi Nagar, Thandalam, Chennai, Tamil Nadu 602105, India
- **Institutional Email:** `dhanesh.sk.2024.csd@rajalakshmi.edu.in`
- **Research Interests:** Information Retrieval, Semantic Vector Embeddings, Knowledge Retention in Large Language Models, Software Testing and Quality Assurance.

#### **Academic Background**
- **Bachelor of Engineering / Technology in Computer Science and Design**  
  *Rajalakshmi Engineering College (Affiliated to Anna University), Chennai, India*  
  - Focus Areas: Information Retrieval, Natural Language Processing, Data Structures & Algorithms, Computer Networks.

#### **Research Contributions & Projects**
- **Co-Researcher – Summit Project:**
  - Co-designed the dual-tier persistent project memory architecture coupling SQLite relational tables with a local ChromaDB vector store.
  - Formulated a 384-dimensional subword hash projection embedding model (`LocalEmbeddingFunction`) operating offline without GPU dependencies.
  - Implemented cosine-distance semantic deduplication routines ($\delta < 0.10$) preventing redundant memory item creation.
  - Conducted experimental performance evaluations, empirical test categorization, and multi-tenant isolation validation.

#### **Technical Proficiencies**
- **Languages:** Python, TypeScript, SQL, HTML5/CSS3.
- **Frameworks & Tools:** ChromaDB, NumPy, LiteLLM, Pytest, Git, FastEmbed/HNSW Graph Indexing.
- **Domain Specializations:** Vector Similarity Search, Semantic Deduplication, Test-Driven Development (TDD).

---

## 3. Corresponding Author / Faculty Supervisor CV

### **Revathy P**
- **Affiliation:** Department of Computer Science and Design, Rajalakshmi Engineering College
- **Address:** Rajalakshmi Nagar, Thandalam, Chennai, Tamil Nadu 602105, India
- **Institutional Email:** `revathy.p@rajalakshmi.edu.in`
- **Role:** Faculty Mentor / Academic Supervisor / Corresponding Author
- **Research Interests:** Software Engineering Methodologies, Artificial Intelligence in Education and Development, Distributed Database Systems, Collaborative Computing.

#### **Academic Background & Professional Appointments**
- **Faculty Member / Assistant Professor**, Department of Computer Science and Design, Rajalakshmi Engineering College, Chennai, India.
- **Postgraduate & Doctoral Specialization** in Computer Science and Engineering / Software Systems.

#### **Research Supervision & Academic Leadership**
- Guided undergraduate and postgraduate research projects in applied artificial intelligence, automated software engineering, and distributed systems.
- Supervised the design, methodology formulation, threat modeling, and empirical verification of the **Summit** multiplayer AI coding agent framework.
- Evaluated architectural tradeoffs between character-level Operational Transformation (OT)/CRDTs and transaction-level Optimistic Concurrency Control (OCC).

#### **Professional Memberships & Scholarly Activities**
- Active contributor to academic curricula in modern software architecture, cloud platforms, and AI-assisted engineering.
- Peer reviewer and mentor for engineering conferences and publications.

---

## 4. Springer Author Biographies (Bio-sketches for Publication)

*(These concise 80–120 word biographical sketches conform directly to Springer Nature / LNCS manuscript submission guidelines)*

> **Muhilan S** is an undergraduate researcher in the Department of Computer Science and Design at Rajalakshmi Engineering College, Chennai, India. His primary research interests encompass collaborative software engineering, autonomous large language model (LLM) agents, and distributed real-time systems. He is the lead developer of the Summit collaborative AI coding environment, with a strong focus on concurrency control protocols and context management for multi-user software development.

> **Dhanesh SK** is an undergraduate researcher in the Department of Computer Science and Design at Rajalakshmi Engineering College, Chennai, India. His research focuses on semantic information retrieval, offline vector embeddings, and retrieval-augmented generation (RAG) architectures. He contributed significantly to the persistent memory lifecycle and offline semantic deduplication mechanisms within the Summit project.

> **Revathy P** is a faculty member in the Department of Computer Science and Design at Rajalakshmi Engineering College, Chennai, India. Her academic and research specializations include advanced software engineering, distributed computing, database systems, and artificial intelligence. She has supervised numerous student research initiatives in intelligent system design and software verification.

---

## 5. Springer Manuscript Submission Cover Letter

**To:** The Editor-in-Chief / Editorial Board  
**Journal / Series:** Springer Nature / Lecture Notes in Computer Science (LNCS) / SN Computer Science  
**Subject:** Submission of Original Research Article titled *"Multiplayer AI Coding Agent with Persistent Project Memory: Architecture, Concurrency Control, and Dual-Tier Knowledge Retention"*  

Dear Editor,

We are pleased to submit our original research manuscript titled **"Multiplayer AI Coding Agent with Persistent Project Memory: Architecture, Concurrency Control, and Dual-Tier Knowledge Retention"** for consideration in your esteemed Springer publication.

### Background and Research Highlights
Most contemporary AI coding assistants (e.g., GitHub Copilot, Cursor, OpenHands) are restricted to single-user, solitary sessions. When software engineering teams collaborate on a shared codebase, existing developer tools segregate interactions into isolated chat threads—failing to persist architectural decisions across sessions and inviting catastrophic file overwrite conflicts during concurrent human and autonomous agent edits.

To address these challenges, our manuscript presents **Summit**, a real-time multiplayer AI coding agent workspace featuring:
1. **Full-Duplex Multiplayer Event Bus:** A centralized WebSocket presence and event normalization gateway that broadcasts agent reasoning tokens, tool invocations, and workspace file alterations in real time.
2. **Optimistic Concurrency Control (OCC):** A monotonic versioning protocol that detects concurrent write conflicts between developers and autonomous agent tools, providing visual side-by-side resolution.
3. **Dual-Tier Persistent Memory Engine:** A hybrid storage engine combining an ACID-compliant relational database (SQLite) with an offline local vector store (ChromaDB) powered by a 384-dimensional subword hash projection embedding model ($\delta < 0.10$).
4. **Intelligent Context Budgeting:** A relevance-scoring algorithm that selectively injects architectural memory and prioritized code files into LLM context windows under strict token budgets.
5. **Empirical Verification:** Comprehensive evaluation over 23 automated unit and integration tests confirming deterministic path-traversal sandboxing, concurrency conflict handling, and semantic deduplication.

### Declarations
- This manuscript represents original work that has not been published previously and is not currently under consideration for publication elsewhere.
- All authors have reviewed and approved the manuscript and agree with its submission.
- There are no competing financial or non-financial interests to declare.
- Ethical guidelines and institutional computational support have been duly acknowledged.

Thank you very much for your time and consideration of our manuscript.

Sincerely,

**Muhilan S** (Primary Author)  
Email: `muhilan.s.2024.csd@rajalakshmi.edu.in`  

**Dhanesh SK** (Co-Author)  
Email: `dhanesh.sk.2024.csd@rajalakshmi.edu.in`  

**Revathy P** (Corresponding Author / Faculty Supervisor)  
Email: `revathy.p@rajalakshmi.edu.in`  
Department of Computer Science and Design  
Rajalakshmi Engineering College, Chennai, Tamil Nadu, India  
