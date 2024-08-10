from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
import re
import sqlite3
from datetime import datetime
# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name

    # Проверяем, есть ли пользователь в базе данных
    user_data = get_user(user_id)

    # Записываем вход пользователя
    record_user_entry(user_id)

    if not user_data:
        # Если пользователя нет, добавляем его
        save_user(user_id)
        update.message.reply_text(f'Привет, {first_name}! Как твое имя?')
        context.user_data['awaiting_name'] = True
    else:
        if user_data['Name'] is None:
            update.message.reply_text('Как твое имя?')
            context.user_data['awaiting_name'] = True
        elif user_data['age'] is None:
            update.message.reply_text('Сколько вам лет?')
            context.user_data['awaiting_age'] = True
        else:
            update.message.reply_text(f'Привет снова, {user_data["Name"]}!')


# Функция для обработки текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    # Проверка, хочет ли пользователь изменить имя
    if 'сменить имя' in text or 'изменить имя' in text or 'новое имя' in text:
        update.message.reply_text('Какое новое имя ты хочешь использовать?')
        context.user_data['waiting_for_new_name'] = True
        return  # Завершаем функцию, чтобы не обрабатывать это сообщение как обычное

    # Получение данных пользователя
    user_data = get_user(user_id)

    # Проверка, если имя еще не введено
    if user_data['Name'] is None and context.user_data.get('awaiting_name'):
        if is_valid_name(text):
            update_user_name(user_id, text)
            update.message.reply_text(f'Приятно познакомиться, {text}!')
            context.user_data['awaiting_name'] = False
            context.user_data['awaiting_age'] = True
            update.message.reply_text('Сколько вам лет?')
        else:
            update.message.reply_text('Похоже, это не имя. Попробуй снова.')
        return

    # Проверка на ввод возраста
    if context.user_data.get('awaiting_age'):
        if text.isdigit() and 0 < int(text) < 120:  # Простая проверка возраста
            update_user_age(user_id, int(text))
            update.message.reply_text(f'Ваш возраст успешно обновлен на {text} лет!')
            context.user_data['awaiting_age'] = False
        else:
            update.message.reply_text('Пожалуйста, введите корректный возраст.')
        return

    # Обработка некорректного имени
    if context.user_data.get('waiting_for_new_name'):
        if is_valid_name(text):
            update_user_name(user_id, text)
            update.message.reply_text(f'Имя успешно изменено на {text}!')
            context.user_data['waiting_for_new_name'] = False
        else:
            update.message.reply_text('Это не похоже на имя. Попробуй снова.')
        return

    # Приветствие пользователя, если все данные уже введены
    if user_data['Name'] is not None:
        update.message.reply_text(f'Привет снова, {user_data["Name"]}!')


# Получение данных пользователя
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if user:
        return {
            'user_id': user[0],
            'Name': user[1],
            'P_Name1': user[2],
            'P_Name2': user[3],
            'P_Name3': user[4],
            'age': user[5]  # Добавляем поле age
        }
    return {
        'user_id': user_id,
        'Name': None,
        'P_Name1': None,
        'P_Name2': None,
        'P_Name3': None,
        'age': None  # Обеспечиваем наличие ключа age
    }


def process_new_name(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('waiting_for_new_name'):
        user_id = update.message.from_user.id
        text = update.message.text

        if is_valid_name(text):
            update_user_name(user_id, text)
            update.message.reply_text(f'Имя успешно изменено на {text}!')
            context.user_data['waiting_for_new_name'] = False
        else:
            update.message.reply_text('Это не похоже на имя. Попробуй снова.')

# Проверка корректности имени
def is_valid_name(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Zа-яА-ЯёЁ]+$', name))

# Сохранение пользователя в базе данных
def save_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()

    if user is None:
        c.execute("INSERT INTO users (user_id, timestamp, age) VALUES (?, ?, ?)", (user_id, datetime.now(), None))
        conn.commit()
        print(f"Добавлен новый пользователь: {user_id}")
    else:
        c.execute("UPDATE users SET timestamp=? WHERE user_id=?", (datetime.now(), user_id))
        conn.commit()
        print(f"Обновлена метка времени для пользователя: {user_id}")

    conn.close()

# Обновление имени пользователя
def update_user_name(user_id, name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET Name=? WHERE user_id=?", (name, user_id))
    conn.commit()
    conn.close()
def update_user_age(user_id, age):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET age=? WHERE user_id=?", (age, user_id))
    conn.commit()
    conn.close()


# Обработка некорректного имени
def handle_invalid_name(user_id, invalid_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT P_Name1, P_Name2 FROM users WHERE user_id=?", (user_id,))
    p_name1, p_name2 = c.fetchone()

    if p_name1 is None:
        c.execute("UPDATE users SET P_Name1=? WHERE user_id=?", (invalid_name, user_id))
    elif p_name2 is None:
        c.execute("UPDATE users SET P_Name2=? WHERE user_id=?", (invalid_name, user_id))
    else:
        c.execute("UPDATE users SET P_Name3=? WHERE user_id=?", (invalid_name, user_id))
        if invalid_name == p_name1 == p_name2:
            c.execute("UPDATE users SET Name=?, P_Name1=NULL, P_Name2=NULL, P_Name3=NULL WHERE user_id=?", 
                      (invalid_name, user_id))

    conn.commit()
    conn.close()

# Создание базы данных (если еще не создана)
def create_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Создание таблицы для пользователей
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                Name TEXT,
                P_Name1 TEXT,
                P_Name2 TEXT,
                P_Name3 TEXT,
                timestamp TEXT,
                age INTEGER  
            )
        ''')
        print("Таблица users создана или уже существует.")

        # Создание таблицы для подсчета входов
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_entries (
                user_id INTEGER,
                entry_date TEXT,
                entry_count INTEGER,
                PRIMARY KEY (user_id, entry_date)
            )
        ''')
        print("Таблица user_entries создана или уже существует.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")

# Функция для получения статистики посещений

# счетчик входа
def record_user_entry(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Попробуем обновить запись
    c.execute('''
        INSERT INTO user_entries (user_id, entry_date, entry_count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, entry_date) 
        DO UPDATE SET entry_count = entry_count + 1
    ''', (user_id, today_date))

    conn.commit()
    conn.close()

def get_user_entry_stats(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT entry_date, entry_count FROM user_entries
        WHERE user_id=?
    ''', (user_id,))
    
    entries = c.fetchall()
    conn.close()
    
    return entries
    # это статистика  его еще в main добавить dispatcher.add_handler(CommandHandler("stats", stats))
def stats(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    entries = get_user_entry_stats(user_id)
    if entries:
        response = "Ваша статистика посещений:\n"
        for entry_date, entry_count in entries:
            response += f"{entry_date}: {entry_count} входов\n"
    else:
        response = "Нет данных о ваших посещениях."
    
    update.message.reply_text(response)


# Основной блок запуска бота
def main() -> None:
    create_db()  # Сначала создаем базу данных и таблицу, если её еще нет
    updater = Updater("7301174197:AAGIGf2rwsSJRKJulnIqSqcGsD0gVidAKkU", use_context=True)
    dispatcher = updater.dispatcher

    # Обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CommandHandler("stats", stats))
    
    # Обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

 

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
