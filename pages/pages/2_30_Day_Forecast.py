# ============================================================
# pages/2_30_Day_Forecast.py — THE "FUTURE" PAGE
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="30-Day Forecast", page_icon="🔮", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("blood_donation_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()
fore = df[df["Data_Type"] == "Future Forecast"].copy()
hist = df[df["Data_Type"] == "Historical"].copy()

# ---- PAGE TITLE ----
st.title("🔮 30-Day Blood Donation Forecast")
st.markdown("Predicting the **next 30 days** to help plan blood drives ahead of shortages.")
st.markdown("---")

# ---- SIDEBAR FILTER ----
st.sidebar.header("🔍 Filters")
blood_types = st.sidebar.multiselect(
    "Select Blood Type(s):",
    options=sorted(fore["Blood_Type"].unique()),
    default=sorted(fore["Blood_Type"].unique())
)
filtered = fore[fore["Blood_Type"].isin(blood_types)]

# ---- 3-LEVEL SHORTAGE RISK ----
# Instead of a simple yes/no, we count how many forecast days
# fall below critical and caution thresholds from historical data.
# p10 = bottom 10% of historical days (critical)
# p25 = bottom 25% of historical days (caution)
hist_filtered = hist[hist["Blood_Type"].isin(blood_types)]
hist_daily = hist_filtered.groupby("Date")["Actual_Donations"].sum()
p10 = hist_daily.quantile(0.10) if len(hist_daily) > 0 else 0
p25 = hist_daily.quantile(0.25) if len(hist_daily) > 0 else 0

fore_daily = filtered.groupby("Date")["Predicted_Donations"].sum()
lowest_day = fore_daily.min() if len(fore_daily) > 0 else 0
critical_days = int((fore_daily < p10).sum()) if len(fore_daily) > 0 else 0
caution_days = int(((fore_daily >= p10) & (fore_daily < p25)).sum()) if len(fore_daily) > 0 else 0
ok_days = int((fore_daily >= p25).sum()) if len(fore_daily) > 0 else 0

if critical_days > 0:
    risk_level = "🔴 High Risk"
    risk_color = "error"
elif caution_days > 0:
    risk_level = "🟡 Moderate"
    risk_color = "warning"
else:
    risk_level = "🟢 Low Risk"
    risk_color = "success"

# ---- KPI ROW ----
k1, k2, k3, k4 = st.columns(4)
total_fore = int(filtered["Predicted_Donations"].sum())
avg_fore = fore_daily.mean() if len(fore_daily) > 0 else 0

k1.metric("Total Predicted (30 Days)", f"{total_fore:,} bags")
k2.metric("Average Daily Forecast", f"{avg_fore:,.0f} bags")
k3.metric("Lowest Forecast Day", f"{lowest_day:,.0f} bags")
k4.metric("Shortage Risk", risk_level)

# ---- RISK BANNER ----
if critical_days > 0:
    st.error(f"🔴 **High Risk:** **{critical_days}** day(s) are predicted to drop "
             f"below the critical threshold ({p10:,.0f} bags). "
             f"Additionally, **{caution_days}** day(s) are in the caution zone. "
             f"Immediate action recommended — schedule emergency blood drives.")
elif caution_days > 0:
    st.warning(f"🟡 **Moderate Risk:** No critical days detected, but **{caution_days}** "
               f"day(s) fall in the caution zone (below {p25:,.0f} bags). "
               f"Consider planning targeted donation drives as a precaution.")
else:
    st.success(f"🟢 **Low Risk:** All 30 forecast days remain above the caution "
               f"threshold ({p25:,.0f} bags). Supply is healthy for the next month.")

st.markdown("---")

# ---- CHART 1: FORECAST LINE CHART ----
st.subheader("30-Day Forecast by Blood Type")
st.caption("Each line is one blood type's predicted daily donations for the next 30 days.")

colors = {"A": "#C0392B", "B": "#2C3E50", "AB": "#E67E22", "O": "#27AE60"}
fig1 = go.Figure()
for bt in sorted(filtered["Blood_Type"].unique()):
    bt_data = filtered[filtered["Blood_Type"] == bt].sort_values("Date")
    fig1.add_trace(go.Scatter(
        x=bt_data["Date"], y=bt_data["Predicted_Donations"],
        name=f"Type {bt}", mode="lines+markers",
        line=dict(color=colors.get(bt, "#888"), width=2)
    ))
fig1.update_layout(
    height=420, hovermode="x unified",
    xaxis_title="Date", yaxis_title="Predicted Blood Bags",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ---- CHART 2 & 3 ----
c1, c2 = st.columns(2)

with c1:
    st.subheader("Predicted Supply Share by Blood Type")
    bt_total = filtered.groupby("Blood_Type")["Predicted_Donations"].sum().reset_index()
    fig2 = px.pie(
        bt_total, names="Blood_Type", values="Predicted_Donations",
        hole=0.45, color="Blood_Type", color_discrete_map=colors
    )
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    st.subheader("Total Forecast by Blood Type")
    fig3 = px.bar(
        bt_total, x="Blood_Type", y="Predicted_Donations",
        color="Blood_Type", color_discrete_map=colors,
        labels={"Predicted_Donations": "Total Bags", "Blood_Type": "Blood Type"}
    )
    fig3.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---- ACTIONABLE INSIGHTS ----
st.subheader("💡 Actionable Insights")

fore_by_bt = filtered.groupby("Blood_Type")["Predicted_Donations"].sum()
if len(fore_by_bt) > 0:
    lowest_bt = fore_by_bt.idxmin()

    fore_weekend = filtered[filtered["Is_Weekend"] == 1].groupby("Date")["Predicted_Donations"].sum()
    fore_weekday = filtered[filtered["Is_Weekend"] == 0].groupby("Date")["Predicted_Donations"].sum()
    weekend_avg = fore_weekend.mean() if len(fore_weekend) > 0 else 0
    weekday_avg = fore_weekday.mean() if len(fore_weekday) > 0 else 0

    holiday_days = filtered[filtered["Is_Holiday"] == 1]["Date"].dt.strftime("%d %b").unique()
    ramadan_days = filtered[filtered["Is_Ramadan"] == 1]["Date"].dt.strftime("%d %b").unique()

    i1, i2 = st.columns(2)

    with i1:
        st.info(f"""
        **🩸 Blood Type to Watch:** Type **{lowest_bt}** has the lowest total
        predicted supply ({int(fore_by_bt[lowest_bt]):,} bags) over the next 30 days.
        Consider targeting Type {lowest_bt} donors in upcoming drives.
        """)

        if len(holiday_days) > 0:
            st.warning(f"""
            **📅 Holiday Alert:** The forecast period includes public holidays
            on **{', '.join(holiday_days)}**. Expect reduced donations on these days
            and plan drives around them.
            """)
        else:
            st.success("**📅 No public holidays** fall within the 30-day forecast window.")

    with i2:
        if weekday_avg > 0:
            diff_pct = ((weekend_avg - weekday_avg) / weekday_avg) * 100
            direction = "higher" if diff_pct > 0 else "lower"
            st.info(f"""
            **📆 Weekend Pattern:** Forecast shows weekends averaging
            **{weekend_avg:,.0f}** bags/day vs **{weekday_avg:,.0f}** on weekdays
            ({abs(diff_pct):.1f}% {direction}). Schedule major drives on high-turnout days.
            """)

        if len(ramadan_days) > 0:
            st.warning(f"""
            **🌙 Ramadan Period:** {len(ramadan_days)} forecast days fall within Ramadan.
            Donor turnout typically decreases during fasting. Consider evening drives
            or post-Iftar collection sessions.
            """)
        else:
            st.success("**🌙 No Ramadan days** fall within the 30-day forecast window.")

st.markdown("---")

# ---- FORECAST DETAIL TABLE ----
st.subheader("📋 Forecast Detail Table")
st.caption("The full day-by-day forecast. You can download this on the Download Center page.")

table = filtered[["Date", "Blood_Type", "Predicted_Donations", "Day_of_Week", "Is_Holiday", "Is_Ramadan"]].copy()
table["Date"] = table["Date"].dt.strftime("%Y-%m-%d")
table = table.sort_values(["Date", "Blood_Type"]).reset_index(drop=True)
table.index = table.index + 1

# Replace 0/1 with clear symbols
table["Is_Holiday"] = table["Is_Holiday"].map({1: "Yes", 0: "—"})
table["Is_Ramadan"] = table["Is_Ramadan"].map({1: "Yes", 0: "—"})

table.columns = ["Date", "Blood Type", "Predicted Bags", "Day", "Holiday", "Ramadan"]

# Use column_config for proper formatting and alignment
st.dataframe(
    table,
    use_container_width=True,
    height=400,
    column_config={
        "Date": st.column_config.TextColumn("Date", width="medium"),
        "Blood Type": st.column_config.TextColumn("Blood Type", width="small"),
        "Predicted Bags": st.column_config.NumberColumn("Predicted Bags", format="%d"),
        "Day": st.column_config.TextColumn("Day", width="medium"),
        "Holiday": st.column_config.TextColumn("Holiday", width="small"),
        "Ramadan": st.column_config.TextColumn("Ramadan", width="small"),
    }
)
