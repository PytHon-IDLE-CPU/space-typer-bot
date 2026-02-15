import asyncio
import random
import json
import os
import logging
import math
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ===================== [ КОНФИГУРАЦИЯ ] =====================
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 5056869104
DB_PATH = "omega_universe_v6.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

global_tasks = {}

HEADER = "<b>🧬 ╔═══════ [ OMEGA-SYSTEM ] ═══════╗</b>"
FOOTER = "<b>🧬 ╚═══════════════════════════════╝</b>"
SEP = "<b><pre>───────────────────────────────</pre></b>"

# ===================== [ ПОЛНЫЕ ДАННЫЕ (БЕЗ СОКРАЩЕНИЙ) ] =====================

SHIPS = {
    "shuttle":      {"name": "🛸 'Бродяга'",           "price": 0,           "mult": 1.0,      "lvl": 1},
    "scout":        {"name": "📡 'Разведчик С-12'",    "price": 500,           "mult": 1.5,      "lvl": 2},
    "interceptor":  {"name": "⚡️ 'Стриж'",             "price": 2000,          "mult": 2.2,      "lvl": 3},
    "drone_eye":    {"name": "👁 'Око Саурона'",        "price": 7500,          "mult": 3.8,      "lvl": 4},
    "hauler":       {"name": "🚜 'Косм. Бык'",          "price": 18000,         "mult": 5.5,      "lvl": 5},
    "fighter":      {"name": "⚔️ 'Валькирия'",        "price": 45000,         "mult": 11.0,     "lvl": 7},
    "bomber":       {"name": "💣 'Сверхновая'",         "price": 120000,        "mult": 20.0,     "lvl": 9},
    "corvette":     {"name": "🛡 'Бастион'",           "price": 300000,        "mult": 35.0,     "lvl": 11},
    "frigate":      {"name": "🔱 'Посейдон'",          "price": 850000,        "mult": 60.0,     "lvl": 13},
    "destroyer":    {"name": "🔥 'Гнев'",                "price": 1900000,       "mult": 130.0,    "lvl": 16},
    "cruiser":      {"name": "🛰 'Титан'",              "price": 5000000,       "mult": 320.0,    "lvl": 20},
    "carrier":      {"name": "🦅 'Фенрир'",              "price": 15000000,      "mult": 800.0,    "lvl": 25},
    "battleship":   {"name": "👑 'Император'",         "price": 35000000,      "mult": 1900.0,   "lvl": 30},
    "dreadnought":  {"name": "💀 'Бездна'",            "price": 100000000,     "mult": 5500.0,   "lvl": 38},
    "reaper":       {"name": "🩸 'Жнец'",                "price": 350000000,     "mult": 16000.0,  "lvl": 45},
    "nebula":       {"name": "🌌 'Скиталец'",            "price": 900000000,     "mult": 55000.0,  "lvl": 55},
    "kronos":       {"name": "⌛️ 'Кронос'",            "price": 3000000000,    "mult": 165000.0, "lvl": 70},
    "star_eater":   {"name": "🌑 'Пожиратель'",          "price": 15000000000,   "mult": 650000.0, "lvl": 85},
    "void_walker":  {"name": "👻 'Ходок'",              "price": 75000000000,   "mult": 2200000.0,"lvl": 100},
    "infinity":     {"name": "♾ 'Бесконечность'",      "price": 300000000000,  "mult": 11000000.0,"lvl": 120},
    "creator":      {"name": "✨ 'ТВОРЕЦ'",            "price": 777777777777,  "mult": 60000000.0,"lvl": 150}
}

