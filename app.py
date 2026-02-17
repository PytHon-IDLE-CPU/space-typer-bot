import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- КОНФИГ ---
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен бота не задан в переменной окружения BOT_TOKEN")

# Безопасное получение ADMIN_ID с заглушкой
ADMIN_ID_STR = os.getenv("ADMIN_ID")
if ADMIN_ID_STR:
    ADMIN_ID = int(ADMIN_ID_STR)
else:
    ADMIN_ID = None  # Заглушка: если ADMIN_ID не задан, функционал админа будет недоступен

DB_PATH = "cs2_arena_db.json"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- FSM-СОСТОЯНИЯ ---
class PlayerState(StatesGroup):
    choosing_training_location = State()
    opening_case = State()
    confirming_transfer = State()
    selecting_tactic = State()

# --- БАЗА ДАННЫХ: ЗАГРУЗКА/СОХРАНЕНИЕ ---
def load_db():
    """Загружает БД из JSON-файла. Если файла нет — создаёт дефолтную.
    Обрабатывает ошибки JSON."""
    if not os.path.exists(DB_PATH):
        default_db = {},
            "users": {},
            "market": [],
            "tournaments": [],
"cases": {
    "OperationPhoenix": {
        "chance": 0.05,
        "items": [
            "AWP | Dragon Lore",
            "M4A4 | Howl",
            "Desert Eagle | Blaze",
            "Кредиты (500)",
            "Редкий игрок (AWPer)"
        ]
    },
    "LegacyCase": {
        "chance": 0.06,
        "items": [
            "AK-47 | Vulcan",
            "Glock-18 | Candy Apple",
            "USP-S | Orion",
            "Кредиты (300)",
            "Игрок (Rifle)"
        ]
    },
    "Tournament2026": {
        "chance": 0.03,
        "items": [
            "M4A1-S | Player's",
            "AWP | Fever Dream",
            "Five-SeveN | Hybrid",
            "Кредиты (1000)",
            "Легендарный игрок"
        ]
    },
    "MysteryBox": {
        "chance": 0.02,
        "items": [
            "Случайный скин (любой редкость)",
            "Случайный игрок (любая роль)",
            "Кредиты (200–1000)",
            "Эксклюзивный скин",
            "Секретный предмет"
        ]
    },
    "WeaponExpert": {
        "chance": 0.07,
        "items": [
            "AK-47 | Safety Net",
            "M4A4 | Neo-Noir",
            "P250 | Supervillain",
            "Кредиты (400)",
            "Игрок (Support)"
        ]
    },
    "TeamSpirit": {
        "chance": 0.04,
        "items": [
            "Эмблема команды (анимированная)",
            "Граффити 'GO!'",
            "Наклейка 'Champion'",
            "Кредиты (600)",
            "Игрок (IGL)"
        ]
    },
    "GoldenAge": {
        "chance": 0.01,
        "items": [
            "AWP | Gold Arabesque",
            "AK-47 | Gold Arabesque",
            "Karambit | Gold",
            "Кредиты (1500)",
            "Золотой скин (уникальный)"
        ]
    },
    "Cyberpunk": {
        "chance": 0.045,
        "items": [
            "MP9 | Hot Rod",
            "SG 553 | Danger Close",
            "Tec-9 | Red Quartz",
            "Кредиты (500)",
            "Скины с неоновой подсветкой"
        ]
    },
    "ClassicCollection": {
        "chance": 0.08,
        "items": [
            "AK-47 | Cartel",
            "M4A4 | Desert-Strike",
            "P2000 | Urban Hazard",
            "Кредиты (250)",
            "Игрок (Entry Fragger)"
        ]
    },
    "CommunityChoice": {
        "chance": 0.035,
        "items": [
            "Скины от фанатов (топ-10)",
            "Граффити с автографом",
            "Наклейки (редкие)",
            "Кредиты (700)",
            "Специальный игрок"
        ]
    },
    "LimitedEdition": {
        "chance": 0.005,
        "items": [
            "AWP | Asiimov (редкий)",
            "M4A4 | The Emperor",
            "Bayonet | Doppler",
            "Кредиты (2000)",
            "Эксклюзивы (выходят из продажи)"
        ]
    },
    "LuckyDraw": {
        "chance": 0.015,
        "items": [
            "Шанс на Legendary Case",
            "Кредиты (100–800)",
            "Случайный редкий скин",
            "Игрок (случайная роль)",
            "Бонус к ELO (+50)"
        ]
    },
    "RetroLegends": {
        "chance": 0.025,
        "items": [
            "AK-47 | Fire Serpent (CS 1.6)",
            "M4A1 | Vulcan (CS 1.6)",
            "Deagle | Blaze (CS 1.6)",
            "Кредиты (800)",
            "Ретро‑игрок"
        ]
    },
    "NeonNights": {
        "chance": 0.04,
        "items": [
            "UMP-45 | Neon Cutter",
            "P90 | Trigon",
            "Dual Berettas | Cobra Strike",
            "Кредиты (600)",
            "Светящиеся скины"
        ]
    },
    "MilitaryGrade": {
        "chance": 0.065,
        "items": [
            "AK-47 | Point Disarray",
            "M4A1-S | Mecha Industries",
            "SCAR-20 | Cyrex",
            "Кредиты (450)",
            "Игрок (Defender)"
        ]
    },
    "AnimeEdition": {
        "chance": 0.02,
        "items": [
            "AWP | Atheris",
            "Galil AR | Cerberus",
            "MAC-10 | Neon Rider",
            "Кредиты (900)",
            "Аниме‑скин (анимированный)"
        ]
    },
    "HalloweenSpecial": {
        "chance": 0.01,  # Только в октябре
        "items": [
            "M4A4 | Nightmare",
            "Sawed-Off | Wasteland Princess",
            "Sticker 'Pumpkin'",
            "Кредиты (1200)",
            "Сезонный скин"
        ]
    },
    "WinterWonderland": {
        "chance": 0.01,  # Только в декабре
        "items": [
            "AK-47 | Ice Coaled",
            "G3SG1 | Polar Camo",
            "Sticker 'Snowman'",
            "Кредиты (1100)",
            "Зимний скин"
        ]
    },
    "StreetArt": {
        "chance": 0.03,
        "items": [
            "UMP-45 | Blaze",
            "P250 | Contempt",
            "Nova | Bloomstick",
            "Кредиты (700)",
            "Граффити‑скин"
        ]
    },
    "CyberMutants": {
        "chance": 0.008,
        "items": [
            "AUG | Stymphalian",
            "SSG 08 | Dragonfire",
            "Tec-9 | Fuel Injector",
            "Кредиты (1300)",
            "Био‑скин (мутант)"
        ]
    }
}
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=2)
        return default_db

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка чтения JSON-базы: {e}")
        # Создаём новую БД при ошибке
        default_db = {"users": {}, "market": [], "tournaments": [], "cases": {}}
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=2)
        return default_db

