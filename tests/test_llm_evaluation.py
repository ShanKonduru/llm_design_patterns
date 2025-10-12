import pytest
from unittest.mock import MagicMock, patch
from datasets import Dataset
from src.llm_evaluation import RagasEvaluator, LLMFactory

# Mock LLM for testing
class MockLLM:
    def __init__(self, model_name="mock"):
        self.llm = MagicMock()
        self.embeddings = MagicMock()

    def generate(self, prompt: str) -> str:
        return "mocked answer"

@pytest.fixture
def evaluator():
    """Fixture to create a RagasEvaluator with a mocked LLM."""
    mock_llm_instance = MockLLM()
    return RagasEvaluator(mock_llm_instance)

# --- Positive Test Cases ---

@pytest.mark.positive
def test_evaluate_faithfulness_positive(evaluator):
    """
    Tests that faithfulness evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"faithfulness": 1.0}
        result = evaluator.evaluate_faithfulness(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            contexts=["Paris is the capital and most populous city of France."]
        )
        assert "faithfulness" in result
        assert result["faithfulness"] == 1.0
        mock_evaluate.assert_called_once()

@pytest.mark.positive
def test_evaluate_answer_relevancy_positive(evaluator):
    """
    Tests that answer relevancy evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"answer_relevancy": 1.0}
        result = evaluator.evaluate_answer_relevancy(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            contexts=["Paris is the capital and most populous city of France."]
        )
        assert "answer_relevancy" in result
        assert result["answer_relevancy"] == 1.0
        mock_evaluate.assert_called_once()

@pytest.mark.positive
def test_evaluate_context_recall_positive(evaluator):
    """
    Tests that context recall evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"context_recall": 1.0}
        result = evaluator.evaluate_context_recall(
            question="What is the capital of France?",
            contexts=["Paris is the capital and most populous city of France."],
            ground_truth="The capital of France is Paris."
        )
        assert "context_recall" in result
        assert result["context_recall"] == 1.0
        mock_evaluate.assert_called_once()

@pytest.mark.positive
def test_evaluate_context_precision_positive(evaluator):
    """
    Tests that context precision evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"context_precision": 1.0}
        result = evaluator.evaluate_context_precision(
            question="What is the capital of France?",
            contexts=["Paris is the capital and most populous city of France."],
            ground_truth="The capital of France is Paris."
        )
        assert "context_precision" in result
        assert result["context_precision"] == 1.0
        mock_evaluate.assert_called_once()

@pytest.mark.positive
def test_evaluate_context_precision_positive(evaluator):
    """
    Tests that context precision evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"context_precision": 1.0}
        result = evaluator.evaluate_context_precision(
            question="What is the capital of France?",
            contexts=["Paris is the capital and most populous city of France."],
            ground_truth="The capital of France is Paris."
        )
        assert "context_precision" in result
        assert result["context_precision"] == 1.0
        mock_evaluate.assert_called_once()

@pytest.mark.positive
def test_evaluate_answer_correctness_positive(evaluator):
    """
    Tests that answer correctness evaluation runs with valid inputs.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"answer_correctness": 1.0}
        result = evaluator.evaluate_answer_correctness(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            ground_truth="The capital of France is Paris."
        )
        assert "answer_correctness" in result
        assert result["answer_correctness"] == 1.0
        mock_evaluate.assert_called_once()


# --- Negative Test Cases ---

@pytest.mark.negative
def test_evaluate_faithfulness_negative_empty_context(evaluator):
    """
    Tests faithfulness evaluation with empty context.
    Ragas should handle this gracefully, likely resulting in a low score.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"faithfulness": 0.0}
        result = evaluator.evaluate_faithfulness(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            contexts=[]
        )
        assert "faithfulness" in result
        assert result["faithfulness"] == 0.0
        mock_evaluate.assert_called_once()

@pytest.mark.negative
def test_evaluate_answer_relevancy_negative_irrelevant_answer(evaluator):
    """
    Tests answer relevancy with a completely irrelevant answer.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {"answer_relevancy": 0.1}
        result = evaluator.evaluate_answer_relevancy(
            question="What is the capital of France?",
            answer="I like turtles.",
            contexts=["Paris is the capital of France."]
        )
        assert "answer_relevancy" in result
        assert result["answer_relevancy"] < 0.5
        mock_evaluate.assert_called_once()

# --- Edge Case Test Cases ---

@pytest.mark.edge
def test_evaluate_all_metrics_edge_case(evaluator):
    """
    Tests the 'evaluate_all' method to ensure it calls the underlying
    evaluate function with all registered metrics.
    """
    with patch('src.llm_evaluation.evaluate') as mock_evaluate:
        mock_evaluate.return_value = {
            "faithfulness": 1.0,
            "answer_relevancy": 1.0,
            "context_recall": 1.0,
            "context_precision": 1.0,
            "context_relevance": 1.0,
            "answer_correctness": 1.0,
        }
        result = evaluator.evaluate_all(
            question="What is the capital of France?",
            answer="Paris is the capital of France.",
            contexts=["Paris is the capital and most populous city of France."],
            ground_truth="The capital of France is Paris."
        )
        assert len(result) == 6
        mock_evaluate.assert_called_once()
        # Check that all metrics were passed to the evaluate call
        called_metrics = mock_evaluate.call_args[1]['metrics']
        assert len(called_metrics) == len(evaluator.metrics)

@pytest.mark.edge
def test_llm_factory_edge_unsupported_type():
    """
    Tests that the LLMFactory raises a ValueError for an unsupported LLM type.
    """
    with pytest.raises(ValueError):
        LLMFactory.get_llm("unsupported_llm_type")
