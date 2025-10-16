# app.py
# PharmaPulse — Pro DUS Dashboard with auto-stats, visualizations, PDF & share link

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile, os, uuid, json
from io import BytesIO
from datetime import datetime

# stats
from scipy import stats
from sklearn.linear_model import LinearRegression

# PDF: fpdf2 interface
from fpdf import FPDF

# HTTP upload for share link
import requests

# -----------------------
# Helpers: effect sizes
# -----------------------
def cohen_d(x, y):
    x = np.asarray(x.dropna())
    y = np.asarray(y.dropna())
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return np.nan
    sdx = x.std(ddof=1)
    sdy = y.std(ddof=1)
    pooled = np.sqrt(((nx-1)*sdx**2 + (ny-1)*sdy**2) / (nx+ny-2))
    if pooled == 0:
        return np.nan
    return (x.mean() - y.mean()) / pooled

def eta_squared(groups):
    allvals = np.concatenate(groups)
    grand_mean = allvals.mean()
    ss_between = sum(len(g)*(g.mean()-grand_mean)**2 for g in groups)
    ss_total = ((allvals - grand_mean)**2).sum()
    if ss_total == 0:
        return np.nan
    return ss_between / ss_total

def cramers_v(table):
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.sum()
    if n == 0:
        return np.nan
    r, k = table.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))

# -----------------------
# PDF class (footer)
# -----------------------
class SafePDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100,100,100)
        self.cell(0, 10, "pharmapulsebydrk", 0, 0, "C")

def pdf_bytes_from_parts(title_text, author, results_text, conclusion_text, chart_paths, df_preview):
    pdf = SafePDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Title page
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 12, title_text, ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"By: {author}", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", align="C")

    # Results
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Results", ln=True)
    pdf.set_font("Arial", "", 11)
    try:
        pdf.multi_cell(0, 7, results_text)
    except Exception:
        pdf.multi_cell(0, 7, results_text.encode('latin-1', errors='replace').decode('latin-1'))

    # Charts pages
    for path in chart_paths:
        if not os.path.exists(path):
            continue
        pdf.add_page()
        # ensure image fits width
        try:
            pdf.image(path, x=10, y=20, w=190)
        except Exception:
            # as fallback just print filename
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 6, f"[Image: {os.path.basename(path)}]")

    # Data preview
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Sample Data Preview (first 10 rows)", ln=True)
    pdf.set_font("Courier", "", 9)
    preview = df_preview.to_string(index=False)
    try:
        pdf.multi_cell(0, 6, preview)
    except Exception:
        pdf.multi_cell(0, 6, preview.encode('latin-1', errors='replace').decode('latin-1'))

    # Conclusion
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Conclusion", ln=True)
    pdf.set_font("Arial", "", 11)
    try:
        pdf.multi_cell(0, 7, conclusion_text)
    except Exception:
        pdf.multi_cell(0, 7, conclusion_text.encode('latin-1', errors='replace').decode('latin-1'))

    # Export bytes
    s = pdf.output(dest='S')
    if isinstance(s, str):
        out = s.encode('latin-1', errors='replace')
    else:
        out = s
    return out

# -----------------------
# Utility: save matplotlib fig -> temp png path
# -----------------------
def save_fig_temp(fig):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches='tight')
    plt.close(fig)
    tmp.close()
    return tmp.name

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="PharmaPulse Pro DUS", layout="wide")
st.title("PharmaPulse — Pro DUS Research Dashboard")
st.write("Upload Excel(.xlsx). App auto-detects variables, runs sensible tests, makes publication-style figures and a PDF report. 👇")

uploaded = st.file_uploader("Upload Excel file (XLSX)", type=["xlsx"])
if not uploaded:
    st.info("Upload an Excel file to begin. Keep column names tidy (Age, Gender, Drug, Dose, Duration etc.).")
    st.stop()

try:
    df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Failed to read Excel file: {e}")
    st.stop()

st.success(f"Loaded: {uploaded.name}")
st.subheader("Data preview (first 10 rows)")
st.dataframe(df.head(10))

# Clean column names
df.columns = [str(c) for c in df.columns]

# auto detect types
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object','category']).columns.tolist()

