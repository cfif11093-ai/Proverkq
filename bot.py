import telebot
import requests
import time

# Ваш токен
BOT_TOKEN = '8960373658:AAGx8LfFv2Kp-5qWQhhDHDGFvKwL0NmOEcY'
bot = telebot.TeleBot(BOT_TOKEN)

def parse_avito(query):
    # Превращаем пробелы в плюсы для ссылки Авито (например iphone+12)
    search_query = query.replace(' ', '+')
    url = f"https://www.avito.ru/miass/telefony?q={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # ВАЖНО: timeout=10 не даст боту зависнуть навсегда!
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return "❌ Ошибка 403: Авито понял, что мы бот, и заблокировал доступ."
        elif response.status_code == 200:
            return "✅ Бот смог пробиться на сайт Авито! (Но парсинг цен без Selenium с телефона сделать не выйдет)."
        else:
            return f"⚠️ Сайт вернул странный ответ: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏳ Авито слишком долго не отвечает (сработала защита Cloudflare). Бот прервал попытку, чтобы не зависнуть."
    except Exception as e:
        return f"❌ Ошибка соединения: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = "Привет! Я бот для мониторинга Авито.\n\nНапиши команду поиска. Например:\n/find iPhone 12 - 8000"
    bot.reply_to(message, text)

@bot.message_handler(commands=['find'])
def find_command(message):
    try:
        # Убираем слово /find из сообщения
        text = message.text.replace('/find', '').strip()
        
        # Проверяем наличие дефиса
        if '-' not in text:
            bot.reply_to(message, "⚠️ Неверный формат! Обязательно используйте дефис. Пример:\n/find iPhone 12 - 8000")
            return
            
        parts = text.split('-')
        query = parts[0].strip()
        max_price = parts[1].strip()
        
        bot.reply_to(message, f"🔍 Ищу: {query} (до {max_price} руб.)\n⏳ Пытаюсь обойти защиту Авито, ждите...")
        
        # Запускаем функцию поиска
        result = parse_avito(query)
        bot.reply_to(message, result)
        
    except Exception as e:
        bot.reply_to(message, "❌ Произошла непредвиденная ошибка в коде.")

print("--------------------------------------------------")
print("Бот успешно запущен и защищен от зависаний!")
print("Перейдите в Телеграм и напишите: /find iPhone 12 - 8000")
print("--------------------------------------------------")

# Бессмертный цикл
while True:
    try:
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Сбой интернета. Переподключение через 5 секунд...")
        time.sleep(5)
