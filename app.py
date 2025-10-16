import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# --- Page setup ---
st.set_page_config(page_title="Pharma DUS Visualizer", layout="wide")

st.title("📊 Drug Utilization Data Visualization Tool")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    st.sidebar.header("📈 Visualization Settings")
    
    # --- Variable selection ---
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["int64", "float64"]).columns.tolist()
    
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Histogram", "Line Chart"])
    
    x_axis = st.sidebar.selectbox("Select X-axis variable", df.columns)
    y_axis = st.sidebar.selectbox("Select Y-axis variable (optional for comparison)", [None] + df.columns.tolist())

    st.markdown("---")
    st.subheader("📊 Data Visualization")

    # --- Visualization section ---
    fig, ax = plt.subplots(figsize=(8, 5))

    if chart_type == "Bar Chart":
        if y_axis:
            df.groupby(x_axis)[y_axis].mean().plot(kind='bar', ax=ax)
            ax.set_ylabel(f"Average {y_axis}")
        else:
            df[x_axis].value_counts().plot(kind='bar', ax=ax)
        ax.set_title(f"{chart_type} of {x_axis}")
        st.pyplot(fig)

    elif chart_type == "Histogram":
        if y_axis:
            df[[x_axis, y_axis]].plot(kind='hist', alpha=0.6, ax=ax)
            ax.set_title(f"Histogram of {x_axis} vs {y_axis}")
        else:
            df[x_axis].plot(kind='hist', bins=10, ax=ax)
            ax.set_title(f"Histogram of {x_axis}")
        st.pyplot(fig)

    elif chart_type == "Line Chart":
        if y_axis:
            df.plot(x=x_axis, y=y_axis, kind='line', ax=ax)
            ax.set_title(f"{x_axis} vs {y_axis}")
        else:
            df[x_axis].plot(kind='line', ax=ax)
            ax.set_title(f"Line Chart of {x_axis}")
        st.pyplot(fig)

    # --- Additional fixed chart: Age vs Diagnosis ---
    if "Age" in df.columns and "Diagnosis" in df.columns:
        st.markdown("---")
        st.subheader("🧍‍♂️ Age vs Diagnosis Distribution")
        plt.figure(figsize=(8, 5))
        df.groupby("Diagnosis")["Age"].mean().plot(kind="bar")
        plt.title("Average Age per Diagnosis")
        plt.ylabel("Age")
        st.pyplot(plt)

    # --- Print and Share section ---
    st.markdown("---")
    st.subheader("🖨️ Print / Share Data Visualization")

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()

    href = f'<a href="data:file/png;base64,{b64}" download="visualization.png">📤 Download Visualization</a>'
    st.markdown(href, unsafe_allow_html=True)

else:
    st.info("👆 Please upload an Excel file to begin visualization.")
