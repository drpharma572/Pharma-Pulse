# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import uuid

st.set_page_config(page_title="PharmaPulse DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Digital DUS & Data Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# -------------------------------
# Upload Section
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Excel/CSV file (XLSX, XLS, CSV)", 
    type=["xlsx", "xls", "csv"]
)

if uploaded_file:
    file_name = uploaded_file.name
    # Load the data
    try:
        if file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded: {file_name}")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    # -------------------------------
    # Display overview
    # -------------------------------
    st.subheader("📋 Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    st.markdown(f"**Detected numeric columns:** {numeric_cols}")
    st.markdown(f"**Detected categorical columns:** {categorical_cols}")

    # -------------------------------
    # Optional filters
    # -------------------------------
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        options = filtered_df[col].unique().tolist()
        selected = st.multiselect(f"Filter {col}", options=options, default=options)
        filtered_df = filtered_df[filtered_df[col].isin(selected)]
    st.write(f"Filtered Rows: {len(filtered_df)}")

    # -------------------------------
    # Display full data option
    # -------------------------------
    if st.checkbox("📄 Display Full Filtered Data"):
        st.dataframe(filtered_df)

    # -------------------------------
    # Descriptive statistics
    # -------------------------------
    st.subheader("📈 Descriptive Statistics")
    st.dataframe(filtered_df.describe(include='all').T)

    # -------------------------------
    # Visualization Section
    # -------------------------------
    st.subheader("🎨 Data Visualizations")

    # Bar Chart
    if numeric_cols and categorical_cols:
        st.markdown("**Bar Chart**")
        num_col = st.selectbox("Select Numeric Column", numeric_cols, key="bar_num")
        cat_col = st.selectbox("Select Categorical Column", categorical_cols, key="bar_cat")
        bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
        ax.set_title(f"{num_col} by {cat_col}")
        st.pyplot(fig)

    # Histogram
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df[hist_col], kde=False, bins=15, ax=ax)
        ax.set_title(f"Distribution of {hist_col}")
        st.pyplot(fig)

    # Scatter Plot
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig)

    # Pie Chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select Categorical Column", categorical_cols, key="pie")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig)

    # Line Chart
    if numeric_cols:
        st.markdown("**Line Chart**")
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line")
        fig, ax = plt.subplots()
        ax.plot(filtered_df[line_col])
        ax.set_title(f"Line chart of {line_col}")
        st.pyplot(fig)

    # Correlation Heatmap
    if numeric_cols:
        st.markdown("**Correlation Heatmap**")
        fig, ax = plt.subplots()
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # -------------------------------
    # Auto Results & Conclusion
    # -------------------------------
    st.subheader("🧠 Auto-generated Results & Conclusion")
    st.text_area("Results", f"Data contains {len(filtered_df)} rows and {len(filtered_df.columns)} columns.")
    st.text_area("Conclusion", "Visualizations suggest trends and distributions. Further statistical analysis recommended.")

    # -------------------------------
    # Shareable Link
    # -------------------------------
    st.subheader("📤 Generate Shareable Link")
    file_id = str(uuid.uuid4())
    APP_BASE_URL = "https://your-app-name.streamlit.app"  # replace with your deployed URL
    share_url = f"{APP_BASE_URL}?file_id={file_id}"
    st.info(f"Shareable Link: [Click Here]({share_url})")
