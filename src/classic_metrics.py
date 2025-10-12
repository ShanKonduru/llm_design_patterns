import numpy as np
from rouge_score import rouge_scorer
import sacrebleu
from bert_score import score as bert_score_calc
from sklearn.metrics import label_ranking_average_precision_score
import torch

class ClassicMetricEvaluator:
    """
    A class to encapsulate classic NLP and Information Retrieval metrics.
    """
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    def evaluate_rouge(self, generated_text, reference_text):
        """
        Calculates ROUGE scores (R-1, R-2, R-L).
        Focuses on recall by measuring n-gram overlap.
        """
        scores = self.rouge_scorer.score(reference_text, generated_text)
        return {
            "rouge1": scores['rouge1'].fmeasure,
            "rouge2": scores['rouge2'].fmeasure,
            "rougeL": scores['rougeL'].fmeasure
        }

    def evaluate_bleu(self, generated_text, reference_text):
        """
        Calculates BLEU score.
        Focuses on precision, good for evaluating translation-like tasks.
        """
        # sacrebleu expects a list of references
        score = sacrebleu.corpus_bleu([generated_text], [[reference_text]])
        return {"bleu": score.score / 100} # Scale to 0-1 range

    def evaluate_bert_score(self, generated_text, reference_text):
        """
        Calculates BERTScore.
        Measures semantic similarity between generated and reference text.
        """
        # bert_score returns P, R, F1 tensors. We'll use F1.
        # The device can be set to 'cuda' if a GPU is available.
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        P, R, F1 = bert_score_calc([generated_text], [reference_text], lang="en", device=device)
        return {"bert_score_f1": F1.mean().item()}

    def evaluate_retrieval_metrics(self, retrieved_contexts, relevant_contexts):
        """
        Calculates Precision@K, Recall@K, and MRR for retrieval.
        """
        k = len(retrieved_contexts)
        retrieved_set = set(retrieved_contexts)
        relevant_set = set(relevant_contexts)
        
        true_positives = len(retrieved_set.intersection(relevant_set))
        
        precision_at_k = true_positives / k if k > 0 else 0.0
        recall_at_k = true_positives / len(relevant_set) if len(relevant_set) > 0 else 0.0
        
        # MRR
        mrr = 0.0
        for i, doc in enumerate(retrieved_contexts):
            if doc in relevant_set:
                mrr = 1.0 / (i + 1)
                break
        
        return {
            f"precision_at_{k}": precision_at_k,
            f"recall_at_{k}": recall_at_k,
            "mrr": mrr
        }

    def evaluate_ndcg(self, retrieved_contexts, relevant_contexts_with_scores):
        """
        Calculates Normalized Discounted Cumulative Gain (nDCG).
        Requires relevance scores for each document.
        """
        k = len(retrieved_contexts)
        
        # Create relevance scores for retrieved items
        relevance_map = dict(relevant_contexts_with_scores)
        retrieved_scores = [relevance_map.get(doc, 0) for doc in retrieved_contexts]
        
        # DCG
        dcg = 0.0
        for i in range(k):
            dcg += retrieved_scores[i] / np.log2(i + 2)
            
        # Ideal DCG
        ideal_scores = sorted([score for doc, score in relevant_contexts_with_scores], reverse=True)
        idcg = 0.0
        for i in range(min(k, len(ideal_scores))):
            idcg += ideal_scores[i] / np.log2(i + 2)
            
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        return {f"ndcg_at_{k}": ndcg}
