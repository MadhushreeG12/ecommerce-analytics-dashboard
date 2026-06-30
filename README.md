# 🚀 E-Commerce Customer Analytics Dashboard

A **Streamlit** web application for Predictive Analytics on Customer Behaviour in E-Commerce.  
Built as a Phase 2 deliverable demonstrating end-to-end machine learning — from EDA through  
feature engineering to live inference.

---

## 📊 Dashboard Features

| Tab | Contents |
|-----|----------|
| 📈 Overview | Customer demographics, churn distribution, tenure & satisfaction |
| 📉 Churn Deep Dive | Correlation heatmap, churn by complaint & city tier |
| 🛍️ Behavioral Patterns | Login device, payment preferences, cashback vs order analysis |
| 🤖 Predictive AI | **Classification** model comparison + **Regression** spending predictor results |
| 🚨 High Risk Customers | Live ML inference simulator, risk passports, campaign CSV export |

---

## ⚙️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Place the Data File (IMPORTANT)

The dashboard looks for the data file in the following order — use **any one** of these options:

| Priority | Path | Notes |
|----------|------|-------|
| 1st | `archive (3)/E Commerce Dataset.xlsx` | Original project folder name |
| 2nd | `data/E_Commerce_Dataset.xlsx` | **Recommended for evaluators** — create a `data/` folder and place the file here |
| 3rd | `cleaned_ecommerce_dataset.csv` | Pre-cleaned CSV (included in repo) |
| 4th | `E_Commerce_Dataset.csv` | Raw CSV fallback |

> **For evaluators running on a fresh machine:** The simplest approach is to create a `data/` folder  
> in the same directory as `dashboard.py` and place `E Commerce Dataset.xlsx` inside it.  
> Alternatively, the included `cleaned_ecommerce_dataset.csv` will load automatically with no setup needed.

### 3. Run the ML Training (if .pkl files are missing)
```bash
python phase2_ml.py
```
This generates `best_model_gb.pkl`, `scaler.pkl`, `model_summary.json`, and all figure PNGs.

### 4. Launch Dashboard
```bash
streamlit run dashboard.py
```

---

## 🤖 Machine Learning Models

### Classification — Churn Prediction
| Model | Accuracy | F1-Score | ROC-AUC |
|-------|----------|----------|---------|
| Logistic Regression | 79.1% | 56.6% | 86.8% |
| Decision Tree | 80.0% | 58.9% | 87.9% |
| Random Forest | 95.3% | 86.0% | 98.4% |
| **Gradient Boosting** ✅ | **97.2%** | **91.2%** | **99.6%** |

### Regression — Spending Prediction (CashbackAmount)
| Model | R² Score | RMSE |
|-------|----------|------|
| Ridge Regression | 69.4% | ₹27.39 |
| Decision Tree Regressor | 93.6% | ₹12.51 |
| **Random Forest Regressor** ✅ | **98.3%** | **₹6.40** |

---

## 📁 Project Structure

```
├── dashboard.py                  # Main Streamlit dashboard
├── phase2_ml.py                  # Phase 2: ML model training (classification + regression)
├── eda_phase1.py                 # Phase 1: EDA & visualizations
├── generate_report.py            # Report generation script
├── generate_stats.py             # Statistical summary generation
├── requirements.txt              # Python dependencies
│
├── data/                         # ← Place E Commerce Dataset.xlsx here (for evaluators)
├── archive (3)/                  # Original dataset folder
│   └── E Commerce Dataset.xlsx
├── cleaned_ecommerce_dataset.csv # Pre-cleaned CSV (auto-loaded if Excel not found)
│
├── best_model_gb.pkl             # Trained Gradient Boosting classifier
├── scaler.pkl                    # Feature StandardScaler
├── model_summary.json            # All model metrics (classification + regression)
│
├── Phase2_ML_Model_Report.md     # Standalone model evaluation report
├── Phase1_EDA_Report.docx        # Phase 1 EDA report (Word document)
├── Phase2_Predictive_Modeling_Report.docx  # Phase 2 full report (Word document)
│
├── fig6_model_comparison.png     # Classification model comparison chart
├── fig7_roc_confusion.png        # ROC curves + confusion matrix
├── fig8_feature_importance.png   # Feature importances (Gradient Boosting)
└── fig9_regression.png           # Regression model benchmarks
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Plotly
- **Backend**: Python 3.x, Pandas, NumPy
- **ML**: Scikit-learn (Gradient Boosting, Random Forest, Logistic Regression, Ridge Regression)
- **Serialisation**: Joblib (model persistence)