CASES = {
    "free":  {"n": "🎁 БЕСПЛАТНЫЙ", "p": 0, "drop": {"money": (500, 2000), "xp": (10, 50)}},
    "beta":  {"n": "🧪 БЕТА-КЕЙС", "p": 5000, "drop": {"money": (3000, 10000), "xp": (50, 200)}},
    "ref":   {"n": "🔗 РЕФЕРАЛЬНЫЙ", "p": 0, "drop": {"money": (15000, 40000), "xp": (200, 600)}},
    "cheap": {"n": "📦 НЕДОРОГОЙ", "p": 15000, "drop": {"money": (10000, 25000), "xp": (100, 300)}},
    "mid":   {"n": "💎 СРЕДНИЙ", "p": 100000, "drop": {"money": (80000, 250000), "xp": (500, 1500)}},
    "rich":  {"n": "💰 ДЛЯ БОГАТЫХ", "p": 1000000, "drop": {"money": (900000, 3000000), "xp": (2000, 10000)}},
    "ultra": {"n": "👑 МИЛЛИОНЕР", "p": 50000000, "drop": {"money": (45000000, 150000000), "xp": (50000, 200000)}}
}

PETS = {
    "droid": {"n": "🤖 Дроид", "price_cr": 50000, "b_money": 1.1},
    "alien_cat": {"n": "🐱 Кот Ориона", "price_cr": 250000, "b_money": 1.3},
    "dragon": {"n": "🐉 Дракон", "price_cr": 5000000, "b_money": 2.0}
}

RESOURCES = {"iron": "⛓ Железо", "crystal": "💎 Кристалл", "chip": "💾 Чип", "relic": "⚛️ Осколок Бездны"}

# ===================== [ СИСТЕМА ДАННЫХ ] =====================
def load_data():
    if not os.path.exists(DB_PATH):
        return {"players": {}, "market": [], "boss": {"hp": 1000000, "max_hp": 1000000, "active": False}}
    with open(DB_PATH, "r", encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DB_PATH, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_lvl(xp): return int(xp**0.5 // 2) + 1

# ===================== [ КЛАВИАТУРЫ ] =====================
def main_kb(uid, xp):
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🌀 СИНТЕЗ", callback_data="game_go"),
          types.InlineKeyboardButton(text="🌋 РЕЙД БОСС", callback_data="boss_menu"))
    b.row(types.InlineKeyboardButton(text="👤 ПРОФИЛЬ", callback_data="view_profile"),
          types.InlineKeyboardButton(text="🛒 ВЕРФЬ", callback_data="open_shop"))
    b.row(types.InlineKeyboardButton(text="📈 РЫНОК", callback_data="market_menu"),
          types.InlineKeyboardButton(text="⚔️ PVP", callback_data="pvp_menu"))
    b.row(types.InlineKeyboardButton(text="📦 КЕЙСЫ", callback_data="cases_menu"),
          types.InlineKeyboardButton(text="🔧 СЕРВИС", callback_data="service_menu"))
    return b.as_markup()

# ===================== [ ОБРАБОТЧИКИ ] =====================

@dp.message(Command("start"))
async def start(msg: types.Message):
    uid = str(msg.from_user.id)
    data = load_data()
    if uid not in data["players"]:
        data["players"][uid] = {
            "money": 1000, "xp": 0, "ship": "shuttle", "inventory": ["shuttle"],
            "res": {k: 0 for k in RESOURCES}, "skills": {"agg": 0, "tra": 0},
            "durability": 100, "name": msg.from_user.first_name, "pvp_wins": 0, "boss_dmg": 0
        }
        save_data(data)
    await msg.answer(f"{HEADER}\n🚀 <b>ДОБРО ПОЖАЛОВАТЬ, ПИЛОТ!</b>\n{SEP}\nИспользуйте меню для навигации по вселенной.\n{FOOTER}", parse_mode="HTML", reply_markup=main_kb(uid, data["players"][uid]["xp"]))

# --- 1. МАСШТАБНАЯ ФИЧА: МИРОВОЙ БОСС ---
@dp.callback_query(F.data == "boss_menu")
async def boss_menu(call: types.CallbackQuery):
    data = load_data()
    boss = data["boss"]
    status = "🔴 СПИТ" if not boss["active"] else "🟣 АКТИВЕН"
    
    text = (f"{HEADER}\n🌋 <b>МИРОВОЙ РЕЙД: ПОЖИРАТЕЛЬ</b>\n{SEP}\n"
            f"Статус: {status}\n"
            f"Здоровье: {boss['hp']:,} / {boss['max_hp']:,} HP\n"
            f"Ваш вклад: {data['players'][str(call.from_user.id)]['boss_dmg']:,} урона\n\n"
            f"<i>Бейте босса всей Галактикой! Когда HP упадет до 0, все участники получат Кредиты и Осколки Бездны.</i>\n{FOOTER}")
    
    b = InlineKeyboardBuilder()
    if boss["active"]:
        b.row(types.InlineKeyboardButton(text="💥 НАНЕСТИ УДАР", callback_data="boss_attack"))
    elif str(call.from_user.id) == str(ADMIN_ID):
        b.row(types.InlineKeyboardButton(text="⚡️ ПРОБУДИТЬ (АДМИН)", callback_data="boss_spawn"))
    
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=b.as_markup())