st.markdown(f"**Detected numeric columns:** {numeric_cols}")
st.markdown(f"**Detected categorical columns:** {categorical_cols}")

# Sidebar controls for user override
st.sidebar.header("Analysis overrides (optional)")
author_name = st.sidebar.text_input("Author name for report", value="Dr. K")
title_text = st.sidebar.text_input("Report title", value="PharmaPulse Research Report")
# choose columns
sel_num_for_tests = st.sidebar.selectbox("Pick numeric column for tests (or leave blank)", [None] + numeric_cols, index=0)
sel_cat_for_tests = st.sidebar.selectbox("Pick categorical column for tests (or leave blank)", [None] + categorical_cols, index=0)
sel_num_x = st.sidebar.selectbox("Numeric X (for correlation/regression) (opt)", [None] + numeric_cols, index=0)
sel_num_y = st.sidebar.selectbox("Numeric Y (for correlation/regression) (opt)", [None] + numeric_cols, index=0)

# Filtering UI (simple)
st.subheader("Quick Filters")
filters = {}
for col in st.multiselect("Choose columns to filter (optional)", df.columns.tolist(), max_selections=3):
    vals = df[col].dropna().unique().tolist()
    sel = st.multiselect(f"Filter {col}", vals, default=vals)
    filters[col] = sel
    df = df[df[col].isin(sel)]

st.write(f"After filters: {len(df)} rows")

# Prepare results & charts
results_lines = []
chart_paths = []

# Descriptive statistics
st.subheader("Descriptive statistics (auto)")
desc = df.describe(include='all').T
st.dataframe(desc)

# Clean continuous columns (avoid integer-coded categories misread as continuous)
# We try to detect if a numeric column is actually categorical encoded (few unique)
real_numeric = []
for c in numeric_cols:
    if df[c].nunique() <= 10 and df[c].dtype.kind in 'iu':  # integers with few unique -> might be categorical
        # treat as categorical candidate (leave in numeric but warn)
        pass
    real_numeric.append(c)
# use real_numeric as numeric_cols for plotting
if real_numeric:
    numeric_for_plot = real_numeric
else:
    numeric_for_plot = numeric_cols

# -------------------------
# Visualizations (pro set)
# -------------------------
st.subheader("Visualizations")

