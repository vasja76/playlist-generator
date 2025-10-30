# -*- coding: utf-8 -*-
import os

# === Настройки ===
INPUT_FILE = "playlist3.m3u8"  # Берём уже готовый playlist3
OUTPUT_FILE = "playlist4.m3u8"

# === Список нужных каналов ===
# Редактируйте список здесь
CHANNELS = [
    "Беларусь 24",
    "Беларусь 1",
    "Мега UA",
    "К1 UA",
    "К2 UA",
    "Перший UA",
    "Первый канал",
    "Первый канал +2",
    "Россия 1",
    "Россия 1 +2",
    "ТНТ",
    "ТНТ +2",
    "СТС",
    "СТС +2",
    "Че!",
    "Ностальгия",
    "Ю ТВ",
    "ТНТ4",
    "Ретро",
    "VF Comedy",
    "VF Солдаты",
    "VF Воронины",
    "VF Универ",
    "VF Кухня",
    "VF Michael Jackson",
    "VF Орел и решка",
    "StrahTV Ольга HD",
    "MTV HD",
    "Europa Plus TV",
    "ТНТ Music",
    "Discovery Channel",
    "Animal Planet",
    "Охота и рыбалка",
    "Red Lips",
    "Exxxotica HD",
    "Red TV Russian"
]

# === Проверяем наличие playlist3 ===
if not os.path.isfile(INPUT_FILE):
    print(f"Error: {INPUT_FILE} не найден. Сначала сформируйте playlist3.")
    exit(1)

# === Считываем playlist3 ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

# === Фильтруем нужные каналы ===
filtered_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        parts = line.split(",", 1)
        if len(parts) == 2:
            channel_name = parts[1].strip()
            if channel_name in CHANNELS:
                # Добавляем #EXTINF
                filtered_lines.append(line)
                # Добавляем следующую строку (обычно URL)
                if i + 1 < len(lines):
                    filtered_lines.append(lines[i + 1])
                # Добавляем ещё одну строку, если есть #EXTGRP
                if i + 2 < len(lines) and lines[i + 2].startswith("#EXTGRP"):
                    filtered_lines.append(lines[i + 2])
    i += 1

# === Сохраняем playlist4 ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(filtered_lines))

print(f"Done. {OUTPUT_FILE} успешно сгенерирован из {INPUT_FILE}.")
