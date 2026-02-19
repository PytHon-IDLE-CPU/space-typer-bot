# app.py

import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- ИМПОРТЫ И КОНФИГ ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на реальный токен
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ ---
DATABASE_FILE = "arena_data.json"

def load_db():
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Инициализируем базу с пустой структурой
        initial_data = {"users": {}}
        save_db(initial_data)
        return initial_data

def save_db(data):
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- FSM ---
class Registration(StatesGroup):
    waiting_for_team_name = State()

# --- КЛАВИАТУРЫ ---
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="Моя Команда 👨‍🏫"), KeyboardButton(text="Трансферный Рынок 📈")],
        [KeyboardButton(text="Матчи ⚔️"), KeyboardButton(text="Турниры 🏅")],
        [KeyboardButton(text="Букмекер 💰"), KeyboardButton(text="Статистика 📊")],
        [KeyboardButton(text="Настройки ⚙️")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    db = load_db()
    
    if user_id not in db["users"]:
        # Создаём профиль нового пользователя
        db["users"][user_id] = {
            "balance": 5000,
            "elo": 1000,
            "energy": 100,
            "reputation": 50,
            "sponsor": None,
            "team_name": None,
            "players": [
                {
                    "name": "RushMaster",
            "role": "Entry",
            "stats": {"Aim": 75, "Tactics": 60},
            "stamina": 100,
            "morale": 100
                },
                {
            "name": "HeadshotKing",
            "role": "AWPer",
            "stats": {"Aim": 90, "Tactics": 50},
            "stamina": 100,
            "morale": 100
        },
        {
            "name": "Tactician",
            "role": "IGL",
            "stats": {"Aim": 65, "Tactics": 85},
            "stamina": 100,
            "morale": 100
        },
        {
            "name": "SupportGuy",
            "role": "Support",
            "stats": {"Aim": 60, "Tactics": 70},
            "stamina": 100,
            "morale": 100
        },
        {
            "name": "RiflerPro",
            "role": "Rifler",
            "stats": {"Aim": 80, "Tactics": 65},
            "stamina": 100,
            "morale": 100
        }
            ]
        }
        save_db(db)
        await message.answer(
            "Добро пожаловать в CS2 Arena Manager!\n\n"
            "Для начала создайте название для вашей команды:"
        )
        await state.set_state(Registration.waiting_for_team_name)
    else:
        team_name = db["users"][user_id]["team_name"] or "Без названия"
        await message.answer(
            f"Добро пожаловать обратно, менеджер!\n"
            f"Ваша команда: {team_name}\n"
            f"Баланс: {db['users'][user_id]['balance']} АК\n"
            f"Рейтинг ELO: {db['users'][user_id]['elo']}",
            reply_markup=get_main_menu_keyboard()
        )

@dp.message(Registration.waiting_for_team_name)
async def process_team_name(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    team_name = message.text.strip()
    
    db = load_db()
    db["users"][user_id]["team_name"] = team_name
    save_db(db)
    
    await message.answer(
        f"Отлично! Ваша команда '{team_name}' успешно создана.\n"
        f"Теперь вы можете управлять составом, участвовать в матчах и турнирах!",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

# --- ЗАПУСК БОТА ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
