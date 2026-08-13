# 📊 Math Tutor Bot — AI-Powered Adaptive Learning

A Telegram bot that generates personalized math exercises for students and uses **machine learning** to adapt difficulty based on individual performance patterns.

## 🎯 What It Does

- Generates math tasks (addition, subtraction, multiplication, division) tailored to student's grade level
- Tracks every answer: correctness, time spent, number properties
- Uses a **Random Forest classifier** to predict which types of problems a student will struggle with
- Provides performance analytics: accuracy rate, average response time, weak areas
- Stores all data in **SQLite** for persistent tracking

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Bot Framework | python-telegram-bot |
| Database | SQLite |
| Data Analysis | pandas |
| Machine Learning | scikit-learn (RandomForestClassifier) |
| Language | Python 3 |

## 📁 Project Structure

```
├── bot.py              # Main Telegram bot (v1) — user registration, task flow
├── main_bot_v3.py      # Enhanced bot (v3) — conversation handler, improved UX
├── analysis.py         # Performance analytics — accuracy, timing, statistics
├── model_update_v3.py  # ML model — trains on user data, predicts difficulty
├── task_v3.py          # Task generator — creates math problems by difficulty
├── tasks.py            # Task utilities
├── users.db            # SQLite database (user data + answers)
└── requirements.txt    # Dependencies
```

## 🧠 ML Pipeline

```
Student answers → SQLite DB → pandas DataFrame → Feature extraction
    → RandomForestClassifier training → Difficulty prediction
    → Adaptive task generation
```

**Features used for prediction:**
- `num1`, `num2` — operands
- `d1`, `d2` — digit counts
- `ones` — number of single-digit operations
- `width` — result magnitude

## 📈 Key Metrics Tracked

- Total tasks completed
- Correct vs incorrect answers
- Average time per task
- Accuracy by operation type (+, −, ×, ÷)
- Difficulty progression over time

## 🚀 How to Run

```bash
pip install -r requirements.txt
python bot.py
```

## 💡 Use Cases

- **Math tutoring** — personalized homework generation
- **Education analytics** — track student progress over time
- **Adaptive learning** — ML-driven difficulty adjustment
- **Parent/teacher dashboards** — performance reports

## 📝 About

Built as a diploma project for GeekBrains AI/Data Science program (2024).
Combines education domain expertise with practical ML application.

**Author:** Ruslan Lukmanov — [GitHub](https://github.com/Temnihan)
