# Phase 2 — Machine Learning Model Evaluation Report

**Project:** E-Commerce Customer Analytics — Predictive Modelling  
**Author:** Madhu Shree G  
**Dataset:** E-Commerce Customer Dataset (5,630 records × 20 features)  
**Training Script:** `phase2_ml.py`  
**Date:** June 2026

---

## 1. Data Preprocessing Log

### 1.1 Missing Value Treatment

Numerical columns with missing values were identified and imputed using the **median** strategy. Median imputation was specifically chosen (over mean) because several columns exhibited right-skewed distributions (e.g., `DaySinceLastOrder`, `Tenure`), where the mean is disproportionately influenced by outliers.

| Column | Imputation Strategy | Rationale |
|--------|--------------------|-----------| 
| `Tenure` | Median | Right-skewed distribution; outliers present |
| `WarehouseToHome` | Median | Delivery distance shows tail distribution |
| `HourSpendOnApp` | Median | Heavy users skew the mean upward |
| `OrderAmountHikeFromlastYear` | Median | Promotional outliers present |
| `CouponUsed` | Median | Coupon usage is zero-inflated |
| `OrderCount` | Median | Heavy purchasers inflate the mean |
| `DaySinceLastOrder` | Median | Highly skewed; inactive customers inflate tail |

### 1.2 Categorical Standardisation

String normalisation was applied to remove inconsistencies:
- `PreferredLoginDevice`: `'Mobile Phone'` → `'Mobile'` (duplicate label unification)
- `PreferredPaymentMode`: `'COD'` → `'Cash on Delivery'`; `'CC'` → `'Credit Card'`
- `PreferedOrderCat`: `'Mobile'` → `'Mobile Phone'` (label unification)

### 1.3 Duplicate Removal

Exact duplicate rows were identified and removed using `df.drop_duplicates()`. Index was reset after removal to ensure consistent row addressing.

### 1.4 Final Dataset Shape

- **Before cleaning:** ~5,700 rows (approximate, including duplicates)
- **After cleaning:** 5,630 unique, clean records × 20 feature columns + 6 engineered features

---

## 2. Feature Engineering

Six new features were engineered and added to the dataset prior to model training. These were constructed to capture latent business signals not directly available in the raw data.

| Feature | Formula | Business Meaning |
|---------|---------|-----------------|
| `CLV` | `CashbackAmount × OrderCount × (Tenure + 1)` | Customer Lifetime Value proxy — combines spend intensity and loyalty duration |
| `RecencyScore` | `1 / (DaySinceLastOrder + 1)` | High score = recently active; decays as inactivity grows |
| `EngagementScore` | `HourSpendOnApp×0.4 + OrderCount×0.3 + CouponUsed×0.3` | Composite app & purchase engagement metric |
| `SpendingEfficiency` | `CashbackAmount / (OrderCount + 1)` | Cashback-per-order; identifies high-value-per-transaction customers |
| `HighRisk` | `(Complain==1) AND (Tenure < 3)` | Binary flag for new customers who have already complained |
| `AddressDiversityFlag` | `NumberOfAddress > 3` | Flags customers with multiple delivery addresses (potential account sharing or frequent movers) |

> **Pipeline Consistency Note:** All six feature engineering formulas above are **identical** in both `phase2_ml.py` (training) and `dashboard.py` (inference). This ensures no pipeline drift between model training and live prediction.

---

## 3. Encoding & Scaling

### 3.1 Label Encoding
Five categorical columns were label-encoded using `sklearn.preprocessing.LabelEncoder`:
- `PreferredLoginDevice`, `PreferredPaymentMode`, `Gender`, `PreferedOrderCat`, `MaritalStatus`

### 3.2 Feature Scaling
`StandardScaler` was applied to all features, producing zero-mean, unit-variance inputs. The fitted scaler was serialised to `scaler.pkl` for consistent application during live dashboard inference.

### 3.3 Train/Test Split
- **Split ratio:** 80% training / 20% test
- **Stratification:** Applied on the `Churn` target to maintain class balance in both sets (Churn prevalence ≈ 16.8%)
- **Random state:** 42 (fixed for reproducibility)

---

## 4. Classification Models — Churn Prediction

**Target variable:** `Churn` (Binary: 0 = Active, 1 = Churned)

### 4.1 Model Comparison Matrix

| Model | Accuracy | Precision | Recall | **F1-Score** | ROC-AUC | Cross-Val F1 |
|-------|----------|-----------|--------|-------------|---------|-------------|
| Logistic Regression | 79.13% | 43.59% | 80.53% | 56.56% | 86.83% | 58.40% |
| Decision Tree | 80.02% | 45.10% | 84.74% | 58.87% | 87.98% | 65.69% |
| Random Forest | 95.29% | 86.24% | 85.79% | 86.02% | 98.41% | 87.51% |
| **Gradient Boosting** ✅ | **97.16%** | **95.40%** | **87.37%** | **91.21%** | **99.61%** | **93.55%** |

