import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, json
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                              roc_auc_score, confusion_matrix,
                              mean_squared_error, r2_score, roc_curve)
import joblib

sns.set_theme(style="whitegrid", palette="muted")
COLORS = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B3","#937860"]
plt.rcParams.update({"figure.dpi":150,"font.family":"DejaVu Sans"})

# ═══════════════════════════════════════════════════════════
# LOAD & CLEAN
# ═══════════════════════════════════════════════════════════
import os
data_path = os.path.join('archive (3)', 'E Commerce Dataset.xlsx')
if os.path.exists(data_path):
    df = pd.read_excel(data_path, sheet_name='E Comm')
elif os.path.exists('cleaned_ecommerce_dataset.csv'):
    df = pd.read_csv('cleaned_ecommerce_dataset.csv')
else:
    df = pd.read_csv('E_Commerce_Dataset.csv')
df['PreferredLoginDevice'] = df['PreferredLoginDevice'].str.strip().replace({'Mobile Phone':'Mobile'})
df['PreferredPaymentMode'] = df['PreferredPaymentMode'].str.strip().replace({'COD':'Cash on Delivery','CC':'Credit Card'})
df['PreferedOrderCat'] = df['PreferedOrderCat'].str.strip().replace({'Mobile':'Mobile Phone'})
for c in ['Tenure','WarehouseToHome','HourSpendOnApp','OrderAmountHikeFromlastYear','CouponUsed','OrderCount','DaySinceLastOrder']:
    df[c] = df[c].fillna(df[c].median())
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"Data loaded: {df.shape}")

# ═══════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════

# ── Step 1: Compute data-driven EngagementScore weights FIRST ──
# Use the raw DataFrame (before any engineered columns are added)
# to calculate absolute Pearson correlation of each engagement
# feature with Churn, then normalise to sum to 1.0.
# IMPORTANT: weights are computed here before adding any new columns
# so that the raw column layout is identical to what corrwith expects.
_eng_features = ['HourSpendOnApp', 'OrderCount', 'CouponUsed']
_corr      = df[_eng_features].corrwith(df['Churn']).abs()  # absolute correlation with Churn
_corr_norm = _corr / _corr.sum()                             # normalise so weights sum to 1.0
w_hour  = round(float(_corr_norm['HourSpendOnApp']), 4)
w_order = round(float(_corr_norm['OrderCount']),     4)
w_coupon= round(float(_corr_norm['CouponUsed']),     4)
print(f"EngagementScore weights (data-driven): "
      f"HourSpendOnApp={w_hour:.4f}, OrderCount={w_order:.4f}, CouponUsed={w_coupon:.4f}")

# ── Step 2: Add all engineered columns in EXACT same order as dashboard.py ──
# ORDER MUST MATCH dashboard.py to prevent scaler feature-name mismatch errors.
df['CLV']                = df['CashbackAmount'] * df['OrderCount'] * (df['Tenure'] + 1)
df['RecencyScore']       = 1 / (df['DaySinceLastOrder'] + 1)
df['EngagementScore']    = (          # ← position 3, same as dashboard.py
    df['HourSpendOnApp'] * w_hour +
    df['OrderCount']     * w_order +
    df['CouponUsed']     * w_coupon
)
df['SpendingEfficiency'] = df['CashbackAmount'] / (df['OrderCount'] + 1)
df['HighRisk']           = ((df['Complain']==1) & (df['Tenure']<3)).astype(int)
df['AddressDiversityFlag'] = (df['NumberOfAddress']>3).astype(int)
print("Feature engineering done.")

# ═══════════════════════════════════════════════════════════
# ENCODING & SCALING
# ═══════════════════════════════════════════════════════════
cat_cols = ['PreferredLoginDevice','PreferredPaymentMode','Gender','PreferedOrderCat','MaritalStatus']
df_enc = df.copy()
le = LabelEncoder()
for c in cat_cols:
    df_enc[c] = le.fit_transform(df_enc[c])

feature_cols = [c for c in df_enc.columns if c not in ['CustomerID','Churn']]
X = df_enc[feature_cols]
y = df_enc['Churn']

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
print(f"Feature columns ({len(feature_cols)}): {feature_cols}")

# ═══════════════════════════════════════════════════════════
# CLASSIFICATION MODELS
# ═══════════════════════════════════════════════════════════
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
    "Decision Tree":        DecisionTreeClassifier(max_depth=6, random_state=42, class_weight='balanced'),
    "Random Forest":        RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, class_weight='balanced'),
    "Gradient Boosting":    GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]
    cv = cross_val_score(model, X_scaled, y, cv=StratifiedKFold(5), scoring='f1').mean()
    results[name] = {
        "model": model, "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred), "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred), "roc_auc": roc_auc_score(y_test, y_prob),
        "cv_f1": cv, "y_pred": y_pred, "y_prob": y_prob,
    }
    print(f"{name}: Acc={results[name]['accuracy']:.3f}  F1={results[name]['f1']:.3f}  AUC={results[name]['roc_auc']:.3f}  CV_F1={cv:.3f}")

