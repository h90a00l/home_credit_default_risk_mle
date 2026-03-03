# Installment Payments Feature Engineering – Glossary

All features are aggregated at the customer level:

> One row per `SK_ID_CURR`

These variables summarize the historical installment payment behavior of each client based on `installments_payments.csv`.

The focus is on delay behavior, payment discipline, recency effects, and behavioral deterioration over time.

---

## 1. INST_DPD_MEAN

**Definition:**  
Average Days Past Due (DPD) across all installments.

DPD is calculated as:  
DPD = max(0, DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT)

**Interpretation:**  
Represents the typical delay behavior of the client.

**Signal captured:**
- Chronic delay behavior  
- General payment discipline  

---

## 2. INST_DPD_MAX

**Definition:**  
Maximum Days Past Due observed across all installments.

**Interpretation:**  
Captures the worst historical delinquency episode.

**Signal captured:**
- Extreme delinquency  
- Tail risk behavior  

---

## 3. INST_LATE_RATIO

**Definition:**  
Proportion of installments paid late.

Calculated as:  
Number of installments with DPD > 0 divided by total number of installments.

**Interpretation:**  
Measures how frequently the client pays late.

**Signal captured:**
- Behavioral consistency  
- Chronic delinquency tendency  

---

## 4. INST_DPD_30_RATIO

**Definition:**  
Proportion of installments with DPD greater than 30 days.

**Interpretation:**  
Measures frequency of severe DPD.

**Signal captured:**
- Material credit deterioration  
- Risk of transition into default  

---

## 5. INST_PAYMENT_RATIO_MEAN

**Definition:**  
Average ratio between amount paid and amount expected.

Calculated as:  
AMT_PAYMENT divided by AMT_INSTALMENT

**Interpretation:**  
Indicates whether the client tends to fully meet installment obligations.

**Signal captured:**
- Payment sufficiency  
- Financial stress behavior  

---

## 6. INST_PAYMENT_RATIO_MIN

**Definition:**  
Minimum observed payment ratio across all installments.

**Interpretation:**  
Captures the worst underpayment event in history.

**Signal captured:**
- Extreme underpayment behavior  
- Liquidity constraints  

---

## 7. INST_LOW_PAYMENT_RATIO

**Definition:**  
Proportion of installments where the amount paid was lower than the amount due.

Calculated as:  
Number of installments with AMT_PAYMENT < AMT_INSTALMENT divided by total installments.

**Interpretation:**  
Measures frequency of partial payments.

**Signal captured:**
- Recurrent underpayment  
- Potential financial instability  

---

## 8. INST_RECENT_DPD_MEAN_90D

**Definition:**  
Average Days Past Due considering only installments with scheduled date within the last 90 days of the dataset timeline.

**Interpretation:**  
Captures recent delay behavior.

**Signal captured:**
- Short-term deterioration  
- Immediate credit risk signal  

---

## 9. INST_RECENT_LATE_RATIO_90D

**Definition:**  
Proportion of installments paid late within the last 90 days.

**Interpretation:**  
Measures recent delinquency frequency.

**Signal captured:**
- Current payment discipline  
- Near-term default probability  

---

## 10. INST_DPD_TREND

**Definition:**  
Linear trend (slope) of Days Past Due over time, using DAYS_INSTALMENT as the time axis.

**Interpretation:**  
Measures whether delay behavior is improving or worsening over time.

**Signal captured:**
- Behavioral deterioration  
- Risk acceleration  

Positive values indicate increasing delinquency over time.  
Negative values indicate improving payment behavior.

---
