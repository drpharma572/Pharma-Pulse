import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Optional advanced charts for paid users
try:
    from matplotlib_venn import venn2, venn3
    from scipy.integrate import simps
except ImportError:
    pass

# ------------------------
# App config
# ------------------------
st.set_page_config(page_title="PharmaPulse Excel Viewer", layout="wide")
st.title("📊 PharmaPulse Interactive Excel Viewer")

# ------------------------
# Subscription selection
# ------------------------
subscription_status = st.radio(
    "Select Access Type:",
    ("Free User", "Paid Subscriber"),
    index=0
)

# ------------------------
# File upload
# ------------------------
if subscription_status == "Free User":
    uploaded_file = st.file_uploader("Upload a single Excel file (Free users)", type=["xlsx"])
    files_to_process = [uploaded_file] if uploaded_file else []
else:
    uploaded_file = st.file_uploader("Upload Excel file(s) for advanced analysis", type=["xlsx"], accept_multiple_files=True)
    files_to_process = uploaded_file if uploaded_file else []

# ------------------------
# Process uploaded files
# ------------------------
if files_to_process:
    dfs = [pd.read_excel(f) for f in files_to_process]
    df = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
    st.success(f"✅ {len(dfs)} file(s) loaded")

    # ------------------------
    # Preview data
    # ------------------------
    st.subheader("Preview of Data")
    st.dataframe(df)

    # ------------------------
    # Free charts: Bar & Pie
    # ------------------------
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    st.subheader("📈 Free Charts")
    chart_results = []

    if numeric_cols and categorical_cols:
        col_to_plot = st.selectbox("Select numeric column for Bar chart", numeric_cols)
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
        bar_data = df.groupby(cat_col)[col_to_plot].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=col_to_plot, data=bar_data, ax=ax)
        ax.set_title(f"{col_to_plot} by {cat_col}")
        st.pyplot(fig)

        # Record results for auto conclusion
        top_cat = bar_data.sort_values(col_to_plot, ascending=False).iloc[0]
        chart_results.append(f"Highest {col_to_plot} observed in category '{top_cat[cat_col]}' with value {top_cat[col_to_plot]}.")

    if categorical_cols:
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols)
        pie_data = df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig2)

        # Record results for auto conclusion
        most_common = pie_data.idxmax()
        chart_results.append(f"Most frequent category in '{pie_col}' is '{most_common}'.")

    # ------------------------
    # Paid subscriber features
    # ------------------------
    if subscription_status == "Paid Subscriber":
        st.subheader("🔬 Advanced Charts & Analysis")
        st.write("Advanced charts like histogram, scatter, Venn, dose-response, funnel plots, line diagrams, AUC, multiple filters, and PDF export can be implemented here.")
        st.download_button("Download CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="filtered_data.csv")

    # ------------------------
    # Auto-generated Results & Conclusion
    # ------------------------
    st.subheader("📑 Auto-Generated Research Results")
    if chart_results:
        results_text = "\n".join(chart_results)
    else:
        results_text = "No significant patterns detected from the selected charts."
    st.text_area("Results", value=results_text, height=150)

    st.subheader("📌 Auto-Generated Conclusion")
    conclusion_text = "Based on the uploaded data, the analysis indicates key trends as mentioned in Results. Further study may be required for comprehensive insights."
    st.text_area("Conclusion", value=conclusion_text, height=100)
