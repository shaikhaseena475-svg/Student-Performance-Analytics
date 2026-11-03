import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1220, #111c35, #172554);
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: #101a30;
    border-right: 1px solid #334155;
}

h1, h2, h3 {
    color: #f8fafc !important;
}

p, label {
    color: #cbd5e1;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b, #263b60);
    border: 1px solid #475569;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}

[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-size: 28px;
    font-weight: bold;
}

.stTabs [data-baseweb="tab"] {
    color: #cbd5e1;
    font-size: 16px;
}

.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #475569;
    border-radius: 12px;
}

hr {
    border-color: #475569;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div style="
    background: linear-gradient(100deg,#312e81,#1d4ed8,#0891b2);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
">
    <h1 style="color:white !important; margin:0;">
        🎓 Student Performance Dashboard
    </h1>
    <p style="color:#e0f2fe !important; font-size:17px;">
        Smart analytics for student marks, attendance and academic performance.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    return pd.read_csv("dataset/cleaned_student_data.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found! Check dataset/cleaned_student_data.csv")
    st.stop()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

if df.empty:
    st.error("Your dataset is empty.")
    st.stop()

# Required columns
required = ["Percentage", "Attendance_Percentage"]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing columns in CSV: {missing}")
    st.stop()

if "Student_Name" not in df.columns:
    df["Student_Name"] = [
        f"Student {i+1}" for i in range(len(df))
    ]

# Convert numerical columns
numeric_cols = [
    "Percentage",
    "Attendance_Percentage",
    "Python_Marks",
    "SQL_Marks",
    "Excel_Marks",
    "PowerBI_Marks"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Create performance category if missing
if "Performance" not in df.columns:
    df["Performance"] = pd.cut(
        df["Percentage"],
        bins=[-1, 39, 59, 74, 100],
        labels=["Poor", "Average", "Good", "Excellent"]
    ).astype(str)

df["Performance"] = df["Performance"].fillna("Not Classified")

df = df.dropna(
    subset=["Percentage", "Attendance_Percentage"]
)

if df.empty:
    st.error("No valid student records found.")
    st.stop()


# ---------------- SIDEBAR FILTERS ----------------

st.sidebar.markdown("# 🎛️ Dashboard Controls")
st.sidebar.write("Filter student data")

performance_options = sorted(
    df["Performance"].unique().tolist()
)

selected_performance = st.sidebar.multiselect(
    "Performance Category",
    options=performance_options,
    default=performance_options
)

attendance_min = float(df["Attendance_Percentage"].min())
attendance_max = float(df["Attendance_Percentage"].max())

if attendance_min < attendance_max:
    attendance_range = st.sidebar.slider(
        "Attendance Range (%)",
        min_value=attendance_min,
        max_value=attendance_max,
        value=(attendance_min, attendance_max)
    )
else:
    attendance_range = (attendance_min, attendance_max)

search_name = st.sidebar.text_input(
    "🔍 Search Student",
    placeholder="Enter student name..."
)

st.sidebar.divider()

st.sidebar.info(
    "🎓 Student Performance Analysis Project"
)


# Apply filters
filtered_df = df[
    (df["Performance"].isin(selected_performance)) &
    (df["Attendance_Percentage"] >= attendance_range[0]) &
    (df["Attendance_Percentage"] <= attendance_range[1])
]

filtered_df = filtered_df[
    filtered_df["Student_Name"].astype(str).str.contains(
        search_name, case=False, na=False
    )
]


# ---------------- KPI CARDS ----------------

st.markdown("## 📌 Overall Performance Overview")

c1, c2, c3, c4 = st.columns(4)

total_students = len(filtered_df)

avg_percentage = (
    filtered_df["Percentage"].mean()
    if total_students else 0
)

avg_attendance = (
    filtered_df["Attendance_Percentage"].mean()
    if total_students else 0
)

top_percentage = (
    filtered_df["Percentage"].max()
    if total_students else 0
)

with c1:
    st.metric("👨‍🎓 Total Students", total_students)

with c2:
    st.metric("📊 Average Percentage", f"{avg_percentage:.2f}%")

with c3:
    st.metric("📅 Average Attendance", f"{avg_attendance:.2f}%")

with c4:
    st.metric("🏆 Highest Percentage", f"{top_percentage:.2f}%")

st.divider()


# ---------------- EMPTY FILTER CHECK ----------------

if filtered_df.empty:
    st.warning("No students match your selected filters.")
    st.stop()


# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Analytics",
    "🏆 Top Students",
    "🤖 AI Insights",
    "📋 Student Records"
])


# ---------------- ANALYTICS TAB ----------------

with tab1:

    st.subheader("📚 Subject-wise Performance")

    subjects = [
        "Python_Marks",
        "SQL_Marks",
        "Excel_Marks",
        "PowerBI_Marks"
    ]

    available_subjects = [
        col for col in subjects if col in filtered_df.columns
    ]

    col1, col2 = st.columns(2)

    with col1:

        if available_subjects:
            subject_avg = (
                filtered_df[available_subjects]
                .mean()
                .reset_index()
            )

            subject_avg.columns = [
                "Subject", "Average Marks"
            ]

            subject_avg["Subject"] = (
                subject_avg["Subject"]
                .str.replace("_Marks", "", regex=False)
            )

            fig1 = px.bar(
                subject_avg,
                x="Subject",
                y="Average Marks",
                color="Subject",
                text_auto=".1f",
                title="Average Marks by Subject",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold
            )

            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(
                fig1, use_container_width=True
            )
        else:
            st.info("No subject marks columns found.")

    with col2:

        performance_count = (
            filtered_df["Performance"]
            .value_counts()
            .reset_index()
        )

        performance_count.columns = [
            "Performance", "Students"
        ]

        fig2 = px.pie(
            performance_count,
            names="Performance",
            values="Students",
            hole=0.55,
            title="Performance Distribution",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig2, use_container_width=True
        )

    st.divider()

    st.subheader("📊 Attendance vs Academic Performance")

    fig3 = px.scatter(
        filtered_df,
        x="Attendance_Percentage",
        y="Percentage",
        color="Performance",
        hover_name="Student_Name",
        size="Percentage",
        title="Does Attendance Affect Student Performance?",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig3, use_container_width=True
    )

    st.subheader("📉 Percentage Distribution")

    fig4 = px.histogram(
        filtered_df,
        x="Percentage",
        nbins=10,
        color="Performance",
        title="Student Marks Distribution",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig4, use_container_width=True
    )


# ---------------- TOP STUDENTS TAB ----------------

with tab2:

    st.subheader("🏆 Top 5 Performing Students")

    top5 = filtered_df.nlargest(
        5, "Percentage"
    ).copy()

    top5.insert(
        0, "Rank",
        range(1, len(top5) + 1)
    )

    st.dataframe(
        top5[
            ["Rank", "Student_Name", "Percentage", "Performance"]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📉 Students Needing Improvement")

    low5 = filtered_df.nsmallest(
        5, "Percentage"
    )

    st.dataframe(
        low5[
            ["Student_Name", "Percentage", "Performance"]
        ],
        use_container_width=True,
        hide_index=True
    )


# ---------------- AI INSIGHTS TAB ----------------

with tab3:

    st.subheader("🤖 Automated Student Performance Insights")

    if available_subjects:

        averages = filtered_df[available_subjects].mean()

        best_subject = averages.idxmax().replace(
            "_Marks", ""
        )

        weak_subject = averages.idxmin().replace(
            "_Marks", ""
        )

        col1, col2 = st.columns(2)

        with col1:
            st.success(
                f"📈 Strongest Subject: {best_subject}"
            )

        with col2:
            st.warning(
                f"📉 Subject Needing Improvement: {weak_subject}"
            )

    low_attendance = (
        filtered_df["Attendance_Percentage"] < 75
    ).sum()

    high_performers = (
        filtered_df["Percentage"] >= 75
    ).sum()

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            f"⚠️ Students with attendance below 75%: {low_attendance}"
        )

    with col2:
        st.success(
            f"🌟 Students scoring 75% or above: {high_performers}"
        )

    st.markdown("### 💡 Recommendations")

    if low_attendance > 0:
        st.write(
            "• Improve attendance through regular classes and monitoring."
        )
    else:
        st.write(
            "• All filtered students have attendance of at least 75%."
        )

    if available_subjects:
        st.write(
            f"• Arrange extra practice sessions for {weak_subject}."
        )

    st.write(
        "• Encourage high-performing students to maintain consistency."
    )

    st.caption(
        "Note: These are automated rule-based insights, not predictions from a trained AI model."
    )


# ---------------- STUDENT RECORDS TAB ----------------

with tab4:

    st.subheader("📋 Complete Student Database")

    st.write(
        f"Showing {len(filtered_df)} student records."
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Student Report",
        data=csv,
        file_name="Student_Performance_Report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="color:#94a3b8;">
        🎓 Student Performance Analytics Dashboard
    </p>
    <p style="color:#64748b; font-size:13px;">
        Developed using Python | Streamlit | Pandas | Plotly
    </p>
</div>
""", unsafe_allow_html=True)