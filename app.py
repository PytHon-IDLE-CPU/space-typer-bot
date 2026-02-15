import asyncio, random, json, os, logging, time, datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ===================== [ КОНФИГУРАЦИЯ ЯДРА ] =====================
TOKEN = os.getenv("BOT_TOKEN") # Railway сам подставит токен
ADMIN_ID = 5056869104          # Твой ID
VERSION = "OMEGA-GENESIS v1.0"
DB_PATH = "/data/players.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
global_tasks = {}

# ===================== [ ГРАФИЧЕСКИЙ ДВИЖОК UI ] =====================
# Элементы интерфейса "1000 разработчиков"
H_LINE = "━" * 15
DIVIDER = "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
HEADER_FRAME = "╔════════════ [ SYSTEM ] ════════════╗"
FOOTER_FRAME = "╚════════════════════════════════════╝"

def progress_bar(current, total, length=10):
    percent = min(1, current / total)
    filled = int(length * percent)
    return "█" * filled + "░" * (length - filled)

# ===================== [ БАЗА ДАННЫХ ЛОРА (50 ФРАЗ) ] =====================
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

JOKES = [
    "🚀 — Капитан, у нас дыра в обшивке! \n— Это технологическое отверстие для вентиляции вакуумом.",
    "🪐 — Почему Сатурн не женится? \n— Потому что он уже окольцован!",
    "👽 Инопланетяне прилетели на Землю, посмотрели цены на видеокарты и улетели майнить на астероидах.",
    "🛰 — Хьюстон, у нас проблемы. \n— У нас тоже, доллар опять вырос, держитесь там.",
    "🌑 Луна — это просто обратная сторона Солнца, когда оно спит. (Научный факт от прапорщика).",
    "🛸 Я не говорю, что это были пришельцы... но это были пришельцы.",
    "🤖 Искусственный интеллект решил уничтожить человечество, но залип в TikTok."
]

# ===================== [ ВЕРФЬ: ПОЛНЫЙ СПИСОК ] =====================
# НИКАКИХ УРЕЗАНИЙ. ВСЕ КОРАБЛИ С ОПИСАНИЕМ.
SHIPS = {
    "shuttle":      {"name": "🛸 'Бродяга'",           "price": 0,             "mult": 1.0,      "lvl": 1,   "desc": "Ржавая посудина, но она летает."},
    "scout":        {"name": "📡 'Разведчик С-12'",    "price": 500,           "mult": 1.5,      "lvl": 2,   "desc": "Легкий корпус, мощные сканеры."},
    "interceptor":  {"name": "⚡️ 'Стриж'",            "price": 2000,          "mult": 2.2,      "lvl": 3,   "desc": "Скорость превыше всего."},
    "drone_eye":    {"name": "👁 'Око Саурона'",       "price": 7500,          "mult": 3.8,      "lvl": 4,   "desc": "Всевидящий дрон наблюдения."},
    "hauler":       {"name": "🚜 'Косм. Бык'",         "price": 18000,         "mult": 5.5,      "lvl": 5,   "desc": "Тяжелый грузовик для руды."},
    "fighter":      {"name": "⚔️ 'Валькирия'",        "price": 45000,         "mult": 11.0,     "lvl": 7,   "desc": "Боевая классика флота."},
    "bomber":       {"name": "💣 'Сверхновая'",        "price": 120000,        "mult": 20.0,     "lvl": 9,   "desc": "Несет заряд антиматерии."},
    "corvette":     {"name": "🛡 'Бастион'",          "price": 300000,        "mult": 35.0,     "lvl": 11,  "desc": "Летающая крепость."},
    "frigate":      {"name": "🔱 'Посейдон'",          "price": 850000,        "mult": 60.0,     "lvl": 13,  "desc": "Флагман малых эскадр."},
    "destroyer":    {"name": "🔥 'Гнев'",              "price": 1900000,       "mult": 130.0,    "lvl": 16,  "desc": "Уничтожитель миров."},
    "cruiser":      {"name": "🛰 'Титан'",             "price": 5000000,       "mult": 320.0,    "lvl": 20,  "desc": "Тяжелый крейсер класса 'Доминатор'."},
    "carrier":      {"name": "🦅 'Фенрир'",            "price": 15000000,      "mult": 800.0,    "lvl": 25,  "desc": "Несет на борту 1000 истребителей."},
    "battleship":   {"name": "👑 'Император'",         "price": 35000000,      "mult": 1900.0,   "lvl": 30,  "desc": "Королевский линкор."},
    "dreadnought":  {"name": "💀 'Бездна'",            "price": 100000000,     "mult": 5500.0,   "lvl": 38,  "desc": "Запрещенное оружие галактики."},
    "reaper":       {"name": "🩸 'Жнец'",              "price": 350000000,     "mult": 16000.0,  "lvl": 45,  "desc": "Собирает урожай душ."},
    "nebula":       {"name": "🌌 'Скиталец'",          "price": 900000000,     "mult": 55000.0,  "lvl": 55,  "desc": "Рожденный в туманности."},
    "kronos":       {"name": "⌛️ 'Кронос'",           "price": 3000000000,    "mult": 165000.0, "lvl": 70,  "desc": "Управляет временем."},
    "star_eater":   {"name": "🌑 'Пожиратель'",        "price": 15000000000,   "mult": 650000.0, "lvl": 85,  "desc": "Питается солнцами."},
    "void_walker":  {"name": "👻 'Ходок'",             "price": 75000000000,   "mult": 2200000.0,"lvl": 100, "desc": "Существует вне измерений."},
    "infinity":     {"name": "♾ 'Бесконечность'",      "price": 300000000000,  "mult": 11000000.0,"lvl": 120, "desc": "Конец и начало всего."},
    "creator":      {"name": "✨ 'ТВОРЕЦ'",            "price": 777777777777,  "mult": 60000000.0,"lvl": 150, "desc": "БОЖЕСТВЕННАЯ СУЩНОСТЬ."}
}

