# parser.py
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import date
import logging
import os
import requests

# Конфигурация Telegram
TG_TOKEN = "8760369139:AAEkS3iMVNC5GPw5lbfYde5_RBjijW8o0iI"  # токен от BotFather
TG_CHAT_ID = "1022165128"         # твой chat_id от userinfobot

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=5)
    except:
        pass  # чтобы парсер не упал, если нет интернета

send_telegram("🔍 Тестовое сообщение: бот работает!")

# Создаём папку для логов, если её нет
if not os.path.exists('logs'):
    os.makedirs('logs')

# Настройка логов
logging.basicConfig(filename='logs/parser.log', level=logging.INFO)

# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    database="books_monitor",
    user="postgres",
    password="123"
)

def save_books(books):
    cursor = conn.cursor()
    for rank, title in enumerate(books, 1):
        # Вставляем книгу
        cursor.execute(
            "INSERT INTO books (title, rank, collected_date) VALUES (%s, %s, %s) RETURNING id",
            (title, rank, date.today())
        )
        book_id = cursor.fetchone()[0]
        
        # Пишем историю
        cursor.execute(
            "INSERT INTO books_history (book_id, title, rank, change_date) VALUES (%s, %s, %s, %s)",
            (book_id, title, rank, date.today())
        )
    conn.commit()
    logging.info(f"Сохранено {len(books)} книг")

def parse_gutenberg():
    url = "https://www.gutenberg.org/browse/scores/top"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    books = []
    ol = soup.find("ol")
    if ol:
        for li in ol.find_all("li")[:100]:
            books.append(li.get_text(strip=True))
    return books

if __name__ == "__main__":
    try:
        books = parse_gutenberg()
        save_books(books)
        logging.info("Парсинг успешно завершён")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
try:
    # ... твой существующий код парсера ...
    send_telegram("✅ <b>Парсинг выполнен успешно!</b>\n\nСохранено книг: " + str(len(books)))
except Exception as e:
    send_telegram(f"❌ <b>Ошибка парсинга!</b>\n\n{str(e)}")
    raise
