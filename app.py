import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Database Connection
@st.cache_resource
def get_engine():
    db_path = Path(__file__).parent / 'ecommerce.db'
    return create_engine(f'sqlite:///{db_path}')

engine = get_engine()

# Query Functions
@st.cache_data
def load_data(query):
    """Load data from SQLite database"""
    return pd.read_sql(query, engine)

def get_kpis():
    """Get key performance indicators"""
    query = """
    SELECT 
        COUNT(DISTINCT order_id) as total_orders,
        COUNT(DISTINCT user_id) as total_customers,
        ROUND(SUM(item_total), 2) as total_revenue,
        ROUND(SUM(item_total) / COUNT(DISTINCT order_id), 2) as avg_order_value
    FROM fact_order_items
    """
    return load_data(query)

def get_monthly_revenue():
    """Get monthly revenue trend"""
    query = """
    SELECT
        DATE(order_date) as date,
        ROUND(SUM(item_total), 2) as revenue,
        strftime('%Y-%m', order_date) as year_month
    FROM fact_order_items foi
    JOIN fact_orders fo ON foi.order_id = fo.order_id
    GROUP BY strftime('%Y-%m', order_date)
    ORDER BY year_month
    """
    return load_data(query)

def get_top_products(limit=10):
    """Get top products by revenue"""
    query = f"""
    SELECT 
        dp.product_name,
        dp.product_id,
        dp.category,
        ROUND(SUM(foi.item_total), 2) as revenue,
        SUM(foi.quantity) as units_sold
    FROM fact_order_items foi
    JOIN dim_products dp ON foi.product_id = dp.product_id
    GROUP BY foi.product_id, dp.product_name, dp.category
    ORDER BY revenue DESC
    LIMIT {limit}
    """
    return load_data(query)

def get_conversion_funnel():
    """Get conversion funnel data"""
    query = """
    SELECT 
        'Views' as stage,
        COUNT(DISTINCT CASE WHEN event_type = 'view' THEN event_id END) as count
    FROM fact_events
    UNION ALL
    SELECT 
        'Add to Cart' as stage,
        COUNT(DISTINCT CASE WHEN event_type IN ('cart', 'add_to_cart') THEN event_id END) as count
    FROM fact_events
    UNION ALL
    SELECT 
        'Purchases' as stage,
        COUNT(DISTINCT order_id) as count
    FROM fact_order_items
    """
    return load_data(query)

def get_category_revenue():
    """Get revenue by product category"""
    query = """
    SELECT 
        dp.category,
        ROUND(SUM(foi.item_total), 2) as revenue,
        COUNT(DISTINCT foi.order_id) as orders,
        SUM(foi.quantity) as units
    FROM fact_order_items foi
    JOIN dim_products dp ON foi.product_id = dp.product_id
    GROUP BY dp.category
    ORDER BY revenue DESC
    """
    return load_data(query)

def get_customer_metrics():
    """Get customer-related metrics"""
    query = """
    SELECT
        du.user_id,
        du.name,
        du.city,
        COUNT(DISTINCT foi.order_id) as orders,
        ROUND(SUM(foi.item_total), 2) as total_spent,
        ROUND(SUM(foi.item_total) / COUNT(DISTINCT foi.order_id), 2) as avg_order_value
    FROM dim_users du
    LEFT JOIN fact_order_items foi ON du.user_id = foi.user_id
    GROUP BY du.user_id, du.name, du.city
    ORDER BY total_spent DESC
    """
    return load_data(query)

def get_revenue_by_brand():
    """Get revenue by brand"""
    query = """
    SELECT 
        dp.brand,
        ROUND(SUM(foi.item_total), 2) as revenue,
        COUNT(DISTINCT foi.order_id) as orders
    FROM fact_order_items foi
    JOIN dim_products dp ON foi.product_id = dp.product_id
    GROUP BY dp.brand
    ORDER BY revenue DESC
    LIMIT 10
    """
    return load_data(query)

def get_product_ratings():
    """Get product ratings distribution"""
    query = """
    SELECT 
        ROUND(dp.rating, 1) as rating,
        COUNT(DISTINCT dp.product_id) as count
    FROM dim_products dp
    GROUP BY ROUND(dp.rating, 1)
    ORDER BY rating
    """
    return load_data(query)

# Sidebar Navigation
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio(
    "Select a page:",
    ["Overview", "Revenue Trends", "Products", "Funnel Analysis", "Customers", "Reports"]
)

