import asyncio
import random
import json
import os
import logging
import time
from datetime import datetime, timedelta


from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode


# ===================== [ КОНФИГУРАЦИЯ ] =====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Переменная BOT_TOKEN не установлена!")
    print("❌ ОШИБКА: Укажите BOT_TOKEN в переменных окружения.")
    exit(1)

ADMIN_ID = 5056869104
DB_PATH = "omega_universe_data.json"


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


global_tasks = {}
global_event = {"name": "Тишина", "bonus_money": 1.0, "bonus_xp": 1.0}

HEADER = "<b>🧬 ╔═══════ [ OMEGA-SYSTEM ] ═══╗</b>"
FOOTER = "<b>🧬 ╚═══════ [ END ] ═══╝</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"


# ===================== [ ДАННЫЕ ] =====================
PHRASES = [
    "✨ Ваша туманность начала светиться лазурным светом.",
    "🧬 В первичном океане зародились первые аминокислоты.",
    "🌿 Зелёный покров окутал материки планет.",
    "🐾 На сушу выбрались первые существа.",
    "🧠 Одна из рас научилась использовать огонь.",
    "🧬 Вы создали кремниевую форму жизни.",
    "🍄 Споры гигантских грибов захватили луну.",
    "🐋 В недрах гиганта зародились левиафаны.",
    "☄️ Метеоритный поток принёс редкие изотопы.",
    "☀️ Звезда перешла в стадию красного гиганта.",
    "🕳 Рядом открылась микрочёрная дыра.",
    "💥 Сверхновая вспыхнула в соседнем секторе.",
    "🌪 Ионный шторм вывел из строя связь.",
    "🧊 Ледниковый период сковал океаны.",
    "🌋 Извержение создало горы из кристаллов.",
    "🛰 Квантовый скачок открыл новую реальность.",
    "📡 Древний маяк начал подавать сигналы.",
    "💠 Вы построили Сферу Дайсона вокруг звезды.",
    "🛸 Неопознанный объект оставил капсулу.",
    "🌀 Открыт стабильный переход в туманность Андромеды.",
    "🦾 Цивилизация перешла на аугментации.",
    "💎 Найден кристалл 'Сердце Звезды'.",
    "🪐 Кольца планеты превратились в щит.",
    "🐚 Найдены города под водой.",
    "📜 Расшифрован код матрицы Вселенной.",
    "🧘 Найдена раса существ из света.",
    "🎼 Звёзды издали гармоничный резонанс.",
    "🚪 Обнаружена дверь в Пустоту.",
    "🍏 Планета-сад расцвела миллионами цветов.",
    "🧩 Планета приняла форму куба.",
    "🕰 На спутнике время потекло вспять.",
    "☁️ Живое облако газа начало петь.",
    "👁 В центре галактики открылось Око Бездны.",
    "🧸 Найдена планета из мягкого пуха.",
    "🍭 Атмосфера луны пахнет карамелью.",
    "🗿 Гигантские статуи смотрят в небо.",
    "👑 Ваше имя высечено на кольцах Сатурна.",
    "🏗 Построен мост между мирами.",
    "🎭 Раса созданий считает вас Богом.",
    "🌊 Океан на планете стал разумным.",
    "🎇 Великий Парад Планет начался.",
    "🛡 Создан непробиваемый планетарный щит.",
    "🔋 Энергия вакуума течёт в реакторы.",
    "🌈 В космосе расцвели звёздные цветы.",
    "🕊 В системе наступила эпоха Мира.",
    "💎 Алмазный дождь на ваших колониях.",
    "🌑 Луна внезапно подмигнула вам.",
    "🌌 Вы создали новую галактику из пыли.",
    "🎷 Космический джаз на всех частотах.",
    "🛑 Время остановилось по приказу.",
    "🌠 В глубинах космоса обнаружен древний артефакт.",
    "⚡ Молнии энергии пронзили пространство.",
    "🌄 На горизонте появилась загадочная планета.",
    "🔮 Магические вихри окутали ваш корабль.",
    "🚀 Старт новой эры освоения космоса!",
    "🔍 Детекторы зафиксировали аномалию.",
    "💫 Звёздный ветер принёс весть о далёких мирах.",
    "🔬 Лаборатория готова к новым экспериментам.",
    "🌐 Сеть связи охватила всю галактику."
]


PETS = {
    "droid": {
        "n": "🤖 Дроид-помощник",
        "price_stars": 0,
        "b_money": 1.1,
        "b_xp": 1.0,
        "desc": "+10% к доходу",
        "ability": "Автоматически собирает ресурсы раз в 6 часов"
    },
    "alien_cat": {
        "n": "🐱 Кот Ориона",
        "price_stars": 10,
        "b_money": 1.25,
        "b_xp": 1.15,
        "desc": "+25% дохода, +15% опыта",
        "ability": "Увеличивает шанс найти редкие ресурсы на 15%"
    },
    "space_dragon": {
        "n": "🐉 Звёздный Дракон",
        "price_stars": 50,
        "b_money": 2.5,
        "b_xp": 2.0,
        "desc": "x2.5 доход, x2 опыт",
        "ability": "Даёт шанс получить двойной доход раз в сутки"
    },
    "void_beast": {
        "n": "👾 Тварь Бездны",
        "price_stars": 150,
        "b_money": 4.0,
        "b_xp": 3.5,
        "desc": "x4 доход, x3.5 опыт",
        "ability": "Снижает затраты на ремонт корабля на 50%"
    },
    "cosmic_owl": {
        "n": "🦉 Космическая Сова",
        "price_stars": 75,
        "b_money": 1.8,
        "b_xp": 1.7,
        "desc": "+80% доход, +70% опыт",
        "ability": "Позволяет увидеть скрытые ресурсы на карте"
    },
    "quantum_fox": {
        "n": "🦊 Квантовая Лиса",
        "price_stars": 200,
        "b_money": 3.0,
        "b_xp": 2.8,
        "desc": "x3 доход, x2.8 опыт",
        "ability": "Создаёт квантовые копии ресурсов (шанс 10%)"
    }
}

PLANETS = {
    "earth": {"n": "🌍 Земля", "lvl": 1, "desc": "Колыбель жизни. Безопасно.", "mult": 1.0},
    "mars": {"n": "🔴 Марс", "lvl": 10, "desc": "Ржавые пустыни. Больше опыта.", "mult": 1.5},
    "titan": {"n": "🧊 Титан", "lvl": 25, "desc": "Ледяные луны. Редкие ресурсы.", "mult": 2.5},
    "void": {"n": "🕳 Пустота", "lvl": 50, "desc": "Искажение реальности. Опасно.", "mult": 5.0}
}

RESOURCES = {
    "iron": "⛓ Железо",
    "crystal": "💎 Кристалл",
    "chip": "💾 Чип Древних",
    "heart": "❤️ Сердце Звезды",
    "blueprint": "📜 Чертеж Творца"
}

SHIPS = {
    "shuttle": {
        "name": "🛸 «Бродяга»",
        "price": 0,
        "mult": 1.0,
        "lvl": 1,
        "desc": "Старый, но надёжный. Идеален для начинающих."
    },
    "scout": {
        "name": "📡 «Разведчик С‑12»",
        "price": 500,
        "mult": 1.5,
        "lvl": 2,
        "desc": "Быстрый сканер. Подходит для исследования новых территорий."
    },
    "interceptor": {
        "name": "⚡️ «Стриж»",
        "price": 2000,
        "mult": 2.2,
        "lvl": 3,
        "desc": "Для молниеносных атак. Высокая маневренность."
    },
    "drone_eye": {
        "name": "👁 «Око Саурона»",
        "price": 7500,
        "mult": 3.8,
        "lvl": 4,
        "desc": "Всевидящий дрон. Обеспечивает полный обзор пространства."
    },
    "hauler": {
        "name": "🚜 «Косм. Бык»",
        "price": 18000,
        "mult": 5.5,
        "lvl": 5,
        "desc": "Грузовик для руды. Вместительный и прочный."
    },
    "fighter": {
        "name": "⚔️ «Валькирия»",
        "price": 45000,
        "mult": 11.0,
        "lvl": 7,
        "desc": "Боевая мощь флота. Отлично показывает себя в сражениях."
    },
    "bomber": {
        "name": "💣 «Сверхновая»",
        "price": 120000,
        "mult": 20.0,
        "lvl": 9,
        "desc": "Бомбардировщик. Наносит огромный урон по площади."
    },
    "corvette": {
        "name": "🛡 «Бастион»",
        "price": 300000,
        "mult": 35.0,
        "lvl": 11,
        "desc": "Летающая крепость. Отличная защита и огневая мощь."
    },
    "frigate": {
        "name": "🔱 «Посейдон»",
        "price": 850000,
        "mult": 60.0,
        "lvl": 13,
        "desc": "Флагман эскадр. Универсальный корабль для любых задач."
    },
    "destroyer": {
        "name": "🔥 «Гнев»",
        "price": 1900000,
        "mult": 130.0,
        "lvl": 16,
        "desc": "Уничтожитель миров. Способен справиться с любым противником."
    },
    "cruiser": {
        "name": "🛰 «Титан»",
        "price": 5000000,
        "mult": 320.0,
        "lvl": 20,
        "desc": "Тяжёлый крейсер. Мощь и надёжность в одном корпусе."
    },
    "carrier": {
        "name": "🦅 «Фенрир»",
        "price": 15000000,
        "mult": 800.0,
        "lvl": 25,
        "desc": "Авианосец флота. Несёт на борту эскадрильи истребителей."
    },
    "battleship": {
        "name": "👑 «Император»",
        "price": 35000000,
        "mult": 1900.0,
        "lvl": 30,
        "desc": "Линкор высшего класса. Вершина инженерной мысли."
    },
    "dreadnought": {
        "name": "💀 «Бездна»",
        "price": 100000000,
        "mult": 5500.0,
        "lvl": 38,
        "desc": "Запрещённое оружие. Вызывает трепет у врагов."
    },
    "reaper": {
        "name": "🩸 «Жнец»",
        "price": 350000000,
        "mult": 16000.0,
        "lvl": 45,
        "desc": "Собиратель душ. Ничто не устоит перед его мощью."
    },
    "nebula": {
        "name": "🌌 «Скиталец»",
        "price": 900000000,
        "mult": 55000.0,
        "lvl": 55,
        "desc": "Дух туманности. Обладает уникальными свойствами."
    },
    "kronos": {
        "name": "⌛️ «Кронос»",
        "price": 3000000000,
        "mult": 165000.0,
        "lvl": 70,
        "desc": "Властелин времени. Способен изменять ход событий."
    },
    "star_eater": {
        "name": "🌑 «Пожиратель»",
        "price": 15000000000,
        "mult": 650000.0,
        "lvl": 85,
        "desc": "Ест звёзды. Абсолютное оружие разрушения."
    },
    "void_walker": {
        "name": "👻 «Ходок»",
        "price": 75000000000,
        "mult": 2200000.0,
        "lvl": 100,
        "desc": "Вне реальности. Превосходит все известные технологии."
    },
    "infinity": {
        "name": "♾ «Бесконечность»",
        "price": 300000000000,
        "mult": 110000000.0,
        "lvl": 120,
        "desc": "Конец всего. Символ безграничной мощи."
    },
    "creator": {
        "name": "✨ «ТВОРЕЦ»",
        "price": 777777777777,
        "mult": 60000000.0,
        "lvl": 150,
        "desc": "ВЫ — БОГ. Вершина эволюции космических кораблей."
    }
}

