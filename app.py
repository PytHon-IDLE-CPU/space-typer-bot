import asyncio, random, json, os, logging, time, datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import LabeledPrice, PreCheckoutQuery

# ===================== [ КОНФИГУРАЦИЯ ] =====================
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 5056869104
DB_PATH = "/data/players.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
global_tasks = {}

HEADER = "<b>🧬 ╔═══════ [ OMEGA-SYSTEM ] ═══════╗</b>"
FOOTER = "<b>🧬 ╚═══════════════════════════════╝</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"

# ===================== [ ДАННЫЕ ] =====================
# (CASES, SHIPS, FACTIONS остаются такими же, как в твоем коде)
CASES = {
    "free": {"n": "🎁 БЕСПЛАТНЫЙ", "p": 0, "drop": {"money": (500, 2000), "xp": (10, 50)}, "chance": "Обычный"},
    "beta": {"n": "🧪 БЕТА-КЕЙС", "p": 5000, "drop": {"money": (3000, 10000), "xp": (50, 200)}, "chance": "Средний"},
    "ref":  {"n": "🔗 РЕФЕРАЛЬНЫЙ", "p": 0, "drop": {"money": (10000, 30000), "xp": (200, 500)}, "chance": "Высокий"},
    "cheap": {"n": "📦 НЕДОРОГОЙ", "p": 15000, "drop": {"money": (10000, 25000), "xp": (100, 300)}, "chance": "Обычный"},
    "mid":   {"n": "💎 СРЕДНИЙ", "p": 100000, "drop": {"money": (80000, 250000), "xp": (500, 1500)}, "chance": "Хороший"},
    "rich":  {"n": "💰 ДЛЯ БОГАТЫХ", "p": 1000000, "drop": {"money": (900000, 3000000), "xp": (2000, 10000)}, "chance": "Эпик"},
    "ultra": {"n": "👑 МИЛЛИОНЕР", "p": 50000000, "drop": {"money": (45000000, 150000000), "xp": (50000, 200000)}, "chance": "Легенда"}
}

SHIPS = {
    "shuttle":      {"name": "🛸 'Бродяга'",           "price": 0,             "mult": 1.0,      "lvl": 1},
    "scout":        {"name": "📡 'Разведчик С-12'",    "price": 500,           "mult": 1.5,      "lvl": 2},
    "interceptor":  {"name": "⚡️ 'Стриж'",            "price": 2000,          "mult": 2.2,      "lvl": 3},
    "drone_eye":    {"name": "👁 'Око Саурона'",       "price": 7500,          "mult": 3.8,      "lvl": 4},
    "hauler":       {"name": "🚜 'Косм. Бык'",         "price": 18000,         "mult": 5.5,      "lvl": 5},
    "fighter":      {"name": "⚔️ 'Валькирия'",        "price": 45000,         "mult": 11.0,     "lvl": 7},
    "bomber":       {"name": "💣 'Сверхновая'",        "price": 120000,        "mult": 20.0,     "lvl": 9},
    "corvette":     {"name": "🛡 'Бастион'",          "price": 300000,        "mult": 35.0,     "lvl": 11},
    "frigate":      {"name": "🔱 'Посейдон'",          "price": 850000,        "mult": 60.0,     "lvl": 13},
    "destroyer":    {"name": "🔥 'Гнев'",              "price": 1900000,       "mult": 130.0,    "lvl": 16},
    "cruiser":      {"name": "🛰 'Титан'",             "price": 5000000,       "mult": 320.0,    "lvl": 20},
    "carrier":      {"name": "🦅 'Фенрир'",            "price": 15000000,      "mult": 800.0,    "lvl": 25},
    "battleship":   {"name": "👑 'Император'",         "price": 35000000,      "mult": 1900.0,   "lvl": 30},
    "dreadnought":  {"name": "💀 'Бездна'",            "price": 100000000,     "mult": 5500.0,   "lvl": 38},
    "reaper":       {"name": "🩸 'Жнец'",              "price": 350000000,     "mult": 16000.0,  "lvl": 45},
    "nebula":       {"name": "🌌 'Скиталец'",          "price": 900000000,     "mult": 55000.0,  "lvl": 55},
    "kronos":       {"name": "⌛️ 'Кронос'",           "price": 3000000000,    "mult": 165000.0, "lvl": 70},
    "star_eater":   {"name": "🌑 'Пожиратель'",        "price": 15000000000,   "mult": 650000.0, "lvl": 85},
    "void_walker":  {"name": "👻 'Ходок'",             "price": 75000000000,   "mult": 2200000.0,"lvl": 100},
    "infinity":     {"name": "♾ 'Бесконечность'",      "price": 300000000000,  "mult": 11000000.0,"lvl": 120},
    "creator":      {"name": "✨ 'ТВОРЕЦ'",            "price": 777777777777,  "mult": 60000000.0,"lvl": 150}
}

