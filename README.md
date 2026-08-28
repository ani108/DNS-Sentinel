# SIH DNS Security Project ![SIH Badge](https://img.shields.io/badge/SIH-2026-blue)

DNS Filtering Service using Threat Intelligence and AI/ML.

## Architecture

```mermaid
graph TD
    Client[Client Devices] -->|UDP Port 53| DNS[DNS Proxy Server]
    
    subgraph Core Engine
        DNS -->|Check cache| Redis[(Redis Cache)]
        DNS -->|Threat Check| Blocklist[Threat Intel Lists]
        DNS -->|Extract Features| ML[Random Forest ML Model]
        DNS -->|Time Window| Tunnel[DNS Tunneling Detector]
    end
    
    DNS -->|Allowed?| Upstream[Upstream DNS e.g. 1.1.1.1]
    Upstream -.->|Response| DNS
    DNS -.->|Filtered Response| Client
    
    subgraph Data Pipeline
        DNS -->|Pub/Sub Publish| Redis
        Redis -->|WebSocket Stream| FastAPI[FastAPI Backend]
        FastAPI -->|Save Query| Postgres[(PostgreSQL DB)]
    end
    
    subgraph Dashboard UI
        FastAPI <-->|REST API & WSS| React[React / Vite Frontend]
    end
```

## Tech Stack

| Component | Technology |
| --- | --- |
| Backend | Python 3.11, FastAPI, SQLAlchemy (Async) |
| Database | PostgreSQL, Redis |
| AI/ML | scikit-learn, XGBoost |
| DNS | dnslib, dnspython |
| Frontend | React / Next.js (Node.js) |
| Container | Docker, Docker Compose |

## Quick Start

```bash
docker-compose up --build
```

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
- `backend/`: FastAPI backend, ML models, and DNS server code.
- `frontend/`: React frontend for dashboard.
- `ml_training/`: Data and notebooks for model training.

## License
MIT
