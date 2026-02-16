import asyncio
import json
import random
import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FContext

# --- НАСТРОЙКИ ---
TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"
ADMIN_ID = 12345678 # Твой ID
DB_PATH = "omega_data.json"

# Визуал терминала
HEADER = "🧬 <b>╔═══════ [ OMEGA-SYSTEM ] ═══╗</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class FeedbackState(StatesGroup):
    waiting_for_idea = State()

# --- ЛОГИКА ДАННЫХ ---
def load_data():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"players": {}, "used_codes": {}}, f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid, name="Неизвестный"):
    uid = str(uid)
    data = load_data()
    if uid not in data["players"]:
        data["players"][uid] = {
            "name": name, "level": 1, "exp": 0, "credits": 1000,
            "hp": 100, "power": 10, "faction": "Нейтрал",
            "inventory": {"metal": 0, "chips": 0, "energy": 5, "keys": 0},
            "drone": None, "stats": {"luck": 0, "armor": 0},
            "bank": 0, "crypto_wallet": 0, "rad": 0, "food": 100,
            "last_search": None, "archive": ["Система активирована."]
        }
        save_data(data)
    return data["players"][uid]
def add_exp(uid, amount):
    uid = str(uid)
    data = load_data()
    u = data["players"][uid]
    u["exp"] += amount
    new_level = (u["exp"] // 500) + 1
    if new_level > u["level"]:
        u["level"] = new_level
        u["hp"] = 100
        u["power"] += 5
        save_data(data)
        return True
    save_data(data)
    return False

def get_title(level):
    titles = {0: "🔘 Скиталец", 5: "🟢 Оперативник", 10: "🔵 Техно-рыцарь", 20: "🟣 Хранитель", 50: "👑 Властелин"}
    return next((v for k, v in sorted(titles.items(), reverse=True) if level >= k), titles[0])

def get_weather():
    h = datetime.now().hour
    if 0 <= h < 7: return {"name": "⛈ ЭМИ-Шторм", "bonus": 0.5}
    if 18 <= h < 22: return {"name": "🌌 Сияние", "bonus": 2.0}
    return {"name": "☀️ Ясно", "bonus": 1.0}

def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"), 
           types.InlineKeyboardButton(text="🛰 Сканер", callback_data="anomaly_scanner"))
    kb.row(types.InlineKeyboardButton(text="🔍 Поиск", callback_data="search_logic"), 
           types.InlineKeyboardButton(text="🤖 Ангар", callback_data="drone_hub"))
    kb.row(types.InlineKeyboardButton(text="🧪 Лаба", callback_data="lab_menu"), 
           types.InlineKeyboardButton(text="☢️ Выживание", callback_data="survival_hub"))
    kb.row(types.InlineKeyboardButton(text="🛒 Магазин", callback_data="shop_menu"), 
           types.InlineKeyboardButton(text="💎 ДОНАТ", callback_data="donate_menu"))
    kb.row(types.InlineKeyboardButton(text="⚔️ Арена", callback_data="pvp_menu"), 
           types.InlineKeyboardButton(text="📈 Биржа", callback_data="crypto_menu"))
    kb.row(types.InlineKeyboardButton(text="🏆 Топ", callback_data="top_players"), 
           types.InlineKeyboardButton(text="💡 Идея", callback_data="suggest_idea"))
    return kb.as_markup()
def main_menu_kb():
    kb = InlineKeyboardBuilder()
    # Ряд 1: Главное
    kb.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"), 
           types.InlineKeyboardButton(text="🔍 Поиск", callback_data="search_logic"))
    # Ряд 2: Война
    kb.row(types.InlineKeyboardButton(text="⚔️ Арена", callback_data="pvp_menu"), 
           types.InlineKeyboardButton(text="👾 МИРОВОЙ БОСС", callback_data="raid_boss"))
    # Ряд 3: Экономика
    kb.row(types.InlineKeyboardButton(text="📈 Биржа", callback_data="crypto_menu"), 
           types.InlineKeyboardButton(text="🔮 Артефакты", callback_data="art_market"))
    # Ряд 4: Социум
    kb.row(types.InlineKeyboardButton(text="🏢 Кланы", callback_data="clan_menu"), 
           types.InlineKeyboardButton(text="📅 Задания", callback_data="daily_tasks"))
    # Ряд 5: Техника
    kb.row(types.InlineKeyboardButton(text="🤖 Ангар", callback_data="drone_hub"), 
           types.InlineKeyboardButton(text="🎒 Склад", callback_data="inv_menu"))
    # Ряд 6: Поддержка
    kb.row(types.InlineKeyboardButton(text="💎 ДОНАТ ⭐", callback_data="donate_menu"),
           types.InlineKeyboardButton(text="💡 Идея", callback_data="suggest_idea"))
    
    return kb.as_markup()
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    u = get_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f"{HEADER}\nДобро пожаловать в систему, {u['name']}!\n{SEP}", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "profile")
async def view_profile(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n👤 <b>ДОСЬЕ: {u['name']}</b>\n{SEP}\n"
            f"🎖 Уровень: {u['level']} | Ранг: {get_title(u['level'])}\n"
            f"💳 Кредиты: {u['credits']} | 🏦 Банк: {u['bank']}\n"
            f"☢️ Радиация: {u['rad']} | 🍞 Сытость: {u['food']}%\n{SEP}")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📜 Архив", callback_data="archive_records"),
           types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "search_logic")