FACTIONS = {
    "empire": {"n": "⚔️ Империя", "b": "+20% к XP", "id": "emp"},
    "rebels": {"n": "🛠 Повстанцы", "b": "+15% к доходу", "id": "reb"},
    "syndicate": {"n": "💎 Синдикат", "b": "-10% потерь в казино", "id": "syn"}
}

PHRASES = ["✨ Ваша туманность светится...", "🧬 Аминокислоты зародились...", "🌿 Зеленый покров...", "🧠 Огонь освоен..."]

# ===================== [ СИСТЕМА ДАННЫХ ] =====================
def load_data():
    if not os.path.exists(DB_PATH): 
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {"players": {}, "market": []} # Добавили список market
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f:
            d = json.load(f)
            if "market" not in d: d["market"] = []
            return d
    except: return {"players": {}, "market": []}

def save_data(data):
    with open(DB_PATH, "w", encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)

def get_lvl(xp): return int(xp**0.5 // 2) + 1

# ===================== [ КЛАВИАТУРА ] =====================
def main_kb(uid):
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 НЕЙРО-СИНТЕЗ", callback_data="game_go"))
    b.row(types.InlineKeyboardButton(text="👤 ПРОФИЛЬ", callback_data="view_profile"),
          types.InlineKeyboardButton(text="🛒 ВЕРФЬ", callback_data="open_shop_0"))
    b.row(types.InlineKeyboardButton(text="🏛 БИРЖА", callback_data="market_view_0"), # Новая кнопка
          types.InlineKeyboardButton(text="📦 КЕЙСЫ", callback_data="cases_menu"))
    b.row(types.InlineKeyboardButton(text="🛠 СЕРВИС", callback_data="service_menu"),
          types.InlineKeyboardButton(text="📅 АДВЕНТ", callback_data="advent_menu"))
    b.row(types.InlineKeyboardButton(text="🎰 КАЗИНО", callback_data="casino_menu"),
          types.InlineKeyboardButton(text="⚔️ PVP БОЙ", callback_data="pvp_menu"))
    b.row(types.InlineKeyboardButton(text="🏳️ ФРАКЦИЯ", callback_data="faction_menu"),
          types.InlineKeyboardButton(text="💎 STARS", callback_data="star_shop"))
    if int(uid) == ADMIN_ID: b.row(types.InlineKeyboardButton(text="🛡 АДМИН", callback_data="admin_main"))
    return b.as_markup()

# ===================== [ ТОРГОВАЯ БИРЖА ] =====================
@dp.callback_query(F.data.startswith("market_view_"))
async def market_view(call: types.CallbackQuery):
    page = int(call.data.split("_")[2])
    data = load_data(); m = data["market"]
    b = InlineKeyboardBuilder()
    text = f"{HEADER}\n🏛 <b>МЕЖГАЛАКТИЧЕСКАЯ БИРЖА</b>\n{SEP}\n"
    
    if not m:
        text += "Лотов пока нет. Будь первым!\n"
    else:
        # Пагинация лотов (по 5 на страницу)
        start_idx = page * 5; end_idx = start_idx + 5
        for idx, lot in enumerate(m[start_idx:end_idx]):
            ship_name = SHIPS[lot['ship_id']]['name']
            text += f"🏷 <b>{ship_name}</b>\n└ Цена: <code>{lot['price']:,}</code> CR\n└ Продавец: {lot['seller_name']}\n\n"
            b.row(types.InlineKeyboardButton(text=f"Купить {ship_name}", callback_data=f"market_buy_{start_idx + idx}"))

    b.row(types.InlineKeyboardButton(text="➕ ПРОДАТЬ СВОЙ", callback_data="market_sell_list"))
    
    nav = []
    if page > 0: nav.append(types.InlineKeyboardButton(text="⬅️", callback_data=f"market_view_{page-1}"))
    nav.append(types.InlineKeyboardButton(text="↩️ МЕНЮ", callback_data="back_main"))
    if len(m) > (page + 1) * 5: nav.append(types.InlineKeyboardButton(text="➡️", callback_data=f"market_view_{page+1}"))
    b.row(*nav)
    
    await call.message.edit_text(text + FOOTER, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "market_sell_list")
async def market_sell_list(call: types.CallbackQuery):
    uid = str(call.from_user.id); data = load_data(); u = data["players"][uid]
    b = InlineKeyboardBuilder()
    text = f"{HEADER}\n📤 <b>ВЫСТАВИТЬ НА ПРОДАЖУ</b>\n{SEP}\nВыбери корабль из инвентаря:\n"
    
    for sid in u["inventory"]:
        if sid == "shuttle": continue # Шаттл нельзя продать
        if sid == u["ship"]: continue # Нельзя продать то, на чем летишь
        b.row(types.InlineKeyboardButton(text=SHIPS[sid]['name'], callback_data=f"market_setprice_{sid}"))
    
    b.row(types.InlineKeyboardButton(text="↩️ ОТМЕНА", callback_data="market_view_0"))
    await call.message.edit_text(text + FOOTER, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("market_setprice_"))
async def market_setprice(call: types.CallbackQuery):
    sid = call.data.split("_")[2]
    # Используем временное хранилище или просим ввести цену
    await call.message.answer(f"Чтобы выставить {SHIPS[sid]['name']} на биржу, введи команду:\n<code>/sell {sid} ЦЕНА</code>\n\nПример: <code>/sell scout 10000</code>")

@dp.message(Command("sell"))
async def market_sell_process(msg: types.Message):
    args = msg.text.split()
    if len(args) < 3: return await msg.answer("❌ Формат: /sell [id_корабля] [цена]")
    
    sid, price = args[1], args[2]
    if not price.isdigit(): return await msg.answer("❌ Цена должна быть числом!")
    price = int(price); uid = str(msg.from_user.id); data = load_data(); u = data["players"][uid]
    
    if sid not in u["inventory"] or sid == "shuttle" or sid == u["ship"]:
        return await msg.answer("❌ Нельзя продать этот корабль!")
    
    # Убираем из инвентаря и добавляем в маркет
    u["inventory"].remove(sid)
    data["market"].append({
        "seller_id": uid,
        "seller_name": u["name"],
        "ship_id": sid,
        "price": price
    })
    save_data(data)
    await msg.answer(f"✅ {SHIPS[sid]['name']} выставлен на биржу за {price:,} CR!", reply_markup=main_kb(uid))

@dp.callback_query(F.data.startswith("market_buy_"))
async def market_buy(call: types.CallbackQuery):
    idx = int(call.data.split("_")[2]); uid = str(call.from_user.id); data = load_data()
    u = data["players"][uid]
    
    if idx >= len(data["market"]): return await call.answer("❌ Лот уже продан!", show_alert=True)
    
    lot = data["market"][idx]
    if lot["seller_id"] == uid: return await call.answer("❌ Ты не можешь купить свой же лот!", show_alert=True)
    if u["money"] < lot["price"]: return await call.answer("❌ Недостаточно кредитов!", show_alert=True)
    
    # Процесс сделки
    u["money"] -= lot["price"]
    u["inventory"].append(lot["ship_id"])
    
    # Отдаем деньги продавцу
    seller_id = lot["seller_id"]
    if seller_id in data["players"]:
        data["players"][seller_id]["money"] += lot["price"]
    
    del data["market"][idx]
    save_data(data)
    
    await call.answer(f"🎉 Поздравляем с покупкой {SHIPS[lot['ship_id']]['name']}!", show_alert=True)
    await market_view(call)

# ===================== [ ОСТАЛЬНЫЕ СИСТЕМЫ ] =====================
# (Оставляешь весь свой код из предыдущего сообщения: start, service_menu, advent_menu и т.д.)
# Просто убедись, что main_kb(uid) обновлена как в моем примере.

@dp.callback_query(F.data == "back_main")
async def back_to_main(call: types.CallbackQuery):
    uid = str(call.from_user.id)
    await call.message.edit_text(f"{HEADER}\n🚀 <b>ГЛАВНЫЙ МОСТИК</b>\n{SEP}\nВыберите модуль:\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))

# 

@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id); data = load_data()
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000, "xp": 0, "ship": "shuttle", "inventory": ["shuttle"],
            "last_daily": 0, "vip": 1, "name": msg.from_user.first_name,
            "faction": None, "tuning": {"eng": 0, "atk": 0, "def": 0},
            "exp_end": 0, "durability": 100, "repair_until": 0,
            "own_service": False, "service_lvl": 1, "last_advent": 0
        }
        save_data(data)
    await msg.answer(f"{HEADER}\n🚀 <b>ПИЛОТ {msg.from_user.first_name.upper()}, ДОБРО ПОЖАЛОВАТЬ!</b>\n{SEP}\nВсе системы в норме.\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))

# (Здесь вставь все функции Кейсов, Сервиса, Адвента и Игры из своего прошлого кода)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
