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
        default_db = {
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
    

