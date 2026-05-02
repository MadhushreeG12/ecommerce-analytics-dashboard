# 🚀 E-Commerce Customer Analytics Dashboard

A **Streamlit** web application for Predictive Analytics on Customer Behavior in E-Commerce.

## 📊 Features
- **Overview Tab**: Customer demographics, churn distribution, tenure & satisfaction analysis
- **Churn Deep Dive**: Correlation heatmap, churn by complaint & city tier
- **Behavioral Patterns**: Login device, payment preferences, cashback vs order analysis
- **Predictive AI (Phase 2)**: ML model comparison, feature importance, business recommendations

## 🛠️ Tech Stack
- **Frontend**: Streamlit + Plotly
- **Backend**: Python, Pandas, NumPy
- **ML Models**: Scikit-learn (Random Forest, Gradient Boosting, Logistic Regression)

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## 📁 Project Structure
```
├── dashboard.py               # Main Streamlit dashboard
├── eda_phase1.py              # Phase 1: EDA & visualizations
├── phase2_ml.py               # Phase 2: ML model training
├── generate_stats.py          # Statistical summary generation
├── requirements.txt           # Python dependencies
├── archive (3)/               # Dataset folder
│   └── E Commerce Dataset.xlsx
├── best_model_rf.pkl          # Trained Random Forest model
└── scaler.pkl                 # Feature scaler
```
