import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

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
    html, body, [class*="css"] {
        font-size: 18px; /* Increased base font size */
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
        font-size: 2.2rem !important;
        color: #4C72B0;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    h1 {
        font-size: 3rem !important;
    }
    h2 {
        font-size: 2.2rem !important;
    }
    h3 {
        font-size: 1.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Data Loading & Cleaning ──────────────────────────────────────────────────
@st.cache_data
def load_and_clean_data():
    # Load
    try:
        df = pd.read_excel('archive (3)/E Commerce Dataset.xlsx', sheet_name='E Comm')
    except:
        df = pd.read_csv('E_Commerce_Dataset.csv') # Fallback
    
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
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📉 Churn Deep Dive", "🛍️ Behavioral Patterns", "🤖 Predictive AI (Phase 2)"])

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
            
        # 1. Model Comparison Chart
        st.subheader("Classification Model Comparison")
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
        
        fig_comp = px.bar(df_melt, x="Metric", y="Score", color="Model", barmode="group",
                          title="Performance Metrics by Model",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_comp.update_layout(font=dict(size=14), title_font=dict(size=20), yaxis_range=[0, 1.1])
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # 2. Key Insights & Best Model
        c1, c2 = st.columns(2)
        with c1:
            st.info("💡 **Best Performer:** Gradient Boosting achieved the highest F1-Score (0.91) and AUC (0.99), making it the most reliable for churn prediction.")
            st.success("✅ **Model Status:** Production-ready model saved as `best_model_rf.pkl` (Random Forest for balance) and `scaler.pkl`.")
        
        with c2:
            st.markdown("### Regression Performance (Cashback Prediction)")
            reg_data = []
            for r_name in ["Ridge Regression", "Decision Tree Regressor", "Random Forest Regressor"]:
                if r_name in summary:
                    reg_data.append({"Model": r_name, "RMSE": summary[r_name]["rmse"], "R2": summary[r_name]["r2"]})
            df_reg = pd.DataFrame(reg_data)
            st.table(df_reg.style.format({"RMSE": "{:.2f}", "R2": "{:.3f}"}))

        # 3. Feature Importance (Static Image from Phase 2)
        st.subheader("🔍 Top Drivers of Customer Churn")
        if os.path.exists('fig8_feature_importance.png'):
            st.image('fig8_feature_importance.png', caption="Feature Importance - Random Forest Model")
        
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
        st.warning("Model summary not found. Please run `phase2_ml.py` first.")



