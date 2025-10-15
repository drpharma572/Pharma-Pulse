import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

# --------------------------
# Streamlit App Configuration
# --------------------------
st.set_page_config(page_title="PharmaPulse DUS Analyzer", layout="wide")
st.title("💊 PharmaPulse: Drug Utilization Study Dashboard")

# --------------------------
# File Upload
# --------------------------
uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx", "xls"])

# --------------------------
# Helper function: PDF creation
# --------------------------
def create_pdf(dataframe, result_text, chart_images):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cover Page
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "PharmaPulse DUS Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "This report includes data analysis, visual insights, and summary conclusions.")
    pdf.ln(10)

    # Sample Data
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Sample Data Preview:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    sample_data = dataframe.head(10).to_string(index=False)
    pdf.multi_cell(0, 8, sample_data)
    pdf.ln(10)

    # Results Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Results and Conclusions:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, result_text)
    pdf.ln(10)

    # Charts Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Data Visualization:", ln=True)
    pdf.ln(5)

    for img in chart_images:
        pdf.image(img, w=160)
        pdf.ln(10)

    # Save to BytesIO buffer
    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    return pdf_buffer

# --------------------------
# Main Analysis Function
# --------------------------
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")

    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    # --------------------------
    # Basic descriptive stats
    # --------------------------
    st.subheader("📊 Data Analysis")
    st.write("Basic Statistics:")
    st.write(df.describe(include='all'))

    # --------------------------
    # Continuous variable chart
    # --------------------------
    st.subheader("📈 Continuous Variable: Age Distribution")
    if "Age" in df.columns:
        fig, ax = plt.subplots()
        df["Age"].plot(kind="hist", bins=20, ax=ax)
        ax.set_title("Age Distribution")
        ax.set_xlabel("Age")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    else:
        st.warning("⚠️ Column 'Age' not found in dataset.")

    # --------------------------
    # Categorical analysis
    # --------------------------
    st.subheader("🧠 Drug Utilization by Drug Name")
    if "Drug" in df.columns:
        fig2, ax2 = plt.subplots()
        df["Drug"].value_counts().plot(kind="bar", ax=ax2)
        ax2.set_title("Drug Utilization Pattern")
        ax2.set_xlabel("Drug Name")
        ax2.set_ylabel("Count")
        st.pyplot(fig2)
    else:
        st.warning("⚠️ Column 'Drug' not found in dataset.")

    # --------------------------
    # Summary text
    # --------------------------
    result_text = (
        f"Total Records: {len(df)}\n\n"
        f"Number of Unique Drugs: {df['Drug'].nunique() if 'Drug' in df.columns else 'N/A'}\n\n"
        "Conclusion:\n"
        "The dataset shows significant variability in drug utilization. "
        "Continuous variables like Age are represented accurately, "
        "and categorical data like Drug distribution provides insight into prescribing trends."
    )

    # --------------------------
    # Save charts to memory
    # --------------------------
    chart_images = []
    for fig in [plt.figure(1), plt.figure(2)]:
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        chart_images.append(img_buffer)

    # --------------------------
    # Create PDF and Download
    # --------------------------
    pdf_file = create_pdf(df, result_text, chart_images)

    st.download_button(
        label="📥 Download Full Report (PDF)",
        data=pdf_file,
        file_name="PharmaPulse_Report.pdf",
        mime="application/pdf"
    )
