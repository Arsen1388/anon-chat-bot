import telebot
import random
import json
import requests

TOKEN = '7231586415:AAGAb5nQGQ-gCSJaTO7F266mPpYs2eRNP7g'
bot = telebot.TeleBot(TOKEN)

users = {}
waiting_users = []

OPENAI_KEY = "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"

def ask_gpt(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "⚠️ Что-то пошло не так. Попробуй снова."

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users[user_id] = {'partner': None, 'is_ai': False}
    bot.send_message(user_id, "👋 Привет! Напиши /search чтобы начать искать собеседника.")

@bot.message_handler(commands=['search'])
def search(message):
    user_id = message.chat.id
    if users[user_id]['partner']:
        bot.send_message(user_id, "❗ Вы уже в чате. Напишите /stop чтобы выйти.")
        return
    if waiting_users:
        partner_id = waiting_users.pop(0)
        users[user_id]['partner'] = partner_id
        users[partner_id]['partner'] = user_id
        bot.send_message(user_id, "✅ Вы подключены к собеседнику. Напишите сообщение.")
        bot.send_message(partner_id, "✅ Вы подключены к собеседнику. Напишите сообщение.")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⏳ Ожидаем другого пользователя...")

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    partner_id = users[user_id].get('partner')
    if partner_id:
        users[partner_id]['partner'] = None
        bot.send_message(partner_id, "❌ Собеседник покинул чат.")
    users[user_id]['partner'] = None
    bot.send_message(user_id, "🚫 Вы покинули чат.")

@bot.message_handler(func=lambda m: True)
def chat(message):
    user_id = message.chat.id
    partner_id = users[user_id].get('partner')

    if partner_id:
        if users[partner_id].get('is_ai'):
            reply = ask_gpt(message.text)
            bot.send_message(user_id, reply)
        else:
            bot.send_message(partner_id, message.text)
    else:
        # Если нет партнёра, подключаем ИИ
        ai_id = f'ai_{user_id}'
        users[user_id]['partner'] = ai_id
        users[ai_id] = {'partner': user_id, 'is_ai': True}
        bot.send_message(user_id, "🤖 Присоединился собеседник. Начните разговор!")

bot.polling()
