# app.py
st.set_page_config(page_title="PharmaPulse", page_icon="💊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stToolbar"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

st.set_page_config(page_title="PharmaPulse Visualizer", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

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

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    st.subheader("📋 Data Overview")
    st.write("**Numeric Columns:**", numeric_cols)
    st.write("**Categorical Columns:**", categorical_cols)

    # Filters
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        options = st.multiselect(f"Filter {col}", df[col].unique(), default=df[col].unique())
        filtered_df = filtered_df[filtered_df[col].isin(options)]

    st.write(f"Filtered Rows: {len(filtered_df)}")

    chart_images = []

    # ------------------------
    # Comparison Bar Chart (Two numeric variables)
    # ------------------------
    st.subheader("Bar Chart (Comparison)")
    if len(numeric_cols) >= 2:
        bar_x = st.selectbox("Select first numeric column", numeric_cols, key="bar_x")
        bar_y = st.selectbox("Select second numeric column", numeric_cols, key="bar_y")
        fig, ax = plt.subplots()
        ax.bar(range(len(filtered_df)), filtered_df[bar_x], alpha=0.6, label=bar_x)
        ax.bar(range(len(filtered_df)), filtered_df[bar_y], alpha=0.6, label=bar_y)
        ax.set_title(f"Comparison: {bar_x} vs {bar_y}")
        ax.set_xlabel("Index")
        ax.set_ylabel("Values")
        ax.legend()
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("bar_compare.png", fig))

    # ------------------------
    # Simple Bar Chart (Numeric vs Categorical)
    # ------------------------
    st.subheader("Simple Bar Chart (Numeric vs Categorical)")
    if numeric_cols and categorical_cols:
        simple_num = st.selectbox("Select numeric column", numeric_cols, key="simple_num")
        simple_cat = st.selectbox("Select categorical column", categorical_cols, key="simple_cat")
        fig, ax = plt.subplots(figsize=(10,5))
        simple_data = filtered_df.groupby(simple_cat)[simple_num].mean().sort_values()
        simple_data.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title(f"{simple_num} by {simple_cat}")
        ax.set_ylabel(simple_num)
        ax.set_xlabel(simple_cat)
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("bar_simple.png", fig))

    # ------------------------
    # Histogram Comparison
    # ------------------------
    st.subheader("Histogram (Comparison)")
    if len(numeric_cols) >= 2:
        hist_x = st.selectbox("Select first numeric column", numeric_cols, key="hist_x")
        hist_y = st.selectbox("Select second numeric column", numeric_cols, key="hist_y")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[hist_x].dropna(), bins=15, color="blue", alpha=0.6, label=hist_x, ax=ax)
        sns.histplot(filtered_df[hist_y].dropna(), bins=15, color="red", alpha=0.6, label=hist_y, ax=ax)
        ax.set_title(f"Histogram Comparison: {hist_x} vs {hist_y}")
        ax.legend()
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("hist_compare.png", fig))

    # ------------------------
    # Line Chart Comparison
    # ------------------------
    st.subheader("Line Chart (Comparison)")
    if len(numeric_cols) >= 2:
        line_x = st.selectbox("Select first numeric column", numeric_cols, key="line_x")
        line_y = st.selectbox("Select second numeric column", numeric_cols, key="line_y")
        fig, ax = plt.subplots()
        ax.plot(filtered_df[line_x].values, label=line_x)
        ax.plot(filtered_df[line_y].values, label=line_y)
        ax.set_title(f"Line Chart Comparison: {line_x} vs {line_y}")
        ax.set_xlabel("Index")
        ax.set_ylabel("Values")
        ax.legend()
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("line_compare.png", fig))

    # Scatter Plot
    st.subheader("Scatter Plot")
    if len(numeric_cols) >= 2:
        scatter_x = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        scatter_y = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=filtered_df[scatter_x], y=filtered_df[scatter_y], ax=ax)
        ax.set_title(f"{scatter_y} vs {scatter_x}")
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

    # Correlation Heatmap
    st.subheader("Correlation Heatmap")
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig, use_container_width=True)
        chart_images.append(("heatmap.png", fig))

    # ------------------------
    # Share & Print Visualization Only
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
