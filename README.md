SmartStay / Ttrip
SmartStay (codename: Ttrip) is a multi-agent travel booking platform that helps users search, select, and book hotels and flights through a natural-language chat interface.
The project combines a Next.js frontend, an asynchronous FastAPI backend, LangGraph-based AI orchestration, and LiteAPI travel services for real-time hotel and flight inventory. It also uses PostgreSQL, Redis, and Elasticsearch to support booking persistence, conversation memory, and retrieval-augmented generation.

Table of Contents
·	Project Overview
·	DeepWiki Project Overview Full Text
·	Main Features
·	High-Level Architecture
·	Tech Stack
·	Core Booking Workflows
·	AI Agent System
·	Backend Architecture
·	Frontend Architecture
·	LiteAPI Integration
·	Payment Flow
·	Local Development
·	Environment Variables
·	Useful Commands
·	Testing
·	Project Structure
·	Roadmap Ideas

Project Overview
SmartStay / Ttrip is designed as an AI-powered travel assistant. Instead of forcing users to fill long forms, the platform allows them to describe what they want in natural language, then the system extracts travel intent, asks for missing details, calls external travel APIs, and guides the user through the booking process.
Example user flow:
User: I want a hotel in Paris from June 10 to June 14 for 2 adults.
Ttrip: Searches available hotels using LiteAPI.
User: Selects a hotel or asks questions about amenities.
Ttrip: Prebooks the selected offer and starts payment.
User: Completes payment.
Ttrip: Confirms the booking and stores it in the database.

The platform supports:
·	Natural-language travel search
·	Hotel discovery and booking
·	Flight search and booking workflow
·	AI-guided slot filling
·	Conversation memory
·	Secure payment handoff using LiteAPI Payment SDK
·	Authenticated frontend experience using Clerk
·	Persistent booking records
·	RAG-ready knowledge retrieval using Elasticsearch

DeepWiki Project Overview Full Text
Source: SmartStay (ttrip) — Project Overview on DeepWiki
SmartStay (ttrip) — Project Overview
Relevant source files
·	README.md
·	backend/app/main.py
·	backend/app/services/liteapi_service.py
·	backend/requirements.txt
·	docker-compose.yml
SmartStay (codenamed ttrip) is a multi-agent travel platform designed to facilitate hotel and flight bookings through a natural language interface. The system leverages LangGraph for orchestration, FastAPI for the backend service, and Next.js for the frontend. It integrates with LiteAPI for real-time travel data and utilizes a multi-layer storage strategy involving PostgreSQL, Redis, and Elasticsearch.
System Architecture
The platform is divided into a high-performance backend and a responsive frontend, bridged by a multi-agent AI system that handles intent recognition and task execution.
High-Level Component Interaction
Sources: backend/app/main.py lines 73-93, docker-compose.yml lines 21-64.
Tech Stack
Layer	Technology	Key Components
Backend	FastAPI	RequestContextMiddleware, limiter, lifespan
AI Orchestration	LangGraph	StateGraph, BookingState, AsyncPostgresSaver
Database	PostgreSQL	SQLAlchemy, AsyncConnectionPool
Caching/Memory	Redis	ConversationMemory, Session Persistence
Search/RAG	Elasticsearch	OrchestrationRetriever, Knowledge Retrieval
External API	LiteAPI	LiteAPIService, LiteAPIHotelsService
Frontend	Next.js 14	App Router, Clerk Auth, Tailwind CSS

Sources: backend/requirements.txt lines 1-22, backend/app/main.py lines 1-22.
Key Architectural Decisions
1.	Multi-Agent Orchestration: Instead of a single monolithic LLM prompt, the system uses a booking_graph defined in LangGraph to route user requests to specialized sub-agents, for example hotel_agent and insurance_agent.
2.	Stateless API with State-full Agents: The FastAPI layer remains largely stateless, while the agent's state is persisted across turns using an AsyncPostgresSaver checkpointer or MemorySaver.
3.	Resilient Service Layer: The LiteAPIService implements a robust request mechanism with exponential backoff and retry logic for external API calls.
4.	Hybrid Memory: User profiles and short-term conversation context are cached in Redis, while the long-term agent state resides in PostgreSQL.
Code Entity Mapping: Backend Initialization
Sources: backend/app/main.py lines 41-68, backend/app/services/liteapi_service.py lines 10-14.
External Integrations
The system relies heavily on the LiteAPIService to interact with travel providers. It maintains two distinct base URLs for data retrieval and booking operations:
·	Data API: https://api.liteapi.travel/v3.0
·	Booking API: https://book.liteapi.travel/v3.0
The service class LiteAPIService handles header injection using X-API-Key and manages request timeouts and retries via httpx.AsyncClient.
Sources: backend/app/services/liteapi_service.py lines 10-53.
Child Pages
Detailed documentation for specific subsystems can be found in the following sections:
·	Getting Started & Local Development: Instructions on using Docker Compose to spin up the full environment, including geai_fastapi, geai_frontend, geai_redis, and geai_elasticsearch.
·	Configuration & Settings Reference: A guide to the Pydantic-based settings object and the environment variables required for LLM providers, OpenAI/Google, and LiteAPI.
Sources: docker-compose.yml lines 1-99, backend/app/main.py line 15.

