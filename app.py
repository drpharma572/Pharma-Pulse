import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.integrate import simps
from fpdf import FPDF
from io import BytesIO

# App config
st.set_page_config(page_title="PharmaPulse Dashboard", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")

# ------------------------
# File upload
# ------------------------
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])

# ------------------------
# Function to create PDF
# ------------------------
def create_pdf(dataframes, results_list, chart_images):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, df in enumerate(dataframes):
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Data Preview - File {i+1}", ln=True)
        # Preview sample data (first 5 rows)
        pdf.set_font("Arial", "", 12)
        sample = df.head().to_string(index=False)
        pdf.multi_cell(0, 5, sample)
        
        pdf.ln(5)
        # Add results
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "📈 Results", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 6, results_list[i])
        
        # Add charts
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "📊 Charts", ln=True)
        for img in chart_images[i]:
            pdf.image(img, w=180)
    
    # Add conclusion
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "🎯 Conclusion", ln=True)
    pdf.set_font("Arial", "", 12)
    for i, res in enumerate(results_list):
        pdf.multi_cell(0, 6, f"File {i+1} Conclusion:\n{res}\n\n")
    
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ------------------------
# Analysis
# ------------------------
if uploaded_file:
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")
    df = pd.read_excel(uploaded_file)
    
    # Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head())
    
    # Summary stats using NumPy
    st.subheader("📈 Summary Statistics")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    stats_dict = {}
    for col in numeric_cols:
        stats_dict[col] = {
            "mean": np.mean(df[col]),
            "median": np.median(df[col]),
            "std_dev": np.std(df[col]),
            "min": np.min(df[col]),
            "max": np.max(df[col]),
            "AUC": simps(df[col].dropna()) if len(df[col].dropna())>1 else "N/A"
        }
    st.table(pd.DataFrame(stats_dict).T)
    
    # Charts
    st.subheader("📊 Data Visualization")
    chart_images = []
    
    # Bar chart
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols)
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
        bar_data = df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, estimator=None, ci=None, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig)
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="PNG")
        img_buffer.seek(0)
        chart_images.append([img_buffer])
    
    # Pie chart
    if categorical_cols:
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="pie")
        pie_data = df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig2)
        img_buffer2 = BytesIO()
        fig2.savefig(img_buffer2, format="PNG")
        img_buffer2.seek(0)
        chart_images[-1].append(img_buffer2)
    
    # Histogram for numeric columns
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.hist(df[col].dropna(), bins=10, color="skyblue", edgecolor="black")
        ax.set_title(f"Histogram of {col}")
        st.pyplot(fig)
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="PNG")
        img_buffer.seek(0)
        chart_images[-1].append(img_buffer)
    
    # Generate Results text
    results_text = ""
    for col in numeric_cols:
        results_text += f"{col} - Mean: {np.mean(df[col]):.2f}, Median: {np.median(df[col]):.2f}, Std Dev: {np.std(df[col]):.2f}, AUC: {simps(df[col].dropna()) if len(df[col].dropna())>1 else 'N/A'}\n"
    
    st.subheader("🎯 Auto-generated Results & Conclusion")
    st.text_area("Results & Conclusion", value=results_text, height=200)
    
    # PDF Download
    st.download_button(
        label="📄 Download Full Report as PDF",
        data=create_pdf([df], [results_text], [chart_images]),
        file_name="PharmaPulse_Report.pdf",
        mime="application/pdf"
    )
