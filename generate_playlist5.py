#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фильтрация M3U8-плейлиста: удаляем целые блоки каналов по group-title.
Не меняем содержимое оставшихся блоков.
Автор: Vasily Alexeev (правка)
"""

import re
import requests
import os

# === НАСТРОЙКИ ===

# Источник (если нужно скачивать). Если хочешь брать локальный playlist5.m3u8,
# просто положи файл рядом и скрипт прочтёт его (см. ниже).
PLAYLIST_URL = "http://vipl.one/hls/kbasrzi4t3cf/playlist.m3u8"

# Файлы
INPUT_FILE = "playlist5.m3u8"   # если локальный файл присутствует, будет использован
OUTPUT_FILE = "playlist5.m3u8"  # перезаписываем тот же файл

# 0 — не удалять по "HD" в имени, 1 — удалять (по желанию)
REMOVE_HD = 1

# Список категорий group-title, которые нужно удалить (совпадение нечувствительно к регистру)
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
]

# === ФУНКЦИИ ===

def get_playlist_text():
    """Возвращает текст плейлиста: сначала пытаемся прочесть локальный INPUT_FILE,
    иначе скачиваем по PLAYLIST_URL."""
    if os.path.isfile(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    # локального нет — скачиваем
    resp = requests.get(PLAYLIST_URL, timeout=20)
    resp.raise_for_status()
    return resp.text

def should_remove_extinf_line(extinf_line: str) -> bool:
    """
    Решает, нужно ли удалить блок, исходя из строки #EXTINF.
    Удаляем, если group-title совпадает с REMOVE_GROUPS (частичное/ нечувствительное к регистру)
    или (опционально) в имени канала есть 'HD' и REMOVE_HD == 1.
    """
    # Найдём значение group-title="..."
    gm = re.search(r'group-title="([^"]+)"', extinf_line, flags=re.IGNORECASE)
    if gm:
        group = gm.group(1).strip().lower()
        for g in REMOVE_GROUPS:
            if g.strip().lower() == group:
                return True

    # Если нет group-title, можно ещё попытаться удалить по ключевым словам в самой строке
    # (но по умолчанию мы этого не делаем — только explicit group-title).
    # Проверка на HD в названии (после последней запятой)
    if REMOVE_HD:
        m = re.match(r'.*,\s*(.+)$', extinf_line)
        if m:
            chname = m.group(1).strip().lower()
            if "hd" in chname.split():  # слово HD отдельно
                return True
            # также проверим вхождение 'hd' в конце/скобках и т.п.
            if "hd" in chname:
                return True

    return False

def filter_playlist_text(text: str) -> str:
    """
    Парсим плейлист построчно. Каждый блок начинается с #EXTINF и продолжается до
    следующей строки, начинающейся с #EXTINF (не включая её) — все эти строки считаются частью блока.
    Если блок помечен на удаление — пропускаем весь блок.
    Иначе — копируем блок в выходной текст в точности как есть.
    Также сохраняем любые строки до первого #EXTINF (заголовки).
    """
    lines = text.splitlines()
    out_lines = []
    i = 0
    n = len(lines)

    # Сохраняем все строки до первого #EXTINF (обычно #EXTM3U и возможные мета)
    while i < n and not lines[i].startswith("#EXTINF"):
        out_lines.append(lines[i])
        i += 1

    # Обрабатываем блоки, начинающиеся с #EXTINF
    while i < n:
        if not lines[i].startswith("#EXTINF"):
            # неожиданные строки — просто копируем
            out_lines.append(lines[i])
            i += 1
            continue

        # Начинается блок
        block = [lines[i]]
        j = i + 1
        # Собираем все последующие строк до следующего #EXTINF или EOF
        while j < n and not lines[j].startswith("#EXTINF"):
            block.append(lines[j])
            j += 1

        extinf_line = block[0]
        if should_remove_extinf_line(extinf_line):
            # Пропускаем весь блок (ничего не добавляем)
            pass
        else:
            # Копируем блок без изменений
            out_lines.extend(block)

        i = j  # продолжаем с следующего блока

    # Воссоздаём текст с сохранением переводов строки как в оригинале (LF)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

# === MAIN ===

def main():
    try:
        original = get_playlist_text()
    except Exception as e:
        print("Ошибка при получении плейлиста:", e)
        return

    filtered = filter_playlist_text(original)

    # Записываем результат, перезаписывая OUTPUT_FILE (без архивов)
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(filtered)
        print(f"Готово — записан {OUTPUT_FILE}")
    except Exception as e:
        print("Ошибка при записи файла:", e)

if __name__ == "__main__":
    main()
