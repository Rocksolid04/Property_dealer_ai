# 🏠 Property Dealer AI

An AI-powered property discovery platform built with **FastAPI, PostgreSQL, SQLAlchemy, Alembic, Qdrant, Redis, GenAI, Supabase, Apify, and Telegram**.

The project started as a property listing backend and evolved into a production-oriented system capable of understanding natural-language property requirements, retrieving relevant properties using semantic search, and generating AI-assisted responses.

The primary focus of this project is the **backend architecture, data pipeline, search/retrieval system, RAG implementation, caching, database design, migrations, and deployment**.

---

## 🚀 What Problem Does It Solve?

Traditional property websites usually require users to manually select filters such as:

* Location
* Property type
* BHK
* Budget
* Listing type
* Area

This works well for structured queries, but users naturally describe their requirements in sentences:

> "I want a 2 BHK apartment in Mumbai under ₹2 crore."

or:

> "Show me a spacious house in Thane suitable for a family."

The goal of this project was to build a system that can understand these natural-language requirements and connect them with structured property data.

The system combines:

**Structured filtering + semantic retrieval + AI reasoning + caching**

to provide more relevant property results.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      User / Client   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Flask Frontend     │
                         │      (Web UI)        │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                    ┌──────────────────────────────┐
                    │       FastAPI Backend        │
                    │                              │
                    │  REST APIs                    │
                    │  Authentication               │
                    │  Property Search              │
                    │  AI Search                    │
                    │  RAG Pipeline                 │
                    │  Caching                      │
                    └───────┬───────┬───────┬──────┘
                            │       │       │
              ┌─────────────┘       │       └─────────────┐
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │  PostgreSQL  │      │    Qdrant    │      │    Redis     │
      │              │      │              │      │              │
      │ Properties   │      │ Embeddings   │      │ Cache        │
      │ Users        │      │ Vector Search │      │ Search Cache │
      │ Images       │      │              │      │ AI Cache     │
      │ Inquiries    │      └──────────────┘      └──────────────┘
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │   Supabase   │
      │              │
      │ PostgreSQL   │
      │ Storage      │
      └──────────────┘

      External Services
      ├── Apify       → Property data ingestion
      ├── Groq        → LLM / GenAI
      └── Telegram    → Chatbot integration
```

---

# 🧰 Tech Stack

## Backend

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Alembic**
* **PostgreSQL**
* **Pydantic / Pydantic Settings**
* **JWT Authentication**
* **Redis**

## AI / Search

* **GenAI / LLM**
* **Groq**
* **RAG**
* **Sentence Transformers**
* **Qdrant**
* **Semantic Search**
* **Hybrid Search**

## Data & Infrastructure

* **Supabase PostgreSQL**
* **Supabase Storage**
* **Apify**
* **Redis**
* **Docker**
* **Railway**

## Frontend

* Flask
* HTML/CSS/Jinja templates

The frontend is intentionally lightweight. Most of the engineering work in this project is concentrated in the backend and AI/search pipeline.

---

# 📊 Data Ingestion Pipeline

One of the important parts of this project was understanding that an AI property search system is only as good as the data being retrieved.

Instead of manually inserting every property, I built a data ingestion workflow using **Apify** for collecting property information.

The general pipeline is:

```text
Property Source
      │
      ▼
    Apify
      │
      ▼
Raw Property Data
      │
      ▼
Data Cleaning / Normalization
      │
      ├── Title
      ├── Description
      ├── Location
      ├── Price
      ├── BHK
      ├── Bathrooms
      ├── Area
      ├── Property Type
      └── Listing Type
      │
      ▼
PostgreSQL
      │
      ▼
Embedding Generation
      │
      ▼
Qdrant
```

The ingestion process also required handling inconsistent real-world values.

For example, property prices can appear as:

```text
₹8 Lakh - ₹12 Lakh
8-12 LPA
₹1.2 Crore
```

These values cannot simply be stored as strings if the application needs to perform meaningful price filtering.

This forced me to think about:

* Data normalization
* Missing values
* Duplicate records
* Company/source information
* Price parsing
* Structured vs unstructured fields
* Database constraints

This was one of the first places where the project became more than a CRUD application.

---

# 🗄️ Database Design

PostgreSQL is the primary source of truth for structured application data.

The database contains entities such as:

```text
Users
  │
  ├── Favorites
  └── Inquiries

Properties
  │
  ├── Images
  ├── Owner
  └── Search metadata
```

The application uses **SQLAlchemy ORM** rather than writing raw SQL throughout the application.

This helped me understand how application models map to relational database tables.

---

# 🧱 SQLAlchemy

SQLAlchemy became one of the most important parts of the backend architecture.

Instead of directly writing database queries everywhere, the application uses SQLAlchemy models and sessions.

The backend follows the basic flow:

```text
FastAPI Route
     │
     ▼
