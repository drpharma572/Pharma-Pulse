import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import os
import pickle
import tempfile

# ------------------------
# App Config
# ------------------------
st.set_page_config(page_title="PharmaPulse — DUS Digital Model", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Model")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------
# Temp storage for shared links
# ------------------------
SHARE_DIR = "shared_files"
os.makedirs(SHARE_DIR, exist_ok=True)

# ------------------------
# Helper functions
# ------------------------
def save_session(data, charts, results, conclusion):
    file_id = str(uuid.uuid4())
    path = os.path.join(SHARE_DIR, f"{file_id}.pkl")
    with open(path, "wb") as f:
        pickle.dump({"data": data, "charts": charts, "results": results, "conclusion": conclusion}, f)
    return file_id

def load_session(file_id):
    path = os.path.join(SHARE_DIR, f"{file_id}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def generate_charts(df):
    charts = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    # Bar Chart (first numeric vs first categorical)
    if numeric_cols and categorical_cols:
        fig, ax = plt.subplots()
        bar_data = df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index()
        sns.barplot(x=categorical_cols[0], y=numeric_cols[0], data=bar_data, ax=ax)
        ax.set_title(f"{numeric_cols[0]} by {categorical_cols[0]}")
        charts["bar"] = fig

    # Histogram (first numeric)
    if numeric_cols:
        fig, ax = plt.subplots()
        df[numeric_cols[0]].plot(kind="hist", bins=10, ax=ax)
        ax.set_title(f"Histogram of {numeric_cols[0]}")
        charts["hist"] = fig

    # Pie (first categorical)
    if categorical_cols:
        fig, ax = plt.subplots()
        pie_data = df[categorical_cols[0]].value_counts()
        ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax.set_title(f"Pie Chart of {categorical_cols[0]}")
        charts["pie"] = fig

    # Scatter (first 2 numeric)
    if len(numeric_cols) >= 2:
        fig, ax = plt.subplots()
        sns.scatterplot(x=numeric_cols[0], y=numeric_cols[1], data=df, ax=ax)
        ax.set_title(f"Scatter: {numeric_cols[0]} vs {numeric_cols[1]}")
        charts["scatter"] = fig

    # Line chart (first numeric)
    if numeric_cols:
        fig, ax = plt.subplots()
        df[numeric_cols[0]].plot(kind="line", ax=ax)
        ax.set_title(f"Line Chart of {numeric_cols[0]}")
        charts["line"] = fig

    # Correlation heatmap
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots()
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        charts["heatmap"] = fig

    return charts

def auto_results(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    results = "Descriptive Summary:\n"
    if numeric_cols:
        results += df[numeric_cols].describe().to_string()
    if categorical_cols:
        results += "\n\nCategorical Counts:\n"
        results += df[categorical_cols].apply(pd.Series.value_counts).to_string()
    return results

def auto_conclusion(results_text):
    return "Auto-generated Conclusion: Review the above summary to interpret trends and patterns for research purposes."

# ------------------------
# Handle shareable links
# ------------------------
query_params = st.query_params
if "file_id" in query_params:
    file_id = query_params["file_id"][0]
    session_data = load_session(file_id)
    if session_data:
        st.success(f"📌 Loaded shared dataset: {file_id}")
        df = session_data["data"]
        charts = session_data["charts"]
        results_text = session_data["results"]
        conclusion_text = session_data["conclusion"]
    else:
        st.error("❌ Invalid or expired link.")
        df = None
else:
    df = None

# ------------------------
# Upload new file if not loaded via link
# ------------------------
if df is None:
    uploaded_file = st.file_uploader("Upload Excel/CSV file", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded: {uploaded_file.name}")
        st.dataframe(df.head(10))

        # Generate charts and results
        charts = generate_charts(df)
        results_text = auto_results(df)
        conclusion_text = auto_conclusion(results_text)

        # Save session for shareable link
        file_id = save_session(df, charts, results_text, conclusion_text)
        share_url = f"{st.get_url()}?file_id={file_id}"
        st.info(f"Shareable Link: [Click Here]({share_url})")

# ------------------------
# Display visualizations
# ------------------------
if df is not None:
    st.subheader("### 📋 Data Preview (first 10 rows)")
    st.dataframe(df.head(10))

    st.subheader("### 📈 Descriptive Statistics & Visualizations")
    for name, fig in charts.items():
        st.pyplot(fig, use_container_width=True)

    st.subheader("### 🧠 Auto-generated Results & Conclusion")
    st.text_area("Results", results_text, height=150)
    st.text_area("Conclusion", conclusion_text, height=100)
