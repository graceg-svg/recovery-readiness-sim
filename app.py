import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Recovery Readiness Diet Simulator", layout="centered")

st.title("Recovery Readiness Diet Simulator")
st.caption(
    "Educational simulation for comparing diet patterns and recovery-readiness proxies. Not medical advice."
)

with st.expander("What do the inputs and outputs mean?"):
    st.markdown(
        """
**Inputs (0–10 proxies)**  
- **Repair support:** Proxy for how much the diet supports tissue repair and nervous system recovery (protein quality + micronutrient density).  
- **Inflammation calming:** Proxy for how much the diet supports downshifting inflammation (omega-3 + fiber + polyphenols + whole foods).  
- **Processed load:** Proxy for ultra-processed intake (added sugar/refined oils/packaged foods). Higher = worse.

**Outputs**  
- **Recovery readiness (0–100):** A relative score computed from the inputs. Higher = better recovery environment *in this model*.  
- **14-day inflammation curve (proxy):** Simulated inflammation resolution after injury. Higher readiness → faster decline.  

*Note: This is an educational proxy model for comparing scenarios and generating hypotheses. It does not provide medical advice or predict personal recovery timelines.*
"""
    )

# 0–10 scale inputs (simple proxies)
diet_library = {
    "Typical Teen (Processed-Heavy)": {"repair_support": 3, "inflammation_calming": 3, "processed_load": 8},
    "Mediterranean Recovery": {"repair_support": 7, "inflammation_calming": 8, "processed_load": 2},
    "Anti-Inflammatory Focus": {"repair_support": 6, "inflammation_calming": 9, "processed_load": 2},
    "High-Protein Unbalanced Athlete": {"repair_support": 5, "inflammation_calming": 4, "processed_load": 6},
    "High-Protein Balanced Athlete": {"repair_support": 7, "inflammation_calming": 6, "processed_load": 4},
    "Whole-Food Plant-Based": {"repair_support": 6, "inflammation_calming": 8, "processed_load": 2},
    "Vegetarian (Packaged/Processed)": {"repair_support": 4, "inflammation_calming": 5, "processed_load": 6},
    "DASH-Style": {"repair_support": 6, "inflammation_calming": 7, "processed_load": 3},
    "Low-Carb Whole Foods": {"repair_support": 6, "inflammation_calming": 6, "processed_load": 3},
    "Ultra-Processed Convenience": {"repair_support": 2, "inflammation_calming": 2, "processed_load": 9},
}

def recovery_readiness_raw(d):
    r = d["repair_support"] / 10
    i = d["inflammation_calming"] / 10
    p = d["processed_load"] / 10
    return float(0.45 * r + 0.45 * i - 0.35 * p)

# Theoretical bounds of the formula
MIN_RAW, MAX_RAW = -0.35, 0.90

def to_0_100(raw):
    return 100 * (raw - MIN_RAW) / (MAX_RAW - MIN_RAW)

def simulate_inflammation_curve(readiness_0_100, days=14, initial_load=1.0, floor=0.15):
    readiness = max(0.0, min(1.0, readiness_0_100 / 100.0))
    k = 0.10 + 0.40 * readiness  # Higher readiness -> faster decay
    t = np.arange(0, days + 1)
    load = floor + (initial_load - floor) * np.exp(-k * t)
    return t, load

st.subheader("1) Choose diets to compare")

options = list(diet_library.keys())
default = ["Mediterranean Recovery", "Typical Teen (Processed-Heavy)"]

st.sidebar.header("Controls")
selected = st.sidebar.multiselect("Pick 2–4 diets", options, default=default)

if len(selected) < 2:
    st.warning("Pick at least 2 diets.")
    st.stop()
if len(selected) > 4:
    st.warning("Keep it simple: Pick max 4 diets.")
    selected = selected[:4]

st.sidebar.markdown("---")
st.sidebar.subheader("Custom diet (Optional)")

repair_support = st.sidebar.slider("Repair support", 0, 10, 5)
inflammation_calming = st.sidebar.slider("Inflammation calming", 0, 10, 5)
processed_load = st.sidebar.slider("Processed load", 0, 10, 5)

include_custom = st.sidebar.checkbox("Include custom diet", value=False)

rows = []
for name in selected:
    d = diet_library[name]
    raw = recovery_readiness_raw(d)
    rows.append(
        {
            "diet": name,
            **d,
            "recovery_readiness_0_100": to_0_100(raw),
        }
    )

if include_custom:
    d = {
        "repair_support": repair_support,
        "inflammation_calming": inflammation_calming,
        "processed_load": processed_load,
    }
    raw = recovery_readiness_raw(d)
    rows.append(
        {
            "diet": "Your Custom Diet",
            **d,
            "recovery_readiness_0_100": to_0_100(raw),
        }
    )

df = pd.DataFrame(rows).sort_values("recovery_readiness_0_100", ascending=False)

st.subheader("Results")
st.dataframe(df, use_container_width=True)

# Smaller charts
fig1 = plt.figure(figsize=(6, 3), dpi=150)
plt.bar(df["diet"], df["recovery_readiness_0_100"])
plt.xticks(rotation=25, ha="right")
plt.ylabel("Recovery readiness (0–100)")
plt.title("Recovery readiness by diet (proxy)")
plt.tight_layout()
st.pyplot(fig1)

show_curve = st.checkbox("Show 14-day inflammation resolution curve", value=True)
if show_curve:
    fig2 = plt.figure(figsize=(6, 3), dpi=150)
    for _, row in df.iterrows():
        t, load = simulate_inflammation_curve(row["recovery_readiness_0_100"], days=14)
        plt.plot(t, load, label=row["diet"])
    plt.xlabel("Days after injury")
    plt.ylabel("Inflammation load (proxy)")
    plt.title("Simulated post-injury inflammation resolution (proxy)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    st.pyplot(fig2)

st.caption(
    "Note: Simplified proxy model for comparing scenarios and generating hypotheses. Not a medical prediction tool."
)
