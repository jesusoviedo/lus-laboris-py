"""
Servicio de monitoreo con Phoenix para tracking de LLM y métricas de calidad
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

from openinference.instrumentation.openai import OpenAIInstrumentor

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import SpanKind, Status, StatusCode

# Phoenix imports
from phoenix.otel import register

from ..config import settings

OPENAI_INSTRUMENTOR_AVAILABLE = True

logger = logging.getLogger(__name__)


class PhoenixMonitoringService:
    """Servicio de monitoreo con Phoenix para tracking de LLM y métricas"""

    def __init__(self):
        self.project_name = settings.api_phoenix_project_name
        self.enabled = settings.api_phoenix_enabled
        self.session_tracker = {}
        self.tracer = None

        if self.enabled:
            self._initialize_phoenix()
        else:
            logger.info("Phoenix monitoring disabled by configuration")

    def _initialize_phoenix(self):
        """Initialize Phoenix with project configuration"""
        try:
            # Get configuration from settings (centralized)
            is_production = settings.api_environment.lower() == "production"
            phoenix_endpoint = settings.api_phoenix_endpoint or "http://localhost:6006"
            use_grpc = settings.api_phoenix_use_grpc
            grpc_endpoint = settings.api_phoenix_grpc_endpoint

            # If gRPC is enabled, use gRPC endpoint
            if use_grpc and grpc_endpoint:
                logger.info("Attempting to connect to Phoenix via gRPC at {grpc_endpoint}")

                # Register Phoenix with gRPC endpoint
                self.tracer_provider = register(
                    project_name=self.project_name,
                    auto_instrument=True,
                    endpoint=f"grpc://{grpc_endpoint}",  # Use gRPC protocol
                    api_key=settings.api_phoenix_api_key,
                    batch=is_production,
                )

                transport = "gRPC"
            else:
                # Fallback to HTTP
                logger.info("Connecting to Phoenix via HTTP at {phoenix_endpoint}")

                self.tracer_provider = register(
                    project_name=self.project_name,
                    auto_instrument=True,
                    endpoint=phoenix_endpoint,
                    api_key=settings.api_phoenix_api_key,
                    batch=is_production,
                )

                transport = "HTTP"

            # Get tracer
            self.tracer = trace.get_tracer(__name__)

            # Initialize OpenInference instrumentors
            self._initialize_openinference_instrumentors()

            processor_type = "BatchSpanProcessor" if is_production else "SimpleSpanProcessor"
            logger.info("Phoenix monitoring initialized for project: {self.project_name}")
            logger.info("Using {processor_type} (environment: {settings.api_environment})")
            logger.info(
                "Transport: {transport} - {'Optimized for performance' if transport == 'gRPC' else 'Standard HTTP'}"
            )

        except Exception as e:
            logger.exception("Failed to initialize Phoenix with gRPC, falling back to HTTP")

            # Fallback to HTTP if gRPC fails
            try:
                phoenix_endpoint = settings.api_phoenix_endpoint or "http://localhost:6006"
                is_production = settings.api_environment.lower() == "production"

                self.tracer_provider = register(
                    project_name=self.project_name,
                    auto_instrument=True,
                    endpoint=phoenix_endpoint,
                    api_key=settings.api_phoenix_api_key,
                    batch=is_production,
                )
                self.tracer = trace.get_tracer(__name__)
                logger.warning("Fell back to HTTP transport for Phoenix")
            except Exception as e2:
                logger.exception("Failed to initialize Phoenix even with HTTP")
                self.enabled = False

    def _initialize_openinference_instrumentors(self):
        """Initialize OpenInference instrumentors for automatic LLM tracking"""
        try:
            # Instrument OpenAI
            if OPENAI_INSTRUMENTOR_AVAILABLE:
                OpenAIInstrumentor().instrument()
                logger.info("✅ OpenInference: OpenAI instrumented successfully")
            else:
                logger.warning("⚠️ OpenInference: OpenAI instrumentor not available")

            # Note: google-genai (Gemini AI Studio) doesn't have OpenInference instrumentor yet
            # Using manual instrumentation via track_llm_call() for Gemini
            logger.info(
                "ℹ️ OpenInference: Gemini uses manual instrumentation (google-genai not supported yet)"
            )

        except Exception as e:
            logger.exception("Failed to initialize OpenInference instrumentors")
            logger.info("Continuing with manual instrumentation only")

    def create_session(self, user_id: str | None = None) -> str:
        """Crear una nueva sesión de monitoreo"""
        session_id = str(uuid.uuid4())

        self.session_tracker[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": datetime.now(),
            "actions": [],
            "llm_calls": [],
            "metrics": {},
        }

        logger.info("Created monitoring session: {session_id}")
        return session_id

    def end_session(self, session_id: str) -> dict[str, Any]:
        """Finalizar una sesión y calcular métricas finales"""
        if session_id not in self.session_tracker:
            logger.warning("Session {session_id} not found")
            return {}

        session_data = self.session_tracker[session_id]
        session_data["end_time"] = datetime.now()
        session_data["duration"] = (
            session_data["end_time"] - session_data["start_time"]
        ).total_seconds()

        # Calcular métricas de sesión
        session_metrics = self._calculate_session_metrics(session_data)
        session_data["final_metrics"] = session_metrics

        logger.info("Session {session_id} ended. Duration: {session_data['duration']:.2f}s")

        # Limpiar sesión después de un tiempo
        del self.session_tracker[session_id]

        return session_data

    def _serialize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Serialize complex metadata values to OpenTelemetry-compatible types.

        OpenTelemetry only accepts: bool, str, bytes, int, float, or sequences of those.
        This function converts dicts and other complex types to JSON strings.
        """
        serialized = {}
        for key, value in metadata.items():
            if isinstance(value, bool | str | bytes | int | float):
                # Primitive types: use as-is
                serialized[key] = value
            elif isinstance(value, list | tuple):
                # Sequences: convert to string if they contain complex types
                try:
                    # Try to keep as list if all elements are primitive
                    if all(isinstance(item, bool | str | bytes | int | float) for item in value):
                        serialized[key] = list(value)
                    else:
                        serialized[key] = json.dumps(value)
                except Exception:
                    serialized[key] = json.dumps(value)
            elif isinstance(value, dict):
                # Dicts: convert to JSON string
                serialized[key] = json.dumps(value)
            elif value is None:
                # None: convert to string
                serialized[key] = "null"
            else:
                # Other types: convert to string
                serialized[key] = str(value)

        return serialized

    def track_llm_call(
        self,
        session_id: str,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trackear una llamada a LLM (OpenAI o Gemini)"""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(
                name=f"llm_call_{provider}_{model}",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    ResourceAttributes.SERVICE_VERSION: "1.0.0",
                    "llm.provider": provider,
                    "llm.model": model,
                    "llm.prompt_length": len(prompt),
                    "llm.response_length": len(response),
                    "session.id": session_id,
                    **self._get_session_attributes(session_id),
                },
            ) as span:
                # Registrar datos de la llamada LLM
                llm_call_data = {
                    "timestamp": datetime.now(),
                    "provider": provider,
                    "model": model,
                    "prompt": prompt,
                    "response": response,
                    "metadata": metadata or {},
                }

                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["llm_calls"].append(llm_call_data)
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "llm_call",
                            "timestamp": datetime.now(),
                            "provider": provider,
                            "model": model,
                        }
                    )

                # Evaluate calidad de la respuesta
                quality_metrics = self._evaluate_response_quality(prompt, response)

                # Agregar métricas al span
                span.set_attributes(
                    {
                        "llm.quality.coherence": quality_metrics.get("coherence", 0),
                        "llm.quality.relevance": quality_metrics.get("relevance", 0),
                        "llm.quality.completeness": quality_metrics.get("completeness", 0),
                    }
                )

                span.set_status(Status(StatusCode.OK))

                logger.info("Tracked LLM call: {provider}/{model} for session {session_id}")

        except Exception as e:
            logger.exception("Failed to track LLM call")

    def track_vectorstore_search(
        self,
        session_id: str,
        query: str,
        results_count: int,
        search_time: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trackear una búsqueda en vectorstore (Qdrant)"""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(
                name="vectorstore_search",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    "vectorstore.query_length": len(query),
                    "vectorstore.results_count": results_count,
                    "vectorstore.search_time": search_time,
                    "session.id": session_id,
                    **self._get_session_attributes(session_id),
                },
            ) as span:
                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "vectorstore_search",
                            "timestamp": datetime.now(),
                            "query": query,
                            "results_count": results_count,
                            "search_time": search_time,
                            "metadata": metadata,
                        }
                    )

                span.set_status(Status(StatusCode.OK))

                logger.info("Tracked vectorstore search for session {session_id}")

        except Exception as e:
            logger.exception("Failed to track vectorstore search")

    def track_embedding_generation(
        self,
        session_id: str,
        text: str,
        model: str,
        generation_time: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trackear generación de embeddings"""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(
                name="embedding_generation",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    "embedding.model": model,
                    "embedding.text_length": len(text),
                    "embedding.generation_time": generation_time,
                    "session.id": session_id,
                    **self._get_session_attributes(session_id),
                },
            ) as span:
                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "embedding_generation",
                            "timestamp": datetime.now(),
                            "text": text,
                            "model": model,
                            "generation_time": generation_time,
                            "metadata": metadata,
                        }
                    )

                span.set_status(Status(StatusCode.OK))

                logger.info("Tracked embedding generation for session {session_id}")

        except Exception as e:
            logger.exception("Failed to track embedding generation")

    def track_vectorstore_operation(
        self,
        session_id: str,
        operation_type: str,
        collection_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track vectorstore operations (load, delete, etc.)"""
        if not self.enabled:
            return

        try:
            # Serialize complex metadata to OpenTelemetry-compatible types
            serialized_metadata = self._serialize_metadata(metadata or {})

            # Get session attributes and serialize them too
            session_attrs = self._serialize_metadata(self._get_session_attributes(session_id))

            with self.tracer.start_as_current_span(
                name=f"vectorstore_{operation_type}",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    "vectorstore.operation": operation_type,
                    "vectorstore.collection": collection_name,
                    "session.id": session_id,
                    **session_attrs,
                    **serialized_metadata,
                },
            ) as span:
                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "vectorstore_operation",
                            "operation": operation_type,
                            "timestamp": datetime.now(),
                            "collection": collection_name,
                            "metadata": metadata or {},
                        }
                    )

                span.set_status(Status(StatusCode.OK))

                logger.debug(
                    "Tracked vectorstore operation '{operation_type}' for session {session_id}"
                )

        except Exception as e:
            logger.exception("Failed to track vectorstore operation")

    def track_reranking(
        self,
        session_id: str,
        query: str,
        documents_count: int,
        reranking_time: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trackear proceso de reranking"""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(
                name="document_reranking",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    "reranking.query_length": len(query),
                    "reranking.documents_count": documents_count,
                    "reranking.time": reranking_time,
                    "session.id": session_id,
                    **self._get_session_attributes(session_id),
                },
            ) as span:
                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "reranking",
                            "timestamp": datetime.now(),
                            "query": query,
                            "documents_count": documents_count,
                            "reranking_time": reranking_time,
                            "metadata": metadata,
                        }
                    )

                span.set_status(Status(StatusCode.OK))

                logger.info("Tracked reranking for session {session_id}")

        except Exception as e:
            logger.exception("Failed to track reranking")

    def track_authentication(
        self,
        session_id: str,
        user_id: str | None,
        success: bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trackear autenticación JWT"""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(
                name="jwt_authentication",
                kind=SpanKind.CLIENT,
                attributes={
                    "service.name": "lus-laboris-api",
                    "auth.success": success,
                    "auth.user_id": user_id or "anonymous",
                    "session.id": session_id,
                    **self._get_session_attributes(session_id),
                },
            ) as span:
                # Agregar a la sesión
                if session_id in self.session_tracker:
                    self.session_tracker[session_id]["actions"].append(
                        {
                            "type": "authentication",
                            "timestamp": datetime.now(),
                            "user_id": user_id,
                            "success": success,
                            "metadata": metadata,
                        }
                    )

                status = Status(StatusCode.OK) if success else Status(StatusCode.ERROR)
                span.set_status(status)

                logger.info("Tracked authentication for session {session_id}")

        except Exception as e:
            logger.exception("Failed to track authentication")

    def _get_session_attributes(self, session_id: str) -> dict[str, Any]:
        """Obtener atributos de la sesión para el span"""
        if session_id not in self.session_tracker:
            return {}

        session_data = self.session_tracker[session_id]
        return {
            "session.user_id": session_data.get("user_id"),
            "session.start_time": session_data["start_time"].isoformat(),
            "session.actions_count": len(session_data["actions"]),
            "session.llm_calls_count": len(session_data["llm_calls"]),
        }

    def _evaluate_response_quality(self, prompt: str, response: str) -> dict[str, float]:
        """Evaluar calidad de la respuesta del LLM"""
        try:
            # Métricas básicas de calidad
            metrics = {}

            # Coherencia: longitud de respuesta vs prompt
            prompt_length = len(prompt.split())
            response_length = len(response.split())
            metrics["coherence"] = min(response_length / max(prompt_length, 1), 2.0) / 2.0

            # Relevancia: presencia de palabras clave del prompt en la respuesta
            prompt_words = set(prompt.lower().split())
            response_words = set(response.lower().split())
            if prompt_words:
                metrics["relevance"] = len(prompt_words.intersection(response_words)) / len(
                    prompt_words
                )
            else:
                metrics["relevance"] = 0.0

            # Completitud: longitud de respuesta
            metrics["completeness"] = min(len(response) / 1000, 1.0)  # Normalizar a 1000 caracteres

            return metrics

        except Exception as e:
            logger.exception("Failed to evaluate response quality")
            return {"coherence": 0.0, "relevance": 0.0, "completeness": 0.0}

    def _calculate_session_metrics(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """Calcular métricas finales de la sesión"""
        try:
            metrics = {
                "total_actions": len(session_data["actions"]),
                "llm_calls_count": len(session_data["llm_calls"]),
                "duration_seconds": session_data["duration"],
                "actions_per_minute": len(session_data["actions"])
                / max(session_data["duration"] / 60, 1),
            }

            # Métricas de LLM
            if session_data["llm_calls"]:
                llm_calls = session_data["llm_calls"]
                metrics["llm"] = {
                    "total_calls": len(llm_calls),
                    "providers_used": list({call["provider"] for call in llm_calls}),
                    "models_used": list({call["model"] for call in llm_calls}),
                    "avg_response_length": sum(len(call["response"]) for call in llm_calls)
                    / len(llm_calls),
                }

            # Métricas por tipo de acción
            action_types = {}
            for action in session_data["actions"]:
                action_type = action["type"]
                if action_type not in action_types:
                    action_types[action_type] = 0
                action_types[action_type] += 1

            metrics["action_types"] = action_types

            return metrics

        except Exception as e:
            logger.exception("Failed to calculate session metrics")
            return {}

    def health_check(self) -> dict[str, Any]:
        """
        Check Phoenix monitoring service health

        Returns basic status without authentication, detailed status with authentication.
        """
        try:
            if not self.enabled:
                return {
                    "status": "disabled",
                    "message": "Phoenix monitoring is disabled in configuration",
                }

            # Basic check: verify tracer is available
            if not self.tracer:
                return {"status": "unhealthy", "error": "Tracer not initialized"}

            # Get basic status
            basic_status = {
                "status": "healthy",
                "project_name": self.project_name,
                "active_sessions": len(self.session_tracker),
                "total_llm_calls": sum(
                    len(s.get("llm_calls", [])) for s in self.session_tracker.values()
                ),
                "total_actions": sum(
                    len(s.get("actions", [])) for s in self.session_tracker.values()
                ),
            }

            return basic_status

        except Exception as e:
            logger.exception("Phoenix health check failed")
            return {"status": "unhealthy", "error": str(e)}

    def health_check_extended(self) -> dict[str, Any]:
        """
        Extended health check with connection test to Phoenix collector

        This should only be called with authentication as it performs
        active connection testing.
        """
        try:
            basic_health = self.health_check()

            if basic_health.get("status") != "healthy":
                return basic_health

            # Perform connection test by creating a test span
            test_session_id = "health-check-test"

            try:
                # Create a test span to verify connection
                with self.tracer.start_as_current_span(
                    name="phoenix_health_check_test",
                    kind=SpanKind.INTERNAL,
                    attributes={
                        "health_check": True,
                        "test_type": "connection_verification",
                        "session.id": test_session_id,
                    },
                ) as span:
                    span.set_status(Status(StatusCode.OK))
                    span.add_event("Health check test completed")

                # If we got here, connection is working
                basic_health["phoenix_connection"] = "verified"
                basic_health["collector_reachable"] = True

            except Exception as conn_error:
                logger.warning("Phoenix connection test failed: {conn_error}")
                basic_health["phoenix_connection"] = "degraded"
                basic_health["collector_reachable"] = False
                basic_health["connection_error"] = str(conn_error)

            return basic_health

        except Exception as e:
            logger.exception("Phoenix extended health check failed")
            return {"status": "unhealthy", "error": str(e)}


# Instancia global del servicio de monitoreo
phoenix_service = PhoenixMonitoringService()
