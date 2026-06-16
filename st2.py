import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient
from datetime import datetime

st.set_page_config(
    page_title="Kayfa Analytics Dashboard",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS (نفس اللي عندك)
# ============================================================
st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background:
        radial-gradient(circle at top left, #2a1458 0%, transparent 30%),
        radial-gradient(circle at bottom right, #5b21b6 0%, transparent 25%),
        linear-gradient(135deg, #09090f 0%, #0f172a 100%);
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}

/* ===== REMOVE DEFAULT STREAMLIT ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(168, 85, 247, 0.3);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #d8b4fe !important;
}

/* ===== MAIN TITLES ===== */
h1 {
    color: white !important;
    font-size: 42px !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #d8b4fe !important;
    font-weight: 700 !important;
}

/* ===== GLASS CONTAINERS ===== */
.block-container {
    padding-top: 2rem;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(168,85,247,0.25);
    backdrop-filter: blur(10px);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 0 20px rgba(168,85,247,0.15);
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 25px rgba(168,85,247,0.5);
}

/* ===== RADIO BUTTONS ===== */
.stRadio > div {
    background: rgba(255,255,255,0.03);
    padding: 10px;
    border-radius: 14px;
}

/* ===== SELECT BOX ===== */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(168,85,247,0.3) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(168,85,247,0.2);
}

/* ===== PLOTLY CHARTS ===== */
.js-plotly-plot {
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 0 30px rgba(168,85,247,0.15);
    background: rgba(255,255,255,0.02);
    padding: 10px;
}

/* ===== CARDS EFFECT ===== */
div[data-testid="stVerticalBlock"] > div:has(div.js-plotly-plot) {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(168,85,247,0.15);
    border-radius: 22px;
    padding: 20px;
    backdrop-filter: blur(12px);
    margin-bottom: 20px;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #111827;
}
::-webkit-scrollbar-thumb {
    background: #7c3aed;
    border-radius: 20px;
}

/* ===== TEXT ===== */
p, label, span {
    color: #e5e7eb !important;
}

/* ===== HORIZONTAL LINE ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #a855f7, transparent);
}

/* ===== ANIMATION ===== */
@keyframes glow {
    0% { box-shadow: 0 0 5px rgba(168,85,247,0.2); }
    50% { box-shadow: 0 0 20px rgba(168,85,247,0.5); }
    100% { box-shadow: 0 0 5px rgba(168,85,247,0.2); }
}
.js-plotly-plot:hover {
    animation: glow 2s infinite;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# style_chart function
# ============================================================
def style_chart(fig, height=500):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"),
        title_font=dict(size=24),
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    return fig

# ============================================================
# MongoDB Connection
# ============================================================
@st.cache_resource
def init_connection():
    uri = "mongodb+srv://amarsayed405_db_user:MezKtw7OuqwdeWw9@cluster0.phnplnc.mongodb.net/?retryWrites=true&w=majority&connectTimeoutMS=30000&socketTimeoutMS=30000"
    return MongoClient(uri)

client = init_connection()
db = client["kayfa_analytics"]

@st.cache_data(ttl=3600)
def load_collection(collection_name):
    try:
        return pd.DataFrame(list(db[collection_name].find()))
    except Exception as e:
        st.error(f"Error loading {collection_name}: {e}")
        return pd.DataFrame()

students_master    = load_collection("students_master")
group_attendance   = load_collection("group_attendance")
course_grades      = load_collection("course_grades")
concept_failures   = load_collection("concept_failures")
at_risk_students   = load_collection("at_risk_students")
monthly_attendance = load_collection("monthly_attendance")
group_trends       = load_collection("group_trends")
score_by_type      = load_collection("score_by_type")
concept_trend      = load_collection("concept_trend")
late_vs_score      = load_collection("late_vs_score")
monthly_engagement = load_collection("monthly_engagement")

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.image("logo.png", width=200)
    st.markdown("### 🎓 Student Analytics")
    st.caption("Student Performance Dashboard")
    st.markdown("---")
    st.markdown("## 📊 Navigation")

    questions = {
        "Q1": "📈 Attendance Rate per Group",
        "Q2": "📊 Score Distribution by Assessment Type",
        "Q3": "🏆 Course Performance",
        "Q4": "📉 Attendance vs Grade Correlation",
        "Q5": "💻 Engagement vs Performance",
        "Q6": "❌ Concept Failure Rates",
        "Q7": "📈 Weakest Concept Trend",
        "Q8": "⏰ Late Submissions vs Score",
        "Q9": "📅 Monthly Attendance & Engagement",
        "Q10": "👥 Age Band Analysis",
        "Q11": "🎯 Student Segmentation",
        "Q12": "📏 Group Sizes: Stated vs Actual",
        "Q13": "🔍 Smallest Group Recommendation",
        "Q14": "🚨 Top 10 At-Risk Students",
        "Q15": "📈 Group Grade Trends Over Time"
    }

    selected_q = st.radio(
        "Select a question:",
        options=list(questions.keys()),
        format_func=lambda x: f"{x} - {questions[x]}",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("© 2026 Kayfa Analytics")

# ============================================================
# Main Content
# ============================================================
st.title("📊 Kayfa Student Analytics Dashboard")
st.markdown("---")

# ============================================================
# Q1: Attendance Rate per Group
# ============================================================
if selected_q == "Q1":
    st.header("📈 Q1: Attendance Rate per Group")

    if not group_attendance.empty:
        platform_avg = group_attendance['att_rate'].mean()

        fig = px.bar(
            group_attendance,
            x='group_id',
            y='att_rate',
            color=group_attendance['att_rate'].apply(
                lambda x: 'Below Average' if x < platform_avg else 'Above Average'
            ),
            color_discrete_map={'Below Average': '#EF4444', 'Above Average': '#10B981'},
            title='Attendance Rate per Group',
            labels={'att_rate': 'Attendance Rate (%)', 'group_id': 'Group'},
            text='att_rate'
        )

        fig.add_hline(
            y=platform_avg,
            line_dash='dash',
            line_color='#A855F7',
            annotation_text=f'Platform Avg: {platform_avg:.1f}%'
        )

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            group_attendance.rename(columns={
                'group_id': 'Group',
                'att_rate': 'Attendance Rate (%)'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ group_attendance collection is empty. Run test.py first.")

# ============================================================
# Q2: Score Distribution by Assessment Type
# ============================================================
elif selected_q == "Q2":
    st.header("📊 Q2: Score Distribution by Assessment Type")

    if not score_by_type.empty:
        fig = px.bar(
            score_by_type,
            x='type',
            y='mean',
            error_y='std',
            color='mean',
            color_continuous_scale='Teal',
            title='Average Score (%) by Assessment Type',
            labels={
                'type': 'Assessment Type',
                'mean': 'Average Score (%)',
                'count': 'Count'
            },
            text='mean',
            hover_data=['std', 'count']
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            score_by_type.rename(columns={
                'type': 'Type',
                'mean': 'Avg Score (%)',
                'std': 'Std Dev',
                'count': 'Count'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ score_by_type collection is empty. Run test.py first.")

# ============================================================
# Q3: Course Performance
# ============================================================
elif selected_q == "Q3":
    st.header("🏆 Q3: Course Performance")

    if not course_grades.empty:
        fig = px.bar(
            course_grades,
            x='course_name',
            y='mean',
            error_y='std',
            color='mean',
            color_continuous_scale='RdYlGn',
            title='Average Grade per Course',
            labels={
                'course_name': 'Course',
                'mean': 'Average Grade (%)',
                'std': 'Standard Deviation'
            },
            text='mean',
            hover_data=['std', 'count']
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            course_grades.rename(columns={
                'course_name': 'Course',
                'mean': 'Avg Grade (%)',
                'std': 'Std Dev',
                'count': 'Student Count'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ course_grades collection is empty. Run test.py first.")

# ============================================================
# Q4: Attendance vs Grade Correlation
# ============================================================
elif selected_q == "Q4":
    st.header("📉 Q4: Attendance vs Grade Correlation")

    if not students_master.empty and 'attendance_rate' in students_master.columns and 'avg_grade' in students_master.columns:
        from scipy.stats import pearsonr

        data = students_master.dropna(subset=['attendance_rate', 'avg_grade'])

        if len(data) > 1:
            corr, pval = pearsonr(data['attendance_rate'], data['avg_grade'])

            fig = px.scatter(
                data,
                x='attendance_rate',
                y='avg_grade',
                color='course_name' if 'course_name' in data.columns else None,
                trendline='ols',
                title=f'Attendance Rate vs Average Grade (r = {corr:.3f}, p = {pval:.4f})',
                labels={
                    'attendance_rate': 'Attendance Rate (%)',
                    'avg_grade': 'Average Grade (%)'
                },
                opacity=0.7
            )

            style_chart(fig)

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                data[['attendance_rate', 'avg_grade']].rename(columns={
                    'attendance_rate': 'Attendance Rate (%)',
                    'avg_grade': 'Average Grade (%)'
                }),
                use_container_width=True
            )

        else:
            st.warning("⚠️ Not enough data for correlation.")
    else:
        st.warning("⚠️ Required columns not found in students_master.")

# ============================================================
# Q5: Engagement vs Performance
# ============================================================
elif selected_q == "Q5":
    st.header("💻 Q5: Engagement vs Performance")

    if not students_master.empty:
        data = students_master.dropna(subset=['login_count', 'total_video_minutes', 'avg_grade'])

        if len(data) > 1:
            from scipy.stats import pearsonr

            r_login, p_login = pearsonr(data['login_count'], data['avg_grade'])
            r_video, p_video = pearsonr(data['total_video_minutes'], data['avg_grade'])

            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=[
                    f'Login Frequency vs Grade (r={r_login:.2f})',
                    f'Video Watch Time vs Grade (r={r_video:.2f})'
                ]
            )

            fig.add_trace(
                go.Scatter(
                    x=data['login_count'],
                    y=data['avg_grade'],
                    mode='markers',
                    name='Logins',
                    marker=dict(color='#3B82F6', opacity=0.6, size=8)
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=data['total_video_minutes'],
                    y=data['avg_grade'],
                    mode='markers',
                    name='Video Minutes',
                    marker=dict(color='#F59E0B', opacity=0.6, size=8)
                ),
                row=1, col=2
            )

            fig.update_xaxes(title_text="Login Count", row=1, col=1)
            fig.update_xaxes(title_text="Video Minutes", row=1, col=2)
            fig.update_yaxes(title_text="Average Grade (%)", row=1, col=1)
            fig.update_yaxes(title_text="Average Grade (%)", row=1, col=2)

            style_chart(fig)

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                data[['login_count', 'total_video_minutes', 'avg_grade']].rename(columns={
                    'login_count': 'Login Count',
                    'total_video_minutes': 'Video Minutes',
                    'avg_grade': 'Avg Grade (%)'
                }),
                use_container_width=True
            )

        else:
            st.warning("⚠️ Not enough data for engagement analysis.")
    else:
        st.warning("⚠️ students_master is empty.")

# ============================================================
# Q6: Concept Failure Rates
# ============================================================
elif selected_q == "Q6":
    st.header("❌ Q6: Concept Failure Rates")

    if not concept_failures.empty:
        top_n = st.slider("Show Top N Concepts", 5, 30, 15)

        top = concept_failures.nlargest(top_n, 'fail_rate')

        fig = px.bar(
            top.sort_values('fail_rate'),
            x='fail_rate',
            y='concept_name',
            orientation='h',
            color='course_name' if 'course_name' in top.columns else 'fail_rate',
            color_continuous_scale='Reds',
            title=f'Top {top_n} Concepts by Failure Rate',
            labels={
                'fail_rate': 'Failure Rate (%)',
                'concept_name': 'Concept'
            },
            text='fail_rate',
            hover_data=['course_name'] if 'course_name' in top.columns else None
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        style_chart(fig, height=600)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            concept_failures.rename(columns={
                'concept_name': 'Concept',
                'fail_rate': 'Failure Rate (%)',
                'course_name': 'Course'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ concept_failures collection is empty. Run test.py first.")

# ============================================================
# Q7: Weakest Concept Trend
# ============================================================
elif selected_q == "Q7":
    st.header("📈 Q7: Weakest Concept Trend Over Time")

    if not concept_trend.empty:
        if 'timestamp' in concept_trend.columns:
            concept_trend['timestamp'] = pd.to_datetime(concept_trend['timestamp'])

        worst_name = concept_failures.iloc[0]['concept_name'] if not concept_failures.empty else "Weakest Concept"

        fig = px.line(
            concept_trend,
            x='timestamp',
            y='score_pct',
            title=f'Weekly Avg Score Trend: "{worst_name}"',
            labels={
                'timestamp': 'Week',
                'score_pct': 'Avg Score (%)'
            },
            markers=True,
            line_shape='spline'
        )

        fig.update_traces(
            line_color='#EF4444',
            marker=dict(size=10, color='#EF4444')
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            concept_trend.rename(columns={
                'timestamp': 'Week',
                'score_pct': 'Avg Score (%)'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ concept_trend collection is empty. Run test.py first.")

# ============================================================
# Q8: Late Submissions vs Score
# ============================================================
elif selected_q == "Q8":
    st.header("⏰ Q8: Late Submissions vs Score")

    if not late_vs_score.empty:
        summary = late_vs_score.groupby('is_late')['score_pct'].mean().round(2).reset_index()
        summary['label'] = summary['is_late'].map({True: 'Late', False: 'On-Time'})
        summary['color'] = summary['is_late'].map({True: '#EF4444', False: '#10B981'})

        fig = px.bar(
            summary,
            x='label',
            y='score_pct',
            color='label',
            color_discrete_map={'On-Time': '#10B981', 'Late': '#EF4444'},
            title='Submission Timing vs Average Score',
            labels={
                'label': 'Submission Timing',
                'score_pct': 'Average Score (%)'
            },
            text='score_pct'
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            late_vs_score.rename(columns={
                'is_late': 'Is Late',
                'score_pct': 'Score (%)'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ late_vs_score collection is empty. Run test.py first.")

# ============================================================
# Q9: Monthly Attendance & Engagement
# ============================================================
elif selected_q == "Q9":
    st.header("📅 Q9: Monthly Attendance & Engagement")

    has_attendance = not monthly_attendance.empty
    has_engagement = not monthly_engagement.empty

    if has_attendance or has_engagement:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=['Monthly Attendance Rate (%)', 'Monthly Engagement Events'],
            vertical_spacing=0.15
        )

        if has_attendance:
            fig.add_trace(
                go.Scatter(
                    x=monthly_attendance['month'],
                    y=monthly_attendance['att_rate'],
                    mode='lines+markers',
                    name='Attendance Rate',
                    line=dict(color='#3B82F6', width=3),
                    marker=dict(size=10, color='#3B82F6')
                ),
                row=1, col=1
            )

        if has_engagement:
            fig.add_trace(
                go.Bar(
                    x=monthly_engagement['month'],
                    y=monthly_engagement['event_count'],
                    name='Engagement Events',
                    marker_color='#F59E0B'
                ),
                row=2, col=1
            )

        style_chart(fig, height=650)

        st.plotly_chart(fig, use_container_width=True)

        if has_attendance:
            st.dataframe(
                monthly_attendance.rename(columns={
                    'month': 'Month',
                    'att_rate': 'Attendance Rate (%)'
                }),
                use_container_width=True
            )

    else:
        st.warning("⚠️ No attendance or engagement data found. Run test.py first.")

# ============================================================
# Q10: Age Band Analysis
# ============================================================
elif selected_q == "Q10":
    st.header("👥 Q10: Age Band Analysis")

    if not students_master.empty and 'age_band' in students_master.columns:
        age_stats = (
            students_master.groupby('age_band', observed=True)
            .agg(
                avg_grade=('avg_grade', 'mean'),
                avg_attendance=('attendance_rate', 'mean'),
                avg_logins=('login_count', 'mean'),
                student_count=('student_id', 'count')
            )
            .round(2)
            .reset_index()
        )

        fig = px.bar(
            age_stats.melt(
                id_vars='age_band',
                value_vars=['avg_grade', 'avg_attendance', 'avg_logins']
            ),
            x='age_band',
            y='value',
            color='variable',
            barmode='group',
            title='Outcomes by Age Band',
            labels={
                'age_band': 'Age Band',
                'value': 'Average Value',
                'variable': 'Metric'
            },
            color_discrete_map={
                'avg_grade': '#10B981',
                'avg_attendance': '#3B82F6',
                'avg_logins': '#F59E0B'
            },
            text='value'
        )

        fig.update_traces(
            texttemplate='%{text:.1f}',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            age_stats.rename(columns={
                'age_band': 'Age Band',
                'avg_grade': 'Avg Grade (%)',
                'avg_attendance': 'Avg Attendance (%)',
                'avg_logins': 'Avg Logins',
                'student_count': 'Student Count'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ age_band column not found in students_master.")

# ============================================================
# Q11: Student Segmentation
# ============================================================
elif selected_q == "Q11":
    st.header("🎯 Q11: Student Segmentation (K-Means)")

    if not students_master.empty and 'segment_label' in students_master.columns:
        segment_counts = students_master['segment_label'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']

        fig = px.pie(
            segment_counts,
            values='Count',
            names='Segment',
            title='Student Segment Distribution',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(
            students_master.dropna(subset=['attendance_rate', 'avg_grade']),
            x='attendance_rate',
            y='avg_grade',
            color='segment_label',
            title='Student Segments: Attendance vs Grade',
            labels={
                'attendance_rate': 'Attendance Rate (%)',
                'avg_grade': 'Average Grade (%)'
            },
            hover_data=['student_id', 'full_name'],
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        style_chart(fig2)

        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            students_master[['full_name', 'group_id', 'segment_label', 'attendance_rate', 'avg_grade']].rename(columns={
                'full_name': 'Student Name',
                'group_id': 'Group',
                'segment_label': 'Segment',
                'attendance_rate': 'Attendance (%)',
                'avg_grade': 'Avg Grade (%)'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ Segmentation not available. Run clustering in Colab first.")

# ============================================================
# Q12: Group Sizes: Stated vs Actual
# ============================================================
elif selected_q == "Q12":
    st.header("📏 Q12: Group Sizes — Stated vs Actual")

    if not students_master.empty:
        true_sizes = students_master.groupby('group_id').size().reset_index(name='true_num_students')

        stated_cols = ['group_id']
        if 'group_name' in students_master.columns:
            stated_cols.append('group_name')
        if 'stated_num_students' in students_master.columns:
            stated_cols.append('stated_num_students')

        stated_sizes = students_master[stated_cols].drop_duplicates(subset=['group_id'])
        size_compare = stated_sizes.merge(true_sizes, on='group_id', how='left')

        if 'stated_num_students' in size_compare.columns:
            size_compare['discrepancy'] = size_compare['true_num_students'] - size_compare['stated_num_students']
            size_compare['flagged'] = size_compare['discrepancy'].abs() > 2

        fig = go.Figure()

        if 'stated_num_students' in size_compare.columns:
            fig.add_trace(
                go.Bar(
                    name='Stated',
                    x=size_compare['group_id'],
                    y=size_compare['stated_num_students'],
                    marker_color='#3B82F6'
                )
            )

        fig.add_trace(
            go.Bar(
                name='Actual',
                x=size_compare['group_id'],
                y=size_compare['true_num_students'],
                marker_color='#F59E0B'
            )
        )

        fig.update_layout(
            barmode='group',
            title='Group Sizes: Stated vs Actual',
            xaxis_title='Group',
            yaxis_title='Number of Students'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            size_compare.rename(columns={
                'group_id': 'Group',
                'stated_num_students': 'Stated Size',
                'true_num_students': 'Actual Size',
                'discrepancy': 'Discrepancy'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ students_master is empty.")

# ============================================================
# Q13: Smallest Group Recommendation
# ============================================================
elif selected_q == "Q13":
    st.header("🔍 Q13: Smallest Group Recommendation")

    if not students_master.empty:
        group_sizes = students_master.groupby('group_id').size().reset_index(name='num_students')

        if 'group_name' in students_master.columns:
            group_names = students_master[['group_id', 'group_name']].drop_duplicates()
            group_sizes = group_sizes.merge(group_names, on='group_id', how='left')
        else:
            group_sizes['group_name'] = group_sizes['group_id']

        group_sizes = group_sizes.sort_values('num_students')
        smallest = group_sizes.iloc[0]

        fig = px.bar(
            group_sizes,
            x='group_id',
            y='num_students',
            title=f'Smallest Group: {smallest["group_id"]} ({smallest["num_students"]} students)',
            labels={
                'num_students': 'Number of Students',
                'group_id': 'Group'
            },
            text='num_students',
            color='num_students',
            color_continuous_scale='Reds'
        )

        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            group_sizes.rename(columns={
                'group_id': 'Group',
                'group_name': 'Group Name',
                'num_students': 'Students'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ students_master is empty.")

# ============================================================
# Q14: Top 10 At-Risk Students
# ============================================================
elif selected_q == "Q14":
    st.header("🚨 Q14: Top 10 At-Risk Students")

    if not at_risk_students.empty:
        top10 = at_risk_students.head(10).sort_values('at_risk_score', ascending=False)

        fig = px.bar(
            top10,
            x='at_risk_score',
            y='full_name',
            orientation='h',
            color='at_risk_score',
            color_continuous_scale='Reds',
            title='Top 10 At-Risk Students (Highest Priority)',
            labels={
                'at_risk_score': 'At-Risk Score',
                'full_name': 'Student'
            },
            text='at_risk_score',
            hover_data=['group_id', 'course_name']
        )

        fig.update_traces(
            texttemplate='%{text:.1f}',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            top10.rename(columns={
                'full_name': 'Student Name',
                'group_id': 'Group',
                'course_name': 'Course',
                'at_risk_score': 'Risk Score',
                'attendance_rate': 'Attendance (%)',
                'avg_grade': 'Avg Grade (%)'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ at_risk_students collection is empty. Run test.py first.")

# ============================================================
# Q15: Group Grade Trends Over Time
# ============================================================
elif selected_q == "Q15":
    st.header("📈 Q15: Group Grade Trends Over Time")

    if not group_trends.empty:
        fig = px.bar(
            group_trends,
            x='group_id',
            y='grade_change',
            color='trend',
            color_discrete_map={
                '↑ Trending Up': '#10B981',
                '→ Flat': '#F59E0B',
                '↓ Trending Down': '#EF4444'
            },
            title='Grade Change Over Term by Group',
            labels={
                'grade_change': 'Grade Change (%)',
                'group_id': 'Group'
            },
            text='grade_change',
            hover_data=['trend']
        )

        fig.add_hline(
            y=0,
            line_dash='dash',
            line_color='#8A9BA8'
        )

        fig.update_traces(
            texttemplate='%{text:+.1f}%',
            textposition='outside'
        )

        style_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            group_trends.rename(columns={
                'group_id': 'Group',
                'grade_change': 'Grade Change (%)',
                'trend': 'Trend'
            }),
            use_container_width=True
        )

    else:
        st.warning("⚠️ group_trends collection is empty. Run test.py first.")
