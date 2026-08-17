import os
import random
import requests
import telebot
import time
import datetime
from telebot import types
from flask import Flask
from threading import Thread

# --- СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот работает 24/7 (Меню Жанров + Сериалы + Собачки)!"

def run():
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- КЛЮЧИ И БОТ ---
BOT_TOKEN = "8707742030:AAGRAQir0UimjP93MSBRdDJVfH80FIxOjSM"
KINO_TOKEN = "MT8XHBK-G7VMM0M-JPZYHK4-DXN85K9"
bot = telebot.TeleBot(BOT_TOKEN)

GENRES = {
    "action": "боевик",
    "comedy": "комедия",
    "thriller": "триллер",
    "scifi": "фантастика",
    "horror": "ужасы",
    "drama": "драма"
}

# --- БАЗА КИНОФАКТОВ ---
CINEMA_FACTS = [
    {"movie": "🎬 Властелин колец: Две крепости", "fact": "В сцене, где Арагорн пинает шлем орка и истошно кричит, крик был настоящим: Вигго Мортенсен сломал два пальца на ноге."},
    {"movie": "🎬 Бойцовский клуб", "fact": "Практически в каждой сцене фильма на заднем плане можно заметить бумажный стаканчик из Starbucks."},
    {"movie": "🎬 Темный рыцарь", "fact": "Когда Джокер взрывает больницу и взрыв задерживается, Хит Леджер искренне начал трясти детонатор — это чистая импровизация."},
    {"movie": "🎬 Джанго освобожденный", "fact": "Леонардо ДиКаприо случайно разбил ладонью стеклянный бокал во время монолога. Рука залилась кровью, но он доиграл дубль до конца."},
    {"movie": "🎬 Пираты Карибского моря", "fact": "Продюсеры Disney всерьез думали, что Джонни Депп пьян или сошел с ума из-за его манер и походки."}
]

# --- БАЗА ПИНТЕРЕСТ-СОБАК ---
FUNNY_DOGS = [
    {
        "url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&q=80&w=800",
        "caption": "Когда надел свое лучшее смарт-кэжуал пальто, но тебя всё равно назвали просто «хорошим мальчиком» 🧥"
    },
    {
        "url": "https://images.unsplash.com/photo-1561037404-61cd46aa615b?auto=format&fit=crop&q=80&w=800",
        "caption": "Этот парень явно планирует дзен-поездку к горе Фудзи, не мешайте ему 🌸🗻"
    },
    {
        "url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&q=80&w=800",
        "caption": "Лицо того, кто только что с треском проиграл в Монополию, но ему всё простят, потому что у него лапки 🎲🐶"
    },
    {
        "url": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&q=80&w=800",
        "caption": "Готов к пятничному киномарафону больше, чем ты 🍿"
    },
    {
        "url": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&q=80&w=800",
        "caption": "Случайно включил фронтальную камеру во время просмотра триллера 😱"
    }
]

# --- СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ДЛЯ РАССЫЛКИ ---
USERS_FILE = 'users.txt'

def save_user(chat_id):
    users = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = set(f.read().splitlines())
    
    if str(chat_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{chat_id}\n")

def get_all_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

# --- ФОНОВАЯ РАССЫЛКА (НАПОМИНАНИЯ) ---
def reminder_loop():
    while True:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        if now.weekday() in [4, 5] and now.hour == 19 and now.minute == 0:
            users = get_all_users()
            for user_id in users:
                try:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("🎲 Выбрать случайный", callback_data="next_random"))
                    bot.send_message(
                        user_id, 
                        "🍿 Пятничный вечер наступил!\n\nНе хочешь выбрать годный фильмец на вечер?", 
                        reply_markup=markup
                    )
                except Exception as e:
                    print(f"Не удалось отправить {user_id}: {e}")
            time.sleep(61)
        else:
            time.sleep(30)

Thread(target=reminder_loop, daemon=True).start()

# --- ТЕСТ: КТО ТЫ ИЗ ШРЕКА ---
user_quiz_state = {}
QUIZ_QUESTIONS = [
    {
        "text": "1️⃣ Идеальный вечер пятницы для тебя — это:",
        "answers": [("Сидеть на своем болоте", "shrek"), ("Ворваться в тусовку", "donkey"), ("Обольщать людей", "puss"), ("Командовать всеми", "farquaad")]
    },
    {
        "text": "2️⃣ Как ты реагируешь на гостей?",
        "answers": [("«ЧТО ВЫ ДЕЛАЕТЕ НА МОЕМ БОЛОТЕ?!»", "shrek"), ("«Ура, гости!»", "donkey"), ("Снимаю шляпу 🥺", "puss"), ("Вызываю охрану", "farquaad")]
    },
    {
        "text": "3️⃣ Твое отношение к романтике:",
        "answers": [("Главное — принимать друг друга", "shrek"), ("Любовь с первого взгляда!", "donkey"), ("Я одинокий волк 😼", "puss"), ("Мне нужен статус 👑", "farquaad")]
    },
    {
        "text": "4️⃣ Твое оружие в споре:",
        "answers": [("Тяжелый взгляд", "shrek"), ("Заболтать оппонента", "donkey"), ("Харизма и шпага", "puss"), ("Чужие руки", "farquaad")]
    }
]

