import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import warnings
from mastery import compute_topic_stats, compute_topic_mastery
from learning_path import generate_learning_path
warnings.filterwarnings('ignore')

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

class LearnerProfile:
    """Manages learner profiles and tracks performance metrics"""
    
    def __init__(self):
        self.profiles_file = 'data/learner_profiles.json'
        self.profiles = self._load_profiles()
        
        # Initialize sentence transformer if available
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self.embedder = None
                print("Warning: Could not load sentence transformer, falling back to keyword matching")
        else:
            self.embedder = None
    
    def _load_profiles(self) -> Dict:
        """Load existing profiles from JSON file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_profiles(self):
        """Save profiles to JSON file"""
        os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def get_profile(self, student_id: str) -> Optional[Dict[str, float]]:
        """Get profile for a specific student"""
        return self.profiles.get(student_id)
    
    def update_profile(self, student_id: str, quiz_answers: Dict[str, Dict]) -> Dict[str, float]:
        """Update learner profile based on quiz answers and compute topic-wise mastery"""

        # ---------------------------
        # SAFETY: Empty submission
        # ---------------------------
        if not quiz_answers:
            return self.get_profile(student_id) or {
                'accuracy': 0.0,
                'pace': 0.0,
                'engagement': 0.0,
                'topic_mastery': {}
            }

        # ---------------------------
        # SESSION-LEVEL METRICS
        # ---------------------------
        total_questions = len(quiz_answers)
        correct_answers = sum(
            1 for a in quiz_answers.values() if a.get('correct', False)
        )
        skipped_questions = sum(
            1 for a in quiz_answers.values() if a.get('skipped', False)
        )
        response_times = [
            a.get('response_time', 0) for a in quiz_answers.values()
        ]

        current_accuracy = correct_answers / total_questions if total_questions else 0
        current_pace = sum(response_times) / len(response_times) if response_times else 0
        current_engagement = (
            1 - (skipped_questions / total_questions)
            if total_questions else 0
        )

        # ---------------------------
        # LOAD EXISTING PROFILE
        # ---------------------------
        existing_profile = self.profiles.get(student_id, {
            'accuracy': 0.0,
            'pace': 0.0,
            'engagement': 0.0,
            'topic_mastery': {},
            'quiz_count': 0,
            'last_updated': None
        })

        quiz_count = existing_profile.get('quiz_count', 0)

        # Give higher weight to recent performance
        weight = 0.7 if quiz_count > 0 else 1.0

        # ---------------------------
        # WEIGHTED UPDATE
        # ---------------------------
        new_accuracy = (
            existing_profile.get('accuracy', 0) * (1 - weight)
            + current_accuracy * weight
        )

        new_pace = (
            existing_profile.get('pace', 0) * (1 - weight)
            + current_pace * weight
        )

        new_engagement = (
            existing_profile.get('engagement', 0) * (1 - weight)
            + current_engagement * weight
        )

        # ---------------------------
        # COMPUTE TOPIC-WISE MASTERY
        # ---------------------------
        from mastery import compute_topic_stats, compute_topic_mastery
        from logger import QuizLogger

        logger = QuizLogger()
        student_logs = logger.get_student_logs(student_id)

        if not student_logs.empty:
            topic_stats = compute_topic_stats(student_logs)
            topic_mastery = compute_topic_mastery(topic_stats)
        else:
            topic_mastery = {}

        # ---------------------------
        # FINAL PROFILE OBJECT
        # ---------------------------
        updated_profile = {
            'accuracy': round(new_accuracy, 3),
            'pace': round(new_pace, 2),
            'engagement': round(new_engagement, 3),
            'topic_mastery': topic_mastery,
            'quiz_count': quiz_count + 1,
            'last_updated': datetime.now().isoformat()
        }

        # ---------------------------
        # SAVE + RETURN
        # ---------------------------
        self.profiles[student_id] = updated_profile
        self._save_profiles()

        return {
            'accuracy': updated_profile['accuracy'],
            'pace': updated_profile['pace'],
            'engagement': updated_profile['engagement'],
            'topic_mastery': topic_mastery
        }

    def get_weak_topics(self, student_id: str) -> List[str]:
        """Identify topics where student needs improvement"""
        # This is a simplified implementation
        # In a real system, you would track performance by topic
        profile = self.get_profile(student_id)
        if not profile:
            return ['fractions', 'algebra']
        
        if profile['accuracy'] < 0.6:
            return ['fractions', 'basic arithmetic']
        elif profile['accuracy'] < 0.8:
            return ['algebra', 'geometry']
        else:
            return ['advanced algebra', 'calculus']

    def get_learning_plan(self, student_id, logs_df, questions_df):
        mastery = compute_topic_mastery(logs_df)

        topic_difficulty = (
            questions_df.groupby("topic")["difficulty"].mean().to_dict()
        )

        return generate_learning_path(mastery, topic_difficulty)

class ContentRecommender:
    """Provides content recommendations based on learner profile and ML algorithms"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.clusterer = None
        self.classifier = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for recommendations"""
        try:
            # Initialize with default parameters
            self.clusterer = KMeans(n_clusters=3, random_state=42, n_init=10)
            self.classifier = DecisionTreeClassifier(random_state=42, max_depth=5)
        except Exception as e:
            print(f"Warning: Could not initialize ML models: {e}")
    
    def get_recommendations(self, student_id: str, profile: Dict[str, float], 
                          questions_df: pd.DataFrame, num_recommendations: int = 3) -> List[Dict]:
        """Get personalized content recommendations with explanations"""
        if questions_df.empty:
            return []
        
        try:
            # Rule-based recommendations based on accuracy
            accuracy = profile.get('accuracy', 0.0)
            engagement = profile.get('engagement', 0.0)
            pace = profile.get('pace', 0.0)
            
            recommendations = []
            
            if accuracy < 0.6:
                # Student needs remedial content - Scenario 1 from project doc
                explanation = f"Based on your {accuracy:.1%} accuracy, the system has identified that you need additional support with foundational concepts. "
                explanation += "This recommendation provides simplified content with visual aids and guided practice to help reinforce basic skills."
                
                remedial_questions = questions_df[questions_df['difficulty'] <= 2].copy()
                if not remedial_questions.empty:
                    # Add one remedial question
                    rec = remedial_questions.sample(n=1).iloc[0]
                    recommendations.append({
                        'type': 'remedial',
                        'question_id': rec['question_id'],
                        'topic': rec['topic'],
                        'difficulty': rec['difficulty'],
                        'text': rec['text'],
                        'hint': rec['hint'],
                        'explanation': explanation
                    })
                
                # Add practice questions
                practice_questions = questions_df[questions_df['difficulty'] == 1].copy()
                if not practice_questions.empty:
                    n_practice = min(2, len(practice_questions))
                    for _, rec in practice_questions.sample(n=n_practice).iterrows():
                        explanation = f"This practice question reinforces basic concepts you've been working on. "
                        explanation += "Since your accuracy is {accuracy:.1%}, extra practice with fundamentals will help build confidence."
                        recommendations.append({
                            'type': 'practice',
                            'question_id': rec['question_id'],
                            'topic': rec['topic'],
                            'difficulty': rec['difficulty'],
                            'text': rec['text'],
                            'hint': rec['hint'],
                            'explanation': explanation
                        })
            
            elif 0.6 <= accuracy <= 0.85:
                # Student needs practice and some challenge
                explanation = f"With {accuracy:.1%} accuracy, you're showing solid understanding but can still improve. "
                explanation += "This content balances practice with challenges to help you advance."
                
                practice_questions = questions_df[questions_df['difficulty'] == 2].copy()
                challenge_questions = questions_df[questions_df['difficulty'] >= 3].copy()
                
                # Add practice questions
                if not practice_questions.empty:
                    n_practice = min(2, len(practice_questions))
                    for _, rec in practice_questions.sample(n=n_practice).iterrows():
                        explanation = f"This practice question reinforces your current skill level. "
                        explanation += "Balanced practice with questions at your level helps maintain and improve your {accuracy:.1%} accuracy."
                        recommendations.append({
                            'type': 'practice',
                            'question_id': rec['question_id'],
                            'topic': rec['topic'],
                            'difficulty': rec['difficulty'],
                            'text': rec['text'],
                            'hint': rec['hint'],
                            'explanation': explanation
                        })
                
                # Add one challenge question
                if not challenge_questions.empty:
                    rec = challenge_questions.sample(n=1).iloc[0]
                    explanation = f"This challenge question is designed to stretch your abilities. "
                    explanation += "With {accuracy:.1%} accuracy, you're ready to tackle more complex problems."
                    recommendations.append({
                        'type': 'challenge',
                        'question_id': rec['question_id'],
                        'topic': rec['topic'],
                        'difficulty': rec['difficulty'],
                        'text': rec['text'],
                        'hint': rec['hint'],
                        'explanation': explanation
                    })
            
            else:
                # High-performing student needs challenging content - Scenario 2 from project doc
                explanation = f"Excellent work! With {accuracy:.1%} accuracy, you're identified as an advanced learner. "
                explanation += "This recommendation skips remedial content and offers challenging, case study-based activities to keep you engaged."
                
                challenge_questions = questions_df[questions_df['difficulty'] >= 3].copy()
                
                if not challenge_questions.empty:
                    n_challenge = min(3, len(challenge_questions))
                    for _, rec in challenge_questions.sample(n=n_challenge).iterrows():
                        explanation = f"As an advanced learner with {accuracy:.1%} accuracy, this challenge question is designed to deepen your understanding. "
                        explanation += "It goes beyond basic concepts to encourage creative thinking and application."
                        recommendations.append({
                            'type': 'challenge',
                            'question_id': rec['question_id'],
                            'topic': rec['topic'],
                            'difficulty': rec['difficulty'],
                            'text': rec['text'],
                            'hint': rec['hint'],
                            'explanation': explanation
                        })
            
            # Ensure we have exactly the requested number of recommendations
            if len(recommendations) < num_recommendations:
                # Fill with random questions
                remaining = num_recommendations - len(recommendations)
                used_ids = {rec['question_id'] for rec in recommendations}
                available_questions = questions_df[~questions_df['question_id'].isin(used_ids)]
                
                if not available_questions.empty:
                    for _, rec in available_questions.sample(n=min(remaining, len(available_questions))).iterrows():
                        explanation = f"This additional question complements your learning path based on your {accuracy:.1%} accuracy and {engagement:.1%} engagement."
                        recommendations.append({
                            'type': 'additional',
                            'question_id': rec['question_id'],
                            'topic': rec['topic'],
                            'difficulty': rec['difficulty'],
                            'text': rec['text'],
                            'hint': rec['hint'],
                            'explanation': explanation
                        })
            
            return recommendations[:num_recommendations]
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Fallback to random questions
            if not questions_df.empty:
                return [
                    {
                        'type': 'fallback',
                        'question_id': rec['question_id'],
                        'topic': rec['topic'],
                        'difficulty': rec['difficulty'],
                        'text': rec['text'],
                        'hint': rec['hint'],
                        'explanation': 'Fallback recommendation due to system error'
                    }
                    for _, rec in questions_df.sample(n=min(num_recommendations, len(questions_df))).iterrows()
                ]
            return []
    
    def _get_ml_recommendations(self, profile: Dict[str, float], 
                               questions_df: pd.DataFrame) -> List[Dict]:
        """Use ML models for more sophisticated recommendations"""
        try:
            # Create feature vector for student
            features = np.array([[
                profile.get('accuracy', 0),
                profile.get('pace', 0),
                profile.get('engagement', 0)
            ]])
            
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Use clustering to find similar student patterns
            if self.clusterer and len(questions_df) > 3:
                # Fit clusterer on question difficulties
                question_features = questions_df[['difficulty']].values
                self.clusterer.fit(question_features)
                
                # Get cluster for current student profile
                student_cluster = self.clusterer.predict(features_scaled[:, :1])[0]
                
                # Recommend questions from the same cluster
                question_clusters = self.clusterer.predict(question_features)
                recommended_questions = questions_df[question_clusters == student_cluster]
                
                return recommended_questions.to_dict('records')
            
        except Exception as e:
            print(f"ML recommendation error: {e}")
        
        # Fallback to rule-based if ML fails
        return []

def create_sample_profiles():
    """Create sample learner profiles for testing"""
    profiles = {
        's1': {
            'accuracy': 0.75,
            'pace': 25.5,
            'engagement': 0.9,
            'quiz_count': 3,
            'last_updated': datetime.now().isoformat()
        },
        's2': {
            'accuracy': 0.45,
            'pace': 45.2,
            'engagement': 0.6,
            'quiz_count': 2,
            'last_updated': datetime.now().isoformat()
        },
        's3': {
            'accuracy': 0.92,
            'pace': 18.7,
            'engagement': 0.95,
            'quiz_count': 5,
            'last_updated': datetime.now().isoformat()
        }
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/learner_profiles.json', 'w') as f:
        json.dump(profiles, f, indent=2)
    
    return profiles

if __name__ == "__main__":
    # Test the models
    profile_manager = LearnerProfile()
    recommender = ContentRecommender()
    
    # Create sample profiles
    create_sample_profiles()
    
    print("Models initialized successfully!")
