import asyncio, random, json, os, logging, time, datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import LabeledPrice, PreCheckoutQuery

# ===================== [ КОНФИГУРАЦИЯ ] =====================
TOKEN = os.getenv("BOT_TOKEN") 

# Жесткая проверка токена при старте
if not TOKEN:
    logging.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Переменная BOT_TOKEN не установлена!")
    print("❌ ОШИБКА: Забыли указать BOT_TOKEN в переменных окружения.")
    exit(1)

ADMIN_ID = 5056869104
DB_PATH = "/data/players.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

global_tasks = {}
global_event = {"name": "Стазис", "bonus": 1.0}

HEADER = "<b>🧬 ╔═══════ [ OMEGA-SYSTEM ] ═══════╗</b>"
FOOTER = "<b>🧬 ╚═══════════════════════════════╝</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"

# ===================== [ ДАННЫЕ (БЕЗ ЭКОНОМИИ) ] =====================
PHRASES = [
    "✨ Ваша туманность начала светиться лазурным светом.", "🧬 В первичном океане зародились первые аминокислоты.",
    "🌿 Зеленый покров окутал материки планет.", "🐾 На сушу выбрались первые существа.",
    "🧠 Одна из рас научилась использовать огонь.", "🧬 Вы создали кремниевую форму жизни.",
    "🍄 Споры гигантских грибов захватили луну.", "🐋 В недрах гиганта зародились левиафаны.",
    "☄️ Метеоритный поток принес редкие изотопы.", "☀️ Звезда перешла в стадию красного гиганта.",
    "🕳 Рядом открылась микрочерная дыра.", "💥 Сверхновая вспыхнула в соседнем секторе.",
    "🌪 Ионный шторм вывел из строя связь.", "🧊 Ледниковый период сковал океаны.",
    "🌋 Извержение создало горы из кристаллов.", "🛰 Квантовый скачок открыл новую реальность.",
    "📡 Древний маяк начал подавать сигналы.", "💠 Вы построили Сферу Дайсона вокруг звезды.",
    "🛸 Неопознанный объект оставил капсулу.", "🌀 Открыт стабильный переход в туманность Андромеды.",
    "🦾 Цивилизация перешла на аугментации.", "💎 Найден кристалл 'Сердце Звезды'.",
    "🪐 Кольца планеты превратились в щит.", "🐚 Найдены города под водой.",
    "📜 Расшифрован код матрицы Вселенной.", "🧘 Найдена раса существ из света.",
    "🎼 Звезды издали гармоничный резонанс.", "🚪 Обнаружена дверь в Пустоту.",
    "🍏 Планета-сад расцвела миллионами цветов.", "🧩 Планета приняла форму куба.",
    "🕰 На спутнике время потекло вспять.", "☁️ Живое облако газа начало петь.",
    "👁 В центре галактики открылось Око Бездны.", "🧸 Найдена планета из мягкого пуха.",
    "🍭 Атмосфера луны пахнет карамелью.", "🗿 Гигантские статуи смотрят в небо.",
    "👑 Ваше имя высечено на кольцах Сатурна.", "🏗 Построен мост между мирами.",
    "🎭 Раса созданий считает вас Богом.", "🌊 Океан на планете стал разумным.",
    "🎇 Великий Парад Планет начался.", "🛡 Создан непробиваемый планетарный щит.",
    "🔋 Энергия вакуума течет в реакторы.", "🌈 В космосе расцвели звездные цветы.",
    "🕊 В системе наступила эпоха Мира.", "💎 Алмазный дождь на ваших колониях.",
    "🌑 Луна внезапно подмигнула вам.", "🌌 Вы создали новую галактику из пыли.",
    "🎷 Космический джаз на всех частотах.", "🛑 Время остановилось по приказу."
]

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
    "cruiser":      {"name": "🛰 'Титан'",              "price": 5000000,       "mult": 320.0,    "lvl": 20},
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

# ===================== [ СИСТЕМА ДАННЫХ ] =====================
def load_data():
    if not os.path.exists(DB_PATH): 
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {"players": {}, "news": "Галактика проснулась."}
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f: return json.load(f)
    except: return {"players": {}, "news": "Ошибка связи."}

def save_data(data):
    with open(DB_PATH, "w", encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)