Service Layer
     │
     ▼
SQLAlchemy ORM
     │
     ▼
PostgreSQL
```

This separation helped keep API routes focused on HTTP concerns while business logic remained in the service layer.

I also learned how:

* Sessions work
* ORM models map to tables
* Relationships are represented
* Foreign keys work
* Transactions work
* Dependency injection can provide database sessions
* Services can reuse database access logic

---

# 🔄 Alembic & Database Migrations

During development, the database schema changed multiple times.

For example:

```text
Initial Property Table
        │
        ▼
Add Users
        │
        ▼
Add Property Owner
        │
        ▼
Add Relationships
        │
        ▼
Add Cascade Behavior
        │
        ▼
Further Schema Changes
```

Instead of manually modifying the production database, I learned how to use **Alembic migrations**.

Typical workflow:

```bash
alembic revision --autogenerate -m "describe change"
```

followed by:

```bash
alembic upgrade head
```

This taught me an important backend engineering principle:

> Database schema changes should be version-controlled just like application code.

I also learned how migration history works, how revisions depend on previous revisions, and how to recover from migration inconsistencies.

---

# 🔎 Search Evolution

Search was one of the most interesting parts of this project.

I did not want to depend on a single search technique.

The backend evolved through multiple search approaches.

## 1. Structured Search

The first approach was traditional database filtering.

For example:

```text
Location = Mumbai
Bedrooms = 2
Listing Type = Buy
```

This works well when the user knows exactly what they want.

But it struggles with natural language.

---

# 🧠 2. Semantic Search

Users don't always use the exact words stored in the database.

For example:

```text
User:
"Looking for a spacious family home in Mumbai"
```

The database might contain:

```text
"Large 3 BHK residential apartment..."
```

A traditional keyword search may not understand that these descriptions are related.

To solve this, property information is converted into embeddings using a sentence-transformer model.

```text
Property Text
     │
     ▼
Embedding Model
     │
     ▼
Vector
     │
     ▼
Qdrant
```

The user query goes through the same process:

```text
User Query
     │
     ▼
Embedding Model
     │
     ▼
Query Vector
     │
     ▼
Qdrant Similarity Search
     │
     ▼
Relevant Properties
```

This introduced me to concepts such as:

* Embeddings
* Vector representations
* Similarity search
* Cosine similarity
* Vector databases
* Retrieval

---

# 🔀 3. Hybrid Search

Semantic search is powerful, but it is not perfect.

Some requirements are inherently structured:

```text
2 BHK
Mumbai
₹2 crore
For Sale
```

These are better handled using database filters.

At the same time, descriptive requirements such as:

```text
spacious
family-friendly
modern
near important areas
```

can benefit from semantic search.

This led to the idea of **hybrid retrieval**:

```text
                    User Query
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      Structured Search     Semantic Search
             │                     │
             │                  Qdrant
             │                     │
             └──────────┬──────────┘
                        ▼
                 Combined Results
                        │
                        ▼
                 Relevant Properties
```

This improved the retrieval approach because the system could use both:

**exact constraints + semantic meaning**

instead of depending entirely on either one.

---

# 🤖 RAG Implementation

The project eventually evolved into a RAG-based architecture.

RAG stands for:

> Retrieval-Augmented Generation

The basic flow is:

```text
User
 │
 │ Natural Language Query
 ▼
AI Search
 │
 ▼
Query Understanding
 │
 ▼
Retrieval
 │
 ├── Structured Search
 │
 ├── Semantic Search
 │
 └── Hybrid Search
 │
 ▼
Relevant Properties
 │
 ▼
Context
 │
 ▼
LLM
 │
 ▼
