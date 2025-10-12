import os
import traceback
import argparse
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException
from src.llm_evaluation import RagasEvaluator, LLMFactory
from src.classic_metrics import ClassicMetricEvaluator
import pandas as pd

load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")


def print_header(title):
    print(f"\n=== {title} ===")
    print("-" * (len(title) + 8))


def print_inputs(question, answer, contexts, ground_truth):
    print(f"  - Question: {question}")
    print(f"  - Answer: {answer}")
    print(f"  - Contexts: {contexts}")
    print(f"  - Ground Truth: {ground_truth}")


def print_score(metric_name, score, explanation=""):
    """Prints the evaluation score and explanation."""
    print(f"\n--- {metric_name} ---")
    if explanation:
        print(explanation)
    
    if score is not None:
        # The result from ragas.evaluate can be an EvaluationResult object or a dict.
        # Using pandas handles both cases gracefully.
        if hasattr(score, 'to_pandas'):
            df = score.to_pandas()
        else:
            df = pd.DataFrame([score])
        print(df.to_string())
    else:
        print("  - Score: N/A (evaluation failed)")


class EvaluationRunner:
    """
    A class to encapsulate the RAG evaluation scenarios.
    """
    def __init__(self):
        self.llm = LLMFactory.get_llm(llm_type="ollama", model_name="llama3.1:latest")
        self.evaluator = RagasEvaluator(self.llm)
        self.classic_evaluator = ClassicMetricEvaluator()
        self._setup_scenarios()

    def _setup_scenarios(self):
        """Defines the positive and negative evaluation scenarios."""
        self.positive_scenario = {
            "name": "Positive Evaluation Scenario",
            "question": "What is the capital of France?",
            "answer": "The capital of France is Paris.",
            "contexts": ["Paris is the capital and most populous city of France."],
            "ground_truth": "The capital of France is Paris, a major European city and a global center for art, fashion, gastronomy and culture."
        }
        self.negative_scenario = {
            "name": "Negative Evaluation Scenario",
            "question": "What is the capital of Italy?",
            "answer": "The capital of Italy is Berlin.",
            "contexts": ["Rome is a city in Italy. It is known for its ancient history.", "Berlin is the capital of Germany."],
            "ground_truth": "The capital of Italy is Rome.",
            "relevant_contexts": ["Rome is the capital of Italy.", "Rome is a city in Italy. It is known for its ancient history."],
            "relevant_contexts_with_scores": [("Rome is the capital of Italy.", 1.0), ("Rome is a city in Italy. It is known for its ancient history.", 0.7)]
        }

    def _run_and_print_evaluation(self, metric_name, scenario, evaluation_func, explanation):
        """Helper to run an evaluation and print the score."""
        print_header(f"{scenario['name']} - {metric_name.replace('_', ' ').title()}")
        print_inputs(scenario['question'], scenario['answer'], scenario['contexts'], scenario['ground_truth'])
        try:
            score = evaluation_func()
            print_score(metric_name, score, explanation)
        except OutputParserException:
            print(f"\nAn error occurred during {metric_name} evaluation: Output Parsing Error.")
            print("This is a known issue where the LLM fails to return a valid JSON format for this metric.")
            print("  - Score: 0.0000 (failed)")
            print(f"  - Raw result: None (due to parsing failure)")
        except Exception as e:
            print(f"\nAn unexpected error occurred during {metric_name} evaluation: {e}")
            traceback.print_exc()

    def evaluate_faithfulness(self):
        self._run_and_print_evaluation(
            "faithfulness",
            self.positive_scenario,
            lambda: self.evaluator.evaluate_faithfulness(self.positive_scenario['question'], self.positive_scenario['answer'], self.positive_scenario['contexts']),
            "The answer is directly supported by the context. (Score should be high, ideally 1.0)"
        )
        self._run_and_print_evaluation(
            "faithfulness",
            self.negative_scenario,
            lambda: self.evaluator.evaluate_faithfulness(self.negative_scenario['question'], self.negative_scenario['answer'], self.negative_scenario['contexts']),
            "The answer 'Berlin' is not supported by the context about Rome. (Score should be low, ideally 0.0)"
        )

    def evaluate_answer_relevancy(self):
        self._run_and_print_evaluation(
            "answer_relevancy",
            self.positive_scenario,
            lambda: self.evaluator.evaluate_answer_relevancy(self.positive_scenario['question'], self.positive_scenario['answer'], self.positive_scenario['contexts']),
            "The answer is highly relevant to the question. (Score should be high, ideally > 0.8)"
        )
        self._run_and_print_evaluation(
            "answer_relevancy",
            self.negative_scenario,
            lambda: self.evaluator.evaluate_answer_relevancy(self.negative_scenario['question'], self.negative_scenario['answer'], self.negative_scenario['contexts']),
            "The answer 'Berlin' is not relevant to the question about Italy's capital. (Score should be low)"
        )

    def evaluate_context_recall(self):
        self._run_and_print_evaluation(
            "context_recall",
            self.positive_scenario,
            lambda: self.evaluator.evaluate_context_recall(self.positive_scenario['question'], self.positive_scenario['contexts'], self.positive_scenario['ground_truth']),
            "The context contains all necessary information from the ground truth. (Score should be high, ideally 1.0)"
        )
        self._run_and_print_evaluation(
            "context_recall",
            self.negative_scenario,
            lambda: self.evaluator.evaluate_context_recall(self.negative_scenario['question'], self.negative_scenario['contexts'], self.negative_scenario['ground_truth']),
            "The context mentions Rome but doesn't explicitly state it's the capital, so it partially misses the ground truth. (Score should be moderate, e.g., 0.5)"
        )

    def evaluate_context_precision(self):
        self._run_and_print_evaluation(
            "context_precision",
            self.positive_scenario,
            lambda: self.evaluator.evaluate_context_precision(self.positive_scenario['question'], self.positive_scenario['contexts'], self.positive_scenario['ground_truth']),
            "All information in the context is relevant to the question. (Score should be high, ideally 1.0)"
        )
        self._run_and_print_evaluation(
            "context_precision",
            self.negative_scenario,
            lambda: self.evaluator.evaluate_context_precision(self.negative_scenario['question'], self.negative_scenario['contexts'], self.negative_scenario['ground_truth']),
            "The context contains irrelevant information (about Berlin). (Score should be low, ideally < 0.5)"
        )

    def evaluate_answer_correctness(self):
        self._run_and_print_evaluation(
            "answer_correctness",
            self.positive_scenario,
            lambda: self.evaluator.evaluate_answer_correctness(self.positive_scenario['question'], self.positive_scenario['answer'], self.positive_scenario['ground_truth']),
            "The answer is factually correct based on the ground truth. (Score should be high, ideally > 0.7)"
        )
        self._run_and_print_evaluation(
            "answer_correctness",
            self.negative_scenario,
            lambda: self.evaluator.evaluate_answer_correctness(self.negative_scenario['question'], self.negative_scenario['answer'], self.negative_scenario['ground_truth']),
            "The answer is factually incorrect. (Score should be low, ideally < 0.3)"
        )

    def evaluate_rouge(self):
        self._run_and_print_evaluation(
            "rouge",
            self.positive_scenario,
            lambda: self.classic_evaluator.evaluate_rouge(self.positive_scenario['answer'], self.positive_scenario['ground_truth']),
            "Measures n-gram overlap between answer and ground truth."
        )

    def evaluate_bleu(self):
        self._run_and_print_evaluation(
            "bleu",
            self.positive_scenario,
            lambda: self.classic_evaluator.evaluate_bleu(self.positive_scenario['answer'], self.positive_scenario['ground_truth']),
            "Measures precision-focused overlap, penalizing different phrasing."
        )

    def evaluate_bert_score(self):
        self._run_and_print_evaluation(
            "bert_score",
            self.positive_scenario,
            lambda: self.classic_evaluator.evaluate_bert_score(self.positive_scenario['answer'], self.positive_scenario['ground_truth']),
            "Measures semantic similarity using BERT embeddings."
        )

    def evaluate_retrieval_metrics(self):
        print_header("Retrieval Metrics (Precision@K, Recall@K, MRR)")
        # Using the negative scenario as it has a more interesting context list
        scenario = self.negative_scenario
        print_inputs(scenario['question'], scenario['answer'], scenario['contexts'], scenario['ground_truth'])
        
        retrieval_scores = self.classic_evaluator.evaluate_retrieval_metrics(
            retrieved_contexts=scenario['contexts'],
            relevant_contexts=scenario['relevant_contexts']
        )
        print_score("retrieval_metrics", retrieval_scores, "Evaluates the quality of the retrieved context.")

    def evaluate_ndcg(self):
        print_header("Retrieval Metrics (nDCG)")
        scenario = self.negative_scenario
        print_inputs(scenario['question'], scenario['answer'], scenario['contexts'], scenario['ground_truth'])

        ndcg_score = self.classic_evaluator.evaluate_ndcg(
            retrieved_contexts=scenario['contexts'],
            relevant_contexts_with_scores=scenario['relevant_contexts_with_scores']
        )
        print_score("ndcg", ndcg_score, "Evaluates the ranked order of retrieved items.")

    def run_all_evaluations(self):
        """Runs all individual and comprehensive evaluations."""
        self.evaluate_faithfulness()
        self.evaluate_answer_relevancy()
        self.evaluate_context_recall()
        self.evaluate_context_precision()
        self.evaluate_answer_correctness()
        self.evaluate_rouge()
        self.evaluate_bleu()
        self.evaluate_bert_score()
        self.evaluate_retrieval_metrics()
        self.evaluate_ndcg()

        print_header("Comprehensive Evaluation (All Metrics)")
        try:
            all_metrics_score = self.evaluator.evaluate_all(
                self.positive_scenario['question'],
                self.positive_scenario['answer'],
                self.positive_scenario['contexts'],
                self.positive_scenario['ground_truth']
            )
            explanation = "\n--- Evaluating all metrics at once for the positive scenario ---"
            print_score("comprehensive", all_metrics_score, explanation)
        except Exception as e:
            print(f"\nAn error occurred during comprehensive evaluation: {e}")


