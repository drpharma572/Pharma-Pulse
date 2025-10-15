import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF

# ==============================
# APP CONFIG
# ==============================
st.set_page_config(page_title="PharmaPulse Research Dashboard", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")
st.write("Upload your Excel data, explore visualizations, and auto-generate research results & conclusions.")

# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])
if not uploaded_file:
    st.warning("Please upload an Excel file to continue.")
    st.stop()

# ==============================
# LOAD DATA
# ==============================
try:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📋 Data Preview")
st.dataframe(df.head())

# ==============================
# BASIC STATS
# ==============================
st.subheader("📈 Summary Statistics")
st.write(df.describe(include="all"))

# ==============================
# FILTERS
# ==============================
st.subheader("🎯 Data Filters")
filter_cols = st.multiselect("Select columns to filter", df.columns.tolist())
filtered_df = df.copy()
for col in filter_cols:
    unique_vals = df[col].dropna().unique()
    selected_vals = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

st.write(f"Filtered Data — {filtered_df.shape[0]} rows remaining.")
st.dataframe(filtered_df)

# ==============================
# CHARTS SECTION
# ==============================
st.subheader("📊 Data Visualization")

chart_tabs = st.tabs(["Bar Chart", "Pie Chart", "Histogram", "Scatter Plot", "Line Chart", "Area Chart"])

# Bar Chart
with chart_tabs[0]:
    numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
    categorical_cols = filtered_df.select_dtypes(exclude="number").columns.tolist()

    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select categorical column", categorical_cols, key="bar_cat")
        fig, ax = plt.subplots()
        try:
            sns.barplot(x=cat_col, y=num_col, data=filtered_df, ax=ax, errorbar=None)
        except Exception:
            ax.bar(filtered_df[cat_col].astype(str), filtered_df[num_col])
        ax.set_title(f"{num_col} by {cat_col}")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("No suitable numeric and categorical columns found.")

# Pie Chart
with chart_tabs[1]:
    categorical_cols = filtered_df.select_dtypes(exclude="number").columns.tolist()
    if categorical_cols:
        pie_col = st.selectbox("Select column for Pie Chart", categorical_cols, key="pie")
        pie_data = filtered_df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Distribution of {pie_col}")
        st.pyplot(fig2)
    else:
        st.info("No categorical columns available for Pie Chart.")

# Histogram
with chart_tabs[2]:
    if numeric_cols:
        hist_col = st.selectbox("Select column for Histogram", numeric_cols, key="hist")
        fig3, ax3 = plt.subplots()
        sns.histplot(filtered_df[hist_col].dropna(), bins=20, kde=False, ax=ax3)
        ax3.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig3)
    else:
        st.info("No numeric columns available for Histogram.")

# Scatter Plot
with chart_tabs[3]:
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig4, ax4 = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax4)
        ax4.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig4)
    else:
        st.info("Need at least two numeric columns for scatter plot.")

# Line Chart
with chart_tabs[4]:
    if len(numeric_cols) >= 1:
        line_col = st.selectbox("Select numeric column for Line Chart", numeric_cols, key="line")
        fig5, ax5 = plt.subplots()
        ax5.plot(filtered_df[line_col].reset_index(drop=True))
        ax5.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig5)
    else:
        st.info("No numeric data for Line Chart.")

# Area Chart
with chart_tabs[5]:
    if len(numeric_cols) >= 1:
        area_col = st.selectbox("Select numeric column for Area Chart", numeric_cols, key="area")
        fig6, ax6 = plt.subplots()
        ax6.fill_between(range(len(filtered_df[area_col].dropna())), filtered_df[area_col].dropna())
        ax6.set_title(f"Area under curve — {area_col}")
        st.pyplot(fig6)
    else:
        st.info("No numeric data for Area Chart.")

# ==============================
# AUTO RESULT & CONCLUSION
# ==============================
st.subheader("🧠 Auto-Generated Results & Conclusion")

try:
    numeric_summary = filtered_df.describe().to_dict()
    insights = []
    for col, stats in numeric_summary.items():
        mean = stats.get("mean", None)
        if mean:
            insights.append(f"• The average value of **{col}** is approximately **{mean:.2f}**.")
    st.markdown("### Results Summary")
    st.markdown("\n".join(insights))

    st.markdown("### Conclusion")
    st.write(
        "Based on the above analysis, we observe that key numerical parameters demonstrate consistent "
        "patterns across the dataset. The generated plots reveal potential correlations and variations "
        "that can guide further research interpretations."
    )
except Exception as e:
    st.warning("Unable to auto-generate results: " + str(e))

# ==============================
# EXPORT PDF REPORT
# ==============================
st.subheader("📥 Export Report")

def create_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PharmaPulse Data Summary", ln=True, align="C")

    for col in dataframe.columns:
        try:
            pdf.multi_cell(0, 8, txt=f"{col}: {dataframe[col].describe().to_dict()}")
        except Exception:
            continue

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

if st.button("Generate PDF Report"):
    pdf_file = create_pdf(filtered_df)
    st.download_button(
        label="Download PDF",
        data=pdf_file,
        file_name="PharmaPulse_Report.pdf",
        mime="application/pdf"
    )
