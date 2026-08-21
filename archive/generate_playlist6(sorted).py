# -*- coding: utf-8 -*-
import os
import re

# === Настройки ===
INPUT_FILE = "playlist5.m3u8"   # Исходный плейлист
OUTPUT_FILE = "playlist6.m3u8"  # Фильтрованный плейлист

# === Список нужных каналов в желаемом порядке ===
CHANNELS = [
    "Первый канал",
    "Россия 1",
    "Рен ТВ",
    "Звезда",
    "СТС",
    "ТНТ",
    "Че",
    "Муз ТВ",
    "Europa Plus",
    "ТНТ Music",
    "TV1000 Русское",
    "Советское кино",
    "Ю",
    "Охота и Рыбалка",
    "Animal Planet",
    "Discovery",
    "National Geographic",
    "Наука 2.0",
    "Вопросы и ответы",
    "Nano TV",
    "КВН ТВ",
    "ТНТ4",
    "Первый канал (+2)",
    "Россия 1 (+2)",
    "СТС (+2)",
    "ТНТ (+2)",
    "ТНТ4 (+2)",
    "Че (+2)",
    "Беларусь 1",
    "Беларусь 24",
    "К1",
    "К2",
    "Интер",
    "Русская ночь",
    "EroLuxe Cinema",
    "EroLuxe Russian Teens"
]

# === Проверка существования playlist5 ===
if not os.path.isfile(INPUT_FILE):
    print(f"Error: {INPUT_FILE} не найден. Сначала сформируйте playlist5.")
    exit(1)

# === Чтение исходного файла ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

# 1. Заголовок плейлиста
header = lines[0] if lines and lines[0].startswith("#EXTM3U") else "#EXTM3U"

# 2. Сбор каналов в словарь { "Имя канала": [строки_блока] }
channels_map = {}
i = 0

while i < len(lines):
    line = lines[i]

    if line.startswith("#EXTINF"):
        match = re.match(r'.*,\s*(.+)$', line)
        if match:
            channel_name = match.group(1).strip()
            block = [line]

            # Проверяем #EXTGRP (если есть)
            if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                block.append(lines[i + 1])
                i += 1

            # Проверяем URL (следующая строка)
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                block.append(lines[i + 1])
                i += 1

            channels_map[channel_name] = block

    i += 1

# === Формирование итоговых строк строго по порядку CHANNELS ===
filtered_lines = [header]

for name in CHANNELS:
    if name in channels_map:
        filtered_lines.extend(channels_map[name])

# === Сохранение результата ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_lines))

print(f"✅ Готово. {OUTPUT_FILE} успешно создан и отсортирован по списку.")
