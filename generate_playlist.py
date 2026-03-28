#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import urllib3
from urllib.parse import urlparse

# Отключаем предупреждения об отсутствии SSL-сертификата
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================================================
# 🔧 НАСТРОЙКИ
# =========================================================

# Откуда берем список каналов
URL_PLAYLIST1 = "http://a6a00836aefe.goodstreem.org/playlists/uplist/0e3bfa31d659f835f335f10165836f6d/playlist.m3u8"

# Откуда берем рабочий сервер (донор)
URL_PLAYLIST2 = "http://7d910a3da525.goodstreem.org/playlists/uplist/22825bfdcdb7e2ef359c18b30e40a234/playlist.m3u8"

# Переключатель логики:
# 0 = ВООБЩЕ НЕ МЕНЯТЬ домены (оставить как в Playlist 1)
# 1 = БРАТЬ БАЗОВЫЙ ДОМЕН из Playlist 2 (автоматика с сохранением субдоменов)
# 2 = БРАТЬ БАЗОВЫЙ ДОМЕН из USER_DOMAIN (вручную с сохранением субдоменов)
SERVER_SOURCE = 1

# Используется, только если SERVER_SOURCE = 2
USER_DOMAIN = "megogo.xyz"

# Резервный домен (используется только при SERVER_SOURCE = 1, если донор упал и кэш пуст)
FALLBACK_BASE_DOMAIN = "siauliairsavlt.com"

OUTPUT_FILE = "playlist3.m3u8"
CACHE_FILE = "domain_cache.txt"
REQUEST_TIMEOUT = 20

# =========================================================
# 🛠 СЛУЖЕБНЫЕ ФУНКЦИИ
# =========================================================

def log(msg): print(f"[INFO] {msg}")
def warn(msg): print(f"[WARN] {msg}")

def download_text(url):
    log(f"Скачивание: {url}")
    response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
    response.raise_for_status()
    return response.text.strip()

def get_base_domain(host):
    """Извлекает последние две части хоста. Пример: 'abc.example.com' -> 'example.com'"""
    if not host: return None
    parts = host.split('.')
    return ".".join(parts[-2:]) if len(parts) >= 2 else host

def extract_host_from_m3u(text):
    """Находит первую ссылку в тексте и возвращает её хост (netloc)."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("http"):
            return urlparse(line).netloc
    return None

# =========================================================
# 🚀 ОСНОВНАЯ ЛОГИКА
# =========================================================

def main():
    try:
        # 1. Загружаем основу (Playlist 1)
        playlist1_content = download_text(URL_PLAYLIST1)
        log("Playlist 1 успешно загружен.")

        # Если выбран режим "без изменений", просто сохраняем оригинал
        if SERVER_SOURCE == 0:
            log("Режим SERVER_SOURCE = 0: сохраняем оригинал без правок.")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(playlist1_content + "\n")
            log(f"✅ Успех! Файл {OUTPUT_FILE} создан (копия оригинала).")
            return

        # 2. Определяем новый БАЗОВЫЙ домен
        new_base_domain = None

        if SERVER_SOURCE == 1:
            try:
                # Пытаемся получить донорский домен из Playlist 2
                donor_full_host = extract_host_from_m3u(download_text(URL_PLAYLIST2))
                new_base_domain = get_base_domain(donor_full_host)
                
                if new_base_domain:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        f.write(new_base_domain)
                    log(f"Новый базовый домен из Playlist 2: {new_base_domain}")
            except Exception as e:
                warn(f"Не удалось получить Playlist 2: {e}")
                if os.path.exists(CACHE_FILE):
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        new_base_domain = f.read().strip()
                        log(f"Используем домен из КЭША: {new_base_domain}")
                else:
                    new_base_domain = FALLBACK_BASE_DOMAIN
                    warn(f"Кэш пуст. Используем FALLBACK: {new_base_domain}")
        
        elif SERVER_SOURCE == 2:
            new_base_domain = USER_DOMAIN
            log(f"Используем пользовательский домен: {new_base_domain}")

        # 3. Трансформация ссылок с сохранением субдоменов
        final_lines = []
        for line in playlist1_content.splitlines():
            line_s = line.strip()
            
            if line_s.startswith("http"):
                parsed = urlparse(line_s)
                original_full_host = parsed.netloc # например, 'riusiepq.alfalt.fun'
                
                parts = original_full_host.split('.')
                # Если в оригинале есть субдомен (больше 2 частей)
                if len(parts) > 2:
                    subdomain = ".".join(parts[:-2]) # вырезаем 'riusiepq'
                    new_host = f"{subdomain}.{new_base_domain}"
                else:
                    new_host = new_base_domain
                
                # Заменяем только хост в строке
                new_line = line_s.replace(original_full_host, new_host)
                final_lines.append(new_line)
            else:
                final_lines.append(line)

        # 4. Сохранение итогового файла
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines) + "\n")
        
        log(f"✅ Успех! Сгенерирован {OUTPUT_FILE} с доменом {new_base_domain}")

    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