def save_db(db):
    """Сохраняет БД в JSON-файл."""
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения БД: {e}")

# --- ФУНКЦИЯ ПОЛУЧЕНИЯ ПОЛЬЗОВАТЕЛЯ ---
def get_user(user_id: int) -> dict:
    """Возвращает словарь с данными пользователя из БД. Если пользователя нет — возвращает None."""
    db = load_db()
    return db["users"].get(str(user_id))

def create_user(user_id: int, team_name: str) -> dict:
    """Создаёт нового пользователя в БД и возвращает его данные.
    Валидирует имя команды."""
    # Валидация имени команды
    if not team_name or len(team_name.strip()) == 0:
        team_name = "Без названия"
    elif len(team_name) > 30:
        team_name = team_name[:30]  # Ограничение длины

    team_name = team_name.strip()

    db = load_db()

    # Стартовые игроки
    starter_players = [
        {
            "name": "Алекс",
            "role": "Rifle",
            "rarity": "Неопытный",
            "stats": {"aim": 50, "reaction": 50, "tactics": 50, "stamina": 50, "leadership": 0},
            "contract": {"salary": 1000, "duration": 52, "bonus_per_win": 200},
            "morale": 75,
            "injury": False,
            "special_trait": None,
            "quests": [],
            "skin": "Стандартный"
        },
        {
            "name": "Мария",
            "role": "AWPer",
            "rarity": "Неопытный",
            "stats": {"aim": 50, "reaction": 50, "tactics": 50, "stamina": 50, "leadership": 0},
            "contract": {"salary": 1000, "duration": 52, "bonus_per_win": 200},
            "morale": 75,
            "injury": False,
            "special_trait": None,
            "quests": [],
            "skin": "Стандартный"
        },
        {
            "name": "Иван",
            "role": "Entry Fragger",
            "rarity": "Неопытный",
            "stats": {"aim": 50, "reaction": 50, "tactics": 50, "stamina": 50, "leadership": 0},
            "contract": {"salary": 1000, "duration": 52, "bonus_per_win": 200},
            "morale": 75,
            "injury": False,
            "special_trait": None,
            "quests": [],
            "skin": "Стандартный"
        }
    ]

    team = {
        "user_id": user_id,
        "team_name": team_name,
        "players": starter_players,
        "balance": 10000,
        "reputation": 0,
        "win_streak": 0,
        "lose_streak": 0,
        "sponsor": None,
        "training_location": "Подвал",
        "elo": 1000,
        "daily_login_streak": 0,
        "inventory": {  # Словарь с разделами
            "skins": [],     # Список скинов оружия
            "cases": [],    # Список кейсов
            "other": []     # Прочие предметы (граффити, наклейки и т.п.)
        },
        "tournament_points": 0,
        "cooldowns": {     # Таймеры для действий
            "match": None,        # Время следующего матча
            "training": None,      # Время окончания тренировки
            "case_opening": None  # Время открытия кейса
        }
    }

    db["users"][str(user_id)] = team
    save_db(db)

    # Логирование нового игрока
    logger.info(f"Зарегистрирован новый пользователь: ID={user_id}, команда='{team_name}'")
    print(f"[INFO] Новый пользователь: ID={user_id}, команда='{team_name}'")

    return team

