# lus-laboris-py

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-FF6B6B?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![DLT](https://img.shields.io/badge/DLT-FF6B35?style=for-the-badge&logo=data&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B35?style=for-the-badge&logo=qdrant&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Phoenix](https://img.shields.io/badge/Phoenix-FF7100?style=for-the-badge&logo=phoenixframework&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

## Description

This project implements a RAG (Retrieval-Augmented Generation) application over Law Nº 213 that Establishes the Labor Code of Paraguay. The main workflow is:

- **Extraction**: Download and store the original law text.
- **Processing**: Use dlt and Python to clean, segment, and enrich the legal text.
- **Storage**: Save the processed file in a Google Cloud Storage (GGS) bucket.
- **Indexing**: Load the processed data into a Qdrant vector database, applying indexing models by language and area, and adding metadata for efficient filtering.
- **Retrieval & Response**: Use OpenAI as the LLM and a specialized prompt to answer user questions about the law, via a REST API built with FastAPI and Pydantic.
- **Evaluation**: Comprehensive evaluation of the RAG application, including prompts, indexing models, and the RAG system itself.
- **Monitoring**: Application and response monitoring using Phoenix.
- **Cloud Deployment**: Google Cloud Run is used both to run the batch process that loads Qdrant and to deploy the FastAPI API that extracts information from the vector database.
- **Automation**: GitHub Actions is used to automate key project processes such as testing, deployment, and CI tasks.

The project is organized in folders such as:
- `data/raw/` — Original downloaded law
- `data/processed/` — Processed law ready for indexing
- `src/processing/` — Extraction and processing scripts
- `src/api/` — REST API with FastAPI
- `src/vectorstore/` — Scripts for loading and managing Qdrant
- `notebooks/` — Documentation and experiments
- `evaluation/` — Scripts and notebooks for RAG application evaluation
- `monitoring/` — Scripts and configuration for monitoring with Phoenix
- `deploy/` — Deployment and configuration files for Google Cloud Run
- `.github/workflows/` — GitHub Actions workflows for automation

## Project Structure

```
lus-laboris-py/
├── data/                   # Data directory
│   ├── raw/               # Original, unprocessed data
│   └── processed/         # Cleaned and processed data
├── deploy/                # Deployment and configuration files
├── evaluation/            # RAG application evaluation scripts
├── monitoring/            # Monitoring and observability scripts
├── notebooks/             # Jupyter notebooks for analysis
│   ├── 01_data_extraction.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── uv.lock
├── src/                   # Main source code
│   ├── api/               # FastAPI REST API implementation
│   ├── core/              # Core functionalities and business logic
│   ├── processing/        # Data extraction and processing scripts
│   └── vectorstore/       # Qdrant vector database scripts
├── tests/                 # Unit and integration tests
├── .github/workflows/     # GitHub Actions workflows
├── LICENSE                # Project license
├── README.md              # This file
└── README_ES.md           # Spanish version of this file
```

## Directory Overview

- **`data/`**: Stores all project data, with subdirectories for raw and processed files.
- **`deploy/`**: Contains deployment guides, Dockerfiles, and configuration files for Google Cloud.
- **`evaluation/`**: Scripts and notebooks for evaluating the RAG application's performance.
- **`monitoring/`**: Scripts and configuration for application monitoring and observability.
- **`notebooks/`**: Jupyter notebooks for experimentation, analysis, and documentation.
- **`src/api/`**: FastAPI REST API implementation for exposing project functionalities.
- **`src/core/`**: Core functionalities and business logic of the project.
- **`src/processing/`**: Scripts for data extraction, cleaning, and processing.
- **`src/vectorstore/`**: Scripts for loading, managing, and querying the Qdrant vector database.
- **`tests/`**: Unit and integration tests to ensure code quality and correctness.

## Features

- **Data Extraction**: Tools for extracting information from web sources
- **Data Analysis**: Jupyter notebooks for interactive analysis
- **API**: Modules for creating web services with FastAPI
- **Processing**: Core functionalities for data processing

## Requirements

- Python 3.13
- uv (dependency manager)
- FastAPI
- Main dependencies:
  - beautifulsoup4 >= 4.13.5
  - notebook >= 7.4.5

## Installation

1. Install uv if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

3. Install dependencies with uv:
```bash
uv sync
```

## Usage

### Running Notebooks

To run the analysis notebooks:

```bash
cd notebooks
uv run jupyter notebook
```

### Using the API

```python
from src.api import your_module
# Your code here
```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

Jesus Oviedo Riquelme - j92riquelme@gmail.com - [LinkedIn](https://www.linkedin.com/in/jesusoviedoriquelme)

Project Link: [https://github.com/jesusoviedo/lus-laboris-py](https://github.com/jesusoviedo/lus-laboris-py)
