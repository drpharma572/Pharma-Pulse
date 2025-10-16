# 📊 PharmaPulse — Digital DUS Dashboard v2.0
# Developed by Dr. K | PharmaPulseByDrK

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tempfile
import base64
from fpdf import FPDF
import io
from PIL import Image

# ------------------------------
# App Configuration
# ------------------------------
st.set_page_config(page_title="PharmaPulse — Digital DUS Model", layout="wide")
st.title("📊 PharmaPulse — Digital Drug Utilization Study (DUS) Model")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")
st.caption("A digital visualization and reporting platform for hospital-based DUS — usable in Govt. & Private Institutions.")

# ------------------------------
# File Upload
# ------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=False
)

if uploaded_file:
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
    # Data Overview
    # ------------------------------
    st.subheader("📋 Data Overview")
    st.dataframe(df.head(10), use_container_width=True)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()
    st.markdown(f"**Numeric Columns:** {numeric_cols}")
    st.markdown(f"**Categorical Columns:** {categorical_cols}")

    # ------------------------------
    # Filter Section
    # ------------------------------
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        opts = st.multiselect(f"Filter {col}", options=filtered_df[col].dropna().unique())
        if opts:
            filtered_df = filtered_df[filtered_df[col].isin(opts)]
    st.info(f"Filtered Rows: {len(filtered_df)}")

    # ------------------------------
    # Descriptive Statistics
    # ------------------------------
    st.subheader("📈 Descriptive Statistics")
    st.dataframe(filtered_df.describe(include="all"), use_container_width=True)

    # ------------------------------
    # Visualization Section
    # ------------------------------
    st.subheader("🎨 Data Visualizations")

    chart_images = []  # Store chart paths for PDF

    def save_chart(fig, name):
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(tmpfile.name, bbox_inches="tight")
        chart_images.append(tmpfile.name)
        return tmpfile.name

    # 1️⃣ Bar Chart
    if numeric_cols and categorical_cols:
        st.markdown("**Bar Chart**")
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select Categorical Column", categorical_cols, key="bar_cat")
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=filtered_df, estimator=np.mean, ax=ax)
        plt.xticks(rotation=45)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "bar_chart")

    # 2️⃣ Histogram
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots()
        ax.hist(filtered_df[hist_col].dropna(), bins=10, color="skyblue", edgecolor="black")
        ax.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "histogram")

    # 3️⃣ Scatter Plot
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=x_col, y=y_col, data=filtered_df, ax=ax)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "scatter")

    # 4️⃣ Pie Chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select Categorical Column", categorical_cols, key="pie_col")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Distribution of {pie_col}")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "pie")

    # 5️⃣ Line Chart
    if numeric_cols:
        st.markdown("**Line Chart**")
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line_col")
        fig, ax = plt.subplots()
        ax.plot(filtered_df[line_col].dropna(), marker="o")
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "line")

    # 6️⃣ Correlation Heatmap
    if len(numeric_cols) > 1:
        st.markdown("**Correlation Heatmap**")
        fig, ax = plt.subplots()
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "heatmap")

    # 7️⃣ Pictogram
    if categorical_cols:
        st.markdown("**Pictogram Representation**")
        pic_col = st.selectbox("Select Column for Pictogram", categorical_cols, key="pictogram_col")
        counts = filtered_df[pic_col].value_counts()
        fig, ax = plt.subplots(figsize=(8, 3))
        icons = ["💊", "👩‍⚕️", "🏥", "🧪", "🧍"]  # fun medical icons
        labels = list(counts.index)
        pictogram = "".join([f"{icons[i % len(icons)]} " * int(v) for i, v in enumerate(counts)])
        ax.text(0.1, 0.5, pictogram, fontsize=14, wrap=True)
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        save_chart(fig, "pictogram")

    # ------------------------------
    # Auto Results & Conclusion
    # ------------------------------
    st.subheader("🧠 Auto-generated Results & Conclusion")

    result_text = f"""
    Total Records: {len(filtered_df)}
    Numeric Columns: {numeric_cols}
    Categorical Columns: {categorical_cols}

    Quick Insight:
    - Mean age (if available): {filtered_df[numeric_cols[0]].mean() if numeric_cols else 'N/A'}
    - Total drugs analyzed: {filtered_df.shape[0]}
    """

    conclusion_text = """
    This digital model demonstrates Drug Utilization Study (DUS) visualization capability for hospital use.
    It allows data filtering, pattern identification, and graphical interpretation of drug use trends.
    The tool can be shared across departments for evidence-based policy and rational drug use monitoring.
    """

    st.text_area("Results", result_text, height=150)
    st.text_area("Conclusion", conclusion_text, height=150)

    # ------------------------------
    # PDF Report Generator
    # ------------------------------
    st.subheader("📄 Generate & Download PDF Report")

    def create_pdf(df, results, conclusion, charts):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PharmaPulse — Digital DUS Report", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, results)
        pdf.multi_cell(0, 8, conclusion)
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "📊 Visualizations", ln=True)
        for chart in charts:
            pdf.image(chart, w=160)
            pdf.ln(10)
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return buf

    pdf_data = create_pdf(filtered_df, result_text, conclusion_text, chart_images)
    st.download_button("⬇️ Download Full PDF Report", data=pdf_data, file_name="PharmaPulse_DUS_Report.pdf", mime="application/pdf")

    # ------------------------------
    # Shareable Link (Public Access)
    # ------------------------------
    st.subheader("🔗 Generate Shareable Dataset Link")
    b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    link = f"data:file/csv;base64,{b64}"
    st.markdown(f"[Click here to download & share the dataset 🔗]({link})", unsafe_allow_html=True)

else:
    st.info("👆 Please upload your DUS dataset (Excel or CSV) to begin.")
