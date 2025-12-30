import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

from models import LearnerProfile, ContentRecommender
from logger import QuizLogger
from utils import generate_feedback, simulate_response_time
from learning_path import generate_learning_path

# Set page config
st.set_page_config(
    page_title="Personalized Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_student' not in st.session_state:
    st.session_state.current_student = None
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = {}
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'start_times' not in st.session_state:
    st.session_state.start_times = {}

# Initialize components
@st.cache_resource
def load_data():
    """Load student and question data"""
    try:
        students_df = pd.read_csv('data/sample_students.csv')
        questions_df = pd.read_csv('data/sample_questions.csv')
        return students_df, questions_df
    except FileNotFoundError:
        st.error("Data files not found. Please run the data generation script first.")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_resource
def initialize_components():
    """Initialize ML components"""
    logger = QuizLogger()
    profile_manager = LearnerProfile()
    recommender = ContentRecommender()
    return logger, profile_manager, recommender

def load_quiz_logs():
    """Load existing quiz logs"""
    try:
        return pd.read_csv('data/logs.csv')
    except FileNotFoundError:
        return pd.DataFrame()

def main():
    # Load data and components
    students_df, questions_df = load_data()
    logger, profile_manager, recommender = initialize_components()
    
    if students_df.empty or questions_df.empty:
        st.error("Please ensure data files exist in the 'data' directory.")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🎓 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Home", "Quiz", "Results", "Teacher Dashboard"]
    )
    
    if page == "Home":
        show_home_page(students_df, profile_manager)
    elif page == "Quiz":
        show_quiz_page(questions_df, logger)
    elif page == "Results":
        show_results_page(students_df, questions_df, profile_manager, recommender)
    elif page == "Teacher Dashboard":
        show_teacher_dashboard()

def show_home_page(students_df, profile_manager):
    """Display the home page"""
    st.title("🎓 Personalized Learning Platform")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Welcome to Your Learning Journey!")
        st.markdown("""
        This platform provides:
        - **Personalized Quizzes** adapted to your learning style
        - **Real-time Performance Tracking** with detailed analytics
        - **Smart Content Recommendations** powered by AI
        - **Progress Monitoring** to track your improvement
        """)
        
        # Student selection
        st.subheader("Select Your Profile")
        student_options = [f"{row['name']} (Grade {row['grade']})" for _, row in students_df.iterrows()]
        selected_student = st.selectbox(
            "Choose your student profile:",
            options=student_options,
            help="Select your profile to continue"
        )
        
        if selected_student:
            # Extract student info
            student_name = selected_student.split(' (')[0]
            student_row = students_df[students_df['name'] == student_name].iloc[0]
            st.session_state.current_student = student_row.to_dict()
            
            st.success(f"Welcome, {student_name}! Ready to start learning?")
            
            if st.button("🚀 Start Quiz", type="primary"):
                st.session_state.quiz_started = True
                st.session_state.quiz_completed = False
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.session_state.start_times = {}
                st.rerun()
    
    with col2:
        if st.session_state.current_student:
            st.subheader("📊 Your Profile Preview")
            student = st.session_state.current_student
            
            # Get current profile
            profile = profile_manager.get_profile(student['student_id'])
            
            with st.container():
                st.metric("Grade Level", student['grade'])
                st.metric("Preferred Format", student['preferred_format'].title())
                
                if profile:
                    st.metric("Accuracy", f"{profile['accuracy']:.1%}")
                    st.metric("Engagement", f"{profile['engagement']:.1%}")
                    st.metric("Response Time", f"{profile['pace']:.1f}s")
                else:
                    st.info("Complete a quiz to see your learning metrics!")

