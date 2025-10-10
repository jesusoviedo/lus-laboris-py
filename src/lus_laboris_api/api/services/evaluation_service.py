"""
Asynchronous evaluation service using Phoenix Evals
"""
import logging
import asyncio
import time
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
    """Service for asynchronous RAG response evaluation using Phoenix Evals"""
    
    def __init__(self):
        self.enabled = settings.api_phoenix_enabled
        self.evaluation_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="eval-worker")
        
        if self.enabled:
            self._initialize_evaluators()
            # Start evaluation worker
            self._start_evaluation_worker()
            logger.info("Evaluation service initialized with Phoenix Evals")
        else:
            logger.warning("Evaluation service disabled by configuration")
    
    def _initialize_evaluators(self):
        """Initialize Phoenix evaluators"""
        try:
            # Configure model for evaluations
            # Use a cost-effective model for evaluations
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
        """Start worker that processes evaluations in background"""
        def worker():
            logger.info("Evaluation worker started")
            while True:
                try:
                    # Get evaluation task from queue
                    eval_task = self.evaluation_queue.get(timeout=1.0)
                    
                    if eval_task is None:  # Shutdown signal
                        break
                    
                    # Execute evaluation
                    self._run_evaluation(eval_task)
                    
                    self.evaluation_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in evaluation worker: {e}")
        
        # Start worker in separate thread
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
        """Enqueue evaluation for asynchronous processing"""
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
        """Execute Phoenix Evals evaluations (runs async loop)"""
        # Run async evaluation in an event loop
        import asyncio
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._run_evaluation_async(eval_task))
        finally:
            loop.close()
    
    async def _run_evaluation_async(self, eval_task: Dict[str, Any]):
        """Execute Phoenix Evals evaluations in parallel (OPTIMIZED)"""
        session_id = eval_task["session_id"]
        question = eval_task["question"]
        context = eval_task["context"]
        answer = eval_task["answer"]
        
        try:
            logger.info(f"Running parallel evaluations for session {session_id}")
            
            # ✅ OPTIMIZATION: Run all 3 evaluations in parallel
            start_time = time.time()
            
            evaluation_results = await asyncio.gather(
                asyncio.to_thread(self._evaluate_relevance, question, context, answer),
                asyncio.to_thread(self._evaluate_hallucination, question, context, answer),
                asyncio.to_thread(self._evaluate_toxicity, answer),
                return_exceptions=True  # Don't fail if one evaluation fails
            )
            
            eval_time = time.time() - start_time
            
            # Extract results
            relevance_score = evaluation_results[0] if not isinstance(evaluation_results[0], Exception) else None
            hallucination_score = evaluation_results[1] if not isinstance(evaluation_results[1], Exception) else None
            toxicity_score = evaluation_results[2] if not isinstance(evaluation_results[2], Exception) else None
            
            # Consolidate metrics
            evaluation_metrics = {
                "relevance": relevance_score,
                "hallucination": hallucination_score,
                "toxicity": toxicity_score,
                "grounding": 1.0 - hallucination_score if hallucination_score is not None else None,
                "overall_quality": self._calculate_overall_quality(
                    relevance_score, hallucination_score, toxicity_score
                ),
                "evaluation_time_seconds": eval_time
            }
            
            # Save metrics to Phoenix
            self._save_evaluation_to_phoenix(session_id, evaluation_metrics, eval_task)
            
            logger.info(f"Parallel evaluation completed for session {session_id} in {eval_time:.2f}s: {evaluation_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to run evaluation for session {session_id}: {e}")
    
    def _evaluate_relevance(self, question: str, context: str, answer: str) -> Optional[float]:
        """Evaluate response relevance using Phoenix Evals"""
        try:
            # Format prompt with dict of variables (ClassificationTemplate expects dict)
            # Note: Template is in English but content (question, context) is in Spanish
            # OpenAI models handle multilingual content well
            variable_values = {
                "input": question,  # Spanish question
                "reference": context  # Spanish context
            }
            prompt = RAG_RELEVANCY_PROMPT_TEMPLATE.format(variable_values)
            
            # Call model directly (it's callable)
            eval_response = self.eval_model(prompt)
            
            # Parse response (Phoenix returns "relevant" or "irrelevant")
            if eval_response and "relevant" in eval_response.lower():
                return 1.0
            elif eval_response and "irrelevant" in eval_response.lower():
                return 0.0
            else:
                return 0.5  # Indeterminate
                
        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            return None
    
    def _evaluate_hallucination(self, question: str, context: str, answer: str) -> Optional[float]:
        """Evaluate hallucinations using Phoenix Evals"""
        try:
            # Format prompt with dict of variables (ClassificationTemplate expects dict)
            # Note: Template is in English but content is in Spanish
            # OpenAI models handle multilingual content well
            variable_values = {
                "input": question,  # Spanish question
                "reference": context,  # Spanish context
                "output": answer  # Spanish answer
            }
            prompt = HALLUCINATION_PROMPT_TEMPLATE.format(variable_values)
            
            # Call model directly (it's callable)
            eval_response = self.eval_model(prompt)
            
            # Parse response (Phoenix returns "factual" or "hallucinated")
            if eval_response and "factual" in eval_response.lower():
                return 0.0  # No hallucinations
            elif eval_response and ("hallucinated" in eval_response.lower() or "hallucination" in eval_response.lower()):
                return 1.0  # High hallucination
            else:
                return 0.5  # Indeterminate
                
        except Exception as e:
            logger.error(f"Hallucination evaluation failed: {e}")
            return None
    
    def _evaluate_toxicity(self, answer: str) -> Optional[float]:
        """Evaluate response toxicity"""
        try:
            # Prompt in Spanish for toxicity evaluation
            toxicity_prompt = f"""
            Evalúa si la siguiente respuesta contiene contenido tóxico, ofensivo o inapropiado.
            
            RESPUESTA: {answer}
            
            Responde únicamente con "tóxico" o "no-tóxico".
            """
            
            # Call model directly (it's callable)
            eval_response = self.eval_model(toxicity_prompt)
            
            if eval_response and ("no-tóxico" in eval_response.lower() or "no toxico" in eval_response.lower() or "no tóxico" in eval_response.lower()):
                return 0.0  # Non-toxic
            elif eval_response and ("tóxico" in eval_response.lower() or "toxico" in eval_response.lower()):
                return 1.0  # Toxic
            else:
                return 0.0  # Default: non-toxic
                
        except Exception as e:
            logger.error(f"Toxicity evaluation failed: {e}")
            return None
    
    def _calculate_overall_quality(
        self,
        relevance: Optional[float],
        hallucination: Optional[float],
        toxicity: Optional[float]
    ) -> Optional[float]:
        """Calculate overall quality score with weighted average"""
        try:
            # Calculate weighted scores
            total_score = 0.0
            total_weight = 0.0
            
            if relevance is not None:
                total_score += relevance * 0.5  # 50% weight
                total_weight += 0.5
            
            if hallucination is not None:
                total_score += (1.0 - hallucination) * 0.4  # 40% weight (inverted: 0=good)
                total_weight += 0.4
            
            if toxicity is not None:
                total_score += (1.0 - toxicity) * 0.1  # 10% weight (inverted: 0=good)
                total_weight += 0.1
            
            if total_weight == 0:
                return None
            
            # Normalize by actual total weight (in case some metrics are missing)
            return total_score / total_weight
            
        except Exception as e:
            logger.error(f"Failed to calculate overall quality: {e}")
            return None
    
    def _save_evaluation_to_phoenix(
        self,
        session_id: str,
        metrics: Dict[str, Any],
        eval_task: Dict[str, Any]
    ):
        """Save evaluation metrics to Phoenix"""
        try:
            # Track evaluation as vectorstore operation
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
                    "question": eval_task["question"][:200],  # Truncate to avoid overflow
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
        """Health check for evaluation service"""
        return {
            "status": "healthy" if self.enabled else "disabled",
            "phoenix_evals_available": True,
            "queue_size": self.evaluation_queue.qsize(),
            "enabled": self.enabled
        }
    
    def shutdown(self):
        """Graceful shutdown of the service"""
        logger.info("Shutting down evaluation service...")
        
        # Signal worker to terminate
        self.evaluation_queue.put(None)
        
        # Wait a que termine el worker
        self.executor.shutdown(wait=True)
        
        logger.info("Evaluation service shut down")


# Global service instance
evaluation_service = EvaluationService()