CHARACTERS = {
    "shrek": {"name": "🧅 ТЫ — ШРЕК!", "desc": "Ты ценишь личные границы и уют. Снаружи ворчливый, но внутри преданный друг.", "image": "https://i.ibb.co/3sBw7W1/shrek.jpg"},
    "donkey": {"name": "🧇 ТЫ — ОСЕЛ!", "desc": "Душа компании! Оптимизм пробивает стены, а твоей смелости позавидует любой.", "image": "https://i.ibb.co/y4L2qT7/donkey.jpg"},
    "puss": {"name": "😼 ТЫ — КОТ В САПОГАХ!", "desc": "Невероятно харизматичный. Когда надо — строишь глазки, когда доходит до дела — достаешь шпагу.", "image": "https://i.ibb.co/h7n1h3k/puss.jpg"},
    "farquaad": {"name": "👑 ТЫ — ЛОРД ФАРКУАД!", "desc": "Человек грандиозных амбиций! Тебе нужны идеальные стандарты, все должны подчиняться твоим правилам.", "image": "https://i.ibb.co/q1zRk5p/farquaad.jpg"}
}

def start_quiz(chat_id):
    user_quiz_state[chat_id] = {"q_index": 0, "scores": {"shrek": 0, "donkey": 0, "puss": 0, "farquaad": 0}}
    send_quiz_question(chat_id)

def send_quiz_question(chat_id, message_id=None):
    state = user_quiz_state.get(chat_id)
    if not state:
        return
        
    q_idx = state["q_index"]
    question = QUIZ_QUESTIONS[q_idx]
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for ans_text, role in question["answers"]:
        markup.add(types.InlineKeyboardButton(ans_text, callback_data=f"quiz_{role}"))
        
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=question["text"], reply_markup=markup)
        except:
            pass
    else:
        bot.send_message(chat_id, question["text"], reply_markup=markup)

def finish_quiz(chat_id, message_id):
    state = user_quiz_state.get(chat_id)
    if not state:
        return
        
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass
        
    scores = state["scores"]
    best_char = max(scores, key=scores.get)
    result = CHARACTERS[best_char]
    text = f"✨ *ИТОГИ ТЕСТА:*\n\n*{result['name']}*\n\n{result['desc']}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Пройти тест заново", callback_data="quiz_restart"))
    
    try:
        bot.send_photo(chat_id, result['image'], caption=text, parse_mode="Markdown", reply_markup=markup)
    except:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
        
    del user_quiz_state[chat_id]

# --- КИНОПОИСК API ---
def get_movie_from_api(category="random"):
    url = "https://api.kinopoisk.dev/v1.4/movie/random"
    headers = {"X-API-KEY": KINO_TOKEN}
    params = {
        "rating.kp": "6.5-10", 
        "notNullFields": ["name", "description", "poster.url"]
    }
    
    if category == "series":
        params["type"] = "tv-series"
    else:
        params["type"] = "movie"
        
    if category == "new":
        params["year"] = "2024-2026"
    elif category in GENRES:
        params["genres.name"] = GENRES[category]
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Ошибка API:", e)
    return None

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🎲 Любой фильм"), types.KeyboardButton("🔥 Новинки"))
    markup.add(types.KeyboardButton("🎭 Выбрать по жанру"), types.KeyboardButton("📺 Сериалы"))
    markup.add(types.KeyboardButton("🧠 Кинофакт на вечер"), types.KeyboardButton("🧅 Тест: Кто ты из Шрека?"))
    markup.add(types.KeyboardButton("🐶 Собачка дня"))
    return markup

def get_genres_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("💥 Боевик"), types.KeyboardButton("😂 Комедия"))
    markup.add(types.KeyboardButton("🍿 Триллер"), types.KeyboardButton("🚀 Фантастика"))
    markup.add(types.KeyboardButton("😱 Ужасы"), types.KeyboardButton("😢 Драма"))
    markup.add(types.KeyboardButton("⬅️ Назад в меню"))
    return markup