# ── Regression: Predict CashbackAmount ──────────────────
X_reg = df_enc[feature_cols].drop(columns=['CashbackAmount'])
y_reg = df_enc['CashbackAmount']
Xr_train, Xr_test, yr_train, yr_test = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
Xr_s = StandardScaler()
Xr_train_s = Xr_s.fit_transform(Xr_train)
Xr_test_s  = Xr_s.transform(Xr_test)

reg_models = {
    "Ridge Regression":          Ridge(alpha=1.0),
    "Decision Tree Regressor":   DecisionTreeRegressor(max_depth=6, random_state=42),
    "Random Forest Regressor":   RandomForestRegressor(n_estimators=100, random_state=42),
}
reg_results = {}
for name, model in reg_models.items():
    model.fit(Xr_train_s, yr_train)
    yp = model.predict(Xr_test_s)
    reg_results[name] = {"rmse": np.sqrt(mean_squared_error(yr_test, yp)), "r2": r2_score(yr_test, yp)}
    print(f"{name}: RMSE={reg_results[name]['rmse']:.3f}  R2={reg_results[name]['r2']:.3f}")

best_name = max(results, key=lambda k: results[k]['f1'])
best = results[best_name]
print(f"\nBest Classifier: {best_name} (F1={best['f1']:.3f})")

# ═══════════════════════════════════════════════════════════
# FIGURE 6: Model Comparison
# ═══════════════════════════════════════════════════════════
metrics = ['accuracy','precision','recall','f1','roc_auc']
fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(len(metrics))
w = 0.18
for i,(name,res) in enumerate(results.items()):
    vals = [res[m] for m in metrics]
    ax.bar(x + i*w, vals, w, label=name, color=COLORS[i], edgecolor='white')
ax.set_xticks(x + w*1.5)
ax.set_xticklabels(['Accuracy','Precision','Recall','F1-Score','ROC-AUC'], fontsize=12)
ax.set_ylim(0, 1.12)
ax.set_title("Classification Model Comparison — All Metrics", fontsize=15, fontweight='bold')
ax.set_ylabel("Score"); ax.legend(loc='upper right', fontsize=10)
ax.axhline(0.8, color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('fig6_model_comparison.png', bbox_inches='tight')
plt.close(); print("Figure 6 saved.")

# ═══════════════════════════════════════════════════════════
# FIGURE 7: ROC Curves + Confusion Matrix
# ═══════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for i,(name,res) in enumerate(results.items()):
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    axes[0].plot(fpr, tpr, color=COLORS[i], lw=2, label=f"{name} (AUC={res['roc_auc']:.3f})")
axes[0].plot([0,1],[0,1],'k--', lw=1)
axes[0].set_title("ROC Curves — All Models", fontsize=13, fontweight='bold')
axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
axes[0].legend(fontsize=9)

cm = confusion_matrix(y_test, best['y_pred'])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],
            xticklabels=['Active','Churned'], yticklabels=['Active','Churned'],
            linewidths=0.5)
