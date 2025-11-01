# -*- coding: utf-8 -*-
import os
import re

# === Настройки ===
INPUT_FILE = "playlist5.m3u8"   # Исходный плейлист
OUTPUT_FILE = "playlist6.m3u8"  # Фильтрованный плейлист

# === Список нужных каналов ===
CHANNELS = [
    "Первый канал",
    "Россия 1",
    "Рен ТВ",
    "СТС",
    "Звезда",
    "ТНТ",
    "Муз ТВ",
    "Че",
    "Europa Plus",
    "ТНТ Music",
    "TV1000 Русское",
    "Советское кино",
    "Ю",
    "Охота и Рыбалка",
    "Беларусь 24",
    "Animal Planet",
    "Da Vinci learning",
    "Discovery",
    "Discovery HD",
    "National Geographic",
    "Наука 2.0",
    "Техно 24",
    "КВН ТВ",
    "ТНТ4",
    "Первый канал (+2)",
    "Россия 1 (+2)",
    "СТС (+2)",
    "ТНТ (+2)",
    "ТНТ4 (+2)",
    "Беларусь 1",
    "Русская ночь",
    "Russian HD",
    "Беларусь 1",
    "К1",
    "К2",
    "1+1",
    "Club Parody",
    "Club Teens HD",
    "EroLuxe Russian Teens",
    "Retro SEX HD"
]

# === Проверка существования playlist5 ===
if not os.path.isfile(INPUT_FILE):
    print(f"Error: {INPUT_FILE} не найден. Сначала сформируйте playlist5.")
    exit(1)

# === Чтение файла ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

filtered_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Заголовок M3U
    if i == 0 and line.startswith("#EXTM3U"):
        filtered_lines.append(line)

    # Поиск строк каналов
    elif line.startswith("#EXTINF"):
        # Извлекаем имя канала (всё после последней запятой)
        match = re.match(r'.*,\s*(.+)$', line)
        if match:
            channel_name = match.group(1).strip()
            if channel_name in CHANNELS:
                filtered_lines.append(line)
                # Добавляем #EXTGRP (если есть)
                if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                    filtered_lines.append(lines[i + 1])
                    i += 1
                # Добавляем URL (следующая строка)
                if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                    filtered_lines.append(lines[i + 1])

    i += 1

# === Сохраняем результат ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_lines))

print(f"✅ Готово. {OUTPUT_FILE} успешно создан из {INPUT_FILE}.")