def get_fact_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Еще один факт", callback_data="next_fact"))
    return markup

def get_dog_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Хочу другую собачку", callback_data="next_dog"))
    return markup

# --- ФУНКЦИИ ОТПРАВКИ ---
def send_fact(chat_id):
    fact_data = random.choice(CINEMA_FACTS)
    text = f"💡 *{fact_data['movie']}*\n\n{fact_data['fact']}"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_fact_keyboard())

def send_dog(chat_id):
    dog_data = random.choice(FUNNY_DOGS)
    try:
        bot.send_photo(chat_id, dog_data['url'], caption=dog_data['caption'], reply_markup=get_dog_keyboard())
    except Exception as e:
        bot.send_message(chat_id, "Ой, песель куда-то убежал! Попробуй еще раз.", reply_markup=get_dog_keyboard())

def send_movie(chat_id, category):
    msg = bot.send_message(chat_id, "⏳ Ищу в базе...")
    movie = get_movie_from_api(category)
    
    try:
        bot.delete_message(chat_id, msg.message_id)
    except:
        pass
    
    if movie:
        title = movie.get('name') or movie.get('alternativeName') or 'Без названия'
        year = movie.get('year', '')
        rating = movie.get('rating', {}).get('kp', 'Нет оценки')
        desc = movie.get('description') or 'Описание отсутствует.'
        poster = movie.get('poster', {}).get('url', '')
        kp_id = movie.get('id')
        genres_list = [g.get('name') for g in movie.get('genres', []) if g.get('name')]
        genres_str = ", ".join(genres_list[:3]) if genres_list else "Кино"
        
        media_type = "📺 Сериал" if category == "series" else "🍿 Фильм"
        
        if len(desc) > 650:
            desc = desc[:650] + "..."
            
        text = f"{media_type}: *{title}* ({year})\n⭐️ *Рейтинг Кинопоиска:* {rating}\n🎭 *Жанр:* {genres_str}\n\n📝 *Описание:*\n{desc}"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_text = "🔄 Выдать другой сериал" if category == "series" else "🔄 Выдать другой фильм"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"next_{category}"))
        
        if kp_id: 
            url_type = "series" if category == "series" else "film"
            markup.add(types.InlineKeyboardButton("🎬 Открыть на Кинопоиске", url=f"https://www.kinopoisk.ru/{url_type}/{kp_id}/"))
            
        if poster:
            try:
                bot.send_photo(chat_id, poster, caption=text, parse_mode="Markdown", reply_markup=markup)
            except:
                bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Не удалось найти ничего подходящего. Попробуй ещё раз!")

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---
@bot.message_handler(commands=['start'])
def start_command(message):
    save_user(message.chat.id)
    text = "Добро пожаловать! Выбирай жанр фильма, сериал или пройди тест 👇"
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    save_user(message.chat.id)
    text = message.text
    
    # Главное меню
    if text == "🎲 Любой фильм":
        send_movie(message.chat.id, "random")
    elif text == "🔥 Новинки":
        send_movie(message.chat.id, "new")
    elif text == "📺 Сериалы":
        send_movie(message.chat.id, "series")
    elif text == "🧠 Кинофакт на вечер":
        send_fact(message.chat.id)
    elif text == "🧅 Тест: Кто ты из Шрека?":
        start_quiz(message.chat.id)
    elif text == "🐶 Собачка дня":
        send_dog(message.chat.id)
    elif text == "🎭 Выбрать по жанру":
        bot.send_message(message.chat.id, "Выбирай жанр 👇", reply_markup=get_genres_keyboard())
    elif text == "⬅️ Назад в меню":
        bot.send_message(message.chat.id, "Главное меню", reply_markup=get_main_menu_keyboard())
        
    # Жанры
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
    elif text == "😢 Драма":
        send_movie(message.chat.id, "drama")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    save_user(chat_id)
    
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    
    if data == "next_fact":
        send_fact(chat_id)
    elif data == "next_dog":
        send_dog(chat_id)
    elif data.startswith("next_"):
        category = data.replace("next_", "")
        send_movie(chat_id, category)
    elif data == "quiz_restart":
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        start_quiz(chat_id)
    elif data.startswith("quiz_"):
        role = data.replace("quiz_", "")
        state = user_quiz_state.get(chat_id)
        if state:
            state["scores"][role] = state["scores"].get(role, 0) + 1
            state["q_index"] += 1
            if state["q_index"] < len(QUIZ_QUESTIONS):
                send_quiz_question(chat_id, message_id)
            else:
                finish_quiz(chat_id, message_id)

keep_alive()
print("PRO Бот обновлен: добавлена Собачка дня!")
bot.infinity_polling()
