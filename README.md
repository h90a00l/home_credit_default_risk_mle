# home_credit_default_risk_mle
End-to-end machine learning project for credit default risk prediction using the Home Credit dataset, focusing on imbalanced classification, feature engineering across relational data, and production-oriented ML pipelines.

## Build the feature store

From the project root, run:

```bash
python -m src.etl.feature_store \
  --data-dir data \
  --application data/application_train.csv \
  --output data/feature_store_train.parquet
```

The output contains one row per `SK_ID_CURR`, retains `TARGET` when it exists
in the application file, and fills missing feature values with zero. Use
`--keep-missing` to preserve missing values.

To build the test feature store:

```bash
python -m src.etl.feature_store \
  --data-dir data \
  --application data/application_test.csv \
  --output data/feature_store_test.parquet
```
