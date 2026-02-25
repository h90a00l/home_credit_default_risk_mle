# Bureau Feature Engineering – Glossary

All features are aggregated at the customer level:

> **One row per `SK_ID_CURR`**

These variables summarize the customer’s external credit exposure based on `bureau.csv`.

---

## 1. BUREAU_TOTAL_LOAN_COUNT

**Definition:**  
Total number of external credit records associated with the customer.

**Interpretation:**  
Measures historical exposure to credit outside the current institution.

**Risk intuition:**
- Very high → potential over-leverage  
- Very low → limited credit experience  

---

## 2. BUREAU_ACTIVE_LOAN_COUNT

**Definition:**  
Number of currently active external credit accounts.

**Interpretation:**  
Represents the customer's current external debt exposure.

---

## 3. BUREAU_CLOSED_LOAN_COUNT

**Definition:**  
Number of external credit accounts that have been closed.

**Interpretation:**  
Indicates historical credit relationships and completed obligations.

---

## 4. BUREAU_ACTIVE_LOAN_RATIO

**Definition:**  
Proportion of active loans relative to total loans.

**Formula:**  
`ACTIVE_LOAN_RATIO = Active Loans / (Active Loans + Closed Loans)`

**Interpretation:**  
Represents how much of the customer’s external credit history is still generating financial obligations.

**Risk intuition:**
- Close to 1 → highly leveraged  
- Close to 0 → mostly closed obligations  

---

## 5. BUREAU_DAYS_CREDIT_MOST_RECENT

**Definition:**  
Number of days since the most recent external credit was granted.

(Note: Values are negative because they represent days before the application date.)

**Interpretation:**
- Close to 0 → very recent credit activity  
- Very negative → older credit history  

---

## 6. BUREAU_DAYS_CREDIT_OLDEST

**Definition:**  
Number of days since the oldest external credit was granted.

**Interpretation:**  
Indicates how long the customer has been exposed to the credit system.

---

## 7. BUREAU_DAYS_CREDIT_SPAN

**Definition:**  
Difference between the most recent and the oldest credit record.

**Formula:**  
`CREDIT_SPAN = MOST_RECENT - OLDEST`

**Interpretation:**  
Represents the total length of the customer’s external credit history.

**Risk intuition:**
- Large span → experienced borrower  
- Small span → short credit history  

---

## 8. BUREAU_OVERDUE_LOAN_RATIO

**Definition:**  
Proportion of external loans that have ever had a recorded overdue amount greater than zero.

**Formula:**  
`OVERDUE_LOAN_RATIO = Loans with overdue / Total loans`

**Interpretation:**  
Captures historical delinquency behavior.

**Risk intuition:**
- Close to 1 → recurrent delinquency  
- 0 → no recorded overdue behavior  

---

## 9. BUREAU_ACTIVE_AMT_CREDIT_SUM_DEBT_SUM

**Definition:**  
Total outstanding debt across all active external credit accounts.

**Interpretation:**  
Represents the customer’s current external debt burden.

---

## 10. BUREAU_ACTIVE_AMT_CREDIT_SUM_SUM

**Definition:**  
Total credit amount granted across active external accounts.

**Interpretation:**  
Represents nominal active credit exposure.

---

## 11. BUREAU_ACTIVE_DEBT_RATIO

**Definition:**  
Ratio of outstanding debt to total granted credit for active accounts.

**Formula:**  
`ACTIVE_DEBT_RATIO = Debt Sum / Credit Sum`

**Interpretation:**
- Close to 1 → credit almost fully utilized  
- Close to 0 → low utilization  

**This is one of the strongest financial risk indicators in this feature set.**

---

## 12. BUREAU_ACTIVE_AMT_CREDIT_MAX_OVERDUE_MAX

**Definition:**  
Maximum overdue amount recorded among active external loans.

**Interpretation:**  
Measures the worst delinquency severity in currently active credit lines.

**Risk intuition:**
- High value → history of severe delinquency  
- Zero → no significant overdue among active loans  

---

## 13. BUREAU_RECENT_1Y_LOAN_COUNT

**Definition:**  
Number of external credit accounts opened within the last 12 months.

(Criteria: `DAYS_CREDIT > -365`)

**Interpretation:**  
Measures recent credit-seeking behavior.

**Risk intuition:**
- High → recent increase in leverage  
- Zero → stable borrowing behavior  

---

# Structural Summary

These features capture four fundamental dimensions of external credit risk:

1. **Credit Volume**
2. **Recency**
3. **Behavior**
4. **Current Leverage**

This feature set provides a strong and interpretable baseline representation of external credit exposure for default prediction models.
