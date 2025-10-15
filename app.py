import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------
# App configuration
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
else:
    uploaded_file = st.file_uploader(
        "Upload Excel file(s) for advanced analysis",
        type=["xlsx"],
        accept_multiple_files=True
    )

# ------------------------
# Load and preview data
# ------------------------
def load_data(files, multiple=False):
    if multiple:
        dfs = [pd.read_excel(f) for f in files]
        df_combined = pd.concat(dfs, ignore_index=True)
        return df_combined
    else:
        return pd.read_excel(files)

if uploaded_file:
    if subscription_status == "Free User":
        df = load_data(uploaded_file)
        st.success(f"✅ File loaded: {uploaded_file.name}")
    else:
        df = load_data(uploaded_file, multiple=True)
        st.success(f"✅ {len(uploaded_file)} file(s) loaded")

    # ------------------------
    # Data preview
    # ------------------------
    st.subheader("Preview of Data")
    st.dataframe(df)

    # ------------------------
    # Free charts: Bar & Pie
    # ------------------------
    st.subheader("Charts for Free Users")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    if numeric_cols and categorical_cols:
        col_to_plot = st.selectbox("Select numeric column for Bar chart", numeric_cols)
        cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols)
        bar_data = df.groupby(cat_col)[col_to_plot].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x=cat_col, y=col_to_plot, data=bar_data, ax=ax)
        ax.set_title(f"{col_to_plot} by {cat_col}")
        st.pyplot(fig)

    if categorical_cols:
        pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols)
        pie_data = df[pie_col].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
        ax2.set_title(f"Pie chart of {pie_col}")
        st.pyplot(fig2)

    # ------------------------
    # Paid subscriber features
    # ------------------------
    if subscription_status == "Paid Subscriber":
        st.subheader("Advanced Analysis (Subscribers Only)")
        st.write(
            "Features like histogram, scatter plots, dose-response, funnel plots, line diagrams, "
            "multiple filters, PDF export, and CSV download can be implemented here."
        )
        filtered_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            data=filtered_csv,
            file_name="filtered_data.csv"
        )

    # ------------------------
    # Research results & conclusion
    # ------------------------
    st.subheader("Research Results")
    st.text_area("Add your research results here...", height=100)

    st.subheader("Conclusion")
    st.text_area("Add your conclusion here...", height=100)