CASES = {
    "syndicate": {
        "n": "💎 Синдикат",
        "p": 10000,
        "drop": {
            "money": (5000, 15000),
            "xp": (100, 300)
        },
        "id": "syn",
        "desc": "Содержит ценные ресурсы и опыт."
    },
    "elite": {
        "n": "🏅 Элитный",
        "p": 25000,
        "drop": {
            "money": (15000, 40000),
            "xp": (300, 800)
        },
        "id": "elite",
        "desc": "Повышенный шанс редких находок."
    },
    "legendary": {
        "n": "🌟 Легендарный",
        "p": 75000,
        "drop": {
            "money": (40000, 120000),
            "xp": (800, 2000)
        },
        "id": "legend",
        "desc": "Гарантированные редкие ресурсы."
    }
}

# ===================== [ СИСТЕМА ДАННЫХ ] =====================
def load_data():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {"players": {}, "market": [], "news": "Галактика проснулась.", "events": []}
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Ошибка чтения базы данных: {e}")
        return {"players": {}, "market": [], "news": "Ошибка загрузки данных.", "events": []}

def save_data(data):
    try:
        with open(DB_PATH, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        logging.error(f"Ошибка сохранения базы данных: {e}")

def get_lvl(xp):
    return int(xp**0.5 // 2) + 1

def progress_bar(current, total, length=10):
    if total <= 0:
        return "▰" * length
    percent = min(current / total, 1.0)
    filled = int(length * percent)
    return "▰" * filled + "▱" * (length - filled)

def format_number(num):
    """Форматирует большие числа с разделителями тысяч."""
    return f"{num:,}".replace(",", " ")


# ===================== [ ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ] =====================
async def send_news_broadcast(text):
    """Рассылает новостное сообщение всем активным игрокам."""
    data = load_data()
    for uid in data["players"]:
        try:
            await bot.send_message(int(uid), f"📢 НОВОСТЬ: {text}")
        except Exception as e:
            logging.warning(f"Не удалось отправить новость пользователю {uid}: {e}")

async def schedule_daily_reset():
    """Планировщик ежедневного сброса заданий и событий."""
    while True:
        now = datetime.now()
        # Время сброса — 00:00 по серверному времени
        next_reset = datetime(now.year, now.month, now.day + 1, 0, 0)
        wait_seconds = (next_reset - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        data = load_data()
        # Сброс ежедневных заданий
        for uid, player in data["players"].items():
            player["last_quest_date"] = ""
            player["dailies"] = []
        # Генерируем новое глобальное событие
        events = [
            "В галактике наблюдается аномальная активность тёмной материи!",
            "Обнаружен древний артефакт на окраине системы.",
            "Метеоритный дождь принёс редкие минералы.",
            "На одной из планет пробудилась древняя цивилизация.",
            "Космическое излучение повысило шанс нахождения редких ресурсов."
        ]
        data["news"] = random.choice(events)
        data["events"].append({
            "text": data["news"],
            "time": datetime.now().isoformat()
        })
        save_data(data)
        await send_news_broadcast(data["news"])


# ===================== [ КЛАВИАТУРЫ ] =====================
def main_kb(uid, xp=0):
    lvl = get_lvl(xp)
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 СИНТЕЗ (ИГРАТЬ)", callback_data="game_go"))
    b.row(
        types.InlineKeyboardButton(text=f"👤 ПРОФИЛЬ (Lvl {lvl})", callback_data="view_profile"),
        types.InlineKeyboardButton(text="🛒 ВЕРФЬ", callback_data="open_shop")
    )
    b.row(
        types.InlineKeyboardButton(text="🐾 ПИТОМЦЫ", callback_data="pets_menu"),
        types.InlineKeyboardButton(text="🌍 КАРТА", callback_data="map_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="🎒 РЕСУРСЫ", callback_data="res_menu"),
        types.InlineKeyboardButton(text="📈 РЫНОК", callback_data="market_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="🧬 НАВЫКИ", callback_data="skills_menu"),
        types.InlineKeyboardButton(text="⚔️ PVP", callback_data="pvp_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="📦 КЕЙСЫ", callback_data="cases_menu"),
        types.InlineKeyboardButton(text="📋 ЗАДАНИЯ", callback_data="daily_quests")
    )
    b.row(
        types.InlineKeyboardButton(text="🏦 БАНК", callback_data="bank_menu"),
        types.InlineKeyboardButton(text="🚜 ГАРАЖ", callback_data="garage_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="🎰 КАЗИНО", callback_data="casino_menu"),
        types.InlineKeyboardButton(text="🎁 БОНУС", callback_data="daily_bonus")
    )
    b.row(types.InlineKeyboardButton(text="🛠 СЕРВИС", callback_data="service_menu"))
    if int(uid) == ADMIN_ID:
        b.row(types.InlineKeyboardButton(text="🛡 АДМИН", callback_data="admin_main"))
    return b.as_markup()


def shop_kb():
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🚀 Корабли", callback_data="shop_ships"))
    b.row(types.InlineKeyboardButton(text="🐾 Питомцы", callback_data="shop_pets"))
    b.row(types.InlineKeyboardButton(text="📦 Кейсы", callback_data="shop_cases"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    return b.as_markup()


def back_kb():
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    return b.as_markup()


# ===================== [ ХЕНДЛЕРЫ ] =====================
@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id)
    data = load_data()
    
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000,
            "xp": 0,
            "stars": 5,  # Начальные звёзды для магазина
            "ship": "shuttle",
            "inventory": ["shuttle"],
            "items": {"free": 0, "beta": 0, "ultra": 0},
            "res": {rid: 0 for rid in RESOURCES},
            "skills": {"agg": 0, "tra": 0, "exp": 0},
            "sp": 0,
            "bank": 0,
            "last_daily": 0,
            "name": msg.from_user.first_name,
            "faction": None,
            "tuning": {"eng": 0, "atk": 0, "def": 0},
            "durability": 100,
            "pvp_wins": 0,
            "location": "earth",
            "last_quest_date": "",
            "pets": [],
            "active_pet": None,
            "daily_streak": 0,  # Серия ежедневных входов
            "achievements": []  # Достижения игрока
        }
        data["news"] = "Добро пожаловать в OMEGA-SYSTEM!"
        save_data(data)
    
    
    u = data["players"][uid]
    text = (
        f"{HEADER}\n"
        f"🚀 <b>ПИЛОТ {u['name'].upper()}, СИСТЕМА ОНЛАЙН!</b>\n"
        f"{SEP}\n"
        f"Локация: {PLANETS[u['location']]['n']}\n"
        f"Уровень: {get_lvl(u['xp'])} (XP: {u['xp']})\n"
        f"Доход: {format_number(int(u['money']))} 💵 | Звёзды: {u['stars']} ⭐\n"
        f"Корабль: {SHIPS[u['ship']]['name']}\n"
        f"Прочность корабля: {u['durability']}%\n"
        f"Серия входов: {u['daily_streak']} дней\n"
        f"{FOOTER}"
    )
    
    await msg.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_kb(uid, u['xp'])
    )

    # Приветственное сообщение при первом входе
    if u['daily_streak'] == 0:
        welcome_msg = (
            "🎯 <b>Добро пожаловать в OMEGA-SYSTEM!</b>\n\n"
            "Вы — пилот межзвёздного корабля, готовый покорять галактики!\n"
            "🔹 Используйте меню ниже, чтобы начать исследование.\n"
            "🔹 Выполняйте задания, чтобы получать награды.\n"
            "🔹 Покупайте корабли и питомцев для усиления.\n"
            "🔹 Участвуйте в PvP-битвах и казино.\n\n"
            "<i>Удачи в освоении космоса!</i>"
        )
        await msg.answer(welcome_msg, parse_mode=ParseMode.HTML)

# --- 5. МАГАЗИН (SHOP) ---
@dp.callback_query(F.data == "open_shop")
async def open_shop(call: types.CallbackQuery):
    await call.message.edit_text(
        f"{HEADER}\n"
        f"<b>🛒 ГАЛАКТИЧЕСКИЙ МАГАЗИН</b>\n"
        f"{SEP}\n"
        f"Выберите категорию для просмотра:\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=shop_kb()
    )

@dp.callback_query(F.data == "shop_ships")
async def shop_ships(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder()
    
    for sid, ship in SHIPS.items():
        if get_lvl(u["xp"]) >= ship["lvl"]:
            status = "🟢" if sid != u["ship"] else "🔵 (текущий)"
            price_str = format_number(ship["price"])
            b.row(
                types.InlineKeyboardButton(
                    text=f"{status} {ship['name']} (Lvl {ship['lvl']}) — {price_str} 💵",
                    callback_data=f"buy_ship_{sid}"
                )
            )
    
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="open_shop"))
    await call.message.edit_text(
        f"{HEADER}\n"
        f"<b>🚀 ВЫБОР КОРАБЛЯ</b>\n"
        f"{SEP}\n"
        f"Улучшайте свой флот для новых свершений!\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("buy_ship_"))
async def buy_ship(call: types.CallbackQuery):
    sid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if sid not in SHIPS:
        await call.answer("❌ Корабль не найден!", show_alert=True)
        return
    
    ship = SHIPS[sid]
    
    if get_lvl(u["xp"]) < ship["lvl"]:
        await call.answer("❌ Ваш уровень слишком низок для этого корабля!", show_alert=True)
        return
    
    if u["money"] < ship["price"]:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
        return
    
    u["money"] -= ship["price"]
    u["ship"] = sid
    u["inventory"].append(sid)
    save_data(data)
    
    await call.answer(f"✅ Вы приобрели корабль: {ship['name']}!")
    await shop_ships(call)

@dp.callback_query(F.data == "shop_pets")
async def shop_pets(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder()
    
    for pid, pet in PETS.items():
        price_str = format_number(pet["price_stars"])
        owned = pid in u["pets"]
        status = "🟡" if not owned else "🟢 (есть)"
        b.row(
            types.InlineKeyboardButton(
                text=f"{status} {pet['n']} — {price_str} ⭐ | {pet['desc']}",
                callback_data=f"buy_pet_{pid}"
            )
        )
    
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="open_shop"))
    await call.message.edit_text(
        f"{HEADER}\n"
        f"<b>🐾 МАГАЗИН ПИТОМЦЕВ</b>\n"
        f"{SEP}\n"
        f"Питомцы дают бонусы к доходу и опыту.\n"
        f"Они также обладают уникальными способностями!\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("buy_pet_"))
async def buy_pet(call: types.CallbackQuery):
    pid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if pid not in PETS:
        await call.answer("❌ Питомец не найден!", show_alert=True)
        return
    
    pet = PETS[pid]
    
    if u["stars"] < pet["price_stars"]:
        await call.answer("❌ Недостаточно звёзд!", show_alert=True)
        return
    
    if pid in u["pets"]:
        await call.answer("❌ У вас уже есть этот питомец!", show_alert=True)
        return
    
    u["stars"] -= pet["price_stars"]
    u["pets"].append(pid)
    save_data(data)
    
    await call.answer(f"✅ Вы приобрели питомца: {pet['n']}!")
    await shop_pets(call)

@dp.callback_query(F.data == "shop_cases")
async def shop_cases(call: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    for cid, case in CASES.items():
        price_str = format_number(case["p"])
        b.row(
            types.InlineKeyboardButton(
                text=f"📦 {case['n']} — {price_str} 💵 | {case['desc']}",
                callback_data=f"buy_case_{cid}"
            )
        )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="open_shop"))
    
    await call.message.edit_text(
        f"{HEADER}\n"
        f"<b>📦 МАГАЗИН КЕЙСОВ</b>\n"
        f"{SEP}\n"
        f"Открывайте кейсы, чтобы получить ценные ресурсы и опыт!\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("buy_case_"))
async def buy_case(call: types.CallbackQuery):
    cid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    if cid not in CASES:
        await call.answer("❌ Кейс не найден!", show_alert=True)
        return

    case = CASES[cid]

    if u["money"] < case["p"]:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
        return

    # Списываем деньги
    u["money"] -= case["p"]

    # Генерируем выпадение из кейса
    money_drop = random.randint(case["drop"]["money"][0], case["drop"]["money"][1])
    xp_drop = random.randint(case["drop"]["xp"][0], case["drop"]["xp"][1])

    u["money"] += money_drop
    u["xp"] += xp_drop

    # Шанс на редкий предмет
    rare_chance = random.random()
    rare_item = None
    if rare_chance < 0.05:  # 5% шанс
        rare_items = ["chip", "heart", "blueprint"]
        item = random.choice(rare_items)
        u["res"][item] += 1
        rare_item = RESOURCES[item]

    save_data(data)

    result_text = (
        f"📦 Вы открыли кейс: <b>{case['n']}</b>\n"
        f"{SEP}\n"
        f"+ {format_number(money_drop)} 💵\n"
        f"+ {xp_drop} XP\n"
    )
    if rare_item:
        result_text += f"+ 1 {rare_item} (редкость!)\n"

    await call.message.edit_text(
        f"{HEADER}\n{result_text}{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 6. ПРОФИЛЬ ИГРОКА ---
@dp.callback_query(F.data == "view_profile")
async def view_profile(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    lvl = get_lvl(u["xp"])

    active_pet_name = "Нет"
    if u["active_pet"] and u["active_pet"] in PETS:
        active_pet_name = PETS[u["active_pet"]]["n"]

    text = (
        f"{HEADER}\n"
        f"<b>👤 ПРОФИЛЬ ИГРОКА</b>\n"
        f"{SEP}\n"
        f"Имя: <b>{u['name']}</b>\n"
        f"Уровень: <b>{lvl}</b> (XP: {format_number(u['xp'])})\n"
        f"Деньги: <b>{format_number(u['money'])}</b> 💵\n"
        f"Звёзды: <b>{u['stars']}</b> ⭐\n"
        f"Корабль: <b>{SHIPS[u['ship']]['name']}</b>\n"
        f"Прочность корабля: <b>{u['durability']}%</b>\n"
        f"Локация: <b>{PLANETS[u['location']]['n']}</b>\n"
        f"Серия входов: <b>{u['daily_streak']}</b> дней\n"
        f"Активный питомец: <b>{active_pet_name}</b>\n"
        f"Побед в PvP: <b>{u['pvp_wins']}</b>\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🐱 Выбрать питомца", callback_data="select_pet"))
    b.row(types.InlineKeyboardButton(text="⚙️ Настроить корабль", callback_data="tune_ship"))
    b.row(types.InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


# --- 7. ВЫБОР ПИТОМЦА ---
@dp.callback_query(F.data == "select_pet")
async def select_pet(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder()

    if not u["pets"]:
        await call.answer("У вас нет питомцев! Купите их в магазине.", show_alert=True)
        await view_profile(call)
        return

    for pid in u["pets"]:
        pet = PETS[pid]
        status = "🔵" if pid == u["active_pet"] else "🟢"
        b.row(
            types.InlineKeyboardButton(
                text=f"{status} {pet['n']} — {pet['desc']}",
                callback_data=f"set_pet_{pid}"
            )
        )

    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="view_profile"))
    await call.message.edit_text(
        f"{HEADER}\n<b>🐾 ВЫБОР ПИТОМЦА</b>\n{SEP}\nВыберите активного питомца:\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("set_pet_"))
async def set_pet(call: types.CallbackQuery):
    pid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    if pid not in u["pets"]:
        await call.answer("Этот питомец не принадлежит вам!", show_alert=True)
        return

    u["active_pet"] = pid
    save_data(data)
    await call.answer(f"✅ Питомец {PETS[pid]['n']} активирован!")
    await select_pet(call)

# --- 8. НАСТРОЙКА КОРАБЛЯ ---
@dp.callback_query(F.data == "tune_ship")
async def tune_ship(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    ship = SHIPS[u["ship"]]

    cost_per_point = 5000
    max_points = u["xp"] // 1000  # Чем больше XP, тем больше можно вложить
    current_points = sum(u["tuning"].values())

    text = (
        f"{HEADER}\n"
        f"<b>⚙️ НАСТРОЙКА КОРАБЛЯ: {ship['name']}</b>\n"
        f"{SEP}\n"
        f"Доступные очки настройки: <b>{max_points - current_points}</b>\n"
        f"Стоимость за очко: <b>{format_number(cost_per_point)}</b> 💵\n\n"
        f"<u>Текущие параметры:</u>\n"
        f"⚙️ Двигатель: +{u['tuning']['eng'] * 5}% скорости\n"
        f⚔ Атака: +{u['tuning']['atk'] * 10}% урона\n"
        f🛡 Защита: +{u['tuning']['def'] * 15}% брони\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    if current_points < max_points:
        b.row(
            types.InlineKeyboardButton(text="+ Двигатель (5%)", callback_data="tune_eng"),
            types.InlineKeyboardButton(text="+ Атака (10%)", callback_data="tune_atk"),
            types.InlineKeyboardButton(text="+ Защита (15%)", callback_data="tune_def")
        )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="view_profile"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "tune_eng")
async def tune_eng(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    ship = SHIPS[u["ship"]]
    
    cost_per_point = 5000
    max_points = u["xp"] // 1000
    current_points = sum(u["tuning"].values())
    
    if current_points >= max_points:
        await call.answer("❌ Недостаточно очков настройки!", show_alert=True)
        return
    
    if u["money"] < cost_per_point:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
        return

    u["money"] -= cost_per_point
    u["tuning"]["eng"] += 1
    save_data(data)
    
    await call.answer("✅ Улучшено: Двигатель (+5% скорости)!")
    await tune_ship(call)

@dp.callback_query(F.data == "tune_atk")
async def tune_atk(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    cost_per_point = 5000
    max_points = u["xp"] // 1000
    current_points = sum(u["tuning"].values())
    
    if current_points >= max_points:
        await call.answer("❌ Недостаточно очков настройки!", show_alert=True)
        return

    if u["money"] < cost_per_point:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
        return

    u["money"] -= cost_per_point
    u["tuning"]["atk"] += 1
    save_data(data)
    
    await call.answer("✅ Улучшено: Атака (+10% урона)!")
    await tune_ship(call)

@dp.callback_query(F.data == "tune_def")
async def tune_def(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    cost_per_point = 5000
    max_points = u["xp"] // 1000
    current_points = sum(u["tuning"].values())
    
    if current_points >= max_points:
        await call.answer("❌ Недостаточно очков настройки!", show_alert=True)
        return

    if u["money"] < cost_per_point:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
        return

    u["money"] -= cost_per_point
    u["tuning"]["def"] += 1
    save_data(data)
    
    await call.answer("✅ Улучшено: Защита (+15% брони)!")
    await tune_ship(call)

# --- 9. ДОСТИЖЕНИЯ ---
@dp.callback_query(F.data == "achievements")
async def achievements(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    
    # Пример системы достижений
    achievements_list = [
        {"id": "first_step", "name": "Первый шаг", "desc": "Войдите в игру впервые", "reward": "5 ⭐", "unlocked": True},
        {"id": "daily_3", "name": "Три дня подряд", "desc": "Входите в игру 3 дня подряд", "reward": "10 ⭐", "unlocked": u["daily_streak"] >= 3},
        {"id": "lvl_10", "name": "Мастер космоса", "desc": "Достигните 10 уровня", "reward": "25 ⭐", "unlocked": get_lvl(u["xp"]) >= 10},
        {"id": "pvp_5", "name": "Боец арены", "desc": "Победите в 5 PvP-битвах", "reward": "20 ⭐", "unlocked": u["pvp_wins"] >= 5},
        {"id": "full_pets", "name": "Коллекционер", "desc": "Соберите всех питомцев", "reward": "50 ⭐", "unlocked": len(u["pets"]) == len(PETS)},
        {"id": "ship_master", "name": "Властелин флота", "desc": "Приобретите корабль уровня 50+", "reward": "100 ⭐", 
         "unlocked": SHIPS[u["ship"]]["lvl"] >= 50}
    ]
    
    unlocked = [a for a in achievements_list if a["unlocked"]]
    locked = [a for a in achievements_list if not a["unlocked"]]

    
    text = (
        f"{HEADER}\n"
        f"<b>🏆 ДОСТИЖЕНИЯ</b>\n"
        f"{SEP}\n"
        f"<u>Открытые:</u>\n"
    )
    for a in unlocked:
        text += f"✅ <b>{a['name']}</b>: {a['desc']} (+{a['reward']})\n"
    
    if locked:
        text += f"\n<u>Неоткрытые:</u>\n"
        for a in locked:
            text += f!⚪ {a['name']}: {a['desc']} (+{a['reward']})\n"

    text += f"{FOOTER}"

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="view_profile"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

# --- 10. ЕЖЕДНЕВНЫЕ ЗАДАНИЯ ---
@dp.callback_query(F.data == "daily_quests")
async def daily_quests(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    now = datetime.now().date().isoformat()

    # Генерируем задания, если их нет или день сменился
    if u.get("last_quest_date") != now:
        u["last_quest_date"] = now
        u["dailies"] = []
        # 3 случайных задания
        quest_pool = [
            {"id": "collect_iron", "name": "Собрать железо", "req": 10, "res": "iron", "reward": {"money": 500, "xp": 20}},
            {"id": "collect_crystal", "name": "Найти кристалл", "req": 3, "res": "crystal", "reward": {"money": 1500, "xp": 50}},
            {"id": "fight_pvp", "name": "Победить в PvP", "req": 1, "type": "pvp", "reward": {"money": 2000, "xp": 100, "stars": 5}},
            {"id": "open_case", "name": "Открыть кейс", "req": 2, "type": "case", "reward": {"money": 1000, "xp": 40}},
            {"id": "upgrade_ship", "name": "Улучшить корабль", "req": 1, "type": "tune", "reward": {"money": 800, "xp": 60}}
        ]
        u["dailies"] = random.sample(quest_pool, 3)

    text = (
        f"{HEADER}\n"
        f"<b>📋 ЕЖЕДНЕВНЫЕ ЗАДАНИЯ</b>\n"
        f"{SEP}\n"
        f"Выполняйте задания для получения наград!\n"
        f"(Обновляются каждый день)\n\n"
    )
    for i, q in enumerate(u["dailies"], 1):
        req_text = ""
        if "res" in q:
            req_text = f"{q['req']} × {RESOURCES[q['res']]}"
        elif "type" in q:
            if q["type"] == "pvp":
                req_text = "1 победа в PvP"
            elif q["type"] == "case":
                req_text = f"{q['req']} открытых кейса"
            elif q["type"] == "tune":
                req_text = "1 улучшение корабля"

        # Проверяем выполнение
        completed = False
        if "res" in q:
            completed = u["res"][q["res"]] >= q["req"]
        elif q.get("type") == "pvp":
            completed = u["pvp_wins"] >= q["req"]
        elif q.get("type") == "case":
            # Для кейсов нет прямого счётчика — считаем условно выполненным при покупке
            completed = True  # Можно доработать логику при наличии лога открытий
        elif q.get("type") == "tune":
            total_tune = sum(u["tuning"].values())
            completed = total_tune >= q["req"]

        status = "✅" if completed else "⚪"
        reward_str = ", ".join([f"{v} {k}" for k, v in q["reward"].items()])
        
        text += (
            f"{i}. {status} <b>{q['name']}</b>\n"
            f"   Требуемое: {req_text}\n"
            f"   Награда: {reward_str}\n"
        )

    text += f"{FOOTER}"

    b = InlineKeyboardBuilder()
    # Кнопка для сбора наград (если все задания выполнены)
    all_completed = all([
        (u["res"][q["res"]] >= q["req"]) if "res" in q else
        (u["pvp_wins"] >= q["req"]) if q.get("type") == "pvp" else
        (sum(u["tuning"].values()) >= q["req"]) if q.get("type") == "tune" else True
        for q in u["dailies"]
    ])
    if all_completed:
        b.row(types.InlineKeyboardButton(text="🎁 Получить награду", callback_data="claim_daily_rewards"))
    
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))

    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "claim_daily_rewards")
async def claim_daily_rewards(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    total_money = 0
    total_xp = 0
    total_stars = 0

    for q in u["dailies"]:
        total_money += q["reward"].get("money", 0)
        total_xp += q["reward"].get("xp", 0)
        total_stars += q["reward"].get("stars", 0)

    u["money"] += total_money
    u["xp"] += total_xp
    u["stars"] += total_stars

    # Сброс заданий (они обновятся при следующем открытии)
    u["dailies"] = []
    u["last_quest_date"] = ""

    save_data(data)

    reward_text = (
        f"✅ Вы получили награды за ежедневные задания!\n\n"
        f"+ {format_number(total_money)} 💵\n"
        f"+ {total_xp} XP\n"
    )
    if total_stars > 0:
        reward_text += f"+ {total_stars} ⭐\n"

    await call.message.edit_text(
        f"{HEADER}\n{reward_text}{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 11. КАЗИНО (рискованные игры) ---
@dp.callback_query(F.data == "casino_menu")
async def casino_menu(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>🎰 КАЗИНО OMEGA-SYSTEM</b>\n"
        f"{SEP}\n"
        f"Испытайте удачу! Но помните: риск — дело благородное.\n\n"
        f"🔹 <b>Колесо Фортуны</b>: поставьте ставку и получите случайный приз.\n"
        f"🔹 <b>Орлянка</b>: угадайте сторону монеты — удвойте ставку!\n"
        f"🔹 <b>Джекпот</b>: участвуйте в розыгрыше крупного приза.\n"
        f"{FOOTER}"
    )
    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="🔄 Колесо Фортуны", callback_data="casino_wheel"),
        types.InlineKeyboardButton(text="🪙 Орлянка", callback_data="casino_flip")
    )
    b.row(types.InlineKeyboardButton(text="🏆 Джекпот", callback_data="casino_jackpot"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "casino_wheel")
async def casino_wheel(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    
    if u["money"] < 100:
        await call.answer("❌ Недостаточно средств! Минимальная ставка: 100 💵", show_alert=True)
        return

    # Вращение колеса (7 секторов)
    rewards = [
        {"type": "money", "amount": 50, "text": "Мелкий выигрыш"},
        {"type": "money", "amount": 200, "text": "Средний выигрыш"},
        {"type": "money", "amount": 500, "text": "Крупный выигрыш"},
        {"type": "xp", "amount": 30, "text": "Опыт"},
        {"type": "xp", "amount": 80, "text": "Много опыта"},
        {"type": "stars", "amount": 2, "text": "Звёзды"},
        {"type": "jackpot", "amount": 0, "text": "ДЖЕКПОТ!"}  # Условный джекпот
    ]
    result = random.choice(rewards)

    u["money"] -= 100  # Ставка
    if result["type"] == "money":
        u["money"] += result["amount"]
        msg = f"💰 Вы выиграли {format_number(result['amount'])} 💵!"
    elif result["type"] == "xp":
        u["xp"] += result["amount"]
        msg = f!🧠 Вы получили {result['amount']} XP!"
    elif result["type"] == "stars":
        u["stars"] += result["amount"]
        msg = f!⭐ Вы получили {result['amount']} ⭐!"
    elif result["type"] == "jackpot":
        jackpot = random.randint(1000, 5000)
        u["money"] += jackpot
        msg = f!🎉 ДЖЕКПОТ! Вы выиграли {format_number(jackpot)} 💵!"

    save_data(data)  # Сохраняем изменения


    await call.message.edit_text(
        f"{HEADER}\n<b>🔄 КОЛЕСО ФОРТУНЫ</b>\n{SEP}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "casino_flip")
async def casino_flip(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]

    if u["money"] < 500:
        await call.answer("❌ Недостаточно средств! Минимальная ставка: 500 💵", show_alert=True)
        return

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="🪙 Орёл", callback_data="flip_heads"),
        types.InlineKeyboardButton(text="🪙 Решка", callback_data="flip_tails")
    )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="casino_menu"))

    await call.message.edit_text(
        f"{HEADER}\n<b>🪙 ОРЛЯНКА</b>\n{SEP}\n"
        "Выберите сторону монеты:\n"
        f"Ставка: {format_number(500)} 💵\n"
        "Выигрыш: удвоение ставки\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("flip_"))
async def flip_result(call: types.CallbackQuery):
    choice = call.data.split("_")[1]  # "heads" или "tails"
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    # Бросок монеты
    result = random.choice(["heads", "tails"])
    is_win = choice == result

    bet = 500
    if is_win:
        winnings = bet * 2
        u["money"] += winnings
        msg = (
            f"🎉 Вы угадали!\n"
            f"+ {format_number(winnings)} 💵 (выигрыш)\n"
            f"- {format_number(bet)} 💵 (ставка)\n"
            f"Итого: +{format_number(winnings - bet)} 💵"
        )
    else:
        u["money"] -= bet
        msg = f"❌ Не угадали! Потеряно: {format_number(bet)} 💵"

    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n<b>🪙 РЕЗУЛЬТАТ ОРЛЯНКИ</b>\n{SEP}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "casino_jackpot")
async def casino_jackpot(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    cost = 10000

    if u["money"] < cost:
        await call.answer(f"❌ Недостаточно средств! Вход в джекпот: {format_number(cost)} 💵", show_alert=True)
        return

    # Шанс на победу: 1 из 50
    win_chance = random.randint(1, 50)
    if win_chance == 1:
        # Победа! Сумма зависит от количества участников (упрощённо)
        jackpot_amount = random.randint(50000, 200000)
        u["money"] += jackpot_amount
        msg = (
            f!💥 ДЖЕКПОТ! ВЫ ВЫИГРАЛИ!\n\n"
            f"<b>{format_number(jackpot_amount)} 💵</b>\n\n"
            "Поздравляем! Это крупная удача!"
        )
    else:
        u["money"] -= cost
        msg = (
            f"❌ Неудача...\n\n"
            f"Вы заплатили {format_number(cost)} 💵 за попытку.\n"
            "Попробуйте ещё раз — удача может улыбнуться!"
        )

    save_data(load_data())

    await call.message.edit_text(
        f"{HEADER}\n<b>🏆 ДЖЕКПОТ-РОЗЫГРЫШ</b>\n{SEP}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 12. РЫНОК (обмен ресурсами) ---
@dp.callback_query(F.data == "market_menu")
async def market_menu(call: types.CallbackQuery):
    data = load_data()
    offers = data.get("market", [])

    text = (
        f"{HEADER}\n"
        f"<b>📈 РЫНОК</b>\n"
        f"{SEP}\n"
        "Здесь можно покупать и продавать ресурсы.\n\n"
    )

    if offers:
        text += "<u>Активные предложения:</u>\n"
        for offer in offers:
            res_name = RESOURCES[offer["resource"]]
            text += (
                f"• {res_name}: {format_number(offer['amount'])} шт.\n"
                f"  Цена: {format_number(offer['price'])} 💵/шт.\n"
                f"  Продавец: {offer['seller_name']}\n\n"
            )
    else:
        text += "На рынке пока нет предложений.\n"

    text += f"{FOOTER}"

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="📥 Продать ресурс", callback_data="market_sell"),
        types.InlineKeyboardButton(text="🛒 Купить ресурс", callback_data="market_buy")
    )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "market_sell")
async def market_sell(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]

    available_res = {k: v for k, v in u["res"].items() if v > 0}
    if not available_res:
        await call.answer("У вас нет ресурсов для продажи!", show_alert=True)
        await market_menu(call)
        return

    text = (
        f"{HEADER}\n"
        f"<b>📥 ПРОДАЖА РЕСУРСОВ</b>\n"
        f"{SEP}\n"
        "Выберите ресурс для продажи:\n"
    )

    b = InlineKeyboardBuilder()
    for rid, amount in available_res.items():
        res_name = RESOURCES[rid]
        b.row(
            types.InlineKeyboardButton(
                text=f"{res_name} ({format_number(amount)} шт.)",
                callback_data=f"sell_{rid}"
            )
        )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="market_menu"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data.startswith("sell_"))
async def sell_resource(call: types.CallbackQuery):
    rid = call.data.split("_")[1]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    if rid not in u["res"] or u["res"][rid] <= 0:
        await call.answer("Ресурс недоступен для продажи!", show_alert=True)
        await market_sell(call)
        return

    # Предлагаем ввести количество и цену
    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="1 шт.", callback_data=f"set_sell_{rid}_1"),
        types.InlineKeyboardButton(text="5 шт.", callback_data=f"set_sell_{rid}_5"),
        types.InlineKeyboardButton(text="10 шт.", callback_data=f"set_sell_{rid}_10")
    )
    b.row(types.InlineKeyboardButton(text="🔢 Ввести вручную", callback_data=f"manual_sell_{rid}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="market_sell"))

    await call.message.edit_text(
        f"{HEADER}\n<b>📥 ПРОДАЖА {RESOURCES[rid].upper()}</b>\n{SEP}\n"
        f"У вас есть: {format_number(u['res'][rid])} шт.\n\n"
        "Выберите количество для продажи:\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("set_sell_"))
async def set_sell_amount(call: types.CallbackQuery):
    parts = call.data.split("_")
    rid, amount = parts[2], int(parts[3])
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]

    if u["res"][rid] < amount:
        await call.answer("У вас недостаточно ресурса!", show_alert=True)
        await sell_resource(call)
        return

    # Сохраняем параметры продажи в контексте (можно использовать FSM или временный словарь)
    sell_context[uid] = {"rid": rid, "amount": amount}

    b = InlineKeyboardBuilder()
    for price in [100, 500, 1000, 2500]:
        b.row(types.InlineKeyboardButton(
            text=f"{format_number(price)} 💵/шт.",
            callback_data=f"confirm_sell_{price}"
        ))
    b.row(types.InlineKeyboardButton(text="🔢 Ввести цену вручную", callback_data="manual_price"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data=f"sell_{rid}"))


    await call.message.edit_text(
        f"{HEADER}\n<b>📥 ПРОДАЖА {RESOURCES[rid].upper()}</b>\n{SEP}\n"
        f"Количество: {format_number(amount)} шт.\n\n"
        "Установите цену за единицу:\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )

@dp.callback_query(F.data.startswith("confirm_sell_"))
async def confirm_sell(call: types.CallbackQuery):
    price = int(call.data.split("_")[2])
    uid = str(call.from_user.id)

    if uid not in sell_context:
        await call.answer("Ошибка: данные продажи утеряны!", show_alert=True)
        await market_menu(call)
        return

    data = load_data()
    u = data["players"][uid]
    rid = sell_context[uid]["rid"]
    amount = sell_context[uid]["amount"]


    # Создаём предложение
    offer = {
        "seller_id": uid,
        "seller_name": u["name"],
        "resource": rid,
        "amount": amount,
        "price": price,
        "timestamp": datetime.now().isoformat()
    }
    data["market"].append(offer)
    save_data(data)

    # Уменьшаем количество ресурса у продавца
    u["res"][rid] -= amount
    save_data(data)

    del sell_context[uid]  # Очищаем контекст


    await call.message.edit_text(
        f"{HEADER}\n✅ Предложение размещено!\n\n"
        f"<b>{RESOURCES[rid]}</b>: {format_number(amount)} шт.\n"
        f"Цена: {format_number(price)} 💵/шт.\n\n"
        "Вы можете увидеть его в разделе «Рынок».\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data.startswith("manual_sell_"))
async def manual_sell(call: types.CallbackQuery):
    rid = call.data.split("_")[2]
    await call.message.answer(
        "Введите количество для продажи (только число):",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="/отмена")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    # Здесь нужно реализовать ожидание ввода числа (например, через FSM)

@dp.callback_query(F.data == "market_buy")
async def market_buy(call: types.CallbackQuery):
    data = load_data()
    offers = data.get("market", [])

    if not offers:
        await call.answer("На рынке нет активных предложений!", show_alert=True)
        await market_menu(call)
        return

    text = (
        f"{HEADER}\n"
        f"<b>🛒 ПОКУПКА РЕСУРСОВ</b>\n"
        f"{SEP}\n"
        "<u>Доступные предложения:</u>\n"
    )

    b = InlineKeyboardBuilder()
    for i, offer in enumerate(offers):
        res_name = RESOURCES[offer["resource"]]
        text += (
            f"{i+1}. {res_name}: {format_number(offer['amount'])} шт.\n"
            f"   Цена: {format_number(offer['price'])} 💵/шт.\n"
            f!   Продавец: {offer['seller_name']}\n\n"
        )
        b.row(types.InlineKeyboardButton(
            text=f"Купить #{i+1}",
            callback_data=f"buy_offer_{i}"
        ))

    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="market_menu"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("buy_offer_"))
async def buy_offer(call: types.CallbackQuery):
    offer_idx = int(call.data.split("_")[2])
    data = load_data()
    offers = data["market"]

    if offer_idx >= len(offers):
        await call.answer("Предложение не найдено!", show_alert=True)
        await market_buy(call)
        return

    offer = offers[offer_idx]
    uid = str(call.from_user.id)
    u = data["players"][uid]

    total_cost = offer["price"] * offer["amount"]
    if u["money"] < total_cost:
        await call.answer(f"❌ Недостаточно средств! Требуется: {format_number(total_cost)} 💵", show_alert=True)
        await market_buy(call)
        return

    # Совершаем покупку
    u["money"] -= total_cost
    if offer["resource"] not in u["res"]:
        u["res"][offer["resource"]] = 0
    u["res"][offer["resource"]] += offer["amount"]


    # Удаляем предложение с рынка
    data["market"].pop(offer_idx)

    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Покупка совершена!\n\n"
        f"+ {format_number(offer['amount'])} {RESOURCES[offer['resource']]}\n"
        f"Затраты: {format_number(total_cost)} 💵\n\n"
        "Ресурс добавлен в ваш инвентарь.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 13. СКЛАД (хранение ресурсов) ---
@dp.callback_query(F.data == "storage_menu")
async def storage_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]

    text = (
        f"{HEADER}\n"
        f"<b>📦 СКЛАД</b>\n"
        f"{SEP}\n"
        "<u>Ваши ресурсы:</u>\n"
    )

    if not u["res"] or all(v == 0 for v in u["res"].values()):
        text += "Склад пуст.\n"
    else:
        for rid, amount in u["res"].items():
            if amount > 0:
                text += f"• {RESOURCES[rid]}: {format_number(amount)} шт.\n"

    text += f"\nВместимость: {u['storage_capacity']} ед.\n"
    text += f"Занято: {sum(u['res'].values())} ед.\n"
    text += f"{FOOTER}"

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🔍 Поиск ресурсов", callback_data="search_resources"))
    b.row(types.InlineKeyboardButton(text="⬆️ Улучшить склад", callback_data="upgrade_storage"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "search_resources")
async def search_resources(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    # Шанс найти ресурс (зависит от уровня игрока)
    lvl = get_lvl(u["xp"])
    success_chance = min(0.3 + (lvl * 0.01), 0.8)  # от 30% до 80%

    if random.random() < success_chance:
        # Находим случайный ресурс
        resources_list = list(RESOURCES.keys())
        found_res = random.choice(resources_list)
        found_amount = random.randint(1, 5) * lvl

        u["res"][found_res] = u["res"].get(found_res, 0) + found_amount


        save_data(data)

        msg = (
            f"✅ Вы нашли:\n"
            f"+ {format_number(found_amount)} {RESOURCES[found_res]}\n\n"
            "Продолжайте исследовать космос!"
        )
    else:
        msg = "❌ Поиски не дали результатов. Попробуйте позже!"

    await call.message.edit_text(
        f"{HEADER}\n<b>🔍 ПОИСК РЕСУРСОВ</b>\n{SEP}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "upgrade_storage")
async def upgrade_storage(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    current_cap = u["storage_capacity"]
    next_cap = current_cap + 10
    cost = next_cap * 500  # Чем больше вместимость, тем дороже улучшение


    if u["money"] < cost:
        await call.answer(
            f"❌ Недостаточно средств!\n"
            f!Требуется: {format_number(cost)} 💵\n"
            f!У вас: {format_number(u['money'])} 💵",
            show_alert=True
        )
        await storage_menu(call)
        return

    u["money"] -= cost
    u["storage_capacity"] = next_cap
    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Склад улучшен!\n\n"
        f"Новая вместимость: {next_cap} ед.\n"
        f!Затраты: {format_number(cost)} 💵\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 14. ГЛОБАЛЬНЫЕ СОБЫТИЯ (редкие ивенты) ---
@dp.callback_query(F.data == "global_events")
async def global_events(call: types.CallbackQuery):
    # Имитация глобальных событий (на основе времени/случайности)
    events = [
        {
            "name": "Метеоритный дождь",
            "desc": "В атмосфере планеты обнаружены метеориты, богатые редкими минералами!",
            "reward": {"iron": 50, "crystal": 10},
            "duration": "24 часа"
        },
        {
            "name": "Космический шторм",
            "desc": "Энергетический шторм повышает шанс выпадения редких предметов из кейсов!",
            "reward": {"multiplier": 2},  # Удвоение дропа
            "duration": "12 часов"
        },
        {
            "name": "Торговое окно",
            "desc": "Открыт временный торговый маршрут с повышенной прибылью!",
            "reward": {"market_bonus": 1.5},  # +50% к доходам на рынке
            "duration": "6 часов"
        }
    ]

    text = (
        f"{HEADER}\n"
        f"<b>🌌 ГЛОБАЛЬНЫЕ СОБЫТИЯ</b>\n"
        f"{SEP}\n"
        "<u>Текущие события:</u>\n\n"
    )

    for event in events:
        text += (
            f"<b>{event['name']}</b>\n"
            f"{event['desc']}\n"
            f"Длительность: {event['duration']}\n\n"
        )

    text += (
        "Участвуйте в событиях, чтобы получить уникальные награды!\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🎯 Принять участие", callback_data="join_event"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "join_event")
async def join_event(call: types.CallbackQuery):
    # Случайное событие и награда
    rewards = [
        {"money": 1000, "xp": 50},
        {"iron": 20, "crystal": 5},
        {"stars": 3, "money": 500},
        {"chip": 1, "money": 2000}  # Редкий чип
    ]
    reward = random.choice(rewards)

    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    msg = "<b>Вы приняли участие в глобальном событии!</b>\n\nНаграды:\n"
    for res, amount in reward.items():
        if res in RESOURCES:
            u["res"][res] = u["res"].get(res, 0) + amount
            msg += f"+ {format_number(amount)} {RESOURCES[res]}\n"
        else:
            u[res] += amount
            if res ==
    if res == "money":
        msg += f"+ {format_number(amount)} 💵\n"
    elif res == "xp":
        msg += f"+ {amount} XP\n"
    elif res == "stars":
        msg += f"+ {amount} ⭐\n"
    elif res == "chip":
        msg += f"+ 1 🔬 Редкий чип\n"

    msg += "\nСпасибо за участие в событии!"


    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 15. ПРОФИЛЬ ИГРОКА ---
@dp.callback_query(F.data == "player_profile")
async def player_profile(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]


    lvl = get_lvl(u["xp"])
    next_lvl_xp = get_next_lvl_xp(lvl)

    text = (
        f"{HEADER}\n"
        f"<b>👤 ПРОФИЛЬ ИГРОКА</b>\n"
        f"{SEP}\n"
        f"<b>Имя:</b> {u['name']}\n"
        f"<b>Уровень:</b> {lvl}\n"
        f"<b>Опыт:</b> {u['xp']} / {next_lvl_xp}\n"
        f"<b>Деньги:</b> {format_number(u['money'])} 💵\n"
        f"<b>Звёзды:</b> {u['stars']} ⭐\n"
        f"<b>Победы в PvP:</b> {u['pvp_wins']}\n"
        f"<b>Улучшения корабля:</b> {sum(u['tuning'].values())}\n"
        f"<b>Вместимость склада:</b> {u['storage_capacity']} ед.\n"
        "\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="📊 Статистика", callback_data="player_stats"))
    b.row(types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="player_settings"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "player_stats")
async def player_stats(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]


    total_resources = sum(u["res"].values())
    total_spent = u.get("total_money_spent", 0)
    total_earned = u.get("total_money_earned", 0)

    text = (
        f"{HEADER}\n"
        f"<b>📊 СТАТИСТИКА ИГРОКА</b>\n"
        f"{SEP}\n"
        f"<b>Всего ресурсов собрано:</b> {total_resources} ед.\n"
        f"<b>Потрачено денег:</b> {format_number(total_spent)} 💵\n"
        f"<b>Заработано денег:</b> {format_number(total_earn, 0)} 💵\n"
        f"<b>Соотношение доход/расход:</b> {total_earned / total_spent if total_spent > 0 else '∞'}\n"
        f"<b>Количество выполненных заданий:</b> {u.get('completed_quests', 0)}\n"
        f"<b>Открыто кейсов:</b> {u.get('opened_cases', 0)}\n"
        "\n"
        "Продолжайте играть, чтобы улучшать свои показатели!\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="player_profile"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="player_profile"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "player_settings")
async def player_settings(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>⚙️ НАСТРОЙКИ ПРОФИЛЯ</b>\n"
        f"{SEP}\n"
        "Здесь вы можете:\n"
        "• Изменить имя игрока\n"
        "• Настроить уведомления\n"
        "• Выйти из аккаунта\n"
        "\n"
        "<i>Функция в разработке...</i>\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="player_profile"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="player_profile"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

# --- Вспомогательные функции ---
def get_lvl(xp: int) -> int:
    """Рассчитывает уровень игрока по количеству опыта."""
    lvl = 1
    while xp >= get_next_lvl_xp(lvl):
        lvl += 1
    return lvl

def get_next_lvl_xp(lvl: int) -> int:
    """Возвращает количество опыта для следующего уровня."""
    return 100 * (lvl ** 1.5)

def format_number(num: int) -> str:
    """Форматирует число с разделителями тысяч."""
    return f"{num:,}".replace(",", " ")

def back_kb():
    """Создаёт клавиатуру с кнопкой «Назад»."""
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    return b.as_markup()

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# --- 16. КЕЙСЫ (случайные награды) ---
@dp.callback_query(F.data == "cases_menu")
async def cases_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]

    text = (
        f"{HEADER}\n"
        f"<b>📦 КЕЙСЫ</b>\n"
        f"{SEP}\n"
        "Здесь вы можете открывать кейсы и получать случайные награды.\n\n"
        f"<b>У вас есть:</b>\n"
    )

    case_types = {
        "common": "Обычные (бесплатно)",
        "premium": "Премиум (1 000 💵)",
        "legendary": "Легендарные (10 0000 💵)"
    }

    for case_type, desc in case_types.items():
        count = u["cases"].get(case_type, 0)
        text += f"• {desc}: {count} шт.\n"


    text += f"\n{FOOTER}"


    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="Открыть обычный", callback_data="open_case_common"),
        types.InlineKeyboardButton(text="Купить премиум", callback_data="buy_case_premium")
    )
    b.row(
        types.InlineKeyboardButton(text="Купить легендарный", callback_data="buy_case_legendary"),
        types.InlineKeyboardButton(text="🔄 Обновить", callback_data="cases_menu")
    )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "open_case_common")
async def open_case_common(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    if u["cases"].get("common", 0) <= 0:
        await call.answer("У вас нет обычных кейсов!", show_alert=True)
        await cases_menu(call)
        return

    # Уменьшаем количество кейсов
    u["cases"]["common"] -= 1


    # Случайная награда
    rewards = [
        {"money": 100, "xp": 10},
        {"iron": 5, "crystal": 2},
        {"stars": 1},
        {"chip": 1, "money": 500},
        {"xp": 50}
    ]
    reward = random.choice(rewards)

    msg = "<b>Вы открыли обычный кейс!</b>\n\nНаграды:\n"
    for res, amount in reward.items():
        if res in RESOURCES:
            u["res"][res] = u["res"].get(res, 0) + amount
            msg += f"+ {format_number(amount)} {RESOURCES[res]}\n"
        else:
            if res == "money":
                u["money"] += amount
                msg += f"+ {format_number(amount)} 💵\n"
            elif res == "xp":
                u["xp"] += amount
                msg += f"+ {amount} XP\n"
            elif res == "stars":
                u["stars"] += amount
                msg += f"+ {amount} ⭐\n"
            elif res == "chip":
                msg += f"+ 1 🔬 Редкий чип\n"

    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "buy_case_premium")
async def buy_case_premium(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    cost = 1000
    if u["money"] < cost:
        await call.answer(
            f"❌ Недостаточно средств!\n"
            f!Требуется: {format_number(cost)} 💵\n"
            f!У вас: {format_number(u['money'])} 💵",
            show_alert=True
        )
        await cases_menu(call)
        return

    u["money"] -= cost
    u["cases"]["premium"] = u["cases"].get("premium", 0) + 1
    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Вы купили премиум-кейс!\n\n"
        f"Теперь у вас: {u['cases']['premium']} премиум-кейсов.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "buy_case_legendary")
async def buy_case_legendary(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    cost = 100000
    if u["money"] < cost:
        await call.answer(
            f"❌ Недостаточно средств!\n"
            f!Требуется: {format_number(cost)} 💵\n"
            f!У вас: {format_number(u['money'])} 💵",
            show_alert=True
        )
        await cases_menu(call)
        return

    u["money"] -= cost
    u["cases"]["legendary"] = u["cases"].get("legendary", 0) + 1
    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Вы купили легендарный кейс!\n\n"
        f"Теперь у вас: {u['cases']['legendary']} легендарных кейсов.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 17. PVP-БОИ (игрок против игрока) ---
@dp.callback_query(F.data == "pvp_menu")
async def pvp_menu(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>👊 PVP-БОИ</b>\n"
        f"{SEP}\n"
        "Выберите режим боя:\n\n"
        "1. <b>Случайный противник</b> — система подберёт вам соперника.\n"
        "2. <b>Вызов друга</b> — пригласите друга сразиться.\n"
        "3. <b>Рейтинг</b> — посмотрите топ игроков.\n\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="Случайный бой", callback_data="pvp_random"),
        types.InlineKeyboardButton(text="Вызов друга", callback_data="pvp_invite")
    )
    b.row(
        types.InlineKeyboardButton(text="Рейтинг", callback_data="pvp_rating"),
        types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main")
    )

    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "pvp_random")
async def pvp_random(call: types.CallbackQuery):
    # Логика подбора случайного противника (упрощённо)
    await call.answer("Поиск соперника... Пожалуйста, подождите.", show_alert=False)


    # Имитация поиска (в реальной реализации — поиск в базе)
    await asyncio.sleep(2)


    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    # Случайный результат боя (упрощённая логика)
    win = random.choice([True, False])
    reward = random.randint(500, 2000)


    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    if win:
        u["money"] += reward
        u["pvp_wins"] += 1
        msg = (
            "<b>Победа в PVP-бою!</b>\n\n"
            f"Вы получили: {format_number(reward)} 💵\n"
            "Ваша серия побед увеличена!\n\n"
            "Продолжайте сражаться!"
        )
    else:
        msg = (
            "<b>Поражение в PVP-бою!</b>\n\n"
            "Не расстраивайтесь — в следующий раз повезёт больше!\n\n"
            "Попробуйте снова?"
        )

    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "pvp_invite")
async def pvp_invite(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>👊 ВЫЗОВ ДРУГА</b>\n"
        f"{SEP}\n"
        "Чтобы вызвать друга на бой:\n\n"
        "1. Отправьте ему специальную ссылку-приглашение.\n"
        "2. Друг должен перейти по ссылке и принять вызов.\n"
        "3. Бой начнётся автоматически!\n\n"
        "<i>Функция в разработке...</i>\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="Получить ссылку", callback_data="get_invite_link"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="pvp_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "get_invite_link")
async def get_invite_link(call: types.CallbackQuery):
    # Генерируем уникальную ссылку (в реальной реализации — через базу данных)
    invite_code = f"pvp_{call.from_user.id}_{random.randint(1000, 9999)}"
    link = f"https://t.me/your_bot?start={invite_code}"


    text = (
        f"{HEADER}\n"
        f"<b>🔗 ВАША ССЫЛКА-ПРИГЛАШЕНИЕ</b>\n"
        f"{SEP}\n"
        f"Отправьте эту ссылку другу:\n\n"
        f"<code>{link}</code>\n\n"
        "Когда друг перейдёт по ссылке, бой начнётся автоматически.\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(
            text="Скопировать ссылку",
            url=link
        )
    )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="pvp_invite"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "pvp_rating")
async def pvp_rating(call: types.CallbackQuery):
    data = load_data()
    players = data["players"]


    # Сортируем игроков по количеству побед
    sorted_players = sorted(
        players.values(),
        key=lambda x: x["pvp_wins"],
        reverse=True
    )

    text = (
        f"{HEADER}\n"
        f"<b>🏆 РЕЙТИНГ PVP</b>\n"
        f"{SEP}\n"
        "<u>Топ-10 игроков:</u>\n\n"
    )

    for i, player in enumerate(sorted_players[:10], 1):
        text += (
            f"{i}. <b>{player['name']}</b>\n"
            f"   Победы: {player['pvp_wins']}\n"
            f"   Уровень: {get_lvl(player['xp'])}\n\n"
        )

    text += f"{FOOTER}"


    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="pvp_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


# --- 18. ЗАДАНИЯ (квесты) ---
@dp.callback_query(F.data == "quests_menu")
async def quests_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]


    text = (
        f"{HEADER}\n"
        f"<b>📝 ЗАДАНИЯ</b>\n"
        f"{SEP}\n"
        "Выполняйте задания, чтобы получать награды!\n\n"
        "<u>Доступные задания:</u>\n"
    )

    quests = [
        {"id": "collect_iron", "name": "Собрать железо", "desc": "Найдите 10 железа", "reward": {"money": 500, "xp": 20}},
        {"id": "open_cases", "name": "Открыть кейсы", "desc": "Откройте 3 кейса", "reward": {"stars": 1}},
        {"id": "win_pvp", "name": "Победить в PVP", "desc": "Выиграйте 1 PVP-бой", "reward": {"money": 1000}}
    ]

    completed = u.get("completed_quests", [])

    for quest in quests:
        if quest["id"] not in completed:
            text += (
                f"• <b>{quest['name']}</b>\n"
                f"  {quest['desc']}\n"
                "  Награда: "
            )
            for res, amount in quest["reward"].items():
                if res == "money":
                    text += f"{format_number(amount)} 💵, "
                elif res == "xp":
                    text += f"{amount} XP, "
                elif res == "stars":
                    text += f"{amount} ⭐, "
            text = text.rstrip(", ") + "\n\n"

    if all(q["id"] in completed for q in quests):
        text += "Все задания выполнены! Следите за обновлениями.\n"

    text += f"{FOOTER}"


    b = InlineKeyboardBuilder()
    for quest in quests:
        if quest["id"] not in completed:
            b.row(types.InlineKeyboardButton(
                text=f"Выполнить «{quest['name']}»",
                callback_data=f"do_quest_{quest['id']}"
            ))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data.startswith("do_quest_"))
async def do_quest(call: types.CallbackQuery):
    quest_id = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    quests = {
        "collect_iron": {"check": u["res"].get("iron", 0) >= 10, "reward": {"money": 500, "xp": 20}},
        "open_cases": {"check": u.get("opened_cases", 0) >= 3, "reward": {"stars": 1}},
        "win_pvp": {"check": u["pvp_wins"] >= 1, "reward": {"money": 1000}}
    }

    if quest_id not in quests:
        await call.answer("Задание не найдено!", show_alert=True)
        await quests_menu(call)
        return

    if u.get("completed_quests", []).count(quest_id) > 0:
        await call.answer("Вы уже выполнили это задание!", show_alert=True)
        await quests_menu(call)
        return

    # Проверяем выполнение условий задания
    if not quests[quest_id]["check"]:
        await call.answer(
            "Вы ещё не выполнили условия задания!\n"
            "Проверьте требования и попробуйте снова.",
            show_alert=True
        )
        await quests_menu(call)
        return

    # Выдаём награду
    reward = quests[quest_id]["reward"]
    msg = "<b>Задание выполнено!</b>\n\nНаграда:\n"


    for res, amount in reward.items():
        if res in RESOURCES:
            u["res"][res] = u["res"].get(res, 0) + amount
            msg += f"+ {format_number(amount)} {RESOURCES[res]}\n"
        elif res == "money":
            u["money"] += amount
            msg += f"+ {format_number(amount)} 💵\n"
        elif res == "xp":
            u["xp"] += amount
            msg += f"+ {amount} XP\n"
        elif res == "stars":
            u["stars"] += amount
            msg += f"+ {amount} ⭐\n"

    # Отмечаем задание как выполненное
    if "completed_quests" not in u:
        u["completed_quests"] = []
    u["completed_quests"].append(quest_id)


    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n{msg}\n{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 19. МАГАЗИН (покупки за реальную валюту/внутренние покупки) ---
@dp.callback_query(F.data == "shop_menu")
async def shop_menu(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>🛒 МАГАЗИН</b>\n"
        f"{SEP}\n"
        "Здесь вы можете приобрести редкие предметы и бонусы.\n\n"
        "<u>Доступные товары:</u>\n\n"
        "1. <b>Редкий чип</b>\n"
        "   • Описание: Позволяет улучшить корабль на +5 уровней.\n"
        "   • Цена: 5 000 ⭐ (звёзды)\n\n"
        "2. <b>Ускоритель добычи</b>\n"
        "   • Описание: Увеличивает скорость добычи ресурсов на 50% на 1 час.\n"
        "   • Цена: 2 500 ⭐\n\n"
        "3. <b>Премиум-кейс</b>\n"
        "   • Описание: Содержит редкие ресурсы и деньги.\n"
        "   • Цена: 1 000 ⭐\n\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="Купить чип", callback_data="buy_chip"),
        types.InlineKeyboardButton(text="Купить ускоритель", callback_data="buy_booster")
    )
    b.row(
        types.InlineKeyboardButton(text="Купить премиум-кейс", callback_data="buy_premium_case"),
        types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main")
    )

    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "buy_chip")
async def buy_chip(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]


    cost = 5000
    if u["stars"] < cost:
        await call.answer(
            f"❌ Недостаточно звёзд!\n"
            f!Требуется: {format_number(cost)} ⭐\n"
            f!У вас: {format_number(u['stars'])} ⭐",
            show_alert=True
        )
        await shop_menu(call)
        return

    u["stars"] -= cost
    u["res"]["chip"] = u["res"].get("chip", 0) + 1
    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Вы купили редкий чип!\n\n"
        f"Теперь у вас: {u['res']['chip']} редких чипов.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "buy_booster")
async def buy_booster(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]

    cost = 2500

    if u["stars"] < cost:
        await call.answer(
            f"❌ Недостаточно звёзд!\n"
            f!Требуется: {format_number(cost)} ⭐\n"
            f!У вас: {format_number(u['stars'])} ⭐",
            show_alert=True
        )
        await shop_menu(call)
        return

    u["stars"] -= cost

    # Добавляем эффект ускорителя (в реальной реализации — с таймером)
    if "boosters" not in u:
        u["boosters"] = {}
    u["boost packed"] = u.get("boosters", {})
    u["boosters"]["mining_speed"] = {
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "multiplier": 1.5
    }

    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Ускоритель добычи активирован!\n\n"
        "Скорость добычи ресурсов увеличена на 50% на 1 час.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

@dp.callback_query(F.data == "buy_premium_case")
async def buy_premium_case(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    cost = 1000

    if u["stars"] < cost:
        await call.answer(
            f"❌ Недостаточно звёзд!\n"
            f!Требуется: {format_number(cost)} ⭐\n"
            f!У вас: {format_number(u['stars'])} ⭐",
            show_alert=True
        )
        await shop_menu(call)
        return

    u["stars"] -= cost
    u["cases"]["premium"] = u["cases"].get("premium", 0) + 1
    save_data(data)

    await call.message.edit_text(
        f"{HEADER}\n✅ Вы купили премиум-кейс!\n\n"
        f"Теперь у вас: {u['cases']['premium']} премиум-кейсов.\n"
        f"{FOOTER}",
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb()
    )

# --- 20. ПОМОЩЬ И ИНФОРМАЦИЯ ---
@dp.callback_query(F.data == "help_menu")
async def help_menu(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>❓ ПОМОЩЬ</b>\n"
        f"{SEP}\n"
        "Здесь вы найдёте ответы на частые вопросы.\n\n"
        "<u>Основные разделы:</u>\n\n"
        "• <b>Управление</b>: как взаимодействовать с ботом.\n"
        "• <b>Механики игры</b>: объяснение ключевых систем.\n"
        "• <b>Советы</b>:
        "• <b>Частые вопросы</b>: ответы на популярные вопросы.\n\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="Управление", callback_data="help_controls"),
        types.InlineKeyboardButton(text="Механики игры", callback_data="help_mechanics")
    )
    b.row(
        types.InlineKeyboardButton(text="Советы", callback_data="help_tips"),
        types.InlineKeyboardButton(text="Частые вопросы", callback_data="help_faq")
    )
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "help_controls")
async def help_controls(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>🎮 УПРАВЛЕНИЕ</b>\n"
        f"{SEP}\n"
        "Как взаимодействовать с ботом:\n\n"
        "1. <b>Главное меню</b>: нажмите кнопку «Меню» в чате с ботом.\n"
        "2. <b>Навигация</b>: используйте кнопки в сообщениях для перехода между разделами.\n"
        "3. <b>Действия</b>: выбирайте опции (например, «Купить», «Открыть», «Выполнить») через кнопки.\n"
        "4. <b>Возврат</b>: кнопка «Назад» вернёт вас на предыдущий экран.\n\n"
        "Если вы застряли — нажмите «Назад» несколько раз, чтобы вернуться в главное меню.\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="help_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "help_mechanics")
async def help_mechanics(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>⚙️ МЕХАНИКИ ИГРЫ</b>\n"
        f"{SEP}\n"
        "Основные системы игры:\n\n"
        "1. <b>Ресурсы</b>: собирайте железо, кристаллы и другие материалы для улучшений.\n"
        "2. <b>Опыт (XP)</b>: зарабатывайте XP для повышения уровня. Каждый уровень даёт бонусы.\n"
        "3. <b>Деньги (💵)</b>: внутриигровая валюта для покупок и улучшений.\n"
        "4. <b>Звёзды (⭐)</b>: особая валюта для премиум-товаров и ускорителей.\n"
        "5. <b>Кейсы</b>: открывайте кейсы для случайных наград.\n"
        "6. <b>PVP-бои</b>: сражайтесь с другими игроками за награды.\n"
        "7. <b>Задания</b>: выполняйте квесты для получения бонусов.\n"
        "8. <b>Склад</b>: храните ресурсы и следите за вместимостью.\n\n"
        "Подробнее о каждой механике — в соответствующих разделах меню.\n"
        f"{FOOTER}"
    )

    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="help_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "help_tips")
async def help_tips(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>💡 СОВЕТЫ</b>\n"
        f"{SEP}\n"
        "Как быстрее развиваться:\n\n"
        "1. <b>Регулярно собирайте ресурсы</b>: проверяйте склад и отправляйтесь на поиски.\n"
        "2. <b>Выполняйте задания</b>: квесты дают хорошие награды без риска.\n"
        "3. <b>Участвуйте в PVP</b>: победы приносят деньги и опыт.\n"
        "4. <b>Улучшайте склад</b>: больше вместимость — больше ресурсов.\n"
        "5. <b>Открывайте кейсы</b>: даже обычные кейсы могут дать ценные награды.\n"
        "6. <b>Следите за событиями</b>: глобальные ивенты дают редкие ресурсы.\n"
        "7. <b>Экономьте звёзды</b>: они нужны для премиум-товаров.\n\n"
        "Помните: терпение и стратегия — ключ к успеху!\n"
        f"{FOOTER}"
    )
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="help_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


@dp.callback_query(F.data == "help_faq")
async def help_faq(call: types.CallbackQuery):
    text = (
        f"{HEADER}\n"
        f"<b>❓ ЧАСТЫЕ ВОПРОСЫ</b>\n"
        f"{SEP}\n"
        "<u>1. Как заработать деньги?</u>\n"
        "   • Выполняйте задания, участвуйте в PVP, открывайте кейсы, продавайте ресурсы.\n\n"
        "<u>2. Где найти редкие ресурсы?</u>\n"
        "   • В глобальных событиях, премиальных кейсах или при улучшенном поиске ресурсов.\n\n"
        "<u>3. Почему не открывается кейс?</u>\n"
        "   • Проверьте, есть ли у вас кейсы в инвентаре. Если нет — купите или получите в событии.\n\n"
        "<u>4. Как повысить уровень?</u>\n"
        "   • Зарабатывайте XP: выполняйте задания, побеждайте в PVP, собирайте ресурсы.\n\n"
        "<u>5. Что делать, если закончились деньги?</u>\n"
        "   • Выполните задания, откройте кейсы или участвуйте в событиях — там часто дают награды.\n\n"
        "<u>6. Как пригласить друга?</u>\n"
        "   • Используйте ссылку из раздела «PVP → Вызов друга».\n\n"
        f"{FOOTER}"
    )
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="help_menu"))


    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())


# --- 21. ВЫХОД ИЗ МЕНЮ (возврат в главное меню) ---
@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]


    text = (
        f"{HEADER}\n"
        f"<b>🚀 ГЛАВНОЕ МЕНЮ</b>\n"
        f"{SEP}\n"
        f"Добро пожаловать, {u['name']}!\n\n"
        "Выберите раздел:\n"
    )

    b = InlineKeyboardBuilder()
    b.row(
        types.InlineKeyboardButton(text="📦 Склад", callback_data="storage_menu"),
        types.InlineKeyboardButton(text="🔍 Поиск ресурсов", callback_data="search_resources")
    )
    b.row(
        types.InlineKeyboardButton(text="🎁 Кейсы", callback_data="cases_menu"),
        types.InlineKeyboardButton(text="👊 PVP-бои", callback_data="pvp_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="📝 Задания", callback_data="quests_menu"),
        types.InlineKeyboardButton(text="🛒 Магазин", callback_data="shop_menu")
    )
    b.row(
        types.InlineKeyboardButton(text="👤 Профиль", callback_data="player_profile"),
        types.InlineKeyboardButton(text="❓ Помощь", callback_data="help_menu")
    )
    await call.message.edit_text(text, parse_mode=Parse

    await call.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=b.as_markup()
    )



