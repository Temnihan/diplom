from telegram import Update
import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from task2 import generate_task
import time
# Чтобы бот реагировал на текстовые сообщения, добавим обработчик сообщений:
from telegram.ext import MessageHandler, Filters
# Замените 'YOUR_TOKEN_HERE' на токен, который вы получили от BotFather
TOKEN = '7301174197:AAGIGf2rwsSJRKJulnIqSqcGsD0gVidAKkU'
# Определяем стадии разговора
ASKING_QUESTION = 1
def create_db():
    try:
        conn = sqlite3.connect('users1.db')
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

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
def create_user_table(user_id: int):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('users1.db')
        c = conn.cursor()

        # Создаем имя таблицы для данного пользователя
        table_name = f"user_{user_id}"

        # Создаем таблицу с нужными полями
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN,
                time_spent REAL,
                timestamp TEXT
            )
        ''')

        print(f"Таблица {table_name} создана или уже существует.")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании таблицы для пользователя {user_id}: {e}")

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name or update.message.from_user.username
    context.user_data['user_id'] = user_id  # Сохраняем ID пользователя
    context.user_data['name'] = name  # Сохраняем имя пользователя
    update.message.reply_text(f'Привет! {name}.')  
    # Создаем таблицу для пользователя (если она не создана)
    create_user_table(user_id)
    return ask_question(update, context)  # Задаем первый вопрос     
def ask_question(update: Update, context: CallbackContext) -> int:
    # Генерация задачи и сохранение правильного ответа в user_data
    example, correct_answer =generate_task()
    context.user_data['correct_answer'] = correct_answer # как бы еще одна переменная для ожидания
    update.message.reply_text(f' сколькобудет {example}')
    context.user_data['start_time'] = time.time()  # Сохраняем время начала решения задачи

    return ASKING_QUESTION

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды: /start, /help')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def handle_answer(update: Update, context: CallbackContext) -> int:
    user_answer = str(update.message.text.strip())  # Удаление пробелов
    correct_answer = str(context.user_data.get('correct_answer'))
    name = context.user_data.get('name')
    start_time = context.user_data.get('start_time')  # Время начала
    time_spent = time.time() - start_time  # Время, затраченное на решение
    is_correct = user_answer == correct_answer  # Проверяем, правильный ли ответ
    save_user_result(context.user_data['user_id'], context.user_data.get('question'), user_answer, correct_answer, is_correct, time_spent)

    if is_correct:
        update.message.reply_text(f'Good!')
    else:
        update.message.reply_text(f'Bad.')

    # Завершение разговора
    return  ask_question(update, context)  # Продолжаем задавать вопросы
def save_user_result(user_id: int, question: str, user_answer: str, correct_answer: str, is_correct: bool, time_spent: float):
    try:
        conn = sqlite3.connect('users1.db')
        c = conn.cursor()
        table_name = f"user_{user_id}"

        # Вставляем данные в таблицу
        c.execute(f'''
            INSERT INTO {table_name} (question, user_answer, correct_answer, is_correct, time_spent, timestamp)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (question, user_answer, correct_answer, is_correct, time_spent))

        conn.commit()
        conn.close()
        print(f"Результаты для пользователя {user_id} успешно сохранены.")
    except Exception as e:
        print(f"Ошибка при сохранении данных для пользователя {user_id}: {e}")

def main() -> None:
    # Создание updater и передача токена
    updater = Updater(TOKEN)

    # Получение диспетчера для обработки команд
    dispatcher = updater.dispatcher
    # Создание ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASKING_QUESTION: [MessageHandler(Filters.text & ~Filters.command, handle_answer)],
        },
        fallbacks=[],
    )
    
    # Добавление обработчиков
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    # Запуск бота
    updater.start_polling()

    # Ожидание завершения работы
    updater.idle()

if __name__ == '__main__':
    create_db()
    main()