# Main Content
if page == "Overview":
    st.title("📊 Ecommerce Analytics Dashboard - Overview")
    st.markdown("---")
    
    # Load KPIs
    kpis = get_kpis()
    
    if not kpis.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"${kpis['total_revenue'].values[0]:,.2f}")
        
        with col2:
            st.metric("Total Orders", f"{int(kpis['total_orders'].values[0]):,}")
        
        with col3:
            st.metric("Avg Order Value", f"${kpis['avg_order_value'].values[0]:,.2f}")
        
        with col4:
            st.metric("Total Customers", f"{int(kpis['total_customers'].values[0]):,}")
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue by Category")
        category_data = get_category_revenue()
        if not category_data.empty:
            fig = px.pie(
                category_data,
                values='revenue',
                names='category',
                title='Revenue Distribution by Category'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Product Ratings Distribution")
        ratings = get_product_ratings()
        if not ratings.empty:
            fig = px.bar(
                ratings,
                x='rating',
                y='count',
                title='Product Ratings Distribution',
                labels={'rating': 'Rating', 'count': 'Number of Products'}
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Revenue Trends":
    st.title("💰 Revenue Trends Analysis")
    st.markdown("---")
    
    monthly_revenue = get_monthly_revenue()
    
    if not monthly_revenue.empty:
        # Monthly Revenue Line Chart
        st.subheader("Monthly Revenue Trend")
        
        # Convert year_month to datetime for proper sorting
        monthly_revenue['year_month'] = pd.to_datetime(monthly_revenue['year_month'])
        monthly_revenue = monthly_revenue.sort_values('year_month')
        
        fig = px.line(
            monthly_revenue,
            x='year_month',
            y='revenue',
            title='Monthly Revenue Trend',
            labels={'year_month': 'Month', 'revenue': 'Revenue ($)'},
            markers=True
        )
        fig.update_traces(line=dict(color='#1f77b4', width=3), marker=dict(size=8))
        fig.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Revenue Statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Revenue", f"${monthly_revenue['revenue'].sum():,.2f}")
        
        with col2:
            st.metric("Avg Monthly Revenue", f"${monthly_revenue['revenue'].mean():,.2f}")
        
        with col3:
            st.metric("Max Monthly Revenue", f"${monthly_revenue['revenue'].max():,.2f}")
        
        # Revenue by Brand
        st.subheader("🏢 Revenue by Brand (Top 10)")
        brand_revenue = get_revenue_by_brand()
        if not brand_revenue.empty:
            fig = px.bar(
                brand_revenue,
                x='revenue',
                y='brand',
                orientation='h',
                title='Top 10 Brands by Revenue',
                labels={'revenue': 'Revenue ($)', 'brand': 'Brand'},
                color='revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Products":
    st.title("🛍️ Product Analysis")
    st.markdown("---")
    
    # Top Products
    st.subheader("Top 10 Products by Revenue")
    top_products = get_top_products(10)
    
    if not top_products.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_products,
                x='revenue',
                y='product_name',
                orientation='h',
                title='Top 10 Products by Revenue',
                labels={'revenue': 'Revenue ($)', 'product_name': 'Product'},
                color='revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Product Details")
            st.dataframe(top_products.head(5), use_container_width=True)
    
    # Products Table
    st.subheader("All Products Performance")
    all_products = get_top_products(100)
    if not all_products.empty:
        st.dataframe(all_products, use_container_width=True)

elif page == "Funnel Analysis":
    st.title("📊 Conversion Funnel Analysis")
    st.markdown("---")
    
    funnel_data = get_conversion_funnel()
    
    if not funnel_data.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Funnel Chart
            fig = go.Figure(go.Funnel(
                y=funnel_data['stage'],
                x=funnel_data['count'],
                textposition='inside',
                textinfo='value+percent initial',
                marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ))
            fig.update_layout(
                title='Conversion Funnel',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Conversion Rates")
            
            # Calculate conversion rates
            if len(funnel_data) >= 3:
                views = funnel_data[funnel_data['stage'] == 'Views']['count'].values[0]
                carts = funnel_data[funnel_data['stage'] == 'Add to Cart']['count'].values[0]
                purchases = funnel_data[funnel_data['stage'] == 'Purchases']['count'].values[0]
                
                view_to_cart = (carts / views * 100) if views > 0 else 0
                cart_to_purchase = (purchases / carts * 100) if carts > 0 else 0
                overall_conversion = (purchases / views * 100) if views > 0 else 0
                
                st.metric("View to Cart Rate", f"{view_to_cart:.2f}%")
                st.metric("Cart to Purchase Rate", f"{cart_to_purchase:.2f}%")
                st.metric("Overall Conversion Rate", f"{overall_conversion:.2f}%")

elif page == "Customers":
    st.title("👥 Customer Analysis")
    st.markdown("---")
    
    customer_data = get_customer_metrics()
    
    if not customer_data.empty:
        # Remove rows with NULL values for analysis
        customer_data_clean = customer_data[customer_data['total_spent'].notna()].copy()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Customers", f"{len(customer_data):,}")
        
        with col2:
            avg_spent = customer_data_clean['total_spent'].mean()
            st.metric("Avg Customer Lifetime Value", f"${avg_spent:,.2f}")
        
        with col3:
            avg_orders = customer_data_clean[customer_data_clean['orders'] > 0]['orders'].mean()
            st.metric("Avg Orders per Customer", f"{avg_orders:.2f}")
        
        # Customer Distribution
        st.subheader("Customer Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Customers by Spending")
            top_customers = customer_data_clean.nlargest(10, 'total_spent')[['name', 'city', 'orders', 'total_spent']]
            st.dataframe(top_customers, use_container_width=True)
        
        with col2:
            st.subheader("Top Cities by Customer Count")
            city_counts = customer_data_clean['city'].value_counts().head(10)
            fig = px.bar(
                x=city_counts.values,
                y=city_counts.index,
                orientation='h',
                title='Top 10 Cities by Customer Count',
                labels={'x': 'Number of Customers', 'y': 'City'}
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "Reports":
    st.title("📋 Detailed Reports")
    st.markdown("---")
    
    report_type = st.selectbox(
        "Select Report Type:",
        ["Summary Report", "Revenue Report", "Product Report", "Customer Report"]
    )
    
    if report_type == "Summary Report":
        st.subheader("Business Summary Report")
        kpis = get_kpis()
        
        if not kpis.empty:
            st.markdown(f"""
            ### Key Metrics Summary
            
            - **Total Revenue:** ${kpis['total_revenue'].values[0]:,.2f}
            - **Total Orders:** {int(kpis['total_orders'].values[0]):,}
            - **Average Order Value:** ${kpis['avg_order_value'].values[0]:,.2f}
            - **Total Customers:** {int(kpis['total_customers'].values[0]):,}
            - **Customer Acquisition Cost:** ${kpis['total_revenue'].values[0] / int(kpis['total_customers'].values[0]):,.2f}
            """)
    
    elif report_type == "Revenue Report":
        st.subheader("Revenue Analysis Report")
        monthly_revenue = get_monthly_revenue()
        
        if not monthly_revenue.empty:
            st.markdown(f"""
            ### Revenue Metrics
            
            - **Total Revenue:** ${monthly_revenue['revenue'].sum():,.2f}
            - **Average Monthly Revenue:** ${monthly_revenue['revenue'].mean():,.2f}
            - **Highest Month:** ${monthly_revenue['revenue'].max():,.2f}
            - **Lowest Month:** ${monthly_revenue['revenue'].min():,.2f}
            - **Growth Trend:** {('📈 Positive' if monthly_revenue['revenue'].iloc[-1] > monthly_revenue['revenue'].iloc[0] else '📉 Negative')}
            """)
            
            st.dataframe(monthly_revenue, use_container_width=True)
    
    elif report_type == "Product Report":
        st.subheader("Product Performance Report")
        products = get_top_products(50)
        
        if not products.empty:
            st.markdown(f"""
            ### Product Insights
            
            - **Total Products:** {len(products)}
            - **Top Product:** {products.iloc[0]['product_name']} (${products.iloc[0]['revenue']:,.2f})
            - **Average Product Revenue:** ${products['revenue'].mean():,.2f}
            - **Best Category:** {products.iloc[0]['category']}
            """)
            
            st.dataframe(products, use_container_width=True)
    
    elif report_type == "Customer Report":
        st.subheader("Customer Insights Report")
        customers = get_customer_metrics()
        
        if not customers.empty:
            customers_clean = customers[customers['total_spent'].notna()]
            
            st.markdown(f"""
            ### Customer Metrics
            
            - **Total Customers:** {len(customers):,}
            - **Active Customers:** {len(customers_clean):,}
            - **Average Customer Value:** ${customers_clean['total_spent'].mean():,.2f}
            - **Top Customer:** {customers_clean.iloc[0]['name']} (${customers_clean.iloc[0]['total_spent']:,.2f})
            - **Average Orders per Customer:** {customers_clean[customers_clean['orders'] > 0]['orders'].mean():.2f}
            """)
            
            st.dataframe(customers_clean.head(50), use_container_width=True)
