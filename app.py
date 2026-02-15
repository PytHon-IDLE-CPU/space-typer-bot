import asyncio
import random
import json
import os
import logging
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ===================== [ КОНФИГУРАЦИЯ ] =====================
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 5056869104
DB_PATH = "omega_universe_data.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

global_tasks = {}
global_event = {"name": "Тишина", "bonus_money": 1.0, "bonus_xp": 1.0}

HEADER = "<b>🧬 ╔═══════ [ OMEGA-SYSTEM ] ═══════╗</b>"
FOOTER = "<b>🧬 ╚═══════════════════════════════╝</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"

# ===================== [ ДАННЫЕ МИРА ] =====================
PETS = {
    "droid": {
        "n": "🤖 Дроид-помощник", 
        "price_cr": 50000, "price_stars": 0, 
        "b_money": 1.1, "b_xp": 1.0, "desc": "+10% к доходу"
    },
    "alien_cat": {
        "n": "🐱 Кот Ориона", 
        "price_cr": 250000, "price_stars": 10, 
        "b_money": 1.25, "b_xp": 1.15, "desc": "+25% доната, +15% опыта"
    },
    "space_dragon": {
        "n": "🐉 Звездный Дракон", 
        "price_cr": 5000000, "price_stars": 50, 
        "b_money": 2.5, "b_xp": 2.0, "desc": "ЛЕГЕНДА: x2.5 доход, x2 опыт"
    },
    "void_beast": {
        "n": "👾 Тварь Бездны", 
        "price_cr": 0, "price_stars": 150, 
        "b_money": 4.0, "b_xp": 3.5, "desc": "БОЖЕСТВО: x4 доход, x3.5 опыт" 
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
    "shuttle":      {"name": "🛸 'Бродяга'",           "price": 0,           "mult": 1.0,      "lvl": 1,    "desc": "Старый, но надежный."},
    "scout":        {"name": "📡 'Разведчик С-12'",    "price": 500,           "mult": 1.5,      "lvl": 2,    "desc": "Быстрый сканер."},
    "interceptor":  {"name": "⚡️ 'Стриж'",             "price": 2000,          "mult": 2.2,      "lvl": 3,    "desc": "Для молниеносных атак."},
    "drone_eye":    {"name": "👁 'Око Саурона'",        "price": 7500,          "mult": 3.8,      "lvl": 4,    "desc": "Всевидящий дрон."},
    "hauler":        {"name": "🚜 'Косм. Бык'",          "price": 18000,         "mult": 5.5,      "lvl": 5,    "desc": "Грузовик для руды."},
    "fighter":      {"name": "⚔️ 'Валькирия'",        "price": 45000,         "mult": 11.0,     "lvl": 7,    "desc": "Боевая мощь флота."},
    "bomber":       {"name": "💣 'Сверхновая'",         "price": 120000,        "mult": 20.0,     "lvl": 9,    "desc": "Бомбардировщик."},
    "corvette":     {"name": "🛡 'Бастион'",           "price": 300000,        "mult": 35.0,     "lvl": 11,   "desc": "Летающая крепость."},
    "frigate":      {"name": "🔱 'Посейдон'",          "price": 850000,        "mult": 60.0,     "lvl": 13,   "desc": "Флагман эскадр."},
    "destroyer":    {"name": "🔥 'Гнев'",               "price": 1900000,       "mult": 130.0,    "lvl": 16,   "desc": "Уничтожитель миров."},
    "cruiser":      {"name": "🛰 'Титан'",              "price": 5000000,       "mult": 320.0,    "lvl": 20,   "desc": "Тяжелый крейсер."},
    "carrier":      {"name": "🦅 'Фенрир'",             "price": 15000000,      "mult": 800.0,    "lvl": 25,   "desc": "Авианосец флота."},
    "battleship":   {"name": "👑 'Император'",         "price": 35000000,      "mult": 1900.0,   "lvl": 30,   "desc": "Линкор высшего класса."},
    "dreadnought":  {"name": "💀 'Бездна'",            "price": 100000000,     "mult": 5500.0,   "lvl": 38,   "desc": "Запрещенное оружие."},
    "reaper":       {"name": "🩸 'Жнец'",               "price": 350000000,     "mult": 16000.0,  "lvl": 45,   "desc": "Собиратель душ."},
    "nebula":       {"name": "🌌 'Скиталец'",           "price": 900000000,     "mult": 55000.0,  "lvl": 55,   "desc": "Дух туманности."},
    "kronos":       {"name": "⌛️ 'Кронос'",            "price": 3000000000,    "mult": 165000.0, "lvl": 70,   "desc": "Властелин времени."},
    "star_eater":   {"name": "🌑 'Пожиратель'",         "price": 15000000000,   "mult": 650000.0, "lvl": 85,   "desc": "Ест звезды."},
    "void_walker":  {"name": "👻 'Ходок'",              "price": 75000000000,   "mult": 2200000.0,"lvl": 100,  "desc": "Вне реальности."},
    "infinity":     {"name": "♾ 'Бесконечность'",      "price": 300000000000,  "mult": 11000000.0,"lvl": 120, "desc": "Конец всего."},
    "creator":      {"name": "✨ 'ТВОРЕЦ'",            "price": 777777777777,  "mult": 60000000.0,"lvl": 150, "desc": "ВЫ — БОГ."}
}

CASES = {
    "free": {"n": "🎁 БЕСПЛАТНЫЙ", "p": 0, "drop": {"money": (500, 2000), "xp": (10, 50)}, "chance": "Обычный"},
    "beta": {"n": "🧪 БЕТА-КЕЙС", "p": 5000, "drop": {"money": (3000, 10000), "xp": (50, 200)}, "chance": "Средний"},
    "ref":  {"n": "🔗 РЕФЕРАЛЬНЫЙ", "p": 0, "drop": {"money": (10000, 30000), "xp": (200, 500)}, "chance": "Высокий"},
    "cheap": {"n": "📦 НЕДОРОГОЙ", "p": 15000, "drop": {"money": (10000, 25000), "xp": (100, 300)}, "chance": "Обычный"},
    "mid":   {"n": "💎 СРЕДНИЙ", "p": 100000, "drop": {"money": (80000, 250000), "xp": (500, 1500)}, "chance": "Хороший"},
    "rich":  {"n": "💰 ДЛЯ БОГАТЫХ", "p": 1000000, "drop": {"money": (900000, 3000000), "xp": (2000, 10000)}, "chance": "Эпик"},
    "ultra": {"n": "👑 МИЛЛИОНЕР", "p": 50000000, "drop": {"money": (45000000, 150000000), "xp": (50000, 200000)}, "chance": "Легенда"}
}

FACTIONS = {
    "empire": {"n": "⚔️ Империя", "b": "+20% к XP", "id": "emp"},
    "rebels": {"n": "🛠 Повстанцы", "b": "+15% к доходу", "id": "reb"},
    "syndicate": {"n": "💎 Синдикат", "b": "-10% потерь в казино", "id": "syn"}
}

PHRASES = ["✨ Звезды шепчут...", "🧬 ДНК мутирует...", "🛰 Сигнал принят...", "🌌 Туманность зовет...", "☄️ Комета близко..."]

# ===================== [ УТИЛИТЫ ] =====================

def load_data():
    if not os.path.exists(DB_PATH): 
        return {"players": {}, "market": []}
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f: 
            return json.load(f)
    except:
        return {"players": {}, "market": []}

def save_data(data):
    with open(DB_PATH, "w", encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_lvl(xp): 
    return int(xp**0.5 // 2) + 1

def progress_bar(current, total, length=10):
    if total <= 0: return "▰" * length
    percent = min(current / total, 1.0)
    filled = int(length * percent)
    return "▰" * filled + "▱" * (length - filled)

# ===================== [ КЛАВИАТУРЫ ] =====================

def main_kb(uid, xp=0):
    lvl = get_lvl(xp)
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 СИНТЕЗ (ИГРАТЬ)", callback_data="game_go"))
    b.row(types.InlineKeyboardButton(text=f"👤 ПРОФИЛЬ (Lvl {lvl})", callback_data="view_profile"),
          types.InlineKeyboardButton(text="🛒 ВЕРФЬ", callback_data="open_shop"))
    
    # НОВАЯ СТРОКА С ПИТОМЦАМИ
    b.row(types.InlineKeyboardButton(text="🐾 ПИТОМЦЫ", callback_data="pets_menu"),
          types.InlineKeyboardButton(text="🌍 КАРТА", callback_data="map_menu"))
    
    b.row(types.InlineKeyboardButton(text="🎒 РЕСУРСЫ", callback_data="res_menu"),
          types.InlineKeyboardButton(text="📈 РЫНОК", callback_data="market_menu"))
    b.row(types.InlineKeyboardButton(text="🧬 НАВЫКИ", callback_data="skills_menu"),
          types.InlineKeyboardButton(text="⚔️ PVP", callback_data="pvp_menu"))
    b.row(types.InlineKeyboardButton(text="📦 КЕЙСЫ", callback_data="cases_menu"),
          types.InlineKeyboardButton(text="📋 ЗАДАНИЯ", callback_data="daily_quests"))
    b.row(types.InlineKeyboardButton(text="🏦 БАНК", callback_data="bank_menu"),
          types.InlineKeyboardButton(text="🛠 СЕРВИС", callback_data="service_menu"))
    
    if int(uid) == ADMIN_ID: 
        b.row(types.InlineKeyboardButton(text="🛡 АДМИН", callback_data="admin_main"))
    return b.as_markup()

# ===================== [ ЛОГИКА СИСТЕМ ] =====================

@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id)
    data = load_data()
    
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000, "xp": 0, "stars": 0,
            "ship": "shuttle", "inventory": ["shuttle"], 
            "items": {"free": 0, "beta": 0, "ultra": 0}, # Инвентарь кейсов для продажи
            "res": {"iron": 0, "crystal": 0, "chip": 0, "heart": 0, "blueprint": 0},
            "skills": {"agg": 0, "tra": 0, "exp": 0},
            "sp": 0, # Skill Points
            "bank": 0, "last_daily": 0, "name": msg.from_user.first_name,
            "faction": None, "durability": 100, "pvp_wins": 0,
            "location": "earth", "last_quest_date": ""
        }
        save_data(data)
    
    u = data["players"][uid]
    text = f"{HEADER}\n🚀 <b>ПИЛОТ {u['name'].upper()}, СИСТЕМА ОНЛАЙН!</b>\n{SEP}\nЛокация: {PLANETS[u['location']]['n']}\n{FOOTER}"
    await msg.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_kb(uid, u['xp']))

