import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Excel Viewer", layout="wide")
st.title("📊 Interactive Excel Viewer")
st.write("Upload your Excel file below to view and analyze data interactively.")

# Upload Excel
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded: {uploaded_file.name}")

    # Preview data
    st.subheader("Preview of Data")
    st.dataframe(df)

    # Column filter
    st.subheader("Filter Data by Column")
    col_to_filter = st.selectbox("Select column to filter", df.columns.tolist())
    val_to_filter = st.selectbox("Select value", df[col_to_filter].unique())
    filtered_df = df[df[col_to_filter] == val_to_filter]
    st.dataframe(filtered_df)

    # Quick histogram for numeric columns
    st.subheader("Quick Charts")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        col_to_plot = st.selectbox("Select numeric column to plot", numeric_cols)
        fig, ax = plt.subplots()
        sns.histplot(df[col_to_plot], kde=True, bins=20, ax=ax)
        ax.set_title(f'Histogram of {col_to_plot}')
        st.pyplot(fig)

    # Download filtered data
    st.subheader("Download Filtered Data")
    filtered_csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=filtered_csv, file_name="filtered_data.csv", mime="text/csv")

