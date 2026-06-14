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

students_master = load_collection("students_master")
group_attendance = load_collection("group_attendance")
course_grades = load_collection("course_grades")
concept_failures = load_collection("concept_failures")
at_risk_students = load_collection("at_risk_students")
monthly_attendance = load_collection("monthly_attendance")
group_trends = load_collection("group_trends")

# Extra collections (real data)
score_by_type    = load_collection("score_by_type")
concept_trend    = load_collection("concept_trend")
late_vs_score    = load_collection("late_vs_score")
monthly_engagement = load_collection("monthly_engagement")

# Sidebar - Logo + Navigation
with st.sidebar:
    # Logo
    st.image("logo.png", width=200)
    
    # Title under logo
    st.markdown("### 🎓 Kayfa Analytics")
    st.caption("Student Performance Dashboard")
    
    st.markdown("---")
    st.markdown("## 📊 Navigation")
    
    # Questions List
    questions = {
        "Q1": "📈 Attendance Rate per Group",
        "Q2": "📊 Score Distribution by Assessment Type",
        "Q3": "🏆 Course Performance (Highest/Lowest)",
        "Q4": "📉 Attendance vs Grade Correlation",
        "Q5": "💻 Engagement vs Performance",
        "Q6": "❌ Concept Failure Rates",
        "Q7": "📈 Weakest Concept Trend Over Time",
        "Q8": "⏰ Late Submissions vs Score",
        "Q9": "📅 Monthly Attendance & Engagement",
        "Q10": "👥 Age Band Analysis",
        "Q11": "🎯 Student Segmentation (Clustering)",
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

# Main Content
st.title("📊 Kayfa Student Analytics Dashboard")
st.markdown("---")

# Q1: Attendance Rate per Group
if selected_q == "Q1":
    st.header("📈 Q1: Attendance Rate per Group")
    
    platform_avg = group_attendance['att_rate'].mean()
    
    fig = px.bar(
        group_attendance, x='group_id', y='att_rate',
        color=group_attendance['att_rate'].apply(lambda x: 'Below Average' if x < platform_avg else 'Above Average'),
        color_discrete_map={'Below Average': '#EF4444', 'Above Average': '#10B981'},
        title='Attendance Rate per Group',
        labels={'att_rate': 'Attendance Rate (%)', 'group_id': 'Group'},
        text='att_rate'
    )
    fig.add_hline(y=platform_avg, line_dash='dash', line_color='navy',
                   annotation_text=f'Platform Avg: {platform_avg:.1f}%')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
# Q2: Score Distribution by Assessment Type

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
            labels={'type': 'Assessment Type', 'mean': 'Average Score (%)', 'count': 'Count'},
            text='mean',
            hover_data=['std', 'count']
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            score_by_type.rename(columns={'type': 'Type', 'mean': 'Avg Score (%)', 'std': 'Std Dev', 'count': 'Count'}),
            use_container_width=True
        )
    else:
        st.warning("⚠️ score_by_type collection is empty. Run test.py first.")


