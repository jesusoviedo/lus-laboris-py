#!/usr/bin/env python3
"""
Generate GCP Infrastructure Diagram for Lus Laboris RAG Application
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.gcp.compute import GCE, Run
from diagrams.gcp.devtools import Scheduler
from diagrams.gcp.security import KMS
from diagrams.gcp.storage import GCS
from diagrams.onprem.iac import Terraform

# Graph attributes for better visualization
graph_attr = {
    "fontsize": "16",
    "bgcolor": "#F8FBFF",  # Very light blue background
    "fontcolor": "black",
    "pad": "0.5",
    "splines": "spline",  # Smooth splines
    "nodesep": "1.0",
    "ranksep": "1.8",
    "compound": "true",
}

# Cluster colors for GCP
cluster_gcp_attr = {
    "bgcolor": "white",
    "fontcolor": "black",
    "pencolor": "#4285F4",  # GCP blue border
    "style": "rounded",
    "labelloc": "t",
}

cluster_api_attr = {
    "bgcolor": "#E3F2FD",  # Light blue
    "fontcolor": "black",
    "pencolor": "#4285F4",
    "style": "rounded",
}

cluster_processing_attr = {
    "bgcolor": "#E1F5FE",  # Lighter blue
    "fontcolor": "black",
    "pencolor": "#0288D1",
    "style": "rounded",
}

cluster_automation_attr = {
    "bgcolor": "#F3E5F5",  # Light purple
    "fontcolor": "black",
    "pencolor": "#9C27B0",
    "style": "rounded",
}

cluster_storage_attr = {
    "bgcolor": "#E8F5E9",  # Light green
    "fontcolor": "black",
    "pencolor": "#34A853",
    "style": "rounded",
}

cluster_security_attr = {
    "bgcolor": "#FFF9E6",  # Light yellow
    "fontcolor": "black",
    "pencolor": "#FDB913",
    "style": "rounded",
}

cluster_database_attr = {
    "bgcolor": "#FFE0E0",  # Light red/orange
    "fontcolor": "black",
    "pencolor": "#FF6B35",
    "style": "rounded",
}

cluster_cloudrun_attr = {
    "bgcolor": "#E8F4FD",  # Very light blue
    "fontcolor": "black",
    "pencolor": "#1976D2",
    "style": "rounded",
}

cluster_batch_attr = {
    "bgcolor": "#F3E5F5",  # Light purple (for batch processing)
    "fontcolor": "black",
    "pencolor": "#7B1FA2",
    "style": "rounded",
}

cluster_apiservice_attr = {
    "bgcolor": "#E8F4FD",  # Light blue (for API service layer)
    "fontcolor": "black",
    "pencolor": "#1565C0",
    "style": "rounded",
}

cluster_data_attr = {
    "bgcolor": "#E8F5E9",  # Light green (for data layer)
    "fontcolor": "black",
    "pencolor": "#43A047",
    "style": "rounded",
}

# Diagram configuration
with Diagram(
    "GCP Infrastructure - Lus Laboris RAG",
    show=False,
    direction="LR",  # Left to Right
    graph_attr=graph_attr,
    filename="gcp-infrastructure",
):
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: INFRASTRUCTURE AS CODE (LEFT)
    # ═══════════════════════════════════════════════════════════

    terraform = Terraform("Terraform\n(Infrastructure as Code)")

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: GOOGLE CLOUD PLATFORM INFRASTRUCTURE (CENTER/RIGHT)
    # ═══════════════════════════════════════════════════════════

    with Cluster("Google Cloud Platform", graph_attr=cluster_gcp_attr):
        # Batch Processing Layer
        with Cluster("Batch Processing", graph_attr=cluster_batch_attr):
            scheduler = Scheduler("Cloud Scheduler\n(Daily 11 PM)")
            batch_job = Run("Cloud Run Job\nlabor-law-extractor")

        # Data Storage Layer
        with Cluster("Data Layer", graph_attr=cluster_data_attr):
            storage = GCS("Cloud Storage\npy-labor-law-rag")
            qdrant_vm = GCE("Compute Engine\nqdrant-vm")

        # API Service Layer
        with Cluster("API Service Layer", graph_attr=cluster_apiservice_attr):
            api_service = Run("Cloud Run Service\nlus-laboris-api")
            secrets = KMS("Secret Manager\n(.env + JWT)")

    # ═══════════════════════════════════════════════════════════
    # CONNECTIONS - PROVISIONING (from left)
    # ═══════════════════════════════════════════════════════════

    # 1. Terraform provisions all infrastructure (from left)
    (
        terraform
        >> Edge(label="provisions", fontsize="11")
        >> [api_service, batch_job, scheduler, storage, secrets, qdrant_vm]
    )

    # ═══════════════════════════════════════════════════════════
    # CONNECTIONS - GCP INTERNAL DATA FLOW
    # ═══════════════════════════════════════════════════════════

    # 2. Cloud Scheduler triggers Job
    scheduler >> Edge(label="triggers", fontsize="10") >> batch_job

    # 3. Processing Job interactions (writes to storage)
    batch_job >> Edge(label="writes", fontsize="10") >> storage

    # 4. API Service interactions (reads data)
    api_service >> Edge(label="reads", fontsize="10") >> storage
    api_service >> Edge(label="reads", fontsize="10") >> secrets
    api_service >> Edge(label="queries", fontsize="10") >> qdrant_vm