# --- ОБРАБОТЧИК /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user:
        team_name = message.from_user.first_name or "Без названия"
        user = create_user(user_id, team_name)

        await message.answer(
            f"Добро пожаловать в CS2 Arena Manager!\n\n"
            f"Ваша команда: *{user['team_name']}* создана.\n"
            f"Стартовые игроки добавлены.\n\n"
            f"Используйте /menu, чтобы открыть главное меню.",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "Вы уже зарегистрированы! Используйте /menu.",
            parse_mode="Markdown"
        )

# --- ЗАПУСК БОТА ---
async def main():
    logger.info("Бот запущен. Ожидание сообщений...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.markdown import hbold, hitalic

# --- ШКАЛА РАНГОВ ПО ELO (без изменений) ---
def get_rank_by_elo(elo: int) -> dict:
    ranks = [
        {"min": 0, "max": 999, "name": "Новенький", "icon": "🥉", "color": "gray"},
        {"min": 1000, "max": 1299, "name": "Бронза I", "icon": "🥉", "color": "brown"},
        {"min": 1300, "max": 1599, "name": "Бронза II", "icon": "🥉", "color": "brown"},
        {"min": 1600, "max": 1899, "name": "Серебро I", "icon": "🥈", "color": "silver"},
        {"min": 1900, "max": 2199, "name": "Серебро II", "icon": "🥈", "color": "silver"},
        {"min": 2200, "max": 2499, "name": "Золото I", "icon": "🥇", "color": "gold"},
        {"min": 2500, "max": 2799, "name": "Золото II", "icon": "🥇", "color": "gold"},
        {"min": 2800, "max": 3099, "name": "Платина I", "icon": "💎", "color": "blue"},
        {"min": 3100, "max": 3399, "name": "Платина II", "icon": "💎", "color": "blue"},
        {"min": 3400, "max": 3699, "name": "Алмаз", "icon": "✨", "color": "cyan"},
        {"min": 3700, "max": 9999, "name": "Легенда", "icon": "🏆", "color": "purple"}
    ]
    for rank in ranks:
        if rank["min"] <= elo <= rank["max"]:
            return rank
    return ranks[-1]

# --- ИНЛАЙН‑КЛАВИАТУРЫ (единый стиль) ---
def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Профиль команды", callback_data="show_profile")],
        [InlineKeyboardButton(text="🏋️ Тренировки & Локации", callback_data="training_menu")],
        [InlineKeyboardButton(text="🎮 Матчи & Турниры", callback_data="matches_menu")],
        [InlineKeyboardButton(text="🎁 Кейсы & Инвентарь", callback_data="cases_menu")],
        [InlineKeyboardButton(text="⚙️ Настройки & Спонсоры", callback_data="settings_menu")]
    ])
    return keyboard

