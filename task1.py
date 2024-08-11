import random
import sqlite3
from datetime import datetime

def generate_example(level):
    if level == 2:
        return generate_level_2_example()
    elif level == 3:
        return generate_level_3_example()
    # Добавьте дополнительные уровни по мере необходимости

def generate_level_2_example():
    base_number = random.randint(1, 9) * 10 + random.randint(1, 9)
    increment = random.randint(6, 9)
    example = f"{base_number} + {increment}"
    answer = base_number + increment
    return example, answer

def generate_level_3_example():
    num1 = random.randint(10, 99)
    num2 = random.randint(1, 99)
    increment = 5 if random.choice([True, False]) else 6
    example = f"{num1} + {num2} (прибавляем {increment})"
    answer = num1 + num2
    return example, answer

def save_user(user_id, age=None, grade=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = c.fetchone()
    
    if exists is None:
        c.execute("INSERT INTO users (user_id, timestamp, age, grade) VALUES (?, ?, ?, ?)",
                  (user_id, datetime.now(), age, grade))
    else:
        if age is not None:
            c.execute("UPDATE users SET age=? WHERE user_id=?", (age, user_id))
        if grade is not None:
            c.execute("UPDATE users SET grade=? WHERE user_id=?", (grade, user_id))
    
    conn.commit()
    conn.close()

def log_example(user_id, example, answer, correct, duration):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO examples (user_id, example, answer, time_spent, correct)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, example, answer, duration, int(correct)))
    conn.commit()
    conn.close()

def get_user_level(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT grade FROM users WHERE user_id = ?", (user_id,))
    level = c.fetchone()
    conn.close()
    return level[0] if level else 2  # По умолчанию уровень 2

def check_answer(user_id, answer, elapsed_time):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT example, answer FROM examples WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', (user_id,))
    last_example = c.fetchone()
    conn.close()

    if last_example:
        correct_answer = last_example[1]
        is_correct = int(answer) == correct_answer
        log_example(user_id, last_example[0], correct_answer, is_correct, elapsed_time)
        return is_correct
    return False

def start_level(user_id, grade):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    example, answer = generate_example(grade)
    c.execute('DELETE FROM examples WHERE user_id = ? AND example = ?', (user_id, example))
    conn.commit()
    conn.close()

    return example, answer

def repeat_task(user_id, context):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT example, answer FROM examples WHERE user_id = ? AND correct = 0 ORDER BY timestamp DESC LIMIT 1', (user_id,))
    last_example = c.fetchone()
    conn.close()

    if last_example:
        example, answer = last_example
        # Генерация нового примера с тем же фиксированным числом
        example, answer = generate_example(grade)
        # Возвращаем новый пример
        return example, answer
    return None, None
