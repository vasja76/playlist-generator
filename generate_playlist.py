import requests

# === Настройки ===
N_DAYS = 3  # интервал обновления в днях, можно менять
URL_PLAYLIST1 = "http://a6a00836aefe.goodstreem.org/playlists/uplist/0e3bfa31d659f835f335f10165836f6d/playlist.m3u8"
OLD_SERVER = "http://riusiepq.alfalt.fun/"
NEW_SERVER = "http://riusiepq.siauliairsavlt.com/"
OUTPUT_FILE = "playlist3.m3u8"

# === Основная логика ===
print("Downloading playlist1...")
try:
    r = requests.get(URL_PLAYLIST1, timeout=15)
    r.raise_for_status()
except Exception as e:
    print(f"Error downloading playlist1: {e}")
    exit(1)

content = r.text

print("Replacing server URLs...")
content = content.replace(OLD_SERVER, NEW_SERVER)

print(f"Saving updated playlist to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Playlist3 generated successfully.")