def get_profile_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_profile"),
            InlineKeyboardButton(text="👥 Состав", callback_data="team_roster")
        ],
        [
            InlineKeyboardButton(text="💼 Инвентарь", callback_data="inventory"),
            InlineKeyboardButton(text="🏆 Ранги", callback_data="show_ranks")
        ]
    ])
    return keyboard

# --- ОБРАБОТЧИК /menu ---
@dp.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы! Используйте /start.")
        return

    await message.answer(
        hbold("Главное меню CS2 Arena Manager") + "\n\n"
        "Выберите раздел ниже 👇",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

# --- ОБРАБОТЧИК ПРОФИЛЯ ---
@dp.callback_query(F.data == "show_profile")
async def show_profile(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден.")
        return

    # Расчёт средних статов
    total_stats = {"aim": 0, "reaction": 0, "tactics": 0, "stamina": 0}
    for player in user["players"]:
        for stat, value in player["stats"].items():
            if stat in total_stats:
                total_stats[stat] += value
    avg_stats = {k: v // len(user["players"]) for k, v in total_stats.items()}


    # Индикатор морали (5 сегментов)
    morale_percent = user["morale"]
    morale_bars = "🟩" * (morale_percent // 20)  # Полные сегменты
    if morale_percent % 20 > 0 and len(morale_bars) < 5:
        morale_bars += "🟨!  # Частичный сегмент
    morale_bars = morale_bars.ljust(5, "⬜️")  # Дополнить пустыми

    # Ранг и иконка
    rank = get_rank_by_elo(user["elo"])
    rank_line = f"{rank['icon']} <b>{rank['name']}</b> ({user['elo']} ELO)"

    # Формирование профиля
    profile_text = (
        f"<b>🏛️ {user['team_name']}</b>\n"
        f"{rank_line}\n"
        f"────────────────────\n"
        f"<i>Баланс:</i> <b>{user['balance']}</b> кредитов\n"
        f"<i>Репутация:</i> <b>{user['reputation']}/100</b>\n"
        f"<i>Стрик побед:</i> <code>{user['win_streak']}</code>\n"
        f"<i>Локация:</i> {user['training_location']}\n\n"

        f"<u>Средняя статистика команды:</u>\n"
        f!🎯 <b>Aim:</b> {avg_stats['aim']}\n"
        f!⚡ <b>Reaction:</b> {avg_stats['reaction']}\n"
        f!🧠 <b>Tactics:</b> {avg_stats['tactics']}\n"
        f!💪 <b>Stamina:</b> {avg_stats['stamina']}\n\n"

        f"<i>Мораль:</i>\n{morale_bars} <code>({morale_percent}%)</code>\n\n"

        f"<code>• • • • • • • • • • •</code>\n"
        f"<i>Очки турниров:</i> <b>{user['tournament_points']}</b>"
    )

    await callback.message.edit_text(
        text=profile_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- CALLBACK-ОБРАБОТЧИКИ (исправлены все ссылки на user["players"]) ---
@dp.callback_query(F.data == "refresh_profile")
async def refresh_profile(callback: types.CallbackQuery):
    await show_profile(callback)  # Переиспользуем основную функцию

@dp.callback_query(F.data == "team_roster")
async def show_team_roster(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден.")
        return

    roster_text = f"<b>👥 Состав команды: {user['team_name']}</b>\n\n"
    for i, player in enumerate(user["players"], 1):
        rarity_icon = "🔶! if player["rarity"] == "Неопытный! else \
                     "🔷! if player["rarity"] == "Опытный! else \
                    "⭐! if player["rarity"] == "Звезда! else "✨"


        roster_text += (
            f"<b>{i}.</b> {rarity_icon} <i>{player['name']}</i> "
            f"(<code>{player['role']}</code>)\n"
            f!   📈 <b>Aim:</b> {player['stats']['aim']}, "
            f"<b>Reaction:</b> {player['stats']['reaction']}\n"
            f!   🧠 <b>Tactics:</b> {player['stats']['tactics']}, "
            f"<b>Stamina:</b> {player['stats']['stamina']}\n"
            f!   ❤️ <b>Мораль:</b> {player['morale']}%\n"
            f!   🛡️ <b>Скин:</b> {player['skin']}\n\n"
        )


    await callback.message.edit_text(
        text=roster_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@dp.callback_query(F.data == "inventory")
async def show_inventory(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден.")
        return

    inv = user["inventory"]
    inv_text = "<b>💼 Инвентарь</b>\n\n"

    if inv["skins"]:
        inv_text += "<u>Скины оружия:</u>\n"
        for skin in inv["skins"]:
            inv_text += f!   - 🔫 {skin}\n"
        inv_text += "\n"
    else:
        inv_text += "<i>Скины отсутствуют</i>\n\n"

    if inv["cases"]:
        inv_text += "<u>Кейсы:</u>\n"
        for case in inv["cases"]:
            inv_text += f!   - 🎁 {case}\n"
        inv_text += "\n"
    else:
        inv_text += "<i>Кейсы отсутствуют</i>\n\n"


    if inv["other"]:
        inv_text += "<u>Прочее:</u>\n"
        for item in inv["other"]:
            inv_text += f!   - ➕ {item}\n"
    else:
        inv_text += "<i>Прочие предметы отсутствуют</i>"

    await callback.message.edit_text(
        text=inv_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@dp.callback_query(F.data == "show_ranks")
async def show_ranks(callback: types.CallbackQuery):
    ranks = [
        {"min": 0, "max": 999, "name": "Новенький", "icon": "🥉"},
        {"min": 1000, "max": 1299, "name": "Бронза I", "icon": "🥉"},
        {"min": 1300, "max": 1599, "name": "Бронза II", "icon": "🥉"},
        {"min": 1600, "max": 1899, "name": "Серебро I", "icon": "🥈"},
        {"min": 1900, "max": 2199, "name": "Серебро II", "icon": "🥈"},
        {"min": 2200, "max": 2499, "name": "Золото I", "icon": "🥇"},
        {"min": 2500, "max": 2799, "name": "Золото II", "icon": "🥇"},
        {"min": 2800, "max": 3099, "name": "Платина I", "icon": "💎"},
        {"min": 3100, "max": 3399, "name": "Платина II", "icon": "💎"},
        {"min": 3400, "max": 3699, "name": "Алмаз", "icon": "✨"},
        {"min": 3700, "max": 9999, "name": "Легенда", "icon": "🏆"}
    ]


    rank_text = "<b>🏆 Шкала рангов</b>\n\n"
    for rank in ranks:
        rank_text += (
            f"{rank['icon']} <b>{rank['name']}</b> "
            f"(<code>{rank['min']}–{rank['max']} ELO</code>)\n"
        )

    current_rank = get_rank_by_elo(user["elo"])
    rank_text += (
        "\n<i>Ваш текущий ранг:</i>\n"
        f"{current_rank['icon']} <b>{current_rank['name']}</b> "
        f"({user['elo']} ELO)"
    )

    await callback.message.edit_text(
        text=rank_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()



