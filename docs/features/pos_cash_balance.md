# POS_CASH_balance Feature Engineering – Glossary

All features are aggregated at the customer level:

> One row per `SK_ID_CURR`

These variables summarize the historical internal installment payment behavior of each customer based on `POS_CASH_balance.csv`.

---

# 1. Reporting Volume & Time Coverage

## 1.1 POS_RECORD_COUNT

Definition:  
Total number of monthly records available across all POS/Cash contracts for the customer.

Interpretation:  
Represents the total observation length of installment-based contracts.

Signal captured:
- Intensity of historical internal activity  
- Stability of reporting history  

---

## 1.2 POS_MONTHS_OLDEST

Definition:  
Oldest recorded month in the customer's POS/Cash history.

Note: `MONTHS_BALANCE` is typically negative; 0 represents the most recent month.

Interpretation:  
Indicates how far back installment-based contracts extend.

---

## 1.3 POS_MONTHS_MOST_RECENT

Definition:  
Most recent recorded month in the customer's POS/Cash history.

Interpretation:  
Confirms recency of installment contract activity.

---

## 1.4 POS_MONTH_SPAN

Definition:  
Difference between the most recent and oldest recorded month.

Formula:
POS_MONTH_SPAN = POS_MONTHS_MOST_RECENT - POS_MONTHS_OLDEST

Interpretation:  
Represents the total duration of observed installment behavior.

Signal captured:
- Relationship persistence  
- Long-term behavioral consistency  

---

# 2. Severity of Payment Delays

## 2.1 POS_DPD_MAX

Definition:  
Maximum Days Past Due (DPD) observed across all installment contracts.

Interpretation:  
Measures the worst payment delay severity.

Risk intuition:
- Higher values → severe historical payment problems  
- Zero → no observed delay  

---

## 2.2 POS_DPD_MEAN

Definition:  
Average DPD across all recorded months.

Interpretation:  
Represents typical delay level.

---

## 2.3 POS_DPD_DEF_MAX

Definition:  
Maximum value of `SK_DPD_DEF`, which reflects DPD under internal default definition rules.

Interpretation:  
Captures severity according to stricter internal risk criteria.

---

# 3. Frequency of Payment Delays

## 3.1 POS_DPD_RATIO

Definition:  
Proportion of months with DPD greater than zero.

Formula:
POS_DPD_RATIO = Months_with_DPD / POS_RECORD_COUNT

Interpretation:  
Measures how frequently payment delays occurred.

Risk intuition:
- Close to 1 → persistent late payments  
- Close to 0 → generally on-time payments  

---

## 3.2 POS_DPD_DEF_RATIO

Definition:  
Proportion of months flagged under internal default criteria.

Formula:
POS_DPD_DEF_RATIO = Months_with_DPD_DEF / POS_RECORD_COUNT

Interpretation:  
Measures frequency of behavior considered problematic by internal standards.

---

## 3.3 POS_RECENT_1Y_DPD_RATIO

Definition:  
Proportion of months with DPD greater than zero in the last 12 months.

Criteria: MONTHS_BALANCE > -365

Formula:
POS_RECENT_1Y_DPD_RATIO = Recent_1Y_Months_with_DPD / POS_RECORD_COUNT

Interpretation:  
Captures recent payment behavior.

Risk intuition:
- High value → recent deterioration in payment performance  
- Low value → stable recent behavior  

---

## 3.4 POS_HAS_DPD_FLAG

Definition:  
Binary indicator showing whether the customer has ever experienced payment delay.

Formula:
POS_HAS_DPD_FLAG = 1 if POS_DPD_MAX > 0, else 0

Interpretation:  
Simple and robust indicator of past payment issues.

---

# 4. Contract Progress

## 4.1 POS_INSTALLMENT_PROGRESS_MEAN

Definition:  
Average proportion of installments already paid.

Formula:
INSTALLMENT_PROGRESS = (CNT_INSTALMENT - CNT_INSTALMENT_FUTURE) / CNT_INSTALMENT

(Mean across all contracts and months.)

Interpretation:  
Measures how advanced installment contracts typically are.

Signal captured:
- Early-stage borrowers vs late-stage borrowers  
- Contract maturity exposure  

---

# Structural Summary

These features capture four core internal behavioral dimensions:

1. Exposure Duration – length and stability of installment contracts  
2. Severity of Delay – worst payment behavior observed  
3. Frequency of Delay – consistency of late payments  
4. Contract Progression – stage of repayment lifecycle  

Together, they provide a compact and high-signal representation of internal payment behavior, which is typically one of the strongest predictors of default risk.