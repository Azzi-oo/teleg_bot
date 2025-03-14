import telebot
import os
from telebot import types
import logging
import sqlite3

bot = telebot.TeleBot('7674701748:AAHGEGtpYtFZmYGYo6px7MzgAHFXLH4QHqI')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect('bot_database.db')
    return conn

def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        logger.info("Command /start from user %s", message.chat.id)
        bot.send_message(message.chat.id, "Welcome!")
    except telebot.apihelper.ApiException as e:
        logger.error("Error for messaging message %s", e)
        print(f"Error for send messaging: {e}")
        bot.send_message(message.chat.id, "Вышла ошибка при отправке сообщения")
    except Exception as e:
        logger.exception("uNDEFINED ERROR: %s", e)
        bot.send_message(message.chat.id, "Undefined error making")
    else:
        logger.info("Message successfull messaging %s", message.chat.id)
    finally:
        logger.info("Завершение обработки команды /start. %s", message.chat.id)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    button1 = types.InlineKeyboardButton('Кнопка 1', callback_data='data1')
    button2 = types.InlineKeyboardButton('Кнопка 2', callback_data='data2')
    
    keyboard.add(button1, button2)
    
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'data1':
        bot.send_message(call.message.chat.id, "Вы нажали кнопку 1")
        
    elif call.data == 'data2':
        bot.send_message(call.message.chat.id, "Вы нажали кнопку 2")

@bot.message_handler(commands=['help', 'about'])
def help_command(message):
    bot.reply_to(message, "Раздел помощи.")

# @bot.message_handler(content_types=['text'])
# def handle_text(message):
#     response = f"Вы написали: {message.text}"
#     bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['create'])
def create_user(message):
    msg = bot.reply_to(message, "Введите имя пользователя и возраст через пробел:")
    bot.register_next_step_handler(msg, process_create_step)
    
def process_create_step(message):
    try:
        username, age = message.text.split()
        age = int(age)
        create_users_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, age) VALUES (?, ?)", (username, age))
        conn.commit()
        conn.close()
        bot.reply_to(message, "User success create")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


@bot.message_handler(commands=['read'])
def read_user(message):
    msg = bot.reply_to(message, "Input name users:")
    bot.register_next_step_handler(msg, process_read_step)
    
def process_read_step(message):
    try:
        username = message.text
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            bot.reply_to(message, f"User: {user}")
        else:
            bot.reply_to(message, "User not found")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


@bot.message_handler(commands=['update'])
def update_user(message):
    msg = bot.reply_to(message, "Input name user's and new age, example Aza 20: ")
    bot.register_next_step_handler(msg, process_update_step)
    
def process_update_step(message):
    try:
        username, age = message.text.split()
        age = int(age)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET age = ? WHERE username = ?", (age, username))
        conn.commit()
        conn.close()
        bot.reply_to(message, "User successfull added")
    except Exception as e:
        bot.reply_to(message, f"Error do: {e}")
        
@bot.message_handler(commands=['delete'])
def delete_user(message):
    msg = bot.reply_to(message, "Input name users for delete:")
    bot.register_next_step_handler(msg, process_delete_step)
    
def process_delete_step(message):
    try:
        username = message.text 
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        bot.reply_to(message, "User successfull deleted!")
    except Exception as e:
        bot.reply_to(message, f"Error do: {e}")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("received_image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
        
    bot.reply_to(message, "Изображение получено и сохранено!")

@bot.message_handler(commands=['sendphoto'])
def send_photo(message):
    file_path = 'received_image.jpg'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.reply_to(message, "Файл не найден!")

@bot.message_handler(content_types=['documemt'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(message.document.file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
        
    bot.reply_to(message, "Документ получен и сохранен!")
    
@bot.message_handler(commands=['senddocument'])
def send_document(message):
    document = open('path_to_your_document.pdf', 'rb')
    bot.send_document(message.chat.id, document)

bot.polling()