Main Features
AI Travel Chat
Users interact with the system through a chat interface. The AI agent understands travel requests, extracts useful information, and routes each step to the correct specialized workflow.
Hotel Booking
The platform can search hotel destinations, retrieve live rates, prebook offers, initialize payment, and finalize confirmed bookings.
Flight Booking
The flight workflow follows the stricter flight booking lifecycle:
Search → Select → Verify → Prebook → Add Extras → Book → Confirm

Verification is required before prebooking because flight prices and availability can change quickly.
Persistent Conversation State
The system keeps track of booking state across messages, including destination, dates, guests, selected offers, prebook IDs, payment status, and final booking references.
External Travel Provider Integration
LiteAPI is used as the primary travel inventory and booking provider for hotels and flights.
Payment Integration
The payment flow uses LiteAPI Payment SDK. The backend creates the prebook session, the frontend renders the payment widget, and the backend resumes booking finalization after successful payment.

High-Level Architecture
graph TD
    U[User] --> UI[Ttrip Chat UI / Next.js Frontend]
    UI --> Proxy[Next.js API Proxy]
    Proxy --> API[FastAPI Backend]

    API --> Auth[Clerk Auth Context]
    API --> Agent[LangGraph Booking Agent]
    Agent --> Tools[MCP / LiteAPI Tools]
    Tools --> LiteAPI[LiteAPI Hotels & Flights]

    API --> PG[(PostgreSQL)]
    API --> Redis[(Redis Memory)]
    API --> ES[(Elasticsearch RAG)]

    UI --> Payment[LiteAPI Payment Widget]
    Payment --> LiteAPI
    LiteAPI --> API

The architecture is separated into:
1.	Frontend layer: Next.js chat UI, Clerk authentication, typed API proxy, payment widget.
2.	Backend API layer: FastAPI routers, middleware, validation, metrics, and standardized responses.
3.	Agent layer: LangGraph orchestration, booking state, specialized nodes, and LLM routing.
4.	Service layer: LiteAPI hotel/flight services, retry logic, external provider integration.
5.	Persistence layer: PostgreSQL for bookings and users, Redis for short-term memory, Elasticsearch for retrieval.

Tech Stack
Layer	Technology	Role
Frontend	Next.js 14, React, TypeScript	Chat UI, routing, API proxy, payment UI
Styling	Tailwind CSS	Responsive UI and layout
Authentication	Clerk	User authentication and protected pages
Backend	FastAPI, Uvicorn	Async API service
AI Orchestration	LangGraph	Booking graph, routing, state machine
LLM Providers	Gemini, Groq, SwiftRouter-compatible providers	AI reasoning and intent routing
Database	PostgreSQL, SQLAlchemy async, asyncpg	Users, profiles, bookings, agent persistence
Memory / Cache	Redis	Conversation memory and session state
Search / RAG	Elasticsearch	Knowledge retrieval for orchestration
External Travel API	LiteAPI	Hotel and flight inventory, booking, payment
Observability	Prometheus, JSON logs	Metrics and structured logs
Rate Limiting	SlowAPI	API quota and abuse protection
Deployment	Docker Compose, Docker	Local multi-service environment


Core Booking Workflows
Hotel Booking Workflow
sequenceDiagram
    participant User
    participant UI as Ttrip Chat UI
    participant API as FastAPI Backend
    participant Agent as LangGraph Agent
    participant LiteAPI
    participant DB as PostgreSQL

    User->>UI: Ask for a hotel
    UI->>API: Send chat message
    API->>Agent: Invoke booking graph
    Agent->>LiteAPI: Search places / rates
    LiteAPI-->>Agent: Hotel offers
    Agent-->>API: Structured hotel results
    API-->>UI: Render hotel options
    User->>UI: Select hotel rate
    UI->>API: Confirm selected offer
    API->>Agent: Prebook selected rate
    Agent->>LiteAPI: Prebook
    LiteAPI-->>Agent: Prebook ID + payment data
    API-->>UI: Payment widget metadata
    User->>UI: Complete payment
    UI->>API: Payment verified sentinel
    API->>LiteAPI: Final book call
    API->>DB: Persist booking
    API-->>UI: Booking confirmation

