import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

def update_album_tags(root_directory):
    """
    Проходит по всем подпапкам в указанной директории и устанавливает тег 'album'
    для каждого MP3-файла равным имени папки, в которой файл находится.
    """
    for root, dirs, files in os.walk(root_directory):
        # Имя текущей папки, которое будем использовать как название альбома
        folder_name = os.path.basename(root)
        for file in files:
            if file.lower().endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    # Пытаемся загрузить ID3 теги файла
                    audio = EasyID3(file_path)
                except Exception as e:
                    try:
                        # Если теги отсутствуют, создаем их
                        audio = MP3(file_path, ID3=EasyID3)
                        audio.add_tags()
                        audio = EasyID3(file_path)
                    except Exception as e2:
                        print(f"Ошибка обработки файла {file_path}: {e2}")
                        continue

                # Устанавливаем тег 'album' равным имени папки
                audio["album"] = folder_name
                try:
                    audio.save()
                    print(f"Обновлен файл: {file_path} -> альбом: '{folder_name}'")
                except Exception as save_error:
                    print(f"Ошибка сохранения файла {file_path}: {save_error}")

if __name__ == "__main__":
    # Запрашиваем путь к каталогу с музыкой
    music_directory = input("Введите путь к каталогу с музыкой: ").strip()
    if os.path.isdir(music_directory):
        update_album_tags(music_directory)
    else:
        print("Указанный путь не является директорией.")