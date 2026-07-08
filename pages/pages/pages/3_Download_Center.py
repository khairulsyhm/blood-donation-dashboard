# ============================================================
# pages/3_Download_Center.py — DOWNLOAD PAGE
# ============================================================
# This page fulfils the objective: "user can download the report."
# It offers 3 downloads:
#   1. Full data as CSV
#   2. Forecast-only data as CSV
#   3. A formatted PDF summary report (generated with FPDF)
# ============================================================

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Download Center", page_icon="📥", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("blood_donation_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()
hist = df[df["Data_Type"] == "Historical"].copy()
fore = df[df["Data_Type"] == "Future Forecast"].copy()

# ---- PAGE TITLE ----
st.title("📥 Download Center")
st.markdown("Download the forecast data and summary report in your preferred format.")
st.markdown("---")

# ============================================================
# SECTION 1 — CSV DOWNLOADS
# ============================================================
st.subheader("📊 Data Downloads (CSV)")
st.caption("CSV files open in Excel or Google Sheets.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Full Dataset**")
    st.write("Historical + forecast data, all columns.")
    # Convert dataframe to CSV text, then offer as download.
    # This is the core Streamlit download feature — one function.
    full_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Full Data (CSV)",
        data=full_csv,
        file_name="blood_donation_full_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.markdown("**30-Day Forecast Only**")
    st.write("Just the future predictions.")
    fore_csv = fore.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Forecast Only (CSV)",
        data=fore_csv,
        file_name="blood_donation_30day_forecast.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")

# ============================================================
# SECTION 2 — PDF REPORT
# ============================================================
st.subheader("📄 Summary Report (PDF)")
st.caption("A formatted report with model performance, forecast summary, and risk status.")

# ---- BUILD THE PDF (function) ----
def create_pdf_report():
    # Calculate all the numbers we want in the report
    total_hist = int(hist["Actual_Donations"].sum())
    total_fore = int(fore["Predicted_Donations"].sum())
    hist_daily_avg = hist.groupby("Date")["Actual_Donations"].sum().mean()
    fore_daily = fore.groupby("Date")["Predicted_Donations"].sum()
    fore_avg = fore_daily.mean()
    lowest_day = fore_daily.min()
    safety_line = hist_daily_avg * 0.7
    is_high_risk = lowest_day < safety_line

    # Per-blood-type forecast totals
    bt_totals = fore.groupby("Blood_Type")["Predicted_Donations"].sum()

    # Create the PDF object
    pdf = FPDF()
    pdf.add_page()

    # --- Title ---
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Selangor Blood Donation Forecasting Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
    pdf.ln(6)

    # --- Model Performance ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Model Performance", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Algorithm: XGBoost (Extreme Gradient Boosting)", ln=True)
    pdf.cell(0, 7, "R-Squared Accuracy: 86.73%", ln=True)
    pdf.cell(0, 7, "Mean Absolute Error (MAE): 65.36 bags/day", ln=True)
    pdf.cell(0, 7, "Root Mean Squared Error (RMSE): 103.54 bags/day", ln=True)
    pdf.ln(4)

    # --- Summary ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Forecast Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Total Historical Donations: {total_hist:,} bags", ln=True)
    pdf.cell(0, 7, f"Total Predicted (Next 30 Days): {total_fore:,} bags", ln=True)
    pdf.cell(0, 7, f"Historical Daily Average: {hist_daily_avg:,.0f} bags/day", ln=True)
    pdf.cell(0, 7, f"Forecast Daily Average: {fore_avg:,.0f} bags/day", ln=True)
    pdf.cell(0, 7, f"Safety Threshold (70%): {safety_line:,.0f} bags/day", ln=True)
    pdf.cell(0, 7, f"Lowest Forecast Day: {lowest_day:,.0f} bags", ln=True)
    pdf.ln(4)

    # --- Risk Status ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Shortage Risk Status", ln=True)
    pdf.set_font("Helvetica", "B", 11)
    if is_high_risk:
        pdf.set_text_color(192, 57, 43)  # red
        pdf.cell(0, 7, "Status: HIGH RISK - Forecast dips below safety threshold.", ln=True)
    else:
        pdf.set_text_color(39, 174, 96)  # green
        pdf.cell(0, 7, "Status: STABLE - Supply stays above safety threshold.", ln=True)
    pdf.set_text_color(0, 0, 0)  # reset to black
    pdf.ln(4)

    # --- Per Blood Type ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Predicted Supply by Blood Type (Next 30 Days)", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for bt in ["A", "B", "AB", "O"]:
        if bt in bt_totals.index:
            pdf.cell(0, 7, f"Type {bt}: {int(bt_totals[bt]):,} bags", ln=True)
    pdf.ln(6)

    # --- Footer ---
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5,
        "This report was generated by the Selangor Blood Donation Forecasting System. "
        "Developed by Khairul Syahmi bin Khairul Nizam (2023436178), supervised by "
        "En. Azizian bin Mohd Sapawi, Universiti Teknologi MARA (UiTM), 2026.")

    # Return the PDF as bytes so Streamlit can offer it for download
    return bytes(pdf.output())

# ---- DOWNLOAD BUTTON FOR PDF ----
st.write("Click below to generate and download the full PDF report:")
pdf_bytes = create_pdf_report()
st.download_button(
    label="⬇️ Download PDF Report",
    data=pdf_bytes,
    file_name=f"Blood_Donation_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf",
    use_container_width=True
)

st.markdown("---")

# ---- PREVIEW OF WHAT'S IN THE REPORT ----
st.subheader("📋 Report Preview")
st.info("""
The PDF report contains:
- **Model Performance** — accuracy metrics (R², MAE, RMSE)
- **Forecast Summary** — total historical & predicted donations, daily averages
- **Shortage Risk Status** — automatic High Risk / Stable assessment
- **Blood Type Breakdown** — predicted supply for each blood type
""")
