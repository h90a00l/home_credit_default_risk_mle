# Feature Selection Results

The [feature selection notebook](../../notebooks/04_modeling_feature_selection.ipynb) evaluates whether smaller feature sets preserve the performance of the [baseline models](baseline_results.md): **Logistic Regression (LR)** and **Hist Gradient Boosting (HGB)**.

## Experiment

- **Data:** 184,506 training and 61,502 validation clients, with approximately 8.07% defaults. Initial correlation and permutation analyses explore feature relevance.
- **Evaluation:** five-fold stratified cross-validation on training data, comparing **10, 7, and 5 features** for each model. Within each outer training fold, an 80/20 stratified split supports permutation importance using Average Precision (AP) and five repeats. Each subset is then refitted on the full outer training fold and evaluated on its untouched validation fold.
- **Preprocessing:** median imputation for both models and standard scaling for LR, fitted within each training pipeline. Metrics and feature selection frequencies are tracked in MLflow.
- **Selection rule:** choose the smallest subset whose mean AP is at least the best mean AP minus its standard error (**One-SE rule**).

## Cross-validation results

**AP is the primary metric.** Values are mean ± sample standard deviation across five folds; bold rows indicate the One-SE selections.

| Model | Features | Average precision | ROC-AUC |
| --- | ---: | ---: | ---: |
| LR | 10 | 0.1349 ± 0.0027 | 0.6374 ± 0.0045 |
| LR | 7 | 0.1347 ± 0.0029 | 0.6368 ± 0.0046 |
| **LR** | **5** | **0.1338 ± 0.0026** | **0.6338 ± 0.0042** |
| HGB | 10 | 0.1447 ± 0.0024 | 0.6542 ± 0.0038 |
| **HGB** | **7** | **0.1438 ± 0.0028** | **0.6511 ± 0.0036** |
| HGB | 5 | 0.1365 ± 0.0044 | 0.6342 ± 0.0091 |

The One-SE thresholds are approximately **0.1337 for LR** and **0.1437 for HGB**. All LR subsets qualify; only the 10- and 7-feature HGB configurations qualify.

## Key conclusions

- **Feature relevance depends on the model.** `CC_UTIL_MEAN` leads the initial permutation rankings for both models. HGB also benefits from features with little importance for LR, including `CC_PAYMENT_TO_BALANCE_RATIO` and `PREV_CREDIT_TO_APPLICATION_RATIO_MEAN`.
- **Five-feature LR provides a stable, compact candidate.** AP decreases by only **0.83%** relative to its full baseline, and the same five predictors are selected in every fold.
- **Seven-feature HGB balances performance and simplicity.** AP decreases by approximately **0.63%**, with six predictors selected in all five folds and the seventh varying. Reducing to five features produces a larger **5.72%** AP loss and less stable selection.

**Carry forward five-feature LR and seven-feature HGB**, retaining their full baselines for comparison. HGB achieves higher AP, while LR tolerates greater feature reduction. Next steps are class imbalance experiments and hyperparameter optimization, followed by independent test-set evaluation.
