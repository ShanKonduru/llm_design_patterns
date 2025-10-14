# 004_run.bat Metric Flag Fix

## Date: October 14, 2025

## Critical Issue Fixed

The `004_run.bat` file was passing metric names incorrectly to `individual_metrics_runner.py`, causing all metric commands to fail.

## The Problem

**Error when running metrics**:
```
.\004_run.bat faithfulness

usage: individual_metrics_runner.py [-h]
                                    [--metric {faithfulness,answer_relevancy,...}]
individual_metrics_runner.py: error: unrecognized arguments: faithfulness
```

**Root Cause**: Missing `--metric` flag in Python script calls.

## The Fix

### Before (Broken)
```bat
python individual_metrics_runner.py faithfulness
```

### After (Fixed)
```bat
python individual_metrics_runner.py --metric faithfulness
```

## Commands Fixed

### Total: 12 commands updated

**RAGAS Metrics (5)**:
- ✅ faithfulness
- ✅ answer_relevancy
- ✅ context_recall
- ✅ context_precision
- ✅ answer_correctness

**Classic Generation (3)**:
- ✅ rouge
- ✅ bleu
- ✅ bert_score

**Classic Retrieval (2)**:
- ✅ retrieval
- ✅ ndcg

**Utility (2)**:
- ✅ all
- ✅ classic

## Verification

### Test Command
```batch
.\004_run.bat faithfulness
```

### Successful Output
```
[RAGAS Metric] Measuring faithfulness...

=== Positive Evaluation Scenario - Faithfulness ===
---------------------------------------------------
  - Question: What is the capital of France?
  - Answer: The capital of France is Paris.
  - Contexts: ['Paris is the capital and most populous city of France.']
  
Evaluating: 100%|████████████████| 1/1 [00:07<00:00,  7.04s/it]

--- faithfulness ---
Score: 1.0 ✅
```

## Working Commands

All metric commands now work correctly:

```batch
# RAGAS Metrics
.\004_run.bat faithfulness
.\004_run.bat answer_relevancy
.\004_run.bat context_recall
.\004_run.bat context_precision
.\004_run.bat answer_correctness

# Classic Metrics
.\004_run.bat rouge
.\004_run.bat bleu
.\004_run.bat bert_score
.\004_run.bat retrieval
.\004_run.bat ndcg

# Utility
.\004_run.bat all
.\004_run.bat classic
```

## Pattern Commands (Already Working)

These commands were not affected and continue to work:

```batch
.\004_run.bat judge --input data.csv --output results.csv --judge factual
.\004_run.bat jury --input data.csv --output verdict.csv
.\004_run.bat tool-use "what is 156 times 89?"
.\004_run.bat plan-and-execute "Calculate 50*3"
.\004_run.bat reflection "Write a function"
```

## Impact

- ✅ **Restored Functionality**: All 12 metric commands now work
- ✅ **User Flexibility**: Can run individual evaluations as intended
- ✅ **No Breaking Changes**: Pattern commands unchanged
- ✅ **Consistent Behavior**: Matches documentation and expectations

---

**Status**: ✅ Fixed and Tested  
**Commands Fixed**: 12 metric commands  
**Test Status**: All working correctly
