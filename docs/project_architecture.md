# Project Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Data Sources"
        A[Ley Nº 213<br/>Código del Trabajo<br/>Paraguay] --> B[Web Scraping<br/>BeautifulSoup]
    end
    
    subgraph "Data Processing"
        B --> C[Data Cleaning<br/>dlt + Python]
        C --> D[Text Segmentation<br/>Article Processing]
        D --> E[Metadata Enrichment<br/>Language & Area Classification]
    end
    
    subgraph "Storage Layer"
        E --> F[Google Cloud Storage<br/>Processed JSON Files]
        F --> G[Qdrant Vector Database<br/>Semantic Search Index]
    end
    
    subgraph "API Layer"
        G --> H[FastAPI REST API<br/>Query Interface]
        H --> I[OpenAI Integration<br/>LLM Processing]
    end
    
    subgraph "User Interface"
        I --> J[Web Application<br/>Question & Answer]
        J --> K[User Queries<br/>Labor Law Questions]
    end
    
    subgraph "Infrastructure"
        L[Terraform<br/>Infrastructure as Code] --> M[Google Cloud Platform<br/>Cloud Run + Storage]
        M --> F
        M --> H
    end
    
    subgraph "Monitoring & Evaluation"
        H --> N[Phoenix Monitoring<br/>Response Tracking]
        I --> O[RAG Evaluation<br/>Performance Metrics]
    end
    
    subgraph "Automation"
        P[GitHub Actions<br/>CI/CD Pipeline] --> Q[Automated Testing<br/>Deployment]
        Q --> M
    end
    
    style A fill:#e1f5fe
    style G fill:#f3e5f5
    style H fill:#e8f5e8
    style I fill:#fff3e0
    style L fill:#fce4ec
    style P fill:#f1f8e9
```

## Technology Stack

- **Data Extraction**: BeautifulSoup, Python
- **Data Processing**: dlt, Python
- **Storage**: Google Cloud Storage, Qdrant
- **API**: FastAPI, OpenAI
- **Infrastructure**: Terraform, Google Cloud Run
- **Monitoring**: Phoenix
- **Automation**: GitHub Actions
- **Package Management**: UV
