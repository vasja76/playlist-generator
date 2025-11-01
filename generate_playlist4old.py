# -*- coding: utf-8 -*-
import os

# === Настройки ===
INPUT_FILE = "playlist3.m3u8"   # Берём готовый playlist3
OUTPUT_FILE = "playlist4.m3u8"

# === Список нужных каналов ===
CHANNELS = [
    "Беларусь 24", "Беларусь 1", "Мега UA", "К1 UA", "К2 UA", "Перший UA",
    "Первый канал", "Первый канал +2", "Россия 1", "Россия 1 +2",
    "ТНТ", "ТНТ +2", "СТС", "СТС +2", "Че!", "Ностальгия",
    "Ю ТВ", "ТНТ4", "Ретро", "VF Comedy", "VF Солдаты", "VF Воронины",
    "VF Универ", "VF Кухня", "VF Michael Jackson", "VF Орел и решка",
    "StrahTV Ольга HD", "Europa Plus TV", "ТНТ Music",
    "Discovery Channel", "Animal Planet", "Охота и рыбалка",
    "Red Lips", "Exxxotica HD", "Red TV Russian", "МУЗ-ТВ", "MTV Hits"
]

# === Проверка существования playlist3 ===
if not os.path.isfile(INPUT_FILE):
    print(f"Error: {INPUT_FILE} не найден. Сначала сформируйте playlist3.")
    exit(1)

# === Чтение playlist3 ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

filtered_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Ищем #EXTINF строки
    if line.startswith("#EXTINF"):
        parts = line.split(",", 1)
        if len(parts) == 2:
            channel_name = parts[1].strip()
            # Сохраняем только выбранные каналы
            if channel_name in CHANNELS:
                # Добавляем #EXTINF
                filtered_lines.append(line)
                # Проверяем, есть ли #EXTGRP
                if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                    filtered_lines.append(lines[i + 1])
                    i += 1
                # Добавляем URL (следующая строка)
                if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                    filtered_lines.append(lines[i + 1])
    else:
        # Сохраняем все строки до первого #EXTINF (например, заголовок #EXTM3U)
        if i == 0 and line.startswith("#EXTM3U"):
            filtered_lines.append(line)
    i += 1

# === Сохраняем playlist4 ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_lines))

print(f"Done. {OUTPUT_FILE} успешно сгенерирован из {INPUT_FILE}.")
