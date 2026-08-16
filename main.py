import os
import random
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖКИ РАБОТЫ НА RENDER ---
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

# --- КЛЮЧИ И ИНИЦИАЛИЗАЦИЯ ---
BOT_TOKEN = "8707742030:AAGRAQir0UimjP93MSBRdDJVfH80FIxOjSM"
KINO_TOKEN = "MT8XHBK-G7VMM0M-JPZYHK4-DXN85K9"
bot = telebot.TeleBot(BOT_TOKEN)

# Жанры: название на кнопке -> название в базе Кинопоиска
GENRES = {
    "action": "боевик",
    "comedy": "комедия",
    "thriller": "триллер",
    "scifi": "фантастика",
    "horror": "ужасы",
    "drama": "драма"
}

def get_movie_from_api(category="random"):
    url = "https://api.kinopoisk.dev/v1.4/movie/random"
    headers = {"X-API-KEY": KINO_TOKEN}
    
    params = {
        "type": "movie",
        "rating.kp": "6.5-10",
        "notNullFields": ["name", "description", "poster.url"]
    }
    
    # Фильтр для новинок (свежие релизы)
    if category == "new":
        params["year"] = "2024-2026"
    # Фильтр по жанру
    elif category in GENRES:
        params["genres.name"] = GENRES[category]
        
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Ошибка запроса к Кинопоиску:", e)
    return None

def get_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_random = types.KeyboardButton("🎲 Любой случайный")
    btn_new = types.KeyboardButton("🔥 Новинки")
    btn_action = types.KeyboardButton("💥 Боевик")
    btn_comedy = types.KeyboardButton("😂 Комедия")
    btn_thriller = types.KeyboardButton("🍿 Триллер")
    btn_scifi = types.KeyboardButton("🚀 Фантастика")
    btn_horror = types.KeyboardButton("😱 Ужасы")
    btn_drama = types.KeyboardButton("🎭 Драма")
    
    markup.add(btn_random, btn_new)
    markup.add(btn_action, btn_comedy)
    markup.add(btn_thriller, btn_scifi)
    markup.add(btn_horror, btn_drama)
    return markup

def get_inline_keyboard(category, kp_id=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопка повтора в этой же категории
    markup.add(types.InlineKeyboardButton("🔄 Выдать другой фильм", callback_data=f"next_{category}"))
    
    # Ссылка на страницу Кинопоиска
    if kp_id:
        markup.add(types.InlineKeyboardButton("🎬 Открыть на Кинопоиске", url=f"https://www.kinopoisk.ru/film/{kp_id}/"))
        
    return markup

def send_movie(chat_id, category):
    bot.send_message(chat_id, "⏳ Подбираю фильм из базы...")
    movie = get_movie_from_api(category)
    
    if movie:
        title = movie.get('name') or movie.get('alternativeName') or 'Без названия'
        year = movie.get('year', '')
        rating = movie.get('rating', {}).get('kp', 'Нет оценки')
        desc = movie.get('description') or 'Описание отсутствует.'
        poster = movie.get('poster', {}).get('url', '')
        kp_id = movie.get('id')
        
        # Получаем жанры строкой
        genres_list = [g.get('name') for g in movie.get('genres', []) if g.get('name')]
        genres_str = ", ".join(genres_list[:3]) if genres_list else "Кино"
        
        if len(desc) > 650:
            desc = desc[:650] + "..."
            
        text = (
            f"🍿 *{title}* ({year})\n"
            f"⭐️ *Рейтинг Кинопоиска:* {rating}\n"
            f"🎭 *Жанр:* {genres_str}\n\n"
            f"📝 *Описание:*\n{desc}"
        )
        
        reply_markup = get_inline_keyboard(category, kp_id)
        
        if poster:
            try:
                bot.send_photo(chat_id, poster, caption=text, parse_mode="Markdown", reply_markup=reply_markup)
            except Exception:
                bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        bot.send_message(chat_id, "Не удалось найти подходящий фильм с высоким рейтингом. Попробуй ещё раз!")

@bot.message_handler(commands=['start'])
def start_command(message):
    text = (
        "Привет! Выбирай категорию или жми на случайный фильм — "
        "я подберу только годное кино с нормальной оценкой 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu_keyboard())

# Обработка нажатий на кнопки внизу клавиатуры
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    text = message.text
    if text == "🎲 Любой случайный":
        send_movie(message.chat.id, "random")
    elif text == "🔥 Новинки":
        send_movie(message.chat.id, "new")
    elif text == "💥 Боевик":
        send_movie(message.chat.id, "action")
    elif text == "😂 Комедия":
        send_movie(message.chat.id, "comedy")
    elif text == "🍿 Триллер":
        send_movie(message.chat.id, "thriller")
    elif text == "🚀 Фантастика":
        send_movie(message.chat.id, "scifi")
    elif text == "😱 Ужасы":
        send_movie(message.chat.id, "horror")
    elif text == "🎭 Драма":
        send_movie(message.chat.id, "drama")

# Обработка нажатия на кнопку "🔄 Выдать другой фильм"
@bot.callback_query_handler(func=lambda call: call.data.startswith("next_"))
def handle_inline_callback(call):
    category = call.data.replace("next_", "")
    bot.answer_callback_query(call.id)
    send_movie(call.message.chat.id, category)

keep_alive()
print("Бот обновлен и запущен!")
bot.infinity_polling()
