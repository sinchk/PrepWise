# PrepWise: AI Personalized Study Planner 📚🤖

### **Project Track:** AI for Personalized Learning (Recommendation System + ML)

## 📖 **Project Overview**
**PrepWise** is an intelligent, data-driven study scheduling system designed to solve the problem of inefficient academic planning. Unlike generic timetables, this system utilizes a **Hybrid Recommendation Engine** and **Machine Learning Regression** to generate adaptive study plans tailored to a student's learning pace, current stress levels, and exam deadlines .

[cite_start]The system addresses core student challenges such as poor time management, lack of prioritization, and academic burnout by dynamically allocating study hours where they are most needed.

---

## 🛠️ **Technical Architecture & Logic**

### **1. Data Strategy (Synthetic Generation)**
Due to privacy constraints with real-world student data, this project implements a robust **Synthetic Data Generation** module to create realistic training data.
* **Student Profiles:** Simulates attributes like `Student Type` (Fast Learner, Needs Support), `Stress Level`, and `Average Study Capacity`.
* **Performance Metrics:** Generates subject-wise scores, confidence levels, and identifies "Weak Areas" (<60% performance).
* **Feature Engineering:** Creates critical ML features such as **`Study Urgency`** (calculated from performance gaps and exam priority) and **`Priority Score`**.

### **2. Machine Learning Algorithms**
The core intelligence is built upon a **Hybrid Approach** combining three distinct techniques:

1.  **Collaborative Filtering (User-Based):**
    * **Technique:** Cosine Similarity.
    * **Logic:** Identifies peers with similar performance patterns and recommends study strategies that worked for successful similar students.

2.  **Content-Based Filtering:**
    * **Technique:** Attribute matching (Subject Difficulty, Credit Weightage).
    * **Logic:** Ensures difficult or high-stakes subjects are recommended even if the student has no prior history with them (solving the "Cold Start" problem).

3.  **Predictive Modeling (Random Forest Regressor):**
    * **Model:** Random Forest Regressor.
    * **Input Features:** `Current Score`, `Days Remaining`, `Study Urgency`, `Stress Level`, `Difficulty`.
    * **Target:** `Optimal Study Hours`.
    * **Why Random Forest?** Handles non-linear relationships (e.g., high stress ≠ more study hours) and provides feature importance.

### **3. The Recommendation Engine**
The final schedule is generated using a weighted ensemble formula:
$$\text{Hybrid Score} = (0.4 \times \text{ML Prediction}) + (0.3 \times \text{Collaborative}) + (0.3 \times \text{Content-Based})$$

---

## 🚀 **Key Features**

* **Adaptive Scheduling:** Automatically scales study hours based on "Days Remaining" until the exam.
* **Stress-Aware Planning:** Respects the student's `Stress Level` (High/Medium/Low) by limiting maximum daily study hours to prevent burnout.
* **Weak Area Prioritization:** Automatically detects and prioritizes subjects where confidence or scores are low.
* **Scenario Handling:** Adapts plans differently for "Fast Learners" (efficiency-focused) vs. "Inconsistent Learners" (structure-focused).

---

## 📊 **Evaluation & Results**

The model was rigorously evaluated using quantitative metrics and scenario testing:

* **Model Accuracy:** The Random Forest Regressor achieved an **$R^2$ Score of >0.98** and a low **MAE (Mean Absolute Error) of ~0.08 hours**, indicating highly reliable study hour predictions.
* **Recommendation Precision:** The system successfully identified **student weak areas** in the top 3 recommendations with high accuracy.
* **Feature Importance:** The model identified `Current Score` and `Difficulty` as the most significant factors driving study time allocation.

---

## 💻 **Dependencies & Usage**

**Requirements:**
* Python 3.x
* Libraries: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`.

**How to Run:**
1.  Open the `.ipynb` file in Jupyter Notebook or Google Colab.
2.  Run the cells sequentially from top to bottom.
3.  **Customization:** You can modify the `generate_student_profiles` parameters to simulate different class sizes or student types.

---

## ⚖️ **Ethical Considerations**
The project explicitly addresses **Responsible AI**:
* **Bias Mitigation:** Prevents "Performance Bias" by capping loads for struggling students to avoid overwhelming them.
* **Transparency:** All recommendations are explainable based on clear metrics (urgency, difficulty), ensuring the student understands *why* a subject is prioritized.

---

**Author:** Sinchana Kulkarni
**Date:** 17-01-2026
