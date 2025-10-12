import os
from dotenv import load_dotenv
from src.llm_evaluation import LLMFactory, RagasEvaluator

load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")


def main():
    # 1. Set up sample data for evaluation
    question = "What is the capital of France?"
    answer = "The capital of France is Paris."
    # The 'ground_truth' or 'reference' answer is needed for several metrics
    ground_truth = "Paris is the capital of France."
    contexts = [
        "France is a country in Western Europe.",
        "Paris is the most populous city in France.",
        "The Eiffel Tower is a famous landmark in Paris.",
    ]

    print("Starting LLM evaluation demo...")
    print("-" * 30)
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Contexts: {contexts}")
    print("-" * 30)

    try:
        # 2. Use the factory to get an Ollama LLM instance.
        model_to_use = "llama3.1:latest"
        print(f"Initializing LLM from factory (model: {model_to_use})...")
        llm_instance = LLMFactory.get_llm("ollama", model_name=model_to_use)
        print("LLM Initialized.")

        # 3. Create an evaluator instance
        evaluator = RagasEvaluator(llm_instance)
        print("Ragas Evaluator Initialized.")
        print("-" * 30)

        # 4. Evaluate using individual methods
        print("Running individual evaluations...")

        faithfulness_score = evaluator.evaluate_faithfulness(question, answer, contexts)
        print(f"Faithfulness Score: {faithfulness_score}")

        answer_relevancy_score = evaluator.evaluate_answer_relevancy(
            question, answer, contexts
        )
        print(f"Answer Relevancy Score: {answer_relevancy_score}")

        context_recall_score = evaluator.evaluate_context_recall(
            question, contexts, ground_truth
        )
        print(f"Context Recall Score: {context_recall_score}")

        print("-" * 30)

        # 5. Evaluate all metrics at once
        print("Running all evaluations at once...")
        all_scores = evaluator.evaluate_all(question, answer, contexts, ground_truth)
        print("All Scores:")
        print(all_scores)
        print("-" * 30)

        print("Evaluation demo finished successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure Ollama is running and the specified model is available.")


if __name__ == "__main__":
    main()
