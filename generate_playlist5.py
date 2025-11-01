#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для загрузки m3u8-плейлиста.
Автор: Vasily Alexeev
Дата: 2025-11-01
"""

import requests

# 🔧 Укажите здесь URL плейлиста
PLAYLIST_URL = "http://vipl.one/hls/kbasrzi4t3cf/playlist.m3u8"

# Имя сохраняемого файла
OUTPUT_FILE = "playlist5.m3u8"


def download_playlist(url: str, filename: str) -> None:
    """Загружает M3U8-плейлист по указанному URL и сохраняет локально."""
    try:
        print(f"📥 Загружаем плейлист: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Плейлист сохранён как {filename}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке: {e}")


if __name__ == "__main__":
    download_playlist(PLAYLIST_URL, OUTPUT_FILE)