axes[1].set_title(f"Confusion Matrix — {best_name}", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Predicted"); axes[1].set_ylabel("Actual")
plt.tight_layout()
plt.savefig('fig7_roc_confusion.png', bbox_inches='tight')
plt.close(); print("Figure 7 saved.")

# ═══════════════════════════════════════════════════════════
# FIGURE 8: Feature Importance
# ═══════════════════════════════════════════════════════════
gb_model = results["Gradient Boosting"]["model"]
importances = pd.Series(gb_model.feature_importances_, index=X.columns).sort_values(ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
top15 = importances.head(15)
sns.barplot(x=top15.values, y=top15.index, ax=axes[0], palette='Blues_r')
axes[0].set_title("Top 15 Feature Importances\n(Gradient Boosting)", fontsize=13, fontweight='bold')
axes[0].set_xlabel("Importance Score")

eng_feats = ['CLV','RecencyScore','EngagementScore','SpendingEfficiency','HighRisk','AddressDiversityFlag']
eng_imp = importances[eng_feats].sort_values(ascending=False)
bars = axes[1].barh(eng_imp.index, eng_imp.values, color=COLORS[:len(eng_feats)])
axes[1].set_title("Engineered Feature Importances", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Importance Score")
for bar, val in zip(bars, eng_imp.values):
    axes[1].text(val+0.0003, bar.get_y()+bar.get_height()/2, f'{val:.4f}', va='center', fontsize=10)
plt.tight_layout()
plt.savefig('fig8_feature_importance.png', bbox_inches='tight')
plt.close(); print("Figure 8 saved.")

# ═══════════════════════════════════════════════════════════
# FIGURE 9: Regression Results
# ═══════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
names_r   = list(reg_results.keys())
rmse_vals = [reg_results[n]['rmse'] for n in names_r]
r2_vals   = [reg_results[n]['r2']   for n in names_r]

sns.barplot(x=names_r, y=rmse_vals, ax=axes[0], palette=COLORS[:3])
axes[0].set_title("Regression Models — RMSE (lower = better)", fontsize=13, fontweight='bold')
axes[0].set_ylabel("RMSE (Rs.)"); axes[0].tick_params(axis='x', rotation=10)
for i,v in enumerate(rmse_vals):
    axes[0].text(i, v+0.3, f"Rs.{v:.1f}", ha='center', fontweight='bold')

sns.barplot(x=names_r, y=r2_vals, ax=axes[1], palette=COLORS[:3])
axes[1].set_title("Regression Models — R² Score (higher = better)", fontsize=13, fontweight='bold')
axes[1].set_ylabel("R² Score"); axes[1].tick_params(axis='x', rotation=10)
for i,v in enumerate(r2_vals):
    axes[1].text(i, v+0.005, f"{v:.3f}", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('fig9_regression.png', bbox_inches='tight')
plt.close(); print("Figure 9 saved.")

# ═══════════════════════════════════════════════════════════
# FIGURE 10: Business Insights Dashboard
# ═══════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Business Insights Dashboard", fontsize=16, fontweight='bold')

axes[0,0].hist(best['y_prob'][y_test==0], bins=30, alpha=0.6, color=COLORS[0], label='Active')
axes[0,0].hist(best['y_prob'][y_test==1], bins=30, alpha=0.6, color=COLORS[3], label='Churned')
axes[0,0].set_title(f"Predicted Churn Probability Distribution\n({best_name})", fontsize=12, fontweight='bold')
axes[0,0].set_xlabel("Predicted Probability of Churn"); axes[0,0].set_ylabel("Count"); axes[0,0].legend()

sns.boxplot(x='Churn', y='CLV', data=df, ax=axes[0,1], palette=[COLORS[0], COLORS[3]])
axes[0,1].set_title("Customer Lifetime Value vs Churn", fontsize=12, fontweight='bold')
axes[0,1].set_xticklabels(['Active','Churned']); axes[0,1].set_xlabel("Status"); axes[0,1].set_ylabel("CLV Score")

sns.boxplot(x='Churn', y='EngagementScore', data=df, ax=axes[1,0], palette=[COLORS[0], COLORS[3]])
axes[1,0].set_title("Engagement Score vs Churn", fontsize=12, fontweight='bold')
axes[1,0].set_xticklabels(['Active','Churned']); axes[1,0].set_xlabel("Status"); axes[1,0].set_ylabel("Engagement Score")

hr_churn = df.groupby('HighRisk')['Churn'].mean() * 100
sns.barplot(x=['Normal Risk','High Risk'], y=hr_churn.values, ax=axes[1,1], palette=[COLORS[0], COLORS[3]])
axes[1,1].set_title("Churn Rate: Normal vs High Risk Customers", fontsize=12, fontweight='bold')
axes[1,1].set_ylabel("Churn Rate (%)")
for i,v in enumerate(hr_churn.values):
    axes[1,1].text(i, v+0.5, f"{v:.1f}%", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('fig10_business_insights.png', bbox_inches='tight')
plt.close(); print("Figure 10 saved.")

# ═══════════════════════════════════════════════════════════
# SAVE MODEL & PRINT SUMMARY
# ═══════════════════════════════════════════════════════════
joblib.dump(results["Gradient Boosting"]["model"], 'best_model_gb.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("\n=== FINAL SUMMARY ===")
for name,res in results.items():
    print(f"{name}: Acc={res['accuracy']:.3f} Prec={res['precision']:.3f} Rec={res['recall']:.3f} F1={res['f1']:.3f} AUC={res['roc_auc']:.3f} CV_F1={res['cv_f1']:.3f}")
print("\nRegression:")
for name,res in reg_results.items():
    print(f"{name}: RMSE={res['rmse']:.3f} R2={res['r2']:.3f}")
print(f"\nBest Classifier: {best_name} (F1={best['f1']:.3f}  AUC={best['roc_auc']:.3f})")
print(f"High-Risk churn rate: {df[df['HighRisk']==1]['Churn'].mean()*100:.1f}%")
print(f"Normal churn rate:    {df[df['HighRisk']==0]['Churn'].mean()*100:.1f}%")

# Save summary JSON for report
summary = {}
for name,res in results.items():
    summary[name] = {k:round(float(v),4) for k,v in res.items() if k not in ['model','y_pred','y_prob']}
for name,res in reg_results.items():
    summary[name] = {k:round(float(v),4) for k,v in res.items()}

# Save data-driven EngagementScore weights so dashboard.py
# can load and use the EXACT same weights — no hardcoding anywhere.
summary['engagement_weights'] = {
    'HourSpendOnApp': w_hour,
    'OrderCount':     w_order,
    'CouponUsed':     w_coupon,
    'method':         'absolute_pearson_correlation_normalised'
}

# Save the exact feature column list in the exact order the scaler was fitted on.
# dashboard.py loads this list and uses it directly — eliminates ALL column
# order mismatch errors between training and inference permanently.
summary['feature_cols'] = feature_cols

with open('model_summary.json','w') as f:
    json.dump(summary, f, indent=2)
print("Model summary saved.")
print(f"Engagement weights saved: {summary['engagement_weights']}")
print(f"Feature cols saved ({len(feature_cols)}): {feature_cols}")