@dp.callback_query(F.data == "boss_spawn")
async def boss_spawn(call: types.CallbackQuery):
    if str(call.from_user.id) != str(ADMIN_ID): return
    data = load_data()
    data["boss"]["active"] = True
    data["boss"]["hp"] = data["boss"]["max_hp"]
    save_data(data)
    await call.answer("Босс пробужден!", show_alert=True)
    await boss_menu(call)

@dp.callback_query(F.data == "boss_attack")
async def boss_attack(call: types.CallbackQuery):
    data = load_data(); uid = str(call.from_user.id); u = data["players"][uid]
    if not data["boss"]["active"]: return await call.answer("Босс уже побежден!")
    if u["durability"] < 10: return await call.answer("Корабль слишком поврежден для атаки!")

    dmg = int(SHIPS[u["ship"]]["mult"] * random.randint(50, 150))
    data["boss"]["hp"] -= dmg
    u["boss_dmg"] += dmg
    u["durability"] -= 2
    
    msg = f"💥 Вы нанесли {dmg:,} урона!"
    
    if data["boss"]["hp"] <= 0:
        data["boss"]["active"] = False
        msg = "🎉 БОСС ПОВЕРЖЕН! Награды разосланы участникам."
        for p_id, p_data in data["players"].items():
            if p_data["boss_dmg"] > 0:
                reward = int(p_data["boss_dmg"] * 10)
                p_data["money"] += reward
                p_data["res"]["relic"] += 1
                p_data["boss_dmg"] = 0 
        data["boss"]["max_hp"] = int(data["boss"]["max_hp"] * 1.2) # Становится сильнее

    save_data(data)
    await call.answer(msg)
    await boss_menu(call)

