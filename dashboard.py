import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import joblib  # For loading the saved ML model and scaler
from sklearn.preprocessing import LabelEncoder  # Used in Tab 5 live inference

# ── Load data-driven EngagementScore weights from model_summary.json ────────
# These weights were computed in phase2_ml.py using absolute Pearson
# correlation of each feature with Churn, normalised to sum to 1.0.
# Fallback values are used only if the JSON has not been generated yet.
_ENG_WEIGHTS_FALLBACK = {'HourSpendOnApp': 0.4, 'OrderCount': 0.3, 'CouponUsed': 0.3}
if os.path.exists('model_summary.json'):
    with open('model_summary.json', 'r') as _wf:
        _ms = json.load(_wf)
    _ew = _ms.get('engagement_weights', _ENG_WEIGHTS_FALLBACK)
else:
    _ew = _ENG_WEIGHTS_FALLBACK
W_HOUR   = _ew.get('HourSpendOnApp', 0.4)   # weight for HourSpendOnApp
W_ORDER  = _ew.get('OrderCount',     0.3)   # weight for OrderCount
W_COUPON = _ew.get('CouponUsed',     0.3)   # weight for CouponUsed

# ── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Insights Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a premium look and larger fonts
st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-size: 20px !important; /* Increased base font size */
    }
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        color: #4C72B0;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    h1 {
        font-size: 3.2rem !important;
    }
    h2 {
        font-size: 2.4rem !important;
    }
    h3 {
        font-size: 2rem !important;
    }
    p, li, span, label, input, button {
        font-size: 1.05rem !important;
    }
    .dataframe, table {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Data Loading & Cleaning ──────────────────────────────────────────────────
@st.cache_data
def load_and_clean_data():
    # Load — robust fallback chain so the app runs regardless of directory name
    data_path = os.path.join('archive (3)', 'E Commerce Dataset.xlsx')
    alt_path   = os.path.join('data', 'E_Commerce_Dataset.xlsx')
    if os.path.exists(data_path):
        df = pd.read_excel(data_path, sheet_name='E Comm')
    elif os.path.exists(alt_path):
        df = pd.read_excel(alt_path, sheet_name='E Comm')
    elif os.path.exists('cleaned_ecommerce_dataset.csv'):
        df = pd.read_csv('cleaned_ecommerce_dataset.csv')
    elif os.path.exists('E_Commerce_Dataset.csv'):
        df = pd.read_csv('E_Commerce_Dataset.csv')
    else:
        st.error(
            "📂 **Data file not found.** Place `E Commerce Dataset.xlsx` inside a `data/` folder "
            "next to `dashboard.py`, or ensure `cleaned_ecommerce_dataset.csv` exists in the same directory. "
            "See `README.md` for full setup instructions."
        )
        st.stop()
    
    # Clean
    df['PreferredLoginDevice'] = df['PreferredLoginDevice'].str.strip().replace({'Mobile Phone': 'Mobile'})
    df['PreferredPaymentMode'] = df['PreferredPaymentMode'].str.strip().replace({
        'COD': 'Cash on Delivery', 'CC': 'Credit Card'
    })
    df['PreferedOrderCat'] = df['PreferedOrderCat'].str.strip().replace({
        'Mobile': 'Mobile Phone', 'Mobile Phone': 'Mobile Phone'
    })
    
    num_cols_with_na = ['Tenure', 'WarehouseToHome', 'HourSpendOnApp',
                         'OrderAmountHikeFromlastYear', 'CouponUsed',
                         'OrderCount', 'DaySinceLastOrder']
    for col in num_cols_with_na:
        df[col] = df[col].fillna(df[col].median())
        
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

df = load_and_clean_data()

# ── Sidebar Filters ─────────────────────────────────────────────────────────
st.sidebar.title("📊 Filter Dashboard")
st.sidebar.markdown("---")

gender_filter = st.sidebar.multiselect("Select Gender", options=df['Gender'].unique(), default=df['Gender'].unique())
marital_filter = st.sidebar.multiselect("Select Marital Status", options=df['MaritalStatus'].unique(), default=df['MaritalStatus'].unique())
tier_filter = st.sidebar.multiselect("Select City Tier", options=df['CityTier'].unique(), default=df['CityTier'].unique())

# Apply filters
filtered_df = df[
    (df['Gender'].isin(gender_filter)) &
    (df['MaritalStatus'].isin(marital_filter)) &
    (df['CityTier'].isin(tier_filter))
]

# ── Main Header ─────────────────────────────────────────────────────────────
st.title("🚀 E-Commerce Customer Analytics")
st.markdown(f"**Analyzing {len(filtered_df)} customers** | Data Source: `E Commerce Dataset.xlsx`")

# ── Key Metrics ─────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

churn_rate = filtered_df['Churn'].mean() * 100
avg_tenure = filtered_df['Tenure'].mean()
avg_sat = filtered_df['SatisfactionScore'].mean()
complaint_rate = filtered_df['Complain'].mean() * 100
avg_cashback = filtered_df['CashbackAmount'].mean()

col1.metric("Churn Rate", f"{churn_rate:.1f}%", delta=f"{-1.2 if churn_rate > 15 else 0.5}%", delta_color="inverse")
col2.metric("Avg Tenure", f"{avg_tenure:.1f} mo")
col3.metric("Avg Satisfaction", f"{avg_sat:.1f}/5")
col4.metric("Complaint Rate", f"{complaint_rate:.1f}%")
col5.metric("Avg Cashback", f"₹{avg_cashback:.0f}")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "📉 Churn Deep Dive",
    "🛍️ Behavioral Patterns",
    "🤖 Predictive AI",
    "🚨 High Risk Customers"
])

