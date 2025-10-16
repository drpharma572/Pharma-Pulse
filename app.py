# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

st.set_page_config(page_title="PharmaPulse DUS Dashboard", layout="wide")
st.title("📊 PharmaPulse — Digital DUS Data Visualization")
st.markdown("**Developed by Dr. K | PharmaPulseByDrK**")

# ------------------------
# File upload
# ------------------------
uploaded_file = st.file_uploader("Upload Excel file (.xlsx) for visualization", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)
st.success(f"✅ Loaded: {uploaded_file.name}")

# ------------------------
# Detect numeric & categorical columns
# ------------------------
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

st.subheader("### Data preview (first 10 rows)")
st.dataframe(df.head(10))
st.write(f"**Numeric columns:** {numeric_cols}")
st.write(f"**Categorical columns:** {categorical_cols}")

# ------------------------
# Filters
# ------------------------
st.subheader("### Filters (Optional)")
filtered_df = df.copy()
for col in categorical_cols:
    options = st.multiselect(f"Filter {col}", options=df[col].unique(), default=df[col].unique())
    if options:
        filtered_df = filtered_df[filtered_df[col].isin(options)]
st.write(f"After filters: {filtered_df.shape[0]} rows")

# ------------------------
# Charts
# ------------------------
st.subheader("### Visualizations")
chart_images = []

def save_chart(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    return buf

# 1️⃣ Bar chart (numeric by category)
if numeric_cols and categorical_cols:
    num_col = st.selectbox("Select numeric column for Bar chart", numeric_cols, key="bar_num")
    cat_col = st.selectbox("Select categorical column for Bar chart", categorical_cols, key="bar_cat")
    bar_data = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(x=cat_col, y=num_col, data=bar_data, ax=ax)
    ax.set_title(f"{num_col} by {cat_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 2️⃣ Histogram (numeric)
if numeric_cols:
    hist_col = st.selectbox("Select numeric column for Histogram", numeric_cols, key="hist_num")
    fig, ax = plt.subplots()
    ax.hist(filtered_df[hist_col], bins=10, color='skyblue', edgecolor='black')
    ax.set_title(f"Histogram of {hist_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 3️⃣ Pie chart (categorical)
if categorical_cols:
    pie_col = st.selectbox("Select categorical column for Pie chart", categorical_cols, key="pie_cat")
    pie_data = filtered_df[pie_col].value_counts()
    fig, ax = plt.subplots()
    ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%")
    ax.set_title(f"Pie chart of {pie_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 4️⃣ Scatter plot
if len(numeric_cols) >= 2:
    x_col = st.selectbox("Select X-axis numeric column for Scatter", numeric_cols, key="scatter_x")
    y_col = st.selectbox("Select Y-axis numeric column for Scatter", numeric_cols, key="scatter_y")
    fig, ax = plt.subplots()
    sns.scatterplot(x=filtered_df[x_col], y=filtered_df[y_col], ax=ax)
    ax.set_title(f"Scatter plot: {y_col} vs {x_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 5️⃣ Line chart
if numeric_cols:
    line_col = st.selectbox("Select numeric column for Line chart", numeric_cols, key="line_num")
    fig, ax = plt.subplots()
    ax.plot(filtered_df[line_col], marker='o')
    ax.set_title(f"Line chart of {line_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 6️⃣ Area chart
if numeric_cols:
    area_col = st.selectbox("Select numeric column for Area chart", numeric_cols, key="area_num")
    fig, ax = plt.subplots()
    ax.fill_between(range(len(filtered_df[area_col])), filtered_df[area_col], color='lightgreen', alpha=0.5)
    ax.set_title(f"Area chart of {area_col}")
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# 7️⃣ Correlation heatmap
if numeric_cols:
    st.subheader("Correlation Heatmap")
    corr = filtered_df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)
    chart_images.append(save_chart(fig))

# ------------------------
# Shareable link
# ------------------------
st.subheader("### Share your dashboard")
def get_table_download_link(df):
    """Generates a shareable download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">📥 Download filtered data CSV</a>'

st.markdown(get_table_download_link(filtered_df), unsafe_allow_html=True)
st.info("You can share this CSV link with colleagues or departments securely.")

st.success("✅ Dashboard ready. All charts and filters are interactive, shareable, and suitable for DUS reporting.")
