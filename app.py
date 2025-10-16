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

# Temporary directory for shared files
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
    # Descriptive Statistics
    # -----------------------------
    st.subheader("### 📈 Descriptive Statistics (Auto)")
    st.dataframe(filtered_df.describe(include='all').T)

    # -----------------------------
    # Data Visualizations
    # -----------------------------
    st.subheader("### 🎨 Data Visualizations")

    # Strip plot for continuous vs categorical
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select numeric column for Strip chart", numeric_cols)
        cat_col = st.selectbox("Select categorical column for Strip chart", categorical_cols)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.stripplot(x=cat_col, y=num_col, data=filtered_df, jitter=True, ax=ax)
        ax.set_title(f"{num_col} by {cat_col} (Strip plot for continuous values)")
        st.pyplot(fig)

    # Histogram
    if numeric_cols:
        hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(filtered_df[hist_col].dropna(), bins=10, kde=True, ax=ax)
        ax.set_title(f"Histogram of {hist_col}")
        st.pyplot(fig)

    # Scatter plot
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis for Scatter plot", numeric_cols)
        y_col = st.selectbox("Y-axis for Scatter plot", numeric_cols)
        fig, ax = plt.subplots(figsize=(8, 5))
        hue_col = categorical_cols[0] if categorical_cols else None
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col],
                        hue=filtered_df[hue_col] if hue_col else None, ax=ax)
        ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
        st.pyplot(fig)

    # Pie chart
    if categorical_cols:
        pie_col = st.selectbox("Categorical column for Pie chart", categorical_cols)
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie Chart of {pie_col}")
        st.pyplot(fig)

    # Line chart
    if numeric_cols:
        line_col = st.selectbox("Numeric column for Line chart", numeric_cols)
        fig, ax = plt.subplots(figsize=(8, 5))
        filtered_df[line_col].plot.line(ax=ax)
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig)

    # Correlation heatmap
    if numeric_cols:
        st.subheader("Correlation Heatmap (Numeric columns)")
        corr = filtered_df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Pictogram
    if categorical_cols:
        pict_col = st.selectbox("Column for Pictogram representation", categorical_cols)
        counts = filtered_df[pict_col].value_counts()
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(counts.index, counts.values)
        ax.set_title(f"Pictogram of {pict_col}")
        st.pyplot(fig)

    # -----------------------------
    # Print / View Filtered Data
    # -----------------------------
    st.subheader("### 🖨️ Print / View Filtered Data")
    st.dataframe(filtered_df)

    # -----------------------------
    # Shareable Link (Large Files)
    # -----------------------------
    st.subheader("### 🔗 Shareable Link for Filtered Data")
    # Save filtered data to temp CSV file
    safe_filename = f"filtered_data_{uploaded_file.name.split('.')[0]}.csv"
    temp_file_path = os.path.join(TEMP_DIR, safe_filename)
    filtered_df.to_csv(temp_file_path, index=False)

    # Generate link
    st.markdown(f"[Click here to download filtered data]({quote(temp_file_path)})", unsafe_allow_html=True)
