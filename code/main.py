import os
import sys
import requests
import shutil
from yandex_music import Client
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TLAN

# 🔑 Вставьте свой OAuth-токен
TOKEN = ""

# Авторизация в API Яндекс.Музыки
client = Client(TOKEN).init()


def get_playlist_info(user_id, playlist_id):
    """
    Получает информацию о плейлисте (название и список треков)
    через метод client.users_playlist(user_id, playlist_id).
    """
    try:
        playlist = client.users_playlists(playlist_id, user_id)
        return playlist.title, playlist.tracks
    except Exception as e:
        print(f"❌ Ошибка при получении плейлиста: {e}")
        sys.exit(1)


def download_track(track, playlist_base_folder):
    """
    Скачивает трек и сохраняет его в папке плейлиста (без вложенной папки для категории).
    После этого обновляет метаданные и копирует файл в две дополнительные структуры:
      1. В структуру языка+категории: ./<язык>/<категория>/
      2. В структуру категории: ./<категория>/
    Все данные (язык, категория) берутся из метаданных трека.
    """
    title = "Unknown Title"
    try:
        # Получаем полную информацию о треке
        track_obj = track.fetch_track()
        title = track_obj.title
        artist = ", ".join([a.name for a in track_obj.artists])
        album = track_obj.albums[0].title if track_obj.albums else "Unknown Album"
        genre = (track_obj.albums[0].genre
                 if track_obj.albums and track_obj.albums[0].genre
                 else "Unknown Genre")
        cover_url = (track_obj.cover_uri.replace("%%", "200x200")
                     if track_obj.cover_uri else None)

        # Берём язык из метаданных (если отсутствует – "Unknown")
        language = track_obj.language if hasattr(track_obj, "language") and track_obj.language else "Unknown"

        # Обеспечиваем, что папка плейлиста существует
        os.makedirs(playlist_base_folder, exist_ok=True)

        # Формируем имя файла и путь для сохранения (файл сохраняется прямо в папке плейлиста)
        file_name = f"{artist} - {title}.mp3"
        file_path = os.path.join(playlist_base_folder, file_name)
        if os.path.exists(file_path):
            print(f"🔄 Трек уже существует: {file_path}, перезаписываем...")

        # Скачивание трека с нужным битрейтом
        track_obj.download(file_path, bitrate_in_kbps=320)
        print(f"✅ {title} загружен в плейлист!")

        # Обновление метаданных (название, исполнитель, альбом, жанр, язык и обложка)
        update_mp3_metadata(file_path, title, artist, album, genre, language, cover_url)

        # Копирование в структуру языка + категории: ./<язык>/<категория>/
        copy_to_language_structure(file_path, file_name, language, genre)

        # Копирование в структуру категории: ./<категория>/
        copy_to_category_structure(file_path, file_name, genre)

    except Exception as e:
        print(f"❌ Ошибка при скачивании трека {title}: {e}")


def update_mp3_metadata(file_path, title, artist, album, genre, language, cover_url):
    """
    Обновляет ID3-теги MP3-файла: название, исполнитель, альбом, жанр и язык (TLAN).
    Если указан URL обложки, пытается его загрузить и добавить в теги.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        audio.tags.add(TCON(encoding=3, text=genre))
        audio.tags.add(TLAN(encoding=3, text=language))

        if cover_url:
            # Если URL начинается с "https:" но нет двойных слэшей, корректируем его
            if cover_url.startswith("https:") and not cover_url.startswith("https://"):
                cover_url = "https://" + cover_url[len("https:"):].lstrip('/')
            elif not (cover_url.startswith("http://") or cover_url.startswith("https://")):
                cover_url = "https://" + cover_url.lstrip('/')
            response = requests.get(cover_url)
            if response.status_code == 200:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # обложка (front cover)
                    desc='Cover',
                    data=response.content
                ))
                print("🖼 Обложка добавлена!")
            else:
                print(f"❌ Не удалось загрузить обложку. HTTP статус: {response.status_code}")

        audio.save()
    except Exception as e:
        print(f"❌ Ошибка при обновлении метаданных: {e}")


def copy_to_language_structure(source_file_path, file_name, language, genre):
    """
    Копирует скачанный трек в структуру: ./<язык>/<категория>/.
    Если нужные каталоги отсутствуют, они создаются.
    """
    try:
        dest_folder = os.path.join(".", language, genre)
        os.makedirs(dest_folder, exist_ok=True)
        dest_file_path = os.path.join(dest_folder, file_name)
        shutil.copy2(source_file_path, dest_file_path)
        print(f"📂 Трек скопирован в языковую структуру: {dest_file_path}")
    except Exception as e:
        print(f"❌ Ошибка при копировании в языковую структуру: {e}")


def copy_to_category_structure(source_file_path, file_name, genre):
    """
    Копирует скачанный трек в структуру: ./<категория>/.
    Если нужная папка отсутствует, она создаётся.
    """
    try:
        dest_folder = os.path.join(".", genre)
        os.makedirs(dest_folder, exist_ok=True)
        dest_file_path = os.path.join(dest_folder, file_name)
        shutil.copy2(source_file_path, dest_file_path)
        print(f"📂 Трек скопирован в категорийную структуру: {dest_file_path}")
    except Exception as e:
        print(f"❌ Ошибка при копировании в категорийную структуру: {e}")


if __name__ == "__main__":
    try:
        raw_url = input("🔗 Вставьте ссылку на плейлист Яндекс.Музыки: ").strip()
        if not raw_url:
            raise ValueError("Ссылка не может быть пустой.")

        # Ожидаемый формат URL:
        # https://music.yandex.ru/users/<user_id>/playlists/<playlist_id>?...
        parts = raw_url.split("/")
        if len(parts) < 2:
            raise ValueError("Некорректная ссылка.")

        # Извлекаем user_id и playlist_id (обычно user_id находится перед "playlists")
        user_id = parts[-3]
        playlist_id = parts[-1].split("?")[0]

        # Получаем название плейлиста и список треков
        playlist_name, tracks = get_playlist_info(user_id, playlist_id)
        print(f"🎵 Название плейлиста: {playlist_name}")
        print(f"📥 Найдено треков: {len(tracks)}")

        # Создаём папку для плейлиста (например, "./Mood: Αγάπη")
        playlist_folder = os.path.join(".", playlist_name)
        os.makedirs(playlist_folder, exist_ok=True)

        # Скачиваем каждый трек из плейлиста
        for track in tracks:
            download_track(track, playlist_folder)

        print(f"✅ Все треки из плейлиста «{playlist_name}» загружены!")
    except ValueError as e:
        print(f"❌ Ошибка ввода: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🚪 Программа прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)