def get_lvl(xp): return int(xp**0.5 // 2) + 1

def progress_bar(curr, total, size=10):
    perc = min(curr / total, 1.0)
    fill = int(size * perc)
    return "▰" * fill + "▱" * (size - fill)

# ===================== [ КЛАВИАТУРЫ ] =====================
def main_kb(uid, xp=0):
    lvl = get_lvl(xp)
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 НЕЙРО-СИНТЕЗ", callback_data="game_go"))
    b.row(types.InlineKeyboardButton(text=f"👤 ПРОФИЛЬ (Lvl {lvl})", callback_data="view_profile"),
          types.InlineKeyboardButton(text="🛒 ВЕРФЬ", callback_data="open_shop_0"))
    b.row(types.InlineKeyboardButton(text="🏦 БАНК", callback_data="bank_menu"),
          types.InlineKeyboardButton(text="🚜 ГАРАЖ", callback_data="garage_menu"))
    b.row(types.InlineKeyboardButton(text="🎰 КАЗИНО", callback_data="casino_menu"),
          types.InlineKeyboardButton(text="📦 КЕЙСЫ", callback_data="cases_menu"))
    b.row(types.InlineKeyboardButton(text="🛠 СЕРВИС", callback_data="service_menu"),
          types.InlineKeyboardButton(text="🎁 БОНУС", callback_data="daily_bonus"))
    if int(uid) == ADMIN_ID: b.row(types.InlineKeyboardButton(text="🛡 АДМИН", callback_data="admin_main"))
    return b.as_markup()

# ===================== [ ХЕНДЛЕРЫ ] =====================
@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id); data = load_data()
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000, "xp": 0, "ship": "shuttle", "inventory": ["shuttle"], 
            "bank": 0, "last_daily": 0, "name": msg.from_user.first_name,
            "faction": None, "tuning": {"eng": 0, "atk": 0, "def": 0},
            "durability": 100
        }
        save_data(data)
    u = data["players"][uid]
    await msg.answer(f"{HEADER}\n🚀 <b>ПИЛОТ {u['name'].upper()}, СИСТЕМА ОНЛАЙН!</b>\n{SEP}\nДоступ разрешен.\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=main_kb(uid, u['xp']))

@dp.callback_query(F.data == "view_profile")
async def profile(call: types.CallbackQuery):
    uid = str(call.from_user.id); u = load_data()["players"][uid]
    lvl = get_lvl(u['xp']); next_xp = (lvl * 2)**2
    bar = progress_bar(u['xp'], next_xp)
    text = (f"{HEADER}\n👤 <b>ПРОФИЛЬ:</b> {u['name']}\n{SEP}\n"
            f"📊 <b>Lvl:</b> {lvl}\n🧪 <b>XP:</b> {bar} ({u['xp']}/{next_xp})\n"
            f"💰 <b>Баланс:</b> {u['money']:,} CR\n🛸 <b>Корабль:</b> {SHIPS[u['ship']]['name']}\n{FOOTER}")
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=main_kb(uid, u['xp']))

@dp.callback_query(F.data == "cases_menu")
async def cases_ui(call: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    for cid, info in CASES.items():
        b.row(types.InlineKeyboardButton(text=f"{info['n']} ({info['p']:,} CR)", callback_data=f"open_case_{cid}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"{HEADER}\n📦 <b>МАГАЗИН КЕЙСОВ</b>\n{SEP}\nВыбери контейнер:\n{FOOTER}", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("open_case_"))
async def open_case(call: types.CallbackQuery):
    cid = call.data.split("_")[2]; uid = str(call.from_user.id); data = load_data(); u = data["players"][uid]
    info = CASES[cid]
    if u["money"] < info["p"]: return await call.answer("❌ Недостаточно средств!", show_alert=True)
    u["money"] -= info["p"]
    mr = random.randint(*info["drop"]["money"]); xr = random.randint(*info["drop"]["xp"])
    u["money"] += mr; u["xp"] += xr; save_data(data)
    await call.message.answer(f"📦 {info['n']} ОТКРЫТ!\n{SEP}\nНаграда: +{mr:,} CR | +{xr} XP", parse_mode=ParseMode.HTML)
    await cases_ui(call)

@dp.callback_query(F.data == "game_go")
async def game_start(call: types.CallbackQuery):
    phrase = random.choice(PHRASES); global_tasks[str(call.from_user.id)] = phrase
    await call.message.edit_text(f"{HEADER}\n🧩 <b>СИНТЕЗ:</b>\n<code>{phrase}</code>", parse_mode=ParseMode.HTML)

@dp.message()
async def game_logic(m: types.Message):
    uid = str(m.from_user.id); data = load_data()
    if uid in global_tasks and m.text == global_tasks[uid]:
        u = data["players"][uid]
        if u["durability"] <= 5: return await m.answer("🛠 Корабль слишком поврежден!")
        rew = int(random.randint(200, 500) * SHIPS[u["ship"]]["mult"])
        u["money"] += rew; u["xp"] += 20; u["durability"] -= 1
        save_data(data); del global_tasks[uid]
        await m.answer(f"✅ +{rew:,} CR | +20 XP", reply_markup=main_kb(uid, u['xp']))

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    await start(call.message)

# ===================== [ ЗАПУСК ] =====================
async def main():
    # Очистка очереди обновлений, чтобы бот не «лагал» после рестарта
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 OMEGA-SYSTEM запущен успешно!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
