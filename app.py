# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO
import os

# Try importing SciPy (optional AUC)
try:
    from scipy.integrate import simps
    scipy_available = True
except ImportError:
    scipy_available = False
    st.warning("SciPy not installed: AUC calculations will be skipped.")

# App configuration
st.set_page_config(page_title="📊 PharmaPulse Excel Viewer", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")
st.markdown("Upload your Excel data, explore visualizations, and auto-generate research results & conclusions.")

# ------------------------
# File upload
# ------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel file (XLSX)", 
    type=["xlsx"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")

    # ------------------------
    # Data Preview & Summary
    # ------------------------
    st.subheader("📋 Data Preview")
    st.dataframe(df.head())

    st.subheader("📈 Summary Statistics")
    st.dataframe(df.describe(include='all').T)

    # ------------------------
    # Data Filtering
    # ------------------------
    st.subheader("🎯 Data Filters")
    filtered_df = df.copy()
    filter_cols = st.multiselect("Select columns to filter", df.columns.tolist())
    for col in filter_cols:
        unique_vals = df[col].dropna().unique().tolist()
        selected_vals = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

    st.write(f"Filtered Data — {len(filtered_df)} rows remaining.")

    # ------------------------
    # Charts
    # ------------------------
    st.subheader("📊 Data Visualization")
    chart_images = []

    numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = filtered_df.select_dtypes(include='object').columns.tolist()

    # Bar chart
    if numeric_cols and categorical_cols:
        st.markdown("### Bar Chart")
        num_col = st.selectbox("Select numeric column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select categorical column", categorical_cols, key="bar_cat")
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=filtered_df, ci=None, ax=ax)  # ci=None avoids errors with small datasets
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig)
        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        chart_images.append(buffer)

    # Pie chart
    if categorical_cols:
        st.markdown("### Pie Chart")
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="pie_col")
        pie_data = filtered_df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig2)
        buffer2 = BytesIO()
        fig2.savefig(buffer2, format="png")
        chart_images.append(buffer2)

    # Histogram
    if numeric_cols:
        st.markdown("### Histogram")
        hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols, key="hist_col")
        fig3, ax3 = plt.subplots()
        ax3.hist(filtered_df[hist_col].dropna(), bins='auto', color='skyblue', edgecolor='black')
        ax3.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig3)
        buffer3 = BytesIO()
        fig3.savefig(buffer3, format="png")
        chart_images.append(buffer3)

    # Scatter plot
    if len(numeric_cols) >= 2:
        st.markdown("### Scatter Plot")
        x_col = st.selectbox("Select X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Select Y-axis", numeric_cols, key="scatter_y")
        fig4, ax4 = plt.subplots()
        ax4.scatter(filtered_df[x_col], filtered_df[y_col], c='green', alpha=0.6)
        ax4.set_xlabel(x_col)
        ax4.set_ylabel(y_col)
        ax4.set_title(f"Scatter Plot: {y_col} vs {x_col}")
        st.pyplot(fig4)
        buffer4 = BytesIO()
        fig4.savefig(buffer4, format="png")
        chart_images.append(buffer4)

    # Line chart
    if numeric_cols:
        st.markdown("### Line Chart")
        line_col = st.selectbox("Select numeric column for Line chart", numeric_cols, key="line_col")
        fig5, ax5 = plt.subplots()
        ax5.plot(filtered_df[line_col], marker='o', color='orange')
        ax5.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig5)
        buffer5 = BytesIO()
        fig5.savefig(buffer5, format="png")
        chart_images.append(buffer5)

    # Area chart
    if numeric_cols:
        st.markdown("### Area Chart")
        area_col = st.selectbox("Select numeric column for Area chart", numeric_cols, key="area_col")
        fig6, ax6 = plt.subplots()
        ax6.fill_between(filtered_df.index, filtered_df[area_col], color='lightblue', alpha=0.6)
        ax6.set_title(f"Area Chart of {area_col}")
        st.pyplot(fig6)
        buffer6 = BytesIO()
        fig6.savefig(buffer6, format="png")
        chart_images.append(buffer6)

    # ------------------------
    # Generate Results & Conclusion
    # ------------------------
    st.subheader("📄 Auto Results & Conclusion")
    result_text = f"Data contains {len(filtered_df)} rows and {len(filtered_df.columns)} columns.\n"
    result_text += f"Numeric columns: {numeric_cols}\nCategorical columns: {categorical_cols}\n"

    conclusion_text = "The analysis provides visual insights into the dataset, showing distribution and relationships between variables."

    st.text_area("Results", value=result_text, height=100)
    st.text_area("Conclusion", value=conclusion_text, height=100)

    # ------------------------
    # PDF Export
    # ------------------------
    def create_pdf(df, results, chart_buffers):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title page
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "📊 PharmaPulse Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, results)
        pdf.ln(5)

        # Charts
        for buf in chart_buffers:
            buf.seek(0)
            pdf.add_page()
            pdf.image(buf, x=10, y=20, w=180)

        # Data preview
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Data Preview", ln=True)
        pdf.set_font("Arial", "", 10)
        for i, row in df.head(10).iterrows():
            pdf.multi_cell(0, 6, str(row.to_dict()))
            pdf.ln(1)

        # Conclusion
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Conclusion", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, conclusion_text)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    st.download_button(
        "📥 Download PDF Report",
        data=create_pdf(filtered_df, result_text, chart_images),
        file_name="PharmaPulse_Report.pdf",
        mime="application/pdf"
    )
