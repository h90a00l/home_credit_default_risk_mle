# Previous Application Feature Engineering – Glossary

All features are aggregated at the customer level:

> **One row per `SK_ID_CURR`**

These variables summarize the historical internal credit applications made by each customer based on `previous_application.csv`.

---

# 1. Application Volume

## 1.1 PREV_APP_COUNT

**Definition:**  
Total number of previous credit applications made by the customer.

**Interpretation:**  
Measures overall credit demand history within the institution.

**Signal captured:**
- Credit-seeking behavior intensity  
- Customer-bank interaction frequency  

---

## 1.2 PREV_APPROVED_COUNT

**Definition:**  
Number of previous applications that were approved.

**Interpretation:**  
Indicates successful past credit relationships.

---

## 1.3 PREV_REFUSED_COUNT

**Definition:**  
Number of previous applications that were refused.

**Interpretation:**  
Measures how often the institution previously rejected the customer.

**Risk intuition:**
- Higher values → possible historical risk concerns  

---

## 1.4 PREV_APPROVAL_RATIO

**Formula:**  
`APPROVAL_RATIO = PREV_APPROVED_COUNT / PREV_APP_COUNT`

**Interpretation:**  
Proportion of successful applications.

---

## 1.5 PREV_REFUSED_RATIO

**Formula:**  
`REFUSED_RATIO = PREV_REFUSED_COUNT / PREV_APP_COUNT`

**Interpretation:**  
Proportion of rejected applications.

---

## 1.6 PREV_HAS_REFUSED_FLAG

**Definition:**  
Binary indicator showing whether the customer has ever had a refused application.

**Rule:**  
`HAS_REFUSED = 1 if REFUSED_COUNT > 0 else 0`

**Interpretation:**  
Simple risk flag for past internal rejection.

---

# 2. Recency & Relationship Duration

## 2.1 PREV_DAYS_DECISION_MOST_RECENT

**Definition:**  
Number of days since the most recent previous application decision.

(Values are negative, representing days before the current application.)

**Interpretation:**  
Measures how recently the customer requested credit.

---

## 2.2 PREV_DAYS_DECISION_OLDEST

**Definition:**  
Number of days since the oldest recorded previous application.

**Interpretation:**  
Indicates how long the customer has been interacting with the institution.

---

## 2.3 PREV_DAYS_DECISION_SPAN

**Formula:**  
`DECISION_SPAN = MOST_RECENT - OLDEST`

**Interpretation:**  
Represents the total time span of the customer's application history.

---

## 2.4 PREV_LAST_1Y_APP_COUNT

**Definition:**  
Number of applications submitted within the last 12 months.

(Criteria: `DAYS_DECISION > -365`)

**Interpretation:**  
Captures recent credit-seeking intensity.

**Risk intuition:**
- Higher values → recent increase in leverage demand  

---

# 3. Financial Amount Features

## 3.1 PREV_AMT_CREDIT_MEAN

**Definition:**  
Average credit amount granted in previous applications.

**Interpretation:**  
Represents typical loan size historically granted.

---

## 3.2 PREV_AMT_CREDIT_MAX

**Definition:**  
Maximum credit amount ever granted.

**Interpretation:**  
Captures peak exposure level.

---

## 3.3 PREV_AMT_APPLICATION_MEAN

**Definition:**  
Average requested amount across previous applications.

**Interpretation:**  
Measures typical demand size.

---

## 3.4 PREV_AMT_ANNUITY_MEAN

**Definition:**  
Average annuity value of previous loans.

**Interpretation:**  
Represents typical installment burden.

---

# 4. Contract Structure

## 4.1 PREV_CNT_PAYMENT_MEAN

**Definition:**  
Average number of installments across previous loans.

**Interpretation:**  
Indicates typical loan duration.

---

## 4.2 PREV_CNT_PAYMENT_MAX

**Definition:**  
Maximum number of installments observed.

**Interpretation:**  
Captures longest repayment commitment.

---

# 5. Bank Adjustment Signals

## 5.1 PREV_CREDIT_TO_APPLICATION_RATIO_MEAN

**Formula:**  
`CREDIT_TO_APPLICATION_RATIO = AMT_CREDIT / AMT_APPLICATION`

(Mean across previous applications.)

**Interpretation:**  
Measures how much of the requested amount was actually granted.

**Risk intuition:**
- Values < 1 → bank reduced requested amount  
- Persistent reductions may indicate perceived risk  

---

## 5.2 PREV_CREDIT_MINUS_APPLICATION_MEAN

**Formula:**  
`CREDIT_MINUS_APPLICATION = AMT_CREDIT - AMT_APPLICATION`

(Mean across previous applications.)

**Interpretation:**  
Captures average deviation between requested and granted credit.

---

# Structural Summary

These features capture four key internal behavioral dimensions:

1. **Application Volume & Approval Behavior**
2. **Recency and Relationship Duration**
3. **Financial Exposure Levels**
4. **Institutional Adjustment Signals**

Together, they provide a compact and interpretable representation of the customer’s historical interaction with the institution’s credit process, which is highly relevant for default risk modeling.