Flight Booking Workflow
graph LR
    A[Search Flights] --> B[Select Offer]
    B --> C[Verify Offer]
    C --> D[Prebook Flight]
    D --> E[Add Extras]
    E --> F[Book]
    F --> G[Confirm]

Flight booking is stricter than hotel booking because the selected offer must be verified before prebooking. Optional extras such as baggage or seat selection can be attached before the final booking call.

AI Agent System
The AI system is built around a LangGraph booking graph. The graph receives the current conversation state, decides the next action, and routes the request to the appropriate node.
Main responsibilities
·	Understand user intent
·	Extract missing travel fields
·	Ask clarification questions
·	Search hotels or flights
·	Handle hotel selection
·	Verify and prebook offers
·	Trigger payment flow
·	Resume final booking after payment
·	Persist confirmed booking data
Agent Architecture
graph TD
    UserMessage[User Message] --> Orchestrator[Travel Orchestrator]

    Orchestrator -->|Hotel intent| HotelAgent[Hotel Agent]
    Orchestrator -->|Flight intent| FlightAgent[Flight Agent]
    Orchestrator -->|General question| GeneralAgent[Travel Assistant]
    Orchestrator -->|Missing data| Clarification[Ask Clarification]

    HotelAgent --> SearchHotels[Search Hotels]
    HotelAgent --> SelectHotel[Hotel Selection]
    HotelAgent --> PrebookHotel[Prebook Hotel]

    FlightAgent --> SearchFlights[Search Flights]
    FlightAgent --> VerifyFlight[Verify Offer]
    FlightAgent --> PrebookFlight[Prebook Flight]
    FlightAgent --> AddExtras[Attach Extras]

    PrebookHotel --> Payment[Payment Required]
    PrebookFlight --> Payment
    Payment --> ConfirmBooking[Finalize Booking]

Booking State
The booking state acts as the single source of truth during the conversation. It can contain:
·	Conversation messages
·	User intent
·	Destination / city
·	Check-in and check-out dates
·	Flight origin and destination
·	Guest and passenger details
·	Selected hotel or flight offer
·	Prebook ID
·	Payment status
·	Provider booking ID
·	Runtime errors or missing fields

Backend Architecture
The backend is an asynchronous FastAPI application that exposes versioned API routes and coordinates the AI booking workflow.
Backend Layers
graph TD
    Client[Frontend / API Client] --> Routers[FastAPI Routers]
    Routers --> Middleware[Middleware & Security]
    Routers --> Schemas[Pydantic Schemas]
    Routers --> AgentLayer[Agent Layer]
    AgentLayer --> Services[Service Layer]
    Services --> LiteAPI[LiteAPI]
    AgentLayer --> Repositories[Repository Layer]
    Repositories --> PostgreSQL[(PostgreSQL)]
    AgentLayer --> Redis[(Redis)]
    AgentLayer --> Elasticsearch[(Elasticsearch)]

Main API Areas
The backend includes routers for:
·	/chat
·	/hotels
·	/flights
·	/bookings
·	/users
·	/health
·	/metrics
Middleware and Operations
The backend includes:
·	Request context middleware
·	Request ID propagation
·	Rate limiting using SlowAPI
·	Prometheus metrics endpoint
·	Centralized error handling
·	Structured JSON logs
·	External provider timeout and retry settings
Application Startup
During startup, the backend:
1.	Configures logging.
2.	Initializes the database engine.
3.	Creates database schemas when needed.
4.	Builds the booking dependency container.
5.	Initializes LangGraph persistence/checkpointing.
6.	Compiles the booking graph.
7.	Attaches shared services to FastAPI app state.

