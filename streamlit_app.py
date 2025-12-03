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

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f39c12;
    }
    
    /* Page background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3em;
        margin-bottom: 10px;
        text-shadow: none;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    
    /* Section headers */
    h2 {
        color: #2c3e50;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 40px;
        font-size: 1.8em;
    }
    
    /* Metric cards with gradient */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3) !important;
        border-left: 5px solid #f39c12;
    }
    
    [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* Chart container */
    .plotly-graph-div {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 10px;
    }
    
    /* Column separator */
    .column-divider {
        border-right: 2px solid #e0e0e0;
    }
    
    /* Success messages */
    .stAlert {
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Data table */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Divider line */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 40px 0;
    }
    
    /* Footer */
    footer {
        background-color: transparent;
    }
    
    /* Text styling */
    .info-text {
        color: #555;
        font-size: 0.95em;
        line-height: 1.6;
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
st.markdown('<p class="subtitle">Real-time insights into your e-commerce business performance</p>', unsafe_allow_html=True)

try:
    # KPIs Section
    st.markdown("### 📈 Key Performance Indicators", unsafe_allow_html=True)
    kpis = get_kpis()
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.metric(
            label="🛒 Total Orders",
            value=f"{int(kpis['total_orders']):,}",
            delta="Orders processed"
        )
    with col2:
        st.metric(
            label="👥 Total Customers", 
            value=f"{int(kpis['total_customers']):,}",
            delta="Active customers"
        )
    with col3:
        st.metric(
            label="💰 Total Revenue",
            value=f"${kpis['total_revenue']:,.2f}",
            delta="Total earned"
        )
    with col4:
        st.metric(
            label="💵 Avg Order Value",
            value=f"${kpis['avg_order_value']:,.2f}",
            delta="Per order"
        )
    
    st.divider()
    
    # Revenue Trend Section
    st.markdown("### 📊 Revenue Trend", unsafe_allow_html=True)
    revenue_data = get_revenue_by_month()
    if not revenue_data.empty:
        fig_revenue = px.line(
            revenue_data,
            x='month',
            y='revenue',
            title='Monthly Revenue Trend',
            markers=True,
            line_shape='linear',
            template='plotly_white'
        )
        fig_revenue.update_traces(
            line=dict(color='#667eea', width=3),
            marker=dict(size=10, color='#764ba2')
        )
        fig_revenue.update_layout(
            hovermode='x unified',
            plot_bgcolor='rgba(240, 240, 240, 0.5)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(size=12),
            height=400
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.divider()
    
    # Products and Ratings Section
    st.markdown("### 🏆 Products Performance", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### Top 10 Products by Revenue")
        top_products = get_top_products()
        if not top_products.empty:
            fig_products = px.bar(
                top_products,
                x='total_revenue',
                y='product_name',
                orientation='h',
                template='plotly_white',
                color='total_revenue',
                color_continuous_scale='Viridis'
            )
            fig_products.update_layout(
                showlegend=False,
                hovermode='y',
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='rgba(255,255,255,0)',
                height=500,
                xaxis_title="Revenue ($)",
                yaxis_title=""
            )
            st.plotly_chart(fig_products, use_container_width=True)
    
    with col2:
        st.markdown("#### Top Rated Products")
        reviews = get_product_reviews()
        if not reviews.empty:
            fig_ratings = px.scatter(
                reviews,
                x='review_count',
                y='avg_rating',
                size='avg_rating',
                hover_name='product_name',
                template='plotly_white',
                color='avg_rating',
                color_continuous_scale='RdYlGn'
            )
            fig_ratings.update_layout(
                hovermode='closest',
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='rgba(255,255,255,0)',
                height=500,
                xaxis_title="Review Count",
                yaxis_title="Average Rating"
            )
            st.plotly_chart(fig_ratings, use_container_width=True)
    
    st.divider()
    
    # Customer Insights Section
    st.markdown("### 👥 Customer Insights", unsafe_allow_html=True)
    customer_metrics = get_customer_metrics()
    
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.metric(
            label="👫 Total Customers",
            value=f"{int(customer_metrics['total_customers']):,}",
            delta="Active users"
        )
    with col2:
        st.metric(
            label="📦 Avg Orders per Customer",
            value=f"{customer_metrics['avg_orders_per_customer']:.2f}",
            delta="Per user"
        )
    with col3:
        st.metric(
            label="💳 Avg Spend per Customer",
            value=f"${customer_metrics['avg_spend_per_customer']:,.2f}",
            delta="Lifetime value"
        )
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 50px;'>
        <p>📊 <b>Dashboard Information:</b></p>
        <p>Data updates automatically | All metrics calculated in real-time | Star-schema database design</p>
        <p style='margin-top: 20px; color: #999;'>Built with Streamlit • Powered by SQLite • Analytics Dashboard v1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.info("Please ensure the database has been initialized with the ETL pipeline.")
