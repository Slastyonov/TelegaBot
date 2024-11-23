pip install python-telegram-bot
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import threading
import datetime
import time

# ВАШ ТОКЕН БОТА
TOKEN = '7401843171:AAGRq5yxApTRL8QnVqAxlTpAQRJKvR26dok'

# Глобальні змінні
selected_users = []  # Вибрані користувачі
mode = 'day'  # Режим роботи (day або night)
active = False  # Статус бота

# Час повідомлень
day_schedule = ['10:05', '12:05', '14:35', '17:05']
night_schedule = ['21:50', '23:50', '02:35', '05:05']

# Функція для відправки повідомлень
def send_messages(bot: Bot, chat_id: int, users: list, schedule: list):
    for time_str in schedule:
        if not active:  # Перевіряємо, чи бот активний
            break

        now = datetime.datetime.now()
        target_time = datetime.datetime.strptime(time_str, '%H:%M').replace(
            year=now.year, month=now.month, day=now.day)

        # Якщо час уже пройшов, переносимо на наступний день
        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        time.sleep(wait_time)

        if active:  # Перевіряємо, чи бот все ще активний
            bot.send_message(chat_id, f"Прибираємо на рядах! {users[0]} {users[1]}")

# Команда /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привіт! Я допоможу організувати прибирання. Напишіть /choose, щоб вибрати учасників.")

# Команда /choose
def choose(update: Update, context: CallbackContext):
    global selected_users
    chat = update.message.chat
    members = [f"@{member.user.username}" for member in context.bot.get_chat_administrators(chat.id) if member.user.username]

    if len(members) < 2:
        update.message.reply_text("Недостатньо учасників у групі для вибору.")
        return

    selected_users = members[:2]  # Ви можете замінити це на логіку рандомного вибору
    update.message.reply_text(f"Обрано: {selected_users[0]} і {selected_users[1]}. Напишіть /start_day або /start_night для запуску.")

# Команда /start_day
def start_day(update: Update, context: CallbackContext):
    global mode, active
    if not selected_users:
        update.message.reply_text("Спочатку оберіть учасників за допомогою /choose.")
        return

    mode = 'day'
    active = True
    update.message.reply_text("Денний режим активовано. Надсилання повідомлень почнеться за графіком.")
    thread = threading.Thread(target=send_messages, args=(context.bot, update.message.chat_id, selected_users, day_schedule))
    thread.start()

# Команда /start_night
def start_night(update: Update, context: CallbackContext):
    global mode, active
    if not selected_users:
        update.message.reply_text("Спочатку оберіть учасників за допомогою /choose.")
        return

    mode = 'night'
    active = True
    update.message.reply_text("Нічний режим активовано. Надсилання повідомлень почнеться за графіком.")
    thread = threading.Thread(target=send_messages, args=(context.bot, update.message.chat_id, selected_users, night_schedule))
    thread.start()

# Команда /stop
def stop(update: Update, context: CallbackContext):
    global active
    active = False
    update.message.reply_text("Робота бота зупинена. Напишіть /start, щоб почати заново.")

# Основна функція
def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("choose", choose))
    dispatcher.add_handler(CommandHandler("start_day", start_day))
    dispatcher.add_handler(CommandHandler("start_night", start_night))
    dispatcher.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()