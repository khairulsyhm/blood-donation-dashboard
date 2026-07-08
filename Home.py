# ============================================================
# Home.py — MAIN PAGE of the Streamlit website
# ============================================================
# In Streamlit, the file called "Home.py" (the one you run) becomes
# the first page. Any file placed inside a folder called "pages/"
# automatically becomes an extra page in the sidebar menu.
# ============================================================

import streamlit as st
import pandas as pd

# ---- PAGE CONFIG ----
# This sets the browser tab title, the little icon, and makes the
# app use the full width of the screen. Must be the first Streamlit
# command in the file.
st.set_page_config(
    page_title="Selangor Blood Donation Forecasting",
    page_icon="🩸",
    layout="wide"
)

# ---- BLOOD-THEMED STYLING ----
# Custom CSS to give the whole app a blood donation theme.
# This applies to ALL pages (Streamlit shares CSS across pages).
st.markdown("""
<style>
    /* Header banner with blood-red gradient */
    .stApp > header {
        background: linear-gradient(90deg, #8B0000, #C0392B) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0000 0%, #2d0a0a 100%);
    }
    [data-testid="stSidebar"] * {
        color: #f0d0d0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ff9999 !important;
    }

    /* Metric cards — white background with red top border */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-top: 4px solid #C0392B;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    [data-testid="stMetric"] label {
        color: #666666 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }

    /* Blood drop decorative separator */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C0392B, transparent);
        margin: 1.5rem 0;
    }

    /* Subheaders in blood red */
    h2, h3 {
        color: #8B0000 !important;
    }

    /* Info/success/warning/error box styling */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
    }

    /* Footer styling */
    .stCaption {
        color: #999 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA (shared by all pages) ----
# @st.cache_data tells Streamlit: "load this CSV once and remember it"
# so the website stays fast and does not re-read the file every click.
@st.cache_data
def load_data():
    df = pd.read_csv("blood_donation_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ---- HEADER ----
st.title("🩸 Selangor Blood Donation Forecasting System")
st.markdown("#### Predicting daily blood donation trends using Machine Learning (XGBoost)")
st.markdown("---")

# ---- PROJECT SUMMARY ----
st.markdown("""
Welcome to the **Selangor Blood Donation Forecasting Dashboard**.

This system uses an **XGBoost machine learning model** to forecast daily blood
donations in Selangor, Malaysia. It transforms historical public donation data
into a **30-day future forecast**, helping hospital administrators plan blood
drives and avoid shortages before they happen.

Use the menu on the **left sidebar** to explore:
""")

# ---- NAVIGATION GUIDE (3 cards using columns) ----
# st.columns(3) splits the row into 3 equal side-by-side boxes.
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    ### 📊 Historical Analysis
    See how accurately the model predicted **past** donations, and explore
    weekly and seasonal patterns.
    """)

with col2:
    st.success("""
    ### 🔮 30-Day Forecast
    View the **future** 30-day prediction for each blood type and check
    shortage risk warnings.
    """)

with col3:
    st.warning("""
    ### 📥 Download Center
    Download the full forecast data as **CSV** or a formatted **PDF report**
    for offline use and sharing.
    """)

st.markdown("---")

# ---- KEY METRICS AT A GLANCE ----
st.subheader("📈 Model Performance at a Glance")

# st.metric shows a big number with a label — perfect for KPIs.
m1, m2, m3, m4 = st.columns(4)

# Calculate the numbers from the data
hist = df[df["Data_Type"] == "Historical"]
fore = df[df["Data_Type"] == "Future Forecast"]
total_hist = int(hist["Actual_Donations"].sum())
total_fore = int(fore["Predicted_Donations"].sum())

m1.metric("Model Accuracy (R²)", "86.73%")
m2.metric("Avg Error (MAE)", "65.36 bags/day")
m3.metric("Total Historical Bags", f"{total_hist:,}")
m4.metric("Predicted Next 30 Days", f"{total_fore:,}")

st.markdown("---")

# ---- FOOTER ----
st.caption("""
Developed by Khairul Syahmi bin Khairul Nizam (2023436178) ·
Supervised by En. Azizian bin Mohd Sapawi ·
Universiti Teknologi MARA (UiTM) · 2026
""")
