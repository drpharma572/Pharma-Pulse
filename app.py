# 📊 PharmaPulse — Interactive Research Data Dashboard
# Streamlit App

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO
import tempfile
import os
import numpy as np

# App config
st.set_page_config(page_title="PharmaPulse Excel Viewer", layout="wide")
st.title("📊 PharmaPulse Interactive Excel Viewer")

# ------------------------
# File upload
# ------------------------
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")

    # ------------------------
    # Data preview
    # ------------------------
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10))

    st.subheader("📈 Summary Statistics")
    st.dataframe(df.describe(include='all'))

    # ------------------------
    # Data filters
    # ------------------------
    st.subheader("🎯 Data Filters")
    cols_to_filter = st.multiselect("Select columns to filter", df.columns.tolist())
    filtered_df = df.copy()
    for col in cols_to_filter:
        if df[col].dtype == object:
            selected = st.multiselect(f"Filter {col}", df[col].unique())
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
        else:
            min_val, max_val = st.slider(f"{col} range", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))
            filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
    st.write(f"Filtered Data — {filtered_df.shape[0]} rows remaining.")

    # ------------------------
    # Charts
    # ------------------------
    st.subheader("📊 Data Visualization")

    chart_images = []

    numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = filtered_df.select_dtypes(include='object').columns.tolist()

    # Bar Chart
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols)
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
        bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        chart_images.append(buf)

    # Pie Chart
    if categorical_cols:
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols)
        pie_data = filtered_df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig2)
        buf2 = BytesIO()
        fig2.savefig(buf2, format="png")
        buf2.seek(0)
        chart_images.append(buf2)

    # Histogram
    if numeric_cols:
        hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols)
        fig3, ax3 = plt.subplots()
        ax3.hist(filtered_df[hist_col], bins=10, color='skyblue', edgecolor='black')
        ax3.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig3)
        buf3 = BytesIO()
        fig3.savefig(buf3, format="png")
        buf3.seek(0)
        chart_images.append(buf3)

    # Scatter plot
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("Select X-axis numeric column for Scatter plot", numeric_cols)
        y_col = st.selectbox("Select Y-axis numeric column for Scatter plot", numeric_cols)
        fig4, ax4 = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax4)
        ax4.set_title(f"Scatter Plot: {x_col} vs {y_col}")
        st.pyplot(fig4)
        buf4 = BytesIO()
        fig4.savefig(buf4, format="png")
        buf4.seek(0)
        chart_images.append(buf4)

    # Line Chart
    if numeric_cols:
        line_col = st.selectbox("Select numeric column for Line chart", numeric_cols)
        fig5, ax5 = plt.subplots()
        ax5.plot(filtered_df[line_col], marker='o')
        ax5.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig5)
        buf5 = BytesIO()
        fig5.savefig(buf5, format="png")
        buf5.seek(0)
        chart_images.append(buf5)

    # Area Chart
    if numeric_cols:
        area_col = st.selectbox("Select numeric column for Area chart", numeric_cols)
        fig6, ax6 = plt.subplots()
        ax6.fill_between(range(len(filtered_df[area_col])), filtered_df[area_col], color='orange', alpha=0.5)
        ax6.set_title(f"Area Chart of {area_col}")
        st.pyplot(fig6)
        buf6 = BytesIO()
        fig6.savefig(buf6, format="png")
        buf6.seek(0)
        chart_images.append(buf6)

    # ------------------------
    # Auto-generate Results & Conclusion
    # ------------------------
    st.subheader("📝 Auto-generated Research Results & Conclusion")
    result_text = f"The dataset contains {filtered_df.shape[0]} rows and {filtered_df.shape[1]} columns. Key numeric columns: {numeric_cols}. Key categorical columns: {categorical_cols}."
    st.text_area("Results", result_text, height=100)
    conclusion_text = "The analysis provides visual insights into the dataset, showing distribution and relationships between variables."
    st.text_area("Conclusion", conclusion_text, height=100)

    # ------------------------
    # PDF Download
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
        temp_files = []
        for buf in chart_buffers:
            buf.seek(0)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_file.write(buf.getbuffer())
            temp_file.close()
            pdf.add_page()
            pdf.image(temp_file.name, x=10, y=20, w=180)
            temp_files.append(temp_file.name)

        # Data preview
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Data Preview (first 10 rows)", ln=True)
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

        # Clean up temp files
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        for f in temp_files:
            os.remove(f)
        return buffer

    pdf_file = create_pdf(filtered_df, result_text, chart_images)
    st.download_button("📥 Download Full PDF Report", data=pdf_file, file_name="pharmapulse_report.pdf", mime="application/pdf")
