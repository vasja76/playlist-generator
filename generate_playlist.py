#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_playlist.py

Назначение:
    Формирует итоговый файл playlist3.m3u8.

Логика работы:
    1. Основа каналов берётся из URL_PLAYLIST1
    2. Серверная часть URL может браться:
        - либо из URL_PLAYLIST2 (SERVER_SOURCE = 1)
        - либо из пользовательского домена USER_DOMAIN (SERVER_SOURCE = 2)

Логика fallback для SERVER_SOURCE = 1:
    1. Пытаемся скачать playlist2
    2. Если не удалось — используем локальный кэш
    3. Если и кэша нет — используем последний известный рабочий сервер
       для playlist3

Особенности:
    - При USER_DOMAIN меняется только основная доменная часть,
      а субдомен сохраняется:
        было: riusiepq.alfalt.fun
        стало: riusiepq.akadatel.com

Важно:
    - FALLBACK_SERVER_HOST должен быть именно рабочим сервером,
      который уже использовался в удачном playlist3,
      а НЕ доменом из playlist1.

Автор: ChatGPT
"""

import os
import sys
import requests
from urllib.parse import urlparse

# =========================================================
# НАСТРОЙКИ
# =========================================================

# Основной плейлист (отсюда берём каналы)
URL_PLAYLIST1 = "https://example.com/playlist1.m3u8"

# Донор серверной части (отсюда берём рабочий сервер, если SERVER_SOURCE = 1)
URL_PLAYLIST2 = "https://example.com/playlist2.m3u8"

# Переключатель источника сервера:
# 1 = брать сервер из playlist2 (с fallback)
# 2 = брать пользовательский домен USER_DOMAIN
SERVER_SOURCE = 1

# Пользовательский домен (если SERVER_SOURCE = 2)
# Важно: заменяется только основная доменная часть,
# а субдомен сохраняется
USER_DOMAIN = "akadatel.com"

# Последний известный рабочий сервер для playlist3
# Используется ТОЛЬКО если:
#   - playlist2 не скачался
#   - кэш отсутствует или битый
#
# ВАЖНО:
#   Это должен быть НЕ домен из playlist1,
#   а именно рабочий сервер из последнего удачного playlist3.
FALLBACK_SERVER_HOST = "riusiepq.siauliairsavlt.com"

# Итоговый выходной файл
OUTPUT_FILE = "playlist3.m3u8"

# Кэш для playlist2
CACHE_FILE = "playlist2_cache.m3u8"

# Таймаут запросов (сек)
REQUEST_TIMEOUT = 20

# User-Agent для запросов
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; playlist-generator/1.0)"
}


# =========================================================
# СЛУЖЕБНЫЕ ФУНКЦИИ
# =========================================================

def log(message: str) -> None:
    """Красивый вывод в консоль GitHub Actions / локального запуска."""
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    """Вывод предупреждения."""
    print(f"[WARN] {message}")


def error(message: str) -> None:
    """Вывод ошибки."""
    print(f"[ERROR] {message}", file=sys.stderr)


def download_text(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    """
    Скачивает текст по URL и возвращает содержимое.

    Если ответ не 200 или тело пустое — бросает исключение.
    """
    log(f"Скачивание: {url}")
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()

    text = response.text.strip()
    if not text:
        raise ValueError(f"Пустой ответ от: {url}")

    return text


def save_text_to_file(filepath: str, text: str) -> None:
    """Сохраняет текст в файл UTF-8."""
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def load_text_from_file(filepath: str) -> str:
    """Читает текст из файла UTF-8."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def is_valid_m3u(text: str) -> bool:
    """
    Простая проверка, что это похоже на M3U-плейлист.
    """
    if not text or "#EXTM3U" not in text:
        return False

    if "#EXTINF" not in text:
        return False

    return True


def fetch_playlist2_with_fallback(url: str, cache_file: str) -> str | None:
    """
    Получает playlist2 с fallback на кэш.

    Возвращает:
        - текст playlist2, если удалось взять онлайн
        - текст кэша, если онлайн недоступен
        - None, если не удалось получить ни онлайн, ни кэш

    Важно:
        Если вернулся None — вызывающий код должен использовать
        FALLBACK_SERVER_HOST.
    """

    # ---------------------------------------------------------
    # 1. Пытаемся скачать актуальный playlist2
    # ---------------------------------------------------------
    try:
        playlist2_text = download_text(url)

        if not is_valid_m3u(playlist2_text):
            raise ValueError("playlist2 скачан, но не похож на корректный M3U")

        # Сохраняем свежую рабочую копию в кэш
        save_text_to_file(cache_file, playlist2_text)
        log(f"playlist2 успешно скачан и сохранён в кэш: {cache_file}")

        return playlist2_text

    except Exception as e:
        warn(f"Не удалось скачать playlist2: {e}")

    # ---------------------------------------------------------
    # 2. Пытаемся использовать кэш
    # ---------------------------------------------------------
    if os.path.exists(cache_file):
        try:
            cached_text = load_text_from_file(cache_file)

            if not is_valid_m3u(cached_text):
                raise ValueError("Кэш-файл найден, но невалидный")

            log(f"Используется fallback-кэш: {cache_file}")
            return cached_text

        except Exception as e:
            warn(f"Не удалось прочитать кэш playlist2: {e}")

    # ---------------------------------------------------------
    # 3. Не удалось ни онлайн, ни кэш
    # ---------------------------------------------------------
    warn("Не удалось получить playlist2 ни онлайн, ни из кэша")
    return None


