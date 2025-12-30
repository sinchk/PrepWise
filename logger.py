import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
import json


class QuizLogger:
    """Handles logging of quiz attempts and performance data"""

    def __init__(self, log_file: str = 'data/logs.csv'):
        self.log_file = log_file
        self.in_memory_logs = []
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Ensure the log file and directory exist"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        if not os.path.exists(self.log_file):
            # Create empty log file with headers
            empty_df = pd.DataFrame(columns=[
                'student_id', 'timestamp', 'question_id', 'answer', 'correct',
                'skipped', 'response_time', 'accuracy', 'engagement',
                'avg_response_time', 'session_id'
            ])
            empty_df.to_csv(self.log_file, index=False)

    def log_attempt(self, student_id: str, questions: pd.DataFrame,
                    answers: Dict[str, Dict]) -> bool:
        """Log a complete quiz attempt"""
        try:
            session_id = f"{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            timestamp = datetime.now().isoformat()

            # Calculate session metrics
            total_questions = len(answers)
            correct_answers = sum(1 for answer in answers.values()
                                  if answer.get('correct', False))
            skipped_questions = sum(1 for answer in answers.values()
                                    if answer.get('skipped', False))
            response_times = [
                answer.get('response_time', 0) for answer in answers.values()
            ]

            accuracy = correct_answers / total_questions if total_questions > 0 else 0
            engagement = 1 - (skipped_questions /
                              total_questions) if total_questions > 0 else 0
            avg_response_time = sum(response_times) / len(
                response_times) if response_times else 0

            # Create log entries for each question
            log_entries = []

            for question_id, answer_data in answers.items():
                log_entry = {
                    'student_id': student_id,
                    'timestamp': timestamp,
                    'question_id': question_id,
                    'answer': answer_data.get('answer', ''),
                    'correct': answer_data.get('correct', False),
                    'skipped': answer_data.get('skipped', False),
                    'response_time': answer_data.get('response_time', 0),
                    'accuracy': accuracy,
                    'engagement': engagement,
                    'avg_response_time': avg_response_time,
                    'session_id': session_id
                }
                log_entries.append(log_entry)
                self.in_memory_logs.append(log_entry)

                question_row = questions[questions["question_id"] == question_id].iloc[0]

                log_entry.update({
                    "topic": question_row["topic"],
                    "difficulty": question_row["difficulty"]
                })

            # Append to CSV file
            new_df = pd.DataFrame(log_entries)

            # Read existing data and append
            try:
                existing_df = pd.read_csv(self.log_file)
                combined_df = pd.concat([existing_df, new_df],
                                        ignore_index=True)
            except (pd.errors.EmptyDataError, FileNotFoundError):
                combined_df = new_df

            # Save to file
            combined_df.to_csv(self.log_file, index=False)

            return True

        except Exception as e:
            print(f"Error logging quiz attempt: {e}")
            return False

    def get_student_logs(self, student_id: str) -> pd.DataFrame:
        """Get all logs for a specific student"""
        try:
            df = pd.read_csv(self.log_file)
            return df[df['student_id'] == student_id]
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame()

    def get_all_logs(self) -> pd.DataFrame:
        """Get all logged data"""
        try:
            return pd.read_csv(self.log_file)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame()

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary for a specific session"""
        try:
            df = pd.read_csv(self.log_file)
            session_data = df[df['session_id'] == session_id]

            if session_data.empty:
                return {}

            # Get the first row for session-level metrics
            first_row = session_data.iloc[0]

            return {
                'student_id': first_row['student_id'],
                'timestamp': first_row['timestamp'],
                'total_questions': len(session_data),
                'correct_answers': session_data['correct'].sum(),
                'accuracy': first_row['accuracy'],
                'engagement': first_row['engagement'],
                'avg_response_time': first_row['avg_response_time'],
                'questions_skipped': session_data['skipped'].sum()
            }

        except Exception as e:
            print(f"Error getting session summary: {e}")
            return {}

    def get_student_performance_summary(self,
                                        student_id: str) -> Dict[str, Any]:
        """Get performance summary for a student across all sessions"""
        try:
            student_logs = self.get_student_logs(student_id)

            if student_logs.empty:
                return {
                    'total_sessions': 0,
                    'total_questions': 0,
                    'overall_accuracy': 0.0,
                    'average_engagement': 0.0,
                    'average_response_time': 0.0,
                    'improvement_trend': 'No data'
                }

            # Group by session to get session-level metrics
            session_groups = student_logs.groupby('session_id')
            session_summaries = []

            for session_id, session_data in session_groups:
                first_row = session_data.iloc[0]
                session_summaries.append({
                    'session_id':
                    session_id,
                    'timestamp':
                    first_row['timestamp'],
                    'accuracy':
                    first_row['accuracy'],
                    'engagement':
                    first_row['engagement'],
                    'avg_response_time':
                    first_row['avg_response_time']
                })

            sessions_df = pd.DataFrame(session_summaries)

            # Calculate overall metrics
            total_sessions = len(sessions_df)
            total_questions = len(student_logs)
            overall_accuracy = sessions_df['accuracy'].mean()
            average_engagement = sessions_df['engagement'].mean()
            average_response_time = sessions_df['avg_response_time'].mean()

            # Calculate improvement trend
            if len(sessions_df) >= 2:
                first_half_accuracy = sessions_df.head(len(sessions_df) //
                                                       2)['accuracy'].mean()
                second_half_accuracy = sessions_df.tail(len(sessions_df) //
                                                        2)['accuracy'].mean()

                if second_half_accuracy > first_half_accuracy + 0.05:
                    improvement_trend = 'Improving'
                elif second_half_accuracy < first_half_accuracy - 0.05:
                    improvement_trend = 'Declining'
                else:
                    improvement_trend = 'Stable'
            else:
                improvement_trend = 'Insufficient data'

            return {
                'total_sessions': total_sessions,
                'total_questions': total_questions,
                'overall_accuracy': round(overall_accuracy, 3),
                'average_engagement': round(average_engagement, 3),
                'average_response_time': round(average_response_time, 2),
                'improvement_trend': improvement_trend,
                'sessions': session_summaries
            }

        except Exception as e:
            print(f"Error calculating student performance summary: {e}")
            return {}

    def export_logs(self, filename: str = None) -> str:
        """Export logs to a CSV file"""
        if filename is None:
            filename = f"quiz_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            df = self.get_all_logs()
            export_path = os.path.join('data', filename)
            df.to_csv(export_path, index=False)
            return export_path
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return ""

    def clear_logs(self, confirm: bool = False) -> bool:
        """Clear all logs (use with caution)"""
        if not confirm:
            return False

        try:
            # Create empty DataFrame with headers
            empty_df = pd.DataFrame(columns=[
                'student_id', 'timestamp', 'question_id', 'answer', 'correct',
                'skipped', 'response_time', 'accuracy', 'engagement',
                'avg_response_time', 'session_id'
            ])
            empty_df.to_csv(self.log_file, index=False)
            self.in_memory_logs = []
            return True
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return False


def create_sample_logs():
    """Create sample log data for testing"""
    logger = QuizLogger()

    # Sample data for testing
    sample_questions = pd.DataFrame({
        'question_id': ['q1', 'q2', 'q3', 'q4', 'q5'],
        'topic': ['fractions', 'algebra', 'geometry', 'fractions', 'algebra'],
        'difficulty': [1, 2, 2, 1, 3],
        'text': [
            'What is 1/2 + 1/3?', 'Solve 2x + 3 = 11',
            'Find the area of a rectangle with length 5 and width 3',
            'What is 3/4 - 1/4?', 'Solve x² - 5x + 6 = 0'
        ]
    })

    sample_answers = {
        'q1': {
            'answer': '5/6',
            'correct': True,
            'skipped': False,
            'response_time': 23.5
        },
        'q2': {
            'answer': '4',
            'correct': True,
            'skipped': False,
            'response_time': 31.2
        },
        'q3': {
            'answer': '15',
            'correct': True,
            'skipped': False,
            'response_time': 18.7
        },
        'q4': {
            'answer': '1/2',
            'correct': True,
            'skipped': False,
            'response_time': 15.3
        },
        'q5': {
            'answer': '',
            'correct': False,
            'skipped': True,
            'response_time': 45.0
        }
    }

    # Log sample attempt
    logger.log_attempt('s1', sample_questions, sample_answers)

    print("Sample logs created successfully!")
    return logger


if __name__ == "__main__":
    # Test the logger
    logger = create_sample_logs()

    # Test retrieval functions
    all_logs = logger.get_all_logs()
    print(f"Total log entries: {len(all_logs)}")

    student_summary = logger.get_student_performance_summary('s1')
    print(f"Student s1 summary: {student_summary}")