Frontend Architecture
The frontend is a Next.js 14 application using the App Router. It provides the main user-facing experience for chatting with the AI travel agent.
Frontend Responsibilities
·	Public landing page
·	Authenticated chat page
·	Sidebar conversation history
·	Header and user navigation
·	Chat input and message rendering
·	Hotel selection modal
·	Flight result rendering
·	Payment widget rendering
·	API proxy to FastAPI backend
·	Type-safe data models using TypeScript interfaces
Frontend Data Flow
graph TD
    Page[Chat Page] --> ChatInterface[Chat Interface]
    ChatInterface --> ChatInput[Chat Input]
    ChatInterface --> ChatMessage[Chat Message]
    ChatMessage --> HotelModal[Hotel Selection Modal]
    ChatMessage --> FlightList[Flight Selection List]
    ChatMessage --> PaymentWidget[LiteAPI Payment Widget]

    ChatInterface --> ApiProxy[Next.js API Proxy]
    ApiProxy --> Backend[FastAPI Backend]
    ApiProxy --> Clerk[Clerk Auth Token]

The frontend uses a proxy pattern so authentication headers and response normalization can be handled server-side before forwarding requests to the backend.

LiteAPI Integration
LiteAPI is the main provider for travel inventory and booking fulfillment.
Base Services
The backend uses a base LiteAPI service that handles:
·	API key injection through X-API-Key
·	Data API and booking API URL switching
·	Request timeouts
·	Retryable error handling
·	Exponential backoff
·	Transport error handling
LiteAPI Base URLs
Purpose	Base URL
Data API	https://api.liteapi.travel/v3.0
Booking API	https://book.liteapi.travel/v3.0

Hotel Service Capabilities
Function	Purpose
search_places	Resolve text destinations into LiteAPI place IDs
search_rates	Fetch live hotel rates
prebook_full	Lock an offer and create a prebook session
book	Finalize a booking
cancel_booking	Cancel a reservation
semantic_search	Search hotels using natural language attributes
ask_question	Ask questions about a hotel

Flight Service Capabilities
Function	Purpose
search	Search flight offers
verify	Verify selected flight offer validity
prebook	Reserve a verified flight offer
attach_services	Add extras such as baggage or seat selection
book	Complete the final booking


Payment Flow
SmartStay uses a multi-stage payment lifecycle based on LiteAPI Payment SDK.
sequenceDiagram
    participant User
    participant UI as Frontend
    participant API as Backend
    participant Agent as LangGraph Agent
    participant LiteAPI
    participant DB as PostgreSQL

    User->>UI: Select offer
    UI->>API: Send selected offer
    API->>Agent: Trigger prebook node
    Agent->>LiteAPI: Prebook with usePaymentSdk=true
    LiteAPI-->>Agent: prebookId, transactionId, secretKey
    API-->>UI: Payment metadata
    UI->>LiteAPI: Render Payment SDK
    User->>LiteAPI: Pay
    LiteAPI-->>UI: Redirect with payment_success=1
    UI->>API: Send internal payment verified message
    API->>LiteAPI: Final book request
    LiteAPI-->>API: Booking confirmation
    API->>DB: Save booking
    API-->>UI: Show confirmation

Sentinel Message Pattern
After payment, the frontend sends a hidden internal message to the backend:
__internal_payment_verified__

This allows the backend to resume the booking flow after the external payment redirect and finalize the booking using the stored conversation and prebook state.

Local Development
Prerequisites
Make sure you have:
·	Docker
·	Docker Compose
·	Node.js / npm, if running frontend outside Docker
·	Python 3.11+, if running backend outside Docker
·	LiteAPI API key
·	At least one LLM provider API key, such as Gemini, Groq, or SwiftRouter-compatible key

Environment Variables
Create a backend environment file:
cp backend/.env.example backend/.env

Then configure the required values.
Example .env
APP_NAME=ttrip
APP_VERSION=0.1.0
APP_DESCRIPTION=ttrip API
ENVIRONMENT=local

# AI inference
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

# LiteAPI
LITEAPI_API_KEY=
LITEAPI_ENV=sandbox
LITEAPI_MCP_TOOL_NAMES=get_data_hotels
LITEAPI_MCP_TOOL_TIMEOUT_SECONDS=8

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=myapp

# Redis
REDIS_URL=
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
REDIS_KEY_PREFIX=ttrip
ORCHESTRATOR_MEMORY_TURNS=6

# Elasticsearch
ELASTICSEARCH_HOST=
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_INDEX=ttrip_knowledge
ORCHESTRATOR_RETRIEVAL_LIMIT=3

# Operations
LOG_LEVEL=INFO
JSON_LOGS=true
REQUEST_ID_HEADER=X-Request-ID
ENABLE_METRICS=true
RATE_LIMIT_ENABLED=false
RATE_LIMIT_DEFAULT=120/minute
PROVIDER_REQUEST_TIMEOUT_SECONDS=30
PROVIDER_MAX_RETRIES=2

