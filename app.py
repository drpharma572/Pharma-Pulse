# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

st.set_page_config(page_title="PharmaPulse — Digital DUS Model", layout="wide")
st.title("📊 PharmaPulse — Digital Drug Utilization Study (DUS) Model")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")
st.write("A digital visualization platform for hospital-based DUS — Govt. & Private institutions.")

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"],
    help="Limit 200MB per file"
)

# -----------------------------
# Load file and detect numeric/categorical columns
# -----------------------------
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ Loaded: {uploaded_file.name}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    st.subheader("📋 Data Overview")
    st.write(f"**Numeric Columns:** {numeric_cols}")
    st.write(f"**Categorical Columns:** {categorical_cols}")

    # -----------------------------
    # Filters
    # -----------------------------
    st.subheader("🧩 Apply Filters (Optional)")
    filtered_df = df.copy()
    for col in categorical_cols:
        options = st.multiselect(f"Filter {col}", df[col].unique(), default=None)
        if options:
            filtered_df = filtered_df[filtered_df[col].isin(options)]

    st.write(f"Filtered Rows: {filtered_df.shape[0]}")

    # -----------------------------
    # Descriptive stats
    # -----------------------------
    st.subheader("📈 Descriptive Statistics")
    st.dataframe(filtered_df.describe(include="all"))

    # -----------------------------
    # Charts
    # -----------------------------
    st.subheader("🎨 Data Visualizations")

    # Bar Chart — only categorical x-axis
    if categorical_cols and numeric_cols:
        st.markdown("**Bar Chart**")
        cat_col = st.selectbox("Select Categorical Column for Bar Chart", categorical_cols)
        num_col = st.selectbox("Select Numeric Column for Bar Chart", numeric_cols)
        if cat_col and num_col:
            fig, ax = plt.subplots()
            sns.barplot(x=cat_col, y=num_col, data=filtered_df, ci=None)
            ax.set_title(f"{num_col} by {cat_col}")
            st.pyplot(fig)

    # Histogram — for numeric columns
    if numeric_cols:
        st.markdown("**Histogram**")
        hist_col = st.selectbox("Select Numeric Column for Histogram", numeric_cols, key="hist")
        if hist_col:
            fig, ax = plt.subplots()
            ax.hist(filtered_df[hist_col].dropna(), bins=15, color="skyblue", edgecolor="black")
            ax.set_title(f"Histogram of {hist_col}")
            st.pyplot(fig)

    # Scatter Plot
    if len(numeric_cols) >= 2:
        st.markdown("**Scatter Plot**")
        x_col = st.selectbox("Select X-axis Numeric Column", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Select Y-axis Numeric Column", numeric_cols, key="scatter_y")
        fig, ax = plt.subplots()
        ax.scatter(filtered_df[x_col], filtered_df[y_col], alpha=0.7, color="green")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        st.pyplot(fig)

    # Pie Chart
    if categorical_cols:
        st.markdown("**Pie Chart**")
        pie_col = st.selectbox("Select Categorical Column for Pie Chart", categorical_cols, key="pie")
        pie_data = filtered_df[pie_col].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie Chart of {pie_col}")
        st.pyplot(fig)

    # Line Chart — numeric
    if numeric_cols:
        st.markdown("**Line Chart**")
        line_col = st.selectbox("Select Numeric Column for Line Chart", numeric_cols, key="line")
        fig, ax = plt.subplots()
        ax.plot(filtered_df[line_col].dropna(), marker='o')
        ax.set_title(f"Line Chart of {line_col}")
        st.pyplot(fig)

    # Correlation Heatmap
    if len(numeric_cols) >= 2:
        st.markdown("**Correlation Heatmap (Numeric Columns)**")
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(filtered_df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # -----------------------------
    # Auto-generated results & conclusion
    # -----------------------------
    st.subheader("🧠 Auto-generated Results & Conclusion")
    st.text_area("Results", value="Results summary will be generated based on uploaded data.", height=100)
    st.text_area("Conclusion", value="Conclusion summary will be generated based on uploaded data.", height=100)

    # -----------------------------
    # Shareable link generation
    # -----------------------------
    st.subheader("🔗 Generate Shareable Link")
    csv_bytes = filtered_df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv_bytes).decode()
    shareable_url = f"{st.secrets.get('APP_URL', 'https://your-app-url.streamlit.app')}?data={b64}"
    st.markdown(f"[Click here to share your data]({shareable_url})", unsafe_allow_html=True)
