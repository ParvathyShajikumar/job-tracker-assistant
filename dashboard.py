import streamlit as st
import plotly.express as px
import sqlite3
import pandas as pd

DB_NAME = "job_applications.db"

def get_latest_applications():
    conn = sqlite3.connect(DB_NAME)
    # query = """
    # SELECT company, role, subject, date_applied, status, unique_key
    # FROM applications
    # WHERE rowid IN (
    #     SELECT MAX(rowid)
    #     FROM applications
    #     GROUP BY unique_key
    # )
    # """
    query = """
    SELECT company, role, subject, date_applied, status, unique_key
    FROM applications
    WHERE id IN (
        SELECT MAX(id)
        FROM applications
        GROUP BY unique_key
    )
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_data():
    """Load job applications from SQLite into a DataFrame"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM applications", conn)
    conn.close()
    return df

def main():
    # --- Custom Styling ---
    st.markdown(
        """
        <style>
        .main {
            background-color: #f9f9f9;
            font-family: 'Segoe UI', sans-serif;
        }
        h1 {
            color: #2E86C1;
        }
        .stMetric {
            background: #EAF2F8;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Branding Header ---
    st.title("🚀 Parvathy’s Job Tracker")
    st.caption("Aspiring AI Automation Engineer | Certified Databricks & AWS")

    # --- Sidebar Profile ---
    #st.sidebar.image("https://via.placeholder.com/150", caption="Parvathy", use_column_width=True)
    st.sidebar.image("https://via.placeholder.com/150", caption="Parvathy", use_container_width=True)

    st.sidebar.markdown("**🌸 AI Automation Enthusiast**")
    st.sidebar.markdown("📍 Kerala, India")
    st.sidebar.markdown("[LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourprofile)")

    # --- Load Data ---
    df = get_latest_applications()

    if df.empty:
        st.warning("No job applications found yet. Run email_reader.py to add some!")
        return

    # --- KPI Metrics ---
    st.subheader("✨ Key Metrics")
    # total_apps = len(df)
    # interviews = (df["status"] == "Interview").sum()
    # offers = (df["status"] == "Offer").sum()
    # rejections = (df["status"] == "Rejected").sum()
    total_apps = len(df)
    interviews = len(df[df['status'] == 'Interview'])
    offers = len(df[df['status'] == 'Offer'])
    rejections = len(df[df['status'] == 'Rejected'])
    applied = len(df[df['status'] == 'Applied'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Applied", applied)
    col2.metric("🎯 Interviews", interviews)
    col3.metric("🏆 Offers", offers)
    col4.metric("❌ Rejections", rejections)

    # --- Filters ---
    st.sidebar.header("🔍 Filters")
    company_filter = st.sidebar.selectbox("Filter by Company", ["All"] + sorted(df["company"].unique()))
    role_filter = st.sidebar.selectbox("Filter by Role", ["All"] + sorted(df["role"].unique()))
    status_filter = st.sidebar.selectbox("Filter by Status", ["All"] + sorted(df["status"].unique()))

    filtered_df = df.copy()
    if company_filter != "All":
        filtered_df = filtered_df[filtered_df["company"] == company_filter]
    if role_filter != "All":
        filtered_df = filtered_df[filtered_df["role"] == role_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]

    # --- Applications Table ---
    st.subheader("📋 Applications Table")
    st.dataframe(filtered_df)

    # --- Download Button ---
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Applications as CSV",
        data=csv,
        file_name="applications.csv",
        mime="text/csv",
    )

    # --- Applications by Status ---
    st.subheader("📈 Applications by Status")
    status_counts = filtered_df["status"].value_counts()
    fig_status = px.bar(
        status_counts,
        x=status_counts.index,
        y=status_counts.values,
        labels={"x": "Status", "y": "Count"},
        title="Applications by Status",
        color=status_counts.index
    )
    st.plotly_chart(fig_status)

    # --- Applications Over Time ---
    st.subheader("⏳ Applications Over Time")
    filtered_df["date_applied"] = pd.to_datetime(filtered_df["date_applied"], errors="coerce")
    timeline = filtered_df.groupby("date_applied")["company"].count().reset_index()
    fig_timeline = px.line(
        timeline,
        x="date_applied",
        y="company",
        labels={"date_applied": "Date", "company": "Applications"},
        title="Applications Timeline"
    )
    st.plotly_chart(fig_timeline)

    # --- Applications by Company ---
    st.subheader("🏢 Applications by Company")
    company_counts = filtered_df["company"].value_counts().reset_index()
    company_counts.columns = ["company", "count"]
    fig_company = px.bar(
        company_counts,
        x="company",
        y="count",
        title="Applications per Company",
        color="count"
    )
    st.plotly_chart(fig_company)

    # --- Applications by Role ---
    st.subheader("💼 Applications by Role")
    role_counts = filtered_df["role"].value_counts().reset_index()
    role_counts.columns = ["role", "count"]
    fig_role = px.bar(
        role_counts,
        x="role",
        y="count",
        title="Applications per Role",
        color="count"
    )
    st.plotly_chart(fig_role)

if __name__ == "__main__":
    main()
