from abc import ABC, abstractmethod
from langchain_ollama.llms import OllamaLLM as Ollama
from langchain_ollama import OllamaEmbeddings
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    ContextRelevance,
    AnswerCorrectness,
)
from ragas import evaluate
from datasets import Dataset

# Abstract base class for LLMs
class LLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# Concrete implementation for Ollama
class OllamaLLM(LLM):
    def __init__(self, model_name="llama2"):
        self.llm = Ollama(model=model_name)
        # Use a local embedding model from Ollama
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt)

# Factory to switch between LLMs
class LLMFactory:
    @staticmethod
    def get_llm(llm_type="ollama", **kwargs):
        if llm_type == "ollama":
            return OllamaLLM(**kwargs)
        # Future LLMs can be added here
        # elif llm_type == "openai":
        #     return OpenAILLM(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

# Ragas evaluator class
class RagasEvaluator:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.metrics = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_recall": context_recall,
            "context_precision": context_precision,
            "context_relevance": ContextRelevance(),
            "answer_correctness": AnswerCorrectness(),
        }

    def _evaluate(self, dataset: Dataset, metrics: list):
        """Helper to run evaluation."""
        return evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=self.llm.llm,
            embeddings=self.llm.embeddings
        )

    def evaluate_faithfulness(self, question: str, answer: str, contexts: list[str]):
        dataset = Dataset.from_dict({"question": [question], "answer": [answer], "contexts": [contexts]})
        return self._evaluate(dataset, [self.metrics["faithfulness"]])

    def evaluate_answer_relevancy(self, question: str, answer: str, contexts: list[str]):
        dataset = Dataset.from_dict({"question": [question], "answer": [answer], "contexts": [contexts]})
        return self._evaluate(dataset, [self.metrics["answer_relevancy"]])

    def evaluate_context_recall(self, question: str, contexts: list[str], ground_truth: str):
        dataset = Dataset.from_dict({"question": [question], "contexts": [contexts], "ground_truth": [ground_truth]})
        return self._evaluate(dataset, [self.metrics["context_recall"]])

    def evaluate_context_precision(self, question: str, contexts: list[str], ground_truth: str):
        dataset = Dataset.from_dict({"question": [question], "contexts": [contexts], "ground_truth": [ground_truth]})
        return self._evaluate(dataset, [self.metrics["context_precision"]])

    def evaluate_context_relevance(self, question: str, contexts: list[str]):
        """
        Evaluates the relevance of the retrieved context to the question.
        """
        dataset = Dataset.from_dict({"question": [question], "contexts": [contexts]})
        return self._evaluate(dataset, [self.metrics["context_relevance"]])

    def evaluate_answer_correctness(self, question: str, answer: str, ground_truth: str):
        """
        Evaluates the factual correctness of the answer compared to a ground truth.
        """
        dataset = Dataset.from_dict({"question": [question], "answer": [answer], "ground_truth": [ground_truth]})
        return self._evaluate(dataset, [self.metrics["answer_correctness"]])

    def evaluate_all(self, question: str, answer: str, contexts: list[str], ground_truth: str):
        dataset = Dataset.from_dict({
            "question": [question], 
            "answer": [answer], 
            "contexts": [contexts],
            "ground_truth": [ground_truth]
        })
        # Evaluate all metrics except those that might be missing
        metrics_to_run = [
            self.metrics["faithfulness"],
            self.metrics["answer_relevancy"],
            self.metrics["context_recall"],
            self.metrics["context_precision"],
            self.metrics["context_relevance"],
            self.metrics["answer_correctness"],
        ]
        return self._evaluate(dataset, metrics_to_run)
