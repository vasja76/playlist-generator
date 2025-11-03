#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для загрузки и фильтрации M3U8-плейлиста.
Автор: Vasily Alexeev
Дата: 2025-11-02
"""

import re
import requests

# === 🔧 Настройки ===

# URL источника
PLAYLIST_URL = "http://vipl.one/hls/kbasrzi4t3cf/playlist.m3u8"

# Основной файл
OUTPUT_FILE = "playlist5.m3u8"

# 1 — удалять каналы с "HD" в названии, 0 — оставлять
REMOVE_HD = 1

# Категории, которые нужно удалить
REMOVE_GROUPS = [
    "Детские",
    "Региональные",
    "Германия",
    "Армения",
    "Грузия",
    "Казахстан",
    "Молдова",
    "Азербайджан",
    "Израиль",
    "Спортивные",
    "Таджикистан",
    "Узбекистан",
    "Турция",
    "Польша",
    "Эстония",
    "Латвия",
    "Литва"
]


# === ⚙️ Функции ===

def download_playlist(url: str) -> list:
    """Загружает плейлист и возвращает список строк."""
    print(f"📥 Загружаем плейлист: {url}")
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    lines = response.text.splitlines()
    print(f"✅ Плейлист загружен ({len(lines)} строк)")
    return lines


def filter_playlist(lines: list) -> list:
    """Удаляет ненужные категории и HD-каналы (если REMOVE_HD = 1)."""
    filtered = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if i == 0 and line.startswith("#EXTM3U"):
            filtered.append(line)
            i += 1
            continue

        if line.startswith("#EXTINF"):
            group_match = re.search(r'group-title="([^"]+)"', line)
            channel_match = re.match(r'.*,\s*(.+)$', line)
            group = group_match.group(1) if group_match else ""
            channel = channel_match.group(1).strip() if channel_match else ""

            # Удаляем по категории
            if any(gr.lower() in group.lower() for gr in REMOVE_GROUPS):
                i += 2
                continue

            # Удаляем по слову "HD", если включено
            if REMOVE_HD and "HD" in channel.upper():
                i += 2
                continue

            # Добавляем канал и его URL
            filtered.append(line)
            if i + 1 < len(lines):
                filtered.append(lines[i + 1])
            i += 2
            continue

        i += 1

    print(f"🧹 После фильтрации осталось {len(filtered)} строк")
    return filtered


def save_playlist(lines: list, filename: str):
    """Сохраняет результат в файл."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"💾 Сохранён обновлённый файл: {filename}")


# === 🚀 Основной блок ===

if __name__ == "__main__":
    try:
        raw_lines = download_playlist(PLAYLIST_URL)
        result = filter_playlist(raw_lines)
        save_playlist(result, OUTPUT_FILE)
        print("✅ Готово. Плейлист успешно обновлён.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
