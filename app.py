# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

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

    # Bar Chart (Continuous variables handled correctly)
    st.subheader("Bar Chart")
    if numeric_cols:
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        fig, ax = plt.subplots()
        ax.bar(range(len(filtered_df)), filtered_df[num_col])  # Continuous variable, no aggregation
        ax.set_title(f"{num_col} (continuous)")
        ax.set_xlabel("Index")
        ax.set_ylabel(num_col)
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("bar.png", fig))

    # Histogram (without KDE)
    st.subheader("Histogram")
    if numeric_cols:
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist_col")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[hist_col].dropna(), bins=15, kde=False, ax=ax)
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
        ax.plot(filtered_df[line_col].values)
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("line.png", fig))

    # Correlation Heatmap
    st.subheader("Correlation Heatmap")
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("heatmap.png", fig))

    # ------------------------
    # Share & Print Graphs Only
    # ------------------------
    st.subheader("🖨 Print & Share Visualization Only")

    # Convert matplotlib figures to base64 images
    def fig_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    # Generate shareable HTML link for graphs
    img_html_list = [f'<img src="data:image/png;base64,{fig_to_base64(fig)}" width="600"><br>' 
                     for _, fig in chart_images]
    html_content = "".join(img_html_list)
    b64_html = base64.b64encode(html_content.encode()).decode()
    share_link = f"data:text/html;base64,{b64_html}"
    st.markdown(f"[📤 Share Visualization via Link]({share_link})", unsafe_allow_html=True)

    # Print all graphs inline
    if st.button("Print Graphs"):
        for _, fig in chart_images:
            st.pyplot(fig, use_container_width=True)
