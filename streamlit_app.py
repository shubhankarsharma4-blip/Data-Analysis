import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime, timedelta
import os

BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "Data" / "Processed"
CSV_TABLES = [
    "dim_products",
    "dim_users",
    "fact_orders",
    "fact_order_items",
    "fact_reviews",
    "fact_events",
]


def safe_read_csv(csv_file: Path) -> tuple[pd.DataFrame, dict]:
    """Read a CSV safely and return debug metadata for the UI."""
    relative_path = str(csv_file.relative_to(BASE_DIR))

    try:
        if not csv_file.exists():
            return pd.DataFrame(), {
                "status": "missing",
                "path": relative_path,
                "message": "File not found",
            }

        df = pd.read_csv(csv_file)
        return df, {
            "status": "loaded",
            "path": relative_path,
            "message": f"Loaded {len(df):,} rows",
        }
    except Exception as e:
        return pd.DataFrame(), {
            "status": "error",
            "path": relative_path,
            "message": f"{type(e).__name__}: {e}",
        }

# Page Configuration - Must be first
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSV data directly into memory as fallback
@st.cache_data
def load_csv_data():
    """Load all CSV files directly into memory using repo-relative paths."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    debug_info = {}

    for table_name in CSV_TABLES:
        csv_file = PROCESSED_DIR / f"{table_name}.csv"
        df, status = safe_read_csv(csv_file)
        data[table_name] = df
        debug_info[table_name] = status

    return {"tables": data, "debug": debug_info}

# Initialize database from CSV files
@st.cache_resource
def get_database_engine():
    """Initialize database from CSV files - always rebuild"""
    db_path = BASE_DIR / "ecommerce.db"
    
    try:
        from sqlalchemy import create_engine

        engine = create_engine(f"sqlite:///{db_path.as_posix()}")
        
        loaded_count = 0
        for table_name, df in csv_data.items():
            if df.empty:
                continue

            try:
                df.to_sql(table_name, engine, if_exists="replace", index=False)
                loaded_count += 1
            except Exception as e:
                st.warning(f"Database skipped `{table_name}`: {e}")
        
        if loaded_count == 0:
            return None
            
        return engine
        
    except Exception as e:
        st.error(f"❌ Database initialization error: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        return None

# Initialize on startup
csv_payload = load_csv_data()
csv_data = csv_payload["tables"]
csv_debug = csv_payload["debug"]
engine = get_database_engine()

loaded_files = [name for name, info in csv_debug.items() if info["status"] == "loaded"]
missing_files = [name for name, info in csv_debug.items() if info["status"] == "missing"]
errored_files = [name for name, info in csv_debug.items() if info["status"] == "error"]
demo_mode = len(loaded_files) == 0


def has_columns(table_name, columns):
    """Check that a cached DataFrame exists and contains the required columns."""
    df = csv_data.get(table_name, pd.DataFrame())
    return not df.empty and set(columns).issubset(df.columns)

# Check if we have data
if False and csv_data.get('fact_order_items', pd.DataFrame()).empty:
    st.error("❌ No data found! Please ensure CSV files exist in Data/Processed/")
    st.info("Required files: fact_order_items.csv, fact_orders.csv, dim_users.csv, dim_products.csv")
    pass

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

# Sidebar Navigation
st.sidebar.title("Dashboard Navigation")
page = st.sidebar.selectbox("Choose a page", ["Overview", "Analytics"])

if demo_mode:
    st.warning(
        "Data files were not found in `Data/Processed/`. The dashboard is running in demo mode and will keep rendering with empty-state UI."
    )
elif missing_files or errored_files:
    st.warning(
        "Some CSV files are unavailable, so a few charts may show empty states while the rest of the dashboard continues to work."
    )

with st.sidebar.expander("Data Loading Debug", expanded=False):
    st.caption(f"Processed directory: `{PROCESSED_DIR.relative_to(BASE_DIR)}`")
    for table_name in CSV_TABLES:
        info = csv_debug[table_name]
        status_label = {"loaded": "OK", "missing": "Missing", "error": "Error"}[info["status"]]
        st.write(f"{status_label}: `{table_name}.csv`")
        st.caption(f"{info['path']} | {info['message']}")

analytics_option = None
if page == "Analytics":
    analytics_option = st.sidebar.selectbox(
        "Choose Analytics Category",
        [
            "Revenue Trends",
            "Products Performance",
            "Customer Insights",
            "Category Analysis",
            "Customer Segmentation",
            "Sales Trend by Category",
            "Top Customers",
            "Detailed Product Performance",
            "User Demographics"
        ]
    )

# Data loading functions - use CSV directly if database fails
def load_data(query):
    """Load data - try database first, fallback to CSV"""
    if engine:
        try:
            result = pd.read_sql(query, engine)
            if not result.empty:
                return result
        except:
            pass  # Fall back to CSV
    
    # Fallback: Calculate from CSV data
    return calculate_from_csv(query)

def calculate_from_csv(query):
    """Calculate query results from CSV data directly"""
    # This is a simplified fallback - implement specific queries as needed
    return pd.DataFrame()

# Query Functions using CSV data directly
def get_kpis():
    """Get key performance indicators"""
    if not has_columns("fact_order_items", {"order_id", "user_id", "item_total"}):
        return {
            'total_orders': 0,
            'total_customers': 0,
            'total_revenue': 0.0,
            'avg_order_value': 0.0
        }
    
    df = csv_data['fact_order_items']
    
    total_orders = df['order_id'].nunique()
    total_customers = df['user_id'].nunique()
    total_revenue = df['item_total'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        'total_orders': int(total_orders),
        'total_customers': int(total_customers),
        'total_revenue': float(round(total_revenue, 2)),
        'avg_order_value': float(round(avg_order_value, 2))
    }

def get_revenue_by_month():
    """Get monthly revenue trend"""
    if not has_columns("fact_order_items", {"order_id", "item_total"}) or not has_columns("fact_orders", {"order_id", "order_date"}):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    orders = csv_data['fact_orders']
    
    # Merge and calculate
    merged = order_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')
    merged['order_date'] = pd.to_datetime(merged['order_date'])
    merged['month'] = merged['order_date'].dt.to_period('M').astype(str)
    
    monthly = merged.groupby('month')['item_total'].sum().reset_index()
    monthly.columns = ['month', 'revenue']
    monthly['revenue'] = monthly['revenue'].round(2)
    
    return monthly.sort_values('month')

def get_top_products():
    """Get top 10 products by revenue"""
    if not has_columns("fact_order_items", {"product_id", "item_total", "quantity"}) or not has_columns("dim_products", {"product_id", "product_name"}):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    products = csv_data['dim_products']
    
    merged = order_items.merge(products[['product_id', 'product_name']], on='product_id', how='left')
    
    top = merged.groupby('product_name').agg({
        'item_total': 'sum',
        'quantity': 'count'
    }).reset_index()
    
    top.columns = ['product_name', 'total_revenue', 'quantity_sold']
    top['total_revenue'] = top['total_revenue'].round(2)
    
    return top.nlargest(10, 'total_revenue')

def get_customer_metrics():
    """Get customer-related metrics"""
    if not has_columns("fact_order_items", {"user_id", "order_id", "item_total"}):
        return {
            'total_customers': 0,
            'avg_orders_per_customer': 0.0,
            'avg_spend_per_customer': 0.0
        }
    
    df = csv_data['fact_order_items']
    
    customer_stats = df.groupby('user_id').agg({
        'order_id': 'nunique',
        'item_total': 'sum'
    }).reset_index()
    
    customer_stats.columns = ['user_id', 'order_count', 'total_spent']
    
    total_customers = len(customer_stats)
    avg_orders = customer_stats['order_count'].mean()
    avg_spend = customer_stats['total_spent'].mean()
    
    return {
        'total_customers': int(total_customers),
        'avg_orders_per_customer': float(round(avg_orders, 2)),
        'avg_spend_per_customer': float(round(avg_spend, 2))
    }

def get_product_reviews():
    """Get product ratings"""
    if not has_columns("fact_reviews", {"product_id", "rating", "review_id"}) or not has_columns("dim_products", {"product_id", "product_name"}):
        return pd.DataFrame()
    
    reviews = csv_data['fact_reviews']
    products = csv_data['dim_products']
    
    merged = reviews.merge(products[['product_id', 'product_name']], on='product_id', how='left')
    
    product_reviews = merged.groupby('product_name').agg({
        'rating': 'mean',
        'review_id': 'count'
    }).reset_index()
    
    product_reviews.columns = ['product_name', 'avg_rating', 'review_count']
    product_reviews['avg_rating'] = product_reviews['avg_rating'].round(2)
    
    return product_reviews.nlargest(10, 'avg_rating')

def get_category_analysis():
    """Get product category analysis"""
    if not has_columns("fact_order_items", {"product_id", "order_id", "item_total", "item_price", "quantity"}) or not has_columns("dim_products", {"product_id", "category"}):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    products = csv_data['dim_products']
    
    merged = order_items.merge(products[['product_id', 'category']], on='product_id', how='left')
    
    category_stats = merged.groupby('category').agg({
        'product_id': 'nunique',
        'order_id': 'nunique',
        'item_total': 'sum',
        'item_price': 'mean',
        'quantity': 'sum'
    }).reset_index()
    
    category_stats.columns = ['category', 'product_count', 'order_count', 'category_revenue', 'avg_price', 'total_quantity']
    category_stats['category_revenue'] = category_stats['category_revenue'].round(2)
    category_stats['avg_price'] = category_stats['avg_price'].round(2)
    
    return category_stats.sort_values('category_revenue', ascending=False)

def get_customer_segments():
    """Get customer segmentation analysis"""
    if not has_columns("fact_order_items", {"user_id", "order_id", "item_total"}):
        return pd.DataFrame()
    
    df = csv_data['fact_order_items']
    
    customer_stats = df.groupby('user_id').agg({
        'order_id': 'nunique',
        'item_total': 'sum'
    }).reset_index()
    
    customer_stats.columns = ['user_id', 'order_count', 'total_spent']
    
    def get_segment(spent):
        if spent > 5000:
            return 'Premium (>$5k)'
        elif spent > 2000:
            return 'Gold ($2k-$5k)'
        elif spent > 500:
            return 'Silver ($500-$2k)'
        else:
            return 'Bronze (<$500)'
    
    customer_stats['segment'] = customer_stats['total_spent'].apply(get_segment)
    
    segments = customer_stats.groupby('segment').agg({
        'user_id': 'count',
        'total_spent': ['mean', 'sum'],
        'order_count': 'mean'
    }).reset_index()
    
    segments.columns = ['segment', 'customer_count', 'avg_spend', 'segment_revenue', 'avg_orders']
    segments['avg_spend'] = segments['avg_spend'].round(2)
    segments['segment_revenue'] = segments['segment_revenue'].round(2)
    segments['avg_orders'] = segments['avg_orders'].round(2)
    
    return segments.sort_values('segment_revenue', ascending=False)

def get_sales_by_category():
    """Get sales trend by category"""
    if (
        not has_columns("fact_order_items", {"order_id", "product_id", "item_total"})
        or not has_columns("fact_orders", {"order_id", "order_date"})
        or not has_columns("dim_products", {"product_id", "category"})
    ):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    orders = csv_data['fact_orders']
    products = csv_data['dim_products']
    
    merged = order_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')
    merged = merged.merge(products[['product_id', 'category']], on='product_id', how='left')
    
    merged['order_date'] = pd.to_datetime(merged['order_date'])
    merged['month'] = merged['order_date'].dt.to_period('M').astype(str)
    
    monthly_category = merged.groupby(['month', 'category'])['item_total'].sum().reset_index()
    monthly_category.columns = ['month', 'category', 'revenue']
    monthly_category['revenue'] = monthly_category['revenue'].round(2)
    
    return monthly_category.sort_values(['month', 'revenue'], ascending=[True, False])

def get_top_customers():
    """Get top customers by revenue"""
    if not has_columns("fact_order_items", {"user_id", "order_id", "item_total", "item_price"}) or not has_columns("dim_users", {"user_id", "name"}):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    users = csv_data['dim_users']
    
    customer_stats = order_items.groupby('user_id').agg({
        'order_id': 'nunique',
        'item_total': 'sum',
        'item_price': 'mean'
    }).reset_index()
    
    customer_stats.columns = ['user_id', 'order_count', 'total_spent', 'avg_purchase']
    
    merged = customer_stats.merge(users[['user_id', 'name']], on='user_id', how='left')
    merged['total_spent'] = merged['total_spent'].round(2)
    merged['avg_purchase'] = merged['avg_purchase'].round(2)

    return merged.nlargest(10, 'total_spent')[['user_id', 'name', 'order_count', 'total_spent', 'avg_purchase']]

def get_product_performance():
    """Get detailed product performance metrics"""
    if not has_columns("fact_order_items", {"product_id", "order_id", "quantity", "item_total", "item_price"}) or not has_columns("dim_products", {"product_id", "product_name", "category"}):
        return pd.DataFrame()
    
    order_items = csv_data['fact_order_items']
    products = csv_data['dim_products']
    
    merged = order_items.merge(products[['product_id', 'product_name', 'category']], on='product_id', how='left')
    
    product_stats = merged.groupby(['product_id', 'product_name', 'category']).agg({
        'order_id': 'nunique',
        'quantity': 'sum',
        'item_total': 'sum',
        'item_price': 'mean'
    }).reset_index()
    
    product_stats.columns = ['product_id', 'product_name', 'category', 'times_sold', 'units_sold', 'total_revenue', 'avg_price']
    product_stats['total_revenue'] = product_stats['total_revenue'].round(2)
    product_stats['avg_price'] = product_stats['avg_price'].round(2)
    product_stats['units_sold'] = product_stats['units_sold'].round(0)
    
    # Add ratings if available
    if has_columns("fact_reviews", {"product_id", "rating"}):
        reviews = csv_data['fact_reviews']
        avg_ratings = reviews.groupby('product_id')['rating'].mean().reset_index()
        avg_ratings.columns = ['product_id', 'avg_rating']
        avg_ratings['avg_rating'] = avg_ratings['avg_rating'].round(2)
        product_stats = product_stats.merge(avg_ratings, on='product_id', how='left')
        product_stats['avg_rating'] = product_stats['avg_rating'].fillna(0)
    else:
        product_stats['avg_rating'] = 0.0
    
    return product_stats.nlargest(15, 'total_revenue')

def get_gender_distribution():
    """Get gender distribution of users"""
    if not has_columns("dim_users", {"gender"}):
        return pd.DataFrame()

    users = csv_data['dim_users']
    gender_dist = users['gender'].value_counts().reset_index()
    gender_dist.columns = ['gender', 'count']
    gender_dist['percentage'] = (gender_dist['count'] / gender_dist['count'].sum() * 100).round(1)

    return gender_dist

def get_city_distribution():
    """Get top cities by user count"""
    if not has_columns("dim_users", {"city"}):
        return pd.DataFrame()

    users = csv_data['dim_users']
    city_dist = users['city'].value_counts().reset_index()
    city_dist.columns = ['city', 'user_count']
    city_dist['percentage'] = (city_dist['user_count'] / city_dist['user_count'].sum() * 100).round(1)

    return city_dist.nlargest(10, 'user_count')

def get_signup_trends():
    """Get user signup trends by month"""
    if not has_columns("dim_users", {"signup_date"}):
        return pd.DataFrame()

    users = csv_data['dim_users'].copy()
    users['signup_date'] = pd.to_datetime(users['signup_date'])
    users['signup_month'] = users['signup_date'].dt.to_period('M').astype(str)

    signup_trends = users.groupby('signup_month').size().reset_index()
    signup_trends.columns = ['month', 'new_users']

    return signup_trends.sort_values('month')

# Main App
st.title("E-Commerce Analytics Dashboard")
st.markdown('<p class="subtitle">Real-time insights into your e-commerce business performance</p>', unsafe_allow_html=True)

if loaded_files:
    st.caption(f"Loaded CSV files: {', '.join(f'{name}.csv' for name in loaded_files)}")
if missing_files or errored_files:
    unavailable_files = missing_files + errored_files
    st.caption(f"Unavailable CSV files: {', '.join(f'{name}.csv' for name in unavailable_files)}")

try:
    if page == "Overview":
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

    elif page == "Analytics":
        if analytics_option == "Revenue Trends":
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
            else:
                st.info("No revenue data available")

        elif analytics_option == "Products Performance":
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
                else:
                    st.info("No product data available")

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
                else:
                    st.info("No review data available")

        elif analytics_option == "Customer Insights":
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

        elif analytics_option == "Category Analysis":
            # Category Analysis Section
            st.markdown("### 📦 Product Category Analysis", unsafe_allow_html=True)
            category_data = get_category_analysis()

            if not category_data.empty:
                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown("#### Revenue by Category")
                    fig_category = px.bar(
                        category_data,
                        x='category',
                        y='category_revenue',
                        color='category_revenue',
                        template='plotly_white',
                        color_continuous_scale='Blues'
                    )
                    fig_category.update_layout(
                        showlegend=False,
                        hovermode='x',
                        plot_bgcolor='rgba(240, 240, 240, 0.5)',
                        paper_bgcolor='rgba(255,255,255,0)',
                        height=400,
                        xaxis_title="Category",
                        yaxis_title="Revenue ($)"
                    )
                    st.plotly_chart(fig_category, use_container_width=True)

                with col2:
                    st.markdown("#### Category Metrics Table")
                    display_df = category_data.copy()
                    display_df.columns = ['Category', 'Products', 'Orders', 'Revenue', 'Avg Price', 'Units Sold']
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No category data available")

        elif analytics_option == "Customer Segmentation":
            # Customer Segmentation Section
            st.markdown("### 💼 Customer Segmentation", unsafe_allow_html=True)
            segments = get_customer_segments()

            if not segments.empty:
                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown("#### Customer Segments Distribution")
                    fig_segments = px.pie(
                        segments,
                        values='customer_count',
                        names='segment',
                        template='plotly_white',
                        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                    )
                    fig_segments.update_layout(
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig_segments, use_container_width=True)

                with col2:
                    st.markdown("#### Segment Revenue Analysis")
                    fig_seg_revenue = px.bar(
                        segments,
                        x='segment',
                        y='segment_revenue',
                        color='segment_revenue',
                        template='plotly_white',
                        color_continuous_scale='Greens'
                    )
                    fig_seg_revenue.update_layout(
                        showlegend=False,
                        hovermode='x',
                        plot_bgcolor='rgba(240, 240, 240, 0.5)',
                        paper_bgcolor='rgba(255,255,255,0)',
                        height=400,
                        xaxis_title="Segment",
                        yaxis_title="Revenue ($)"
                    )
                    st.plotly_chart(fig_seg_revenue, use_container_width=True)
            else:
                st.info("No customer segmentation data available")

        elif analytics_option == "Sales Trend by Category":
            # Sales by Category Trend
            st.markdown("### 📈 Sales Trend by Category", unsafe_allow_html=True)
            sales_category = get_sales_by_category()

            if not sales_category.empty:
                fig_sales_trend = px.line(
                    sales_category,
                    x='month',
                    y='revenue',
                    color='category',
                    template='plotly_white',
                    markers=True
                )
                fig_sales_trend.update_layout(
                    hovermode='x unified',
                    plot_bgcolor='rgba(240, 240, 240, 0.5)',
                    paper_bgcolor='rgba(255,255,255,0)',
                    height=450,
                    xaxis_title="Month",
                    yaxis_title="Revenue ($)",
                    legend=dict(
                        title="Category",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                st.plotly_chart(fig_sales_trend, use_container_width=True)
            else:
                st.info("No sales trend data available")

        elif analytics_option == "Top Customers":
            # Top Customers Section
            st.markdown("### 🌟 Top 10 Customers", unsafe_allow_html=True)
            top_customers = get_top_customers()

            if not top_customers.empty:
                fig_customers = px.bar(
                    top_customers,
                    x='total_spent',
                    y='name',
                    orientation='h',
                    template='plotly_white',
                    color='order_count',
                    color_continuous_scale='Oranges'
                )
                fig_customers.update_layout(
                    showlegend=True,
                    hovermode='y',
                    plot_bgcolor='rgba(240, 240, 240, 0.5)',
                    paper_bgcolor='rgba(255,255,255,0)',
                    height=500,
                    xaxis_title="Total Spent ($)",
                    yaxis_title="Customer",
                    coloraxis_colorbar=dict(title="Orders")
                )
                st.plotly_chart(fig_customers, use_container_width=True)
            else:
                st.info("No customer data available")

        elif analytics_option == "Detailed Product Performance":
            # Product Performance Detailed Analysis
            st.markdown("### 🏆 Detailed Product Performance", unsafe_allow_html=True)
            product_perf = get_product_performance()

            if not product_perf.empty:
                st.markdown("#### Top 15 Products by Revenue with Full Metrics")
                display_prod = product_perf.copy()
                display_prod.columns = ['Product ID', 'Product', 'Category', 'Times Sold', 'Units Sold', 'Revenue', 'Avg Price', 'Rating']
                st.dataframe(display_prod, use_container_width=True, hide_index=True)

                # Product scatter plot
                st.markdown("#### Product Performance Scatter (Revenue vs Rating vs Units Sold)")
                fig_prod = px.scatter(
                    product_perf,
                    x='total_revenue',
                    y='avg_rating',
                    size='units_sold',
                    hover_name='product_name',
                    color='category',
                    template='plotly_white',
                    size_max=50
                )
                fig_prod.update_layout(
                    hovermode='closest',
                    plot_bgcolor='rgba(240, 240, 240, 0.5)',
                    paper_bgcolor='rgba(255,255,255,0)',
                    height=450,
                    xaxis_title="Total Revenue ($)",
                    yaxis_title="Average Rating"
                )
                st.plotly_chart(fig_prod, use_container_width=True)
            else:
                st.info("No product performance data available")

        elif analytics_option == "User Demographics":
            # User Demographics Section
            st.markdown("### 👤 User Demographics", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                st.markdown("#### Gender Distribution")
                gender_data = get_gender_distribution()
                if not gender_data.empty:
                    fig_gender = px.pie(
                        gender_data,
                        values='count',
                        names='gender',
                        template='plotly_white',
                        color_discrete_sequence=['#FF69B4', '#4169E1']
                    )
                    fig_gender.update_layout(
                        height=300,
                        showlegend=True
                    )
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("No gender data available")

            with col2:
                st.markdown("#### Top 10 Cities by User Count")
                city_data = get_city_distribution()
                if not city_data.empty:
                    fig_city = px.bar(
                        city_data,
                        x='user_count',
                        y='city',
                        orientation='h',
                        template='plotly_white',
                        color='user_count',
                        color_continuous_scale='Blues'
                    )
                    fig_city.update_layout(
                        showlegend=False,
                        hovermode='y',
                        plot_bgcolor='rgba(240, 240, 240, 0.5)',
                        paper_bgcolor='rgba(255,255,255,0)',
                        height=300,
                        xaxis_title="User Count",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_city, use_container_width=True)
                else:
                    st.info("No city data available")

            with col3:
                st.markdown("#### User Signup Trends")
                signup_data = get_signup_trends()
                if not signup_data.empty:
                    fig_signup = px.line(
                        signup_data,
                        x='month',
                        y='new_users',
                        template='plotly_white',
                        markers=True
                    )
                    fig_signup.update_traces(
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=8, color='#764ba2')
                    )
                    fig_signup.update_layout(
                        hovermode='x unified',
                        plot_bgcolor='rgba(240, 240, 240, 0.5)',
                        paper_bgcolor='rgba(255,255,255,0)',
                        height=300,
                        xaxis_title="Month",
                        yaxis_title="New Users"
                    )
                    st.plotly_chart(fig_signup, use_container_width=True)
                else:
                    st.info("No signup data available")

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
    import traceback
    with st.expander("Error Details"):
        st.code(traceback.format_exc())
    st.info("Please ensure CSV files are available in Data/Processed/ folder")
