# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import urllib.parse

st.set_page_config(page_title="PharmaPulse DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Model")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------
# File Upload
# ------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel/CSV file (XLSX, XLS, CSV)", 
    type=["xlsx", "xls", "csv"]
)

def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# ------------------------
# Load data and preview
# ------------------------
if uploaded_file:
    df = load_file(uploaded_file)
    st.success(f"✅ Loaded: {uploaded_file.name}")
    
    st.subheader("📋 Data Overview")
    st.write("**Numeric Columns:**", df.select_dtypes(include=np.number).columns.tolist())
    st.write("**Categorical Columns:**", df.select_dtypes(include="object").columns.tolist())
    
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in df.select_dtypes(include=["object", "category"]).columns:
        options = st.multiselect(f"Filter {col}", options=df[col].unique())
        if options:
            filtered_df = filtered_df[filtered_df[col].isin(options)]
    st.write(f"Filtered Rows: {len(filtered_df)}")
    
    # ------------------------
    # Descriptive Statistics
    # ------------------------
    st.subheader("📈 Descriptive Statistics")
    st.write(filtered_df.describe(include="all"))

    # ------------------------
    # Visualizations
    # ------------------------
    st.subheader("🎨 Data Visualizations")
    
    numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = filtered_df.select_dtypes(include="object").columns.tolist()
    
    # Bar chart
    if numeric_cols and categorical_cols:
        st.markdown("**Bar Chart**")
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select Categorical Column", categorical_cols, key="bar_cat")
        bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig, use_container_width=True)
    
    # Histogram
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist")
        fig2, ax2 = plt.subplots()
        sns.histplot(filtered_df[hist_col], bins=10, kde=False, ax=ax2)
        ax2.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig2, use_container_width=True)
    
    # Scatter plot
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig3, ax3 = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax3)
        ax3.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig3, use_container_width=True)
    
    # Pie chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select Categorical Column", categorical_cols, key="pie")
        pie_data = filtered_df[pie_col].value_counts()
        fig4, ax4 = plt.subplots()
        ax4.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax4.set_title(f"Pie Chart of {pie_col}")
        st.pyplot(fig4, use_container_width=True)
    
    # Line chart
    if numeric_cols:
        st.markdown("**Line Chart**")
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line")
        st.line_chart(filtered_df[line_col])
    
    # ------------------------
    # Auto-generated Results & Conclusion
    # ------------------------
    st.subheader("🧠 Auto-generated Results & Conclusion")
    results_text = f"Results: Data contains {len(filtered_df)} rows and {len(filtered_df.columns)} columns."
    conclusion_text = "Conclusion: Descriptive statistics and charts generated for uploaded DUS data."
    st.text(results_text)
    st.text(conclusion_text)

    # ------------------------
    # Shareable Link
    # ------------------------
    st.subheader("🔗 Shareable Link")
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    b64_csv = base64.b64encode(csv_bytes).decode()
    params = {"data": b64_csv}
    query_str = urllib.parse.urlencode(params)
    shareable_link = f"{st.runtime.scriptrunner.get_url()}?{query_str}" if hasattr(st.runtime, "scriptrunner") else f"?{query_str}"
    st.write(f"[Click here to share this report]({shareable_link})")

# ------------------------
# Load shared data from URL
# ------------------------
query_params = st.query_params
if "data" in query_params:
    b64_csv = query_params["data"][0]
    decoded = base64.b64decode(b64_csv)
    df_shared = pd.read_csv(pd.compat.StringIO(decoded.decode("utf-8")))
    st.info("Loaded shared report from link")
    st.dataframe(df_shared.head())
