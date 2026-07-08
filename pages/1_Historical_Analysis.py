# ============================================================
# pages/1_Historical_Analysis.py — THE "PAST" PAGE
# ============================================================
# The number "1_" at the start controls the order in the sidebar.
# The emoji shows up as the page icon. Streamlit reads this
# automatically — no manual menu setup needed.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Historical Analysis", page_icon="📊", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("blood_donation_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Keep only historical rows on this page
hist = df[df["Data_Type"] == "Historical"].copy()

# ---- PAGE TITLE ----
st.title("📊 Historical Analysis")
st.markdown("Reviewing how accurately the model predicted **past** blood donations.")
st.markdown("---")

# ---- SIDEBAR FILTERS ----
# Anything inside st.sidebar appears in the left menu.
st.sidebar.header("🔍 Filters")

# Blood type filter — multiselect lets users pick one or many
blood_types = st.sidebar.multiselect(
    "Select Blood Type(s):",
    options=sorted(hist["Blood_Type"].unique()),
    default=sorted(hist["Blood_Type"].unique())
)

# Date range filter — a slider between the earliest and latest date
min_date = hist["Date"].min().date()
max_date = hist["Date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(max_date.replace(year=max_date.year - 1), max_date),  # default: last 1 year
    min_value=min_date,
    max_value=max_date
)

# ---- APPLY FILTERS ----
filtered = hist[hist["Blood_Type"].isin(blood_types)]
if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["Date"].dt.date >= start) &
        (filtered["Date"].dt.date <= end)
    ]

# ---- KPI ROW ----
k1, k2, k3 = st.columns(3)
total_actual = int(filtered["Actual_Donations"].sum())
avg_daily = filtered.groupby("Date")["Actual_Donations"].sum().mean()
mae = abs(filtered["Actual_Donations"] - filtered["Predicted_Donations"]).mean()

k1.metric("Total Actual Donations", f"{total_actual:,} bags")
k2.metric("Average Daily Donations", f"{avg_daily:,.0f} bags")
k3.metric("Average Prediction Error", f"{mae:,.1f} bags")

st.markdown("---")

# ---- CHART 1: ACTUAL vs PREDICTED LINE CHART ----
st.subheader("Actual vs Predicted Donations Over Time")
st.caption("Blue = what really happened · Red dashed = what the model predicted. "
           "The closer the lines, the more accurate the model.")

