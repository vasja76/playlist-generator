#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для загрузки и очистки m3u8-плейлиста от лишних категорий.
Автор: Vasily Alexeev
Дата: 2025-11-02
"""

import re
import requests

# === 🔧 НАСТРОЙКИ ===

# URL исходного плейлиста
PLAYLIST_URL = "http://vipl.one/hls/d3zwhr58b7mv/playlist.m3u8"

# Имя сохраняемого файла
OUTPUT_FILE = "playlist5.m3u8"

# Категории (group-title), которые нужно удалить из плейлиста
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
    "Литва",
    "Религиозные",
    "Кулинарные",
    "Саудовская Аравия"
]

# Триггер: если 1 — удалять каналы, в названии которых есть "HD"
REMOVE_HD = 1


def download_playlist(url: str) -> str:
    """Загружает M3U8-плейлист и возвращает его содержимое в виде текста."""
    print(f"📥 Загружаем плейлист: {url}")
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    print("✅ Плейлист успешно загружен.")
    return response.text


def filter_playlist(content: str) -> str:
    """
    Удаляет из M3U8-плейлиста все каналы, принадлежащие к категориям REMOVE_GROUPS,
    а также, при активном REMOVE_HD, каналы с 'HD' в названии.
    """
    lines = content.splitlines()
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Сохраняем заголовок
        if i == 0 and line.startswith("#EXTM3U"):
            result.append(line)

        # Проверяем строки каналов
        elif line.startswith("#EXTINF"):
            # Извлекаем категорию (group-title="...")
            match = re.search(r'group-title="([^"]+)"', line)
            group = match.group(1) if match else ""

            # Извлекаем имя канала (после запятой)
            name_match = re.match(r'.*,\s*(.+)$', line)
            channel_name = name_match.group(1).strip() if name_match else ""

            # Проверяем, нужно ли удалить
            remove_block = False
            reason = []

            if group in REMOVE_GROUPS:
                remove_block = True
                reason.append(f"group={group}")
            if REMOVE_HD and "HD" in channel_name.upper():
                remove_block = True
                reason.append("HD-name")

            if remove_block:
                print(f"🗑 Удалён канал: {channel_name} ({', '.join(reason)})")
                # Пропускаем #EXTINF, #EXTGRP и URL
                i += 1
                if i < len(lines) and lines[i].startswith("#EXTGRP"):
                    i += 1
                if i < len(lines):
                    i += 1
                continue  # не добавляем в result

            # Если категория разрешена — добавляем блок целиком
            result.append(line)
            if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                result.append(lines[i + 1])
                i += 1
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                result.append(lines[i + 1])

        i += 1

    print("🧹 Плейлист очищен от указанных категорий и HD-каналов (если включено).")
    return "\n".join(result)


def save_playlist(content: str, filename: str) -> None:
    """Сохраняет текст в файл."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Плейлист сохранён как {filename}")


def main():
    try:
        text = download_playlist(PLAYLIST_URL)
        filtered = filter_playlist(text)
        save_playlist(filtered, OUTPUT_FILE)
        print("✅ Готово. Плейлист успешно обновлён и очищен.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
