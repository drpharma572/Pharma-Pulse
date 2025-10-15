import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib_venn import venn2, venn3
from scipy.integrate import simps
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Advanced Research Dashboard", layout="wide")
st.title("📊 Advanced Research Dashboard")

# -------------------
# Subscription Setup
# -------------------
subscribers = ["user1@example.com", "user2@example.com"]
user_email = st.text_input("Enter your email for premium features:")
is_subscriber = user_email in subscribers

if is_subscriber:
    st.success("✅ Subscriber verified. Premium features unlocked.")
elif user_email:
    st.warning("⚠️ Not a subscriber. Premium features are locked.")

# -------------------
# Upload Excel
# -------------------
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet = st.selectbox("Select sheet", sheet_names) if len(sheet_names) > 1 else sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet)
    st.success(f"✅ Loaded sheet: {sheet}")

    # -------------------
    # Data Preview & Filters
    # -------------------
    st.subheader("Data Preview & Filters")
    st.dataframe(df)

    filters = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            vals = df[col].unique().tolist()
            selected = st.multiselect(f"Filter {col}", vals, default=vals)
            filters[col] = selected
        else:
            min_val, max_val = float(df[col].min()), float(df[col].max())
            selected = st.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
            filters[col] = selected

    filtered_df = df.copy()
    for col, val in filters.items():
        if df[col].dtype == 'object':
            filtered_df = filtered_df[filtered_df[col].isin(val)]
        else:
            filtered_df = filtered_df[(filtered_df[col] >= val[0]) & (filtered_df[col] <= val[1])]
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    # -------------------
    # Summary Statistics
    # -------------------
    st.subheader("Dynamic Summary Statistics")
    st.write(filtered_df.describe(include='all'))

    # -------------------
    # Charts Tabs
    # -------------------
    tab_free, tab_premium = st.tabs(["Free Charts", "Premium Charts"])

    # Free Charts
    with tab_free:
        st.write("📈 Free Charts: Bar & Pie")
        numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
        categorical_cols = filtered_df.select_dtypes(exclude='number').columns.tolist()

        if categorical_cols and numeric_cols:
            x_col = st.selectbox("Bar Chart: Categorical Column", categorical_cols, key="free_bar_x")
            y_col = st.selectbox("Bar Chart: Numeric Column", numeric_cols, key="free_bar_y")
            bar_data = filtered_df.groupby(x_col)[y_col].mean()
            fig, ax = plt.subplots()
            ax.bar(bar_data.index, bar_data.values, color="orange", edgecolor="black")
            ax.set_title(f'{y_col} by {x_col}')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        if categorical_cols:
            pie_col = st.selectbox("Pie Chart: Categorical Column", categorical_cols, key="free_pie")
            pie_data = filtered_df[pie_col].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.set_title(f'Pie Chart of {pie_col}')
            st.pyplot(fig)

    # Premium Charts
    with tab_premium:
        if is_subscriber:
            st.write("🔒 Premium Charts")
            numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
            categorical_cols = filtered_df.select_dtypes(exclude='number').columns.tolist()

            # Histogram
            if numeric_cols:
                hist_col = st.selectbox("Histogram", numeric_cols, key="hist")
                fig, ax = plt.subplots()
                ax.hist(filtered_df[hist_col], bins=20, color="green", edgecolor="black")
                ax.set_title(f'Histogram of {hist_col}')
                st.pyplot(fig)

            # Scatter Plot
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("Scatter X", numeric_cols, key="scatter_x")
                y_col = st.selectbox("Scatter Y", numeric_cols, key="scatter_y")
                fig, ax = plt.subplots()
                ax.scatter(filtered_df[x_col], filtered_df[y_col], color="purple")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f'Scatter Plot: {y_col} vs {x_col}')
                st.pyplot(fig)

            # Line Plot / Dose-Response
            if len(numeric_cols) >= 2:
                dose_col = st.selectbox("Dose/Time Column", numeric_cols, key="dose_x")
                response_col = st.selectbox("Response Column", numeric_cols, key="response_y")
                fig, ax = plt.subplots()
                ax.plot(filtered_df[dose_col], filtered_df[response_col], marker='o', color='blue')
                ax.set_title(f'Dose-Response / Line Plot: {response_col} vs {dose_col}')
                st.pyplot(fig)

                # AUC
                auc = simps(filtered_df[response_col], filtered_df[dose_col])
                st.info(f"Area Under Curve (AUC): {auc:.2f}")

            # Venn Diagram
            if len(categorical_cols) >= 2:
                venn_sets = [set(filtered_df[c].dropna()) for c in categorical_cols[:3]]
                fig, ax = plt.subplots()
                if len(venn_sets) == 2:
                    venn2(venn_sets, set_labels=categorical_cols[:2], ax=ax)
                else:
                    venn3(venn_sets, set_labels=categorical_cols[:3], ax=ax)
                st.pyplot(fig)

            # Funnel Plot
            if len(numeric_cols) >= 2:
                effect_col = st.selectbox("Effect Size Column", numeric_cols, key="effect")
                se_col = st.selectbox("Standard Error Column", numeric_cols, key="se")
                fig, ax = plt.subplots()
                ax.scatter(filtered_df[se_col], filtered_df[effect_col], color='red')
                ax.set_xlabel("Standard Error")
                ax.set_ylabel("Effect Size")
                ax.set_title("Funnel Plot")
                st.pyplot(fig)

            # PDF / CSV Downloads
            if st.button("Download PDF Report"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Premium Research Dashboard Report", ln=True, align='C')
                pdf.ln(10)
                pdf.multi_cell(0, 10, txt=str(filtered_df.describe(include='all')))
                pdf_file = BytesIO()
                pdf.output(pdf_file)
                pdf_file.seek(0)
                st.download_button("Download PDF", data=pdf_file, file_name="report.pdf", mime="application/pdf")

            filtered_csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=filtered_csv, file_name="filtered_data.csv", mime="text/csv")

        else:
            st.info("Subscribe to unlock premium charts, PDF & CSV downloads, and advanced analytics.")

    # -------------------
    # Research Results & Conclusion
    # -------------------
    st.subheader("Research Results & Conclusion")
    st.text_area("Results", placeholder="Summarize your results here...")
    st.text_area("Conclusion", placeholder="Summarize your conclusion here...")