def main():
    """
    Main function to demonstrate the LLM evaluation framework.
    """
    parser = argparse.ArgumentParser(description="Run Ragas and Classic evaluation metrics.")
    parser.add_argument(
        "--metric",
        type=str,
        default="all",
        choices=[
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "context_precision",
            "answer_correctness",
            "rouge",
            "bleu",
            "bert_score",
            "retrieval",
            "ndcg",
            "all",
        ],
        help="The metric to evaluate. Defaults to 'all'.",
    )
    args = parser.parse_args()

    runner = EvaluationRunner()

    evaluation_map = {
        "faithfulness": runner.evaluate_faithfulness,
        "answer_relevancy": runner.evaluate_answer_relevancy,
        "context_recall": runner.evaluate_context_recall,
        "context_precision": runner.evaluate_context_precision,
        "answer_correctness": runner.evaluate_answer_correctness,
        "rouge": runner.evaluate_rouge,
        "bleu": runner.evaluate_bleu,
        "bert_score": runner.evaluate_bert_score,
        "retrieval": runner.evaluate_retrieval_metrics,
        "ndcg": runner.evaluate_ndcg,
        "all": runner.run_all_evaluations,
    }

    # Get the function from the map and call it
    evaluation_func = evaluation_map.get(args.metric)
    if evaluation_func:
        evaluation_func()
    else:
        print(f"Invalid metric: {args.metric}")


if __name__ == "__main__":
    main()
