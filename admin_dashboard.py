"""Streamlit dashboard for viewing user tokens."""
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ML Server Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/finalserver_db")

@st.cache_resource
def get_database_connection():
    """Create database connection."""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

def load_users_data():
    """Load all users from database."""
    Session = get_database_connection()
    db = Session()

    try:
        # Query users table
        query = "SELECT id, username, tokens FROM users ORDER BY tokens DESC"
        df = pd.read_sql(query, db.bind)
        return df
    finally:
        db.close()

def load_stats():
    """Load statistics."""
    Session = get_database_connection()
    db = Session()

    try:
        # Get total users
        total_users_query = "SELECT COUNT(*) as count FROM users"
        total_users = pd.read_sql(total_users_query, db.bind)['count'][0]

        # Get total tokens
        total_tokens_query = "SELECT SUM(tokens) as total FROM users"
        total_tokens_result = pd.read_sql(total_tokens_query, db.bind)['total'][0]
        total_tokens = total_tokens_result if total_tokens_result else 0

        # Get total models
        total_models_query = "SELECT COUNT(*) as count FROM model_metadata"
        total_models = pd.read_sql(total_models_query, db.bind)['count'][0]

        return {
            "total_users": total_users,
            "total_tokens": int(total_tokens),
            "total_models": total_models
        }
    finally:
        db.close()

# Title
st.title("📊 ML Server Admin Dashboard")
st.markdown("### User Token Management")

# Add refresh button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()

st.markdown("---")

# Display statistics
try:
    stats = load_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="👥 Total Users",
            value=stats['total_users']
        )

    with col2:
        st.metric(
            label="🪙 Total Tokens",
            value=stats['total_tokens']
        )

    with col3:
        st.metric(
            label="🤖 Total Models",
            value=stats['total_models']
        )

    st.markdown("---")

except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")

# Display users table
st.subheader("👤 User Token Balances")

try:
    df = load_users_data()

    if df.empty:
        st.info("No users found in the database.")
    else:
        # Format the dataframe
        df_display = df.copy()
        df_display.columns = ['ID', 'Username', 'Tokens']

        # Display with custom styling
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Username": st.column_config.TextColumn("Username", width="medium"),
                "Tokens": st.column_config.NumberColumn(
                    "Tokens",
                    width="medium",
                    format="%d 🪙"
                ),
            }
        )

        # Summary
        st.markdown("---")
        st.markdown(f"**Total Users:** {len(df)}")
        st.markdown(f"**Average Tokens per User:** {df['tokens'].mean():.2f}")
        st.markdown(f"**Highest Balance:** {df['tokens'].max()} tokens")
        st.markdown(f"**Lowest Balance:** {df['tokens'].min()} tokens")

        # Token distribution chart
        st.subheader("📈 Token Distribution")
        st.bar_chart(df.set_index('username')['tokens'])

except Exception as e:
    st.error(f"Error loading user data: {str(e)}")
    st.info("Make sure the database is running and accessible.")

# Footer
st.markdown("---")
st.markdown("🔗 **ML Server Dashboard** | Refresh page to update data")