# Security
SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Do not commit real API keys or production secrets to GitHub.

Useful Commands
Start Core Services
docker compose up --build

This starts:
·	PostgreSQL
·	FastAPI backend
·	Next.js frontend
Start With Orchestration Services
docker compose --profile orchestration up --build

This also starts:
·	Redis
·	Elasticsearch
Access Services
Service	URL
Frontend	http://localhost:3005
Backend	http://localhost:8002
Backend health	http://localhost:8002/health
Metrics	http://localhost:8002/metrics
PostgreSQL host port	5434
Redis	6379
Elasticsearch	http://localhost:9200

Stop Services
docker compose down

Stop and Remove Volumes
docker compose down -v


Testing
The backend uses pytest and pytest-asyncio.
cd backend
pytest

If using Docker:
docker compose exec fastapi pytest

Testing should cover:
·	API routes
·	Booking graph nodes
·	LiteAPI service wrappers
·	Repository layer
·	Payment finalization logic
·	Error handling

Project Structure
SmartStay/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── booking/
│   │   │       ├── graph.py
│   │   │       ├── state.py
│   │   │       ├── nodes.py
│   │   │       └── dependencies.py
│   │   ├── api/
│   │   │   └── V1/
│   │   │       ├── chat.py
│   │   │       ├── hotels.py
│   │   │       ├── flights.py
│   │   │       ├── bookings.py
│   │   │       └── users.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── services/
│   │   │   ├── liteapi_service.py
│   │   │   ├── liteapi_hotels_service.py
│   │   │   └── liteapi_flights_service.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── chat/
│   │   ├── payment/
│   │   │   └── liteapi/
│   │   └── api/
│   ├── components/
│   │   └── chat/
│   ├── lib/
│   │   └── types.ts
│   └── package.json
│
├── docker-compose.yml
└── README.md


Configuration Notes
LLM Provider Fallback
The backend supports multiple LLM providers. The dependency container can attempt a primary provider and fall back to another provider when needed.
Common provider variables include:
·	GOOGLE_API_KEY
·	GEMINI_MODEL
·	GROQ_API_KEY
·	GROQ_MODEL
·	SWIFTROUTER_API_KEY
·	SWIFTROUTER_MODEL
LiteAPI Environment
Use sandbox during development:
LITEAPI_ENV=sandbox

For production, use:
LITEAPI_ENV=production

Make sure your LiteAPI account has the required hotel and/or flight permissions enabled.
Redis Memory
Redis stores short-term conversation context and payment-related temporary state.
Important variables:
REDIS_KEY_PREFIX=ttrip
ORCHESTRATOR_MEMORY_TURNS=6

Elasticsearch RAG
Elasticsearch is used for retrieval-augmented orchestration. It can provide domain knowledge to the AI agent.
Important variables:
ELASTICSEARCH_INDEX=ttrip_knowledge
ORCHESTRATOR_RETRIEVAL_LIMIT=3


Error Handling
The backend standardizes errors into JSON responses.
Error Type	Typical Status	Description
Validation error	422	Invalid request body or parameters
Provider runtime error	502 / custom	LiteAPI or LLM provider failure
Rate limit error	429	API quota or request limit exceeded
Internal error	500	Unexpected server-side issue

For provider calls, the LiteAPI service retries transient failures such as rate limits, timeouts, and 5xx errors using exponential backoff.

Security Notes
·	Never expose secretKey returned by payment prebook calls in logs.
·	Never commit .env files containing real credentials.
·	Use Clerk-authenticated requests for protected pages and user-specific bookings.
·	Keep payment finalization server-side.
·	Use SECRET_KEY with a strong production value.
·	Enable rate limiting in production.
·	Keep structured logs free from sensitive payment and API key data.

Roadmap Ideas
Possible improvements:
·	Add full booking management dashboard.
·	Add cancellation and refund UX.
·	Improve flight extras selection UI.
·	Add admin analytics for bookings and provider errors.
·	Add automated RAG indexing pipeline.
·	Add CI/CD pipeline for tests and linting.
·	Add Kubernetes manifests for production deployment.
·	Add Terraform modules for cloud infrastructure.
·	Add end-to-end tests for complete hotel and flight booking flows.

License
Add your project license here.
Example:
MIT License


Acknowledgements
This project uses:
·	FastAPI
·	Next.js
·	LangGraph
·	LiteAPI
·	PostgreSQL
·	Redis
·	Elasticsearch
·	Clerk
·	Docker

Author
Built as part of the SmartStay / Ttrip travel AI project.
