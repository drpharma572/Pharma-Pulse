# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# ------------------------
# App Config
# ------------------------
st.set_page_config(page_title="PharmaPulse Visualizer", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------
# File Upload
# ------------------------
uploaded_file = st.file_uploader(
    "Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ Loaded: {uploaded_file.name}")

    # ------------------------
    # Detect Numeric and Categorical Columns
    # ------------------------
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    st.subheader("📋 Data Overview")
    st.write("**Numeric Columns:**", numeric_cols)
    st.write("**Categorical Columns:**", categorical_cols)

    # ------------------------
    # Filters
    # ------------------------
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        options = st.multiselect(f"Filter {col}", df[col].unique(), default=df[col].unique())
        filtered_df = filtered_df[filtered_df[col].isin(options)]

    st.write(f"Filtered Rows: {len(filtered_df)}")

    # ------------------------
    # Data Visualizations
    # ------------------------
    chart_images = []

    # Bar Chart
    st.subheader("Bar Chart")
    if numeric_cols and categorical_cols:
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select Categorical Column", categorical_cols, key="bar_cat")
        bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("bar.png", fig))

    # Histogram (without KDE)
    st.subheader("Histogram")
    if numeric_cols:
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[hist_col].dropna(), bins=15, kde=False, ax=ax)  # KDE removed
        ax.set_title(f"Distribution of {hist_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("histogram.png", fig))

    # Scatter Plot
    st.subheader("Scatter Plot")
    if numeric_cols:
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("scatter.png", fig))

    # Pie Chart
    st.subheader("Pie Chart")
    if categorical_cols:
        pie_col = st.selectbox("Select Categorical Column", categorical_cols, key="pie")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("pie.png", fig))

    # Line Chart
    st.subheader("Line Chart")
    if numeric_cols:
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line_col")
        fig, ax = plt.subplots()
        sns.lineplot(data=filtered_df[line_col], ax=ax)
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("line.png", fig))

    # Correlation Heatmap
    st.subheader("Correlation Heatmap")
    if numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("heatmap.png", fig))

    # ------------------------
    # Share & Print Options
    # ------------------------
    st.subheader("🖨 Print & Share Visualization")

    # Function to convert chart to image bytes
    def save_chart(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return buf.getvalue()

    # Save all chart images
    image_buffers = [save_chart(fig) for _, fig in chart_images]

    # Print DataFrame
    if st.button("Print Data"):
        st.dataframe(filtered_df)

    # Shareable link (as base64)
    csv_bytes = filtered_df.to_csv(index=False).encode()
    b64_csv = base64.b64encode(csv_bytes).decode()
    share_link = f"data:text/csv;base64,{b64_csv}"
    st.markdown(f"[📤 Share CSV via Link]({share_link})", unsafe_allow_html=True)
