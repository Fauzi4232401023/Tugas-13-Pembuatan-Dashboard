import pandas as pd
import streamlit as st
import plotly.express as px
from babel.numbers import format_currency

# =========================
# FUNCTION
# =========================
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()

    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_sum_order_items_df(df):
    return (
        df.groupby("product_name")
        .quantity_x.sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def create_bygender_df(df):
    return (
        df.groupby("gender")
        .customer_id.nunique()
        .reset_index(name="customer_count")
    )


def create_byage_df(df):
    byage_df = (
        df.groupby("age_group")
        .customer_id.nunique()
        .reset_index(name="customer_count")
    )
    byage_df["age_group"] = pd.Categorical(
        byage_df["age_group"], ["Youth", "Adults", "Seniors"]
    )
    return byage_df


def create_bystate_df(df):
    return (
        df.groupby("state")
        .customer_id.nunique()
        .reset_index(name="customer_count")
    )


def create_rfm_df(df):
    rfm_df = df.groupby("customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date

    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df


# =========================
# LOAD DATA
# =========================
all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_date", "delivery_date"]
for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(drop=True, inplace=True)

min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/mhvvn/dashboard_streamlit/refs/heads/main/img/tshirt.png",
        width=80
    )

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# =========================
# FILTER DATA
# =========================
main_df = all_df[
    (all_df["order_date"] >= pd.to_datetime(start_date)) &
    (all_df["order_date"] <= pd.to_datetime(end_date))
]

# =========================
# PREPARE DATAFRAME
# =========================
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# =========================
# DASHBOARD
# =========================
st.header("My Collection Dashboard ✨")

st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Orders", daily_orders_df.order_count.sum())

with col2:
    st.metric(
        "Total Revenue",
        format_currency(daily_orders_df.revenue.sum(), "AUD", locale="es_CO")
    )

# =========================
# DAILY ORDERS CHART
# =========================
fig = px.line(
    daily_orders_df,
    x="order_date",
    y="order_count",
    markers=True,
    title="Daily Orders"
)
fig.update_layout(xaxis_title=None, yaxis_title=None)
st.plotly_chart(fig, use_container_width=True)

# =========================
# BEST & WORST PRODUCT
# =========================
st.subheader("Best & Worst Performing Product")

best_product = sum_order_items_df.head(5)
worst_product = sum_order_items_df.sort_values("quantity_x").head(5)

fig = px.bar(
    best_product,
    x="quantity_x",
    y="product_name",
    orientation="h",
    title="Best Performing Product"
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    worst_product,
    x="quantity_x",
    y="product_name",
    orientation="h",
    title="Worst Performing Product"
)
st.plotly_chart(fig, use_container_width=True)

# =========================
# CUSTOMER DEMOGRAPHICS
# =========================
st.subheader("Customer Demographics")

fig = px.bar(
    bygender_df.sort_values("customer_count", ascending=False),
    x="gender",
    y="customer_count",
    title="Number of Customer by Gender"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    byage_df,
    x="age_group",
    y="customer_count",
    title="Number of Customer by Age"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    bystate_df.sort_values("customer_count", ascending=False),
    x="customer_count",_