AI Response
```

The important idea is that the LLM does **not** need to know the entire property database.

Instead:

1. Understand the user's request
2. Retrieve relevant properties
3. Provide those properties as context
4. Let the LLM generate a response based on retrieved information

This reduced the need to put the entire dataset into the model's context.

---

# 🧩 Why RAG Instead of Only an LLM?

An LLM alone does not have access to the application's current property inventory.

For example, asking:

```text
"Find me a 2 BHK in Mumbai under ₹2 crore."
```

should be answered using the actual database.

RAG makes the LLM part of a larger system:

Database → Retrieval → Context → LLM


rather than treating the LLM as the database itself.

This was one of the biggest conceptual lessons from the project.

---

# ⚡ Redis Caching

AI search and retrieval can be expensive operations.

Repeatedly processing the same query can result in unnecessary:

* Database queries
* Embedding generation
* Vector searches
* LLM requests

So Redis was introduced as a caching layer.


User Query
    │
    ▼
Generate Cache Key
    │
    ▼
Redis
 ┌──┴───┐
 │      │
Hit    Miss
 │      │
 ▼      ▼
Return  Search
Result    │
          ▼
       Store in
        Redis
          │
          ▼
       Return


The backend caches search-related results using Redis with expiration.

This taught me an important system-design concept:

> Not every request needs to reach the database or AI pipeline.

Caching can reduce latency, backend workload, and repeated computation.

---

# 🧠 System Design Concepts Learned

This project became my practical introduction to backend system design.

Instead of thinking only about:

Request → Response


I started thinking about:
Where should data live?

What should be cached?

Which service owns the data?

What happens if a service fails?

How do we scale search?

How do we separate responsibilities?

How do we prevent expensive operations from happening repeatedly?

How should external services communicate?

How should the application behave in production?

Some of the system-design concepts I learned through this project include:

### Separation of concerns

Routes
  ↓
Services
  ↓
Database / External Services


### Caching

Client
 ↓
API
 ↓
Redis
 ↓
Database / AI pipeline

### Vector retrieval


Query
 ↓
Embedding
 ↓
Vector Database
 ↓
Relevant Context


### External service integration


FastAPI
 ├── Supabase
 ├── Qdrant
 ├── Groq
 ├── Apify
 ├── Redis
 └── Telegram


### Configuration management

Development and production environments use different service URLs while the application code remains environment-independent.

---

# 📱 Telegram Integration

The project also includes a Telegram integration so that property discovery does not have to happen only through a website.

The intended flow is:

Telegram User
      │
      ▼
Telegram Bot
      │
      ▼
Webhook
      │
      ▼
FastAPI
      │
      ▼
AI Search / RAG
      │
      ▼
Relevant Properties
      │
      ▼
Telegram Response

This also helped me understand webhook-based architectures and how external applications can communicate with a backend API.

---

# 🔐 Authentication

The backend includes authentication functionality using:

* User registration
* Login
* Password hashing
* JWT-based authentication
* Protected user endpoints

Authentication was implemented separately from the property search pipeline so that public search functionality and user-specific functionality can remain logically separated.

---

# ☁️ Production Deployment

The application was deployed using **Railway**.

The architecture separates the frontend and backend services:


Railway
│
├── Flask Frontend
│
└── FastAPI Backend
       │
       ├── Supabase PostgreSQL
       ├── Supabase Storage
       ├── Qdrant Cloud
       ├── Redis
       ├── Groq
       └── Apify


Environment-specific configuration is provided through environment variables rather than hardcoded credentials.

---

# 🐛 Challenges Faced

This project was not built without problems. A major part of the learning came from debugging the issues that appeared while moving from local development to a distributed production environment.

## 1. Database Connection Problems

Connecting the local application to Supabase PostgreSQL required understanding:

* Connection strings
* Database hosts
* Ports
* Authentication
* Environment variables
* Local vs cloud database configuration

A small mistake in the connection URL was enough to prevent the application from reaching the database.

This taught me that infrastructure configuration is just as important as application code.

---

## 2. Alembic Migration Conflicts

As the database models evolved, migration history also evolved.

There were cases where the migration state and the database state were not aligned.

Debugging this required learning:

alembic current
alembic history
alembic upgrade head

and understanding revision chains.

This was my first practical experience dealing with database schema versioning rather than simply deleting and recreating tables.

---

## 3. AI Search Returning 500

One of the most useful production debugging experiences happened after deployment.

The Flask frontend was working, and the FastAPI server was running, but AI Search returned:

500 Internal Server Error

Initially, the problem appeared to be related to the API connection.

After tracing the request through the stack:


Flask
  ↓
FastAPI
  ↓
Property Service
  ↓
Redis

the actual error was:


redis.exceptions.ConnectionError:
Error 10061 connecting to localhost:6379


The problem was that Redis worked locally through Docker, but the production FastAPI service was still configured to connect to:


localhost:6379


In production, `localhost` referred to the FastAPI container itself, not the Railway Redis service.

The solution was to make Redis configuration environment-driven:


Local:
REDIS_URL=redis://localhost:6379

Production:
REDIS_URL=${{Redis.REDIS_URL}}


and initialize the Redis client from `REDIS_URL`.

This was an important real-world lesson about **service-to-service communication in cloud deployments**.

---

# 🔧 Localhost vs Production Architecture

A recurring lesson throughout the project was:

> Code that works locally does not automatically work in production.

Locally:


FastAPI
 ├── localhost PostgreSQL / Supabase
 ├── localhost Redis
 └── localhost frontend


Production:

FastAPI Container
 │
 ├── Supabase PostgreSQL
 ├── Railway Redis
 ├── Qdrant Cloud
 ├── Groq
 └── Apify


This required replacing assumptions such as:

host="localhost"

with environment-driven configuration.

---

# 📦 Dependency & Deployment Problems

Another production challenge occurred while deploying the Flask frontend.

The application worked locally through the Python environment, but the Railway deployment initially failed because the deployment environment did not have the expected `uv`/Gunicorn setup.

The solution involved understanding how Railway detects Python applications and ensuring the frontend had its own:

requirements.txt


with the required production dependencies.

The production server was then started using Gunicorn:


gunicorn app:app --bind 0.0.0.0:$PORT

This taught me the difference between:

Development server

and:

Production WSGI server

---

# 🧪 Development vs Production

The project forced me to think beyond simply making APIs work locally.

Development:

uv
FastAPI reload
Docker
localhost
.env


Production:

Railway
Gunicorn / Uvicorn
Cloud PostgreSQL
Cloud Redis
Qdrant Cloud
Environment variables
HTTPS
Service-to-service networking

This difference became one of the most valuable parts of the project.

---

# 📚 What I Learned

This project became a practical learning journey across several areas.

### Backend Development

* FastAPI
* REST API design
* Dependency injection
* Service-layer architecture
* Authentication
* JWT
* Environment configuration
* Error handling

### Databases

* PostgreSQL
* SQLAlchemy
* ORM
* Relationships
* Foreign keys
* Transactions
* Database sessions
* Alembic
* Schema migrations

### GenAI

* LLM integration
* Prompt design
* Embeddings
* Vector databases
* Semantic search
* RAG
* Retrieval pipelines
* Context construction

### Search

* Structured search
* Semantic search
* Vector similarity
* Hybrid search
* Retrieval quality
* Query understanding

### Performance

* Redis
* Cache keys
* TTL
* Avoiding repeated expensive operations
* Separating cache from source-of-truth data

### System Design

* Service separation
* External service integration
* Caching
* Data ownership
* Retrieval architecture
* Cloud deployment
* Environment-specific configuration
* Failure debugging

### DevOps

* Docker
* Railway
* Environment variables
* Production servers
* Cloud databases
* Service networking
* Deployment debugging

---

# 🗂️ Project Structure

The important backend structure is approximately:

Property_dealer_ai/
│
├── src/
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       └── routes/
│       │
│       ├── core/
│       │   └── config.py
│       │
│       ├── database/
│       │   ├── connection.py
│       │   ├── dependencies.py
│       │   └── redis.py
│       │
│       ├── models/
│       │
│       ├── schemas/
│       │
│       ├── services/
│       │   └── property.py
│       │
│       └── main.py
│
├── alembic/
│   └── versions/
│
├── flask_frontend/
│
├── frontend/
│   └── # Next.js frontend - currently separate from deployment
│
├── alembic.ini
├── pyproject.toml
└── README.md

---

# 🔌 Important API Areas

The FastAPI backend provides functionality around:

Properties
Users
Authentication
Favorites
Inquiries
Search
Semantic Search
Hybrid Search
AI Search
Telegram Webhook


The AI search endpoint accepts natural-language requirements rather than requiring the user to construct a large set of filters.

Example:

GET /api/v1/properties/ai-search

Example query:

"I want a 2 BHK in Mumbai to buy under ₹2 crore"

The backend then processes the request through the search and retrieval pipeline.

---

# 🔮 Future Improvements

Possible future improvements include:

* Better retrieval ranking
* Re-ranking retrieved properties
* More sophisticated query parsing
* Property recommendation scoring
* Better duplicate detection during ingestion
* Background ingestion jobs
* Improved observability and logging
* Rate limiting
* More advanced Redis strategies
* Evaluation datasets for retrieval quality
* Automated RAG evaluation
* Better Telegram conversational memory
* Scalable background workers
* More robust production monitoring

---

# 🎯 Why I Built This Project

The main objective was not simply to build another property listing website.

I wanted to understand how a modern backend system is designed when it combines:

Traditional Backend
        +
Relational Database
        +
External Data Ingestion
        +
Vector Search
        +
RAG
        +
LLM
        +
Caching
        +
Cloud Infrastructure


The project helped me move from thinking about individual technologies toward thinking about **how different systems work together as one production application**.

The biggest lesson was that building an AI application is not only about calling an LLM.

A useful AI system requires:

Good Data
   ↓
Good Storage
   ↓
Good Retrieval
   ↓
Good Context
   ↓
Good Generation
   ↓
Good Caching
   ↓
Good Infrastructure


That is the engineering problem this project was designed to explore.

---

# 👨‍💻 Author

Aditya Singh

Data Science & AI | Python | FastAPI | PostgreSQL | GenAI | RAG | System Design

GitHub: Rocksolid04
