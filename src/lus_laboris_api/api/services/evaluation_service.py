"""
Servicio de evaluación asíncrona usando Phoenix Evals
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue

# Phoenix Evals imports
from phoenix.evals import (
    OpenAIModel,
    llm_classify,
    RAG_RELEVANCY_PROMPT_TEMPLATE,
    HALLUCINATION_PROMPT_TEMPLATE,
)

from ..config import settings
from .phoenix_service import phoenix_service

logger = logging.getLogger(__name__)


class EvaluationService:
    """Servicio para evaluación asíncrona de respuestas RAG usando Phoenix Evals"""
    
    def __init__(self):
        self.enabled = settings.api_phoenix_enabled
        self.evaluation_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="eval-worker")
        
        if self.enabled:
            self._initialize_evaluators()
            # Iniciar worker de evaluación
            self._start_evaluation_worker()
            logger.info("Evaluation service initialized with Phoenix Evals")
        else:
            logger.warning("Evaluation service disabled by configuration")
    
    def _initialize_evaluators(self):
        """Inicializar evaluadores de Phoenix"""
        try:
            # Configurar modelo para evaluaciones
            # Usar un modelo más económico para evaluaciones
            eval_model = "gpt-4o-mini" if settings.api_llm_provider == "openai" else "gpt-3.5-turbo"
            
            self.eval_model = OpenAIModel(
                model=eval_model,
                api_key=settings.openai_api_key
            )
            
            logger.info(f"Phoenix evaluators initialized with model: {eval_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize evaluators: {e}")
            self.enabled = False
    
    def _start_evaluation_worker(self):
        """Iniciar worker que procesa evaluaciones en background"""
        def worker():
            logger.info("Evaluation worker started")
            while True:
                try:
                    # Obtener tarea de evaluación de la cola
                    eval_task = self.evaluation_queue.get(timeout=1.0)
                    
                    if eval_task is None:  # Señal de shutdown
                        break
                    
                    # Ejecutar evaluación
                    self._run_evaluation(eval_task)
                    
                    self.evaluation_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in evaluation worker: {e}")
        
        # Iniciar worker en thread separado
        self.executor.submit(worker)
    
    def enqueue_evaluation(
        self,
        session_id: str,
        question: str,
        context: str,
        answer: str,
        documents: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Encolar evaluación para procesamiento asíncrono"""
        if not self.enabled:
            return
        
        eval_task = {
            "session_id": session_id,
            "question": question,
            "context": context,
            "answer": answer,
            "documents": documents,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.evaluation_queue.put(eval_task)
        logger.debug(f"Evaluation enqueued for session {session_id}")
    
    def _run_evaluation(self, eval_task: Dict[str, Any]):
        """Ejecutar evaluaciones de Phoenix Evals"""
        session_id = eval_task["session_id"]
        question = eval_task["question"]
        context = eval_task["context"]
        answer = eval_task["answer"]
        
        try:
            logger.info(f"Running evaluations for session {session_id}")
            
            # 1. Evaluación de Relevancia
            relevance_score = self._evaluate_relevance(question, context, answer)
            
            # 2. Evaluación de Alucinaciones
            hallucination_score = self._evaluate_hallucination(question, context, answer)
            
            # 3. Evaluación de Toxicidad (opcional)
            toxicity_score = self._evaluate_toxicity(answer)
            
            # Consolidar métricas
            evaluation_metrics = {
                "relevance": relevance_score,
                "hallucination": hallucination_score,
                "toxicity": toxicity_score,
                "grounding": 1.0 - hallucination_score if hallucination_score else None,
                "overall_quality": self._calculate_overall_quality(
                    relevance_score, hallucination_score, toxicity_score
                )
            }
            
            # Guardar métricas en Phoenix
            self._save_evaluation_to_phoenix(session_id, evaluation_metrics, eval_task)
            
            logger.info(f"Evaluation completed for session {session_id}: {evaluation_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to run evaluation for session {session_id}: {e}")
    
    def _evaluate_relevance(self, question: str, context: str, answer: str) -> Optional[float]:
        """Evaluar relevancia de la respuesta usando Phoenix Evals"""
        try:
            # Usar template de RAG relevancy de Phoenix
            result = llm_classify(
                dataframe=None,  # No usamos dataframe, evaluamos directamente
                model=self.eval_model,
                template=RAG_RELEVANCY_PROMPT_TEMPLATE,
                rails=["relevant", "irrelevant"],
                provide_explanation=True,
            )
            
            # Para una sola evaluación, construir manualmente
            prompt = RAG_RELEVANCY_PROMPT_TEMPLATE.format(
                query=question,
                reference=context,
                response=answer
            )
            
            # Evaluar
            eval_response = self.eval_model.invoke(prompt)
            
            # Parsear respuesta (Phoenix devuelve "relevant" o "irrelevant")
            if "relevant" in eval_response.lower():
                return 1.0
            elif "irrelevant" in eval_response.lower():
                return 0.0
            else:
                return 0.5  # Indeterminado
                
        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            return None
    
    def _evaluate_hallucination(self, question: str, context: str, answer: str) -> Optional[float]:
        """Evaluar alucinaciones usando Phoenix Evals"""
        try:
            # Usar template de hallucination de Phoenix
            prompt = HALLUCINATION_PROMPT_TEMPLATE.format(
                query=question,
                reference=context,
                response=answer
            )
            
            # Evaluar
            eval_response = self.eval_model.invoke(prompt)
            
            # Parsear respuesta (Phoenix devuelve "factual" o "hallucinated")
            if "factual" in eval_response.lower():
                return 0.0  # Sin alucinaciones
            elif "hallucinated" in eval_response.lower() or "hallucination" in eval_response.lower():
                return 1.0  # Alta alucinación
            else:
                return 0.5  # Indeterminado
                
        except Exception as e:
            logger.error(f"Hallucination evaluation failed: {e}")
            return None
    
    def _evaluate_toxicity(self, answer: str) -> Optional[float]:
        """Evaluar toxicidad de la respuesta"""
        try:
            # Template simple para toxicidad
            toxicity_prompt = f"""
            Evalúa si la siguiente respuesta contiene contenido tóxico, ofensivo o inapropiado.
            
            RESPUESTA: {answer}
            
            Responde solamente con "toxic" o "non-toxic".
            """
            
            eval_response = self.eval_model.invoke(toxicity_prompt)
            
            if "non-toxic" in eval_response.lower() or "non toxic" in eval_response.lower():
                return 0.0  # No tóxico
            elif "toxic" in eval_response.lower():
                return 1.0  # Tóxico
            else:
                return 0.0  # Default: no tóxico
                
        except Exception as e:
            logger.error(f"Toxicity evaluation failed: {e}")
            return None
    
    def _calculate_overall_quality(
        self,
        relevance: Optional[float],
        hallucination: Optional[float],
        toxicity: Optional[float]
    ) -> Optional[float]:
        """Calcular score de calidad general"""
        try:
            scores = []
            
            if relevance is not None:
                scores.append(relevance * 0.5)  # 50% peso
            
            if hallucination is not None:
                scores.append((1.0 - hallucination) * 0.4)  # 40% peso (invertido)
            
            if toxicity is not None:
                scores.append((1.0 - toxicity) * 0.1)  # 10% peso (invertido)
            
            if not scores:
                return None
            
            return sum(scores) / len(scores)
            
        except Exception as e:
            logger.error(f"Failed to calculate overall quality: {e}")
            return None
    
    def _save_evaluation_to_phoenix(
        self,
        session_id: str,
        metrics: Dict[str, Any],
        eval_task: Dict[str, Any]
    ):
        """Guardar métricas de evaluación en Phoenix"""
        try:
            # Track evaluación como operación de vectorstore
            phoenix_service.track_vectorstore_operation(
                session_id=session_id,
                operation_type="llm_evaluation",
                collection_name="evaluation_results",
                metadata={
                    "evaluation_type": "phoenix_evals",
                    "relevance_score": metrics.get("relevance"),
                    "hallucination_score": metrics.get("hallucination"),
                    "toxicity_score": metrics.get("toxicity"),
                    "grounding_score": metrics.get("grounding"),
                    "overall_quality_score": metrics.get("overall_quality"),
                    "question": eval_task["question"][:200],  # Truncar para no saturar
                    "answer_length": len(eval_task["answer"]),
                    "context_length": len(eval_task["context"]),
                    "documents_count": len(eval_task["documents"]),
                    "evaluation_timestamp": eval_task["timestamp"]
                }
            )
            
            logger.debug(f"Evaluation metrics saved to Phoenix for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save evaluation to Phoenix: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check del servicio de evaluación"""
        return {
            "status": "healthy" if self.enabled else "disabled",
            "phoenix_evals_available": True,
            "queue_size": self.evaluation_queue.qsize(),
            "enabled": self.enabled
        }
    
    def shutdown(self):
        """Shutdown graceful del servicio"""
        logger.info("Shutting down evaluation service...")
        
        # Señalar al worker que termine
        self.evaluation_queue.put(None)
        
        # Esperar a que termine el worker
        self.executor.shutdown(wait=True)
        
        logger.info("Evaluation service shut down")


# Global service instance
evaluation_service = EvaluationService()