# ===================== [ СИСТЕМА ДАННЫХ ] =====================
def load_data():
    if not os.path.exists(DB_PATH): 
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {"players": {}, "suggestions": []}
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f: return json.load(f)
    except: return {"players": {}, "suggestions": []}

def save_data(data):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)

def get_rank(lvl):
    if lvl < 5: return "Курсант"
    if lvl < 10: return "Пилот"
    if lvl < 20: return "Капитан"
    if lvl < 40: return "Командор"
    if lvl < 60: return "Адмирал"
    if lvl < 100: return "Владыка"
    return "АРХИТЕКТОР ВСЕЛЕННОЙ"

# ===================== [ ГЕНЕРАТОР ИНТЕРФЕЙСА ] =====================
def main_kb(uid):
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 НЕЙРО-СИНТЕЗ (ИГРАТЬ)", callback_data="game_go"))
    b.row(types.InlineKeyboardButton(text="👤 ПРОФИЛЬ", callback_data="view_profile"),
          types.InlineKeyboardButton(text="🛸 ВЕРФЬ (МАГАЗИН)", callback_data="open_shop_0"))
    b.row(types.InlineKeyboardButton(text="🎰 КАЗИНО", callback_data="casino_menu"),
          types.InlineKeyboardButton(text="📅 ЕЖЕДНЕВНЫЙ БОНУС", callback_data="daily_bonus"))
    b.row(types.InlineKeyboardButton(text="💬 ШУТКА ШЕФА", callback_data="get_joke"),
          types.InlineKeyboardButton(text="💡 ИДЕЯ", callback_data="suggest_idea"))
    
    if int(uid) == ADMIN_ID:
        b.row(types.InlineKeyboardButton(text="🛡 АДМИН-ПАНЕЛЬ", callback_data="admin_main"))
    return b.as_markup()

# ===================== [ ЛОГИКА БОТА ] =====================
@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id); data = load_data()
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000, 
            "xp": 0, 
            "ship": "shuttle", 
            "inventory": ["shuttle"], 
            "last_bonus": 0
        }
        save_data(data)
    
    name = msg.from_user.first_name.upper()
    text = (
        f"<code>{HEADER_FRAME}</code>\n"
        f"🚀 <b>СИСТЕМА ИДЕНТИФИЦИРОВАНА: {name}</b>\n"
        f"{DIVIDER}\n"
        f"Добро пожаловать на борт 'Межгалактического Ковчега'.\n"
        f"Ваша миссия: Развитие от пыли до Абсолюта.\n\n"
        f"🖥 <b>СТАТУС СИСТЕМ:</b>\n"
        f"├ Двигатели: 100%\n"
        f"├ Щиты: АКТИВНЫ\n"
        f"└ Нейросеть: ГОТОВА\n"
        f"{DIVIDER}\n"
        f"<i>Выберите директиву ниже:</i>"
    )
    await msg.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))