# --- 2. РЫНОК (КОМАНДА /market И КНОПКИ) ---
@dp.callback_query(F.data == "market_menu")
async def market_menu(call: types.CallbackQuery):
    data = load_data(); b = InlineKeyboardBuilder()
    text = f"{HEADER}\n📈 <b>РЫНОК РЕСУРСОВ</b>\n{SEP}\n"
    if not data["market"]: text += "Лотов нет. Выставьте лот: `/sell iron 1000`"
    else:
        for lot in data["market"][-10:]:
            b.row(types.InlineKeyboardButton(text=f"🛒 {RESOURCES[lot['item']]} | {lot['price']:,} CR", callback_data=f"blot_{lot['id']}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(text + f"\n{FOOTER}", parse_mode="HTML", reply_markup=b.as_markup())

@dp.message(Command("sell"))
async def sell_cmd(m: types.Message, command: CommandObject):
    data = load_data(); uid = str(m.from_user.id)
    try:
        item, price = command.args.split()
        price = int(price)
        if data["players"][uid]["res"].get(item, 0) < 1: return await m.answer("У вас нет этого ресурса!")
        data["players"][uid]["res"][item] -= 1
        lot_id = len(data["market"]) + 1
        data["market"].append({"id": lot_id, "seller": uid, "item": item, "price": price})
        save_data(data); await m.answer(f"✅ Лот #{lot_id} выставлен!")
    except: await m.answer("Используй: `/sell iron 5000` (iron, crystal, chip, relic)")

@dp.callback_query(F.data.startswith("blot_"))
async def buy_lot(call: types.CallbackQuery):
    lid = int(call.data.split("_")[1]); data = load_data(); uid = str(call.from_user.id)
    lot = next((l for l in data["market"] if l["id"] == lid), None)
    if not lot: return await call.answer("Лот не найден.")
    if data["players"][uid]["money"] < lot["price"]: return await call.answer("Мало денег!")
    
    data["players"][uid]["money"] -= lot["price"]
    data["players"][uid]["res"][lot["item"]] += 1
    data["players"][lot["seller"]]["money"] += lot["price"]
    data["market"].remove(lot)
    save_data(data); await call.answer("Покупка завершена!"); await market_menu(call)

# --- 3. PVP СИСТЕМА ---
@dp.callback_query(F.data == "pvp_menu")
async def pvp_menu(call: types.CallbackQuery):
    u = load_data()["players"][str(call.from_user.id)]
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⚔️ ИСКАТЬ БОЙ", callback_data="pvp_fight"),
                                    types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"⚔️ <b>АРЕНА</b>\nПобед: {u['pvp_wins']}", reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "pvp_fight")
async def pvp_fight(call: types.CallbackQuery):
    data = load_data(); uid = str(call.from_user.id); enemies = [p for p in data["players"] if p != uid]
    if not enemies: return await call.answer("Вы один в космосе...")
    
    e_id = random.choice(enemies); u = data["players"][uid]; e = data["players"][e_id]
    u_p = SHIPS[u["ship"]]["mult"] * random.uniform(0.8, 1.2)
    e_p = SHIPS[e["ship"]]["mult"] * random.uniform(0.8, 1.2)
    
    if u_p > e_p:
        loot = int(e["money"] * 0.1); u["money"] += loot; e["money"] -= loot; u["pvp_wins"] += 1
        res = f"🏆 Победа над {e['name']}! Забрано {loot:,} CR."
    else:
        u["durability"] -= 20; res = f"💀 Поражение от {e['name']}. Корпус -20%."
    
    save_data(data); await call.message.edit_text(res, reply_markup=InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="ВЕРНУТЬСЯ", callback_data="pvp_menu")).as_markup())

# --- 4. МАГАЗИН И КЕЙСЫ (ПОЛНЫЕ) ---
@dp.callback_query(F.data == "open_shop")
async def open_shop(call: types.CallbackQuery):
    u = load_data()["players"][str(call.from_user.id)]; b = InlineKeyboardBuilder()
    for k, v in list(SHIPS.items())[1:]: # Кроме шаттла
        status = "✅" if k in u["inventory"] else f"{v['price']:,} CR"
        b.row(types.InlineKeyboardButton(text=f"{v['name']} ({status})", callback_data=f"buy_ship_{k}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text("🛒 <b>ВЕРФЬ ГАЛАКТИКИ</b>", reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy_ship_"))
async def buy_ship_logic(call: types.CallbackQuery):
    sid = call.data.split("_")[2]; data = load_data(); u = data["players"][str(call.from_user.id)]
    if sid in u["inventory"]: 
        u["ship"] = sid
        await call.answer("Корабль выбран!")
    elif u["money"] >= SHIPS[sid]["price"]:
        u["money"] -= SHIPS[sid]["price"]; u["inventory"].append(sid); u["ship"] = sid
        await call.answer("Успешная покупка!")
    else: return await call.answer("Недостаточно средств!")
    save_data(data); await open_shop(call)