# Group by date so all blood types are summed per day (cleaner line)
daily = filtered.groupby("Date").agg(
    Actual=("Actual_Donations", "sum"),
    Predicted=("Predicted_Donations", "sum")
).reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily["Date"], y=daily["Actual"],
    name="Actual Donations", line=dict(color="#2C3E50", width=2)
))
fig1.add_trace(go.Scatter(
    x=daily["Date"], y=daily["Predicted"],
    name="Predicted Donations", line=dict(color="#C0392B", width=2, dash="dash")
))
fig1.update_layout(
    height=420, hovermode="x unified",
    xaxis_title="Date", yaxis_title="Blood Bags",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ---- CHART 2 & 3 side by side ----
c1, c2 = st.columns(2)

with c1:
    st.subheader("Average Donations by Day of Week")
    st.caption("Shows the weekly cycle the model learned.")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # average per day: first sum per date, then average by weekday
    daily_dow = filtered.groupby(["Date", "Day_of_Week"])["Actual_Donations"].sum().reset_index()
    dow_avg = daily_dow.groupby("Day_of_Week")["Actual_Donations"].mean().reindex(dow_order).reset_index()
    # Colour weekdays navy, weekends red — instantly shows the weekend spike
    dow_avg["Type"] = dow_avg["Day_of_Week"].apply(
        lambda d: "Weekend" if d in ["Saturday", "Sunday"] else "Weekday"
    )
    fig2 = px.bar(
        dow_avg, x="Day_of_Week", y="Actual_Donations",
        color="Type", color_discrete_map={"Weekday": "#2C3E50", "Weekend": "#C0392B"},
        labels={"Actual_Donations": "Avg Bags", "Day_of_Week": "Day"}
    )
    fig2.update_layout(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    st.subheader("Donations by Blood Type")
    st.caption("Total actual donations collected per blood type.")
    bt_total = filtered.groupby("Blood_Type")["Actual_Donations"].sum().reset_index()
    bt_colors = {"A": "#C0392B", "B": "#2C3E50", "AB": "#E67E22", "O": "#27AE60"}
    fig3 = px.pie(
        bt_total, names="Blood_Type", values="Actual_Donations",
        hole=0.45, color="Blood_Type", color_discrete_map=bt_colors
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---- ACTIONABLE INSIGHTS ----
st.subheader("💡 Key Insights from Historical Data")

i1, i2 = st.columns(2)

with i1:
    # Weekend vs weekday insight
    daily_all = filtered.groupby(["Date", "Day_of_Week"])["Actual_Donations"].sum().reset_index()
    daily_all["Is_Weekend"] = daily_all["Day_of_Week"].isin(["Saturday", "Sunday"])
    wknd_avg = daily_all[daily_all["Is_Weekend"]]["Actual_Donations"].mean()
    wkdy_avg = daily_all[~daily_all["Is_Weekend"]]["Actual_Donations"].mean()
    if wkdy_avg > 0:
        diff = ((wknd_avg - wkdy_avg) / wkdy_avg) * 100
        st.info(f"""
        **📆 Weekend Effect:** Weekends average **{wknd_avg:,.0f}** bags/day
        vs **{wkdy_avg:,.0f}** on weekdays — a **{abs(diff):.1f}%**
        {"increase" if diff > 0 else "decrease"}. This weekly cycle is the model's
        strongest learned feature.
        """)

with i2:
    # Busiest vs quietest blood type
    bt_avgs = filtered.groupby("Blood_Type")["Actual_Donations"].mean()
    if len(bt_avgs) > 1:
        top_bt = bt_avgs.idxmax()
        low_bt = bt_avgs.idxmin()
        st.info(f"""
        **🩸 Blood Type Pattern:** Type **{top_bt}** has the highest average daily
        donations ({bt_avgs[top_bt]:,.0f} bags) while Type **{low_bt}** has the
        lowest ({bt_avgs[low_bt]:,.0f} bags). Procurement campaigns should
        prioritise Type {low_bt} donors.
        """)

st.caption("💡 Use the filters in the left sidebar to focus on specific "
           "blood types or date ranges. All charts update automatically.")
# ============================================================
# pages/1_Historical_Analysis.py — THE "PAST" PAGE
# ============================================================
# The number "1_" at the start controls the order in the sidebar.
# The emoji shows up as the page icon. Streamlit reads this
# automatically — no manual menu setup needed.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Historical Analysis", page_icon="📊", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("blood_donation_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Keep only historical rows on this page
hist = df[df["Data_Type"] == "Historical"].copy()

# ---- PAGE TITLE ----
st.title("📊 Historical Analysis")
st.markdown("Reviewing how accurately the model predicted **past** blood donations.")
st.markdown("---")

# ---- SIDEBAR FILTERS ----
# Anything inside st.sidebar appears in the left menu.
st.sidebar.header("🔍 Filters")

# Blood type filter — multiselect lets users pick one or many
blood_types = st.sidebar.multiselect(
    "Select Blood Type(s):",
    options=sorted(hist["Blood_Type"].unique()),
    default=sorted(hist["Blood_Type"].unique())
)

# Date range filter — a slider between the earliest and latest date
min_date = hist["Date"].min().date()
max_date = hist["Date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(max_date.replace(year=max_date.year - 1), max_date),  # default: last 1 year
    min_value=min_date,
    max_value=max_date
)

# ---- APPLY FILTERS ----
filtered = hist[hist["Blood_Type"].isin(blood_types)]
if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["Date"].dt.date >= start) &
        (filtered["Date"].dt.date <= end)
    ]

# ---- KPI ROW ----
k1, k2, k3 = st.columns(3)
total_actual = int(filtered["Actual_Donations"].sum())
avg_daily = filtered.groupby("Date")["Actual_Donations"].sum().mean()
mae = abs(filtered["Actual_Donations"] - filtered["Predicted_Donations"]).mean()

k1.metric("Total Actual Donations", f"{total_actual:,} bags")
k2.metric("Average Daily Donations", f"{avg_daily:,.0f} bags")
k3.metric("Average Prediction Error", f"{mae:,.1f} bags")

st.markdown("---")

# ---- CHART 1: ACTUAL vs PREDICTED LINE CHART ----
st.subheader("Actual vs Predicted Donations Over Time")
st.caption("Blue = what really happened · Red dashed = what the model predicted. "
           "The closer the lines, the more accurate the model.")

# Group by date so all blood types are summed per day (cleaner line)
daily = filtered.groupby("Date").agg(
    Actual=("Actual_Donations", "sum"),
    Predicted=("Predicted_Donations", "sum")
).reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily["Date"], y=daily["Actual"],
    name="Actual Donations", line=dict(color="#2C3E50", width=2)
))
fig1.add_trace(go.Scatter(
    x=daily["Date"], y=daily["Predicted"],
    name="Predicted Donations", line=dict(color="#C0392B", width=2, dash="dash")
))
fig1.update_layout(
    height=420, hovermode="x unified",
    xaxis_title="Date", yaxis_title="Blood Bags",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ---- CHART 2 & 3 side by side ----
c1, c2 = st.columns(2)

with c1:
    st.subheader("Average Donations by Day of Week")
    st.caption("Shows the weekly cycle the model learned.")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # average per day: first sum per date, then average by weekday
    daily_dow = filtered.groupby(["Date", "Day_of_Week"])["Actual_Donations"].sum().reset_index()
    dow_avg = daily_dow.groupby("Day_of_Week")["Actual_Donations"].mean().reindex(dow_order).reset_index()
    # Colour weekdays navy, weekends red — instantly shows the weekend spike
    dow_avg["Type"] = dow_avg["Day_of_Week"].apply(
        lambda d: "Weekend" if d in ["Saturday", "Sunday"] else "Weekday"
    )
    fig2 = px.bar(
        dow_avg, x="Day_of_Week", y="Actual_Donations",
        color="Type", color_discrete_map={"Weekday": "#2C3E50", "Weekend": "#C0392B"},
        labels={"Actual_Donations": "Avg Bags", "Day_of_Week": "Day"}
    )
    fig2.update_layout(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    st.subheader("Donations by Blood Type")
    st.caption("Total actual donations collected per blood type.")
    bt_total = filtered.groupby("Blood_Type")["Actual_Donations"].sum().reset_index()
    bt_colors = {"A": "#C0392B", "B": "#2C3E50", "AB": "#E67E22", "O": "#27AE60"}
    fig3 = px.pie(
        bt_total, names="Blood_Type", values="Actual_Donations",
        hole=0.45, color="Blood_Type", color_discrete_map=bt_colors
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---- ACTIONABLE INSIGHTS ----
st.subheader("💡 Key Insights from Historical Data")

i1, i2 = st.columns(2)

with i1:
    # Weekend vs weekday insight
    daily_all = filtered.groupby(["Date", "Day_of_Week"])["Actual_Donations"].sum().reset_index()
    daily_all["Is_Weekend"] = daily_all["Day_of_Week"].isin(["Saturday", "Sunday"])
    wknd_avg = daily_all[daily_all["Is_Weekend"]]["Actual_Donations"].mean()
    wkdy_avg = daily_all[~daily_all["Is_Weekend"]]["Actual_Donations"].mean()
    if wkdy_avg > 0:
        diff = ((wknd_avg - wkdy_avg) / wkdy_avg) * 100
        st.info(f"""
        **📆 Weekend Effect:** Weekends average **{wknd_avg:,.0f}** bags/day
        vs **{wkdy_avg:,.0f}** on weekdays — a **{abs(diff):.1f}%**
        {"increase" if diff > 0 else "decrease"}. This weekly cycle is the model's
        strongest learned feature.
        """)

with i2:
    # Busiest vs quietest blood type
    bt_avgs = filtered.groupby("Blood_Type")["Actual_Donations"].mean()
    if len(bt_avgs) > 1:
        top_bt = bt_avgs.idxmax()
        low_bt = bt_avgs.idxmin()
        st.info(f"""
        **🩸 Blood Type Pattern:** Type **{top_bt}** has the highest average daily
        donations ({bt_avgs[top_bt]:,.0f} bags) while Type **{low_bt}** has the
        lowest ({bt_avgs[low_bt]:,.0f} bags). Procurement campaigns should
        prioritise Type {low_bt} donors.
        """)

st.caption("💡 Use the filters in the left sidebar to focus on specific "
           "blood types or date ranges. All charts update automatically.")
