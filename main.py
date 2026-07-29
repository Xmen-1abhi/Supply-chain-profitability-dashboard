import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="APL Logistics - Profitability Analytics",page_icon="https://cdn-icons-png.flaticon.com/512/8070/8070595.png",layout="wide")
@st.cache_data
def load_data():
    # Load dataset with correct encoding handling
    df = pd.read_csv('APL_Logistics.csv', encoding='latin1')
    # Financial Validation: Ensure key fields are numeric
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    df['Benefit per order'] = pd.to_numeric(df['Benefit per order'], errors='coerce')
    df['Order Item Discount Rate'] = pd.to_numeric(df['Order Item Discount Rate'], errors='coerce')
    df['Order Item Profit Ratio'] = pd.to_numeric(df['Order Item Profit Ratio'], errors='coerce')
    return df
df = load_data()
st.title(":blue[Customer, Product, and Profitability Performance Analysis]",text_alignment="center")
st.subheader(":red[Supply Chain Operations Diagnostics — APL Logistics Suite]")
st.markdown("---")
st.sidebar.header(" Filter Control Panel")
market_options = ["All"] + list(df['Market'].unique())
selected_market = st.sidebar.selectbox("Select Global Market Region", market_options)
segment_options = ["All"] + list(df['Customer Segment'].unique())
selected_segment = st.sidebar.selectbox("Select Customer Segment", segment_options)
# Discount Rate Threshold Slider
discount_threshold = st.sidebar.slider("Discount Rate Upper Limit Warning Threshold (%)", min_value=0, max_value=25, value=10, step=1)

# Apply dynamic filtering based on user input
filtered_df = df.copy()
if selected_market != "All":
    filtered_df = filtered_df[filtered_df['Market'] == selected_market]
if selected_segment != "All":
    filtered_df = filtered_df[filtered_df['Customer Segment'] == selected_segment]

st.header("📈 Key Performance Indicators (KPIs)")
total_revenue = filtered_df['Sales'].sum()
total_profit = filtered_df['Benefit per order'].sum()
overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
with col2:
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
with col3:
    st.metric(label="Overall Profit Margin (%)", value=f"{overall_margin:.2f}%")

st.markdown("---")

tabs = st.tabs([
    "Revenue & Profit Overview", 
    "Customer Contribution", 
    "Product & Category Performance", 
    "Discount Impact Analyzer"])

# --- TAB 1: REVENUE & PROFIT OVERVIEW ---
with tabs[0]:
    st.subheader("Operational Distribution & Risks")
    col_t1_1, col_t1_2 = st.columns(2)
    with col_t1_1:
        st.write("#### Delivery Status Operational Performance")
        status_counts = filtered_df['Delivery Status'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=status_counts.values, y=status_counts.index, palette="viridis", ax=ax)
        ax.set_xlabel("Order Count")
        st.pyplot(fig)
    with col_t1_2:
        st.write("#### Financial Performance Breakdown by Order Region")
        region_perf = filtered_df.groupby('Order Region')[['Sales', 'Benefit per order']].sum().sort_values(by='Sales', ascending=False).head(10)
        st.dataframe(region_perf.style.format("${:,.2f}"))

# --- TAB 2: CUSTOMER CONTRIBUTION ---
with tabs[1]:
    st.subheader("Customer Segment Profiling")
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        st.write("#### Margin & Profit Contribution by Customer Segment")
        seg_perf = filtered_df.groupby('Customer Segment').agg(
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Benefit per order', 'sum')
        )
        seg_perf['Margin (%)'] = (seg_perf['Total_Profit'] / seg_perf['Total_Sales']) * 100
        st.dataframe(seg_perf.style.format({"Total_Sales": "${:,.2f}", "Total_Profit": "${:,.2f}", "Margin (%)": "{:.2f}%"}))
        
    with col_t2_2:
        st.write("#### Top 10 High-Value Most Profitable Customers")
        # Creating a placeholder full name
        filtered_df['Customer Name'] = filtered_df['Customer Fname'].fillna('') + ' ' + filtered_df['Customer Lname'].fillna('')
        top_cust = filtered_df.groupby('Customer Name').agg(
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Benefit per order', 'sum')
        ).sort_values(by='Total_Profit', ascending=False).head(10)
        st.dataframe(top_cust.style.format("${:,.2f}"))

# --- TAB 3: PRODUCT & CATEGORY PERFORMANCE ---
with tabs[2]:
    st.subheader("Product & Category Profitability Metrics")
    
    st.write("#### Performance by Product Category")
    cat_perf = filtered_df.groupby('Category Name').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Benefit per order', 'sum')
    )
    cat_perf['Category Margin (%)'] = (cat_perf['Total_Profit'] / cat_perf['Total_Sales']) * 100
    cat_perf = cat_perf.sort_values(by='Total_Sales', ascending=False)
    st.dataframe(cat_perf.style.format({"Total_Sales": "${:,.2f}", "Total_Profit": "${:,.2f}", "Category Margin (%)": "{:.2f}%"}))
    # Visualizing Category Margins
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=cat_perf.index[:10], y=cat_perf['Category Margin (%)'].iloc[:10], palette="magma", ax=ax)
    plt.xticks(rotation=45, ha='right')
    ax.set_ylabel("Profit Margin (%)")
    st.pyplot(fig)
# --- TAB 4: DISCOUNT IMPACT ANALYZER ---
with tabs[3]:
    st.subheader("Discount Impact Diagnostics")
    st.markdown(f"🚨 **Warning Threshold Diagnostic Set At:** Orders with discount rates > **{discount_threshold}%**")
    # Calculate eroded margins
    high_discount_df = filtered_df[filtered_df['Order Item Discount Rate'] * 100 > discount_threshold]
    normal_discount_df = filtered_df[filtered_df['Order Item Discount Rate'] * 100 <= discount_threshold]
    col_t4_1, col_t4_2 = st.columns(2)
    with col_t4_1:
        st.write("📊 **High Discount Impact Summary**")
        st.metric("Orders Breaching Threshold", f"{len(high_discount_df):,}")
        high_margin = (high_discount_df['Benefit per order'].sum() / high_discount_df['Sales'].sum() * 100) if not high_discount_df.empty else 0
        st.metric("Average Margin in Breached Group", f"{high_margin:.2f}%")
    with col_t4_2:
        st.write("📊 **Safe Discount Baseline Summary**")
        st.metric("Orders Within Threshold Bounds", f"{len(normal_discount_df):,}")
        normal_margin = (normal_discount_df['Benefit per order'].sum() / normal_discount_df['Sales'].sum() * 100) if not normal_discount_df.empty else 0
        st.metric("Average Margin in Safe Group", f"{normal_margin:.2f}%")
    st.write("#### Discount Rate vs. Item Profit Ratio Visualization")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(
        data=filtered_df.sample(min(2000, len(filtered_df))), 
        x='Order Item Discount Rate', 
        y='Order Item Profit Ratio', 
        alpha=0.4, 
        color='teal',
        ax=ax
    )
    ax.set_xlabel("Discount Rate")
    ax.set_ylabel("Profit Ratio")
    st.pyplot(fig)
