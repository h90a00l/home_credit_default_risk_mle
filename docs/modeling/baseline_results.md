# Baseline Modeling Results

The [baseline notebook](../../notebooks/03_modeling_baseline.ipynb) tests whether 10 engineered features capture default risk and whether a nonlinear model improves on Logistic Regression. The experiment establishes a benchmark for subsequent modeling work.

## Experiment

- **Data:** 246,008 development clients, split into 184,506 training and 61,502 validation observations, stratified by target (`random_state=42`). Default prevalence is **8.07%**.
- **Features:** payment behavior, credit exposure, and previous application history, using the same 10 predictors for both models.
- **Models:** Logistic Regression and Hist Gradient Boosting, compared with a dummy that always predicts non-default.
- **Preprocessing:** median imputation for both models and standard scaling for Logistic Regression, fitted on training data through pipelines.
- **Evaluation:** a fixed **0.5 threshold**, without class weighting or hyperparameter tuning. Runs are tracked in MLflow; results below come from internal validation.

## Results

**ROC-AUC and average precision assess risk ranking; recall and precision assess default detection at the selected threshold.**

| Metric | Logistic Regression | Hist Gradient Boosting |
| --- | ---: | ---: |
| ROC-AUC | **0.64** | **0.65** |
| Average precision (AP) | **0.14** | **0.15** |
| Accuracy | 91.92% | 91.93% |
| Precision | 33.33% | 33.33% |
| Recall | **0.0403%** | **0.0201%** |
| F1-score | 0.000805 | 0.000403 |
| Defaults detected / actual defaults | **2 / 4,965** | **1 / 4,965** |

AP is logged as `pr_auc` in the notebook using `average_precision_score`. Threshold-dependent metrics are calculated from the saved confusion matrices to avoid rounding small recall and F1 values to zero.

The dummy achieves **91.93% accuracy** without detecting any defaults. Both learned models therefore offer little benefit at the default threshold, despite ranking above chance: their AP exceeds the approximately **0.0807** no-skill reference associated with default prevalence.

## Key conclusions

- **There is predictive signal, but separation is limited.** Default clients generally receive higher scores, yet the class distributions overlap substantially. For Logistic Regression, approximately 99% of actual defaults score at or below 0.28.
- **A threshold of 0.5 misses almost every default.** Logistic Regression flags only six clients and Hist Gradient Boosting only three. Their 33.33% precision is based on too few predictions to establish a reliable operating point; accuracy hides this failure.
- **Model complexity alone delivers little improvement.** Boosting increases ROC-AUC and AP by approximately 0.01, suggesting that feature coverage deserves further investigation. One split and two untuned models are insufficient to establish the cause or significance of this difference.

