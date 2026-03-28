#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import urllib3
from urllib.parse import urlparse

# Отключаем предупреждения об отсутствии SSL-сертификата (чтобы не спамить в логах)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================================================
# НАСТРОЙКИ (Ваши реальные данные)
# =========================================================

# Основной плейлист (отсюда берём каналы)
URL_PLAYLIST1 = "http://a6a00836aefe.goodstreem.org/playlists/uplist/0e3bfa31d659f835f335f10165836f6d/playlist.m3u8"

# Донор серверной части
URL_PLAYLIST2 = "http://7d910a3da525.goodstreem.org/playlists/uplist/22825bfdcdb7e2ef359c18b30e40a234/playlist.m3u8"

# 1 = брать сервер из playlist2 (с fallback)
# 2 = брать пользовательский домен USER_DOMAIN
SERVER_SOURCE = 1

# Пользовательский домен (если SERVER_SOURCE = 2)
USER_DOMAIN = "megogo.xyz"

# Резервный сервер (если playlist2 не скачался и кэша нет)
# Сюда впишите последний известный РАБОЧИЙ хост (например, из логов)
FALLBACK_SERVER_HOST = "7d910a3da525.goodstreem.org"

OUTPUT_FILE = "playlist3.m3u8"
CACHE_FILE = "playlist2_cache.m3u8"
REQUEST_TIMEOUT = 20

# =========================================================
# ЛОГИКА
# =========================================================

def log(msg): print(f"[INFO] {msg}")
def warn(msg): print(f"[WARN] {msg}")

def download_text(url):
    log(f"Скачивание: {url}")
    # Добавлен verify=False для обхода ошибок сертификатов
    response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
    response.raise_for_status()
    return response.text.strip()

def extract_host_from_m3u(text):
    """Находит первую ссылку в плейлисте и вырезает из неё хост."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("http"):
            parsed = urlparse(line)
            return parsed.netloc
    return None

def main():
    try:
        # 1. Загружаем основу (Playlist 1)
        playlist1_content = download_text(URL_PLAYLIST1)
        
        # Находим старый сервер в Playlist 1, чтобы потом его заменить
        old_host = extract_host_from_m3u(playlist1_content)
        if not old_host:
            raise ValueError("Не удалось найти сервер в Playlist 1")
        
        # 2. Определяем новый сервер
        new_host = None

        if SERVER_SOURCE == 1:
            try:
                # Пробуем скачать Playlist 2
                playlist2_content = download_text(URL_PLAYLIST2)
                new_host = extract_host_from_m3u(playlist2_content)
                
                # Если скачали успешно — сохраняем в кэш
                if new_host:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        f.write(new_host)
            except Exception as e:
                warn(f"Ошибка загрузки Playlist 2: {e}")
                # Если не скачалось — ищем в кэше
                if os.path.exists(CACHE_FILE):
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        new_host = f.read().strip()
                        log(f"Используем сервер из КЭША: {new_host}")
                else:
                    new_host = FALLBACK_SERVER_HOST
                    warn(f"Кэш пуст. Используем FALLBACK: {new_host}")

        else:
            # SERVER_SOURCE == 2 (Пользовательский домен)
            # Берем субдомен из первой ссылки Playlist 1 и клеим к USER_DOMAIN
            parts = old_host.split('.')
            subdomain = parts[0] if len(parts) > 1 else ""
            new_host = f"{subdomain}.{USER_DOMAIN}" if subdomain else USER_DOMAIN
            log(f"Используем пользовательский домен: {new_host}")

        # 3. Массовая замена
        log(f"Заменяем {old_host} -> {new_host}")
        # Заменяем только хост, чтобы не повредить пути
        final_content = playlist1_content.replace(old_host, new_host)

        # 4. Сохранение
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        log(f"✅ Готово! Файл {OUTPUT_FILE} успешно создан.")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
