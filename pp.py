# PIZZA SALES DASHBOARD (Streamlit Version Inspired by Screenshots)

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Pizza Sales Report", layout="wide")
st.title("🍕 Pizza pulse Dashboard")

# -------------------------------
# LOAD DATA FROM UPLOADED FILE
# -------------------------------
@st.cache_data

def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_time"] = pd.to_datetime(df["order_time"], format="%H:%M:%S").dt.time
    df["hour"] = pd.to_datetime(df["order_time"], format="%H:%M:%S").dt.hour
    df["month"] = df["order_date"].dt.month
    df["year"] = df["order_date"].dt.year
    df["weekday"] = df["order_date"].dt.day_name()
    df["week"] = df["order_date"].dt.isocalendar().week
    df["quarter"] = df["order_date"].dt.quarter
    return df

uploaded_file = st.sidebar.file_uploader("📤 Upload your pizza_sales CSV file", type="csv")
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    st.warning("Please upload a CSV file to begin analysis.")
    st.stop()

# -------------------------------
# TABS: INTERFACES
# -------------------------------
tabs = st.tabs(["Overview", "Trends", "Category & Size", "Best/Worst Pizzas", "Insights", "Yearly Comparison"])

# Shared filters
with st.sidebar:
    st.header("📅 Filters")
    date_range = st.date_input("Select Date Range", [df.order_date.min(), df.order_date.max()])
    pizza_category = st.selectbox("Select Pizza Category", options=["All"] + sorted(df.pizza_category.unique().tolist()))

df_filtered = df.copy()
if pizza_category != "All":
    df_filtered = df_filtered[df_filtered["pizza_category"] == pizza_category]
if len(date_range) == 2:
    df_filtered = df_filtered[(df_filtered["order_date"] >= pd.to_datetime(date_range[0])) &
                              (df_filtered["order_date"] <= pd.to_datetime(date_range[1]))]

# -------------------------------
# TAB 1: OVERVIEW
# -------------------------------
with tabs[0]:
    st.subheader("📊 Key Metrics")
    total_revenue = df_filtered["total_price"].sum()
    total_orders = df_filtered["order_id"].nunique()
    total_pizzas = df_filtered["quantity"].sum()
    avg_order_value = total_revenue / total_orders
    avg_pizzas_per_order = total_pizzas / total_orders

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"${total_revenue:,.1f}K")
    col2.metric("Avg Order Value", f"${avg_order_value:.2f}")
    col3.metric("Total Pizzas Sold", f"{total_pizzas/1000:.2f}K")
    col4.metric("Total Orders", f"{total_orders/1000:.2f}K")
    col5.metric("Avg Pizzas per Order", f"{avg_pizzas_per_order:.2f}")

# -------------------------------
# TAB 2: TRENDS
# -------------------------------
with tabs[1]:
    st.subheader("📈 Sales Trends")
    col6, col7 = st.columns(2)

    hourly = df_filtered.groupby("hour")["quantity"].sum().reset_index()
    hour_chart = alt.Chart(hourly).mark_bar(color="#f39c12").encode(
        x=alt.X("hour:O", title="Hour"),
        y=alt.Y("quantity:Q", title="Total Pizzas Sold")
    ).properties(title="Hourly Trend for Total Pizza Sold")
    col6.altair_chart(hour_chart, use_container_width=True)

    weekly = df_filtered.groupby("week")["order_id"].nunique().reset_index()
    weekly_chart = alt.Chart(weekly).mark_line(color="#2980b9").encode(
        x=alt.X("week:O", title="Week Number"),
        y=alt.Y("order_id:Q", title="Total Orders")
    ).properties(title="Weekly Trend for Total Orders")
    col7.altair_chart(weekly_chart, use_container_width=True)

    monthly = df_filtered.groupby("month")["total_price"].sum().reset_index()
    st.altair_chart(
        alt.Chart(monthly).mark_bar(color="#27ae60").encode(
            x=alt.X("month:O", title="Month"),
            y=alt.Y("total_price:Q", title="Revenue")
        ).properties(title="Monthly Revenue"),
        use_container_width=True
    )

# -------------------------------
# TAB 3: CATEGORY & SIZE ANALYSIS
# -------------------------------
with tabs[2]:
    st.subheader("🧩 Category & Size Performance")
    col8, col9 = st.columns(2)

    category = df_filtered.groupby("pizza_category")["total_price"].sum().reset_index()
    size = df_filtered.groupby("pizza_size")["total_price"].sum().reset_index()

    cat_chart = alt.Chart(category).mark_arc(innerRadius=30).encode(
        theta="total_price", color="pizza_category", tooltip=["pizza_category", "total_price"]
    ).properties(title="Sales Distribution by Pizza Category")

    size_chart = alt.Chart(size).mark_arc(innerRadius=30).encode(
        theta="total_price", color="pizza_size", tooltip=["pizza_size", "total_price"]
    ).properties(title="Sales Distribution by Pizza Size")

    col8.altair_chart(cat_chart, use_container_width=True)
    col9.altair_chart(size_chart, use_container_width=True)

# -------------------------------
# TAB 4: BEST / WORST PERFORMERS
# -------------------------------
with tabs[3]:
    st.subheader("🏆 Best & ❌ Worst Performing Pizzas")
    top5 = df_filtered.groupby("pizza_name")["total_price"].sum().nlargest(5).reset_index()
    bottom5 = df_filtered.groupby("pizza_name")["total_price"].sum().nsmallest(5).reset_index()

    col10, col11 = st.columns(2)
    col10.subheader("Top 5 Pizzas by Revenue")
    col10.bar_chart(top5.set_index("pizza_name"))

    col11.subheader("Bottom 5 Pizzas by Revenue")
    col11.bar_chart(bottom5.set_index("pizza_name"))

# -------------------------------
# TAB 5: TEXTUAL INSIGHTS
# -------------------------------
with tabs[4]:
    st.subheader("🧠 Business Insights")
    st.write("""
    - **Peak Hours**: Between 12 PM–2 PM and 6 PM–7 PM.
    - **Significant Sales Weeks**: Most sales occur during holiday season (especially December).
    - **Classic Category** contributes the most to revenue and orders.
    - **Large Pizza Size** drives the highest revenue.
    - Consider upselling popular pizzas like The Classic Deluxe or Thai Chicken during peak hours.
    """)

# -------------------------------
# TAB 6: YEARLY COMPARISON
# -------------------------------
with tabs[5]:
    st.subheader("📊 Yearly Comparison")
    year_revenue = df.groupby("year")["total_price"].sum().reset_index()
    year_orders = df.groupby("year")["order_id"].nunique().reset_index()

    st.altair_chart(
        alt.Chart(year_revenue).mark_bar(color="#8e44ad").encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("total_price:Q", title="Total Revenue")
        ).properties(title="Year-wise Revenue Comparison"),
        use_container_width=True
    )

    st.altair_chart(
        alt.Chart(year_orders).mark_line(color="#c0392b").encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("order_id:Q", title="Total Orders")
        ).properties(title="Year-wise Orders Comparison"),
        use_container_width=True
    )

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("PizzaPulse • Built with ❤️ using Streamlit | Upload your own data to compare across years")





