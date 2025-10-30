import requests
from urllib.parse import urlparse

# === Настройки ===
N_DAYS = 3  # интервал обновления, менять при необходимости
URL_PLAYLIST1 = "http://a6a00836aefe.goodstreem.org/playlists/uplist/0e3bfa31d659f835f335f10165836f6d/playlist.m3u8"
URL_PLAYLIST2 = "http://7d910a3da525.goodstreem.org/playlists/uplist/22825bfdcdb7e2ef359c18b30e40a234/playlist.m3u8"
OUTPUT_FILE = "playlist3.m3u8"

# === Скачиваем плейлист1 ===
print("Downloading playlist1...")
try:
    r1 = requests.get(URL_PLAYLIST1, timeout=15)
    r1.raise_for_status()
except Exception as e:
    print(f"Error downloading playlist1: {e}")
    exit(1)

playlist1_content = r1.text

# === Скачиваем плейлист2 и определяем актуальный сервер ===
print("Downloading playlist2 to get server...")
try:
    r2 = requests.get(URL_PLAYLIST2, timeout=15)
    r2.raise_for_status()
except Exception as e:
    print(f"Error downloading playlist2: {e}")
    exit(1)

lines2 = r2.text.splitlines()
new_server = None

for line in lines2:
    if line.startswith("http://") or line.startswith("https://"):
        parsed = urlparse(line)
        new_server = f"{parsed.scheme}://{parsed.netloc}/"
        break

if not new_server:
    print("Error: Could not find a valid server in playlist2")
    exit(1)

print("New server from playlist2:", new_server)

# === Определяем старый сервер в плейлисте1 ===
old_server = None
for line in playlist1_content.splitlines():
    if line.startswith("http://") or line.startswith("https://"):
        parsed = urlparse(line)
        old_server = f"{parsed.scheme}://{parsed.netloc}/"
        break

if not old_server:
    print("Error: Could not find a valid server in playlist1")
    exit(1)

print("Old server from playlist1:", old_server)

# === Заменяем сервер ===
print("Replacing old server with new server...")
updated_content = playlist1_content.replace(old_server, new_server)

# === Сохраняем playlist3 ===
print(f"Saving updated playlist to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Done. Playlist3 generated successfully.")