@dp.callback_query(F.data == "cases_menu")
async def cases_menu(call: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    for k, v in CASES.items():
        b.row(types.InlineKeyboardButton(text=f"{v['n']} | {v['p']:,} CR", callback_data=f"opencase_{k}"))
    b.row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text("📦 <b>КОНТЕЙНЕРНЫЙ ТЕРМИНАЛ</b>", reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("opencase_"))
async def open_case(call: types.CallbackQuery):
    cid = call.data.split("_")[1]; data = load_data(); u = data["players"][str(call.from_user.id)]
    if u["money"] < CASES[cid]["p"]: return await call.answer("Недостаточно кредитов!")
    u["money"] -= CASES[cid]["p"]
    m = random.randint(*CASES[cid]["drop"]["money"]); x = random.randint(*CASES[cid]["drop"]["xp"])
    u["money"] += m; u["xp"] += x
    save_data(data); await call.answer(f"📦 Выпало: {m:,} CR и {x} XP!", show_alert=True); await cases_menu(call)

# --- 5. СЕРВИС И ПРОФИЛЬ ---
@dp.callback_query(F.data == "service_menu")
async def service_menu(call: types.CallbackQuery):
    u = load_data()["players"][str(call.from_user.id)]
    b = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🔧 ПОЧИНИТЬ (1000 CR)", callback_data="repair_full"),
                                    types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main"))
    await call.message.edit_text(f"🛠 <b>ТЕХ-ОБСЛУЖИВАНИЕ</b>\nСостояние корпуса: {u['durability']}%", reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "repair_full")
async def repair_full(call: types.CallbackQuery):
    data = load_data(); u = data["players"][str(call.from_user.id)]
    if u["money"] >= 1000:
        u["money"] -= 1000; u["durability"] = 100; save_data(data); await call.answer("Корабль как новый!")
    else: await call.answer("Мало кредитов!")
    await service_menu(call)

@dp.callback_query(F.data == "view_profile")
async def view_profile(call: types.CallbackQuery):
    u = load_data()["players"][str(call.from_user.id)]; lvl = get_lvl(u["xp"])
    res_str = "\n".join([f"{RESOURCES[k]}: {v}" for k, v in u["res"].items() if v > 0])
    text = (f"{HEADER}\n👤 <b>ПРОФИЛЬ ПИЛОТА</b>\n{SEP}\n"
            f"Имя: {u['name']}\nУровень: {lvl} ({u['xp']:,} XP)\n"
            f"Баланс: {u['money']:,} CR\nКорабль: {SHIPS[u['ship']]['name']}\n"
            f"Прочность: {u['durability']}%\nПобед в PVP: {u['pvp_wins']}\n\n"
            f"<b>РЕСУРСЫ:</b>\n{res_str if res_str else 'Пусто'}\n{FOOTER}")
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="↩️ НАЗАД", callback_data="back_main")).as_markup())

# --- 6. ИГРОВАЯ ЛОГИКА (СИНТЕЗ) ---
@dp.callback_query(F.data == "game_go")
async def game_go(call: types.CallbackQuery):
    phrase = random.choice(["СИНТЕЗ", "КВАНТ", "ОМЕГА", "ЗВЕЗДА", "АТОМ"])
    global_tasks[str(call.from_user.id)] = phrase
    await call.message.edit_text(f"🧩 Введите проверочный код: <code>{phrase}</code>", parse_mode="HTML")

@dp.message()
async def game_msg_handler(m: types.Message):
    uid = str(m.from_user.id); data = load_data()
    if uid in global_tasks and m.text.upper() == global_tasks[uid]:
        u = data["players"][uid]
        rew = int(random.randint(200, 500) * SHIPS[u["ship"]]["mult"])
        u["money"] += rew; u["xp"] += 35; u["durability"] -= 1
        del global_tasks[uid]
        if random.random() < 0.1: 
            u["res"]["iron"] += 1; await m.answer("⛓ Найдено Железо!")
        save_data(data)
        await m.answer(f"✅ Синтез успешен: +{rew:,} CR", reply_markup=main_kb(uid, u["xp"]))

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    u = load_data()["players"][str(call.from_user.id)]
    await call.message.edit_text(f"{HEADER}\n🚀 <b>ГЛАВНЫЙ МОСТИК</b>\n{SEP}\nСистемы в норме.\n{FOOTER}", parse_mode="HTML", reply_markup=main_kb(str(call.from_user.id), u["xp"]))

# ===================== [ ЗАПУСК ] =====================
async def main():
    print("💎 OMEGA-SYSTEM V6.0 STARTED")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

