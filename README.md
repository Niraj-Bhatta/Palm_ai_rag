<div align="center">

# Palm Mind AI

### Document Intelligence & Conversational RAG Backend

A modular, AI-powered backend built with **FastAPI** that combines document processing, Retrieval-Augmented Generation (RAG), conversational memory, and intelligent interview booking.

</div>

---

Users can upload PDF and TXT documents, ask natural-language questions about their content, and interact with an AI assistant that maintains conversation context and guides candidates through an interview-booking process.

The system integrates **Qdrant** for vector search, **Sentence Transformers** for local embedding generation, **Google Gemini** for language understanding and response generation, **Redis** for conversational state management, and **SQLite with SQLAlchemy** for persistent relational data.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Application Workflows](#application-workflows)
  - [Document Ingestion Pipeline](#1-document-ingestion-pipeline)
  - [Conversational RAG Pipeline](#2-conversational-rag-pipeline)
  - [Interview Booking Workflow](#3-interview-booking-workflow)
- [Database Design](#database-design)
- [Environment Configuration](#environment-configuration)
- [Installation and Setup](#installation-and-setup)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Project Overview

Traditional document-based question-answering systems often require users to manually search through documents to find relevant information.

This project addresses that problem with a custom Retrieval-Augmented Generation pipeline. Instead of relying entirely on an LLM's pretrained knowledge, the application retrieves relevant information from uploaded documents and uses it as context when generating answers.

The backend also supports multi-turn conversations. Redis maintains conversation history so the assistant can understand follow-up questions and preserve the context of an ongoing interaction.

In addition to document question answering, the application includes an AI-assisted interview-booking workflow. Candidates provide their information through natural-language messages. The system extracts the required details, validates them, presents a booking summary, and saves the booking after confirmation.

### Main Objectives

- Build a modular backend using FastAPI.
- Implement document ingestion and text-processing pipelines.
- Generate and store semantic embeddings.
- Build a custom RAG pipeline without relying on a prebuilt `RetrievalQAChain`.
- Support context-aware, multi-turn conversations.
- Integrate Redis for conversation history and temporary booking state.
- Use an LLM to extract structured interview-booking information.
- Validate and persist booking information using SQLAlchemy and SQLite.

---

## Core Features

### 1. Document Processing and Ingestion

- Upload PDF and TXT documents through a REST API.
- Extract text using PyMuPDF for PDF files and text decoding for TXT files.
- Divide extracted content into smaller, manageable chunks.
- Support configurable chunking strategies.
- Generate 384-dimensional semantic embeddings using Sentence Transformers.
- Store document vectors and associated payloads in Qdrant.
- Maintain document metadata in a relational database.

### 2. Retrieval-Augmented Generation

- Convert user questions into semantic embeddings.
- Search Qdrant for relevant document chunks.
- Retrieve contextual information based on semantic similarity.
- Pass retrieved content and conversation history to Google Gemini.
- Generate answers grounded in retrieved document content.
- Return the answer together with source information and retrieval statistics.

### 3. Conversational Memory

- Maintain conversation history using Redis.
- Associate messages with a conversation ID.
- Preserve context across multiple user interactions.
- Support follow-up questions without requiring users to repeat previous information.
- Store temporary interview-booking progress in Redis.

### 4. AI-Assisted Interview Booking

- Detect interview-booking requests in conversations.
- Extract candidate details from natural-language messages using Gemini.
- Collect the candidate's name, email, and preferred interview date and time.
- Validate email addresses and interview dates.
- Ask follow-up questions when required information is missing.
- Present the extracted details for user confirmation.
- Save confirmed booking information in SQLite.
- Clear the temporary booking state after completion or cancellation.

---

## System Architecture

The application follows a modular, service-oriented structure. API routes handle incoming requests, service modules implement business logic, and database modules manage persistent storage.

### High-Level Architecture

```text
                    CLIENT
                      |
                      v
                FASTAPI BACKEND
                      |
             +--------+--------+
             |                 |
             v                 v
      DOCUMENT API         CHAT API
             |                 |
             v                 v
      DOCUMENT SERVICE     RAG SERVICE
             |                 |
       +-----+-----+     +-----+----------+
       |           |     |                |
       v           v     v                v
   EXTRACTION   CHUNKING RETRIEVAL    BOOKING FLOW
       |           |     |                |
       +-----+-----+     v                |
             |         QDRANT             |
             v                            |
         EMBEDDINGS                       |
             |                            |
             v                            v
           QDRANT                    GEMINI LLM
                                          |
                                  +-------+-------+
                                  |               |
                                  v               v
                                REDIS           SQLITE
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| FastAPI | Exposes REST APIs and handles incoming requests |
| Extraction Service | Extracts text from supported document formats |
| Chunking Service | Splits extracted text into smaller chunks |
| Embedding Service | Converts text into numerical vector representations |
| Vector Store Service | Stores and retrieves document vectors from Qdrant |
| Retrieval Service | Finds relevant document chunks for user questions |
| RAG Service | Coordinates retrieval, memory, and LLM response generation |
| LLM Service | Generates responses and extracts structured booking information |
| Memory Service | Manages conversation history and booking state in Redis |
| Booking Conversation Service | Implements the conversational booking workflow |
| Booking Service | Persists confirmed bookings using SQLAlchemy |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Primary programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI application server |
| Pydantic | Request validation and structured data schemas |
| SQLAlchemy | Relational database ORM |
| SQLite | Document metadata and booking persistence |
| Qdrant Cloud | Vector database and similarity search |
| Sentence Transformers | Local text embedding generation |
| all-MiniLM-L6-v2 | Sentence embedding model |
| Google Gemini | LLM-based response generation and information extraction |
| Redis Cloud | Conversation history and temporary state |
| PyMuPDF | PDF text extraction |
| python-dotenv | Environment variable management |

### Why These Technologies?

- **FastAPI:** A lightweight, asynchronous-friendly framework with automatic OpenAPI documentation and request validation.
- **Qdrant:** Dedicated vector storage and semantic similarity search for document retrieval.
- **Sentence Transformers:** Generates embeddings locally, avoiding the need for a paid embedding API.
- **Google Gemini:** Handles natural-language response generation and structured interview-detail extraction.
- **Redis:** Fast access to conversation history and temporary booking information.
- **SQLite and SQLAlchemy:** Structured, persistent storage for document metadata and interview bookings.

---

## Project Structure

```text
palm-mind-rag/
│
├── app/
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py
│   │       └── documents.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── booking.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── booking_conversation_service.py
│   │   ├── booking_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── extraction_service.py
│   │   ├── llm_service.py
│   │   ├── memory_service.py
│   │   ├── rag_service.py
│   │   ├── retrieval_service.py
│   │   └── vector_store_service.py
│   │
│   └── main.py
│
├── tests/
│
├── uploads/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Directory Explanation

**`app/api/v1/`** — Versioned API endpoints.

- `documents.py`: Handles document-related requests, including uploading and retrieving document metadata.
- `chat.py`: Handles conversational RAG requests.

**`app/db/`** — Database configuration and SQLAlchemy models.

- `database.py`: Database connection and session management.
- `models.py`: Relational models for documents and interview bookings.

**`app/schemas/`** — Pydantic schemas for request validation and response serialization.

- `chat.py`: Chat request and response schemas.
- `booking.py`: Booking creation, response, and extracted booking-detail schemas.

**`app/services/`** — The application's core business logic.

- `extraction_service.py`: Extracts text from uploaded documents.
- `chunking_service.py`: Splits extracted text into chunks.
- `embedding_service.py`: Generates text embeddings.
- `vector_store_service.py`: Handles Qdrant operations.
- `retrieval_service.py`: Retrieves relevant document chunks.
- `llm_service.py`: Communicates with Gemini.
- `memory_service.py`: Manages Redis conversation memory.
- `rag_service.py`: Coordinates the RAG pipeline.
- `booking_conversation_service.py`: Manages conversational booking interactions.
- `booking_service.py`: Creates and persists booking records.

**`app/main.py`** — Initializes the FastAPI application, registers API routers, and configures application startup.

---

## Application Workflows

### 1. Document Ingestion Pipeline

The ingestion pipeline transforms uploaded files into searchable vector representations.

**Step 1 — Document Upload**
A client submits a PDF or TXT file through the document upload endpoint.

**Step 2 — Text Extraction**
The extraction service identifies the file format and extracts its textual content.

- PDF documents are processed using PyMuPDF.
- TXT documents are decoded and read as text.
- Empty extracted content is rejected.

**Step 3 — Text Chunking**
Large documents are divided into smaller chunks to make retrieval more focused and efficient. The application supports configurable chunking strategies, including recursive and token-based chunking.

| Parameter | Default |
|---|---:|
| Chunk size | 500 |
| Chunk overlap | 50 |

Chunk overlap helps preserve contextual continuity between adjacent chunks.

**Step 4 — Embedding Generation**
Each chunk is converted into a numerical vector using `sentence-transformers/all-MiniLM-L6-v2`, which generates 384-dimensional embeddings locally.

**Step 5 — Vector Storage**
The generated embeddings and their metadata are stored in Qdrant. Each stored vector is associated with information that identifies its source document and corresponding content.

**Step 6 — Metadata Persistence**
Document-level metadata is stored in SQLite using SQLAlchemy, separating document management information from the vector representations used for semantic retrieval.

<details>
<summary>Document ingestion flow</summary>

```text
PDF / TXT Upload
       |
       v
File Validation
       |
       v
Text Extraction
       |
       v
Empty Content Check
       |
       v
Text Chunking
       |
       v
Embedding Generation
       |
       v
Qdrant Vector Storage
       |
       v
SQLite Metadata Storage
       |
       v
Document Ready for Retrieval
```

</details>

### 2. Conversational RAG Pipeline

The conversational RAG pipeline combines semantic retrieval with LLM-based generation. Rather than asking the LLM to answer from pretrained knowledge alone, the application first retrieves relevant content from uploaded documents.

**Step 1 — Receive User Question**
The chat API receives a question along with its conversation ID.

**Step 2 — Load Conversation History**
The memory service retrieves previous messages for the conversation from Redis.

**Step 3 — Determine the Request Type**
The application checks whether the message belongs to an ongoing interview-booking conversation or is a new booking request. If so, it is routed to the booking conversation service. Otherwise, the normal RAG pipeline continues.

**Step 4 — Generate Query Embedding**
The embedding service converts the user's question into a vector using the same model used during ingestion.

**Step 5 — Retrieve Relevant Chunks**
The retrieval service searches Qdrant for semantically relevant document chunks.

**Step 6 — Build LLM Context**
The application combines the retrieved document content with relevant conversation history.

**Step 7 — Generate Answer**
Google Gemini generates a response using the supplied context.

**Step 8 — Update Conversation Memory**
The user message and generated assistant response are stored in Redis for future interactions.

**Step 9 — Return API Response**
The application returns the generated answer, source information, and the number of retrieved chunks.

#### RAG Response Structure

```json
{
  "answer": "Generated response based on the retrieved context.",
  "sources": [],
  "retrieved_count": 0
}
```

> The example illustrates the response structure; actual source entries and retrieval counts depend on the query and available documents.

### 3. Interview Booking Workflow

Interview booking is integrated into the conversational endpoint, letting candidates schedule an interview through natural-language messages instead of a separate booking form.

**Step 1 — Booking Intent Detection**
The RAG service identifies interview-booking requests and checks whether a booking conversation is already in progress.

**Step 2 — Extract Candidate Information**
The LLM service uses Google Gemini to extract structured information from the conversation. Required fields:

- Candidate name
- Email address
- Preferred interview date and time

**Step 3 — Maintain Booking State**
The memory service stores partially collected booking information in Redis, so the candidate can provide missing information across multiple messages.

```text
Candidate: I want to schedule an interview.

Assistant: Sure! May I have your name?

Candidate: Niraj Bhatta.

Assistant: Thanks! What is your email address?

Candidate: niraj@example.com.

Assistant: What date and time would you prefer?
```

> The example is illustrative; the actual conversation depends on the information already provided.

**Step 4 — Validate Information**

- Candidate name must not be empty.
- Email must satisfy email validation.
- Interview date and time must be in the future.
- The `Asia/Kathmandu` timezone is used for date-related validation.

If required information is missing or invalid, the assistant requests the necessary correction.

**Step 5 — Request Confirmation**
After collecting the required information, the assistant displays a summary and asks the candidate to confirm.

**Step 6 — Persist Booking**
After confirmation, the booking service creates a booking record using SQLAlchemy and saves it in SQLite.

**Step 7 — Clear Temporary State**
Once the booking is completed or cancelled, the temporary booking state is cleared from Redis.

<details>
<summary>Booking flow</summary>

```text
Interview Booking Request
           |
           v
    Intent Detection
           |
           v
   Extract Information
           |
           v
   Check Missing Fields
           |
       +---+---+
       |       |
     Missing  Complete
       |       |
       v       v
 Ask for     Validate
 Details     Details
       |       |
       +-------+
           |
           v
    Display Summary
           |
           v
   Request Confirmation
           |
       +---+---+
       |       |
      Yes      No
       |       |
       v       v
 Save Booking Cancel Booking
       |       |
       +---+---+
           |
           v
    Clear Redis State
```

</details>

---

## Database Design

The application uses three storage systems, each for a different purpose.

### 1. Qdrant — Vector Database

Qdrant stores the vector representations of document chunks. Each vector is associated with its document-related payload, allowing the retrieval service to search for relevant content and identify the source document. The embedding model produces vectors with 384 dimensions.

### 2. SQLite — Relational Database

SQLite stores structured application records through SQLAlchemy.

**Document** — Stores metadata for uploaded files.

**Booking** — Stores confirmed interview-booking information:

| Field | Description |
|---|---|
| `id` | Unique booking identifier |
| `conversation_id` | Associated conversation |
| `candidate_name` | Candidate's name |
| `email` | Candidate's email |
| `interview_date` | Preferred interview date and time |
| `status` | Booking status |
| `created_at` | Booking creation timestamp |

### 3. Redis — Conversation Storage

Redis holds temporary, frequently accessed conversational information:

- Conversation history
- User and assistant messages
- Partially completed booking information
- Booking confirmation state

Conversation data is configured with a **24-hour TTL**, keeping conversational state separate from persistent relational records.

---

## Environment Configuration

The application uses environment variables for service credentials and configuration. Create a `.env` file in the project root:

```env
# Qdrant Configuration
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=your_collection_name

# Database Configuration
DATABASE_URL=your_database_url

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

# Redis Configuration
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

Replace the placeholder values with your own credentials and configuration.

### Required External Services

1. **Qdrant Cloud:** Create a cluster and obtain its URL and API key.
2. **Google Gemini:** Obtain an API key and configure the model name.
3. **Redis:** Configure a Redis instance and its connection credentials.

SQLite is used as the relational database and does not require a separate server.

> [!WARNING]
> Do not commit `.env` to GitHub. Keep credentials private and provide an `.env.example` file containing placeholders when sharing the project.

---

## Installation and Setup

### Prerequisites

- Python 3.12
- Git
- A Qdrant Cloud account
- A Google Gemini API key
- A Redis instance

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd palm-mind-rag
```

### 2. Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create the `.env` file and add the configuration described [above](#environment-configuration).

### 6. Start the Application

```bash
uvicorn app.main:app --reload
```

The backend will be available at `http://127.0.0.1:8000`.

---

## API Reference

FastAPI automatically generates interactive API documentation. Open Swagger UI at:

**http://127.0.0.1:8000/docs**

### Document APIs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload` | Upload and process a document |
| `GET` | `/api/v1/documents/` | Retrieve document metadata |
| `GET` | `/api/v1/documents/{document_id}` | Retrieve metadata for a specific document |

### Chat API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/` | Submit a question or continue a conversation |

The chat endpoint supports both document-based question answering and the interview-booking conversation flow.

### Example Chat Request

The following illustrates the general structure of a conversational request. Refer to the generated Swagger schema for the exact request fields.

```json
{
  "question": "What information is available in the uploaded document?",
  "conversation_id": "conversation-001"
}
```

### Testing the APIs

Use Swagger UI to:

1. Upload a PDF or TXT document.
2. Verify that document metadata is available.
3. Submit questions about the uploaded content.
4. Ask follow-up questions using the same conversation ID.
5. Start an interview-booking conversation.
6. Provide candidate details and confirm the booking.
7. Verify that the booking has been stored.

---

## Design Decisions

### Custom RAG Implementation

Retrieval and generation are implemented as separate services rather than relying on a prebuilt `RetrievalQAChain`. This provides more control over document retrieval, context construction, conversation history, and response generation.

### Local Embedding Generation

Sentence Transformers generates embeddings locally, while Gemini handles LLM-based tasks. This separates embedding generation from language generation and avoids relying on a paid embedding API.

### Separation of Storage Responsibilities

- **Qdrant** handles semantic vector retrieval.
- **Redis** handles temporary conversational state.
- **SQLite** stores persistent relational records.

### Stateful Conversational Booking

The booking workflow uses Redis to preserve progress across messages. Instead of requiring all candidate information in a single request, the assistant collects missing fields through a multi-turn conversation.

### Modular Service Architecture

Each major operation has a dedicated service module, making the application easier to maintain, debug, extend, and test independently.

---

## Limitations

- Only PDF and TXT document formats are supported.
- Scanned PDFs requiring OCR are not currently supported.
- Interview booking does not connect to an external calendar or independently verify interviewer availability.
- Booking management currently focuses on the creation and cancellation conversation flow.
- The application does not include user authentication or role-based access control.
- Retrieval quality depends on the uploaded document content, chunking configuration, and embedding model.

---

## Future Improvements

- [ ] Add OCR support for scanned PDF documents.
- [ ] Introduce automated unit and integration tests.
- [ ] Implement RAG evaluation to measure retrieval and answer quality.
- [ ] Integrate calendar APIs to verify real interview availability.
- [ ] Add interview rescheduling and booking-management endpoints.
- [ ] Implement authentication and authorization.
- [ ] Add structured application logging and monitoring.
- [ ] Improve retrieval through reranking and more advanced retrieval strategies.
- [ ] Add deployment configuration and production-ready infrastructure.

---

## Author

**Niraj Bhatta**
Computer Engineering Student | AI Engineering

- GitHub: [Niraj-Bhatta](https://github.com/Niraj-Bhatta)
- Portfolio: [nirajbhatta.info.np](https://nirajbhatta.info.np)

---

<div align="center">

*Built as a backend engineering assignment for Palm Mind AI.*

</div>