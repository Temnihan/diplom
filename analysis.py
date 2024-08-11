import sqlite3

def analyze_performance(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        c.execute('''
            SELECT example, correct, time_spent
            FROM examples
            WHERE user_id = ?
        ''', (user_id,))
        
        examples = c.fetchall()

        if not examples:
            return {
                'total_examples': 0,
                'correct_answers': 0,
                'incorrect_answers': 0,
                'average_duration': 0
            }

        correct_answers = [ex for ex in examples if ex[1]]
        incorrect_answers = [ex for ex in examples if not ex[1]]

        total_duration = sum(ex[2] for ex in examples)
        average_duration = total_duration / len(examples) if examples else 0

        performance = {
            'total_examples': len(examples),
            'correct_answers': len(correct_answers),
            'incorrect_answers': len(incorrect_answers),
            'average_duration': average_duration
        }

    except sqlite3.Error as e:
        print(f"Ошибка при анализе производительности: {e}")
        performance = {
            'total_examples': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'average_duration': 0
        }
    
    finally:
        conn.close()

    return performance
