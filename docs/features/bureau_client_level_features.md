# Bureau + Bureau Balance (Client Level) - Feature Glossary

These features are created in `src/etl/bureau_client_level_features.py` by the `build_client_level_bureau_features` function.

Aggregation is at the client level:

> **One row per `SK_ID_CURR`**

The expected input dataset is at contract level (`SK_ID_BUREAU`) and already includes columns derived from `bureau.csv` and `bureau_balance.csv`.

---

## Aggregation Base

## 1. SK_ID_BUREAU_COUNT

**Definition:**  
Number of bureau contracts linked to the client.

**Calculation:**  
`count(SK_ID_BUREAU)`

**Interpretation:**  
Proxy for external credit relationship volume.

---

## DPD Signals

## 2. BUREAU_BALANCE_DPD_MAX_MAX

**Definition:**  
Highest contract-level DPD max across all client contracts.

**Calculation:**  
`max(BUREAU_BALANCE_DPD_MAX)`

**Interpretation:**  
Worst observed payment delay severity in the external portfolio.

## 3. BUREAU_BALANCE_DPD_MAX_MEAN

**Definition:**  
Average contract-level DPD max across the client's contracts.

**Calculation:**  
`mean(BUREAU_BALANCE_DPD_MAX)`

**Interpretation:**  
Average severity of payment delays across contracts.

## 4. BUREAU_BALANCE_DPD_RATIO_MEAN

**Definition:**  
Average share of months with positive DPD across contracts.

**Calculation:**  
`mean(BUREAU_BALANCE_DPD_RATIO)`

**Interpretation:**  
Average frequency of payment delays in the contract set.

## 5. BUREAU_BALANCE_DPD_RATIO_MAX

**Definition:**  
Maximum share of months with positive DPD among client contracts.

**Calculation:**  
`max(BUREAU_BALANCE_DPD_RATIO)`

**Interpretation:**  
Shows whether at least one contract has persistent payment delays.

## 6. BUREAU_BALANCE_HAS_POSITIVE_DPD_SUM

**Definition:**  
Number of contracts with at least one month of positive DPD.

**Calculation:**  
`sum(BUREAU_BALANCE_HAS_POSITIVE_DPD)`

**Interpretation:**  
Absolute count of contracts with payment delay history.

## 7. BUREAU_BALANCE_HAS_POSITIVE_DPD_MEAN

**Definition:**  
Share of contracts with at least one month of positive DPD.

**Calculation:**  
`mean(BUREAU_BALANCE_HAS_POSITIVE_DPD)`

**Interpretation:**  
Percentage of the client's external contracts with payment delay history.

## 8. BUREAU_BALANCE_DPD_RATIO_WEIGHTED_MEAN

**Definition:**  
Weighted average of DPD ratio, using each contract history length as weight.

**Calculation:**  
`sum(BUREAU_BALANCE_DPD_RATIO * BUREAU_BALANCE_MONTH_SPAN) / sum(BUREAU_BALANCE_MONTH_SPAN)`

**Interpretation:**  
Gives more weight to longer contract histories and reduces noise from short histories.

## 9. HAS_RECENT_DPD

**Definition:**  
Binary flag indicating recent DPD signal.

**Contract-level rule:**  
`has_recent_dpd = 1 if (BUREAU_DAYS_CREDIT_MOST_RECENT >= -3 and BUREAU_BALANCE_DPD_MAX > 0) else 0`

**Client-level aggregation:**  
`HAS_RECENT_DPD = max(has_recent_dpd)`

**Interpretation:**  
Indicates whether the client has at least one contract with recent DPD signal.

---

## Historical Time Window

## 10. BUREAU_BALANCE_MONTH_SPAN_MEAN

**Definition:**  
Average contract history length in months.

**Calculation:**  
`mean(BUREAU_BALANCE_MONTH_SPAN)`

**Interpretation:**  
Average observation window across external contracts.

## 11. BUREAU_BALANCE_MONTH_SPAN_MAX

**Definition:**  
Longest contract history length among client contracts.

**Calculation:**  
`max(BUREAU_BALANCE_MONTH_SPAN)`

**Interpretation:**  
Captures maximum available historical depth.

## 12. BUREAU_BALANCE_OLDEST_MONTH_MAX

**Definition:**  
Maximum value of `BUREAU_BALANCE_OLDEST_MONTH` across contracts.

**Calculation:**  
`max(BUREAU_BALANCE_OLDEST_MONTH)`

**Interpretation:**  
Since `MONTHS_BALANCE` is usually negative, higher values are closer to 0.

## 13. BUREAU_BALANCE_OLDEST_MONTH_MIN

**Definition:**  
Minimum value of `BUREAU_BALANCE_OLDEST_MONTH` across contracts.

**Calculation:**  
`min(BUREAU_BALANCE_OLDEST_MONTH)`

**Interpretation:**  
Represents the farthest historical point across all contract histories.

## 14. BUREAU_BALANCE_MOST_RECENT_MONTH_MAX

**Definition:**  
Maximum value of `BUREAU_BALANCE_MOST_RECENT_MONTH` across contracts.

**Calculation:**  
`max(BUREAU_BALANCE_MOST_RECENT_MONTH)`

**Interpretation:**  
Most recently updated contract.

## 15. BUREAU_BALANCE_MOST_RECENT_MONTH_MIN

**Definition:**  
Minimum value of `BUREAU_BALANCE_MOST_RECENT_MONTH` across contracts.

**Calculation:**  
`min(BUREAU_BALANCE_MOST_RECENT_MONTH)`

**Interpretation:**  
Least recent contract in terms of latest reported month.

---

## Credit Recency (bureau)

## 16. BUREAU_DAYS_CREDIT_MOST_RECENT_MAX

**Definition:**  
Maximum value of `BUREAU_DAYS_CREDIT_MOST_RECENT` across contracts.

**Calculation:**  
`max(BUREAU_DAYS_CREDIT_MOST_RECENT)`

**Interpretation:**  
Because values are usually negative, higher values indicate more recent credit activity.

## 17. BUREAU_DAYS_CREDIT_MOST_RECENT_MIN

**Definition:**  
Minimum value of `BUREAU_DAYS_CREDIT_MOST_RECENT` across contracts.

**Calculation:**  
`min(BUREAU_DAYS_CREDIT_MOST_RECENT)`

**Interpretation:**  
Represents the least recent contract within the client's set.

---

## Structural Summary

Final features cover four main signal blocks:

1. **Contract volume** (`SK_ID_BUREAU_COUNT`)
2. **DPD risk profile** (severity, frequency, recent DPD signal)
3. **Historical depth** (month spans and month boundaries)
4. **External credit recency** (`BUREAU_DAYS_CREDIT_MOST_RECENT_*`)
