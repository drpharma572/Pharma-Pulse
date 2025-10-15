# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io
import numpy as np

st.set_page_config(page_title="📊 PharmaPulse Dashboard", layout="wide")
st.title("📊 PharmaPulse — Interactive Research Data Dashboard")

# ------------------------
# Upload Excel File
# ------------------------
uploaded_file = st.file_uploader("Upload an Excel file (XLSX only)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ File loaded successfully: {uploaded_file.name}")
        st.subheader("📋 Data Preview")
        st.dataframe(df)

        # ------------------------
        # Data Summary
        # ------------------------
        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe(include='all').T)

        # ------------------------
        # Filters
        # ------------------------
        st.subheader("🎯 Data Filters")
        filtered_df = df.copy()
        filter_cols = st.multiselect("Select columns to filter", df.columns.tolist())
        for col in filter_cols:
            options = st.multiselect(f"Filter {col}", df[col].unique().tolist())
            if options:
                filtered_df = filtered_df[filtered_df[col].isin(options)]
        st.write(f"Filtered Data — {len(filtered_df)} rows remaining.")

        # ------------------------
        # Charts
        # ------------------------
        st.subheader("📊 Data Visualization")
        chart_images = []

        numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = filtered_df.select_dtypes(exclude=np.number).columns.tolist()

        # ---- Bar Charts ----
        if numeric_cols and categorical_cols:
            num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols)
            cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
            bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(x=cat_col, y=num_col, data=bar_data, ci=None, ax=ax)
            ax.set_title(f"{num_col} by {cat_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ---- Pie Charts ----
        if categorical_cols:
            pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, index=0)
            pie_data = filtered_df[pie_col].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
            ax.set_title(f"Pie Chart of {pie_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ---- Histogram ----
        if numeric_cols:
            hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols, index=0)
            fig, ax = plt.subplots()
            ax.hist(filtered_df[hist_col].dropna(), bins=10, color="skyblue", edgecolor="black")
            ax.set_title(f"Histogram of {hist_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ---- Line Plot ----
        if numeric_cols:
            line_col = st.selectbox("Select numeric column for Line chart", numeric_cols, index=0)
            fig, ax = plt.subplots()
            ax.plot(filtered_df[line_col].dropna(), marker='o', linestyle='-', color="green")
            ax.set_title(f"Line Chart of {line_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ---- Scatter Plot ----
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("Select X column for Scatter Plot", numeric_cols, index=0)
            y_col = st.selectbox("Select Y column for Scatter Plot", numeric_cols, index=1)
            fig, ax = plt.subplots()
            ax.scatter(filtered_df[x_col], filtered_df[y_col], color='orange')
            ax.set_title(f"Scatter Plot: {x_col} vs {y_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ---- Area Plot ----
        if numeric_cols:
            area_col = st.selectbox("Select numeric column for Area chart", numeric_cols, index=0)
            fig, ax = plt.subplots()
            ax.fill_between(range(len(filtered_df[area_col])), filtered_df[area_col], color="lightgreen", alpha=0.6)
            ax.set_title(f"Area Chart of {area_col}")
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            chart_images.append(buf)
            plt.close(fig)

        # ------------------------
        # Auto-generate Results & Conclusion
        # ------------------------
        st.subheader("📄 Research Results")
        result_text = f"Data contains {len(filtered_df)} rows and {len(filtered_df.columns)} columns.\n"
        result_text += f"Columns summary:\n{filtered_df.describe(include='all').T}\n"
        st.text_area("Results", result_text, height=200)

        st.subheader("✅ Conclusion")
        conclusion_text = f"The dataset shows trends across {len(filtered_df.columns)} variables.\nCharts indicate patterns in numerical and categorical data."
        st.text_area("Conclusion", conclusion_text, height=150)

        # ------------------------
        # PDF Generation
        # ------------------------
        st.subheader("📥 Download Report as PDF")

        def create_pdf(dataframe, results, conclusion, chart_buffers):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Page 1: Sample data
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "📂 Sample Data Preview", ln=True)
            pdf.set_font("Arial", "", 10)
            for i in range(min(10, len(dataframe))):  # preview first 10 rows
                row = dataframe.iloc[i].to_dict()
                row_text = " | ".join([f"{k}: {v}" for k, v in row.items()])
                pdf.multi_cell(0, 5, row_text)
            pdf.ln(5)

            # Page 2: Results
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "📄 Results", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 6, results)

            # Page 3: Conclusion
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "✅ Conclusion", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 6, conclusion)

            # Pages: Charts
            for buf in chart_buffers:
                pdf.add_page()
                pdf.image(buf, x=15, y=25, w=180)

            buffer = io.BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            return buffer

        if st.button("Generate PDF"):
            pdf_file = create_pdf(filtered_df, result_text, conclusion_text, chart_images)
            st.download_button("Download PDF Report", data=pdf_file, file_name="PharmaPulse_Report.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