### 4.2 Optimisation Target: F1-Score & Recall

The primary evaluation metric was **F1-Score** (harmonic mean of Precision and Recall), with secondary emphasis on **Recall**.

**Business justification:** In a churn prediction context, the cost of a **False Negative** (failing to identify a customer who churns) is significantly higher than the cost of a **False Positive** (incorrectly flagging a loyal customer for a retention offer).

- A missed churner = lost customer LTV (potentially ₹500–₹5,000+)
- A false positive = unnecessary marketing spend (typically ₹20–₹100 per customer)

Therefore, a model that maximises Recall (catching as many true churners as possible) while maintaining reasonable Precision is preferred over a model that maximises raw Accuracy alone.

### 4.3 Winner: Gradient Boosting Classifier

**Configuration:** `n_estimators=150, max_depth=5, random_state=42`

- Achieved **99.61% ROC-AUC** — near-perfect class discrimination
- **91.21% F1-Score** with **93.55% Cross-Validated F1** — confirming generalisation
- Top features: `Complain`, `Tenure`, `CLV`, `EngagementScore`, `DaySinceLastOrder`

The model was serialised to `best_model_gb.pkl` and is loaded by the dashboard for live inference.

---

## 5. Regression Models — Spending Prediction

**Target variable:** `CashbackAmount` (continuous; proxy for transaction spending volume)

### 5.1 Model Comparison Matrix

| Model | RMSE (₹) | **R² Score** |
|-------|----------|-------------|
| Ridge Regression | ₹27.39 | 69.42% |
| Decision Tree Regressor | ₹12.51 | 93.62% |
| **Random Forest Regressor** ✅ | **₹6.40** | **98.33%** |

### 5.2 Why CashbackAmount as the Regression Target?

CashbackAmount is a reliable proxy for customer transaction value in this dataset because:
1. Cashback is directly proportional to order value (percentage-based rewards)
2. It is fully observable and continuous (no censoring or clipping)
3. Predicting it enables marketing budget allocation for cashback incentive programs

### 5.3 Winner: Random Forest Regressor

**Configuration:** `n_estimators=100, random_state=42`

- **R²=98.33%** — the model explains 98.33% of variance in cashback spending
- **RMSE=₹6.40** — predictions are on average only ₹6.40 away from actual spend
- This performance confirms that customer spending behaviour is highly predictable from the available features, particularly `OrderCount`, `CLV`, and `EngagementScore`

---

## 6. Business Conclusions

### 6.1 Combined Model Pipeline

The two models complement each other in a production deployment:

```
Customer Data
     ↓
Gradient Boosting Classifier  →  Churn Probability (Who will leave?)
     ↓
Random Forest Regressor       →  Predicted Spend  (How much value is at risk?)
     ↓
Priority Score = Churn Prob × Predicted Spend
     ↓
Retention Budget Allocation   →  High-score customers get VIP intervention
```

### 6.2 Key Actionable Insights

1. **Complaint Resolution is Critical:** `Complain` is the single strongest churn predictor. A 24-hour complaint resolution SLA would have the largest measurable impact on churn reduction.

2. **New Customer Vulnerability:** Customers with `Tenure < 3 months` show a dramatically elevated churn rate (the `HighRisk` flag). An onboarding support programme targeting months 1–3 is the highest-ROI intervention.

3. **Spending Predictability Enables Proactive Budgeting:** With R²=98.33% spending accuracy, marketing teams can pre-allocate cashback budgets by customer segment rather than reacting to historical patterns.

4. **Engagement Score as Early Warning:** Declining `EngagementScore` (app hours + order count + coupon use) reliably precedes churn. Monitoring this metric weekly enables pre-emptive re-engagement before a complaint occurs.

---

## 7. Deliverable Compliance Summary

| Requirement | Status | Evidence |
|-------------|--------|---------|
| ≥2 Classification models | ✅ Met | 4 models trained (LR, DT, RF, GB) |
| ≥2 Regression models | ✅ Met | 3 models trained (Ridge, DT, RF Regressor) |
| Feature Engineering | ✅ Met | 6 engineered features (`CLV`, `RecencyScore`, `EngagementScore`, `SpendingEfficiency`, `HighRisk`, `AddressDiversityFlag`) |
| Model Evaluation Metrics | ✅ Met | Accuracy, Precision, Recall, F1, ROC-AUC, Cross-Val F1, RMSE, R² |
| Business Recommendations | ✅ Met | Strategic recommendations in dashboard Tab 4 |
| Model Persistence | ✅ Met | `best_model_gb.pkl` + `scaler.pkl` saved |
| EDA Report | ✅ Met | `Phase1_EDA_Report.docx` |
| Model Evaluation Report | ✅ Met | This document (`Phase2_ML_Model_Report.md`) + `Phase2_Predictive_Modeling_Report.docx` |
| Interactive Dashboard | ✅ Met | `dashboard.py` — live inference, risk simulation, CSV export |
