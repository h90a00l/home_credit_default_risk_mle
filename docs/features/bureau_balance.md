# Bureau Balance Feature Engineering – Glossary

All features are aggregated at the loan level:

> **One row per `SK_ID_BUREAU`**

These variables summarize the monthly behavioral history of each external credit account based on `bureau_balance.csv`.

---

## 1. BUREAU_BALANCE_RECORD_COUNT

**Definition:**  
Total number of monthly records available for the loan.

**Interpretation:**  
Represents how many months of history are recorded for the external credit account.

**Signal captured:**
- Length of monitoring history  
- Stability of the reporting period  

---

## 2. BUREAU_BALANCE_OLDEST_MONTH

**Definition:**  
Oldest recorded month in the loan history (minimum `MONTHS_BALANCE`).

> `MONTHS_BALANCE` is typically negative, where 0 represents the most recent month.

**Interpretation:**  
Indicates how far back the loan’s reporting history extends.

---

## 3. BUREAU_BALANCE_MOST_RECENT_MONTH

**Definition:**  
Most recent recorded month in the loan history (maximum `MONTHS_BALANCE`).

**Interpretation:**  
Usually close to 0. Confirms recency of reporting.

---

## 4. BUREAU_BALANCE_MONTH_SPAN

**Definition:**  
Difference between the most recent and oldest recorded month.

**Formula:**  
`MONTH_SPAN = MOST_RECENT_MONTH - OLDEST_MONTH`

**Interpretation:**  
Represents the total duration of the loan’s recorded behavioral history.

**Signal captured:**
- Persistence of credit relationship  
- Stability over time  

---

## 5. BUREAU_BALANCE_DPD_MAX

**Definition:**  
Maximum Days Past Due (DPD) level observed in the loan’s history.

(Only numeric `STATUS` values 0–5 are considered.)

**Interpretation:**  
Measures the most severe payment delay recorded.

**Risk intuition:**
- Higher values → more severe historical payment issues  
- Zero → no recorded delay  

---

## 6. BUREAU_BALANCE_DPD_RATIO

**Definition:**  
Proportion of months where DPD was greater than zero.

**Formula:**  
`DPD_RATIO = Months with positive DPD / Total recorded months`

**Interpretation:**  
Captures the frequency of payment delays throughout the loan’s history.

**Risk intuition:**
- Close to 1 → persistent payment issues  
- Close to 0 → generally consistent payments  

---

## 7. BUREAU_BALANCE_HAS_POSITIVE_DPD

**Definition:**  
Binary indicator showing whether the loan has ever experienced a positive DPD.

**Rule:**  
`HAS_POSITIVE_DPD = 1 if DPD_MAX > 0 else 0`

**Interpretation:**  
Simple indicator of any historical payment delay.

**Signal captured:**
- Existence of payment issues (regardless of severity)

---

# Structural Summary

These features capture three fundamental behavioral dimensions of each external loan:

1. **History Length** – duration and persistence of reporting  
2. **Severity of Delay** – maximum DPD observed  
3. **Frequency of Delay** – proportion of months with payment issues  

This compact feature set provides a robust representation of historical payment behavior without excessive dimensionality.