def show_quiz_page(questions_df, logger):
    """Display the quiz page"""
    if not st.session_state.current_student:
        st.warning("Please select a student profile from the Home page first.")
        return
    
    if not st.session_state.quiz_started:
        st.info("Please start a quiz from the Home page.")
        return
    
    st.title("📝 Learning Quiz")
    st.markdown("---")
    
    # Select 5 random questions for the quiz
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = questions_df.sample(n=min(5, len(questions_df)))
    
    selected_questions = st.session_state.selected_questions
    current_q = st.session_state.current_question
    
    if current_q < len(selected_questions):
        question_row = selected_questions.iloc[current_q]
        question_id = question_row['question_id']
        
        # Start timing for this question
        if question_id not in st.session_state.start_times:
            st.session_state.start_times[question_id] = time.time()
        
        # Display question
        st.subheader(f"Question {current_q + 1} of {len(selected_questions)}")
        st.write(f"**Topic:** {question_row['topic'].title()}")
        st.write(f"**Difficulty:** {'⭐' * int(question_row['difficulty'])}")
        
        st.markdown(f"### {question_row['text']}")
        
        # Answer input
        answer_key = f"answer_{question_id}"
        user_answer = st.text_input(
            "Your answer:",
            key=answer_key,
            help=f"Hint: {question_row['hint']}"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⏭️ Skip Question"):
                # Record skip
                response_time = time.time() - st.session_state.start_times[question_id]
                st.session_state.answers[question_id] = {
                    'answer': '',
                    'skipped': True,
                    'response_time': response_time,
                    'correct': False
                }
                st.session_state.current_question += 1
                st.rerun()
        
        with col2:
            if st.button("✅ Submit Answer", disabled=not user_answer.strip()):
                # Record answer
                response_time = time.time() - st.session_state.start_times[question_id]
                # Get the correct answer from the questions dataframe
                correct_answer = question_row.get('answer', '')
                # Use the validate_answer function for proper checking
                from utils import validate_answer
                correct = validate_answer(user_answer.strip(), correct_answer, question_row.get('type', 'text'))
                
                st.session_state.answers[question_id] = {
                    'answer': user_answer.strip(),
                    'skipped': False,
                    'response_time': response_time,
                    'correct': correct
                }
                st.session_state.current_question += 1
                st.rerun()
        
        with col3:
            if st.button("🏁 Finish Quiz"):
                st.session_state.quiz_completed = True
                st.session_state.quiz_started = False
                
                # Log the quiz attempt
                logger.log_attempt(
                    student_id=st.session_state.current_student['student_id'],
                    questions=selected_questions,
                    answers=st.session_state.answers
                )
                
                st.rerun()
        
        # Progress bar
        progress = (current_q) / len(selected_questions)
        st.progress(progress)
        
    else:
        # Quiz completed
        st.session_state.quiz_completed = True
        st.session_state.quiz_started = False
        
        # Log the quiz attempt
        logger.log_attempt(
            student_id=st.session_state.current_student['student_id'],
            questions=selected_questions,
            answers=st.session_state.answers
        )
        
        st.success("🎉 Quiz completed! Check your results.")
        if st.button("📊 View Results"):
            st.rerun()

def show_results_page(students_df, questions_df, profile_manager, recommender):
    """Display the results page"""
    if not st.session_state.current_student:
        st.warning("Please select a student profile first.")
        return
    
    if not st.session_state.quiz_completed or not st.session_state.answers:
        st.info("Complete a quiz to see your results!")
        return
    
    st.title("📊 Quiz Results & Recommendations")
    st.markdown("---")
    
    student_id = st.session_state.current_student['student_id']
    answers = st.session_state.answers
    
    # Calculate metrics
    total_questions = len(answers)
    correct_answers = sum(1 for a in answers.values() if a['correct'])
    skipped_questions = sum(1 for a in answers.values() if a['skipped'])
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Answered", total_questions)
        st.metric("Correct Answers", correct_answers)
    
    with col2:
        st.metric("Accuracy", f"{accuracy:.1%}")
        st.metric("Questions Skipped", skipped_questions)
    
    with col3:
        avg_time = sum(a['response_time'] for a in answers.values()) / total_questions
        engagement = 1 - (skipped_questions / total_questions)
        st.metric("Avg Response Time", f"{avg_time:.1f}s")
        st.metric("Engagement Score", f"{engagement:.1%}")
    
    with col4:
        # Gamification elements
        points = int(correct_answers * 10 + (total_questions - skipped_questions) * 5)
        level = min(10, max(1, int(points / 50) + 1))
        st.metric(".Points Earned", f"{points}")
        st.metric("Level", f"{level}/10")
        
        # Progress bar for next level
        progress_to_next = (points % 50) / 50
        st.progress(progress_to_next)
        st.caption(f"{int(progress_to_next * 100)}% to next level")
    
    # Update profile
    profile_manager.update_profile(student_id, answers)
    profile = profile_manager.get_profile(student_id)
    
    st.subheader("📊 Topic-wise Knowledge Mastery")

    topic_mastery = profile.get("topic_mastery", {})

    if topic_mastery:
        for topic, score in topic_mastery.items():
            st.write(f"**{topic.title()}** : {round(score, 2)}")
    else:
        st.info("Topic mastery will appear after more quiz attempts.")

    # Generate learning path
    st.subheader("🗺️ Personalized Learning Path")

    # Build topic difficulty map from question data
    topic_difficulty = (
        questions_df.groupby("topic")["difficulty"]
        .mean()
        .round()
        .to_dict()
    )

    learning_path = generate_learning_path(
        topic_mastery,
        topic_difficulty,
        daily_time=60
    )

    for step in learning_path:
        if step["type"] == "study":
            st.markdown(
                f"📘 **{step['topic'].title()}** "
                f"({step['level']}) — {step['time_minutes']} min"
            )
            st.caption("Activities: " + ", ".join(step["activities"]))
        else:
            st.markdown(
                f"🔁 **Revision:** {step['topic'].title()} — {step['time_minutes']} min"
            )

    # Display updated profile
    st.subheader("📈 Updated Learning Profile")
    profile_col1, profile_col2, profile_col3 = st.columns(3)
    
    with profile_col1:
        st.metric("Overall Accuracy", f"{profile['accuracy']:.1%}")
    with profile_col2:
        st.metric("Average Pace", f"{profile['pace']:.1f}s")
    with profile_col3:
        st.metric("Engagement Level", f"{profile['engagement']:.1%}")
    
    # Generate recommendations
    st.subheader("🎯 Personalized Recommendations")
    recommendations = recommender.get_recommendations(student_id, profile, questions_df)
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            with st.expander(f"📚 Recommendation {i}: {rec['type'].title()}", expanded=True):
                st.write(f"**Topic:** {rec['topic']}")
                st.write(f"**Difficulty:** {'⭐' * rec['difficulty']}")
                st.write(f"**Question:** {rec['text']}")
                st.write(f"**Hint:** {rec['hint']}")
                
                # Show explanation for why this recommendation was made
                if 'explanation' in rec:
                    st.info(f"**Why this recommendation?** {rec['explanation']}")
    
    # Generate feedback
    st.subheader("💬 Personalized Feedback")
    feedback = generate_feedback(accuracy, profile, st.session_state.current_student)
    st.info(feedback)
    
    # Reset quiz button
    if st.button("🔄 Take Another Quiz"):
        st.session_state.quiz_started = True
        st.session_state.quiz_completed = False
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.start_times = {}
        if 'selected_questions' in st.session_state:
            del st.session_state.selected_questions
        st.rerun()

def show_teacher_dashboard():
    """Display the teacher dashboard"""
    st.title("👩‍🏫 Teacher Dashboard")
    st.markdown("---")
    
    # Load quiz logs
    logs_df = load_quiz_logs()
    
    if logs_df.empty:
        st.info("No quiz data available yet. Students need to complete quizzes first.")
        return
    
    # Load student data for names
    students_df, _ = load_data()
    
    # Merge with student names
    if not students_df.empty:
        logs_with_names = logs_df.merge(
            students_df[['student_id', 'name']], 
            on='student_id', 
            how='left'
        )
    else:
        logs_with_names = logs_df
        logs_with_names['name'] = logs_with_names['student_id']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", logs_with_names['student_id'].nunique())
    
    with col2:
        st.metric("Total Quiz Attempts", len(logs_with_names))
    
    with col3:
        avg_accuracy = logs_with_names['accuracy'].mean()
        st.metric("Class Average Accuracy", f"{avg_accuracy:.1%}")
    
    with col4:
        struggling_students = logs_with_names[logs_with_names['accuracy'] < 0.5]['student_id'].nunique()
        st.metric("Struggling Students", struggling_students)
    
    # Accuracy distribution chart
    st.subheader("📊 Class Accuracy Distribution")
    
    fig = px.histogram(
        logs_with_names, 
        x='accuracy', 
        nbins=10,
        title="Distribution of Quiz Accuracies",
        labels={'accuracy': 'Accuracy Score', 'count': 'Number of Attempts'}
    )
    fig.update_traces(marker_color='lightblue', marker_line_color='darkblue', marker_line_width=1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Student performance table
    st.subheader("👥 Student Performance Summary")
    
    # Calculate student summaries
    student_summary = logs_with_names.groupby(['student_id', 'name']).agg({
        'accuracy': ['mean', 'count'],
        'engagement': 'mean',
        'avg_response_time': 'mean'
    }).round(3)
    
    student_summary.columns = ['Avg Accuracy', 'Quiz Count', 'Avg Engagement', 'Avg Response Time']
    student_summary = student_summary.reset_index()
    
    # Highlight struggling students
    def highlight_struggling(row):
        if row['Avg Accuracy'] < 0.5:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)
    
    styled_summary = student_summary.style.apply(highlight_struggling, axis=1)
    st.dataframe(styled_summary, use_container_width=True)
    
    # Struggling students list
    st.subheader("⚠️ Students Needing Attention")
    struggling = student_summary[student_summary['Avg Accuracy'] < 0.5]
    
    if not struggling.empty:
        for _, student in struggling.iterrows():
            with st.expander(f"🔴 {student['name']} (ID: {student['student_id']})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Accuracy", f"{student['Avg Accuracy']:.1%}")
                with col2:
                    st.metric("Engagement", f"{student['Avg Engagement']:.1%}")
                with col3:
                    st.metric("Quiz Attempts", int(student['Quiz Count']))
                
                # Provide AI recommendations for teachers
                st.info("🤖 AI Recommendation for this student:")
                if student['Avg Accuracy'] < 0.3:
                    st.write("• This student is significantly struggling and needs immediate intervention")
                    st.write("• Recommend one-on-one tutoring sessions")
                    st.write("• Provide simplified materials with visual aids")
                    st.write("• Schedule frequent check-ins and progress monitoring")
                elif student['Avg Accuracy'] < 0.5:
                    st.write("• This student needs additional support with foundational concepts")
                    st.write("• Suggest guided practice with immediate feedback")
                    st.write("• Offer alternative learning formats (videos, interactive content)")
                    st.write("• Plan a review session on core topics")
    else:
        st.success("🎉 All students are performing well!")
    
    # Export functionality
    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Full Logs CSV"):
            csv = logs_with_names.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"quiz_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Summary CSV"):
            csv = student_summary.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"student_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()