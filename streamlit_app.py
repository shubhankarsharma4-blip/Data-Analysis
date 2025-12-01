import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime, timedelta
import os

# Initialize database if it doesn't exist
def initialize_database():
    """Initialize database from processed CSV files"""
    db_path = Path(__file__).parent / 'ecommerce.db'
    processed_dir = Path(__file__).parent / 'Data' / 'Processed'
    
    try:
        # Check if database already has tables
        from sqlalchemy import create_engine, inspect
        engine = create_engine(f'sqlite:///{db_path}')
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # If all required tables exist, we're good
        required_tables = ['dim_products', 'dim_users', 'fact_orders', 'fact_order_items', 'fact_reviews']
        if all(table in existing_tables for table in required_tables):
            return True
        
        # Otherwise, initialize from CSV
        st.warning("⚙️ Initializing database from processed data files...")
        
        # List of expected processed tables
        tables = [
            'dim_products',
            'dim_users', 
            'fact_orders',
            'fact_order_items',
            'fact_reviews',
            'fact_events'
        ]
        
        # Load each CSV file into the database
        for table_name in tables:
            csv_file = processed_dir / f'{table_name}.csv'
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        st.success("✅ Database initialized successfully from processed data!")
        return True
        
    except Exception as e:
        st.error(f"❌ Error initializing database: {str(e)}")
        st.info("Trying to load from CSV files directly...")
        return False

# Page Configuration
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if not initialize_database():
    st.stop()

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
@st.cache_data(ttl=3600)
def load_data(query):
    """Load data from SQLite database"""
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Database query error: {e}")
        return pd.DataFrame()

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
    result = load_data(query)
    return result.iloc[0].to_dict()

def get_revenue_by_month():
    """Get monthly revenue trend"""
    query = """
    SELECT 
        strftime('%Y-%m', o.order_date) as month,
        ROUND(SUM(foi.item_total), 2) as revenue
    FROM fact_order_items foi
    JOIN fact_orders o ON foi.order_id = o.order_id
    GROUP BY strftime('%Y-%m', o.order_date)
    ORDER BY month
    """
    return load_data(query)

def get_top_products():
    """Get top 10 products by revenue"""
    query = """
    SELECT 
        p.product_name,
        COUNT(*) as quantity_sold,
        ROUND(SUM(foi.item_total), 2) as total_revenue
    FROM fact_order_items foi
    JOIN dim_products p ON foi.product_id = p.product_id
    GROUP BY foi.product_id, p.product_name
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    return load_data(query)

def get_customer_metrics():
    """Get customer-related metrics"""
    query = """
    SELECT 
        COUNT(DISTINCT user_id) as total_customers,
        ROUND(AVG(order_count), 2) as avg_orders_per_customer,
        ROUND(AVG(total_spent), 2) as avg_spend_per_customer
    FROM (
        SELECT 
            user_id,
            COUNT(*) as order_count,
            SUM(item_total) as total_spent
        FROM fact_order_items
        GROUP BY user_id
    )
    """
    result = load_data(query)
    return result.iloc[0].to_dict()

def get_product_reviews():
    """Get product ratings"""
    query = """
    SELECT 
        p.product_name,
        ROUND(AVG(CAST(fr.rating as float)), 2) as avg_rating,
        COUNT(*) as review_count
    FROM fact_reviews fr
    JOIN dim_products p ON fr.product_id = p.product_id
    GROUP BY fr.product_id, p.product_name
    ORDER BY avg_rating DESC, review_count DESC
    LIMIT 10
    """
    return load_data(query)

# Main App
st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("Real-time insights into your e-commerce business performance")

try:
    # KPIs
    st.subheader("Key Performance Indicators")
    kpis = get_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", f"{int(kpis['total_orders']):,}")
    with col2:
        st.metric("Total Customers", f"{int(kpis['total_customers']):,}")
    with col3:
        st.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
    with col4:
        st.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
    
    st.divider()
    
    # Revenue Trend
    st.subheader("Revenue Trend")
    revenue_data = get_revenue_by_month()
    if not revenue_data.empty:
        fig_revenue = px.line(
            revenue_data,
            x='month',
            y='revenue',
            title='Monthly Revenue Trend',
            markers=True,
            line_shape='linear'
        )
        fig_revenue.update_xaxes(title_text='Month')
        fig_revenue.update_yaxes(title_text='Revenue ($)')
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.divider()
    
    # Top Products
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Products by Revenue")
        top_products = get_top_products()
        if not top_products.empty:
            fig_products = px.bar(
                top_products,
                x='total_revenue',
                y='product_name',
                orientation='h',
                title='Top Products',
                labels={'total_revenue': 'Revenue ($)', 'product_name': 'Product'}
            )
            st.plotly_chart(fig_products, use_container_width=True)
    
    with col2:
        st.subheader("Top Rated Products")
        reviews = get_product_reviews()
        if not reviews.empty:
            fig_ratings = px.scatter(
                reviews,
                x='review_count',
                y='avg_rating',
                size='avg_rating',
                hover_name='product_name',
                title='Product Ratings vs Review Count',
                labels={'avg_rating': 'Average Rating', 'review_count': 'Review Count'}
            )
            st.plotly_chart(fig_ratings, use_container_width=True)
    
    st.divider()
    
    # Customer Metrics
    st.subheader("Customer Insights")
    customer_metrics = get_customer_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", f"{int(customer_metrics['total_customers']):,}")
    with col2:
        st.metric("Avg Orders per Customer", f"{customer_metrics['avg_orders_per_customer']:.2f}")
    with col3:
        st.metric("Avg Spend per Customer", f"${customer_metrics['avg_spend_per_customer']:,.2f}")
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    **Dashboard Information:**
    - Data updates automatically from the ETL pipeline
    - All metrics are calculated in real-time
    - Database: SQLite with star-schema design
    """)
    
except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.info("Please ensure the database has been initialized with the ETL pipeline.")