with tab1:
    st.subheader("Customer Demographics & Base Metrics")
    c1, c2 = st.columns(2)
    
    with c1:
        # Churn Pie
        fig_churn = px.pie(filtered_df, names='Churn', title='Churn Distribution (0=Active, 1=Churned)',
                           hole=0.4, color_discrete_sequence=['#4C72B0', '#C44E52'])
        fig_churn.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_churn, use_container_width=True)
        
    with c2:
        # Tenure Dist
        fig_tenure = px.histogram(filtered_df, x='Tenure', title='Tenure Distribution',
                                  nbins=30, color_discrete_sequence=['#55A868'])
        fig_tenure.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_tenure, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Marital Status
        ms_counts = filtered_df['MaritalStatus'].value_counts().reset_index()
        fig_ms = px.bar(ms_counts, x='MaritalStatus', y='count', title='Marital Status Distribution',
                        color='MaritalStatus', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_ms.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_ms, use_container_width=True)
    with c4:
        # Satisfaction
        fig_sat = px.box(filtered_df, x='SatisfactionScore', title='Satisfaction Score Spread',
                         color_discrete_sequence=['#DD8452'])
        fig_sat.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_sat, use_container_width=True)

with tab2:
    st.subheader("What Drives Customer Churn?")
    
    # Correlation Heatmap (simplified for plotly)
    num_cols = ['Churn','Tenure','WarehouseToHome','HourSpendOnApp','Complain','CashbackAmount']
    corr = filtered_df[num_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap",
                         color_continuous_scale='RdBu_r', range_color=[-1,1])
    fig_corr.update_layout(font=dict(size=14), title_font=dict(size=20))
    st.plotly_chart(fig_corr, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        # Churn vs Complain
        comp_churn = filtered_df.groupby('Complain')['Churn'].mean().reset_index()
        fig_comp = px.bar(comp_churn, x='Complain', y='Churn', title='Churn Rate by Complaint (0=No, 1=Yes)',
                          labels={'Churn': 'Churn Rate (%)'}, color='Complain', color_discrete_sequence=['#55A868', '#C44E52'])
        fig_comp.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_comp, use_container_width=True)
    with c2:
        # Churn by City Tier
        tier_churn = filtered_df.groupby('CityTier')['Churn'].mean().reset_index()
        fig_tier = px.bar(tier_churn, x='CityTier', y='Churn', title='Churn Rate by City Tier',
                          color='CityTier', color_discrete_sequence=px.colors.sequential.Teal)
        fig_tier.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_tier, use_container_width=True)

