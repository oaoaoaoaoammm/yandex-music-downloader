# Как использовать?
1. скачиваете папку [code](https://github.com/oaoaoaoaoammm/yandex-music-downloader/tree/main/code)
2. открываете браузер и логинитесь на [яндекс музыке](https://music.yandex.ru/home)
3. устанавливаете расширение, чтобы получить OAuth токен(я не нашел в консоли, возможно вы подскажите как. сторонний плагин - стрем, согласен) - https://chromewebstore.google.com/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib
4. копируете токен из расширения и вставляете в [TOKEN = ""](https://github.com/oaoaoaoaoammm/yandex-music-downloader/blob/main/code/main.py#L10)
5. запускаете и скачиваете треки из плейлистов

## Нюансы
1. цикл while(True) не добавлял
2. как раз первый пункт не сделал, потому что реализовал:
```python
urls = ["playlist link 1","playlist link 2"]
for raw_url in urls:
```
вместо 
```python 
raw_url = input("🔗 Вставьте ссылку на плейлист Яндекс.Музыки: ").strip()
```
