"""
╔══════════════════════════════════════════════════════════════════════╗
║   CME CLASSIFICATION & RISK SCORING PIPELINE                        ║
║   Coronal Mass Ejection Detection from Multi-Modal Solar Imagery    ║
║                                                                      ║
║   Data sources: EUV (171Å, 193Å, 211Å), White-light coronagraph,   ║
║                 Magnetograms, H-alpha images                         ║
║   Stage 1: CME Type Classification (6 classes)                      ║
║   Stage 2: Operational Risk Classification via XGBoost              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, accuracy_score, f1_score)
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
import xgboost as xgb

np.random.seed(42)

# ─────────────────────────────────────────────────────────────────────
# 1. CME CLASS DEFINITIONS
# ─────────────────────────────────────────────────────────────────────
CME_CLASSES = {
    0: {"name": "No CME",          "color": "#4ade80", "speed_range": (0,    100)},
    1: {"name": "Slow CME",        "color": "#60a5fa", "speed_range": (100,  400)},
    2: {"name": "Moderate CME",    "color": "#fbbf24", "speed_range": (400,  800)},
    3: {"name": "Fast CME",        "color": "#f97316", "speed_range": (800,  1500)},
    4: {"name": "Halo CME",        "color": "#c084fc", "speed_range": (500,  2000)},
    5: {"name": "Earth-directed",  "color": "#f87171", "speed_range": (300,  2500)},
}

RISK_LEVELS = {
    "Low":      {"color": "#4ade80", "speed": (0,    400),  "threshold": 400},
    "Moderate": {"color": "#fbbf24", "speed": (400,  800),  "threshold": 800},
    "High":     {"color": "#f97316", "speed": (800,  1500), "threshold": 1500},
    "Extreme":  {"color": "#f87171", "speed": (1500, 4000), "threshold": 9999},
}

IMAGE_TYPES = ["EUV_171", "EUV_193", "EUV_211", "WL_Coronagraph", "Magnetogram", "H_alpha"]

print("=" * 70)
print("  CME CLASSIFICATION & RISK SCORING PIPELINE")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────
# 2. SYNTHETIC DATASET GENERATION
#    Simulates realistic parameter distributions for each CME class
# ─────────────────────────────────────────────────────────────────────

def generate_cme_dataset(n_samples=3000):
    """
    Generate realistic synthetic CME dataset.
    Each sample represents one solar event with features extracted
    from multi-modal solar imagery.
    """
    print("\n[1/6] Generating synthetic CME dataset...")

    records = []
    # Class distribution (reflects real LASCO/SDO statistics)
    class_dist = {0: 0.35, 1: 0.25, 2: 0.18, 3: 0.10, 4: 0.07, 5: 0.05}
    class_counts = {k: int(v * n_samples) for k, v in class_dist.items()}
    # Adjust last class to hit exact total
    class_counts[5] += n_samples - sum(class_counts.values())

    for cls, count in class_counts.items():
        cfg = CME_CLASSES[cls]
        spd_lo, spd_hi = cfg["speed_range"]

        for _ in range(count):
            speed = np.random.uniform(spd_lo, spd_hi)
            is_cme = cls > 0

            # ── EUV channel features (per wavelength)
            euv_171_brightness = np.random.normal(
                1200 + 800 * is_cme + 200 * (cls == 5), 150)
            euv_193_brightness = np.random.normal(
                1500 + 900 * is_cme + 250 * (cls == 5), 180)
            euv_211_brightness = np.random.normal(
                800  + 600 * is_cme + 150 * (cls == 4), 120)

            # ── Active region properties
            ar_area        = np.random.lognormal(7.5 + 1.2 * is_cme + 0.3 * (cls >= 3), 0.6)
            sunspot_area   = np.random.lognormal(6.0 + 0.9 * is_cme + 0.4 * (cls >= 3), 0.7)
            sunspot_count  = np.random.poisson(3 + 6 * is_cme + 3 * (cls >= 3))
            mag_complexity = np.random.beta(
                2 + 3 * is_cme + 2 * (cls >= 4),
                5 - 2 * is_cme)  # 0-1, higher = more complex

            # ── Flare properties
            flare_size = np.random.exponential(0.5 + 1.5 * is_cme + 0.8 * (cls >= 3))
            flare_peak = np.random.lognormal(-5 + 1.5 * is_cme, 0.8)  # W/m²

            # ── CME morphology (from coronagraph)
            halo_flag     = 1 if cls == 4 else (1 if (cls == 5 and np.random.rand() > 0.3) else 0)
            cme_width     = np.random.normal(
                30 + 70 * is_cme + 100 * halo_flag + 20 * (cls == 5), 25) if is_cme else 0
            cme_width     = max(0, min(360, cme_width))
            cme_direction = np.random.normal(
                180 if cls == 5 else np.random.uniform(0, 360), 20 if cls == 5 else 60)
            cme_speed     = speed + np.random.normal(0, 50)
            cme_accel     = np.random.normal(
                -5 * (speed > 800) + 2 * (speed < 400), 8) if is_cme else 0

            # ── Image texture features (GLCM-style)
            contrast      = np.random.normal(0.3 + 0.4 * is_cme + 0.1 * (cls >= 3), 0.08)
            correlation   = np.random.normal(0.7 - 0.1 * is_cme, 0.06)
            energy        = np.random.normal(0.15 + 0.05 * is_cme, 0.03)
            homogeneity   = np.random.normal(0.6 - 0.15 * is_cme, 0.07)

            # ── Shape features (from segmentation)
            elongation    = np.random.normal(1.0 + 0.8 * is_cme + 0.3 * (cls == 5), 0.2)
            circularity   = np.random.normal(0.85 - 0.3 * is_cme, 0.1)
            edge_density  = np.random.normal(0.1 + 0.25 * is_cme + 0.1 * (cls >= 3), 0.04)

            # ── Optical flow (motion magnitude between frames)
            optical_flow_mean = np.random.exponential(2 + 8 * is_cme + 5 * (cls >= 3))
            optical_flow_max  = optical_flow_mean * np.random.uniform(2, 5)

            # ── Magnetogram features
            total_flux    = np.random.lognormal(20 + 2 * is_cme + 0.5 * (cls >= 4), 0.8)
            flux_imbalance= np.random.normal(0.1 + 0.3 * is_cme, 0.15)
            polarity_sep  = np.random.normal(15 + 10 * is_cme, 5)  # arcsec

            # ── H-alpha features
            ha_brightness = np.random.normal(1.0 + 0.5 * is_cme + 0.3 * (cls >= 3), 0.15)
            ha_area       = np.random.lognormal(5 + 1.5 * is_cme, 0.6)
            filament_flag = int(np.random.rand() < (0.1 + 0.3 * is_cme))

            # Assign risk label from speed
            if cme_speed < 400:   risk = "Low"
            elif cme_speed < 800: risk = "Moderate"
            elif cme_speed < 1500:risk = "High"
            else:                  risk = "Extreme"

            records.append({
                # Labels
                "cme_class": cls,
                "cme_class_name": CME_CLASSES[cls]["name"],
                "risk_level": risk if is_cme else "Low",
                # EUV
                "euv_171_brightness": euv_171_brightness,
                "euv_193_brightness": euv_193_brightness,
                "euv_211_brightness": euv_211_brightness,
                "euv_171_193_ratio":  euv_171_brightness / (euv_193_brightness + 1e-6),
                "euv_193_211_ratio":  euv_193_brightness / (euv_211_brightness + 1e-6),
                # Active region
                "ar_area":        ar_area,
                "sunspot_area":   sunspot_area,
                "sunspot_count":  sunspot_count,
                "mag_complexity": mag_complexity,
                # Flare
                "flare_size":  flare_size,
                "flare_peak":  flare_peak,
                # Coronagraph / CME morphology
                "halo_flag":      halo_flag,
                "cme_width":      cme_width,
                "cme_direction":  cme_direction,
                "cme_speed":      max(0, cme_speed),
                "cme_accel":      cme_accel,
                # Texture
                "tex_contrast":    max(0, contrast),
                "tex_correlation": correlation,
                "tex_energy":      max(0, energy),
                "tex_homogeneity": max(0, homogeneity),
                # Shape
                "shape_elongation": max(1, elongation),
                "shape_circularity":max(0, min(1, circularity)),
                "edge_density":     max(0, edge_density),
                # Optical flow
                "flow_mean": max(0, optical_flow_mean),
                "flow_max":  max(0, optical_flow_max),
                # Magnetogram
                "total_flux":     total_flux,
                "flux_imbalance": abs(flux_imbalance),
                "polarity_sep":   max(0, polarity_sep),
                # H-alpha
                "ha_brightness": max(0, ha_brightness),
                "ha_area":       max(0, ha_area),
                "filament_flag": filament_flag,
            })

    df = pd.DataFrame(records)
    print(f"    Dataset: {len(df)} samples, {df.shape[1]} features")
    print(f"    Class distribution:")
    for cls, info in CME_CLASSES.items():
        n = (df['cme_class'] == cls).sum()
        print(f"      Class {cls} ({info['name']:20s}): {n:4d} samples ({n/len(df)*100:.1f}%)")
    return df


df = generate_cme_dataset(3000)

# ─────────────────────────────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────

def engineer_features(df):
    """Create derived features that improve classification signal."""
    print("\n[2/6] Engineering features...")
    d = df.copy()

    # Multi-channel EUV index (solar activity composite)
    d["euv_composite"]     = (d["euv_171_brightness"] * 0.3 +
                               d["euv_193_brightness"] * 0.5 +
                               d["euv_211_brightness"] * 0.2)
    # Active region complexity score
    d["ar_complexity_score"] = (d["ar_area"] * d["mag_complexity"] *
                                 np.log1p(d["sunspot_count"]) / 1e6)
    # Flare energy proxy
    d["flare_energy_proxy"] = d["flare_size"] * np.log1p(d["flare_peak"] * 1e6)

    # CME kinetic energy proxy (½mv²)
    d["cme_ke_proxy"]    = 0.5 * (d["cme_speed"] ** 2) / 1e6
    # CME momentum proxy
    d["cme_momentum"]    = d["cme_width"] * d["cme_speed"] / 360

    # Texture complexity index
    d["texture_index"]   = (d["tex_contrast"] * d["edge_density"] /
                             (d["tex_homogeneity"] + 1e-6))
    # Motion intensity
    d["motion_intensity"]= d["flow_mean"] * np.log1p(d["flow_max"])

    # Magnetic free energy proxy
    d["free_energy_proxy"]= d["total_flux"] * d["flux_imbalance"] * d["polarity_sep"]

    # Earth-direction likelihood (closeness to solar disk center ~180°)
    d["earth_direction_score"] = np.exp(-0.5 * ((d["cme_direction"] - 180) / 30) ** 2)

    # Halo + high-width combined
    d["halo_width_index"]= d["halo_flag"] * d["cme_width"]

    print(f"    Features after engineering: {d.shape[1]}")
    return d


df = engineer_features(df)

# Feature columns (exclude label columns)
LABEL_COLS = ["cme_class", "cme_class_name", "risk_level"]
FEATURE_COLS = [c for c in df.columns if c not in LABEL_COLS]

print(f"    Feature columns used for ML: {len(FEATURE_COLS)}")

# ─────────────────────────────────────────────────────────────────────
# 4. TRAIN / VALIDATION / TEST SPLIT
# ─────────────────────────────────────────────────────────────────────

X = df[FEATURE_COLS].values
y_cme  = df["cme_class"].values
y_risk = df["risk_level"].values

le_risk = LabelEncoder()
y_risk_enc = le_risk.fit_transform(y_risk)

X_train, X_test, y_cme_train, y_cme_test, y_risk_train, y_risk_test = train_test_split(
    X, y_cme, y_risk_enc, test_size=0.2, random_state=42, stratify=y_cme)

X_train, X_val, y_cme_train, y_cme_val, y_risk_train, y_risk_val = train_test_split(
    X_train, y_cme_train, y_risk_train,
    test_size=0.15, random_state=42, stratify=y_cme_train)

print(f"\n    Split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s   = scaler.transform(X_val)
X_test_s  = scaler.transform(X_test)

# ─────────────────────────────────────────────────────────────────────
# 5. STAGE 1 — CME TYPE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────

print("\n[3/6] Training CME Type Classifiers (Stage 1)...")

# 5a. Random Forest baseline
rf = RandomForestClassifier(
    n_estimators=300, max_depth=18, min_samples_split=4,
    class_weight='balanced', n_jobs=-1, random_state=42)
rf.fit(X_train_s, y_cme_train)
rf_val_acc = accuracy_score(y_cme_val, rf.predict(X_val_s))
print(f"    Random Forest     val accuracy: {rf_val_acc:.4f}")

# 5b. XGBoost CME classifier
cme_weights = {c: len(y_cme_train) / (6 * (y_cme_train == c).sum() + 1e-6)
               for c in range(6)}
sample_weights_train = np.array([cme_weights[c] for c in y_cme_train])

xgb_cme = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.5,
    objective='multi:softmax',
    num_class=6,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1,
)
xgb_cme.fit(
    X_train_s, y_cme_train,
    sample_weight=sample_weights_train,
    eval_set=[(X_val_s, y_cme_val)],
    verbose=False,
)
y_cme_pred = xgb_cme.predict(X_test_s)
y_cme_val_pred = xgb_cme.predict(X_val_s)

cme_test_acc = accuracy_score(y_cme_test, y_cme_pred)
cme_test_f1  = f1_score(y_cme_test, y_cme_pred, average='weighted')
print(f"    XGBoost CME       val accuracy: {accuracy_score(y_cme_val, y_cme_val_pred):.4f}")
print(f"    XGBoost CME      test accuracy: {cme_test_acc:.4f}")
print(f"    XGBoost CME      test F1 (wt): {cme_test_f1:.4f}")

# ─────────────────────────────────────────────────────────────────────
# 6. STAGE 2 — RISK CLASSIFICATION via XGBoost
# ─────────────────────────────────────────────────────────────────────

print("\n[4/6] Training Risk Classifier (Stage 2)...")

risk_labels = le_risk.classes_
print(f"    Risk classes: {list(risk_labels)}")

# Add predicted CME class as a feature for Stage 2
X_train_r = np.hstack([X_train_s, y_cme_train.reshape(-1, 1)])
X_val_r   = np.hstack([X_val_s,   y_cme_val.reshape(-1, 1)])
X_test_r  = np.hstack([X_test_s,  y_cme_pred.reshape(-1, 1)])  # use predicted

n_risk = len(np.unique(y_risk_train))
xgb_risk = xgb.XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.06,
    subsample=0.85,
    colsample_bytree=0.9,
    min_child_weight=2,
    gamma=0.05,
    reg_alpha=0.05,
    reg_lambda=1.2,
    objective='multi:softmax',
    num_class=n_risk,
    eval_metric='mlogloss',
    scale_pos_weight=1,
    random_state=42,
    n_jobs=-1,
)
xgb_risk.fit(
    X_train_r, y_risk_train,
    eval_set=[(X_val_r, y_risk_val)],
    verbose=False,
)
y_risk_pred = xgb_risk.predict(X_test_r)
y_risk_proba = xgb_risk.predict_proba(X_test_r)

risk_acc = accuracy_score(y_risk_test, y_risk_pred)
risk_f1  = f1_score(y_risk_test, y_risk_pred, average='weighted')
print(f"    XGBoost Risk     test accuracy: {risk_acc:.4f}")
print(f"    XGBoost Risk     test F1 (wt): {risk_f1:.4f}")

# ─────────────────────────────────────────────────────────────────────
# 7. FEATURE IMPORTANCE ANALYSIS
# ─────────────────────────────────────────────────────────────────────

print("\n[5/6] Computing feature importances...")

fi_cme = pd.Series(xgb_cme.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
fi_risk = pd.Series(xgb_risk.feature_importances_[:len(FEATURE_COLS)],
                    index=FEATURE_COLS).sort_values(ascending=False)

print("\n    Top 10 features for CME classification:")
for feat, imp in fi_cme.head(10).items():
    bar = "█" * int(imp * 400)
    print(f"      {feat:30s} {imp:.4f}  {bar}")

print("\n    Top 10 features for Risk classification:")
for feat, imp in fi_risk.head(10).items():
    bar = "█" * int(imp * 400)
    print(f"      {feat:30s} {imp:.4f}  {bar}")

# ─────────────────────────────────────────────────────────────────────
# 8. CROSS-VALIDATION
# ─────────────────────────────────────────────────────────────────────

print("\n    Cross-validation (5-fold) on full training set...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# Use simpler model for CV speed
cv_model = xgb.XGBClassifier(n_estimators=150, max_depth=6,
                               objective='multi:softmax', num_class=6,
                               random_state=42, n_jobs=-1, verbosity=0)
cv_scores = cross_val_score(cv_model,
                             scaler.transform(np.vstack([X_train, X_val])),
                             np.concatenate([y_cme_train, y_cme_val]),
                             cv=cv, scoring='f1_weighted')
print(f"    CV F1 scores: {cv_scores.round(4)}")
print(f"    CV mean ± std: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ─────────────────────────────────────────────────────────────────────
# 9. VISUALIZATION — COMPREHENSIVE RESULTS FIGURE
# ─────────────────────────────────────────────────────────────────────

print("\n[6/6] Generating visualizations...")

fig = plt.figure(figsize=(24, 32), facecolor='#0a0a10')
fig.suptitle(
    'CME Classification & Space Weather Risk Scoring Pipeline',
    fontsize=22, fontweight='bold', color='white', y=0.98
)

gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.95, bottom=0.03, left=0.06, right=0.97)

DARK = '#0a0a10'
SURFACE = '#12121e'
BORDER = '#2a2a40'
TEXT = '#e0e0f0'
MUTED = '#6b7280'

def style_ax(ax, title, subtitle=None):
    ax.set_facecolor(SURFACE)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_title(title, color=TEXT, fontsize=12, fontweight='600', pad=10)
    if subtitle:
        ax.set_title(f"{title}\n{subtitle}", color=TEXT, fontsize=11, fontweight='600', pad=10)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)

# ── Panel A: Class distribution
ax_dist = fig.add_subplot(gs[0, 0])
style_ax(ax_dist, "A · Dataset Class Distribution")
classes = [CME_CLASSES[i]["name"] for i in range(6)]
counts  = [(df['cme_class'] == i).sum() for i in range(6)]
colors  = [CME_CLASSES[i]["color"] for i in range(6)]
bars = ax_dist.barh(classes, counts, color=colors, alpha=0.85, height=0.6)
for bar, cnt in zip(bars, counts):
    ax_dist.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                 f'{cnt}', va='center', color=TEXT, fontsize=9)
ax_dist.set_xlabel("Sample Count", color=MUTED)
ax_dist.set_xlim(0, max(counts) * 1.15)

# ── Panel B: Speed distribution by class
ax_spd = fig.add_subplot(gs[0, 1])
style_ax(ax_spd, "B · CME Speed by Class")
for cls in range(1, 6):
    mask = df['cme_class'] == cls
    spds = df.loc[mask, 'cme_speed'].values
    ax_spd.violinplot(spds, positions=[cls], widths=0.7, showmedians=True,
                      showextrema=False)
ax_spd.set_xticks(range(1, 6))
ax_spd.set_xticklabels([CME_CLASSES[i]["name"][:8] for i in range(1, 6)],
                         rotation=30, ha='right', color=MUTED, fontsize=8)
ax_spd.set_ylabel("Speed (km/s)", color=MUTED)
ax_spd.axhline(400,  color='#60a5fa', lw=1, ls='--', alpha=0.6, label='400 km/s')
ax_spd.axhline(800,  color='#fbbf24', lw=1, ls='--', alpha=0.6, label='800 km/s')
ax_spd.axhline(1500, color='#f87171', lw=1, ls='--', alpha=0.6, label='1500 km/s')
ax_spd.legend(fontsize=8, facecolor=DARK, edgecolor=BORDER, labelcolor=MUTED)

# ── Panel C: Risk level distribution
ax_risk_dist = fig.add_subplot(gs[0, 2])
style_ax(ax_risk_dist, "C · Risk Level Distribution")
risk_names = ['Low', 'Moderate', 'High', 'Extreme']
risk_counts = [((df['risk_level'] == r) & (df['cme_class'] > 0)).sum() for r in risk_names]
risk_colors_list = [RISK_LEVELS[r]['color'] for r in risk_names]
wedges, texts, autotexts = ax_risk_dist.pie(
    risk_counts, labels=risk_names, colors=risk_colors_list,
    autopct='%1.1f%%', startangle=90,
    textprops={'color': TEXT, 'fontsize': 9},
    wedgeprops={'linewidth': 0, 'alpha': 0.85}
)
for at in autotexts:
    at.set_color(DARK)
    at.set_fontweight('bold')

# ── Panel D: CME Confusion Matrix
ax_cm = fig.add_subplot(gs[1, 0])
style_ax(ax_cm, "D · CME Classification\nConfusion Matrix (XGBoost)")
cm = confusion_matrix(y_cme_test, y_cme_pred)
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
short_names = [CME_CLASSES[i]["name"][:10] for i in range(6)]
cmap = LinearSegmentedColormap.from_list('cme', ['#0a0a10', '#6366f1', '#c084fc'])
im = ax_cm.imshow(cm_norm, cmap=cmap, vmin=0, vmax=1)
ax_cm.set_xticks(range(6)); ax_cm.set_yticks(range(6))
ax_cm.set_xticklabels(short_names, rotation=40, ha='right', color=MUTED, fontsize=7)
ax_cm.set_yticklabels(short_names, color=MUTED, fontsize=7)
for i in range(6):
    for j in range(6):
        c = 'white' if cm_norm[i,j] < 0.5 else DARK
        ax_cm.text(j, i, f'{cm_norm[i,j]:.2f}', ha='center', va='center',
                   color=c, fontsize=7, fontweight='600')
plt.colorbar(im, ax=ax_cm, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color=MUTED)

# ── Panel E: Risk Confusion Matrix
ax_rcm = fig.add_subplot(gs[1, 1])
style_ax(ax_rcm, "E · Risk Classification\nConfusion Matrix (XGBoost)")
rcm = confusion_matrix(y_risk_test, y_risk_pred)
rcm_norm = rcm.astype(float) / rcm.sum(axis=1, keepdims=True)
risk_tick_labels = le_risk.classes_
cmap2 = LinearSegmentedColormap.from_list('risk', ['#0a0a10', '#f97316', '#f87171'])
im2 = ax_rcm.imshow(rcm_norm, cmap=cmap2, vmin=0, vmax=1)
n_r = len(risk_tick_labels)
ax_rcm.set_xticks(range(n_r)); ax_rcm.set_yticks(range(n_r))
ax_rcm.set_xticklabels(risk_tick_labels, rotation=30, ha='right', color=MUTED, fontsize=9)
ax_rcm.set_yticklabels(risk_tick_labels, color=MUTED, fontsize=9)
for i in range(n_r):
    for j in range(n_r):
        c = 'white' if rcm_norm[i,j] < 0.5 else DARK
        ax_rcm.text(j, i, f'{rcm_norm[i,j]:.2f}', ha='center', va='center',
                    color=c, fontsize=9, fontweight='600')
plt.colorbar(im2, ax=ax_rcm, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color=MUTED)

# ── Panel F: Per-class F1 scores
ax_f1 = fig.add_subplot(gs[1, 2])
style_ax(ax_f1, "F · Per-Class F1 Score\nCME vs Risk Classifiers")
report_cme  = classification_report(y_cme_test, y_cme_pred, output_dict=True)
report_risk = classification_report(y_risk_test, y_risk_pred, output_dict=True)
cme_f1s  = [report_cme[str(i)]['f1-score'] for i in range(6)]
risk_f1s = [report_risk[str(i)]['f1-score'] for i in range(n_r)]
x_cme = np.arange(6)
ax_f1.bar(x_cme - 0.2, cme_f1s, width=0.38, color='#6366f1', alpha=0.8, label='CME type')
ax_f1_r = ax_f1.twinx()
ax_f1_r.bar(np.arange(n_r) + 0.2, risk_f1s, width=0.38, color='#f97316', alpha=0.8, label='Risk')
ax_f1.set_xticks(range(max(6, n_r)))
ax_f1.set_ylim(0, 1.1); ax_f1_r.set_ylim(0, 1.1)
ax_f1.set_ylabel("F1 (CME)", color='#6366f1'); ax_f1_r.set_ylabel("F1 (Risk)", color='#f97316')
ax_f1.set_xticklabels([f'C{i}' for i in range(max(6, n_r))], color=MUTED)
h1,l1 = ax_f1.get_legend_handles_labels(); h2,l2 = ax_f1_r.get_legend_handles_labels()
ax_f1.legend(h1+h2, l1+l2, fontsize=8, facecolor=DARK, edgecolor=BORDER, labelcolor=MUTED)
ax_f1_r.tick_params(colors=MUTED)
ax_f1_r.spines['right'].set_edgecolor(BORDER)

# ── Panel G: Feature importance CME (top 15)
ax_fi = fig.add_subplot(gs[2, :2])
style_ax(ax_fi, "G · Feature Importance — CME Type Classifier (Top 15)")
top15 = fi_cme.head(15)
gradient_colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, 15))
ax_fi.barh(range(15), top15.values[::-1], color=gradient_colors, alpha=0.85, height=0.65)
ax_fi.set_yticks(range(15))
ax_fi.set_yticklabels(top15.index[::-1], color=TEXT, fontsize=9)
ax_fi.set_xlabel("Feature Importance (gain)", color=MUTED)
for i, v in enumerate(top15.values[::-1]):
    ax_fi.text(v + 0.001, i, f'{v:.4f}', va='center', color=MUTED, fontsize=8)

# ── Panel H: Feature importance Risk (top 10)
ax_fir = fig.add_subplot(gs[2, 2])
style_ax(ax_fir, "H · Top Features\nRisk Classifier")
top10r = fi_risk.head(10)
ax_fir.barh(range(10), top10r.values[::-1], color='#f97316', alpha=0.75, height=0.6)
ax_fir.set_yticks(range(10))
ax_fir.set_yticklabels(top10r.index[::-1], color=TEXT, fontsize=9)
ax_fir.set_xlabel("Feature Importance", color=MUTED)

# ── Panel I: CME Speed vs Width scatter
ax_sw = fig.add_subplot(gs[3, 0])
style_ax(ax_sw, "I · CME Speed vs Angular Width")
for cls in range(1, 6):
    mask = df['cme_class'] == cls
    ax_sw.scatter(df.loc[mask, 'cme_width'], df.loc[mask, 'cme_speed'],
                  c=CME_CLASSES[cls]['color'], alpha=0.35, s=18, label=CME_CLASSES[cls]['name'])
ax_sw.axhline(400,  color='#60a5fa', lw=1, ls='--', alpha=0.5)
ax_sw.axhline(800,  color='#fbbf24', lw=1, ls='--', alpha=0.5)
ax_sw.axhline(1500, color='#f87171', lw=1, ls='--', alpha=0.5)
ax_sw.set_xlabel("CME Angular Width (°)", color=MUTED)
ax_sw.set_ylabel("CME Speed (km/s)", color=MUTED)
ax_sw.legend(fontsize=7, facecolor=DARK, edgecolor=BORDER, labelcolor=MUTED, markerscale=1.5)

# ── Panel J: Magnetic complexity vs AR Area
ax_mag = fig.add_subplot(gs[3, 1])
style_ax(ax_mag, "J · Magnetic Complexity vs AR Area")
for cls in range(6):
    mask = df['cme_class'] == cls
    ax_mag.scatter(np.log10(df.loc[mask, 'ar_area'] + 1),
                   df.loc[mask, 'mag_complexity'],
                   c=CME_CLASSES[cls]['color'], alpha=0.3, s=18,
                   label=CME_CLASSES[cls]['name'])
ax_mag.set_xlabel("log₁₀(Active Region Area)", color=MUTED)
ax_mag.set_ylabel("Magnetic Complexity (0-1)", color=MUTED)
ax_mag.legend(fontsize=7, facecolor=DARK, edgecolor=BORDER, labelcolor=MUTED, markerscale=1.5)

# ── Panel K: Risk score probability heatmap
ax_prob = fig.add_subplot(gs[3, 2])
style_ax(ax_prob, "K · Risk Probability\nby Predicted CME Class")
# Mean probability of each risk level for each predicted CME class
pred_cme_test = y_cme_pred
prob_matrix = np.zeros((6, n_r))
for cls in range(6):
    idx = pred_cme_test == cls
    if idx.sum() > 0:
        prob_matrix[cls] = y_risk_proba[idx].mean(axis=0)
cmap3 = LinearSegmentedColormap.from_list('prob', ['#0a0a10', '#f97316'])
im3 = ax_prob.imshow(prob_matrix, cmap=cmap3, aspect='auto', vmin=0, vmax=1)
ax_prob.set_xticks(range(n_r))
ax_prob.set_xticklabels(le_risk.classes_, rotation=30, ha='right', color=MUTED, fontsize=8)
ax_prob.set_yticks(range(6))
ax_prob.set_yticklabels([CME_CLASSES[i]['name'][:10] for i in range(6)], color=MUTED, fontsize=7)
for i in range(6):
    for j in range(n_r):
        c = 'white' if prob_matrix[i,j] < 0.5 else DARK
        ax_prob.text(j, i, f'{prob_matrix[i,j]:.2f}', ha='center', va='center',
                     color=c, fontsize=8)
plt.colorbar(im3, ax=ax_prob, fraction=0.046, pad=0.04)

# ── Panel L: Pipeline architecture diagram
ax_arch = fig.add_subplot(gs[4, :])
style_ax(ax_arch, "L · End-to-End CME Classification & Risk Scoring Pipeline")
ax_arch.set_xlim(0, 20); ax_arch.set_ylim(0, 4)
ax_arch.axis('off')

boxes = [
    # (x, y, w, h, label, sublabel, color)
    (0.1,  1.2, 2.2, 1.6, "SOLAR\nIMAGERY", "EUV 171/193/211Å\nCoronagraph\nMagnetogram\nH-alpha", "#3730a3"),
    (2.8,  1.2, 2.2, 1.6, "FEATURE\nEXTRACTION", "Brightness/Texture\nShape/Flow\nActive Region\nMagnetic", "#4338ca"),
    (5.5,  1.2, 2.2, 1.6, "FEATURE\nENGINEERING", "EUV Composite\nAR Complexity\nCME KE Proxy\nEarth Score", "#6d28d9"),
    (8.2,  1.2, 2.4, 1.6, "STAGE 1\nXGBoost", "CME Type\nClassification\n6 Classes\n500 trees", "#7c3aed"),
    (11.1, 1.2, 2.4, 1.6, "STAGE 2\nXGBoost", "Risk Level\nClassification\n4 Levels\n400 trees", "#9333ea"),
    (14.0, 1.8, 2.4, 1.0, "CME TYPE\nOUTPUT", "No CME / Slow\nModerate / Fast\nHalo / Earth-dir", "#6366f1"),
    (14.0, 0.2, 2.4, 1.0, "RISK LEVEL\nOUTPUT", "Low / Moderate\nHigh / Extreme\n+ Probability", "#f97316"),
    (17.0, 0.7, 2.8, 2.0, "OPERATIONAL\nFORECAST", "Alert Level\nImpact Windows\nSatellite Risk\nGrid Warning", "#dc2626"),
]

for (x, y, w, h, title, sub, col) in boxes:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                    facecolor=col, edgecolor='white',
                                    linewidth=1, alpha=0.85, zorder=2)
    ax_arch.add_patch(rect)
    ax_arch.text(x + w/2, y + h - 0.28, title, ha='center', va='top',
                 color='white', fontsize=7.5, fontweight='bold', zorder=3)
    ax_arch.text(x + w/2, y + 0.12, sub, ha='center', va='bottom',
                 color='rgba(255,255,255,0.75)' if False else '#ccc',
                 fontsize=6, zorder=3, linespacing=1.4)

# Arrows
arrows_xy = [
    (2.3, 2.0, 0.5, 0), (5.0, 2.0, 0.5, 0),
    (7.7, 2.0, 0.5, 0), (10.6, 2.0, 0.5, 0),
    (13.5, 2.0, 0.5,  0.45),
    (13.5, 1.9, 0.5, -0.45),
    (16.4, 2.3, 0.6, 0), (16.4, 1.0, 0.6, 0),
]
for (x1, y1, dx, dy) in arrows_xy:
    ax_arch.annotate('', xy=(x1+dx, y1+dy), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color='#6366f1', lw=1.5),
                     zorder=4)

# Performance metrics text
metrics_txt = (
    f"Pipeline Performance   |   "
    f"CME Classification: Acc={cme_test_acc:.3f}  F1={cme_test_f1:.3f}   |   "
    f"Risk Classification: Acc={risk_acc:.3f}  F1={risk_f1:.3f}   |   "
    f"CV F1: {cv_scores.mean():.3f}±{cv_scores.std():.3f}"
)
fig.text(0.5, 0.01, metrics_txt, ha='center', color=MUTED, fontsize=10,
         fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=0.4', facecolor=SURFACE, edgecolor=BORDER))

plt.savefig('/mnt/user-data/outputs/cme_pipeline_results.png',
            dpi=150, bbox_inches='tight', facecolor=DARK)
print("    Saved: cme_pipeline_results.png")

# ─────────────────────────────────────────────────────────────────────
# 10. SAVE TRAINED MODELS & ARTIFACTS
# ─────────────────────────────────────────────────────────────────────

import pickle, json, os
os.makedirs('/mnt/user-data/outputs/cme_models', exist_ok=True)

# Save models
with open('/mnt/user-data/outputs/cme_models/xgb_cme_classifier.pkl', 'wb') as f:
    pickle.dump(xgb_cme, f)
with open('/mnt/user-data/outputs/cme_models/xgb_risk_classifier.pkl', 'wb') as f:
    pickle.dump(xgb_risk, f)
with open('/mnt/user-data/outputs/cme_models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
with open('/mnt/user-data/outputs/cme_models/label_encoder_risk.pkl', 'wb') as f:
    pickle.dump(le_risk, f)

# Save feature list
with open('/mnt/user-data/outputs/cme_models/feature_columns.json', 'w') as f:
    json.dump(FEATURE_COLS, f, indent=2)

# Save metrics
metrics = {
    "cme_classifier": {
        "model": "XGBoostClassifier",
        "n_estimators": 500,
        "test_accuracy": round(cme_test_acc, 4),
        "test_f1_weighted": round(cme_test_f1, 4),
        "cv_f1_mean": round(float(cv_scores.mean()), 4),
        "cv_f1_std": round(float(cv_scores.std()), 4),
        "n_features": len(FEATURE_COLS),
        "classes": {str(k): v["name"] for k, v in CME_CLASSES.items()},
    },
    "risk_classifier": {
        "model": "XGBoostClassifier",
        "n_estimators": 400,
        "test_accuracy": round(risk_acc, 4),
        "test_f1_weighted": round(risk_f1, 4),
        "classes": list(le_risk.classes_),
    },
    "top_features_cme": fi_cme.head(10).to_dict(),
    "top_features_risk": fi_risk.head(10).to_dict(),
}
with open('/mnt/user-data/outputs/cme_models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("    Saved: models, scaler, encoder, feature list, metrics JSON")

# ─────────────────────────────────────────────────────────────────────
# 11. INFERENCE EXAMPLE — simulate a new event
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("  INFERENCE EXAMPLE — New Solar Event")
print("=" * 70)

def predict_event(event_features: dict):
    """
    Given raw image features from a new solar event,
    return CME type + risk classification + probability scores.
    """
    row = pd.DataFrame([event_features])[FEATURE_COLS]
    # Add any missing features as 0
    for col in FEATURE_COLS:
        if col not in row.columns:
            row[col] = 0.0
    row = row.fillna(0.0)
    X_new = scaler.transform(row.values)

    # Stage 1: CME type
    cme_pred  = xgb_cme.predict(X_new)[0]
    cme_proba = xgb_cme.predict_proba(X_new)[0]

    # Stage 2: Risk (add predicted CME class as feature)
    X_new_r   = np.hstack([X_new, [[cme_pred]]])
    risk_pred  = xgb_risk.predict(X_new_r)[0]
    risk_proba = xgb_risk.predict_proba(X_new_r)[0]
    risk_name  = le_risk.classes_[risk_pred]

    return {
        "cme_class": int(cme_pred),
        "cme_class_name": CME_CLASSES[int(cme_pred)]["name"],
        "cme_probabilities": {CME_CLASSES[i]["name"]: round(float(p), 4) for i, p in enumerate(cme_proba)},
        "risk_level": risk_name,
        "risk_probabilities": {le_risk.classes_[i]: round(float(p), 4) for i, p in enumerate(risk_proba)},
    }

# Simulate a fast halo CME event
fast_halo_event = {
    "euv_171_brightness": 2200, "euv_193_brightness": 2600, "euv_211_brightness": 1600,
    "euv_171_193_ratio": 2200/2600, "euv_193_211_ratio": 2600/1600,
    "ar_area": 80000, "sunspot_area": 35000, "sunspot_count": 18,
    "mag_complexity": 0.82, "flare_size": 4.5, "flare_peak": 1.2e-4,
    "halo_flag": 1, "cme_width": 360, "cme_direction": 185,
    "cme_speed": 1850, "cme_accel": -12,
    "tex_contrast": 0.78, "tex_correlation": 0.55, "tex_energy": 0.22, "tex_homogeneity": 0.31,
    "shape_elongation": 1.9, "shape_circularity": 0.45, "edge_density": 0.42,
    "flow_mean": 28, "flow_max": 95,
    "total_flux": 8e21, "flux_imbalance": 0.45, "polarity_sep": 38,
    "ha_brightness": 1.8, "ha_area": 12000, "filament_flag": 1,
    # Engineered features
    "euv_composite": 2200*0.3 + 2600*0.5 + 1600*0.2,
    "ar_complexity_score": 80000 * 0.82 * np.log1p(18) / 1e6,
    "flare_energy_proxy": 4.5 * np.log1p(1.2e-4 * 1e6),
    "cme_ke_proxy": 0.5 * 1850**2 / 1e6,
    "cme_momentum": 360 * 1850 / 360,
    "texture_index": 0.78 * 0.42 / (0.31 + 1e-6),
    "motion_intensity": 28 * np.log1p(95),
    "free_energy_proxy": 8e21 * 0.45 * 38,
    "earth_direction_score": np.exp(-0.5 * ((185 - 180) / 30)**2),
    "halo_width_index": 1 * 360,
}

result = predict_event(fast_halo_event)
print(f"\n  Event: Suspected Fast Halo CME (synthetic)")
print(f"  ─────────────────────────────────────────")
print(f"  CME Classification : {result['cme_class_name']}  (Class {result['cme_class']})")
print(f"  Risk Level         : {result['risk_level']}")
print(f"\n  CME Type Probabilities:")
for cls, prob in result['cme_probabilities'].items():
    bar = "█" * int(prob * 40)
    print(f"    {cls:25s}  {prob:.4f}  {bar}")
print(f"\n  Risk Level Probabilities:")
for lvl, prob in result['risk_probabilities'].items():
    bar = "█" * int(prob * 40)
    print(f"    {lvl:12s}  {prob:.4f}  {bar}")

print("\n" + "=" * 70)
print("  CLASSIFICATION REPORT — CME Type (XGBoost)")
print("=" * 70)
target_names = [CME_CLASSES[i]["name"] for i in range(6)]
print(classification_report(y_cme_test, y_cme_pred, target_names=target_names))

print("=" * 70)
print("  CLASSIFICATION REPORT — Risk Level (XGBoost)")
print("=" * 70)
print(classification_report(y_risk_test, y_risk_pred,
                             target_names=le_risk.classes_))

print("=" * 70)
print("  PIPELINE COMPLETE")
print("=" * 70)
print(f"  CME Type  — Accuracy: {cme_test_acc:.4f}  |  F1: {cme_test_f1:.4f}")
print(f"  Risk Level — Accuracy: {risk_acc:.4f}  |  F1: {risk_f1:.4f}")
print(f"  Artifacts saved to: /mnt/user-data/outputs/cme_models/")
print("=" * 70)
