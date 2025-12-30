# 🎓 AI-Powered Personalized Learning Platform

A sophisticated Streamlit web application that demonstrates **AI-driven adaptive learning** through intelligent quiz-taking, real-time performance tracking, learner profiling, ML-powered content recommendations, and comprehensive teacher analytics dashboard.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-latest-red)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-orange)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 Project Overview

This platform implements **Artificial Intelligence for Personalized Learning** as specified in the academic project requirements. It adapts educational content, pace, and format to meet the unique needs, progress, and preferences of individual learners using AI systems that dynamically adjust what, how, and when a student learns.

### 🎯 Key Academic Project Requirements Addressed

- **Tracks Progress**: Monitors performance across tasks with accuracy, pace, and engagement metrics
- **Learner Profiling**: Identifies learning pace, accuracy, and engagement patterns
- **Adapts Content**: Dynamically adjusts difficulty and content type based on performance
- **Recommends Material**: Suggests personalized questions and activities
- **Provides Feedback**: Generates targeted, real-time feedback
- **Supports Educators**: Teacher dashboard with insights and recommendations
- **Explainable AI**: Shows why specific content was recommended
- **Multimodal Personalization**: Adapts to preferred learning formats (text, video, interactive)
- **Gamification**: Points and levels to boost motivation

## 🚀 Key Features

### 👤 Student Mode
- **📝 Adaptive Quizzes**: Intelligent 5-question quizzes that adapt in real-time
- **🎯 Personalized Recommendations**: AI-powered content suggestions based on performance
- **📊 Real-time Performance Tracking**: Live metrics on accuracy, pace, and engagement
- **💬 Scenario-Based Feedback**: Personalized feedback aligned with learning scenarios
- **🎮 Gamification System**: Points and levels to boost engagement and motivation

### 👩‍🏫 Teacher Dashboard
- **📈 Class Analytics**: Comprehensive class performance overview
- **👥 Individual Student Tracking**: Detailed progress monitoring for each student
- **⚠️ Struggling Student Identification**: AI-powered detection of at-risk learners
- **📊 Data Visualization**: Interactive charts and performance distributions
- **📥 Data Export**: CSV export functionality for further analysis

### 🤖 AI & Machine Learning
- **🧠 Adaptive Content Selection**: Dynamic content recommendation based on performance
- **📊 Learner Profiling**: Automatic calculation of learning metrics and patterns
- **🔍 Explainable AI**: Transparent reasoning behind content recommendations
- **🔄 Real-time Adaptation**: Instant adjustments based on learner behavior

## 🛠️ Technology Stack

