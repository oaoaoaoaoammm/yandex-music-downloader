import yt_dlp
import os
import sys
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON

def clean_yandex_music_url(url):
    """Очищает URL, удаляя UTM-метки."""
    try:
        return url.split("?")[0] if "?" in url else url
    except Exception as e:
        print(f"❌ Ошибка при обработке ссылки: {e}")
        sys.exit(1)

def get_playlist_info(url):
    """Получает название плейлиста и список треков (используя yt-dlp)."""
    try:
        ydl_opts = {'quiet': True, 'force_generic_extractor': False}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("title", "Unknown_Playlist"), info.get("entries", [])
    except yt_dlp.utils.DownloadError:
        print("❌ Ошибка: плейлист недоступен или ссылка неверная.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при получении информации о плейлисте: {e}")
        sys.exit(1)

def download_track(track, base_folder):
    """Скачивает один трек и сортирует по жанрам."""
    try:
        title = track.get("title", "Unknown_Title")
        artist = track.get("artist", "Unknown_Artist")
        album = track.get("album", "Unknown_Album")
        genres = track.get("genre", ["Unknown_Genre"])
        cover_url = track.get("thumbnail")

        # Если жанры отсутствуют, записываем в "Unknown_Genre"
        if not genres:
            genres = ["Unknown_Genre"]

        for genre in genres:
            genre_folder = os.path.join(base_folder, genre)
            os.makedirs(genre_folder, exist_ok=True)
            file_path = os.path.join(genre_folder, f"{artist} - {title}.mp3")

            # yt-dlp параметры
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': file_path,
                'noplaylist': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }

            # Скачивание
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([track["webpage_url"]])

            # Добавление обложки и тегов
            if os.path.exists(file_path):
                update_mp3_metadata(file_path, title, artist, album, genre, cover_url)

            print(f"✅ {title} ({genre}) загружен!")

    except Exception as e:
        print(f"❌ Ошибка при скачивании трека {track.get('title', 'Unknown')}: {e}")

def update_mp3_metadata(file_path, title, artist, album, genre, cover_url):
    """Добавляет метаданные (исполнитель, альбом, жанр) и обложку в MP3."""
    try:
        audio = MP3(file_path, ID3=ID3)

        # Добавляем ID3 теги, если их нет
        if audio.tags is None:
            audio.tags = ID3()

        audio.tags.add(TIT2(encoding=3, text=title))  # Название трека
        audio.tags.add(TPE1(encoding=3, text=artist))  # Исполнитель
        audio.tags.add(TALB(encoding=3, text=album))  # Альбом
        audio.tags.add(TCON(encoding=3, text=genre))  # Жанр

        # Если есть обложка – загружаем и добавляем в MP3
        if cover_url:
            response = requests.get(cover_url)
            if response.status_code == 200:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=response.content
                ))
                print("🖼 Обложка добавлена!")

        # Сохраняем изменения
        audio.save()
    except Exception as e:
        print(f"❌ Ошибка при обновлении метаданных: {e}")

if __name__ == "__main__":
    try:
        # Запрос ссылки от пользователя
        raw_url = input("🔗 Вставьте ссылку на плейлист Яндекс.Музыки: ").strip()
        if not raw_url:
            raise ValueError("Ссылка не может быть пустой.")

        # Очищаем ссылку
        playlist_url = clean_yandex_music_url(raw_url)
        print(f"✅ Очищенная ссылка: {playlist_url}")

        # Получаем информацию о плейлисте
        playlist_name, tracks = get_playlist_info(playlist_url)
        print(f"🎵 Название плейлиста: {playlist_name}")
        print(f"📥 Найдено треков: {len(tracks)}")

        # Основная папка загрузки
        save_path = f"downloads/{playlist_name}"
        os.makedirs(save_path, exist_ok=True)

        # Скачиваем каждый трек с сортировкой по жанрам
        for track in tracks:
            download_track(track, save_path)

        print(f"✅ Все треки из плейлиста «{playlist_name}» загружены! 🎶")

    except ValueError as e:
        print(f"❌ Ошибка ввода: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🚪 Программа прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)
