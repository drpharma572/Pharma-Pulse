# 📊 PharmaPulse — Hospital DUS Dashboard
# Developed by Dr. K | PharmaPulseByDrK

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import tempfile
from fpdf import FPDF
import numpy as np

# ------------------------------
# App Config
# ------------------------------
st.set_page_config(page_title="PharmaPulse DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Hospital DUS Data Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------------
# File Upload
# ------------------------------
uploaded_file = st.file_uploader(
    "Upload Excel (.xlsx, .xls) or CSV (.csv) file",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=False
)

if uploaded_file:
    # Detect file type and read
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded: {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")
        st.stop()

    # ------------------------------
    # Data Preview
    # ------------------------------
    st.subheader("### Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    st.markdown(f"**Detected numeric columns:** {numeric_cols}")
    st.markdown(f"**Detected categorical columns:** {categorical_cols}")

    # ------------------------------
    # Filters
    # ------------------------------
    st.subheader("### Quick Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        opts = st.multiselect(f"Filter {col}", options=filtered_df[col].unique())
        if opts:
            filtered_df = filtered_df[filtered_df[col].isin(opts)]
    st.markdown(f"After filters: {len(filtered_df)} rows")

    # ------------------------------
    # Descriptive Statistics
    # ------------------------------
    st.subheader("### Descriptive Statistics (Numeric)")
    st.dataframe(filtered_df[numeric_cols].describe())

    st.subheader("### Descriptive Statistics (Categorical)")
    for col in categorical_cols:
        st.write(f"**{col} value counts:**")
        st.dataframe(filtered_df[col].value_counts())

    # ------------------------------
    # Visualizations
    # ------------------------------
    st.subheader("### Visualizations")

    # Bar chart
    if numeric_cols and categorical_cols:
        st.markdown("**Bar Chart**")
        num_col = st.selectbox("Select numeric column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select categorical column", categorical_cols, key="bar_cat")
        fig, ax = plt.subplots()
        grouped = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        sns.barplot(x=cat_col, y=num_col, data=grouped, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig, use_container_width=True)

    # Histogram
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select numeric column for histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots()
        ax.hist(filtered_df[hist_col], bins=10, color="skyblue", edgecolor="black")
        ax.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig, use_container_width=True)

    # Scatter
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("Select X-axis numeric column", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Select Y-axis numeric column", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=x_col, y=y_col, data=filtered_df, ax=ax)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig, use_container_width=True)

    # Pie chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="pie_col")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig, use_container_width=True)

    # ------------------------------
    # Auto-generated Results & Conclusion (simple)
    # ------------------------------
    st.subheader("### 🧠 Auto-generated Research Results & Conclusion")
    result_text = f"Data contains {len(filtered_df)} rows and {len(filtered_df.columns)} columns.\n"
    result_text += f"Numeric columns summary:\n{filtered_df[numeric_cols].describe().to_string()}\n"
    result_text += f"Categorical columns summary:\n"
    for col in categorical_cols:
        result_text += f"{col}: {filtered_df[col].value_counts().to_dict()}\n"

    conclusion_text = "This dataset is suitable for DUS analysis and visual inspection using charts above.\n"
    conclusion_text += "Further statistical tests (chi-square, t-tests, ANOVA) can be performed as needed for publication-ready research."

    st.text_area("Results", result_text, height=200)
    st.text_area("Conclusion", conclusion_text, height=150)

    # ------------------------------
    # Shareable PDF
    # ------------------------------
    st.subheader("### 📄 Generate PDF & Share")
    def create_pdf(df, results, charts):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "📊 PharmaPulse Report", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 6, results)
        pdf.add_page()
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "PharmaPulseByDrK", ln=True)
        pdf.multi_cell(0, 5, df.head(10).to_string())
        # Charts can be saved to temporary PNGs and added here if needed
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer.read()

    chart_images = []  # placeholder for charts if needed
    pdf_data = create_pdf(filtered_df, result_text, chart_images)
    st.download_button("Download PDF", data=pdf_data, file_name="PharmaPulse_Report.pdf", mime="application/pdf")

    # ------------------------------
    # Shareable Link (temporary solution)
    # ------------------------------
    st.subheader("### 🔗 Shareable Link")
    b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{uploaded_file.name}">Click here to download and share your dataset</a>'
    st.markdown(href, unsafe_allow_html=True)
