import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io

st.set_page_config(page_title="PharmaPulse — Research Dashboard", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")
st.write("Upload your Excel data, explore visualizations, and auto-generate research results & conclusions.")

# -------------------- File Upload --------------------
uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully: {uploaded_file.name}")

    # -------------------- Data Preview --------------------
    st.subheader("### 📋 Data Preview")
    st.dataframe(df.head())

    # -------------------- Summary Statistics --------------------
    st.subheader("### 📈 Summary Statistics")
    st.write(df.describe(include="all"))

    # -------------------- Data Filters --------------------
    st.subheader("### 🎯 Data Filters")
    selected_columns = st.multiselect("Select columns to filter", df.columns.tolist())
    filtered_df = df.copy()

    for col in selected_columns:
        unique_vals = df[col].dropna().unique().tolist()
        selected_vals = st.multiselect(f"Filter values for {col}", unique_vals)
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

    st.write(f"Filtered Data — {len(filtered_df)} rows remaining.")
    st.dataframe(filtered_df.head())

    # -------------------- Visualization Section --------------------
    st.subheader("### 📊 Data Visualization")

    chart_type = st.selectbox(
        "Select chart type",
        ["Bar Chart", "Pie Chart", "Histogram", "Scatter Plot", "Line Chart", "Area Chart"]
    )

    numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = filtered_df.select_dtypes(exclude=["number"]).columns.tolist()

    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column", numeric_cols)
        cat_col = st.selectbox("Select categorical column", categorical_cols)

        fig, ax = plt.subplots(figsize=(8, 5))
        if chart_type == "Bar Chart":
            sns.barplot(x=cat_col, y=num_col, data=filtered_df, ax=ax, estimator=sum)
        elif chart_type == "Pie Chart":
            pie_data = filtered_df[cat_col].value_counts()
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
        elif chart_type == "Histogram":
            sns.histplot(filtered_df[num_col], kde=True, ax=ax)
        elif chart_type == "Scatter Plot":
            sns.scatterplot(x=cat_col, y=num_col, data=filtered_df, ax=ax)
        elif chart_type == "Line Chart":
            filtered_df.groupby(cat_col)[num_col].mean().plot(ax=ax, marker="o", linestyle="-")
        elif chart_type == "Area Chart":
            filtered_df.groupby(cat_col)[num_col].mean().plot.area(ax=ax, alpha=0.6)

        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.warning("Please ensure your dataset has both numeric and categorical columns.")

    # -------------------- Auto Result & Conclusion --------------------
    st.subheader("### 🧾 Auto-Generated Results & Conclusion")

    result_text = f"""
    **Results:**
    - Total records analyzed: {len(filtered_df)}
    - Numeric columns identified: {', '.join(numeric_cols) if numeric_cols else 'None'}
    - Categorical columns identified: {', '.join(categorical_cols) if categorical_cols else 'None'}
    - The dataset shows variation across {len(categorical_cols)} categorical and {len(numeric_cols)} numeric parameters.

    **Conclusion:**
    The data suggests notable trends in the selected variables. The visualization aids interpretation and supports rational analysis of prescribing patterns or research parameters within pharmacological studies.
    """

    st.markdown(result_text)

    # -------------------- PDF Generation --------------------
    st.subheader("### 📑 Generate PDF Report")

    def create_pdf(dataframe, text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="PharmaPulse Report", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=text)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt="Sample Data Preview:", ln=True)

        pdf.set_font("Arial", size=10)
        sample_text = dataframe.head().to_string(index=False)
        pdf.multi_cell(0, 10, txt=sample_text)

        pdf.output("report.pdf")

    if st.button("🧾 Generate PDF"):
        create_pdf(filtered_df, result_text)
        with open("report.pdf", "rb") as f:
            st.download_button("⬇️ Download PDF Report", f, file_name="PharmaPulse_Report.pdf")
else:
    st.info("📥 Please upload an Excel (.xlsx) file to begin.")
