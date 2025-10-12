import traceback
from abc import ABC, abstractmethod
from datasets import Dataset
from ragas import evaluate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
)

# Abstract base class for LLMs
class LLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Concrete implementation for Ollama
class OllamaWrapper(LLM):
    def __init__(self, model_name="llama3.1:latest"):
        self.llm = OllamaLLM(model=model_name)
        # Use a local embedding model from Ollama
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

    async def generate(self, prompt: str) -> str:
        return await self.llm.ainvoke(prompt)

# Factory to switch between LLMs
class LLMFactory:
    @staticmethod
    def get_llm(llm_type="ollama", **kwargs):
        if llm_type == "ollama":
            return OllamaWrapper(**kwargs)
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
            "answer_correctness": answer_correctness,
        }

    def _evaluate(self, dataset: Dataset, metrics: list):
        """Helper to run evaluation."""
        try:
            print("Starting evaluation...")
            result = evaluate(
                dataset=dataset,
                metrics=metrics,
                llm=self.llm.llm,
                embeddings=self.llm.embeddings,
                raise_exceptions=True
            )
            print("Evaluation finished.")
            return result
        except Exception as e:
            print(f"An error occurred during Ragas evaluation: {e}")
            # Re-raise the exception so it can be caught by the caller
            raise e

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

    def evaluate_answer_correctness(self, question: str, answer: str, ground_truth: str):
        """
        Evaluates the correctness of the answer based on the ground truth.
        """
        dataset = Dataset.from_dict({"question": [question], "answer": [answer], "ground_truth": [ground_truth]})
        return self._evaluate(dataset, [self.metrics["answer_correctness"]])

    def evaluate_all(self, question: str, answer: str, contexts: list[str], ground_truth: str):
        """
        Evaluates all metrics on the given data.
        """
        dataset = Dataset.from_dict({
            "question": [question],
            "answer": [answer],
            "contexts": [contexts],
            "ground_truth": [ground_truth]
        })
        return self._evaluate(dataset, list(self.metrics.values()))
