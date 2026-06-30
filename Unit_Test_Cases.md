# Unit Test Cases
## E-Commerce Customer Analytics Dashboard
**Author:** Madhu Shree G
**Total Test Cases:** 25 | **Pass:** 20 | **Fail (Intentional):** 5

---

## Module 1 — Data Cleaning

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-CLEAN-01 | Check if `'Mobile Phone'` in `PreferredLoginDevice` is replaced with `'Mobile'` after running the cleaning function | `'Mobile Phone'` should not exist in the column after cleaning | `'Mobile Phone'` is absent — all values are unified to `'Mobile'` | ✅ Pass |
| TC-CLEAN-02 | Check if `'COD'` is replaced with `'Cash on Delivery'` and `'CC'` is replaced with `'Credit Card'` in `PreferredPaymentMode` | Neither `'COD'` nor `'CC'` should appear; `'Cash on Delivery'` should be present | Both shorthand labels are correctly expanded | ✅ Pass |
| TC-CLEAN-03 | Check if all 7 numeric columns (`Tenure`, `WarehouseToHome`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`, `CouponUsed`, `OrderCount`, `DaySinceLastOrder`) have zero missing values after median imputation | `isnull().sum() == 0` for all 7 columns | All 7 columns have 0 null values after imputation | ✅ Pass |
| TC-CLEAN-04 | Inject a duplicate of row 0 into the DataFrame and verify it is removed by `drop_duplicates()` | `df.duplicated().sum() == 0` after cleaning | Duplicate row is dropped; no duplicates remain | ✅ Pass |
| TC-CLEAN-05 *(Intentional Fail)* | On the **raw uncleaned** DataFrame, assert that `'Mobile'` does NOT exist in `PreferedOrderCat` | `'Mobile'` should not be present | Raw data DOES contain `'Mobile'` — cleaning has not been applied yet | ❌ Fail |

---

## Module 2 — Feature Engineering

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-FEAT-01 | Verify CLV formula: `CashbackAmount × OrderCount × (Tenure + 1)` using Row 0 values: `CashbackAmount=150`, `OrderCount=3`, `Tenure=1.0` | `CLV = 150 × 3 × (1+1) = 900.0` | CLV computed as `900.0` — formula is correct | ✅ Pass |
| TC-FEAT-02 | Verify RecencyScore formula: `1 / (DaySinceLastOrder + 1)` using Row 0 where `DaySinceLastOrder = 5` | `RecencyScore = 1/6 = 0.16667` | Value matches to 9 decimal places | ✅ Pass |
| TC-FEAT-03 | Verify HighRisk flag: Row 0 (`Complain=1, Tenure=1.0`) must be flagged as 1; Row 1 (`Complain=0, Tenure=5.0`) must be 0 | `HighRisk[0] = 1`, `HighRisk[1] = 0` | Both rows produce correct values | ✅ Pass |
| TC-FEAT-04 | Verify `AddressDiversityFlag` triggers when `NumberOfAddress > 3`; Row 1 has 5 addresses (flag=1), Row 0 has 2 addresses (flag=0) | `Flag[1] = 1`, `Flag[0] = 0` | Both assertions hold correctly | ✅ Pass |
| TC-FEAT-05 *(Intentional Fail)* | Apply WRONG SpendingEfficiency formula `CashbackAmount / OrderCount` (missing `+1`) and assert it equals the correct result `150 / (3+1) = 37.5` | Result should be `37.5` | Wrong formula gives `50.0`, not `37.5` — the `+1` denominator is critical | ❌ Fail |

---

## Module 3 — Risk Label Categorisation

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-RISK-01 | Pass churn probability of `15%` to `get_risk_label()` | Returns `"Low Risk"` | Returns `"Low Risk"` | ✅ Pass |
| TC-RISK-02 | Pass churn probability of exactly `30%` to test the boundary condition of `<= 30` | Returns `"Low Risk"` (boundary is inclusive) | Returns `"Low Risk"` | ✅ Pass |
| TC-RISK-03 | Pass churn probability of `55%` to `get_risk_label()` | Returns `"Medium Risk"` | Returns `"Medium Risk"` | ✅ Pass |
| TC-RISK-04 | Pass churn probability of `95%` (typical for customers who complained) to `get_risk_label()` | Returns `"High Risk"` | Returns `"High Risk"` | ✅ Pass |
| TC-RISK-05 *(Intentional Fail)* | Pass churn probability of `31%` and assert it returns `"Low Risk"` | Test expects `"Low Risk"` | Function returns `"Medium Risk"` because `31 > 30`, which is the Medium Risk band | ❌ Fail |

---

## Module 4 — Recommendation Engine

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-RECOM-01 | Customer with `CLV = 10000` (above 75th percentile threshold) and `Churn Probability = 85%` (above 70%) passed to `get_recommendation()` | Returns `"VIP Retention Program"` | Returns `"VIP Retention Program"` | ✅ Pass |
| TC-RECOM-02 | Customer with `EngagementScore = 0.3` (below 25th percentile threshold of `1.0`) and `CLV = 100` (below threshold) passed to `get_recommendation()` | Returns `"Re-engagement Campaign"` | Returns `"Re-engagement Campaign"` | ✅ Pass |
| TC-RECOM-03 | Customer with `RecencyScore = 0.5` (above 75th percentile threshold of `0.1`), `CLV = 100`, `EngagementScore = 2.0` passed to `get_recommendation()` | Returns `"Win-back Offer"` | Returns `"Win-back Offer"` | ✅ Pass |
| TC-RECOM-04 | Customer that meets none of the three priority conditions (`CLV = 100`, `Churn Probability = 20%`, `EngagementScore = 2.0`, `RecencyScore = 0.05`) passed to `get_recommendation()` | Returns `"Discount Coupon"` (default fallback) | Returns `"Discount Coupon"` | ✅ Pass |
| TC-RECOM-05 *(Intentional Fail)* | Customer with `Churn Probability = 85%` but `CLV = 50` (below threshold) — assert they get `"VIP Retention Program"` | Test expects `"VIP Retention Program"` | Function returns `"Re-engagement Campaign"` — VIP requires BOTH high CLV AND high churn probability | ❌ Fail |

---

## Module 5 — Model Persistence

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-MODEL-01 | Load `model_summary.json` and check that a `'Gradient Boosting'` key exists with `'f1'` and `'roc_auc'` sub-keys | Both keys must exist inside the `Gradient Boosting` entry | All required keys are present in the JSON | ✅ Pass |
| TC-MODEL-02 | Extract F1-Score from `model_summary.json` for Gradient Boosting and assert it is greater than or equal to `0.90` (NFR-A1 threshold) | `f1 >= 0.90` | F1 = `0.9121` — exceeds the threshold | ✅ Pass |
| TC-MODEL-03 | Load `model_summary.json` and assert that `'feature_cols'` key exists and the list is not empty | `feature_cols` is a non-empty list | List contains all training feature column names | ✅ Pass |
| TC-MODEL-04 | Apply `scaler.pkl` to the cleaned dataset and verify that the mean of scaled output columns is approximately `0` (max allowed: `0.1`) | All column means after scaling are close to `0` | Max column mean after scaling is well below `0.1` — scaler matches training data | ✅ Pass |
| TC-MODEL-05 *(Intentional Fail)* | Access `model_summary.json["Random Forest Regressor"]["f1"]` and assert it is not `None` | Test expects an `f1` key to exist for the regression model | `'f1'` key does not exist — Random Forest Regressor is a regression model and only stores `rmse` and `r2`, not `f1` | ❌ Fail |
