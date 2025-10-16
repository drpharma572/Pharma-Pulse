# PharmaPulse — Digital DUS Visualization
# Developed by Dr. K | PharmaPulseByDrK

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tempfile
import zipfile
from io import BytesIO
from datetime import datetime
import numpy as np

# Optional libraries
try:
    from matplotlib_venn import venn2, venn3
except ImportError:
    pass

st.set_page_config(page_title="PharmaPulse — DUS Visualizer", layout="wide")

st.title("📊 PharmaPulse — Digital DUS Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")
st.write("Upload an Excel/CSV file and get interactive visualizations.")

# ------------------------
# File Upload
# ------------------------
uploaded_file = st.file_uploader("Upload Excel (.xlsx/.xls) or CSV file", type=["xlsx", "xls", "csv"])
if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success(f"✅ Loaded: {uploaded_file.name}")

    # ------------------------
    # Show Data Preview
    # ------------------------
    st.subheader("📋 Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    # Detect columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    st.write(f"**Numeric Columns:** {numeric_cols}")
    st.write(f"**Categorical Columns:** {categorical_cols}")

    # ------------------------
    # Filters
    # ------------------------
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        unique_vals = df[col].dropna().unique().tolist()
        selected = st.multiselect(f"Filter {col}", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

    st.write(f"Filtered Rows: {filtered_df.shape[0]}")

    # ------------------------
    # Visualizations
    # ------------------------
    st.subheader("🎨 Data Visualizations")
    chart_images = []

    # Function to save chart to BytesIO
    def save_chart(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return buf

    # Bar Chart
    if numeric_cols and categorical_cols:
        st.markdown("**Bar Chart**")
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select Categorical Column", categorical_cols, key="bar_cat")
        bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("bar_chart.png", save_chart(fig)))

    # Histogram
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[hist_col].dropna(), kde=True, bins=15, ax=ax)
        ax.set_title(f"Distribution of {hist_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("histogram.png", save_chart(fig)))

    # Scatter Plot
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("scatter.png", save_chart(fig)))

    # Pie Chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select Categorical Column", categorical_cols, key="pie_col")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("pie_chart.png", save_chart(fig)))

    # Line Chart
    if numeric_cols:
        st.markdown("**Line Chart**")
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line_col")
        fig, ax = plt.subplots()
        ax.plot(filtered_df[line_col].values)
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("line_chart.png", save_chart(fig)))

    # Correlation Heatmap
    if numeric_cols:
        st.markdown("**Correlation Heatmap**")
        corr = filtered_df[numeric_cols].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("correlation.png", save_chart(fig)))

    # ------------------------
    # Print Data option
    # ------------------------
    st.subheader("🖨 Print Filtered Data")
    st.dataframe(filtered_df)

    # ------------------------
    # Shareable Link Option
    # ------------------------
    st.subheader("🔗 Generate Shareable Link")
    if st.button("Generate ZIP & Link"):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "visualizations.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                # Save all charts into zip
                for name, buf in chart_images:
                    zipf.writestr(name, buf.read())

            st.info("Charts ZIP created! Please upload to your preferred cloud (e.g., Google Drive, OneDrive) and share the link below.")
            st.text_input("Shareable Link:", value="", key="share_link")