# 1) Correlation heatmap if multiple numeric
if len(numeric_for_plot) >= 2:
    st.markdown("**Correlation heatmap (numeric variables)**")
    corr = df[numeric_for_plot].corr(method='pearson')
    fig = plt.figure(figsize=(6,5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu_r', vmin=-1, vmax=1)
    st.pyplot(fig)
    chart_paths.append(save_fig_temp(fig))

# 2) For a chosen numeric & categorical, show bar, box, violin, pictogram, histogram
if sel_num_for_tests and sel_cat_for_tests:
    num = sel_num_for_tests
    cat = sel_cat_for_tests
    st.markdown(f"**Distribution of {num} by {cat}**")

    # Bar (aggregate mean)
    bar_data = df.groupby(cat)[num].mean().reset_index().sort_values(by=num, ascending=False)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=num, y=bar_data[cat], data=bar_data, ci=None, orient='h', palette='viridis', ax=ax1)
    ax1.set_xlabel(f"Mean {num}")
    ax1.set_ylabel(cat)
    st.pyplot(fig1)
    chart_paths.append(save_fig_temp(fig1))

    # Box + Violin
    fig2, ax2 = plt.subplots()
    sns.boxplot(x=cat, y=num, data=df, ax=ax2)
    sns.violinplot(x=cat, y=num, data=df, inner=None, color='0.9', ax=ax2)
    ax2.set_title("Box + Violin")
    st.pyplot(fig2)
    chart_paths.append(save_fig_temp(fig2))

    # Histogram (clean continuous handling)
    fig3, ax3 = plt.subplots()
    ax3.hist(df[num].dropna(), bins='auto', edgecolor='black', color='skyblue')
    ax3.set_title(f"Histogram of {num}")
    st.pyplot(fig3)
    chart_paths.append(save_fig_temp(fig3))

    # Pictogram-style: represent counts by small squares (one square per N)
    st.markdown("**Pictogram (approx)**")
    counts = df[cat].value_counts().nlargest(6)
    max_count = counts.max()
    # create a pictogram by plotting small square markers in rows
    fig4, ax4 = plt.subplots(figsize=(6, max(2, len(counts)*0.5)))
    y_pos = np.arange(len(counts))
    ax4.barh(y_pos, counts.values, color='lightcoral')
    ax4.set_yticks(y_pos); ax4.set_yticklabels(counts.index)
    ax4.set_xlabel("Count")
    ax4.set_title("Pictogram-like bar (counts)")
    st.pyplot(fig4)
    chart_paths.append(save_fig_temp(fig4))

# 3) Scatter / line / area if two numeric chosen
if sel_num_x and sel_num_y:
    xcol = sel_num_x
    ycol = sel_num_y
    st.markdown(f"**Scatter and Trend: {ycol} vs {xcol}**")
    sub = df[[xcol, ycol]].dropna()
    if len(sub) >= 3:
        fig5, ax5 = plt.subplots()
        ax5.scatter(sub[xcol], sub[ycol], alpha=0.6)
        # regression line
        lr = LinearRegression(); lr.fit(sub[[xcol]], sub[ycol])
        xs = np.linspace(sub[xcol].min(), sub[xcol].max(), 100)
        ax5.plot(xs, lr.predict(xs.reshape(-1,1)), color='red', linewidth=1)
        ax5.set_xlabel(xcol); ax5.set_ylabel(ycol)
        st.pyplot(fig5)
        chart_paths.append(save_fig_temp(fig5))

        # Line (time-series-like) if index is ordered
        fig6, ax6 = plt.subplots()
        ax6.plot(sub[xcol].values, sub[ycol].values, marker='o')
        ax6.set_xlabel(xcol); ax6.set_ylabel(ycol)
        ax6.set_title("Line Plot (ordered pairs)")
        st.pyplot(fig6)
        chart_paths.append(save_fig_temp(fig6))

# 4) Pie chart for a chosen categorical
if sel_cat_for_tests:
    st.markdown(f"**Pie chart for {sel_cat_for_tests}**")
    pc = df[sel_cat_for_tests].value_counts().nlargest(8)
    figp, axp = plt.subplots()
    axp.pie(pc.values, labels=pc.index, autopct="%1.1f%%", startangle=90)
    axp.axis('equal')
    st.pyplot(figp)
    chart_paths.append(save_fig_temp(figp))

# -------------------------
# Statistical testing logic
# -------------------------
st.subheader("Automatic statistical tests (selected)")

# 1) numeric-numeric correlation/regression
if sel_num_x and sel_num_y:
    sub = df[[sel_num_x, sel_num_y]].dropna()
    if len(sub) >= 3:
        r, p_r = stats.pearsonr(sub[sel_num_x], sub[sel_num_y])
        results_lines.append(f"Pearson correlation between {sel_num_x} & {sel_num_y}: r={r:.3f}, p={p_r:.4f}")
        slope, intercept, r_val, p_lin, stderr = stats.linregress(sub[sel_num_x], sub[sel_num_y])
        results_lines.append(f"Linear regression: slope={slope:.4f}, intercept={intercept:.4f}, R={r_val:.3f}, p={p_lin:.4f}")
    else:
        results_lines.append("Not enough pairs for correlation/regression.")

# 2) categorical-categorical chi-square (if sel_cat_for_tests and another categorical exists)
if sel_cat_for_tests:
    other = None
    other_candidates = [c for c in categorical_cols if c != sel_cat_for_tests]
    if other_candidates:
        other = other_candidates[0]
        table = pd.crosstab(df[sel_cat_for_tests].fillna("NA"), df[other].fillna("NA"))
        if table.size > 0:
            chi2, p, dof, expected = stats.chi2_contingency(table)
            cv = cramers_v(table.values)
            results_lines.append(f"Chi-square: {sel_cat_for_tests} vs {other}: chi2={chi2:.3f}, p={p:.4f}, dof={dof}; Cramer's V={cv:.3f}")
        else:
            results_lines.append(f"Chi-square: insufficient data for {sel_cat_for_tests} vs {other}.")

# 3) numeric vs categorical -> t-test or ANOVA
if sel_num_for_tests and sel_cat_for_tests:
    groups = [grp.dropna() for _, grp in df.groupby(sel_cat_for_tests)[sel_num_for_tests]]
    if len(groups) == 2:
        # Welch t-test
        g1 = groups[0]; g2 = groups[1]
        if len(g1) >= 2 and len(g2) >= 2:
            tstat, p = stats.ttest_ind(g1, g2, equal_var=False, nan_policy='omit')
            d = cohen_d(g1, g2)
            results_lines.append(f"T-test ({sel_num_for_tests} by {sel_cat_for_tests}): t={tstat:.3f}, p={p:.4f}, Cohen's d={d:.3f}")
    elif len(groups) > 2:
        valid = [g for g in groups if len(g) >= 2]
        if len(valid) >= 2:
            fstat, p = stats.f_oneway(*valid)
            eta2 = eta_squared(valid)
            results_lines.append(f"ANOVA: {sel_num_for_tests} by {sel_cat_for_tests}: F={fstat:.3f}, p={p:.4f}, eta²={eta2:.3f}")
    else:
        results_lines.append("Not enough groups for t-test/ANOVA.")

# Fallback autos if nothing selected: run a sensible default
if not (sel_num_for_tests or sel_cat_for_tests or sel_num_x or sel_num_y):
    # pick top correlation pair if exists
    if len(numeric_for_plot) >= 2:
        best = None; best_r = 0
        for i in range(len(numeric_for_plot)):
            for j in range(i+1, len(numeric_for_plot)):
                a = numeric_for_plot[i]; b = numeric_for_plot[j]
                sub = df[[a,b]].dropna()
                if len(sub) >= 3:
                    r, p = stats.pearsonr(sub[a], sub[b])
                    if abs(r) > best_r:
                        best_r = abs(r); best = (a,b,r,p)
        if best:
            a,b,r,p = best
            results_lines.append(f"Auto-correlation chosen: {a} vs {b}: r={r:.3f}, p={p:.4f}")

# assemble results and show
results_text = "\n".join(results_lines) if results_lines else "No tests were run (choose columns in the sidebar to run tests)."
st.text_area("Results", value=results_text, height=220)

# auto conclusion (basic)
conclusion_text = "Auto-conclusion: The results above summarize main associations and effect sizes. Interpret in clinical context; data quality checks recommended."
st.text_area("Conclusion", value=conclusion_text, height=140)

# Show generated charts inline
if chart_paths:
    st.subheader("Generated charts")
    for p in chart_paths:
        st.image(p, use_column_width=True)

# -------------------------
# PDF & Share link handling
# -------------------------
st.subheader("Report & Share")

if st.button("Generate PDF report"):
    try:
        pdf_bytes = pdf_bytes_from_parts(title_text, author_name, results_text, conclusion_text, chart_paths, df.head(10))
        st.success("PDF generated in memory. Use Download or Create Share Link.")
        st.session_state['last_pdf'] = pdf_bytes  # store in session
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# Download button (works if PDF generated)
if 'last_pdf' in st.session_state:
    pdf_data = st.session_state['last_pdf']
    st.download_button("Download PDF", data=pdf_data, file_name="PharmaPulse_Report.pdf", mime="application/pdf")

# Share via file.io (anonymous), create public link (one-time host)
st.markdown("**Create a public shareable link (uploads PDF to file.io — temporary host).**")
if st.button("Create Share Link (upload to file.io)"):
    if 'last_pdf' not in st.session_state:
        st.warning("Generate PDF first.")
    else:
        try:
            files = {'file': ('PharmaPulse_Report.pdf', st.session_state['last_pdf'], 'application/pdf')}
            r = requests.post("https://file.io/?expires=7d", files=files, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if j.get('success'):
                    link = j.get('link') or j.get('download_link') or j.get('url') or j.get('file')
                    st.success("Share link created (temporary host). Copy & share:")
                    st.code(link)
                else:
                    st.error("Upload failed: " + json.dumps(j))
            else:
                st.error(f"Upload failed, status {r.status_code}")
        except Exception as e:
            st.error(f"Could not upload to file.io: {e}")
            st.info("Fallback: Download the PDF and share manually (or host on Google Drive/Dropbox).")

# cleanup temp chart files on session end - best effort
def cleanup(paths):
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
        except:
            pass

cleanup(chart_paths)