def extract_first_stream_url(m3u_text: str) -> str:
    """
    Извлекает первый URL потока из M3U-плейлиста.

    Берём первую строку после служебных #EXT...,
    которая начинается с http/https.
    """
    for line in m3u_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("http://") or line.startswith("https://"):
            return line

    raise ValueError("Не удалось найти потоковый URL в плейлисте")


def extract_host_from_url(url: str) -> str:
    """
    Возвращает host из URL.

    Пример:
        https://riusiepq.alfalt.fun/live/123
        -> riusiepq.alfalt.fun
    """
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Не удалось извлечь host из URL: {url}")
    return parsed.netloc


def build_new_host_from_user_domain(original_host: str, user_domain: str) -> str:
    """
    Меняет только основную доменную часть, сохраняя субдомен.

    Пример:
        original_host = riusiepq.alfalt.fun
        user_domain   = akadatel.com

        результат -> riusiepq.akadatel.com

    Логика:
        - если есть субдомен(ы), сохраняем всё до последних двух частей
        - последние 2 части заменяем на user_domain
    """
    original_parts = original_host.split(".")
    user_parts = user_domain.split(".")

    if len(user_parts) < 2:
        raise ValueError(f"USER_DOMAIN выглядит некорректно: {user_domain}")

    # Если хост совсем простой
    if len(original_parts) <= 2:
        return user_domain

    # Сохраняем всё, что было "слева" от основной доменной зоны
    subdomain_parts = original_parts[:-2]

    new_parts = subdomain_parts + user_parts
    return ".".join(new_parts)


def replace_host_in_url(url: str, new_host: str) -> str:
    """
    Заменяет host в URL на новый, сохраняя:
        - схему (http/https)
        - путь
        - query
        - fragment
    """
    parsed = urlparse(url)
    if not parsed.netloc:
        return url

    return parsed._replace(netloc=new_host).geturl()


def get_server_host_from_playlist2(playlist2_text: str) -> str:
    """
    Извлекает host сервера из playlist2.
    """
    sample_url = extract_first_stream_url(playlist2_text)
    host = extract_host_from_url(sample_url)
    log(f"Из playlist2 извлечён сервер: {host}")
    return host


def get_final_server_host(server_source: int) -> str:
    """
    Определяет, какой host использовать для итогового playlist3.

    Возвращает:
        - host из playlist2 / кэша / fallback
        - либо спецмаркер "__USER_DOMAIN_MODE__"
    """
    if server_source == 1:
        playlist2_text = fetch_playlist2_with_fallback(URL_PLAYLIST2, CACHE_FILE)

        # Если удалось взять playlist2 онлайн или из кэша
        if playlist2_text:
            try:
                return get_server_host_from_playlist2(playlist2_text)
            except Exception as e:
                warn(f"Не удалось извлечь host из playlist2: {e}")

        # Если вообще всё провалилось — используем последний рабочий сервер
        warn(f"Используется аварийный fallback-host: {FALLBACK_SERVER_HOST}")
        return FALLBACK_SERVER_HOST

    elif server_source == 2:
        # Для пользовательского домена host нельзя вернуть "в лоб",
        # потому что субдомен должен сохраняться индивидуально для каждого URL.
        return "__USER_DOMAIN_MODE__"

    else:
        raise ValueError("SERVER_SOURCE должен быть только 1 или 2")


def transform_playlist1(playlist1_text: str, server_source: int) -> str:
    """
    Преобразует playlist1 в playlist3:
        - если SERVER_SOURCE = 1:
            заменяет host каждого URL на host из playlist2 / кэша / fallback
        - если SERVER_SOURCE = 2:
            заменяет только основную доменную часть,
            сохраняя исходный субдомен
    """
    final_host = get_final_server_host(server_source)
    output_lines = []

    for line in playlist1_text.splitlines():
        stripped = line.strip()

        # Пустые строки оставляем как есть
        if not stripped:
            output_lines.append(line)
            continue

        # Служебные строки не трогаем
        if stripped.startswith("#"):
            output_lines.append(line)
            continue

        # Меняем только URL-строки
        if stripped.startswith("http://") or stripped.startswith("https://"):
            try:
                original_host = extract_host_from_url(stripped)

                if server_source == 1:
                    # Полная замена host на тот, что определён логикой fallback
                    new_url = replace_host_in_url(stripped, final_host)

                elif server_source == 2:
                    # Сохраняем субдомен, меняем только основную доменную часть
                    new_host = build_new_host_from_user_domain(original_host, USER_DOMAIN)
                    new_url = replace_host_in_url(stripped, new_host)

                else:
                    raise ValueError("SERVER_SOURCE должен быть только 1 или 2")

                output_lines.append(new_url)

            except Exception as e:
                error(f"Не удалось обработать URL: {stripped}")
                error(f"Причина: {e}")
                output_lines.append(line)

        else:
            # Любые прочие строки оставляем как есть
            output_lines.append(line)

    return "\n".join(output_lines) + "\n"


# =========================================================
# ОСНОВНАЯ ЛОГИКА
# =========================================================

def main():
    try:
        log("Запуск генерации playlist3...")

        # 1. Скачиваем основу
        playlist1_text = download_text(URL_PLAYLIST1)

        if not is_valid_m3u(playlist1_text):
            raise RuntimeError("playlist1 не похож на корректный M3U")

        log("playlist1 успешно загружен")

        # 2. Преобразуем
        result_text = transform_playlist1(playlist1_text, SERVER_SOURCE)

        # 3. Сохраняем
        save_text_to_file(OUTPUT_FILE, result_text)

        log(f"Готово: создан файл {OUTPUT_FILE}")

    except Exception as e:
        error(f"Скрипт завершился с ошибкой: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