async def search_handler(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    # Проверка Кулдауна
    if u["last_search"]:
        last = datetime.fromisoformat(u["last_search"])
        if datetime.now() < last + timedelta(seconds=30):
            return await call.answer("⏳ Системы перегружены. Ждите 30 сек.", show_alert=True)

    w = get_weather()
    res = random.choice(["metal", "chips", "nothing"])
    u["last_search"] = datetime.now().isoformat()
    u["rad"] += random.randint(1, 5)
    
    msg = "🛰 Поиск не дал результатов..."
    if res != "nothing":
        amt = int(random.randint(5, 15) * w["bonus"])
        u["inventory"][res] += amt
        msg = f"📦 Найдено: {amt} ед. {res}!"
    
    save_data(data)
    add_exp(uid, 50)
    await call.answer(msg, show_alert=True)
    await call.message.edit_text(f"{HEADER}\n{msg}\n{SEP}\nПогода: {w['name']}", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "back_to_main")
async def back_main(call: types.CallbackQuery):
    await call.message.edit_text(f"{HEADER}\nГлавный терминал активен.\n{SEP}", reply_markup=main_menu_kb())

# --- ФИДБЕК ---
@dp.callback_query(F.data == "suggest_idea")
async def idea_start(call: types.CallbackQuery, state: FContext):
    await state.set_state(FeedbackState.waiting_for_idea)
    await call.message.answer("📝 Введите вашу идею одним сообщением:")

@dp.message(FeedbackState.waiting_for_idea)
async def idea_process(message: types.Message, state: FContext):
    await bot.send_message(ADMIN_ID, f"💡 ИДЕЯ от {message.from_user.id}: {message.text}")
    await message.answer("✅ Отправлено админу!")
    await state.clear()
@dp.callback_query(F.data == "profile")
async def view_profile(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    # Генерируем красивую полоску опыта
    progress = (u['exp'] % 500) // 50
    bar = "🟩" * progress + "⬜" * (10 - progress)
    
    text = (
        f"{HEADER}\n"
        f"👤 <b>ОПЕРАТОР: {u['name']}</b>\n"
        f"{SEP}\n"
        f"🎖 Ранг: <b>{get_title(u['level'])}</b> ({u['level']} ур.)\n"
        f"📈 Опыт: <code>[{bar}]</code>\n"
        f"💳 Баланс: <code>{u['credits']} кр.</code>\n"
        f"☢️ Радиация: <code>{u['rad']} mSv</code>\n"
        f"🛡 Фракция: <i>{u.get('faction', 'Нейтрал')}</i>\n"
        f"{SEP}"
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🏅 Медали", callback_data="medals_menu"),
           types.InlineKeyboardButton(text="🎒 Склад", callback_data="inv_menu"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())
# ===================== [ МОДУЛЬ: ДРОНЫ И BP ] =====================
@dp.callback_query(F.data == "drone_hub")
async def drone_menu(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    d = u.get("drone")
    
    if not d:
        text = f"{HEADER}\n🤖 <b>АНГАР</b>\n{SEP}\nУ вас пока нет активного дрона.\nСтоимость базовой модели: 5000 кр."
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🛠 Купить дрона (5000 кр.)", callback_data="buy_drone"))
    else:
        text = (f"{HEADER}\n🤖 <b>ДРОН: {d['name']}</b>\n{SEP}\n"
                f"🔋 Заряд: {d['battery']}%\n"
                f"📦 Собранные ресурсы: {d['storage']} ед.\n{SEP}")
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🔋 Зарядить (1 Энергия)", callback_data="charge_drone"))
        kb.row(types.InlineKeyboardButton(text="📦 Собрать ресурсы", callback_data="collect_drone"))
    
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "collect_drone")
async def collect_drone(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if u["drone"] and u["drone"]["storage"] > 0:
        amt = u["drone"]["storage"]
        u["credits"] += amt * 10
        u["drone"]["storage"] = 0
        save_data(data)
        await call.answer(f"💰 Дрон разгружен! Получено {amt * 10} кр.")
        await drone_menu(call)
    else:
        await call.answer("📭 Хранилище дрона пусто.")

@dp.callback_query(F.data == "buy_drone")
async def buy_drone(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if u["credits"] >= 5000:
        u["credits"] -= 5000
        u["drone"] = {"name": "M-300", "battery": 100, "storage": 0}
        save_data(data)
        await call.answer("🤖 Дрон приобретен и готов к работе!")
        await drone_menu(call)
    else:
        await call.answer("❌ Недостаточно кредитов!", show_alert=True)
# ===================== [ МОДУЛЬ: КРИПТА И ВЗЛОМ ] =====================
@dp.callback_query(F.data == "crypto_menu")
async def crypto_handler(call: types.CallbackQuery):
    price = get_crypto_price() # Функция из Блока 2
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n📈 <b>OMEGA-EXCHANGE</b>\n{SEP}\n"
            f"Курс Ω-Coin: <code>{price} кр.</code>\n"
            f"Ваш кошелек: <b>{u.get('crypto_wallet', 0)} Ω</b>\n{SEP}\n"
            f"<i>Курс обновляется каждые 15 минут!</i>")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📥 Купить 1 Ω", callback_data="buy_crypto"),
           types.InlineKeyboardButton(text="📤 Продать всё", callback_data="sell_crypto"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "buy_crypto")
async def buy_crypto(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    price = get_crypto_price()
    u = data["players"][uid]
    if u["credits"] >= price:
        u["credits"] -= price
        u["crypto_wallet"] = u.get("crypto_wallet", 0) + 1
        save_data(data)
        await call.answer(f"✅ Куплено 1 Ω за {price} кр.")
        await crypto_handler(call)
    else:
        await call.answer("❌ Недостаточно кредитов!", show_alert=True)

@dp.callback_query(F.data == "anomaly_scanner")
async def hack_menu(call: types.CallbackQuery):
    text = (f"{HEADER}\n📟 <b>ТЕРМИНАЛ ВЗЛОМА</b>\n{SEP}\n"
            f"Попытка взлома защищенного узла банка.\n"
            f"Шанс успеха: 30%\n"
            f"Награда: 3000-7000 кр.\n"
            f"Риск: Блокировка поиска на 10 мин.\n{SEP}")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⚡️ НАЧАТЬ ВЗЛОМ", callback_data="start_hack"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "start_hack")
async def start_hack(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if random.random() < 0.3:
        win = random.randint(3000, 7000)
        u["credits"] += win
        res = f"🟢 <b>УСПЕХ!</b>\nПолучено: {win} кр."
    else:
        u["last_search"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        res = "🔴 <b>ПРОВАЛ!</b>\nСистема заблокирована на 10 минут."
    save_data(data)
    await call.message.answer(f"{HEADER}\n{res}\n{SEP}", parse_mode="HTML")
    await back_main(call)
# ===================== [ МОДУЛЬ: ВЫЖИВАНИЕ И ТОП ] =====================
@dp.callback_query(F.data == "survival_hub")
async def survival_menu(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n☢️ <b>БИО-МОНИТОР</b>\n{SEP}\n"
            f"Радиация: <code>{u['rad']}/100</code>\n"
            f"Сытость: <code>{u['food']}%</code>\n"
            f"Здоровье (HP): <code>{u['hp']}/100</code>\n{SEP}\n"
            f"<i>Если радиация > 70, вы начнете терять HP!</i>")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="💉 Антирадин (800 кр.)", callback_data="buy_med"),
           types.InlineKeyboardButton(text="🍞 Паек (300 кр.)", callback_data="buy_food"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "top_players")
async def top_players(call: types.CallbackQuery):
    data = load_data()
    # Сортировка топ-5 по уровню и опыту
    top = sorted(data["players"].values(), key=lambda x: (x['level'], x['exp']), reverse=True)[:5]
    text = f"{HEADER}\n🏆 <b>ТОП-5 ОПЕРАТОРОВ</b>\n{SEP}\n"
    for i, p in enumerate(top, 1):
        text += f"{i}. <code>{p['name']}</code> — Ур. {p['level']}\n"
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "lab_menu")
async def lab_menu(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n🧪 <b>ЛАБОРАТОРИЯ</b>\n{SEP}\n"
            f"Улучшение чипов защиты:\n"
            f"🍀 Удача: Lvl {u['stats']['luck']}\n"
            f"🛡 Броня: Lvl {u['stats']['armor']}\n{SEP}\n"
            f"Цена улучшения: 5000 кр.")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🍀 Качнуть Удачу", callback_data="up_luck"),
           types.InlineKeyboardButton(text="🛡 Качнуть Броню", callback_data="up_armor"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())
# ===================== [ МОДУЛЬ: СКЛАД И КРАФТ ] =====================
@dp.callback_query(F.data == "inv_menu")
async def inventory_handler(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    items = u.get("inventory", [])
    
    inv_text = ""
    if not items:
        inv_text = "<i>Пусто...</i>"
    else:
        # Считаем количество одинаковых предметов
        from collections import Counter
        counts = Counter(items)
        for item, count in counts.items():
            inv_text += f"📦 {item} — {count} шт.\n"

    text = (f"{HEADER}\n🎒 <b>ЛИЧНЫЙ СКЛАД</b>\n{SEP}\n"
            f"{inv_text}\n{SEP}\n"
            f"Вместимость: {len(items)}/20")
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🛠 Крафт (из мусора)", callback_data="craft_menu"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "shop_menu")
async def shop_handler(call: types.CallbackQuery):
    text = (f"{HEADER}\n🛒 <b>ЧЕРНЫЙ РЫНОК</b>\n{SEP}\n"
            f"🔹 <b>Детектор 'Велес'</b> (5000 кр)\n"
            f"<i>+20% к шансу найти редкий арт</i>\n\n"
            f"🔹 <b>Экзоскелет</b> (15000 кр)\n"
            f"<i>Защита от радиации +50%</i>\n{SEP}")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Купить 'Велес'", callback_data="buy_veles"),
           types.InlineKeyboardButton(text="Купить Экзо", callback_data="buy_exo"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_item_logic(call: types.CallbackQuery):
    item_type = call.data.split("_")[1]
    prices = {"veles": 5000, "exo": 15000}
    names = {"veles": "Детектор 'Велес'", "exo": "Экзоскелет"}
    
    data = load_data()
    u = data["players"][str(call.from_user.id)]
    
    if u["credits"] >= prices[item_type]:
        u["credits"] -= prices[item_type]
        u.setdefault("inventory", []).append(names[item_type])
        save_data(data)
        await call.answer(f"✅ Куплено: {names[item_type]}")
        await shop_handler(call)
    else:
        await call.answer("❌ Недостаточно средств!", show_alert=True)
# ===================== [ МОДУЛЬ: КЕЙСЫ И ДОНАТ ] =====================
@dp.callback_query(F.data == "cases_menu")
async def cases_menu(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n🎁 <b>КЕЙСЫ</b>\n{SEP}\n"
            f"Ключи в наличии: {u['inventory']['keys']} шт.\n{SEP}\n"
            f"Кейс содержит кредиты, опыт или микросхемы.")
    kb = InlineKeyboardBuilder()
    if u["inventory"]["keys"] > 0:
        kb.row(types.InlineKeyboardButton(text="🔓 Открыть (1 ключ)", callback_data="open_case"))
    kb.row(types.InlineKeyboardButton(text="🛒 Купить ключ (1000 кр.)", callback_data="buy_key"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "buy_key")
async def buy_key(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if u["credits"] >= 1000:
        u["credits"] -= 1000
        u["inventory"]["keys"] += 1
        save_data(data)
        await call.answer("🔑 Ключ куплен!")
        await cases_menu(call)
    else:
        await call.answer("❌ Недостаточно кредитов!", show_alert=True)

@dp.callback_query(F.data == "donate_menu")
async def donate_menu(call: types.CallbackQuery):
    text = (f"{HEADER}\n💎 <b>ПОДДЕРЖКА СИСТЕМЫ</b>\n{SEP}\n"
            f"Покупка за Telegram Stars ⭐\n\n"
            f"• 👑 VIP Статус — 150 ⭐\n"
            f"• 📦 Стартовый пак — 50 ⭐")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👑 VIP (150 ⭐)", callback_data="buy_vip"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())
# ===================== [ МОДУЛЬ: ГЛОБАЛЬНЫЕ ИВЕНТЫ ] =====================
def get_global_event():
    """Случайные события, меняющиеся каждый час"""
    hour = datetime.now().hour
    if 18 <= hour <= 21:
        return {"name": "🔥 ЗОЛОТАЯ ЛИХОРАДКА", "multi": 3.0, "desc": "Кредиты в поиске x3!"}
    if 0 <= hour <= 6:
        return {"name": "🌑 НОЧНАЯ СМЕНА", "multi": 1.5, "desc": "Опыт x1.5 за все действия."}
    return {"name": "🤖 СТАНДАРТ", "multi": 1.0, "desc": "Обычный режим работы."}

# ===================== [ МОДУЛЬ: БАНКОВСКОЕ ХРАНИЛИЩЕ ] =====================
@dp.callback_query(F.data == "bank_vault")
async def bank_handler(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    if "bank" not in u: u["bank"] = 0
    
    text = (f"{HEADER}\n🏦 <b>ЦЕНТРАЛЬНЫЙ БАНК</b>\n{SEP}\n"
            f"На руках: <code>{u['credits']} кр.</code>\n"
            f"В сейфе: <code>{u['bank']} кр.</code>\n{SEP}\n"
            f"<i>Деньги в сейфе защищены от налогов и воров!</i>")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📥 Положить 1000", callback_data="bank_deposit"),
           types.InlineKeyboardButton(text="📤 Снять 1000", callback_data="bank_withdraw"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("bank_"))
async def bank_logic(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    if "bank" not in u: u["bank"] = 0

    if action == "deposit":
        if u["credits"] >= 1000:
            u["credits"] -= 1000
            u["bank"] += 1000
        else:
            return await call.answer("❌ Недостаточно наличных!", show_alert=True)
    else:
        if u["bank"] >= 1000:
            u["bank"] -= 1000
            u["credits"] += 1000
        else:
            return await call.answer("❌ В сейфе пусто!", show_alert=True)
            
    save_data(data)
    await bank_handler(call)

# ===================== [ МОДУЛЬ: ТЕРМИНАЛ СВЯЗИ (ПОЧТА) ] =====================
@dp.message(F.text.startswith("/mail"))
async def send_mail(message: types.Message):
    """Отправка сообщения другому игроку: /mail [ID] [Текст]"""
    try:
        parts = message.text.split(maxsplit=2)
        target_id = parts[1]
        msg_text = parts[2]
        
        await bot.send_message(target_id, 
            f"{HEADER}\n📩 <b>ВХОДЯЩЕЕ ПИСЬМО</b>\n{SEP}\n"
            f"От: <code>{message.from_user.id}</code>\n"
            f"Текст: <i>{msg_text}</i>\n{SEP}", parse_mode="HTML")
        await message.answer("✅ Сообщение отправлено в личный терминал адресата.")
    except:
        await message.answer("📝 Формат: <code>/mail ID Текст</code>", parse_mode="HTML")

# ===================== [ МОДУЛЬ: РЕФЕРАЛЬНАЯ СИСТЕМА ] =====================
@dp.callback_query(F.data == "referral_menu")
async def referral_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    text = (f"{HEADER}\n🤝 <b>РЕФЕРАЛЬНЫЙ ЦЕНТР</b>\n{SEP}\n"
            f"Ваш ID: <code>{uid}</code>\n{SEP}\n"
            f"Приглашайте друзей! Пусть введут <code>/start {uid}</code>\n"
            f"Вы оба получите по <b>5,000 кр.</b>")
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())
# ===================== [ МОДУЛЬ: АРТЕФАКТЫ ] =====================
ARTS = {
    "eye": {"name": "👁 Глаз Бури", "luck": 5, "price": 10000},
    "heart": {"name": "🔋 Сердце Ядра", "power": 10, "price": 25000},
    "shield": {"name": "🛡 Осколок Эгиды", "armor": 15, "price": 15000}
}

@dp.callback_query(F.data == "art_market")
async def art_market(call: types.CallbackQuery):
    text = f"{HEADER}\n🔮 <b>РЫНОК АРТЕФАКТОВ</b>\n{SEP}\n"
    kb = InlineKeyboardBuilder()
    
    for key, val in ARTS.items():
        text += f"• {val['name']} | Цена: {val['price']} кр.\n"
        kb.row(types.InlineKeyboardButton(text=f"Купить {val['name']}", callback_data=f"buyart_{key}"))
        
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("buyart_"))
async def buy_art_logic(call: types.CallbackQuery):
    art_key = call.data.split("_")[1]
    art = ARTS[art_key]
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if u["credits"] >= art["price"]:
        u["credits"] -= art["price"]
        # Добавляем бонусы сразу к статам персонажа
        if "luck" in art: u["stats"]["luck"] += art["luck"]
        if "power" in art: u["power"] += art["power"]
        if "armor" in art: u["stats"]["armor"] += art["armor"]
        
        save_data(data)
        await call.answer(f"✨ Артефакт {art['name']} активирован пассивно!", show_alert=True)
        await art_market(call)
    else:
        await call.answer("❌ Не хватает кредитов!", show_alert=True)
# ===================== [ МОДУЛЬ: АРЕНА И ФРАКЦИИ ] =====================
@dp.callback_query(F.data == "pvp_menu")
async def pvp_handler(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = (f"{HEADER}\n⚔️ <b>АРЕНА ГЛАДИАТОРОВ</b>\n{SEP}\n"
            f"Ваша боевая мощь: {u['power']}\n"
            f"Стоимость входа: 500 кр.\n{SEP}")
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="👊 Найти противника", callback_data="pvp_fight"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "pvp_fight")
async def pvp_fight(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if u["credits"] < 500: return await call.answer("❌ Нет денег на взнос!", show_alert=True)
    if u["hp"] < 30: return await call.answer("⚠️ Вы слишком ранены!", show_alert=True)
    
    u["credits"] -= 500
    enemy_power = random.randint(u["power"] - 5, u["power"] + 10)
    
    if u["power"] >= enemy_power:
        win = random.randint(1000, 2500)
        u["credits"] += win
        u["power"] += 1
        res = f"🏆 <b>ПОБЕДА!</b>\nНаграда: +{win} кр. и +1 к мощи."
    else:
        u["hp"] -= 30
        res = f"💀 <b>ПОРАЖЕНИЕ...</b>\nВы потеряли 30 HP."
        
    save_data(data)
    add_exp(uid, 100)
    
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="pvp_menu"))
    await call.message.edit_text(f"{HEADER}\nИТОГ БОЯ:\n{SEP}\n{res}\n{SEP}", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "faction_menu")
async def faction_menu(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = f"{HEADER}\n🛡 <b>ВЫБОР ФРАКЦИИ</b>\n{SEP}\nТекущая сторона: {u['faction']}"
    kb = InlineKeyboardBuilder()
    if u["faction"] == "Нейтрал":
        kb.row(types.InlineKeyboardButton(text="🩸 Синдикат", callback_data="set_fac_Синдикат"))
        kb.row(types.InlineKeyboardButton(text="🛡 Миротворцы", callback_data="set_fac_Миротворцы"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_fac_"))
async def set_faction(call: types.CallbackQuery):
    fac = call.data.split("_")[2]
    uid = str(call.from_user.id)
    data = load_data()
    data["players"][uid]["faction"] = fac
    save_data(data)
    await call.answer(f"✅ Вы вступили в {fac}!")
    await faction_menu(call)
# ===================== [ МОДУЛЬ: СИНДИКАТЫ ] =====================
@dp.callback_query(F.data == "clan_menu")
async def clan_handler(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    # Инициализация списка кланов в базе, если его нет
    if "clans" not in data: data["clans"] = {}
    
    user_clan = u.get("clan")
    
    if not user_clan:
        text = (f"{HEADER}\n🛡 <b>ШТАБ СИНДИКАТОВ</b>\n{SEP}\n"
                f"Вы не состоите в синдикате.\n"
                f"Создание стоит: 50,000 кр.\n{SEP}")
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🏢 Создать Синдикат", callback_data="create_clan"))
    else:
        clan_data = data["clans"][user_clan]
        text = (f"{HEADER}\n🏢 <b>СИНДИКАТ: {user_clan}</b>\n{SEP}\n"
                f"👑 Лидер: <code>{clan_data['leader_name']}</code>\n"
                f"💰 Казна: <code>{clan_data['bank']} кр.</code>\n"
                f"👥 Членов: {len(clan_data['members'])}\n{SEP}")
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="📥 Внести в казну", callback_data="clan_deposit"))
    
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "create_clan")
async def create_clan_logic(call: types.CallbackQuery, state: FContext):
    u = get_user(call.from_user.id)
    if u["credits"] < 50000:
        return await call.answer("❌ Недостаточно кредитов для регистрации синдиката!", show_alert=True)
    
    await call.message.answer("📝 Введите название вашего Синдиката (одним словом):")
    # Используем временное состояние для ввода названия
    await state.set_state(FeedbackState.waiting_for_idea) # Можно переиспользовать или создать новое

@dp.callback_query(F.data == "clan_deposit")
async def clan_dep(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    clan_name = u["clan"]
    
    if u["credits"] >= 5000:
        u["credits"] -= 5000
        data["clans"][clan_name]["bank"] += 5000
        save_data(data)
        await call.answer("💎 Внесено 5,000 кр. в казну синдиката!")
        await clan_handler(call)
    else:
        await call.answer("❌ Нужно минимум 5,000 кр.", show_alert=True)
# ===================== [ МОДУЛЬ: МИРОВЫЕ БОССЫ ] =====================
BOSS_DATA = {
    "name": "⚙️ КИБЕР-ГЕГЕМОН",
    "hp": 50000,
    "reward": 100000,
    "icon": "👾"
}

@dp.callback_query(F.data == "raid_boss")
async def raid_menu(call: types.CallbackQuery):
    data = load_data()
    # Инициализация здоровья босса в БД, если его нет
    if "world_boss_hp" not in data:
        data["world_boss_hp"] = BOSS_DATA["hp"]
        save_data(data)
    
    current_hp = data["world_boss_hp"]
    u = get_user(call.from_user.id)
    
    text = (f"{HEADER}\n{BOSS_DATA['icon']} <b>МИРОВОЙ БОСС</b>\n{SEP}\n"
            f"Имя: <b>{BOSS_DATA['name']}</b>\n"
            f"Здоровье: <code>{current_hp}/{BOSS_DATA['hp']} HP</code>\n{SEP}\n"
            f"Ваша атака: <code>{u['power']}</code>\n"
            f"Затраты: 10 Энергии\n{SEP}")
    
    kb = InlineKeyboardBuilder()
    if current_hp > 0:
        kb.row(types.InlineKeyboardButton(text="⚔️ НАНЕСТИ УДАР", callback_data="attack_boss"))
    else:
        kb.row(types.InlineKeyboardButton(text="💀 БОСС ПОВЕРЖЕН", callback_data="boss_dead"))
    
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "attack_boss")
async def attack_boss(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    
    if u["inventory"]["energy"] < 10:
        return await call.answer("❌ Недостаточно энергии! Нужно 10 ед.", show_alert=True)
    
    dmg = u["power"] + random.randint(1, 10)
    data["world_boss_hp"] -= dmg
    u["inventory"]["energy"] -= 10
    
    # Награда за удар
    reward = dmg * 5
    u["credits"] += reward
    
    if data["world_boss_hp"] <= 0:
        data["world_boss_hp"] = 0
        msg = f"🎊 ВЫ НАНЕСЛИ ПОСЛЕДНИЙ УДАР! Босс повержен! Бонус: {BOSS_DATA['reward']} кр."
        u["credits"] += BOSS_DATA["reward"]
    else:
        msg = f"💥 Удар на {dmg} ед. Награда: {reward} кр."
        
    save_data(data)
    await call.answer(msg, show_alert=True)
    await raid_menu(call)
# ===================== [ МОДУЛЬ: ЗАХВАТ СЕКТОРА ] =====================
@dp.callback_query(F.data == "sector_control")
async def sector_handler(call: types.CallbackQuery):
    data = load_data()
    # Кто владеет сектором?
    owner = data.get("sector_owner", "Никто")
    u = get_user(call.from_user.id)
    
    text = (f"{HEADER}\n🛰 <b>СЕКТОР-7</b>\n{SEP}\n"
            f"Владелец: <b>{owner}</b>\n"
            f"Доход: <code>5,000 кр/час</code> в казну\n{SEP}\n"
            f"Чтобы захватить, ваш клан должен внести 20,000 кр. влияния.")
    
    kb = InlineKeyboardBuilder()
    if u.get("clan"):
        kb.row(types.InlineKeyboardButton(text="🚩 Захватить сектор", callback_data="capture_sector"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="clan_menu"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "capture_sector")
async def capture_logic(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    clan_name = u["clan"]
    
    if data.get("sector_owner") == clan_name:
        return await call.answer("🤝 Ваш синдикат уже контролирует эту зону!", show_alert=True)
    
    if u["credits"] < 20000:
        return await call.answer("❌ У вас нет 20,000 кр. для наемников!", show_alert=True)
        
    u["credits"] -= 20000
    data["sector_owner"] = clan_name
    save_data(data)
    
    await call.answer(f"🚩 СЕКТОР ЗАХВАЧЕН СИНДИКАТОМ {clan_name}!", show_alert=True)
    await sector_handler(call)
# ===================== [ МОДУЛЬ: КВЕСТЫ И НАГРАДЫ ] =====================
@dp.callback_query(F.data == "daily_tasks")
async def daily_handler(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    now = datetime.now().strftime("%Y-%m-%d")
    
    # Проверка, получал ли сегодня
    if u.get("last_daily_claim") == now:
        status = "✅ Выполнено"
    else:
        status = "🎁 Доступно"

    text = (f"{HEADER}\n📅 <b>ЕЖЕДНЕВНЫЙ ТЕРМИНАЛ</b>\n{SEP}\n"
            f"Статус пайка: <b>{status}</b>\n"
            f"Награда: 2,000 кр. + 1 Ключ\n{SEP}\n"
            f"<i>Заходи завтра за новой порцией ресурсов!</i>")
    
    kb = InlineKeyboardBuilder()
    if status == "🎁 Доступно":
        kb.row(types.InlineKeyboardButton(text="📦 Забрать паек", callback_data="claim_daily"))
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "claim_daily")
async def claim_daily(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    data = load_data()
    u = data["players"][uid]
    now = datetime.now().strftime("%Y-%m-%d")
    
    u["last_daily_claim"] = now
    u["credits"] += 2000
    u["inventory"]["keys"] += 1
    
    save_data(data)
    await call.answer("🎁 Вы получили суточный паек и ключ!", show_alert=True)
    await daily_handler(call)
# ===================== [ МОДУЛЬ: ДОСТИЖЕНИЯ ] =====================
ACHIEVEMENTS = {
    "rich": {"name": "💰 Миллионер", "desc": "Собрать 1,000,000 кр.", "req": 1000000},
    "warrior": {"name": "🎖 Ветеран", "desc": "Достичь 20 уровня", "req": 20},
    "miner": {"name": "⛏ Стахановец", "desc": "Собрать 500 металла", "req": 500}
}

@dp.callback_query(F.data == "medals_menu")
async def medals_handler(call: types.CallbackQuery):
    u = get_user(call.from_user.id)
    text = f"{HEADER}\n🏅 <b>ЗАЛ СЛАВЫ</b>\n{SEP}\n"
    
    # Логика проверки (пример)
    owned = []
    if u["credits"] >= ACHIEVEMENTS["rich"]["req"]: owned.append(ACHIEVEMENTS["rich"]["name"])
    if u["level"] >= ACHIEVEMENTS["warrior"]["req"]: owned.append(ACHIEVEMENTS["warrior"]["name"])
    
    if not owned:
        text += "<i>У вас пока нет медалей. Совершайте подвиги!</i>"
    else:
        for m in owned:
            text += f"⭐ <b>{m}</b>\n"
            
    text += f"\n{SEP}"
    kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="profile"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb.as_markup())
# ===================== [ МОДУЛЬ: АДМИН-ПАНЕЛЬ ] =====================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Доступ запрещен. Вы не администратор системы.")
    
    data = load_data()
    total_users = len(data["players"])
    
    text = (f"{HEADER}\n👑 <b>АДМИН-ЦЕНТР</b>\n{SEP}\n"
            f"👥 Всего игроков: <code>{total_users}</code>\n"
            f"👾 ХП Босса: <code>{data.get('world_boss_hp', 0)}</code>\n{SEP}\n"
            f"Команды:\n"
            f"<code>/give [ID] [сумма]</code> — выдать кр.\n"
            f"<code>/reset_boss</code> — возродить босса\n"
            f"<code>/broadcast [текст]</code> — рассылка")
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("give"))
async def admin_give(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, amount = parts[1], int(parts[2])
        data = load_data()
        if target_id in data["players"]:
            data["players"][target_id]["credits"] += amount
            save_data(data)
            await message.answer(f"✅ Игроку {target_id} выдано {amount} кр.")
            await bot.send_message(target_id, f"🎁 Администратор выдал вам {amount} кр.!")
    except:
        await message.answer("⚠️ Формат: /give [ID] [сумма]")

@dp.message(Command("reset_boss"))
async def admin_reset_boss(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    data = load_data()
    data["world_boss_hp"] = BOSS_DATA["hp"]
    save_data(data)
    await message.answer("✅ Мировой босс возрожден!")
# ===================== [ ЗАВЕРШЕНИЕ ФАЙЛА ] =====================

# Хендлер для текстовых сообщений (если кто-то просто пишет боту)
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(f"{HEADER}\n❓ <b>СПРАВКА</b>\n{SEP}\n"
                         f"Используй кнопки интерфейса для управления.\n"
                         f"Если кнопки пропали, напиши /start", parse_mode="HTML")

# Функция запуска
async def main():
    print("--- [ SYSTEM ONLINE ] ---")
    # Удаляем вебхуки и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("--- [ SYSTEM OFFLINE ] ---")
