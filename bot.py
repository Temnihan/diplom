import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, ConversationHandler
from datetime import datetime
import tasks
print(dir(tasks))  # Вывод всех атрибутов и методов модуля tasks 
import analysis

# Состояния для ConversationHandler
AGE, GRADE = range(2)

def create_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Создание таблицы для пользователей
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                timestamp TEXT,
                age INTEGER,
                grade INTEGER
            )
        ''')
        print("Таблица users создана или уже существует.")

        # Создание таблицы для примеров и ответов
        c.execute('''
            CREATE TABLE IF NOT EXISTS examples (
                user_id INTEGER,
                example TEXT,
                answer INTEGER,
                time_spent REAL,
                correct INTEGER,
                PRIMARY KEY (user_id, example)
            )
        ''')
        print("Таблица examples создана или уже существует.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")

def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name or update.message.from_user.username

    update.message.reply_text(f"Привет, {name}!")
    user_level = tasks.get_user_level(user_id)
    
    if user_level is not None:  
        update.message.reply_text(f"Вам уже присвоен уровень{user_level}.. Начнем с него.")
        tasks.start_level(user_id, user_level, update)  # Добавляем update
        return ConversationHandler.END
    else:
        update.message.reply_text("Привет! Сколько вам лет?")  # Спрашиваем возраст
        return AGE  # Переходим к состоянию AGE


def ask_age(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text.isdigit() and 0 < int(text) < 120:
        age = int(text)
        tasks.save_user(user_id, age=age)
        update.message.reply_text("За какой класс хотел бы пройти математику?")
        return GRADE  # Переходим к состоянию GRADE
    else:
        update.message.reply_text("Пожалуйста, введите корректный возраст.")
        return AGE  # Остаёмся на состоянии AGE

def ask_grade(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text.isdigit() and 1 <= int(text) <= 11:
        grade = int(text)
        tasks.save_user(user_id, grade=grade)
        update.message.reply_text(f"Ваш уровень {grade} сохранен!")
        tasks.start_level(user_id, grade)  # Начинаем уровень для пользователя
        return ConversationHandler.END  # Завершаем разговор
    else:
        update.message.reply_text("Пожалуйста, введите корректный уровень.")
        return GRADE  # Остаёмся на состоянии GRADE

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text

    if 'current_task' in context.user_data:
        # Обработка ответа на текущее задание
        start_time = context.user_data['start_time']
        elapsed_time = datetime.now().timestamp() - start_time
        is_correct = tasks.check_answer(user_id, text, elapsed_time)
        if is_correct:
            update.message.reply_text("Верно!")
            context.user_data.pop('current_task', None)
            context.user_data.pop('start_time', None)
            # Начинаем следующий уровень или задачу
            tasks.start_level(user_id)
        else:
            update.message.reply_text("Неверно. Попробуйте еще раз.")
            # Добавляем задачу с тем же числом
            tasks.repeat_task(user_id, context)
    else:
        update.message.reply_text("Я не понимаю этот запрос.")

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Диалог отменён.')
    return ConversationHandler.END

def main() -> None:
    create_db()  # Сначала создаем базу данных и таблицу, если её еще нет
    updater = Updater("7301174197:AAGIGf2rwsSJRKJulnIqSqcGsD0gVidAKkU", use_context=True)
    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGE: [MessageHandler(Filters.text & ~Filters.command, ask_age)],
            GRADE: [MessageHandler(Filters.text & ~Filters.command, ask_grade)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
