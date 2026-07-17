# Asset Management System

This project is a FastAPI-based asset management platform for storing, importing, querying, enriching, and analyzing internet-facing assets. It is designed to handle common inventory challenges such as duplicate records, evolving asset states, and relationships between different assets.

## Features

- Import asset inventories from external sources
- Deduplicate and update existing assets safely
- Query assets using natural language
- Generate risk scores for assets
- Enrich assets with rule-based and LLM-assisted metadata
- Create structured security reports from asset data

## Tech Stack

- FastAPI for the API layer
- SQLAlchemy for database models and ORM access
- PostgreSQL for persistence
- Docker Compose for local database setup
- Pydantic for request and response validation
- LangChain and Google Gemini for AI-powered features

## Project Structure

The application follows a layered structure:

- main.py: FastAPI application entry point
- routes/api/: HTTP route handlers for import, asset, ask, risk, enrichment, and report features
- controllers/agents/: AI orchestration modules used by reporting and other intelligent workflows
- controllers/services/: Core business logic for import, enrichment, risk scoring, reporting, and asset retrieval
- models/schemas/: Pydantic request and response schemas
- models/utils/: Shared utilities such as the rule engine
- db/database/: SQLAlchemy models, database connection, and schema helpers
## Prerequisites

Before running the project, make sure you have:

- Python 3.11
- Docker Desktop for PostgreSQL
- A Google API key for the AI features

## Setup

### 1. Start PostgreSQL with Docker

From the project root, run:

```bash
docker compose up -d
```


The database will be available at:

- Host: localhost
- Port: 5432
- Database: darkatlas
- Username: postgres

### 2. Create and activate a Python environment

```bash
conda create -n asset-env python=3.11
conda activate asset-env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and fill in the required values:

```bash
cp .env.example .env
```

Example contents:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/darkatlas
GOOGLE_API_KEY=your-google-api-key
```

### 5. Create the database tables

```bash
python create_tables.py
```

## Running the Application

Start the API server with:

```bash
uvicorn main:app --reload
```

Once running, the interactive documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Data Model

The application stores assets in PostgreSQL using SQLAlchemy models.

### Asset

Each asset contains:

| Field | Purpose |
| --- | --- |
| id | UUID primary key |
| type | Asset category |
| value | Asset identifier such as a domain or IP address |
| status | Asset lifecycle state such as active, stale, or archived |
| first_seen | First time the asset was discovered |
| last_seen | Most recent time the asset was seen |
| source | Source of the imported record |
| tags | Optional tags associated with the asset |
| metadata_json | Flexible JSON metadata for asset-specific details |

### Relationships

Assets can be linked through relationship records, allowing mappings such as:

- Domain → Subdomain
- Domain → IP Address
- IP Address → Service
- Service → Technology

## Import Workflow

The import endpoint accepts batches of asset records and processes each record independently.

Behavior includes:

- Creating new assets when they do not already exist
- Updating existing assets instead of creating duplicates
- Matching assets by the combination of type and value
- Refreshing last_seen on successful imports
- Reactivating stale assets when they reappear
- Merging tags and metadata without duplicating values
- Skipping malformed records without stopping the full batch

## AI Features

### Natural Language to SQL

Users can ask questions in natural language and the application converts them into SQL queries that are executed against the PostgreSQL database. The system is designed to return only data-backed answers and avoid unsupported or fabricated responses.

### Risk Scoring

The risk scoring feature uses an LLM with a fixed scoring policy to produce a structured risk assessment for each asset.

### Asset Enrichment

Asset enrichment combines a deterministic rule engine with an LLM to infer useful metadata such as environment, category, criticality, description, and tags.

### Report Generation

The reporting feature gathers relevant assets, evaluates their risk, and produces a concise security report with findings and recommendations.

## Notes

- The AI features require a valid Google API key.
- The enrichment pipeline uses rules first and only allows the LLM to complete fields that are still unknown.
- The application is intentionally structured around clear separation between API routes, business logic, and persistence.


