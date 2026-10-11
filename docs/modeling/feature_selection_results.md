# Feature Selection Results

The [feature selection notebook](../../notebooks/04_modeling_feature_selection.ipynb) extends the [baseline experiment](baseline_results.md) to test whether smaller feature sets preserve performance in **Logistic Regression (LR)** and **Hist Gradient Boosting (HGB)**.

## Experiment

- **Data:** 184,506 training and 61,502 validation clients, with approximately 8.07% defaults.
- **Selection:** training-set Pearson correlations and model-specific permutation importance on validation data, using Average Precision (AP) and 10 repeats.
- **Evaluation:** five-fold stratified cross-validation on training data (`random_state=42`), comparing 10/7/5 features for LR and 10/8/5 for HGB.
- **Preprocessing:** median imputation for both models and standard scaling for LR, fitted within each fold. Subset results and configurations are tracked in MLflow.

## Feature relevance

Linear correlations with the target are weak; `CC_UTIL_MEAN` has the strongest positive correlation (**0.13**) and ranks first in permutation importance for both models.

**Feature relevance depends on the model.** HGB benefits from `CC_PAYMENT_TO_BALANCE_RATIO` and `PREV_CREDIT_TO_APPLICATION_RATIO_MEAN`, which contribute little to LR. Both models assign negligible or negative importance to `POS_DPD_RATIO` and `INST_DPD_30_RATIO`; removing these two defines the **eight-feature HGB candidate**.

The top-5 subsets share `CC_UTIL_MEAN`, `PREV_REFUSED_RATIO`, `BUREAU_ACTIVE_DEBT_RATIO`, and `BUREAU_ACTIVE_LOAN_COUNT`. Their fifth feature differs: `INST_LATE_RATIO` for LR and `CC_PAYMENT_TO_BALANCE_RATIO` for HGB.

## Cross-validation results

Values are **mean ± standard deviation across five folds**. AP is the primary comparison metric.

| Model | Features | Average precision | ROC-AUC |
| --- | ---: | ---: | ---: |
| LR | 10 | 0.13492 ± 0.00241 | 0.63742 ± 0.00401 |
| LR | 7 | 0.13465 ± 0.00260 | 0.63683 ± 0.00454 |
| LR | 5 | 0.13380 ± 0.00235 | 0.63378 ± 0.00378 |
| HGB | 10 | 0.14475 ± 0.00219 | 0.65417 ± 0.00339 |
| **HGB** | **8** | **0.14566 ± 0.00220** | **0.65391 ± 0.00312** |
| HGB | 5 | 0.13538 ± 0.00275 | 0.62847 ± 0.00495 |

## Key conclusions

- **Eight-feature HGB offers the strongest AP.** Removing two features improves mean AP by **0.000914**, with gains in all five folds and nearly unchanged ROC-AUC. The improvement is small.
- **LR tolerates stronger reduction.** Moving from 10 to 5 features reduces AP by only **0.83%** relative to its baseline. The same reduction for HGB lowers AP by approximately **6.48%**, indicating that its broader feature set matters.
- **Retain eight-feature HGB as the primary candidate**, with the complete set as a benchmark for class imbalance experiments and hyperparameter optimization.
