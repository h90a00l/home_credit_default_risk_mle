# Credit Card Balance Feature Engineering – Glossary

All features are aggregated at the customer level:

> One row per `SK_ID_CURR`

These variables summarize the credit card usage behavior of each client based on `credit_card_balance.csv`.

The focus is on credit utilization, payment behavior, default, activity level, and debt evolution over time.

---

## 1. CC_UTIL_MEAN

**Definition:**  
Average credit utilization ratio across all months.

Calculated as:  
AMT_BALANCE divided by AMT_CREDIT_LIMIT_ACTUAL

**Interpretation:**  
Represents how much of the available credit limit the client typically uses.

**Signal captured:**
- Credit dependency  
- Financial pressure  

---

## 2. CC_UTIL_MAX

**Definition:**  
Maximum credit utilization observed.

**Interpretation:**  
Captures the highest level of credit usage reached by the client.

**Signal captured:**
- Peak financial stress  
- Limit saturation behavior  

---

## 3. CC_PAYMENT_RATIO_MEAN

**Definition:**  
Average ratio between payment amount and outstanding balance.

Calculated as:  
AMT_PAYMENT_TOTAL_CURRENT divided by AMT_BALANCE

**Interpretation:**  
Indicates how much of the outstanding balance the client pays on average.

**Signal captured:**
- Payment discipline  
- Ability to reduce debt  

---

## 4. CC_LOW_PAYMENT_RATIO

**Definition:**  
Proportion of months where the payment was lower than the outstanding balance.

Calculated as:  
Number of months with AMT_PAYMENT_TOTAL_CURRENT < AMT_BALANCE divided by total months.

**Interpretation:**  
Measures how often the client fails to fully cover the balance.

**Signal captured:**
- Revolving credit behavior  
- Financial stress  

---

## 5. CC_DPD_MEAN

**Definition:**  
Average Days Past Due (DPD) across all months.

**Interpretation:**  
Represents the typical delay in credit card payments.

**Signal captured:**
- Chronic default  
- Payment discipline  

---

## 6. CC_DPD_MAX

**Definition:**  
Maximum Days Past Due observed.

**Interpretation:**  
Captures the worst default episode.

**Signal captured:**
- Severe credit events  
- Tail risk  

---

## 7. CC_ACTIVE_RATIO

**Definition:**  
Proportion of months where the client had a positive balance.

Calculated as:  
Number of months with AMT_BALANCE > 0 divided by total months.

**Interpretation:**  
Measures how frequently the client uses the credit card.

**Signal captured:**
- Exposure to credit  
- Usage behavior  

---

## 8. CC_DRAWINGS_MEAN

**Definition:**  
Average amount drawn (used) from the credit card.

Based on:  
AMT_DRAWINGS_CURRENT

**Interpretation:**  
Represents the typical level of spending or cash usage.

**Signal captured:**
- Consumption intensity  
- Credit dependency  

---

## 9. CC_RECENT_UTIL_MEAN_3M

**Definition:**  
Average credit utilization over the last 3 months.

Filter applied:  
MONTHS_BALANCE >= -3

**Interpretation:**  
Captures recent credit usage behavior.

**Signal captured:**
- Short-term financial stress  
- Recent behavioral changes  

---

## 10. CC_BALANCE_TREND

**Definition:**  
Linear trend (slope) of credit card balance over time, using MONTHS_BALANCE as the time axis.

**Interpretation:**  
Measures whether the outstanding balance is increasing or decreasing over time.

**Signal captured:**
- Debt accumulation  
- Financial deterioration  

Positive values indicate increasing debt over time.  
Negative values indicate decreasing balance.
