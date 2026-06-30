# Phase 1 Report: Predictive Analytics for Customer Behavior

## 1. Introduction
### Project Overview
The "Predictive Analytics for Customer Behavior" project aims to leverage advanced data science techniques to understand, analyze, and predict customer actions within an e-commerce ecosystem. By analyzing historical data, we can identify patterns that lead to customer churn, high satisfaction, or increased spending.

### Objective of Phase 1
The primary objective of this phase is to **collect, clean, and preprocess customer data** to create a robust foundation for further analysis and predictive modeling. This involves handling missing data, correcting inconsistencies, and performing initial exploratory data analysis (EDA) to gain early insights.

---

## 2. Dataset Description
### Dataset Source
The dataset used for this project is the **E-Commerce Dataset**, a comprehensive collection of customer interactions and demographics.

### Dataset Dimensions
*   **Total Rows:** 5,630
*   **Total Columns:** 20

### Key Features
| Feature Name | Description |
| :--- | :--- |
| **CustomerID** | Unique identifier for each customer |
| **Churn** | Target variable (1 if churned, 0 otherwise) |
| **Tenure** | Duration of customer relationship (months) |
| **PreferredLoginDevice** | Device used most frequently (Mobile/Phone/Computer) |
| **CityTier** | Classification of the city (1, 2, or 3) |
| **WarehouseToHome** | Distance from warehouse to customer's home |
| **PreferredPaymentMode** | Payment method (Debit Card, UPI, Credit Card, etc.) |
| **Gender** | Customer gender (Male/Female) |
| **HourSpendOnApp** | Time spent on the application |
| **SatisfactionScore** | Customer satisfaction rating (1-5) |
| **MaritalStatus** | Marital status (Single, Married, Divorced) |
| **Complain** | Whether a complaint was filed (1=Yes, 0=No) |
| **OrderCount** | Total number of orders placed |
| **CashbackAmount** | Average cashback earned by the customer |

📌 **Dataset Preview (First 5 Rows):**

```text
   CustomerID  Churn  Tenure PreferredLoginDevice  CityTier  WarehouseToHome PreferredPaymentMode  Gender  HourSpendOnApp  NumberOfDeviceRegistered    PreferedOrderCat  SatisfactionScore MaritalStatus  NumberOfAddress  Complain  OrderAmountHikeFromlastYear  CouponUsed  OrderCount  DaySinceLastOrder  CashbackAmount
0       50001      1     4.0         Mobile Phone         3              6.0           Debit Card  Female             3.0                         3  Laptop & Accessory                  2        Single                9         1                         11.0         1.0         1.0                5.0          159.93
1       50002      1     NaN                Phone         1              8.0                  UPI    Male             3.0                         4              Mobile                  3        Single                7         1                         15.0         0.0         1.0                0.0          120.90
2       50003      1     NaN                Phone         1             30.0           Debit Card    Male             2.0                         4              Mobile                  3        Single                6         1                         14.0         0.0         1.0                3.0          120.28
3       50004      1     0.0                Phone         3             15.0           Debit Card    Male             2.0                         4  Laptop & Accessory                  5        Single                8         0                         23.0         0.0         1.0                3.0          134.07
4       50005      1     0.0                Phone         1             12.0                   CC    Male             NaN                         3              Mobile                  5        Single                3         0                         11.0         1.0         1.0                3.0          129.60
```

---

## 3. Data Collection Method
The dataset was obtained through a structured extraction process from the **E-Commerce Dataset repository**. The raw data was provided in an Excel format (`.xlsx`) containing multiple facets of customer engagement.

### Tools Used:
*   **Python:** Primary language for data manipulation.
*   **Pandas:** Used for loading, inspecting, and transforming the dataset.
*   **NumPy:** Utilized for numerical operations.

---

## 4. Data Understanding (Exploratory Analysis)
A thorough inspection was performed to understand the structure and quality of the data.

### Data Types & Missing Values
The dataset consists of **numerical (float64, int64)** and **categorical (object)** variables.

📌 **Data Info Output:**
```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 5630 entries, 0 to 5629
Data columns (total 20 columns):
 #   Column                       Non-Null Count  Dtype  
---  ------                       --------------  -----  
 0   CustomerID                   5630 non-null   int64  
 1   Churn                        5630 non-null   int64  
 2   Tenure                       5366 non-null   float64
 3   PreferredLoginDevice         5630 non-null   object 
 ...
 19  CashbackAmount               5630 non-null   float64
dtypes: float64(8), int64(7), object(5)
```

---

## 5. Data Cleaning
Data cleaning is the most critical step to ensure model accuracy. Several issues were identified and resolved:

1.  **Handling Missing Values:**
    *   Features like `Tenure`, `WarehouseToHome`, and `OrderCount` had missing entries.
    *   **Solution:** Replaced missing values with the **Median** of the respective column.
2.  **Removing Duplicates:**
    *   Checked for duplicate records to avoid redundancy.
    *   **Solution:** Identified duplicate rows were removed.
3.  **Correcting Inconsistencies:**
    *   `PreferredLoginDevice`: 'Mobile Phone' -> 'Mobile'.
    *   `PreferredPaymentMode`: Abbreviations like 'COD' and 'CC' were expanded.

---

## 6. Data Preprocessing
Preprocessing prepares the data for machine learning algorithms.

### Key Preprocessing Steps:
1.  **Encoding Categorical Data:**
    *   Used **Label Encoding** for categorical features.
2.  **Feature Scaling:**
    *   Applied **Standardization (StandardScaler)** to numerical features.
3.  **Feature Engineering:**
    *   Created features like `CLV` and `EngagementScore`.

---

## 7. Feature Selection
We analyzed feature importance to retain only the most relevant columns:
*   **Kept:** Tenure, Complain, SatisfactionScore, CashbackAmount.
*   **Removed:** CustomerID.

---

## 8. Data Visualization (Basic Insights)
Visualizations help in understanding the underlying distributions and relationships.

*   **Churn Distribution:** ~17% of customers have churned.
*   **Tenure Histogram:** Most customers are in their early stages (0-10 months).
*   **Gender Distribution:** Relatively balanced distribution.

---

## 9. Final Dataset Summary
After rigorous cleaning and transformation, the final dataset is ready for the modeling phase.

*   **Final Row Count:** 5,630
*   **Final Column Count:** 26 (including engineered features)
*   **Status:** **Ready for Phase 2: Predictive Modeling.**

---

## 10. Tools & Technologies Used
*   **Programming:** Python 3.x
*   **Libraries:** Pandas, NumPy, Scikit-learn
*   **Visualization:** Matplotlib, Seaborn
*   **Environment:** VS Code, Jupyter Notebook

---

## 11. Conclusion
Phase 1 was successfully completed. We have transformed raw, noisy e-commerce data into a clean, feature-rich dataset. The exploratory analysis has already highlighted key churn drivers providing a strong baseline for building predictive models in Phase 2.
