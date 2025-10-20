#!/usr/bin/env python3
"""
CI/CD Pipeline Diagram Generator
Generates a visual representation of the GitHub Actions workflows and GCP deployment.
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.gcp.compute import GCE, Run
from diagrams.gcp.security import KMS
from diagrams.gcp.storage import GCS
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.iac import Terraform
from diagrams.onprem.vcs import Github

# Graph attributes for better visualization
graph_attr = {
    "fontsize": "16",
    "bgcolor": "#F5F5F5",  # Light gray background
    "fontcolor": "black",
    "pad": "0.5",
    "splines": "curved",  # Curved lines instead of straight
    "nodesep": "1.0",
    "ranksep": "1.5",
}

# Cluster colors for differentiation
cluster_github_attr = {
    "bgcolor": "#E8F4F8",  # Light blue
    "fontcolor": "black",
    "pencolor": "#4285F4",  # Blue border
    "style": "rounded",
}

cluster_gcp_attr = {
    "bgcolor": "#FFF4E6",  # Light orange/yellow
    "fontcolor": "black",
    "pencolor": "#FF9800",  # Orange border
    "style": "rounded",
}

cluster_sub_attr = {
    "bgcolor": "white",
    "fontcolor": "black",
    "style": "rounded",
}

# Diagram configuration
with Diagram(
    "CI/CD Pipeline - Lus Laboris",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    filename="cicd-pipeline",
):
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: DEVELOPER & TRIGGERS
    # ═══════════════════════════════════════════════════════════

    developer = User("Developer")
    git_push = Github("Git Push")
    manual_trigger = GithubActions("Manual Trigger\n(workflow_dispatch)")

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: GITHUB ACTIONS WORKFLOWS
    # ═══════════════════════════════════════════════════════════

    with Cluster("GitHub Actions CI/CD", graph_attr=cluster_github_attr):
        # --- Automated Workflows (triggered on push) ---
        with Cluster("Automated Workflows", graph_attr=cluster_sub_attr):
            code_quality = GithubActions("Code Quality\n(lint, test, scan)")
            build_api = Docker("Build API Image")
            build_processing = Docker("Build Processing Image")
            terraform_apply = Terraform("Terraform Apply\n(infrastructure)")

        # --- Docker Registry ---
        docker_hub = Docker("Docker Hub\n(Image Registry)")

        # --- Manual Deployment Workflows ---
        with Cluster("Deployment Workflows", graph_attr=cluster_sub_attr):
            deploy_qdrant = GithubActions("Deploy Qdrant")
            deploy_batch = GithubActions("Update Batch Job")
            deploy_api = GithubActions("Deploy API")

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: GOOGLE CLOUD PLATFORM
    # ═══════════════════════════════════════════════════════════

    with Cluster("Google Cloud Platform", graph_attr=cluster_gcp_attr):
        # Infrastructure Resources
        with Cluster("Infrastructure", graph_attr=cluster_sub_attr):
            gce_qdrant = GCE("Compute Engine\n(Qdrant VM)")
            gcs_storage = GCS("Cloud Storage\n(Data)")
            secret_mgr = KMS("Secret Manager\n(Keys & Env)")

        # Application Services
        with Cluster("Cloud Run Services", graph_attr=cluster_sub_attr):
            api_service = Run("API Service\n(FastAPI)")
            batch_job = Run("Batch Job\n(Processing)")

    # ═══════════════════════════════════════════════════════════
    # CONNECTIONS - SIMPLIFIED WORKFLOW
    # ═══════════════════════════════════════════════════════════

    # 1. Developer commits and pushes code
    developer >> Edge(label="code changes") >> git_push

    # 2. Git push triggers automated workflows (parallel)
    git_push >> Edge(label="triggers") >> code_quality
    git_push >> Edge(label="triggers") >> build_api
    git_push >> Edge(label="triggers") >> build_processing
    git_push >> Edge(label="triggers") >> terraform_apply

    # 3. Docker builds push images to Docker Hub
    build_api >> Edge(label="push") >> docker_hub
    build_processing >> Edge(label="push") >> docker_hub

    # 4. Terraform provisions ALL GCP infrastructure
    (
        terraform_apply
        >> Edge(label="provision")
        >> [gce_qdrant, gcs_storage, secret_mgr, api_service, batch_job]
    )

    # 5. Manual deployment trigger
    developer >> Edge(label="manual") >> manual_trigger
    manual_trigger >> Edge(label="initiates") >> [deploy_qdrant, deploy_batch, deploy_api]

    # 6. Deployment workflows pull images from Docker Hub
    docker_hub >> Edge(label="pull image") >> deploy_qdrant
    docker_hub >> Edge(label="pull image") >> deploy_batch
    docker_hub >> Edge(label="pull image") >> deploy_api

    # 7. Each deployment workflow targets specific GCP service
    deploy_qdrant >> Edge(label="deploy") >> gce_qdrant
    deploy_batch >> Edge(label="update") >> batch_job
    deploy_api >> Edge(label="deploy") >> api_service
