import os
import telebot
from telebot import types
import requests
from flask import Flask
from threading import Thread

# --- СЕРВЕР ---
app = Flask('')

@app.route('/')
def home():
    return "Бот работает 24/7!"

def run():
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- БОТ ---
BOT_TOKEN = "8707742030:AAGRAQir0UimjP93MSBRdDJVfH80FIxOjSM"
KINO_TOKEN = "MT8XHBK-G7VMM0M-JPZYHK4-DXN85K9"
bot = telebot.TeleBot(BOT_TOKEN)

def get_random_movie():
    url = "https://api.kinopoisk.dev/v1.4/movie/random"
    headers = {"X-API-KEY": KINO_TOKEN}
    params = {"type": "movie", "rating.kp": "6-10", "notNullFields": ["name", "description", "poster.url"]}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Ошибка связи с базой:", e)
    return None

def get_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Выдать другой фильм", callback_data="random"))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я подключен к базе Кинопоиска. Жми на кнопку ниже 👇",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("🎬 Случайный фильм")
    )

def send_movie_logic(chat_id):
    bot.send_message(chat_id, "⏳ Ищу крутое кино в базе...")
    movie = get_random_movie()
    
    if movie:
        title = movie.get('name', 'Без названия')
        year = movie.get('year', '')
        rating = movie.get('rating', {}).get('kp', 'Нет оценки')
        desc = movie.get('description', 'Описание отсутствует.')
        poster = movie.get('poster', {}).get('url', '')
        
        if len(desc) > 700:
            desc = desc[:700] + "..."
            
        text = f"🍿 *{title}* ({year})\n⭐️ *Рейтинг:* {rating}\n\n📝 *Описание:*\n{desc}"
        
        if poster:
            bot.send_photo(chat_id, poster, caption=text, parse_mode="Markdown", reply_markup=get_inline_keyboard())
        else:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_inline_keyboard())
    else:
        bot.send_message(chat_id, "База сейчас недоступна, попробуй чуть позже.")

@bot.message_handler(func=lambda message: message.text == "🎬 Случайный фильм")
def handle_text_button(message):
    send_movie_logic(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "random")
def handle_inline_button(call):
    bot.answer_callback_query(call.id) 
    send_movie_logic(call.message.chat.id)

keep_alive()
print("Бот успешно запущен!")
bot.infinity_polling()
