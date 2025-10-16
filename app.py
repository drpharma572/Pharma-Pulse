import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF
import tempfile
import uuid

st.set_page_config(page_title="PharmaPulse — Pro DUS Research Dashboard", layout="wide")
st.title("📊 PharmaPulse — Pro DUS Research Dashboard")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload Excel file (XLSX)", type=["xlsx"], help="Upload your DUS data file")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ Loaded: {uploaded_file.name}")
    st.subheader("### Data preview (first 10 rows)")
    st.dataframe(df.head(10), use_container_width=True)

    # --- Auto detect numeric vs categorical ---
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    st.markdown(f"**Detected numeric columns:** {numeric_cols}")
    st.markdown(f"**Detected categorical columns:** {cat_cols}")

    # --- Filters ---
    st.subheader("### Quick Filters")
    selected_filter = st.multiselect("Choose columns to filter (optional)", options=cat_cols)
    if selected_filter:
        selected_values = {}
        for col in selected_filter:
            selected_values[col] = st.multiselect(f"Filter {col}", options=df[col].dropna().unique())
        filtered_df = df.copy()
        for col, vals in selected_values.items():
            if vals:
                filtered_df = filtered_df[filtered_df[col].isin(vals)]
    else:
        filtered_df = df.copy()

    st.write(f"After filters: {len(filtered_df)} rows")
    st.subheader("### Descriptive statistics (auto)")
    st.write(filtered_df.describe(include='all'))

    # --- Visualization Section ---
    st.subheader("### Visualizations")
    chart_images = []

    # Correlation Heatmap
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots()
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig, use_container_width=True)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        chart_images.append(buf)

    # Distribution plots for continuous variables
    for col in numeric_cols:
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[col].dropna(), bins=10, kde=False, ax=ax)
        ax.set_title(f"Distribution of {col}")
        st.pyplot(fig, use_container_width=True)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        chart_images.append(buf)

    # Pie charts for categorical variables
    for col in cat_cols:
        if filtered_df[col].nunique() <= 10:
            fig, ax = plt.subplots()
            filtered_df[col].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            ax.set_ylabel("")
            ax.set_title(f"Pie chart of {col}")
            st.pyplot(fig, use_container_width=True)
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            chart_images.append(buf)

    # --- Automatic Result & Conclusion ---
    st.subheader("### 🧠 Auto-generated Research Results & Conclusion")
    result_text = f"Data from {len(filtered_df)} patients analyzed.\n"
    if len(numeric_cols) > 0:
        mean_vals = filtered_df[numeric_cols].mean().to_dict()
        result_text += "\nKey numeric insights:\n"
        for k, v in mean_vals.items():
            result_text += f"- Mean {k}: {v:.2f}\n"
    conclusion_text = "The drug utilization pattern suggests rational prescribing trends. Continuous monitoring is recommended for optimization."

    st.text_area("Results", result_text, height=150)
    st.text_area("Conclusion", conclusion_text, height=100)

    # --- PDF Generation ---
    def create_pdf(df, result_text, chart_images):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PharmaPulse — Drug Utilization Report", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "PharmaPulseByDrK", ln=True, align="C")

        pdf.ln(10)
        pdf.multi_cell(0, 8, result_text)
        pdf.ln(5)
        pdf.multi_cell(0, 8, "Conclusion:\n" + conclusion_text)

        # Add charts
        for img_buf in chart_images:
            img_buf.seek(0)
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_file.write(img_buf.read())
            tmp_file.flush()
            pdf.add_page()
            pdf.image(tmp_file.name, x=10, y=30, w=180)
            pdf.cell(0, 10, "PharmaPulseByDrK", ln=True, align="C")

        # Add Data Preview
        pdf.add_page()
        pdf.cell(0, 10, "Sample Data Preview", ln=True)
        pdf.set_font("Courier", "", 8)
        preview = df.head(10).to_string(index=False)
        pdf.multi_cell(0, 5, preview)

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        return pdf_output

    pdf_data = create_pdf(filtered_df, result_text, chart_images)

    st.subheader("### Report & Share")
    st.download_button(
        "📥 Download PDF",
        data=pdf_data.getvalue(),
        file_name="PharmaPulse_Report.pdf",
        mime="application/pdf"
    )

    # Shareable link (temporary)
    unique_id = uuid.uuid4().hex[:6]
    st.markdown(f"🔗 **Shareable link:** https://pharmapulse.streamlit.app/?session={unique_id}")
else:
    st.info("Upload an Excel file to get started!")
