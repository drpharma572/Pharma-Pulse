import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io
import os

st.set_page_config(page_title="PharmaPulse — Research Dashboard", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")
st.write("Upload your Excel data, explore visualizations, and auto-generate a downloadable research report (PDF).")

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

    chart_types = ["Bar Chart", "Pie Chart", "Histogram", "Scatter Plot", "Line Chart", "Area Chart"]
    numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = filtered_df.select_dtypes(exclude=["number"]).columns.tolist()

    chart_images = []  # store chart paths

    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column", numeric_cols)
        cat_col = st.selectbox("Select categorical column", categorical_cols)

        for chart_type in chart_types:
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

            ax.set_title(f"{chart_type}: {num_col} vs {cat_col}")
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Save chart to memory
            chart_path = f"{chart_type.replace(' ', '_')}.png"
            fig.savefig(chart_path, bbox_inches="tight")
            chart_images.append(chart_path)
            plt.close(fig)

    else:
        st.warning("Please ensure your dataset has both numeric and categorical columns.")

    # -------------------- Auto Result & Conclusion --------------------
    st.subheader("### 🧾 Auto-Generated Results & Conclusion")

    result_text = f"""
    **Results:**
    - Total records analyzed: {len(filtered_df)}
    - Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
    - Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}
    - Dataset shows variation across {len(categorical_cols)} categorical and {len(numeric_cols)} numeric parameters.

    **Conclusion:**
    The data suggests consistent patterns among the chosen parameters. Generated charts visually support the relationship between categorical and numeric variables. This structured summary enhances understanding of trends and supports rational interpretation.
    """

    st.markdown(result_text)

    # -------------------- PDF Generation --------------------
    st.subheader("### 📑 Download Complete PDF Report")

    def create_pdf(dataframe, text, chart_list):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(200, 10, txt="PharmaPulse Research Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=text)
        pdf.ln(10)

        # Add all charts
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt="Charts & Visualizations", ln=True)
        pdf.ln(5)
        for img in chart_list:
            try:
                pdf.image(img, w=160)
                pdf.ln(10)
            except:
                pass

        # Add sample data
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt="Sample Data Preview", ln=True)
        pdf.set_font("Arial", size=10)
        sample_text = dataframe.head().to_string(index=False)
        pdf.multi_cell(0, 8, txt=sample_text)

        # Save to memory
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    if st.button("🧾 Generate Full PDF Report"):
        pdf_file = create_pdf(filtered_df, result_text, chart_images)
        st.download_button("⬇️ Download Complete PDF Report", pdf_file, file_name="PharmaPulse_Report.pdf")

        # Clean up temp chart files
        for img in chart_images:
            if os.path.exists(img):
                os.remove(img)
else:
    st.info("📥 Please upload an Excel (.xlsx) file to begin.")
