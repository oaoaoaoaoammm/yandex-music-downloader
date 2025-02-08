import os
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def copy_to_author_structure(source_file_path, file_name, artist):
    """
    Копирует трек в структуру: ./author/<имя автора>/.
    Если нужная папка отсутствует, она создаётся.
    """
    try:
        # Заменяем недопустимые символы в имени автора
        artist_sanitized = "".join(c for c in artist if c.isalnum() or c in (' ', '_')).strip()
        dest_folder = os.path.join("./author/", artist_sanitized)
        os.makedirs(dest_folder, exist_ok=True)
        dest_file_path = os.path.join(dest_folder, file_name)
        shutil.copy2(source_file_path, dest_file_path)
        print(f"📂 Трек скопирован в структуру авторов: {dest_file_path}")
    except Exception as e:
        print(f"❌ Ошибка при копировании в структуру авторов: {e}")


def process_mp3_files(base_folder):
    """
    Рекурсивно обходит папки, находит .mp3 файлы, извлекает имя исполнителя и
    копирует файлы в структуру ./author/<имя автора>/.
    """
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    # Читаем метаданные файла
                    audio = MP3(file_path, ID3=ID3)
                    if audio.tags is None or "TPE1" not in audio.tags:
                        print(f"⚠️ Пропущен файл без информации об исполнителе: {file_path}")
                        continue

                    # Извлекаем имя исполнителя
                    artist = audio.tags["TPE1"].text[0] if isinstance(audio.tags["TPE1"].text, list) else audio.tags["TPE1"].text
                    copy_to_author_structure(file_path, file, artist)
                except Exception as e:
                    print(f"❌ Ошибка при обработке файла {file_path}: {e}")


if __name__ == "__main__":
    base_folder = input("🗂 Укажите путь к папке для сортировки файлов: ").strip()
    if not os.path.isdir(base_folder):
        print(f"❌ Указанная папка не существует: {base_folder}")
    else:
        process_mp3_files(base_folder)
        print("✅ Сортировка завершена!")