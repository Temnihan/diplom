import sqlite3
import random
from datetime import datetime

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

def get_user_level(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT grade FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]  # Возвращаем уровень пользователя (grade)
    return None  # Если запись не найдена, возвращаем None

def start_level(user_id, grade, update):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    if grade == 2:
        task, answer = generate_task(user_id, 2)
    elif grade == 3:
        task, answer = generate_task(user_id, 3)
    # Другие уровни можно добавить здесь
    
    conn.close()

    # Отправка задания пользователю
    update.message.reply_text(f"Ваше задание: {task}")


def generate_task(user_id, level):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if level == 2:
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        example = f"{num1} + {num2}"
        answer = num1 + num2
    elif level == 3:
        num1 = random.randint(100, 999)
        num2 = random.randint(100, 999)
        example = f"{num1} + {num2}"
        answer = num1 + num2
    
    # Сохраняем задание в базе данных
    c.execute("INSERT INTO examples (user_id, example, answer, time_spent, correct) VALUES (?, ?, ?, ?, ?)",
              (user_id, example, answer, None, None))
    conn.commit()
    conn.close()

    return example, answer
def check_answer(user_id, text, elapsed_time):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT example, answer FROM examples WHERE user_id = ? AND correct IS NULL LIMIT 1", (user_id,))
    task = c.fetchone()
    
    if task:
        example, answer = task
        if int(text) == answer:
            c.execute("UPDATE examples SET time_spent=?, correct=1 WHERE user_id=? AND example=?", (elapsed_time, user_id, example))
            conn.commit()
            conn.close()
            return True
        else:
            c.execute("UPDATE examples SET correct=0 WHERE user_id=? AND example=?", (user_id, example))
            conn.commit()
            conn.close()
            return False
    conn.close()
    return False

def repeat_task(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT example FROM examples WHERE user_id = ? AND correct = 0 LIMIT 1", (user_id,))
    task = c.fetchone()
    
    if task:
        example = task[0]
        num1, num2 = map(int, example.split(" + "))
        fixed_num = num2
        new_num1 = random.randint(10, 99)
        new_example = f"{new_num1} + {fixed_num}"
        answer = new_num1 + fixed_num
        c.execute("INSERT INTO examples (user_id, example, answer, time_spent, correct) VALUES (?, ?, ?, ?, ?)",
                  (user_id, new_example, answer, None, None))
        conn.commit()
    
    conn.close()