@dp.callback_query(F.data == "view_profile")
async def profile(call: types.CallbackQuery):
    data = load_data(); u = data["players"].get(str(call.from_user.id))
    lvl = int(u['xp']**0.5 // 2) + 1
    rank = get_rank(lvl)
    ship_name = SHIPS[u['ship']]['name']
    mult = SHIPS[u['ship']]['mult']
    
    bar = progress_bar(u['xp'] % 100, 100, 12)
    
    text = (
        f"<code>{HEADER_FRAME}</code>\n"
        f"👤 <b>ЛИЧНОЕ ДЕЛО: {call.from_user.first_name.upper()}</b>\n"
        f"{DIVIDER}\n"
        f"🎖 <b>Звание:</b> {rank} (Lvl {lvl})\n"
        f"<code>[{bar}]</code>\n"
        f"💰 <b>Баланс:</b> <code>{u['money']:,}</code> CR\n"
        f"🛸 <b>Флагман:</b> {ship_name}\n"
        f"⚡️ <b>Мощность:</b> x{mult}\n"
        f"{DIVIDER}\n"
        f"<i>Системы функционируют нормально.</i>\n"
        f"<code>{FOOTER_FRAME}</code>"
    )
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=main_kb(call.from_user.id))

@dp.callback_query(F.data == "game_go")
async def game_go(call: types.CallbackQuery):
    phrase = random.choice(PHRASES)
    global_tasks[call.from_user.id] = {"text": phrase}
    
    # Имитация загрузки нейросети
    loading_frames = [
        "🔄 <b>ПОИСК СИГНАЛА...</b>",
        "📶 <b>СИГНАЛ НАЙДЕН...</b>",
        "📂 <b>ДЕШИФРОВКА...</b>"
    ]
    
    await call.message.edit_text(loading_frames[0], parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.5) # Маленькая задержка для эффекта
    
    text = (
        f"<code>{HEADER_FRAME}</code>\n"
        f"🌀 <b>НЕЙРО-СИНТЕЗ РЕАЛЬНОСТИ</b>\n"
        f"{DIVIDER}\n"
        f"📜 <b>ЗАДАНИЕ:</b>\n"
        f"<code>{phrase}</code>\n\n"
        f"⌨️ <i>Введите этот код для синхронизации!</i>\n"
        f"<code>{FOOTER_FRAME}</code>"
    )
    await call.message.edit_text(text, parse_mode=ParseMode.HTML)

@dp.message()
async def message_handler(msg: types.Message):
    uid = str(msg.from_user.id); data = load_data()
    if uid not in data["players"]: return

    # Проверка игры
    if int(uid) in global_tasks and msg.text == global_tasks[int(uid)]["text"]:
        ship = SHIPS[data["players"][uid]['ship']]
        base_reward = random.randint(100, 300)
        final_reward = int(base_reward * ship['mult'])
        xp_gain = random.randint(15, 40)
        
        data["players"][uid]['money'] += final_reward
        data["players"][uid]['xp'] += xp_gain
        save_data(data)
        del global_tasks[int(uid)]
        
        await msg.answer(
            f"✅ <b>СИНХРОНИЗАЦИЯ УСПЕШНА!</b>\n"
            f"💰 Получено: <code>{final_reward}</code> CR\n"
            f"🔋 Опыт: +{xp_gain} XP",
            parse_mode=ParseMode.HTML,
            reply_markup=main_kb(uid)
        )
        return

    # Шутки по команде
    if msg.text and msg.text.lower() in ["хочу", "шутка", "анекдот"]:
        await msg.answer(f"🤡 <b>АНЕКДОТ:</b>\n\n{random.choice(JOKES)}", parse_mode=ParseMode.HTML)
        return

    # Идеи
    if msg.text and msg.text.lower().startswith("идея"):
        idea = msg.text[5:].strip()
        data["suggestions"].append({"user": msg.from_user.full_name, "text": idea})
        save_data(data)
        await msg.answer("💾 <b>ИДЕЯ ЗАПИСАНА В БЛОКИ ПАМЯТИ!</b>")

