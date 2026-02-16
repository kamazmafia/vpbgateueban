import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# ================== НАСТРОЙКИ ==================
# Список зеркал сайта (все рабочие адреса)
MIRROR_SITES = [
    "http://124.210.129.68:35405/en/",
    "http://161.248.188.104:47271/en/",
    "http://123.16.31.115:42815/en/",
    "http://118.108.57.136:47201/en/",
    "http://125.134.100.58:64385/en/",
    "http://113.147.98.19:41259/en/"
]

# Токен и Chat ID получаем из секретов GitHub
TOKEN = os.environ.get('7588241489:AAFuX49z2v9787XzxaZV7vQ7a17nNri2lCI')
CHAT_ID = os.environ.get('5173431937')
# ===============================================

def fetch_server_ips():
    """Парсинг IP-адресов и стран с сайта VPN"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in MIRROR_SITES:
        try:
            print(f"🔄 Пробуем зеркало: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Ищем таблицу с серверами
            table = soup.find('table', class_='table')
            if not table:
                table = soup.find('table')
            
            if not table:
                print("⚠️ Таблица не найдена, пробуем следующее зеркало...")
                continue
                
            servers_list = []
            rows = table.find_all('tr')
            
            # Пропускаем заголовок таблицы
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    country = cols[1].text.strip()
                    ip_address = cols[2].text.strip()
                    
                    # Проверка на IP-адрес
                    if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip_address):
                        servers_list.append(f"🌍 {country}: {ip_address}")
                    else:
                        servers_list.append(f"🌍 {country}: {ip_address} (домен)")
            
            if servers_list:
                print(f"✅ Найдено {len(servers_list)} серверов")
                return servers_list
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue
    
    return ["❌ Не удалось получить данные ни с одного зеркала"]

def send_telegram_message(message):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Добавляем время отправки
    current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    full_message = f"<b>🌐 Актуальные серверы VPN</b>\n🕐 {current_time}\n\n{message}"
    
    # Разбиваем длинные сообщения
    if len(full_message) > 4000:
        parts = [full_message[i:i+4000] for i in range(0, len(full_message), 4000)]
        for part in parts:
            data = {
                "chat_id": CHAT_ID,
                "text": part,
                "parse_mode": "HTML"
            }
            requests.post(url, data=data)
    else:
        data = {
            "chat_id": CHAT_ID,
            "text": full_message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)

def main():
    """Главная функция"""
    if not TOKEN or not CHAT_ID:
        print("❌ Ошибка: Не заданы BOT_TOKEN или CHAT_ID")
        return
    
    print(f"🚀 Запуск парсера в {datetime.now().strftime('%H:%M:%S')}")
    
    # Получаем список серверов
    servers = fetch_server_ips()
    
    # Формируем сообщение
    message_text = "\n".join(servers)
    
    # Отправляем в Telegram
    send_telegram_message(message_text)
    print("✅ Сообщение отправлено!")

if __name__ == "__main__":
    main()