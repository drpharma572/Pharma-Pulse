# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import tempfile
import os
from urllib.parse import quote

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="PharmaPulse DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Model")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# Temporary directory for shared visualization files
TEMP_DIR = tempfile.gettempdir()

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file:
    # Load file
    try:
        if uploaded_file.name.endswith(("xlsx", "xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded: {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()

    # Display first 10 rows
    st.subheader("### 📋 Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    st.markdown(f"**Numeric Columns:** {numeric_cols}")
    st.markdown(f"**Categorical Columns:** {categorical_cols}")

    # -----------------------------
    # Quick Filters
    # -----------------------------
    st.subheader("### 🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        unique_vals = filtered_df[col].dropna().unique().tolist()
        if unique_vals:
            sel = st.multiselect(f"Filter {col}", options=unique_vals, default=unique_vals)
            filtered_df = filtered_df[filtered_df[col].isin(sel)]
    st.write(f"Filtered Rows: {filtered_df.shape[0]}")

    # -----------------------------
    # Data Visualizations
    # -----------------------------
    st.subheader("### 🎨 Data Visualizations")
    chart_images = []

    # Bar chart
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols, key="bar_cat")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=cat_col, y=num_col, data=filtered_df, ci=None, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig)
        # Save figure
        bar_buf = io.BytesIO()
        fig.savefig(bar_buf, format='png')
        chart_images.append(bar_buf)

    # Histogram
    if numeric_cols:
        hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(filtered_df[hist_col].dropna(), bins=10, kde=False, ax=ax)
        ax.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig)
        hist_buf = io.BytesIO()
        fig.savefig(hist_buf, format='png')
        chart_images.append(hist_buf)

    # Scatter plot
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis for Scatter plot", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis for Scatter plot", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots(figsize=(8, 5))
        hue_col = categorical_cols[0] if categorical_cols else None
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col],
                        hue=filtered_df[hue_col] if hue_col else None, ax=ax)
        ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
        st.pyplot(fig)
        scatter_buf = io.BytesIO()
        fig.savefig(scatter_buf, format='png')
        chart_images.append(scatter_buf)

    # Pie chart
    if categorical_cols:
        pie_col = st.selectbox("Categorical column for Pie chart", categorical_cols, key="pie_col")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie Chart of {pie_col}")
        st.pyplot(fig)
        pie_buf = io.BytesIO()
        fig.savefig(pie_buf, format='png')
        chart_images.append(pie_buf)

    # Line chart
    if numeric_cols:
        line_col = st.selectbox("Numeric column for Line chart", numeric_cols, key="line_col")
        fig, ax = plt.subplots(figsize=(8, 5))
        filtered_df[line_col].plot.line(ax=ax)
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig)
        line_buf = io.BytesIO()
        fig.savefig(line_buf, format='png')
        chart_images.append(line_buf)

    # Correlation heatmap
    if numeric_cols:
        st.subheader("Correlation Heatmap")
        corr = filtered_df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
        corr_buf = io.BytesIO()
        fig.savefig(corr_buf, format='png')
        chart_images.append(corr_buf)

    # Pictogram
    if categorical_cols:
        pict_col = st.selectbox("Column for Pictogram", categorical_cols, key="pict_col")
        counts = filtered_df[pict_col].value_counts()
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(counts.index, counts.values)
        ax.set_title(f"Pictogram of {pict_col}")
        st.pyplot(fig)
        pict_buf = io.BytesIO()
        fig.savefig(pict_buf, format='png')
        chart_images.append(pict_buf)

    # -----------------------------
    # Shareable Link (Visualizations)
    # -----------------------------
    st.subheader("### 🔗 Shareable Link for Visualizations")
    zip_path = os.path.join(TEMP_DIR, f"visualizations_{uploaded_file.name.split('.')[0]}.zip")
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for i, buf in enumerate(chart_images):
            buf.seek(0)
            zipf.writestr(f"chart_{i+1}.png", buf.read())
    st.markdown(f"[Click here to download all charts as ZIP]({quote(zip_path)})", unsafe_allow_html=True)