@dp.callback_query(F.data.startswith("open_shop_"))
async def shop(call: types.CallbackQuery):
    page = int(call.data.split("_")[2])
    data = load_data(); uid = str(call.from_user.id)
    u_xp = data["players"][uid]['xp']
    lvl = int(u_xp**0.5 // 2) + 1
    
    items_per_page = 5
    all_ships = list(SHIPS.values())
    start = page * items_per_page
    end = start + items_per_page
    current_page = all_ships[start:end]
    
    b = InlineKeyboardBuilder()
    
    text = f"<code>{HEADER_FRAME}</code>\n🛠 <b>ГАЛАКТИЧЕСКАЯ ВЕРФЬ (Стр. {page+1})</b>\n{DIVIDER}\n"
    
    for ship in current_page:
        ship_key = [k for k, v in SHIPS.items() if v == ship][0]
        owned = ship_key in data["players"][uid]["inventory"]
        can_buy = lvl >= ship['lvl']
        
        status_icon = "✅" if owned else ("🔓" if can_buy else "🔒")
        price_txt = "КУПЛЕНО" if owned else f"{ship['price']:,} CR"
        
        text += (
            f"{status_icon} <b>{ship['name']}</b>\n"
            f"├ Ранг: {ship['lvl']} | Мультипликатор: x{ship['mult']}\n"
            f"├ <i>{ship['desc']}</i>\n"
            f"└ Цена: <code>{price_txt}</code>\n\n"
        )
        
        if not owned and can_buy:
             b.row(types.InlineKeyboardButton(text=f"💳 КУПИТЬ: {ship['name']}", callback_data=f"buy_{ship_key}"))
        elif owned and data["players"][uid]['ship'] != ship_key:
             b.row(types.InlineKeyboardButton(text=f"🚀 ОБОРУДОВАТЬ: {ship['name']}", callback_data=f"equip_{ship_key}"))

    # Навигация
    nav_row = []
    if page > 0: nav_row.append(types.InlineKeyboardButton(text="⬅️", callback_data=f"open_shop_{page-1}"))
    nav_row.append(types.InlineKeyboardButton(text="↩️ МЕНЮ", callback_data="back_main"))
    if end < len(all_ships): nav_row.append(types.InlineKeyboardButton(text="➡️", callback_data=f"open_shop_{page+1}"))
    b.row(*nav_row)
    
    await call.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_ship(call: types.CallbackQuery):
    s_key = call.data.split("_")[1]
    uid = str(call.from_user.id); data = load_data()
    price = SHIPS[s_key]['price']
    
    if data["players"][uid]['money'] >= price:
        data["players"][uid]['money'] -= price
        data["players"][uid]['inventory'].append(s_key)
        data["players"][uid]['ship'] = s_key # Сразу надеваем
        save_data(data)
        await call.answer("✅ Успешная покупка! Корабль готов к вылету.", show_alert=True)
        await shop(call) # Обновляем магазин
    else:
        await call.answer("❌ Недостаточно кредитов!", show_alert=True)

@dp.callback_query(F.data.startswith("equip_"))
async def equip_ship(call: types.CallbackQuery):
    s_key = call.data.split("_")[1]
    uid = str(call.from_user.id); data = load_data()
    data["players"][uid]['ship'] = s_key
    save_data(data)
    await call.answer(f"🚀 Вы пересeли на {SHIPS[s_key]['name']}", show_alert=True)
    await shop(call)

@dp.callback_query(F.data == "get_joke")
async def joke_btn(call: types.CallbackQuery):
    await call.message.answer(f"💬 <b>ШУТКА ВЛАДЕЛЬЦА:</b>\n{DIVIDER}\n{random.choice(JOKES)}")
    await call.answer()

@dp.callback_query(F.data == "daily_bonus")
async def daily(call: types.CallbackQuery):
    uid = str(call.from_user.id); data = load_data()
    now = time.time()
    last = data["players"][uid].get("last_bonus", 0)
    
    if now - last > 86400: # 24 часа
        bonus = random.randint(5000, 25000)
        data["players"][uid]["money"] += bonus
        data["players"][uid]["last_bonus"] = now
        save_data(data)
        await call.message.answer(f"🎁 <b>ЕЖЕДНЕВНАЯ ПОСТАВКА:</b>\nВы получили контейнер с {bonus} CR!")
        await call.answer()
    else:
        wait = int((86400 - (now - last)) / 3600)
        await call.answer(f"⏳ Груз еще в пути! Ждать {wait} ч.", show_alert=True)

@dp.callback_query(F.data == "casino_menu")
async def casino(call: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🎲 БРОСОК КУБИКА (500 CR)", callback_data="play_dice"))
    b.row(types.InlineKeyboardButton(text="🎰 СЛОТЫ (1000 CR)", callback_data="play_slots"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"🎰 <b>ОРБИТАЛЬНОЕ КАЗИНО</b>\n{DIVIDER}\nИспытай удачу, пилот!", parse_mode=ParseMode.HTML, reply_markup=b.as_markup())

@dp.callback_query(F.data == "play_dice")
async def play_dice(call: types.CallbackQuery):
    uid = str(call.from_user.id); data = load_data()
    if data["players"][uid]['money'] < 500: return await call.answer("❌ Нет денег!", show_alert=True)
    
    data["players"][uid]['money'] -= 500
    msg = await call.message.answer_dice(emoji="🎲")
    await asyncio.sleep(4)
    score = msg.dice.value
    
    if score > 3:
        win = 500 * 2
        data["players"][uid]['money'] += win
        res = f"🟢 <b>ПОБЕДА!</b> Выпало {score}. Выигрыш: {win}"
    else:
        res = f"🔴 <b>ПОРАЖЕНИЕ.</b> Выпало {score}."
        
    save_data(data)
    await call.message.answer(res, parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "play_slots")
async def play_slots(call: types.CallbackQuery):
    uid = str(call.from_user.id); data = load_data()
    if data["players"][uid]['money'] < 1000: return await call.answer("❌ Нет денег!", show_alert=True)
    
    data["players"][uid]['money'] -= 1000
    msg = await call.message.answer_dice(emoji="🎰")
    await asyncio.sleep(2)
    val = msg.dice.value # Значения для слотов сложные, упростим:
    # 64 - джекпот (три семерки) в Telegram API, но это редкость.
    # Просто дадим рандомный бонус если значение высокое.
    
    if val in [1, 22, 43, 64]: # Условные выигрышные комбинации
        win = 10000
        data["players"][uid]['money'] += win
        await call.message.answer(f"🎰 <b>ДЖЕКПОТ!!!</b> +{win} CR", parse_mode=ParseMode.HTML)
    elif val > 30:
        win = 2000
        data["players"][uid]['money'] += win
        await call.message.answer(f"🟢 <b>Хорошая линия!</b> +{win} CR", parse_mode=ParseMode.HTML)
    else:
        await call.message.answer("🔴 <b>Пусто...</b> Попробуй еще.", parse_mode=ParseMode.HTML)
    save_data(data)

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await start(call.message)

@dp.callback_query(F.data == "admin_main")
async def admin(call: types.CallbackQuery):
    data = load_data()
    ideas = "\n".join([f"- {i['user']}: {i['text']}" for i in data['suggestions'][-5:]])
    await call.message.edit_text(f"🛡 <b>АДМИН-ЦЕНТР</b>\n{DIVIDER}\nИгроков: {len(data['players'])}\n\n<b>Последние идеи:</b>\n{ideas}", parse_mode=ParseMode.HTML, reply_markup=main_kb(call.from_user.id))

@dp.message(Command("gift"))
async def gift(msg: types.Message):
    if msg.from_user.id != ADMIN_ID: return
    try:
        _, uid, amt = msg.text.split()
        data = load_data()
        data["players"][uid]["money"] += int(amt)
        save_data(data)
        await msg.answer("✅ Выдано.")
    except: pass

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
