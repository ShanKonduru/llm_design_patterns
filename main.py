import os
import traceback
from dotenv import load_dotenv
from src.llm_evaluation import RagasEvaluator, LLMFactory

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


def print_score(metric_name, score_result, explanation):
    if isinstance(score_result, dict) and score_result:
        # The key is the metric name, get the score value.
        score_value = score_result.get(metric_name)
        if score_value is not None:
            print(f"  - {metric_name.replace('_', ' ').title()}: Evaluation succeeded.")
            print(f"  - Score: {score_value:.4f}")
            print(f"  - Explanation: {explanation}")
        else:
            print(f"  - {metric_name.replace('_', ' ').title()}: Evaluation failed or returned no score.")
            print(f"  - Raw result: {score_result}")
    else:
        print(f"  - {metric_name.replace('_', ' ').title()}: Evaluation failed or returned no score.")
        print(f"  - Raw result: {score_result}")


def main():
    """
    Main function to demonstrate the LLM evaluation framework.
    """
    # Positive Scenario: The answer is faithful, relevant, and factually correct.
    print_header("Positive Evaluation Scenario")
    question_positive = "What is the capital of France?"
    answer_positive = "The capital of France is Paris."
    contexts_positive = ["Paris is the capital and most populous city of France."]
    ground_truth_positive = "The capital of France is Paris, a major European city and a global center for art, fashion, gastronomy and culture."
    
    print_inputs(question_positive, answer_positive, contexts_positive, ground_truth_positive)

    llm = LLMFactory.get_llm(llm_type="ollama", model_name="llama3.1:latest")
    evaluator = RagasEvaluator(llm)
    
    print("\n--- Running Individual Metric Evaluations (Positive) ---")
    try:
        faithfulness_score = evaluator.evaluate_faithfulness(question_positive, answer_positive, contexts_positive)
        print_score("faithfulness", faithfulness_score, "The answer is directly supported by the context. (Score should be high, ideally 1.0)")

        answer_relevancy_score = evaluator.evaluate_answer_relevancy(question_positive, answer_positive, contexts_positive)
        print_score("answer_relevancy", answer_relevancy_score, "The answer is highly relevant to the question. (Score should be high, ideally > 0.8)")

        context_recall_score = evaluator.evaluate_context_recall(question_positive, contexts_positive, ground_truth_positive)
        print_score("context_recall", context_recall_score, "The context contains all necessary information from the ground truth. (Score should be high, ideally 1.0)")

        context_precision_score = evaluator.evaluate_context_precision(question_positive, contexts_positive, ground_truth_positive)
        print_score("context_precision", context_precision_score, "All information in the context is relevant to the question. (Score should be high, ideally 1.0)")

        answer_correctness_score = evaluator.evaluate_answer_correctness(question_positive, answer_positive, ground_truth_positive)
        print_score("answer_correctness", answer_correctness_score, "The answer is factually correct based on the ground truth. (Score should be high, ideally > 0.7)")

    except Exception as e:
        print(f"\nAn error occurred during positive scenario evaluation: {e}")
        traceback.print_exc()

    # Negative Scenario: The answer is unfaithful and factually incorrect.
    print_header("Negative Evaluation Scenario")
    question_negative = "What is the capital of Italy?"
    answer_negative = "The capital of Italy is Berlin."
    contexts_negative = ["Rome is a city in Italy. It is known for its ancient history.", "Berlin is the capital of Germany."]
    ground_truth_negative = "The capital of Italy is Rome."

    print_inputs(question_negative, answer_negative, contexts_negative, ground_truth_negative)

    print("\n--- Running Individual Metric Evaluations (Negative) ---")
    try:
        faithfulness_score_neg = evaluator.evaluate_faithfulness(question_negative, answer_negative, contexts_negative)
        print_score("faithfulness", faithfulness_score_neg, "The answer 'Berlin' is not supported by the context about Rome. (Score should be low, ideally 0.0)")

        answer_relevancy_score_neg = evaluator.evaluate_answer_relevancy(question_negative, answer_negative, contexts_negative)
        print_score("answer_relevancy", answer_relevancy_score_neg, "The answer 'Berlin' is not relevant to the question about Italy's capital. (Score should be low)")

        context_recall_score_neg = evaluator.evaluate_context_recall(question_negative, contexts_negative, ground_truth_negative)
        print_score("context_recall", context_recall_score_neg, "The context mentions Rome but doesn't explicitly state it's the capital, so it partially misses the ground truth. (Score should be moderate, e.g., 0.5)")

        context_precision_score_neg = evaluator.evaluate_context_precision(question_negative, contexts_negative, ground_truth_negative)
        print_score("context_precision", context_precision_score_neg, "The context contains irrelevant information (about Berlin). (Score should be low, ideally < 0.5)")

        try:
            answer_correctness_score_neg = evaluator.evaluate_answer_correctness(question_negative, answer_negative, ground_truth_negative)
            print_score("answer_correctness", answer_correctness_score_neg, "The answer is factually incorrect. (Score should be low, ideally < 0.3)")
        except Exception as e:
            print(f"  - answer_correctness: Evaluation failed with an exception: {e}")

    except Exception as e:
        print(f"\nAn error occurred during negative scenario evaluation: {e}")
        traceback.print_exc()

    # Comprehensive Scenario: Evaluate all metrics at once.
    print_header("Comprehensive Evaluation (All Metrics)")
    all_metrics_score = evaluator.evaluate_all(question_positive, answer_positive, contexts_positive, ground_truth_positive)
    
    print("\n--- Evaluating all metrics at once for the positive scenario ---")
    if all_metrics_score:
        # The result object can be directly treated as a dictionary
        for metric, score in all_metrics_score.items():
            print(f"  - {metric.replace('_', ' ').title()}: {score:.4f}")
    else:
        print("Evaluation failed to return scores.")


if __name__ == "__main__":
    main()
