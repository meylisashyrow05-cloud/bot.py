import os
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

MENU = {
    "Burgery": {"Klassik": 150, "Chizburger": 180, "Dvojnoj": 220},
    "Kartoshka": {"Fri malyj": 80, "Fri bolshoj": 120},
    "Napitki": {"Kola": 90, "Sok": 100, "Voda": 60},
}

carts = {}

def cart(uid):
    if uid not in carts:
        carts[uid] = {}
    return carts[uid]

def price(item):
    for cat in MENU.values():
        if item in cat:
            return cat[item]
    return 0

@bot.message_handler(commands=["start"])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Menu", "Korzina", "Kontakty")
    bot.send_message(m.chat.id, "Dobro pozhalovat! Vyberi razdel:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "Menu")
def menu(m):
    kb = types.InlineKeyboardMarkup()
    for cat in MENU:
        kb.add(types.InlineKeyboardButton(cat, callback_data="cat_"+cat))
    bot.send_message(m.chat.id, "Vyberi kategoriju:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def show_cat(c):
    cat = c.data[4:]
    kb = types.InlineKeyboardMarkup()
    for item, p in MENU[cat].items():
        kb.add(types.InlineKeyboardButton(f"{item} - {p} rub", callback_data="add_"+item))
    kb.add(types.InlineKeyboardButton("Nazad", callback_data="back"))
    bot.edit_message_text(cat, c.message.chat.id, c.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(c):
    kb = types.InlineKeyboardMarkup()
    for cat in MENU:
        kb.add(types.InlineKeyboardButton(cat, callback_data="cat_"+cat))
    bot.edit_message_text("Vyberi kategoriju:", c.message.chat.id, c.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def add(c):
    item = c.data[4:]
    ct = cart(c.from_user.id)
    ct[item] = ct.get(item, 0) + 1
    bot.answer_callback_query(c.id, f"{item} dobavlen!")

@bot.message_handler(func=lambda m: m.text == "Korzina")
def show_cart(m):
    ct = cart(m.from_user.id)
    if not ct:
        bot.send_message(m.chat.id, "Korzina pusta!")
        return
    text = "Vasha korzina:\n"
    total = 0
    for item, qty in ct.items():
        p = price(item)
        text += f"{item} x{qty} = {p*qty} rub\n"
        total += p * qty
    text += f"\nItogo: {total} rub"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Zakazat", callback_data="order"))
    kb.add(types.InlineKeyboardButton("Ochistit", callback_data="clear"))
    bot.send_message(m.chat.id, text, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "order")
def order(c):
    carts[c.from_user.id] = {}
    bot.edit_message_text("Zakaz prinjat! Zhdi 15-20 minut!", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "clear")
def clear(c):
    carts[c.from_user.id] = {}
    bot.edit_message_text("Korzina ochisthena!", c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: m.text == "Kontakty")
def contacts(m):
    bot.send_message(m.chat.id, "Tel: +7 999 123-45-67\nAdres: ul. Primernaya 1\nRabotaem: 10:00-23:00")

bot.infinity_polling()
