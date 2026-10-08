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
`--keep-missing` to preserve missing values. All feature analysis was performed keeping missing values.

To build the test feature store:

```bash
python -m src.etl.feature_store \
  --data-dir data \
  --application data/application_test.csv \
  --output data/feature_store_test.parquet
```

## Temporal availability rules

All builders filter observation dates before aggregating. Dates must be numeric,
non-null, finite and strictly negative relative to the current application.
Day/month zero is conservatively excluded because within-period availability is
unknown. Exclusions emit a warning with the count and checked columns; raw CSVs
are not modified and no quarantine file is produced.

| Source | Required historical observation dates |
| --- | --- |
| bureau | DAYS_CREDIT and DAYS_CREDIT_UPDATE |
| bureau_balance, POS_CASH_balance, credit_card_balance | MONTHS_BALANCE |
| previous_application | DAYS_DECISION |
| installments_payments | DAYS_ENTRY_PAYMENT |

The same bureau filter applies to the bureau-to-client mapping, so rejected
contracts cannot re-enter through bureau_balance. DAYS_CREDIT_UPDATE is now a
required input. Clients supplied through the application file remain in the
output even if all their source rows are excluded.

Installment features describe observed payments. Missing payment dates are
excluded, not treated as on-time payments; these features do not reconstruct
unpaid installments at the cutoff. A future scheduled due date is allowed when
payment already occurred, but the recent due-date window is [-90, -1] days.
POS recency uses [-12, -1] months and divides late records by records within that
window. Bureau recent DPD uses actual monthly statuses in [-3, -1], aggregated
first by contract, then by client. Credit card recency uses [-3, -1] months.

These checks rely on source dates accurately representing data availability;
they do not reconstruct historical snapshots or later corrections.
TARGET remains a label in the output: remove TARGET and SK_ID_CURR from model
predictors. Fit supervised binning and other learned transformations only on
training folds.

Existing feature store files must be rebuilt with the command above to reflect
these changes. Run regression checks with:

```bash
venv/bin/python -m unittest discover -s tests -v
```
