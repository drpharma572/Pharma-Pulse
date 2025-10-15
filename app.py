import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import tempfile
from io import BytesIO
from fpdf import FPDF, HTMLMixin

# ------------------------------
# PDF class with UTF-8 support and footer
# ------------------------------
class PDF(FPDF, HTMLMixin):
    def footer(self):
        self.set_y(-10)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "PharmaPulseByDrK", align="C")

def create_pdf(df, result_text, chart_buffers):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --------------------
    # Title Page
    # --------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "📊 PharmaPulse", ln=True, align="C")
    pdf.set_font("Arial", "", 14)
    pdf.ln(10)
    pdf.multi_cell(0, 8, "Interactive Research Data Dashboard by Dr. K\n\nThis report includes analysis, charts, and conclusions generated automatically from the uploaded Excel data.", align="C")

    # --------------------
    # Results
    # --------------------
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, "📌 Analysis Results:\n" + result_text)

    # --------------------
    # Charts
    # --------------------
    temp_files = []
    for buf in chart_buffers:
        buf.seek(0)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(buf.getbuffer())
        temp_file.close()
        pdf.add_page()
        pdf.image(temp_file.name, x=10, y=20, w=180)
        temp_files.append(temp_file.name)

    # --------------------
    # Data Preview
    # --------------------
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "📋 Sample Data Preview (First 10 rows):\n")
    for i, row in df.head(10).iterrows():
        pdf.multi_cell(0, 6, str(row.to_dict()))
        pdf.ln(1)

    # --------------------
    # Conclusion
    # --------------------
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, "📄 Conclusion:\nThe analysis provides insights into data distribution, relationships between variables, and key trends.")

    # Save to BytesIO
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    # Clean temp files
    for f in temp_files:
        os.remove(f)

    return buffer

# ------------------------------
# Streamlit App
# ------------------------------
st.set_page_config(page_title="PharmaPulse Excel Viewer", layout="wide")
st.title("📊 PharmaPulse Interactive Excel Viewer")

# ------------------------------
# File Upload
# ------------------------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")

    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df)

    # Summary
    st.subheader("📈 Summary Statistics")
    st.write(df.describe(include='all'))

    # ------------------------------
    # Data Visualization
    # ------------------------------
    chart_images = []

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    # Bar chart
    if numeric_cols and categorical_cols:
        st.subheader("📊 Bar Chart")
        num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols, key="bar_cat")
        if num_col and cat_col:
            bar_data = df.groupby(cat_col)[num_col].sum().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
            ax.set_title(f"{num_col} by {cat_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # Pie chart
    if categorical_cols:
        st.subheader("🥧 Pie Chart")
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="pie_cat")
        if pie_col:
            pie_data = df[pie_col].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
            ax.set_title(f"Pie chart of {pie_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # Histogram
    if numeric_cols:
        st.subheader("📊 Histogram")
        hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols, key="hist_num")
        if hist_col:
            fig, ax = plt.subplots()
            ax.hist(df[hist_col].dropna(), bins='auto', color='skyblue', edgecolor='black')
            ax.set_title(f"Histogram of {hist_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # Scatter plot
    if len(numeric_cols) >= 2:
        st.subheader("🔹 Scatter Plot")
        x_col = st.selectbox("Select X-axis numeric column", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Select Y-axis numeric column", numeric_cols, key="scatter_y")
        if x_col and y_col:
            fig, ax = plt.subplots()
            ax.scatter(df[x_col], df[y_col], color='green')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{y_col} vs {x_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # Line chart
    if numeric_cols:
        st.subheader("📈 Line Chart")
        line_col = st.selectbox("Select numeric column for Line chart", numeric_cols, key="line_col")
        if line_col:
            fig, ax = plt.subplots()
            ax.plot(df[line_col], color='orange')
            ax.set_title(f"Line chart of {line_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # Area chart
    if numeric_cols:
        st.subheader("📊 Area Chart")
        area_col = st.selectbox("Select numeric column for Area chart", numeric_cols, key="area_col")
        if area_col:
            fig, ax = plt.subplots()
            ax.fill_between(df.index, df[area_col], color='lightgreen', alpha=0.6)
            ax.set_title(f"Area chart of {area_col}")
            st.pyplot(fig)
            buf = BytesIO()
            fig.savefig(buf, format="png")
            chart_images.append(buf)
            plt.close(fig)

    # ------------------------------
    # Auto-generated Results & Conclusion
    # ------------------------------
    st.subheader("📝 Auto-generated Research Results & Conclusion")
    result_text = f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns. " \
                  f"Numeric columns: {numeric_cols}, Categorical columns: {categorical_cols}."
    st.text_area("Results", value=result_text, height=100)
    st.text_area("Conclusion", value="The analysis provides insights into distribution and relationships between variables.", height=100)

    # ------------------------------
    # Download PDF
    # ------------------------------
    if st.button("📥 Download Full PDF Report"):
        pdf_file = create_pdf(df, result_text, chart_images)
        st.download_button("Download PDF", data=pdf_file, file_name="PharmaPulse_Report.pdf", mime="application/pdf")
