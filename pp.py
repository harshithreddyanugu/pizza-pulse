# Pizza Sales Dashboard App using Streamlit
# Step-by-step app based on Tableau analysis logic

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Step 1: Define the Scope and Objective
st.title("🍕 PizzaPulse - Sales Revenue Analysis Dashboard")
st.write("Analyze pizza sales data to identify trends, best-selling items, and peak periods.")

# Step 2: Load Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("pizza_sales.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_time"] = pd.to_datetime(df["order_time"], format="%H:%M:%S").dt.time
    return df

# Load data
pizza_df = load_data()

# Step 3: Data Preparation
pizza_df["hour"] = pd.to_datetime(pizza_df["order_time"], format="%H:%M:%S").dt.hour
pizza_df["weekday"] = pizza_df["order_date"].dt.day_name()

# KPIs
total_revenue = pizza_df["total_price"].sum()
total_orders = pizza_df["order_id"].nunique()
total_pizzas = pizza_df["quantity"].sum()
avg_order_value = total_revenue / total_orders
avg_pizzas_per_order = total_pizzas / total_orders
seat_util = min(100, round((total_orders * 3) / (60 * total_orders) * 100, 2))

# Display KPIs
st.markdown("### 📊 Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Avg. Order Value", f"${avg_order_value:.2f}")
kpi3.metric("Total Orders", total_orders)

kpi4, kpi5 = st.columns(2)
kpi4.metric("Total Pizzas Sold", total_pizzas)
kpi5.metric("Seat Utilization", f"{seat_util}%")

# Step 4: Visualizations
st.markdown("---")
st.header("📈 Sales Trends")

# Revenue Over Time
revenue_daily = pizza_df.groupby("order_date")["total_price"].sum().reset_index()
line_chart = alt.Chart(revenue_daily).mark_line().encode(
    x="order_date:T",
    y="total_price:Q"
).properties(title="Total Revenue Over Time")
st.altair_chart(line_chart, use_container_width=True)

# Revenue by Item
revenue_by_item = pizza_df.groupby("pizza_name")["total_price"].sum().sort_values(ascending=False).head(10).reset_index()
bar_chart = alt.Chart(revenue_by_item).mark_bar().encode(
    x=alt.X("total_price:Q", title="Revenue"),
    y=alt.Y("pizza_name:N", sort='-x', title="Pizza")
).properties(title="Top 10 Pizzas by Revenue")
st.altair_chart(bar_chart, use_container_width=True)

# Revenue by Day of Week
revenue_by_day = pizza_df.groupby("weekday")["total_price"].sum().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]).reset_index()
st.bar_chart(revenue_by_day.set_index("weekday"), use_container_width=True)

# Revenue by Hour of Day
revenue_by_hour = pizza_df.groupby("hour")["total_price"].sum().reset_index()
st.line_chart(revenue_by_hour.set_index("hour"), use_container_width=True)

# Best and Worst Selling Pizzas
st.markdown("---")
st.header("🏆 Best & ❌ Worst Selling Pizzas")

best_pizzas = pizza_df.groupby("pizza_name")["total_price"].sum().nlargest(5).reset_index()
worst_pizzas = pizza_df.groupby("pizza_name")["total_price"].sum().nsmallest(5).reset_index()

col1, col2 = st.columns(2)
col1.subheader("Top 5 Best Sellers")
col1.dataframe(best_pizzas)
col2.subheader("Bottom 5 Worst Sellers")
col2.dataframe(worst_pizzas)

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data from Maven Pizza Challenge")

 
   