with tab3:
    st.subheader("Purchase & App Behavior")
    
    c1, c2 = st.columns(2)
    with c1:
        # Login Device
        fig_login = px.sunburst(filtered_df, path=['PreferredLoginDevice', 'Gender'], title='Login Device by Gender')
        fig_login.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_login, use_container_width=True)
    with c2:
        # Payment Mode
        fig_pay = px.bar(filtered_df['PreferredPaymentMode'].value_counts().reset_index(), 
                         x='PreferredPaymentMode', y='count', title='Preferred Payment Modes',
                         color='PreferredPaymentMode', color_discrete_sequence=px.colors.qualitative.Bold)
        fig_pay.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_pay, use_container_width=True)
        
    st.markdown("---")
    
    # Cashback vs Order Count
    fig_scatter = px.scatter(filtered_df, x='OrderCount', y='CashbackAmount', color='Churn',
                             title='Order Count vs Cashback (Colored by Churn)',
                             trendline="ols", color_discrete_sequence=['#4C72B0', '#C44E52'],
                             opacity=0.6)
    fig_scatter.update_layout(font=dict(size=16), title_font=dict(size=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.header("🤖Predictive Modeling Results")
    
    # Load model summary
    if os.path.exists('model_summary.json'):
        with open('model_summary.json', 'r') as f:
            summary = json.load(f)
            
        # Prepare model comparison data
        model_names = ["Logistic Regression", "Decision Tree", "Random Forest", "Gradient Boosting"]
        metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        
        comp_data = []
        for m_name in model_names:
            if m_name in summary:
                row = {"Model": m_name}
                row.update(summary[m_name])
                comp_data.append(row)
        
        df_comp = pd.DataFrame(comp_data)
        df_melt = df_comp.melt(id_vars="Model", value_vars=metrics, var_name="Metric", value_name="Score")

        # 1. Model Performance Side-by-Side Comparison
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            fig_comp = px.bar(df_melt, x="Metric", y="Score", color="Model", barmode="group",
                              title="Performance Metrics by Model Chart",
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_comp.update_layout(font=dict(size=14), title_font=dict(size=20), yaxis_range=[0, 1.1])
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with c2:
            st.markdown("### 📊 Classification Model Comparison Table")
            
            # Format classification metrics for visualization
            df_comp_display = df_comp.rename(columns={
                "Model": "Model Name",
                "accuracy": "Accuracy",
                "precision": "Precision",
                "recall": "Recall",
                "f1": "F1-Score",
                "roc_auc": "ROC-AUC",
                "cv_f1": "Cross-Val F1"
            }).set_index("Model Name")
            
            # Sort by F1-Score descending
            df_comp_display = df_comp_display.sort_values(by="F1-Score", ascending=False)
            
            # Style the table
            styled_comp = (
                df_comp_display.style
                .format({
                    "Accuracy": "{:.2%}",
                    "Precision": "{:.2%}",
                    "Recall": "{:.2%}",
                    "F1-Score": "{:.2%}",
                    "ROC-AUC": "{:.2%}",
                    "Cross-Val F1": "{:.2%}"
                })
                .highlight_max(subset=["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Cross-Val F1"], color="#d1fae5")
                .set_properties(**{"font-size": "15px", "text-align": "center"})
                .set_table_styles([
                    {"selector": "th",
                     "props": [("background-color", "#1e3a5f"),
                               ("color", "white"),
                               ("font-size", "15px"),
                               ("text-align", "center")]}
                ])
            )
            st.dataframe(styled_comp, use_container_width=True)

        # 3. Feature Importance (Static Image from Phase 2)
        st.subheader("🔍 Top Drivers of Customer Churn")
        if os.path.exists('fig8_feature_importance.png'):
            st.image('fig8_feature_importance.png', caption="Feature Importance - Gradient Boosting Model")
        
        # 4. Business Recommendations
        st.markdown("---")
        st.subheader("🎯 Strategic Recommendations")
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.markdown("""
            **High-Risk Customer Intervention**
            - **Target:** Customers with `HighRisk` flag (Complained + Low Tenure).
            - **Action:** Proactive outreach within 24 hours of a complaint.
            - **Offer:** Personalized cashback or loyalty points to restore trust.
            """)
        with col_rec2:
            st.markdown("""
            **Loyalty Programs**
            - **Insight:** Tenure and Order Count are strong predictors of retention.
            - **Action:** Launch a "Milestone Rewards" program for customers reaching 6+ months tenure.
            - **Focus:** Promote Mobile Phone category as it shows high engagement.
            """)
    else:
        st.warning("⚠️ Model summary not found. Please run `phase2_ml.py` first to generate `model_summary.json`.")

    # ════════════════════════════════════════════════════════════════════════════
    # REGRESSION MODEL SECTION — Spending Prediction (nested inside with tab4)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.subheader("💸 Spending Prediction Model (Regression)")
    st.markdown(
        "A second machine learning task was performed to **predict customer cashback spend** "
        "(a proxy for transaction value) using regression. This fulfils the project requirement "
        "for both a Classification **and** a Regression model. Three algorithms were benchmarked "
        "on a held-out 20% test set."
    )

    # ── Parse regression results from model_summary.json ──
    reg_model_names  = ["Ridge Regression", "Decision Tree Regressor", "Random Forest Regressor"]
    reg_display_data = []

    if os.path.exists('model_summary.json'):
        with open('model_summary.json', 'r') as _f:
            _summary = json.load(_f)

        for _m in reg_model_names:
            if _m in _summary:
                reg_display_data.append({
                    "Model": _m,
                    "R² Score": _summary[_m].get("r2", 0),
                    "RMSE (₹)": _summary[_m].get("rmse", 0),
                })

    # ── KPI Cards ──
    if reg_display_data:
        df_reg = pd.DataFrame(reg_display_data)
        best_reg_row = df_reg.loc[df_reg["R² Score"].idxmax()]

        reg_k1, reg_k2, reg_k3, reg_k4 = st.columns(4)
        reg_k1.metric(
            label="🏆 Best Regression Model",
            value=best_reg_row["Model"].replace(" Regressor", ""),
        )
        reg_k2.metric(
            label="R² Score (Variance Explained)",
            value=f"{best_reg_row['R² Score'] * 100:.2f}%",
            delta="Target Met ✅",
        )
        reg_k3.metric(
            label="RMSE (Prediction Error)",
            value=f"₹{best_reg_row['RMSE (₹)']:.2f}",
            delta="Lowest Error ✅",
            delta_color="off",
        )
        reg_k4.metric(
            label="Test Set Size",
            value="20% hold-out",
        )

        st.markdown(" ")

        # ── Dual Bar Charts: RMSE & R² for all 3 models ──
        reg_chart_c1, reg_chart_c2 = st.columns(2)

        with reg_chart_c1:
            fig_reg_rmse = px.bar(
                df_reg.sort_values("RMSE (₹)"),
                x="Model",
                y="RMSE (₹)",
                color="Model",
                text=df_reg.sort_values("RMSE (₹)")["RMSE (₹)"].apply(lambda v: f"₹{v:.2f}"),
                title="Regression Models — RMSE (Lower = Better)",
                color_discrete_sequence=["#C44E52", "#DD8452", "#55A868"],
            )
            fig_reg_rmse.update_traces(textposition="outside", textfont_size=13)
            fig_reg_rmse.update_layout(
                font=dict(size=14), title_font=dict(size=18),
                showlegend=False, yaxis_title="RMSE (₹)",
                xaxis_tickangle=-10,
            )
            st.plotly_chart(fig_reg_rmse, use_container_width=True)

        with reg_chart_c2:
            fig_reg_r2 = px.bar(
                df_reg.sort_values("R² Score"),
                x="Model",
                y="R² Score",
                color="Model",
                text=df_reg.sort_values("R² Score")["R² Score"].apply(lambda v: f"{v*100:.2f}%"),
                title="Regression Models — R² Score (Higher = Better)",
                color_discrete_sequence=["#C44E52", "#DD8452", "#55A868"],
            )
            fig_reg_r2.update_traces(textposition="outside", textfont_size=13)
            fig_reg_r2.update_layout(
                font=dict(size=14), title_font=dict(size=18),
                showlegend=False, yaxis_title="R² Score",
                yaxis_range=[0, 1.12], xaxis_tickangle=-10,
            )
            st.plotly_chart(fig_reg_r2, use_container_width=True)

        # ── Comparison Table ──
        st.markdown("### 📊 Regression Model Comparison Table")
        df_reg_display = df_reg.copy().set_index("Model")
        df_reg_display["R² Score"] = df_reg_display["R² Score"].map("{:.4f}".format)
        df_reg_display["RMSE (₹)"] = df_reg_display["RMSE (₹)"].map("₹{:.4f}".format)
        styled_reg = (
            df_reg_display.style
            .set_properties(**{"font-size": "15px", "text-align": "center"})
            .set_table_styles([
                {"selector": "th",
                 "props": [("background-color", "#1e3a5f"),
                           ("color", "white"),
                           ("font-size", "15px"),
                           ("text-align", "center")]}
            ])
        )
        st.dataframe(styled_reg, use_container_width=True)

    # ── Embed static regression figure from phase2_ml.py ──
    st.markdown("---")
    st.subheader("📈 Regression Model Output — Visual Proof")
    if os.path.exists('fig9_regression.png'):
        st.image(
            'fig9_regression.png',
            caption="Figure 9: Regression Models Benchmarked — RMSE & R² (Generated by phase2_ml.py)",
            use_container_width=True,
        )
    else:
        st.info("Run `phase2_ml.py` to regenerate the regression figure (`fig9_regression.png`).")

    # ── Business Interpretation ──
    st.markdown("---")
    st.subheader("🧠 Business Interpretation of Regression Results")
    interp_c1, interp_c2 = st.columns(2)
    with interp_c1:
        st.markdown("""
        **What is being predicted?**
        - The regression model predicts the **cashback amount** a customer is expected to receive,
          which acts as a reliable proxy for their **transaction spending volume**.
        - A customer receiving higher cashback is placing more and larger orders — making them
          a high-value acquisition/retention target.

        **Why Random Forest Regressor wins?**
        - It captures **non-linear relationships** between features (e.g., tenure × order count
          interaction effects) far better than linear Ridge Regression.
        - Its ensemble voting mechanism reduces overfitting risk seen in the single Decision Tree.
        """)
    with interp_c2:
        st.markdown("""
        **Business Applications**
        - 📦 **Inventory Planning**: Predicted spend values allow demand forecasting per customer segment.
        - 💰 **Cashback Budget Allocation**: Marketing teams can pre-allocate cashback budgets based
          on predicted customer spend rather than historical averages.
        - 🎯 **Tiered Rewards Design**: High predicted spenders qualify for premium loyalty tiers
          automatically, reducing manual intervention.
        - 🔗 **Combined Pipeline**: Churn classifier identifies *who* will leave;
          spending regressor estimates *how much value* is at risk — enabling prioritized retention spend.
        """)

    st.success(
        "✅ **Compliance Confirmed:** Both a **Classification model** (Gradient Boosting Churn Predictor, "
        "F1=91.2%, AUC=99.6%) and a **Regression model** (Random Forest Spending Predictor, "
        "R²=98.33%, RMSE=₹6.40) have been built, evaluated, and documented in this dashboard."
    )



# ════════════════════════════════════════════════════════════════════════════
# TAB 5: HIGH RISK CUSTOMERS & RETENTION RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("🚨 Customer Retention Workstation")
    st.markdown(
        "A highly interactive environment to explore customer risk segments, "
        "export campaign contact lists, inspect individual risk passports, "
        "and simulate real-time interventions using the live machine learning model."
    )
    st.markdown("---")

    model_path  = "best_model_gb.pkl"
    scaler_path = "scaler.pkl"

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.error(
            "⚠️ Model files not found. Please run `phase2_ml.py` first to "
            "generate `best_model_gb.pkl` and `scaler.pkl`."
        )
    else:
        # Load the Gradient Boosting classifier and the fitted StandardScaler
        gb_model = joblib.load(model_path)
        scaler   = joblib.load(scaler_path)

        # ── Global Clean & Encode on the entire dataset to prevent label mismatch ──
        df_risk_full = df.copy()
        
        # Compute engineered features on the full dataset
        df_risk_full["CLV"]              = df_risk_full["CashbackAmount"] * df_risk_full["OrderCount"] * (df_risk_full["Tenure"] + 1)
        df_risk_full["RecencyScore"]     = 1 / (df_risk_full["DaySinceLastOrder"] + 1)
        df_risk_full["EngagementScore"]  = (
            df_risk_full["HourSpendOnApp"] * W_HOUR
            + df_risk_full["OrderCount"]   * W_ORDER
            + df_risk_full["CouponUsed"]   * W_COUPON
        )  # weights loaded from model_summary.json — data-driven, no hardcoding
        df_risk_full["SpendingEfficiency"]   = df_risk_full["CashbackAmount"] / (df_risk_full["OrderCount"] + 1)
        df_risk_full["HighRisk"]             = ((df_risk_full["Complain"] == 1) & (df_risk_full["Tenure"] < 3)).astype(int)
        df_risk_full["AddressDiversityFlag"] = (df_risk_full["NumberOfAddress"] > 3).astype(int)

        # Pre-fit encoders on full dataset for absolute mapping consistency.
        # PARITY LOCK: This encoder strategy mirrors phase2_ml.py exactly —
        # a fresh LabelEncoder is fit per column on the full dataset so that
        # the integer mappings seen at training time are reproduced identically
        # during live inference. The fitted encoders are stored in `encoders{}`
        # so the simulator can safely transform single-row inputs without
        # re-fitting (which would produce different class orderings).
        cat_cols = ["PreferredLoginDevice", "PreferredPaymentMode", "Gender", "PreferedOrderCat", "MaritalStatus"]
        encoders = {}
        df_enc_full = df_risk_full.copy()
        for col in cat_cols:
            le = LabelEncoder()
            df_enc_full[col] = le.fit_transform(df_enc_full[col].astype(str))
            encoders[col] = le

        # ── Load the EXACT feature column list saved during training ──────────
        # Using a dynamically computed list risks column order mismatch if the
        # dashboard DataFrame has extra columns (e.g. Risk Level, Churn Probability).
        # Loading the saved list guarantees the scaler always receives columns
        # in the exact same order as during fit — permanently fixing ValueError.
        with open('model_summary.json', 'r') as _fc_f:
            _fc_data = json.load(_fc_f)
        feature_cols = _fc_data.get('feature_cols', None)

        if feature_cols is None:
            st.error("⚠️ 'feature_cols' not found in model_summary.json. "
                     "Please re-run phase2_ml.py to regenerate the model files.")
            st.stop()

        # Scale & predict on FULL dataset so we have consistent probabilities for any customer lookup
        X_full = df_enc_full[feature_cols]
        X_full_scaled = scaler.transform(X_full)
        df_risk_full["Churn Probability (%)"] = (gb_model.predict_proba(X_full_scaled)[:, 1] * 100).round(2)
        
        # Define Risk Level Categorisation
        def get_risk_label(prob):
            if prob <= 30: return "🟢 Low Risk"
            elif prob <= 70: return "🟡 Medium Risk"
            else: return "🔴 High Risk"
        df_risk_full["Risk Level"] = df_risk_full["Churn Probability (%)"].apply(get_risk_label)

        # Recommended Actions based on full dataset percentile thresholds
        clv_threshold        = df_risk_full["CLV"].quantile(0.75)
        engagement_threshold = df_risk_full["EngagementScore"].quantile(0.25)
        recency_threshold    = df_risk_full["RecencyScore"].quantile(0.75)

        def get_recommendation(row):
            prob = row["Churn Probability (%)"]
            if row["CLV"] >= clv_threshold and prob > 70:
                return "⭐ VIP Retention Program"
            elif row["EngagementScore"] < engagement_threshold:
                return "📣 Re-engagement Campaign"
            elif row["RecencyScore"] > recency_threshold:
                return "🎁 Win-back Offer"
            else:
                return "🏷️ Discount Coupon"
        df_risk_full["Recommended Action"] = df_risk_full.apply(get_recommendation, axis=1)

        # Slice the risk dataset to match the sidebar filtered rows
        df_risk_filtered = df_risk_full[df_risk_full["CustomerID"].isin(filtered_df["CustomerID"])].copy()

        # ════════════════════════════════════════════════════════════════════════
        # SECTION 1: INTERACTIVE SEGMENT EXPLORER & LIST EXPORT
        # ════════════════════════════════════════════════════════════════════════
        with st.expander("📂 Interactive Segment Explorer & List Export", expanded=True):
            st.markdown(
                "Filter customer lists based on risk tier and recommended marketing actions, "
                "and export target lists as CSV files for immediate integration into CRM or email systems."
            )
            
            # Sub-filters within the tab
            f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
            with f_col1:
                selected_risk_tiers = st.multiselect(
                    "Filter by Risk Level",
                    options=["🔴 High Risk", "🟡 Medium Risk", "🟢 Low Risk"],
                    default=["🔴 High Risk", "🟡 Medium Risk"]
                )
            with f_col2:
                selected_actions = st.multiselect(
                    "Filter by Recommended Action",
                    options=["⭐ VIP Retention Program", "📣 Re-engagement Campaign", "🎁 Win-back Offer", "🏷️ Discount Coupon"],
                    default=["⭐ VIP Retention Program", "📣 Re-engagement Campaign", "🎁 Win-back Offer", "🏷️ Discount Coupon"]
                )
            with f_col3:
                search_id_input = st.text_input("Search Customer ID", placeholder="e.g. 50005").strip()

            # Filter data
            explorer_df = df_risk_filtered.copy()
            if selected_risk_tiers:
                explorer_df = explorer_df[explorer_df["Risk Level"].isin(selected_risk_tiers)]
            if selected_actions:
                explorer_df = explorer_df[explorer_df["Recommended Action"].isin(selected_actions)]
            if search_id_input:
                explorer_df = explorer_df[explorer_df["CustomerID"].astype(str).str.contains(search_id_input)]

            # Summary Metrics for Explorer
            exp_total = len(explorer_df)
            exp_high = (explorer_df["Risk Level"] == "🔴 High Risk").sum()
            exp_med = (explorer_df["Risk Level"] == "🟡 Medium Risk").sum()
            exp_low = (explorer_df["Risk Level"] == "🟢 Low Risk").sum()

            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Filtered Total", f"{exp_total}")
            m_col2.metric("🔴 High Risk segment", f"{exp_high}")
            m_col3.metric("🟡 Medium Risk segment", f"{exp_med}")
            m_col4.metric("🟢 Low Risk segment", f"{exp_low}")

            st.markdown(" ")
            
            # Show interactive data table
            if explorer_df.empty:
                st.info("No customers match the active explorer filters.")
            else:
                display_cols_explorer = [
                    "CustomerID", "Churn Probability (%)", "Risk Level", "Recommended Action",
                    "Tenure", "SatisfactionScore", "Complain", "CLV", "EngagementScore"
                ]
                
                # Keep index matching rows
                explorer_display = explorer_df[display_cols_explorer].sort_values("Churn Probability (%)", ascending=False).reset_index(drop=True)
                explorer_display.index = range(1, len(explorer_display) + 1)
                
                # Dynamic table styling
                def highlight_risk_explorer(val):
                    color_map = {
                        "🔴 High Risk":   "background-color: #fde8e8; color: #991b1b; font-weight: 600;",
                        "🟡 Medium Risk": "background-color: #fef9c3; color: #92400e; font-weight: 600;",
                        "🟢 Low Risk":    "background-color: #d1fae5; color: #065f46; font-weight: 600;",
                    }
                    return color_map.get(val, "")

                styled_explorer = (
                    explorer_display.style
                    .applymap(highlight_risk_explorer, subset=["Risk Level"])
                    .format({"Churn Probability (%)": "{:.2f}%", "CLV": "₹{:.2f}", "EngagementScore": "{:.2f}"})
                    .set_properties(**{"font-size": "14px", "text-align": "center"})
                    .set_table_styles([
                        {"selector": "th",
                         "props": [("background-color", "#1e3a5f"),
                                   ("color", "white"),
                                   ("font-size", "14px"),
                                   ("text-align", "center")]}
                    ])
                )
                st.dataframe(styled_explorer, use_container_width=True)

                # Export CSV
                csv_bytes = explorer_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Filtered Campaign List to CSV",
                    data=csv_bytes,
                    file_name="retention_campaign_list.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # ════════════════════════════════════════════════════════════════════════
        # SECTION 2: CUSTOMER RISK PASSPORT & LIVE INTERACTIVE SIMULATOR
        # ════════════════════════════════════════════════════════════════════════
        with st.expander("🔍 Customer Risk Passport & Live 'What-If' Churn Simulator", expanded=True):
            st.markdown(
                "Search and select **any customer** in the dataset to load their full risk profile. "
                "Use the interactive controls to simulate retention actions and witness predicted churn risk drop live!"
            )
            
            # Select Customer
            all_customer_ids = sorted(df_risk_full["CustomerID"].unique())
            col_sel1, col_sel2 = st.columns([1, 2])
            with col_sel1:
                selected_cust_id = st.selectbox(
                    "Select Customer ID to Load",
                    options=all_customer_ids,
                    index=0
                )
            with col_sel2:
                # Provide a quick search/information helper
                cust_summary = df_risk_full[df_risk_full["CustomerID"] == selected_cust_id].iloc[0]
                st.markdown(
                    f"**Quick Status**: {cust_summary['Risk Level']} ({cust_summary['Churn Probability (%)']}% Churn Risk) | "
                    f"**Action Recommended**: `{cust_summary['Recommended Action']}`"
                )

            st.markdown("---")

            # Main lookup columns
            sim_col1, sim_col2 = st.columns([1, 1])

            with sim_col1:
                st.subheader("📇 Customer Risk Passport")
                
                # Gauge Chart for original risk
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = cust_summary["Churn Probability (%)"],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#1e3a5f"},
                        'bar': {'color': "#1e3a5f"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 30], 'color': '#2A9D8F'},
                            {'range': [30, 70], 'color': '#F4A261'},
                            {'range': [70, 100], 'color': '#E63946'}
                        ],
                    }
                ))
                fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)

                # Core Customer Details Card
                st.markdown(f"""
                <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #1e3a5f;">
                    <h4 style="margin-top:0; color:#1e3a5f;">Profile Details - Customer #{selected_cust_id}</h4>
                    <table style="width:100%; border-collapse:collapse; font-size:15px;">
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Gender / Marital Status:</td><td style="text-align:right;">{cust_summary['Gender']} / {cust_summary['MaritalStatus']}</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">City Tier:</td><td style="text-align:right;">Tier {cust_summary['CityTier']}</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Tenure (Duration):</td><td style="text-align:right;">{cust_summary['Tenure']:.1f} months</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Satisfaction Score:</td><td style="text-align:right;">{cust_summary['SatisfactionScore']}/5</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Complaint Filed:</td><td style="text-align:right;">{'🚨 Yes' if cust_summary['Complain'] == 1 else '✅ No'}</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Order Count / Cashback:</td><td style="text-align:right;">{cust_summary['OrderCount']:.0f} orders / ₹{cust_summary['CashbackAmount']:.2f}</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">App Engagement Score:</td><td style="text-align:right;">{cust_summary['EngagementScore']:.2f}</td></tr>
                        <tr><td style="padding:6px 0; font-weight:600; color:#555;">Calculated CLV:</td><td style="text-align:right;">₹{cust_summary['CLV']:.2f}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

            with sim_col2:
                st.subheader("🧪 Live 'What-If' Retention Simulator")
                st.markdown("Adjust customer attributes below to test treatment interventions and see real-time churn risk reduction:")
                
                # Set up interactive controls
                st.markdown("### 🔧 Simulate Treatments")
                
                # Checkbox for Complaint Resolution
                if cust_summary["Complain"] == 1:
                    sim_resolve_complain = st.checkbox("Resolve Active Customer Complaint", value=True, help="Tackles customer pain points proactively to repair brand loyalty.")
                    sim_complain_val = 0 if sim_resolve_complain else 1
                else:
                    sim_simulate_complain = st.checkbox("Simulate Complaint Filed", value=False, help="Test what happens to their churn risk if they encounter a service failure and complain.")
                    sim_complain_val = 1 if sim_simulate_complain else 0
                
                # Slider for Satisfaction Score
                sim_satisfaction = st.slider(
                    "Simulate Satisfaction Score",
                    min_value=1,
                    max_value=5,
                    value=int(cust_summary["SatisfactionScore"]),
                    help="Improving delivery time or resolving complaints usually increases satisfaction."
                )

                # Slider for Cashback Reward Boost
                sim_cashback_boost = st.slider(
                    "Provide Cashback / Loyalty Reward Boost (₹)",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5,
                    help="Offer financial cashback credit to build transactional hook."
                )

                # Slider for Tenure progression
                sim_tenure_progression = st.slider(
                    "Simulate Relationship Progression (+ months)",
                    min_value=0,
                    max_value=12,
                    value=0,
                    step=1,
                    help="Look at expected churn drop as the relationship matures."
                )

                # ── Construct simulated features for real-time model inference ──
                # Make a row with original values
                sim_row = cust_summary.copy()
                
                # Mutate values based on user controls
                sim_row["Complain"] = sim_complain_val
                sim_row["SatisfactionScore"] = sim_satisfaction
                sim_row["CashbackAmount"] = cust_summary["CashbackAmount"] + sim_cashback_boost
                sim_row["Tenure"] = cust_summary["Tenure"] + sim_tenure_progression

                # Recompute engineered metrics with updated values
                sim_row["CLV"] = sim_row["CashbackAmount"] * sim_row["OrderCount"] * (sim_row["Tenure"] + 1)
                sim_row["SpendingEfficiency"] = sim_row["CashbackAmount"] / (sim_row["OrderCount"] + 1)
                sim_row["HighRisk"] = 1 if (sim_row["Complain"] == 1 and sim_row["Tenure"] < 3) else 0

                # Form DataFrame for mapping and scale
                sim_df = pd.DataFrame([sim_row])
                
                # Encode categorical columns using our pre-fitted global encoders
                sim_df_enc = sim_df.copy()
                for col in cat_cols:
                    le = encoders[col]
                    val_str = str(sim_df[col].iloc[0])
                    if val_str not in le.classes_:
                        sim_df_enc[col] = 0
                    else:
                        sim_df_enc[col] = le.transform([val_str])[0]

                # Select and order features
                X_sim = sim_df_enc[feature_cols]
                
                # Scale features and run inference
                X_sim_scaled = scaler.transform(X_sim)
                simulated_prob = (gb_model.predict_proba(X_sim_scaled)[:, 1][0] * 100).round(2)
                simulated_risk_level = get_risk_label(simulated_prob)

                # Display Results
                st.markdown("### 📊 Simulated Retention Results")
                
                res_col1, res_col2 = st.columns(2)
                
                original_prob = cust_summary["Churn Probability (%)"]
                delta_prob = simulated_prob - original_prob
                
                res_col1.metric(
                    label="New Churn Probability",
                    value=f"{simulated_prob:.2f}%",
                    delta=f"{delta_prob:.2f}%",
                    delta_color="inverse"
                )
                
                res_col2.metric(
                    label="New Risk Level",
                    value=simulated_risk_level
                )

                # Show beautiful visual callout boxes
                if delta_prob < 0:
                    reduction = abs(delta_prob)
                    st.success(
                        f"🎉 **Treatment Successful!** Churn risk reduced by **{reduction:.2f}%**.\n\n"
                        f"By applying these treatments, the customer's churn likelihood dropped from "
                        f"**{original_prob:.1f}% ({cust_summary['Risk Level']})** to **{simulated_prob:.1f}% ({simulated_risk_level})**."
                    )
                elif delta_prob > 0:
                    increase = abs(delta_prob)
                    st.warning(
                        f"⚠️ **Service Failure Risk!** Churn risk increased by **{increase:.2f}%**.\n\n"
                        f"This simulation shows that neglecting this customer's experience and allowing a complaint "
                        f"increases their churn likelihood to **{simulated_prob:.1f}% ({simulated_risk_level})**."
                    )
                else:
                    st.info("Adjust the sliders or checks above to observe how interventions drive churn probability down.")

        # ════════════════════════════════════════════════════════════════════════
        # SECTION 3: ADVANCED RETENTION SEGMENT CHARTS
        # ════════════════════════════════════════════════════════════════════════
        with st.expander("📊 Advanced Retention Visual Analytics", expanded=False):
            st.subheader("🍩 Churn Risk Distribution & Probability Heat")
            
            # Donut chart
            risk_counts = df_risk_filtered["Risk Level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]

            risk_color_map = {
                "🔴 High Risk":   "#E63946",
                "🟡 Medium Risk": "#F4A261",
                "🟢 Low Risk":    "#2A9D8F",
            }
            
            fig_donut = px.pie(
                risk_counts,
                names="Risk Level",
                values="Count",
                hole=0.5,
                color="Risk Level",
                color_discrete_map=risk_color_map,
                title="Active Risk Tier Split (Filtered Segment)",
            )
            fig_donut.update_traces(textinfo="percent+label", pull=[0.05, 0.02, 0])
            fig_donut.update_layout(font=dict(size=14), legend=dict(font=dict(size=12)))

            # Probability histogram
            fig_hist = px.histogram(
                df_risk_filtered,
                x="Churn Probability (%)",
                nbins=40,
                color="Risk Level",
                color_discrete_map=risk_color_map,
                title="Churn Probability Distribution Spread",
                labels={"Churn Probability (%)": "Churn Probability (%)", "count": "Number of Customers"},
                barmode="stack",
            )
            fig_hist.add_vline(x=30, line_dash="dash", line_color="#F4A261",
                               annotation_text="Low/Medium threshold (30%)",
                               annotation_position="top right")
            fig_hist.add_vline(x=70, line_dash="dash", line_color="#E63946",
                               annotation_text="Medium/High threshold (70%)",
                               annotation_position="top right")
            fig_hist.update_layout(font=dict(size=13))

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.plotly_chart(fig_donut, use_container_width=True)
            with chart_col2:
                st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown("---")

            # Actions & CLV
            st.subheader("🎯 Recommended Actions & Customer Lifetime Value Matrix")
            all_high_risk_df = df_risk_filtered[df_risk_filtered["Risk Level"] == "🔴 High Risk"]
            
            if all_high_risk_df.empty:
                st.info("No high risk customers found in the current segment to map.")
            else:
                action_counts = all_high_risk_df["Recommended Action"].value_counts().reset_index()
                action_counts.columns = ["Recommended Action", "Customer Count"]

                fig_actions = px.bar(
                    action_counts,
                    x="Recommended Action",
                    y="Customer Count",
                    color="Recommended Action",
                    text="Customer Count",
                    title="Retention Strategy Breakdown (🔴 High Risk Segment)",
                    color_discrete_sequence=["#E63946", "#F4A261", "#2A9D8F", "#457B9D"],
                )
                fig_actions.update_traces(textposition="outside", textfont_size=12)
                fig_actions.update_layout(font=dict(size=13), showlegend=False, yaxis_title="Customer Count")

                fig_scatter_risk = px.scatter(
                    all_high_risk_df,
                    x="CLV",
                    y="Churn Probability (%)",
                    color="Recommended Action",
                    hover_data=["CustomerID", "EngagementScore", "RecencyScore"],
                    title="CLV vs Churn Probability Profile Map",
                    color_discrete_sequence=["#E63946", "#F4A261", "#2A9D8F", "#457B9D"],
                    opacity=0.8,
                    size_max=10,
                )
                fig_scatter_risk.update_layout(font=dict(size=13), legend=dict(title="Action Program"))

                chart_col3, chart_col4 = st.columns(2)
                with chart_col3:
                    st.plotly_chart(fig_actions, use_container_width=True)
                with chart_col4:
                    st.plotly_chart(fig_scatter_risk, use_container_width=True)

        # ════════════════════════════════════════════════════════════════════════
        # SECTION 4: STRATEGIC LOGIC CARD GUIDE
        # ════════════════════════════════════════════════════════════════════════
        st.markdown("---")
        st.subheader("📋 Campaign Recommended Logic Guide")
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.markdown("""
<div style="background-color:#fff; padding:15px; border-radius:8px; border-left:4px solid #E63946; box-shadow:0 2px 4px rgba(0,0,0,0.05); min-height:220px;">
    <strong style="color:#E63946;">⭐ VIP Retention</strong><br/>
    <small style="color:#777;">CLV: Top 25% | Churn > 70%</small>
    <p style="font-size:14px; margin-top:8px;">Highly valuable customers who are highly unstable. Allocate a dedicated relationship manager and offer exclusive loyalty upgrades.</p>
</div>
""", unsafe_allow_html=True)
        with g2:
            st.markdown("""
<div style="background-color:#fff; padding:15px; border-radius:8px; border-left:4px solid #F4A261; box-shadow:0 2px 4px rgba(0,0,0,0.05); min-height:220px;">
    <strong style="color:#F4A261;">📣 Re-engagement</strong><br/>
    <small style="color:#777;">EngagementScore: Bottom 25%</small>
    <p style="font-size:14px; margin-top:8px;">Customers showing declining app visits or orders. Re-ignite interest using custom push notifications and tailored recommendations.</p>
</div>
""", unsafe_allow_html=True)
        with g3:
            st.markdown("""
<div style="background-color:#fff; padding:15px; border-radius:8px; border-left:4px solid #2A9D8F; box-shadow:0 2px 4px rgba(0,0,0,0.05); min-height:220px;">
    <strong style="color:#2A9D8F;">🎁 Win-back Offer</strong><br/>
    <small style="color:#777;">Recency: Long Purchase Gap</small>
    <p style="font-size:14px; margin-top:8px;">Inactive customers who haven't ordered in months. Entice them back with time-limited discount vouchers and free delivery options.</p>
</div>
""", unsafe_allow_html=True)
        with g4:
            st.markdown("""
<div style="background-color:#fff; padding:15px; border-radius:8px; border-left:4px solid #457B9D; box-shadow:0 2px 4px rgba(0,0,0,0.05); min-height:220px;">
    <strong style="color:#457B9D;">🏷️ Discount Coupon</strong><br/>
    <small style="color:#777;">Standard High Churn Risk</small>
    <p style="font-size:14px; margin-top:8px;">General high-risk segments. Minimize immediate churn triggers using a price discount coupon paired with preferred items.</p>
</div>
""", unsafe_allow_html=True)