# --- 1. СИСТЕМА ПЛАНЕТ ---
@dp.callback_query(F.data == "map_menu")
async def map_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder()
    for pid, info in PLANETS.items():
        prefix = "✅ " if u["location"] == pid else ""
        lock = "🔒 " if get_lvl(u["xp"]) < info["lvl"] else ""
        b.row(types.InlineKeyboardButton(text=f"{prefix}{lock}{info['n']} (Lvl {info['lvl']})", callback_data=f"travel_{pid}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"{HEADER}\n🌌 <b>ЗВЕЗДНАЯ КАРТА</b>\n{SEP}\nВыберите точку назначения:\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("travel_"))
async def travel_logic(call: types.CallbackQuery):
    pid = call.data.split("_")[1]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if get_lvl(u["xp"]) < PLANETS[pid]["lvl"]:
        return await call.answer("❌ Уровень слишком низок для варп-прыжка!", show_alert=True)
    
    u["location"] = pid
    save_data(data)
    await call.answer(f"🚀 Прыжок на {PLANETS[pid]['n']} выполнен!")
    await map_menu(call)

# --- 2. РЫНОК ИГРОКОВ ---
@dp.message(Command("sell"))
async def sell_item(msg: types.Message, command: CommandObject):
    uid = str(msg.from_user.id)
    data = load_data()
    if not command.args:
        return await msg.answer("📝 Формат: `/sell [тип_кейса] [цена]`\nПример: `/sell ultra 5000000`", parse_mode="Markdown")
    
    try:
        item_type, price = command.args.split()
        price = int(price)
        if item_type not in CASES: raise ValueError()
        if data["players"][uid]["items"].get(item_type, 0) < 1:
            return await msg.answer("❌ У вас нет такого кейса в инвентаре!")
        
        # Забираем кейс и ставим на рынок
        data["players"][uid]["items"][item_type] -= 1
        data["market"].append({
            "id": len(data["market"]),
            "seller_id": uid,
            "seller_name": data["players"][uid]["name"],
            "item": item_type,
            "price": price
        })
        save_data(data)
        await msg.answer(f"✅ Вы выставили {CASES[item_type]['n']} на рынок за {price:,} CR!")
    except:
        await msg.answer("❌ Ошибка. Проверьте тип кейса и цену.")

@dp.callback_query(F.data == "market_menu")
async def market_menu(call: types.CallbackQuery):
    data = load_data()
    b = InlineKeyboardBuilder()
    for lot in data["market"][-10:]: # Показываем последние 10 лотов
        b.row(types.InlineKeyboardButton(
            text=f"📦 {lot['item']} - {lot['price']:,} CR (от {lot['seller_name']})", 
            callback_data=f"buy_lot_{lot['id']}"
        ))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"{HEADER}\n📈 <b>ГАЛАКТИЧЕСКИЙ РЫНОК</b>\n{SEP}\nЧтобы продать кейс, используй:\n`/sell [тип] [цена]`\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("buy_lot_"))
async def buy_lot_logic(call: types.CallbackQuery):
    lot_id = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    data = load_data()
    
    lot = next((l for l in data["market"] if l["id"] == lot_id), None)
    if not lot: return await call.answer("❌ Лот уже продан!")
    if lot["seller_id"] == uid: return await call.answer("❌ Вы не можете купить свой товар!")
    
    buyer = data["players"][uid]
    if buyer["money"] < lot["price"]: return await call.answer("❌ Недостаточно кредитов!")
    
    # Сделка
    buyer["money"] -= lot["price"]
    buyer["items"][lot["item"]] = buyer["items"].get(lot["item"], 0) + 1
    data["players"][lot["seller_id"]]["money"] += lot["price"]
    
    data["market"].remove(lot)
    save_data(data)
    await call.answer("✅ Успешная покупка!")
    await market_menu(call)

# --- 3. ЕЖЕДНЕВНЫЕ ЗАДАНИЯ ---
@dp.callback_query(F.data == "daily_quests")
async def daily_quests(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    today = datetime.now().strftime("%Y-%m-%d")
    
    if u["last_quest_date"] != today:
        u["last_quest_date"] = today
        # Генерируем новые задания: (Тип, цель, текущее, награда)
        u["dailies"] = [
            {"t": "Победить в PVP", "goal": 1, "cur": 0, "rew": 5},
            {"t": "Открыть кейс", "goal": 2, "cur": 0, "rew": 3},
            {"t": "Заработать кредиты", "goal": 50000, "cur": 0, "rew": 10}
        ]
        save_data(data)

    text = f"{HEADER}\n📋 <b>ЗАДАНИЯ НА СЕГОДНЯ</b>\n{SEP}\n"
    for q in u["dailies"]:
        status = "✅" if q["cur"] >= q["goal"] else "⏳"
        text += f"{status} {q['t']}: {q['cur']}/{q['goal']} (+{q['rew']} ⭐)\n"
    text += f"\n{FOOTER}"
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

# --- 4. RPG НАВЫКИ ---
@dp.callback_query(F.data == "skills_menu")
async def skills_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    
    # Расчет доступных очков навыков (1 за уровень)
    total_sp = get_lvl(u["xp"]) - 1
    spent_sp = sum(u["skills"].values())
    u["sp"] = total_sp - spent_sp
    
    text = (f"{HEADER}\n🧬 <b>ВЕТКИ ТАЛАНТОВ</b>\n{SEP}\n"
            f"Доступно очков: <b>{u['sp']}</b>\n\n"
            f"🔴 Агрессор (Lvl {u['skills']['agg']}): +% к урону\n"
            f"🔵 Торговец (Lvl {u['skills']['tra']}): +% к доходу\n"
            f"🟢 Исследователь (Lvl {u['skills']['exp']}): Шанс на ресурсы\n"
            f"{FOOTER}")
    
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🔴 + АГР", callback_data="up_agg"),
          types.InlineKeyboardButton(text="🔵 + ТОРГ", callback_data="up_tra"),
          types.InlineKeyboardButton(text="🟢 + ИССЛ", callback_data="up_exp"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("up_"))
async def upgrade_skill(call: types.CallbackQuery):
    skill = call.data.split("_")[1]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    total_sp = get_lvl(u["xp"]) - 1
    if sum(u["skills"].values()) < total_sp:
        u["skills"][skill] += 1
        save_data(data)
        await call.answer("🧬 Навык улучшен!")
        await skills_menu(call)
    else:
        await call.answer("❌ Нет свободных очков навыков!", show_alert=True)

# --- 5. КРАФТ И РЕСУРСЫ ---
@dp.callback_query(F.data == "res_menu")
async def res_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    text = f"{HEADER}\n🎒 <b>СКЛАД РЕСУРСОВ</b>\n{SEP}\n"
    for rid, name in RESOURCES.items():
        text += f"{name}: {u['res'].get(rid, 0)}\n"
    text += f"\n<b>РЕЦЕПТ ТВОРЦА:</b>\n"
    text += f"❤️ Сердца: {u['res'].get('heart', 0)}/10\n"
    text += f"📜 Чертежи: {u['res'].get('blueprint', 0)}/1\n"
    text += f"{FOOTER}"
    b = InlineKeyboardBuilder()
    if u['res'].get('heart', 0) >= 10 and u['res'].get('blueprint', 0) >= 1:
        b.row(types.InlineKeyboardButton(text="✨ СОБРАТЬ ТВОРЦА", callback_data="craft_creator"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

# ===================== [ ОБНОВЛЕННАЯ ИГРОВАЯ ЛОГИКА ] =====================

@dp.callback_query(F.data == "game_go")
async def game_go(call: types.CallbackQuery):
    phrase = random.choice(PHRASES)
    global_tasks[str(call.from_user.id)] = phrase
    text = f"{HEADER}\n🧩 <b>КВАНТОВЫЙ СИНТЕЗ</b>\n{SEP}\nСкопируйте фразу ниже:\n\n<code>{phrase}</code>\n{FOOTER}"
    await call.message.edit_text(text, parse_mode=ParseMode.HTML)

# --- СИСТЕМА ПИТОМЦЕВ ---
@dp.callback_query(F.data == "pets_menu")
async def pets_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    # Если в старой базе нет ключа pets, добавляем
    if "pets" not in u: u["pets"] = []
    if "active_pet" not in u: u["active_pet"] = None

    text = f"{HEADER}\n🐾 <b>ЦЕНТР ГЕНЕТИКИ</b>\n{SEP}\n"
    if u["active_pet"]:
        pet = PETS[u["active_pet"]]
        text += f"У вас сейчас: <b>{pet['n']}</b>\nБонус: {pet['desc']}\n\n"
    else:
        text += "У вас пока нет активного спутника.\n\n"
    
    text += "Доступные существа для покупки:\n"
    text += f"{FOOTER}"
    
    b = InlineKeyboardBuilder()
    for pid, info in PETS.items():
        if pid in u["pets"]:
            status = "✅ Выбрать" if u["active_pet"] != pid else "🌟 АКТИВЕН"
            b.row(types.InlineKeyboardButton(text=f"{info['n']} ({status})", callback_data=f"select_pet_{pid}"))
        else:
            price_text = f"{info['price_cr']:,} CR" if info["price_cr"] > 0 else f"{info['price_stars']} ⭐"
            b.row(types.InlineKeyboardButton(text=f"{info['n']} — {price_text}", callback_data=f"buy_pet_{pid}"))
            
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("buy_pet_"))
async def buy_pet_logic(call: types.CallbackQuery):
    pid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    pet = PETS[pid]
    
    if "pets" not in u: u["pets"] = []
    
    # Проверка валюты
    if pet["price_cr"] > 0:
        if u["money"] < pet["price_cr"]:
            return await call.answer("❌ Недостаточно кредитов!", show_alert=True)
        u["money"] -= pet["price_cr"]
    else:
        if u["stars"] < pet["price_stars"]:
            return await call.answer("❌ Недостаточно звезд!", show_alert=True)
        u["stars"] -= pet["price_stars"]
        
    u["pets"].append(pid)
    u["active_pet"] = pid
    save_data(data)
    await call.answer(f"🎉 {pet['n']} теперь ваш спутник!")
    await pets_menu(call)

@dp.callback_query(F.data.startswith("select_pet_"))
async def select_pet_logic(call: types.CallbackQuery):
    pid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    u["active_pet"] = pid
    save_data(data)
    await call.answer(f"🐾 Вы призвали {PETS[pid]['n']}!")
    await pets_menu(call)
    
@dp.message()
async def message_handler(m: types.Message):
    uid = str(m.from_user.id)
    data = load_data()
    if uid not in data["players"]: return

    if uid in global_tasks and m.text == global_tasks[uid]:
        u = data["players"][uid]
        if u["durability"] <= 5: return await m.answer("🧨 <b>Критическая поломка!</b>", parse_mode="HTML")
        
        # Модификаторы навыков
        income_mod = 1.0 + (u["skills"]["tra"] * 0.05)
        xp_mod = 1.0 + (u["skills"]["exp"] * 0.03)
        loc_mult = PLANETS[u["location"]]["mult"]
        
        # --- БОНУСЫ ПИТОМЦА ---
        pet_money_mod = 1.0
        pet_xp_mod = 1.0
        if u.get("active_pet"):
            pet_money_mod = PETS[u["active_pet"]]["b_money"]
            pet_xp_mod = PETS[u["active_pet"]]["b_xp"]
        # ----------------------

        rew = int(random.randint(300, 700) * SHIPS[u["ship"]]["mult"] * loc_mult * income_mod * pet_money_mod)
        xp_rew = int(30 * xp_mod * loc_mult * pet_xp_mod)
        
        u["money"] += rew
        u["xp"] += xp_rew
        u["durability"] -= 1
        
        # Шанс найти ресурс (увеличивается, если есть крутой питомец)
        luck_mod = 1.1 if u.get("active_pet") == "alien_cat" else 1.0
        if random.random() < (0.1 + u["skills"]["exp"] * 0.02) * luck_mod:
            res_type = random.choice(["iron", "crystal", "chip"])
            u["res"][res_type] += 1
            await m.answer(f"📦 {PETS[u['active_pet']]['n'] if u.get('active_pet') else 'Вы'} нашли ресурс: {RESOURCES[res_type]}!")

        # Прогресс дейлика
        for q in u.get("dailies", []):
            if q["t"] == "Заработать кредиты": q["cur"] = min(q["goal"], q["cur"] + rew)

        save_data(data)
        del global_tasks[uid]
        await m.answer(f"✅ <b>СИНТЕЗ ЗАВЕРШЕН</b>\n+{rew:,} CR | +{xp_rew} XP", parse_mode="HTML", reply_markup=main_kb(uid, u['xp']))
# --- ПОВТОР ОСТАЛЬНЫХ ФУНКЦИЙ ДЛЯ ЦЕЛОСТНОСТИ ---

@dp.callback_query(F.data == "view_profile")
async def view_profile(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    lvl = get_lvl(u['xp'])
    next_xp = (lvl * 2)**2
    bar = progress_bar(u['xp'], next_xp)
    text = (f"{HEADER}\n👤 <b>ПРОФИЛЬ:</b> {u['name']}\n{SEP}\n"
            f"📊 LVL: {lvl} | XP: {u['xp']:,}/{next_xp:,}\n[{bar}]\n"
            f"💰 CR: {u['money']:,} | ⭐ STARS: {u['stars']}\n"
            f"🛸 КОРАБЛЬ: {SHIPS[u['ship']]['name']}\n"
            f"🔧 КОРПУС: {u['durability']}%\n"
            f"🌍 МЕСТО: {PLANETS[u['location']]['n']}\n{FOOTER}")
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "open_shop")
async def open_shop(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder()
    for key, val in SHIPS.items():
        if key == "shuttle" or key == "creator": continue
        status = "✅" if key in u["inventory"] else f"{val['price']:,} CR"
        if get_lvl(u['xp']) >= val['lvl'] or key in u["inventory"]:
            b.row(types.InlineKeyboardButton(text=f"{val['name']} ({status})", callback_data=f"buy_ship_{key}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text("🛒 <b>ВЕРФЬ ГАЛАКТИКИ</b>", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("buy_ship_"))
async def buy_ship_logic(call: types.CallbackQuery):
    ship_key = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if ship_key in u["inventory"]: return await call.answer("Уже есть!")
    if u["money"] >= SHIPS[ship_key]["price"]:
        u["money"] -= SHIPS[ship_key]["price"]
        u["inventory"].append(ship_key)
        u["ship"] = ship_key
        save_data(data)
        await call.answer("Корабль куплен!")
        await open_shop(call)
    else: await call.answer("Нет денег!")

@dp.callback_query(F.data == "cases_menu")
async def cases_menu(call: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    for cid, info in CASES.items():
        b.row(types.InlineKeyboardButton(text=f"{info['n']} — {info['p']:,} CR", callback_data=f"open_case_{cid}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text("📦 <b>ТЕРМИНАЛ ПОСТАВОК</b>", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("open_case_"))
async def open_case_logic(call: types.CallbackQuery):
    cid = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if u["money"] < CASES[cid]["p"]: return await call.answer("Нет денег!")
    
    u["money"] -= CASES[cid]["p"]
    m_rew = random.randint(*CASES[cid]["drop"]["money"])
    u["money"] += m_rew
    
    # Шанс на редкие ресурсы из кейсов
    if random.random() < 0.05: u["res"]["heart"] += 1; await call.answer("🔥 ВЫПАЛО СЕРДЦЕ ЗВЕЗДЫ!", show_alert=True)
    if random.random() < 0.02: u["res"]["blueprint"] += 1; await call.answer("📜 ВЫПАЛ ЧЕРТЕЖ ТВОРЦА!", show_alert=True)
    
    save_data(data)
    await call.answer(f"Выпало: {m_rew:,} CR")
    await cases_menu(call)

@dp.callback_query(F.data == "service_menu")
async def service_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🔧 ПОЧИНИТЬ (500 CR)", callback_data="repair_ship"),
                                    types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"🔧 СОСТОЯНИЕ: {u['durability']}%", reply_markup=b.as_markup())

@dp.callback_query(F.data == "repair_ship")
async def repair_ship(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if u["money"] >= 500:
        u["money"] -= 500; u["durability"] = 100
        save_data(data); await call.answer("Починено!"); await service_menu(call)
    else: await call.answer("Нет денег!")

@dp.callback_query(F.data == "pvp_menu")
async def pvp_menu(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⚔️ ИСКАТЬ БОЙ", callback_data="pvp_go"),
                                    types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"⚔️ АРЕНА (Побед: {u['pvp_wins']})", reply_markup=b.as_markup())

@dp.callback_query(F.data == "pvp_go")
async def pvp_go(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if random.random() > 0.5:
        u["pvp_wins"] += 1; u["xp"] += 500
        res = "ПОБЕДА! +500 XP"
    else:
        u["durability"] -= 20
        res = "ПОРАЖЕНИЕ! -20% Корпуса"
    save_data(data)
    await call.message.edit_text(res, reply_markup=InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="Назад", callback_data="pvp_menu")).as_markup())

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    u = load_data()["players"][uid]
    await call.message.edit_text(f"{HEADER}\n🚀 <b>ГЛАВНЫЙ ТЕРМИНАЛ</b>\n{SEP}\nОжидание команд...\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=main_kb(uid, u['xp']))

async def main():
    print("💎 ALMAZ-SYSTEM V3.0 ONLINE")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
