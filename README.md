# PrepWise: AI Personalized Study Planner 📚🤖

### **Project Track:** AI for Personalized Learning (Recommendation System + ML)

## 📖 **Project Overview**
**PrepWise** is an intelligent, data-driven study scheduling system designed to solve the problem of inefficient academic planning. [cite_start]Unlike generic timetables, this system utilizes a **Hybrid Recommendation Engine** and **Machine Learning Regression** to generate adaptive study plans tailored to a student's learning pace, current stress levels, and exam deadlines [cite: 7-8].

[cite_start]The system addresses core student challenges such as poor time management, lack of prioritization, and academic burnout by dynamically allocating study hours where they are most needed [cite: 21-26].

---

## 🛠️ **Technical Architecture & Logic**

### **1. Data Strategy (Synthetic Generation)**
[cite_start]Due to privacy constraints with real-world student data, this project implements a robust **Synthetic Data Generation** module to create realistic training data[cite: 68].
* [cite_start]**Student Profiles:** Simulates attributes like `Student Type` (Fast Learner, Needs Support), `Stress Level`, and `Average Study Capacity`[cite: 70].
* [cite_start]**Performance Metrics:** Generates subject-wise scores, confidence levels, and identifies "Weak Areas" (<60% performance)[cite: 71, 152].
* [cite_start]**Feature Engineering:** Creates critical ML features such as **`Study Urgency`** (calculated from performance gaps and exam priority) and **`Priority Score`**[cite: 354, 377].

### **2. Machine Learning Algorithms**
[cite_start]The core intelligence is built upon a **Hybrid Approach** combining three distinct techniques [cite: 442-445]:

1.  **Collaborative Filtering (User-Based):**
    * [cite_start]**Technique:** Cosine Similarity[cite: 57].
    * [cite_start]**Logic:** Identifies peers with similar performance patterns and recommends study strategies that worked for successful similar students[cite: 443].

2.  **Content-Based Filtering:**
    * [cite_start]**Technique:** Attribute matching (Subject Difficulty, Credit Weightage)[cite: 444].
    * [cite_start]**Logic:** Ensures difficult or high-stakes subjects are recommended even if the student has no prior history with them (solving the "Cold Start" problem)[cite: 450].

3.  **Predictive Modeling (Random Forest Regressor):**
    * [cite_start]**Model:** Random Forest Regressor[cite: 445].
    * [cite_start]**Input Features:** `Current Score`, `Days Remaining`, `Study Urgency`, `Stress Level`, `Difficulty` [cite: 633-644].
    * **Target:** `Optimal Study Hours`.
    * [cite_start]**Why Random Forest?** Handles non-linear relationships (e.g., high stress ≠ more study hours) and provides feature importance [cite: 452-455].

### **3. The Recommendation Engine**
[cite_start]The final schedule is generated using a weighted ensemble formula[cite: 830, 873]:
$$\text{Hybrid Score} = (0.4 \times \text{ML Prediction}) + (0.3 \times \text{Collaborative}) + (0.3 \times \text{Content-Based})$$

---

## 🚀 **Key Features**

* [cite_start]**Adaptive Scheduling:** Automatically scales study hours based on "Days Remaining" until the exam[cite: 463].
* [cite_start]**Stress-Aware Planning:** Respects the student's `Stress Level` (High/Medium/Low) by limiting maximum daily study hours to prevent burnout[cite: 1484, 1559].
* [cite_start]**Weak Area Prioritization:** Automatically detects and prioritizes subjects where confidence or scores are low[cite: 1221].
* [cite_start]**Scenario Handling:** Adapts plans differently for "Fast Learners" (efficiency-focused) vs. "Inconsistent Learners" (structure-focused) [cite: 1449-1450].

---

## 📊 **Evaluation & Results**

[cite_start]The model was rigorously evaluated using quantitative metrics and scenario testing[cite: 1136]:

* [cite_start]**Model Accuracy:** The Random Forest Regressor achieved an **$R^2$ Score of >0.98** and a low **MAE (Mean Absolute Error) of ~0.08 hours**, indicating highly reliable study hour predictions[cite: 1228].
* [cite_start]**Recommendation Precision:** The system successfully identified **student weak areas** in the top 3 recommendations with high accuracy[cite: 1276].
* [cite_start]**Feature Importance:** The model identified `Current Score` and `Difficulty` as the most significant factors driving study time allocation [cite: 742-744].

---

## 💻 **Dependencies & Usage**

**Requirements:**
* Python 3.x
* [cite_start]Libraries: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn` [cite: 42-55].

**How to Run:**
1.  Open the `.ipynb` file in Jupyter Notebook or Google Colab.
2.  Run the cells sequentially from top to bottom.
3.  [cite_start]**Customization:** You can modify the `generate_student_profiles` parameters to simulate different class sizes or student types [cite: 1662-1666].

---

## ⚖️ **Ethical Considerations**
The project explicitly addresses **Responsible AI**:
* **Bias Mitigation:** Prevents "Performance Bias" by capping loads for struggling students to avoid overwhelming them [cite: 1482-1484].
* **Transparency:** All recommendations are explainable based on clear metrics (urgency, difficulty), ensuring the student understands *why* a subject is prioritized.

---

**Author:** Sinchana Kulkarni
**Date:** 17-01-2026