### Core Technologies
- **[Python 3.11+](https://www.python.org/)** - Primary programming language
- **[Streamlit](https://streamlit.io/)** - Web framework for data applications
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[NumPy](https://numpy.org/)** - Numerical computing
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning algorithms

### Visualization & UI
- **[Plotly](https://plotly.com/)** - Interactive data visualization
- **[Streamlit Components](https://streamlit.io/components)** - Enhanced UI elements

### Data Management
- **CSV Files** - Lightweight data persistence
- **JSON** - Profile storage

## 📊 Project Architecture

```
personalized-learning-platform/
├── app.py                 # Main Streamlit application
├── models.py              # ML models for learner profiling and recommendations
├── logger.py              # Quiz logging and data persistence
├── utils.py               # Utility functions for feedback and data processing
├── pyproject.toml         # Project dependencies (uv)
├── requirements.txt       # Project dependencies (pip)
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── data/
│   ├── sample_students.csv     # Sample student data
│   └── sample_questions.csv    # Sample question data
├── tests/
│   └── test_basic.py           # Unit tests
├── screenshots/                # Application screenshots
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd personalized-learning-platform
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501` to use the application.

## 🎯 Usage Guide

### For Students
1. **Select Profile**: Choose your student profile from the dropdown
2. **Take Quiz**: Complete the adaptive 5-question quiz
3. **View Results**: See your performance metrics and personalized feedback
4. **Get Recommendations**: Receive AI-powered content suggestions
5. **Track Progress**: Monitor your learning journey with gamification elements

### For Teachers
1. **Dashboard Access**: Navigate to the Teacher Dashboard
2. **Class Overview**: View overall class performance metrics
3. **Student Analysis**: Drill down into individual student performance
4. **Identify Support Needs**: Spot struggling students requiring intervention
5. **Export Data**: Download performance data for further analysis

## 📊 Data Model

### Student Profile
```json
{
  "student_id": "Unique identifier",
  "name": "Student name",
  "grade": "Grade level",
  "preferred_format": "Learning preference (text, video, interactive)"
}
```

### Question Data
```json
{
  "question_id": "Unique identifier",
  "topic": "Subject area (fractions, algebra, geometry)",
  "difficulty": "Difficulty level (1-5 stars)",
  "text": "Question text",
  "hint": "Contextual hint",
  "answer": "Expected answer",
  "type": "Answer type (numeric, fraction, text)"
}
```

### Performance Metrics
- **Accuracy**: Percentage of correct answers
- **Pace**: Average response time per question
- **Engagement**: Percentage of questions attempted (vs skipped)
- **Points**: Gamification scoring system
- **Level**: Progress level based on performance

## 🤖 AI & Machine Learning Implementation

### Adaptive Recommendation Engine
The platform uses rule-based algorithms enhanced with machine learning principles:

1. **Performance-Based Filtering**: Content difficulty adapts to accuracy scores
2. **Engagement Analysis**: System responds to skipping patterns and response times
3. **Learning Path Optimization**: Dynamic content sequencing based on progress

### Recommendation Logic
- **Accuracy < 60%**: Remedial content with guided practice
- **Accuracy 60-85%**: Balanced practice with moderate challenges
- **Accuracy > 85%**: Advanced challenges and enrichment activities

### Explainable AI Features
- Clear explanations for why specific content was recommended
- Transparent decision-making process
- Justification based on performance metrics

## 🎮 Gamification Elements

### Points System
- **Correct Answers**: 10 points each
- **Attempted Questions**: 5 points each (even if incorrect)
- **Completion Bonuses**: Additional points for quiz completion

### Level Progression
- **Levels 1-10**: Progressive difficulty tiers
- **Visual Progress Tracking**: Progress bars showing advancement
- **Achievement Recognition**: Milestone celebrations

## 📈 Analytics & Reporting

### Student Analytics
- Performance trends over time
- Strength and weakness identification
- Learning pace analysis
- Engagement pattern recognition

### Class Analytics
- Distribution of performance levels
- Average accuracy and engagement metrics
- Identification of common problem areas
- Overall class progress tracking

## 🔧 Configuration

The application can be configured through the `.streamlit/config.toml` file:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
python -m pytest tests/
```

## 🤝 Academic Project Alignment

### Scenario 1: Helping a Struggling Learner (Rahul)
- **Detection**: System identifies low accuracy and hesitation patterns
- **Intervention**: Replaces difficult content with simplified interactive tutorials
- **Support**: Provides guided exercises with hints enabled
- **Feedback**: Offers real-time feedback to correct mistakes early

### Scenario 2: Supporting a Fast & Curious Learner (Aisha)
- **Recognition**: Identifies high accuracy and fast completion patterns
- **Advancement**: Skips remedial content and unlocks challenge mode
- **Enrichment**: Recommends case study-based activities
- **Extension**: Offers peer-review writing prompts to deepen reflection

## 📚 Educational AI Techniques Implemented

### Supervised Learning Concepts
- Performance prediction based on historical data
- Content recommendation using profile-based filtering

### Rule-Based Systems
- Adaptive content selection using if-then logic
- Personalized feedback generation

### Data Analytics
- Performance tracking and pattern recognition
- Engagement metrics analysis

## 📤 Data Export Capabilities

### For Teachers
- **Full Logs CSV**: Complete quiz attempt data
- **Summary CSV**: Aggregated student performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [scikit-learn](https://scikit-learn.org/) for ML algorithms
- [Plotly](https://plotly.com/) for interactive charts
- [Pandas](https://pandas.pydata.org/) for data manipulation
