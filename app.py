# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO
import tempfile

st.set_page_config(page_title="PharmaPulse — Pro DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Pro DUS Research Dashboard")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------
# Upload Excel file
# ------------------------
uploaded_file = st.file_uploader("Upload Excel file (XLSX)", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)
st.success(f"✅ Loaded: {uploaded_file.name}")

# ------------------------
# Detect numeric & categorical columns
# ------------------------
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

st.subheader("### Data preview (first 10 rows)")
st.dataframe(df.head(10))
st.write(f"**Detected numeric columns:** {numeric_cols}")
st.write(f"**Detected categorical columns:** {categorical_cols}")

# ------------------------
# Quick filters
# ------------------------
st.subheader("### Quick Filters (optional)")
filtered_df = df.copy()
for col in categorical_cols:
    options = st.multiselect(f"Filter {col}", options=df[col].unique())
    if options:
        filtered_df = filtered_df[filtered_df[col].isin(options)]
st.write(f"After filters: {filtered_df.shape[0]} rows")

# ------------------------
# Descriptive statistics
# ------------------------
st.subheader("### Descriptive statistics")
st.dataframe(filtered_df.describe(include='all').transpose())

# ------------------------
# Visualizations
# ------------------------
st.subheader("### Visualizations")
chart_images = []

def save_chart_to_buffer(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Bar chart for numeric vs categorical
if numeric_cols and categorical_cols:
    num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols)
    cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
    bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
    ax.set_title(f"{num_col} by {cat_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# Histogram for numeric
if numeric_cols:
    hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols)
    fig, ax = plt.subplots()
    ax.hist(filtered_df[hist_col], bins=10, color='skyblue', edgecolor='black')
    ax.set_title(f"Histogram of {hist_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# Pie chart for categorical
if categorical_cols:
    pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols)
    pie_data = filtered_df[pie_col].value_counts()
    fig, ax = plt.subplots()
    ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
    ax.set_title(f"Pie chart of {pie_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# Scatter plot
if len(numeric_cols) >= 2:
    x_col = st.selectbox("Select X-axis numeric column for Scatter plot", numeric_cols, key='scatter_x')
    y_col = st.selectbox("Select Y-axis numeric column for Scatter plot", numeric_cols, key='scatter_y')
    fig, ax = plt.subplots()
    sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax)
    ax.set_title(f"Scatter plot: {y_col} vs {x_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# Line chart
if numeric_cols:
    line_col = st.selectbox("Select numeric column for Line chart", numeric_cols, key='line_col')
    fig, ax = plt.subplots()
    ax.plot(filtered_df[line_col], marker='o')
    ax.set_title(f"Line chart of {line_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# Area chart
if numeric_cols:
    area_col = st.selectbox("Select numeric column for Area chart", numeric_cols, key='area_col')
    fig, ax = plt.subplots()
    ax.fill_between(range(len(filtered_df[area_col])), filtered_df[area_col], color='lightgreen', alpha=0.5)
    ax.set_title(f"Area chart of {area_col}")
    st.pyplot(fig)
    chart_images.append(save_chart_to_buffer(fig))

# ------------------------
# Auto-generate results & conclusion
# ------------------------
st.subheader("### 🧠 Auto-generated Research Results & Conclusion")
result_text = f"Results: Descriptive statistics and visualizations performed on {filtered_df.shape[0]} records.\n"
result_text += f"Numeric variables: {numeric_cols}\nCategorical variables: {categorical_cols}"
st.text_area("Results", value=result_text, height=120)

conclusion_text = "Conclusion: Findings are summarized with charts and descriptive stats. This report can be used for research publication style insights."
st.text_area("Conclusion", value=conclusion_text, height=100)

# ------------------------
# Generate PDF
# ------------------------
def create_pdf(df, results, charts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "📊 PharmaPulse — Drug Utilization Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "PharmaPulseByDrK", ln=True, align="C")
    pdf.ln(5)

    # Data preview
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Data Preview (first 10 rows)", ln=True)
    pdf.set_font("Arial", "", 10)
    preview = df.head(10).to_string(index=False)
    preview = preview.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, preview)

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Research Results", ln=True)
    pdf.set_font("Arial", "", 10)
    results_text = results.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, results_text)

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Conclusion", ln=True)
    pdf.set_font("Arial", "", 10)
    conclusion_text = conclusion.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, conclusion_text)

    # Charts
    for img_buf in charts:
        pdf.add_page()
        img_buf.seek(0)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_file.write(img_buf.read())
        tmp_file.flush()
        pdf.image(tmp_file.name, x=10, y=30, w=180)
        pdf.cell(0, 10, "PharmaPulseByDrK", ln=True, align="C")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

pdf_data = create_pdf(filtered_df, result_text, chart_images)

st.subheader("### 📄 Report & Share")
st.download_button(
    "📥 Download PDF",
    data=pdf_data.getvalue(),
    file_name="PharmaPulse_Report.pdf",
    mime="application/pdf"
)
st.info("You can share the report PDF with collaborators via any file-sharing service.")