# Q3: Course Performance
elif selected_q == "Q3":
    st.header("🏆 Q3: Highest and Lowest Average Grade by Course")
    
    if not course_grades.empty:
        fig = px.bar(
            course_grades, x='course_name', y='mean',
            error_y='std',
            title='Average Grade per Course (with standard deviation)',
            labels={'mean': 'Average Grade (%)', 'course_name': 'Course'},
            color='mean',
            color_continuous_scale='RdYlGn',
            text='mean'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


# Q4: Attendance vs Grade Correlation
elif selected_q == "Q4":
    st.header("📉 Q4: Relationship Between Attendance Rate and Average Grade")
    
    if not students_master.empty and 'attendance_rate' in students_master.columns and 'avg_grade' in students_master.columns:
        from scipy.stats import pearsonr
        
        data = students_master.dropna(subset=['attendance_rate', 'avg_grade'])
        
        if len(data) > 1:
            corr, pval = pearsonr(data['attendance_rate'], data['avg_grade'])
            
            fig = px.scatter(
                data, x='attendance_rate', y='avg_grade',
                color='course_name' if 'course_name' in data.columns else None,
                trendline='ols',
                title=f'Attendance Rate vs Average Grade (r = {corr:.3f}, p = {pval:.4f})',
                labels={'attendance_rate': 'Attendance Rate (%)', 'avg_grade': 'Average Grade (%)'},
                opacity=0.7
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)


# Q5: Engagement vs Performance
elif selected_q == "Q5":
    st.header("💻 Q5: Does Engagement Relate to Academic Performance?")
    
    if not students_master.empty:
        data = students_master.dropna(subset=['login_count', 'total_video_minutes', 'avg_grade'])
        
        if len(data) > 1:
            from scipy.stats import pearsonr
            
            r_login, p_login = pearsonr(data['login_count'], data['avg_grade'])
            r_video, p_video = pearsonr(data['total_video_minutes'], data['avg_grade'])
            
            fig = make_subplots(rows=1, cols=2,
                                subplot_titles=[f'Login Frequency vs Grade (r={r_login:.2f})',
                                               f'Video Watch Time vs Grade (r={r_video:.2f})'])
            
            fig.add_trace(go.Scatter(x=data['login_count'], y=data['avg_grade'],
                                      mode='markers', name='Logins',
                                      marker=dict(color='steelblue', opacity=0.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=data['total_video_minutes'], y=data['avg_grade'],
                                      mode='markers', name='Video Minutes',
                                      marker=dict(color='darkorange', opacity=0.6)), row=1, col=2)
            
            fig.update_layout(height=500, title_text="Engagement vs Academic Performance")
            fig.update_xaxes(title_text="Login Count", row=1, col=1)
            fig.update_xaxes(title_text="Video Minutes", row=1, col=2)
            fig.update_yaxes(title_text="Average Grade (%)", row=1, col=1)
            fig.update_yaxes(title_text="Average Grade (%)", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
            


# Q6: Concept Failure Rates
elif selected_q == "Q6":
    st.header("❌ Q6: Concepts with Highest Failure Rate")
    
    if not concept_failures.empty:
        top15 = concept_failures.head(15)
        
        fig = px.bar(
            top15, x='fail_rate', y='concept_name',
            orientation='h', color='course_name' if 'course_name' in top15.columns else None,
            title='Top 15 Concepts by Failure Rate',
            labels={'fail_rate': 'Failure Rate (%)', 'concept_name': 'Concept'},
            text='fail_rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        


# Q7: Weakest Concept Trend Over Time
elif selected_q == "Q7":
    st.header("📈 Q7: Weakest Concept Mastery Over Time")

    if not concept_trend.empty:
        # Convert timestamp column
        if 'timestamp' in concept_trend.columns:
            concept_trend['timestamp'] = pd.to_datetime(concept_trend['timestamp'])

        worst_name = concept_failures.iloc[0]['concept_name'] if not concept_failures.empty else "Weakest Concept"

        fig = px.line(
            concept_trend,
            x='timestamp',
            y='score_pct',
            title=f'Q7 — Weekly Avg Score Trend: "{worst_name}"',
            labels={'timestamp': 'Week', 'score_pct': 'Avg Score (%)'},
            markers=True,
            line_shape='spline'
        )
        fig.update_traces(line_color='#EF4444', marker=dict(size=8))
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            concept_trend.rename(columns={'timestamp': 'Week', 'score_pct': 'Avg Score (%)'}),
            use_container_width=True
        )
    else:
        st.warning("⚠️ concept_trend collection is empty. Run test.py first.")
        


# Q8 — Late Submissions vs Score
elif selected_q == "Q8":
    st.header("⏰ Q8: Do Late Submissions Lead to Lower Scores?")

    if not late_vs_score.empty:
        # Compute averages per is_late
        summary = (
            late_vs_score.groupby('is_late')['score_pct']
            .mean().round(2).reset_index()
        )
        summary['label'] = summary['is_late'].map({True: 'Late', False: 'On-Time'})
        summary['color'] = summary['is_late'].map({True: '#EF4444', False: '#10B981'})

        fig = px.bar(
            summary, x='label', y='score_pct',
            color='label',
            color_discrete_map={'On-Time': '#10B981', 'Late': '#EF4444'},
            title='Q8 — Submission Timing vs Average Score',
            labels={'label': 'Submission Timing', 'score_pct': 'Average Score (%)'},
            text='score_pct'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Box plot using real data
        fig2 = go.Figure()
        on_time = late_vs_score[late_vs_score['is_late'] == False]['score_pct']
        late    = late_vs_score[late_vs_score['is_late'] == True]['score_pct']
        fig2.add_trace(go.Box(y=on_time, name='On-Time', marker_color='#10B981'))
        fig2.add_trace(go.Box(y=late,    name='Late',    marker_color='#EF4444'))
        fig2.update_layout(
            title='Score Distribution: On-Time vs Late Submissions (Real Data)',
            yaxis_title='Score (%)',
            height=450
        )
        st.plotly_chart(fig2, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("On-Time Avg Score", f"{on_time.mean():.1f}%")
        col2.metric("Late Avg Score",    f"{late.mean():.1f}%",
                    delta=f"{late.mean() - on_time.mean():.1f}%")
    else:
        st.warning("⚠️ late_vs_score collection is empty. Run test.py first.")
    


# Q9: Monthly Attendance & Engagement
elif selected_q == "Q9":
    st.header("📅 Q9: Attendance and Engagement Over the 6-Month Term")

    has_attendance  = not monthly_attendance.empty
    has_engagement  = not monthly_engagement.empty

    if has_attendance or has_engagement:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            subplot_titles=['Monthly Attendance Rate (%)', 'Monthly Engagement Events'],
            vertical_spacing=0.15
        )

        if has_attendance:
            fig.add_trace(
                go.Scatter(
                    x=monthly_attendance['month'], y=monthly_attendance['att_rate'],
                    mode='lines+markers', name='Attendance Rate',
                    line=dict(color='steelblue', width=3), marker=dict(size=10)
                ), row=1, col=1
            )

        if has_engagement:
            fig.add_trace(
                go.Bar(
                    x=monthly_engagement['month'], y=monthly_engagement['event_count'],
                    name='Engagement Events', marker_color='darkorange'
                ), row=2, col=1
            )

        fig.update_layout(title='Attendance & Engagement Over 6-Month Term (Real Data)', height=650)
        st.plotly_chart(fig, use_container_width=True)

        if has_engagement:
            st.dataframe(
                monthly_engagement.rename(columns={'month': 'Month', 'event_count': 'Events'}),
                use_container_width=True
            )
    else:
        st.warning("⚠️ No attendance or engagement data found. Run test.py first.")
        


# Q10: Age Band Analysis
elif selected_q == "Q10":
    st.header("👥 Q10: Does Age Relate to Outcomes?")
    
    if not students_master.empty and 'age_band' in students_master.columns:
        age_stats = (students_master.groupby('age_band', observed=True)
                     .agg(avg_grade=('avg_grade', 'mean'),
                          avg_attendance=('attendance_rate', 'mean'),
                          avg_logins=('login_count', 'mean'),
                          student_count=('student_id', 'count'))
                     .round(2)
                     .reset_index())
        
        fig = px.bar(
            age_stats.melt(id_vars='age_band', value_vars=['avg_grade', 'avg_attendance', 'avg_logins']),
            x='age_band', y='value', color='variable', barmode='group',
            title='Outcomes by Age Band',
            labels={'age_band': 'Age Band', 'value': 'Average Value', 'variable': 'Metric'},
            color_discrete_map={'avg_grade': '#10B981', 'avg_attendance': '#3B82F6', 'avg_logins': '#F59E0B'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


# Q11: Student Segmentation
elif selected_q == "Q11":
    st.header("🎯 Q11: Student Segmentation Using K-Means")
    
    if not students_master.empty and 'segment_label' in students_master.columns:
        segment_counts = students_master['segment_label'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        
        fig = px.pie(segment_counts, values='Count', names='Segment', title='Student Segment Distribution',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        
        # Scatter plot of segments
        fig2 = px.scatter(
            students_master.dropna(subset=['attendance_rate', 'avg_grade']),
            x='attendance_rate', y='avg_grade',
            color='segment_label',
            title='Student Segments: Attendance vs Grade',
            labels={'attendance_rate': 'Attendance Rate (%)', 'avg_grade': 'Average Grade (%)'},
            hover_data=['student_id', 'full_name']
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Student segmentation data not available. Run clustering first.")


# Q12: Group Sizes Discrepancy
elif selected_q == "Q12":
    st.header("📏 Q12: Group Sizes — Stated vs Actual")

    if not students_master.empty:
        # Actual sizes: count students per group
        true_sizes = students_master.groupby('group_id').size().reset_index(name='true_num_students')

        # Stated sizes: from students_master (merged from groups.csv via kafy_analysis.py)
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
            fig.add_trace(go.Bar(name='Stated', x=size_compare['group_id'],
                                 y=size_compare['stated_num_students'], marker_color='steelblue'))
        fig.add_trace(go.Bar(name='Actual', x=size_compare['group_id'],
                             y=size_compare['true_num_students'], marker_color='darkorange'))
        fig.update_layout(barmode='group', title='Q12 — Group Sizes: Stated vs Actual',
                           xaxis_title='Group', yaxis_title='Number of Students', height=500)
        st.plotly_chart(fig, use_container_width=True)
        

# Q13: Smallest Group Recommendation
elif selected_q == "Q13":
    st.header("🔍 Q13: Identify and Recommend Merge for Smallest Group")
    
    if not students_master.empty:
        # Calculate group sizes
        group_sizes = students_master.groupby('group_id').size().reset_index(name='num_students')
        
        # Add group names if available
        if 'group_name' in students_master.columns:
            group_names = students_master[['group_id', 'group_name']].drop_duplicates()
            group_sizes = group_sizes.merge(group_names, on='group_id', how='left')
        else:
            group_sizes['group_name'] = group_sizes['group_id']
        
        group_sizes = group_sizes.sort_values('num_students')
        smallest = group_sizes.iloc[0]
        
        # Simple bar chart
        fig = px.bar(
            group_sizes, 
            x='group_id', 
            y='num_students',
            title='Q13 — Number of Students per Group',
            labels={'num_students': 'Number of Students', 'group_id': 'Group'},
            text='num_students',
            color='num_students',
            color_continuous_scale='Reds'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        

# Q14: Top 10 At-Risk Students
elif selected_q == "Q14":
    st.header("🚨 Q14: Top 10 At-Risk Students — Contact First")
    
    if not at_risk_students.empty:
        fig = px.bar(
            at_risk_students.head(10), x='at_risk_score', y='full_name', orientation='h',
            color='at_risk_score', color_continuous_scale='Reds',
            title='Top 10 At-Risk Students (Highest Priority)',
            labels={'at_risk_score': 'At-Risk Score', 'full_name': 'Student'},
            text='at_risk_score'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        


# Q15: Group Grade Trends Over Time
elif selected_q == "Q15":
    st.header("📈 Q15: Group Grade Trends Over the Term")
    
    if not group_trends.empty:
        fig = px.bar(
            group_trends, x='group_id', y='grade_change',
            color='trend',
            color_discrete_map={'↑ Trending Up': '#10B981', '→ Flat': '#F59E0B', '↓ Trending Down': '#EF4444'},
            title='Grade Change Over Term by Group',
            labels={'grade_change': 'Grade Change (%)', 'group_id': 'Group'},
            text='grade_change'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
