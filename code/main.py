import yt_dlp
import os
import sys

def clean_yandex_music_url(url):
    """Очищает URL, удаляя UTM-метки и оставляя только нужную часть."""
    try:
        if "?" in url:
            url = url.split("?")[0]  # Убираем UTM-метки
        return url
    except Exception as e:
        print(f"❌ Ошибка при обработке ссылки: {e}")
        sys.exit(1)  # Завершаем программу с ошибкой

def get_playlist_name(url):
    """Извлекает название плейлиста."""
    try:
        ydl_opts = {'quiet': True, 'force_generic_extractor': False}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("title", "Unknown_Playlist")  # Если не удастся получить название
    except yt_dlp.utils.DownloadError:
        print("❌ Ошибка: плейлист недоступен или ссылка неверная.")
        sys.exit(1)  # Завершаем программу с ошибкой
    except Exception as e:
        print(f"❌ Ошибка при получении названия плейлиста: {e}")
        sys.exit(1)

def download_playlist(url, save_folder):
    """Скачивает все треки из плейлиста в указанную папку."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{save_folder}/%(title)s.%(ext)s',
            'noplaylist': False,
            'socket_timeout': 10,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }, {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }, {
                'key': 'FFmpegMetadata',
            }],
        }

        # Запускаем скачивание
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except yt_dlp.utils.DownloadError as e:
        print(f"❌ Ошибка загрузки: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    while(True):
        try:
            # Просим пользователя ввести ссылку
            raw_url = input("🔗 Вставьте ссылку на плейлист Яндекс.Музыки: ").strip()
            if not raw_url:
                raise ValueError("Ссылка не может быть пустой.")

            # Очищаем ссылку
            playlist_url = clean_yandex_music_url(raw_url)
            print(f"✅ Очищенная ссылка: {playlist_url}")

            # Получаем название плейлиста
            playlist_name = get_playlist_name(playlist_url)
            print(f"🎵 Название плейлиста: {playlist_name}")

            # Создаем папку для скачивания
            save_path = f"./{playlist_name}"
            os.makedirs(save_path, exist_ok=True)

            # Скачиваем плейлист
            print(f"📥 Начинаем скачивание в папку: {save_path}")
            download_playlist(playlist_url, save_path)

            print(f"✅ Все треки из плейлиста «{playlist_name}» загружены в {save_path} 🎶")

        except ValueError as e:
            print(f"❌ Ошибка ввода: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n🚪 Программа прервана пользователем.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")
            sys.exit(1)
