import unittest
from unittest.mock import patch, MagicMock
import pytest

# Try to import dependencies - skip all tests if not available
try:
    import numpy as np
    import torch
    from src.classic_metrics import ClassicMetricEvaluator
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    SKIP_REASON = f"Missing dependencies for classic_metrics: {str(e)}"

# Skip entire test class if dependencies not available
pytestmark = pytest.mark.skipif(
    not DEPENDENCIES_AVAILABLE,
    reason="classic_metrics requires sacrebleu, rouge-score, bert-score packages"
)


class TestClassicMetricEvaluator(unittest.TestCase):
    """Test the ClassicMetricEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = ClassicMetricEvaluator()
        self.generated_text = "The capital of France is Paris."
        self.reference_text = "Paris is the capital of France."
    
    def test_evaluator_initialization(self):
        """Test that evaluator initializes correctly."""
        self.assertIsNotNone(self.evaluator)
        self.assertIsNotNone(self.evaluator.rouge_scorer)
    
    def test_evaluate_rouge_identical_texts(self):
        """Test ROUGE scores for identical texts."""
        result = self.evaluator.evaluate_rouge(
            self.reference_text,
            self.reference_text
        )
        
        # Assert all scores are present
        self.assertIn("rouge1", result)
        self.assertIn("rouge2", result)
        self.assertIn("rougeL", result)
        
        # For identical texts, scores should be close to 1.0
        self.assertGreater(result["rouge1"], 0.9)
        self.assertGreater(result["rougeL"], 0.9)
    
    def test_evaluate_rouge_similar_texts(self):
        """Test ROUGE scores for similar texts."""
        result = self.evaluator.evaluate_rouge(
            self.generated_text,
            self.reference_text
        )
        
        # Assert scores are present and reasonable
        self.assertIn("rouge1", result)
        self.assertIn("rouge2", result)
        self.assertIn("rougeL", result)
        
        # Scores should be between 0 and 1
        self.assertGreaterEqual(result["rouge1"], 0.0)
        self.assertLessEqual(result["rouge1"], 1.0)
        self.assertGreaterEqual(result["rouge2"], 0.0)
        self.assertLessEqual(result["rouge2"], 1.0)
    
    def test_evaluate_rouge_different_texts(self):
        """Test ROUGE scores for completely different texts."""
        result = self.evaluator.evaluate_rouge(
            "The sky is blue",
            "Cats enjoy playing with toys"
        )
        
        # Scores should be low for unrelated texts
        self.assertLess(result["rouge1"], 0.5)
        self.assertEqual(result["rouge2"], 0.0)  # No 2-gram overlap
    
    def test_evaluate_bleu_identical_texts(self):
        """Test BLEU score for identical texts."""
        result = self.evaluator.evaluate_bleu(
            self.reference_text,
            self.reference_text
        )
        
        self.assertIn("bleu", result)
        # Identical texts should have high BLEU
        self.assertGreater(result["bleu"], 0.9)
    
    def test_evaluate_bleu_similar_texts(self):
        """Test BLEU score for similar texts."""
        result = self.evaluator.evaluate_bleu(
            self.generated_text,
            self.reference_text
        )
        
        self.assertIn("bleu", result)
        # Score should be between 0 and 1
        self.assertGreaterEqual(result["bleu"], 0.0)
        self.assertLessEqual(result["bleu"], 1.0)
    
    def test_evaluate_bleu_different_texts(self):
        """Test BLEU score for different texts."""
        result = self.evaluator.evaluate_bleu(
            "The sky is blue",
            "Cats enjoy playing"
        )
        
        self.assertIn("bleu", result)
        # Unrelated texts should have low BLEU
        self.assertLess(result["bleu"], 0.3)
    
    @patch('src.classic_metrics.bert_score_calc')
    def test_evaluate_bert_score(self, mock_bert_score):
        """Test BERTScore calculation."""
        # Mock BERTScore to avoid loading large models
        mock_P = torch.tensor([0.85])
        mock_R = torch.tensor([0.90])
        mock_F1 = torch.tensor([0.875])
        mock_bert_score.return_value = (mock_P, mock_R, mock_F1)
        
        result = self.evaluator.evaluate_bert_score(
            self.generated_text,
            self.reference_text
        )
        
        self.assertIn("bert_score_f1", result)
        self.assertEqual(result["bert_score_f1"], 0.875)
        mock_bert_score.assert_called_once()
    
    @patch('src.classic_metrics.bert_score_calc')
    def test_evaluate_bert_score_different_texts(self, mock_bert_score):
        """Test BERTScore for different texts."""
        mock_P = torch.tensor([0.3])
        mock_R = torch.tensor([0.4])
        mock_F1 = torch.tensor([0.35])
        mock_bert_score.return_value = (mock_P, mock_R, mock_F1)
        
        result = self.evaluator.evaluate_bert_score(
            "The sky is blue",
            "Cats enjoy toys"
        )
        
        self.assertIn("bert_score_f1", result)
        self.assertLess(result["bert_score_f1"], 0.5)
    
    def test_evaluate_retrieval_metrics_perfect_retrieval(self):
        """Test retrieval metrics with perfect retrieval."""
        retrieved = ["doc1", "doc2", "doc3"]
        relevant = ["doc1", "doc2", "doc3"]
        
        result = self.evaluator.evaluate_retrieval_metrics(retrieved, relevant)
        
        self.assertIn("precision_at_3", result)
        self.assertIn("recall_at_3", result)
        self.assertIn("mrr", result)
        
        # Perfect retrieval should have precision and recall of 1.0
        self.assertEqual(result["precision_at_3"], 1.0)
        self.assertEqual(result["recall_at_3"], 1.0)
        self.assertEqual(result["mrr"], 1.0)  # First doc is relevant
    
    def test_evaluate_retrieval_metrics_partial_retrieval(self):
        """Test retrieval metrics with partial retrieval."""
        retrieved = ["doc1", "doc2", "doc3", "doc4"]
        relevant = ["doc2", "doc5", "doc6"]
        
        result = self.evaluator.evaluate_retrieval_metrics(retrieved, relevant)
        
        self.assertIn("precision_at_4", result)
        self.assertIn("recall_at_4", result)
        self.assertIn("mrr", result)
        
        # Only doc2 is relevant and retrieved
        self.assertEqual(result["precision_at_4"], 0.25)  # 1/4
        self.assertAlmostEqual(result["recall_at_4"], 0.333, places=2)  # 1/3
        self.assertEqual(result["mrr"], 0.5)  # doc2 is at position 2
    
    def test_evaluate_retrieval_metrics_no_relevant(self):
        """Test retrieval metrics with no relevant documents."""
        retrieved = ["doc1", "doc2", "doc3"]
        relevant = ["doc4", "doc5"]
        
        result = self.evaluator.evaluate_retrieval_metrics(retrieved, relevant)
        
        self.assertEqual(result["precision_at_3"], 0.0)
        self.assertEqual(result["recall_at_3"], 0.0)
        self.assertEqual(result["mrr"], 0.0)
    
    def test_evaluate_retrieval_metrics_empty_retrieval(self):
        """Test retrieval metrics with empty retrieval."""
        retrieved = []
        relevant = ["doc1", "doc2"]
        
        result = self.evaluator.evaluate_retrieval_metrics(retrieved, relevant)
        
        self.assertEqual(result["precision_at_0"], 0.0)
        self.assertEqual(result["recall_at_0"], 0.0)
        self.assertEqual(result["mrr"], 0.0)
    
    def test_evaluate_retrieval_metrics_mrr_second_position(self):
        """Test MRR when first relevant is at second position."""
        retrieved = ["doc1", "doc2", "doc3"]
        relevant = ["doc2", "doc3"]
        
        result = self.evaluator.evaluate_retrieval_metrics(retrieved, relevant)
        
        # First relevant doc (doc2) is at position 2 (index 1)
        self.assertEqual(result["mrr"], 0.5)  # 1/2
    
    def test_evaluate_ndcg_perfect_ranking(self):
        """Test nDCG with perfect ranking."""
        retrieved = ["doc1", "doc2", "doc3"]
        relevant_with_scores = [("doc1", 3), ("doc2", 2), ("doc3", 1)]
        
        result = self.evaluator.evaluate_ndcg(retrieved, relevant_with_scores)
        
        self.assertIn("ndcg_at_3", result)
        # Perfect ranking should have nDCG close to 1.0
        self.assertGreater(result["ndcg_at_3"], 0.99)
    
    def test_evaluate_ndcg_imperfect_ranking(self):
        """Test nDCG with imperfect ranking."""
        retrieved = ["doc3", "doc1", "doc2"]
        relevant_with_scores = [("doc1", 3), ("doc2", 2), ("doc3", 1)]
        
        result = self.evaluator.evaluate_ndcg(retrieved, relevant_with_scores)
        
        self.assertIn("ndcg_at_3", result)
        # Imperfect ranking should have lower nDCG
        self.assertGreater(result["ndcg_at_3"], 0.0)
        self.assertLess(result["ndcg_at_3"], 1.0)
    
    def test_evaluate_ndcg_no_relevant(self):
        """Test nDCG with no relevant documents."""
        retrieved = ["doc4", "doc5", "doc6"]
        relevant_with_scores = [("doc1", 3), ("doc2", 2), ("doc3", 1)]
        
        result = self.evaluator.evaluate_ndcg(retrieved, relevant_with_scores)
        
        self.assertIn("ndcg_at_3", result)
        # No relevant docs should give nDCG of 0
        self.assertEqual(result["ndcg_at_3"], 0.0)
    
    def test_evaluate_ndcg_single_document(self):
        """Test nDCG with single document."""
        retrieved = ["doc1"]
        relevant_with_scores = [("doc1", 5), ("doc2", 3)]
        
        result = self.evaluator.evaluate_ndcg(retrieved, relevant_with_scores)
        
        self.assertIn("ndcg_at_1", result)
        # Single most relevant doc should have high nDCG
        self.assertGreater(result["ndcg_at_1"], 0.9)
    
    def test_evaluate_ndcg_empty_retrieval(self):
        """Test nDCG with empty retrieval."""
        retrieved = []
        relevant_with_scores = [("doc1", 3), ("doc2", 2)]
        
        result = self.evaluator.evaluate_ndcg(retrieved, relevant_with_scores)
        
        self.assertIn("ndcg_at_0", result)
        self.assertEqual(result["ndcg_at_0"], 0.0)


if __name__ == '__main__':
    unittest.main()
