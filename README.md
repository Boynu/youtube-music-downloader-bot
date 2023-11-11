# youtube-music-downloader-bot Ниже на русском языке

https://t.me/YM_Download_bot

This code is a bot for downloading music from YouTube, written in Python. It uses the `aiogram` library for Telegram bot functionality and `pytube' for downloading videos and playlists from YouTube. The downloaded music is saved in MP3 format and can be accessed via the bot.
## Pre-setup

Before running the code, make sure that you have the following dependencies installed:

- `aiogram`
- `pytube`
- `eyed3`
- `ffmpeg`
- `youtube-search-python`

You can install these dependencies using `pip`:

```bash
pip install aiogram pytube eyed3 youtube-search-python
```

`ffmpeg` is required to convert downloaded videos to MP3 format. You can install it by following the instructions for your operating system.

## Setup

1. Clone the repository or upload the code files.

2. Create a new Telegram bot and get its API token. You can do this by contacting BotFather on Telegram.

3. Open the code file and replace the `token` variable with your Telegram bot API token:

   ```python
   token = 'YOUR_TOKEN'
   ```

4. Run the code using the Python interpreter:

   ```bash
   python main.py
   ```

## Usage

1. Start a dialogue with the bot by sending the command `/start'.
2. You can send a link to a song or playlist from YouTube, and the bot will download them for you.
3. The following commands are available to manage playlists:
   - `/get` - show all downloaded songs and playlists.
   - `/clear` - delete all songs from the playlist.
   - `/create` - create a new playlist.
   - `/del` - delete playlist.
   - `/search` - find a song on YouTube

4. To create a new playlist, enter the command `/create` or click "➕Create a new playlist" and follow the bot's instructions.
5. To get a list of songs from the playlist, use the `/get` command or click "📂Show all downloaded music" and select a playlist.
6. To delete a playlist, use the `/del` command and select the playlist to delete.
7. To clear the playlist, use the `/clear` command and select the playlist to clear.
8. You can send the `/help` command to get help on the available commands.

## Notes

- Uploaded songs are saved in a directory with the name of the user's chat ID. After sending them to the user, they are deleted from the local server. The file ID is stored in the file `ids.txt ` or there may be another name for your playlist.
- The bot uses SQLite to store user information, including the chat ID and username.
- The `eyed3` library is used to add metadata (song name and artist) to downloaded MP3 files.
- The `ffmpeg` utility is used to convert downloaded videos to MP3 format.

Feel free to customize the code according to your requirements or add additional features to the bot. Enjoy downloading and listening to your favorite music!

# youtube-music-downloader-bot На русском языке

https://t.me/YM_Download_bot

Данный код представляет собой бота для загрузки музыки из Ютуба, написанного на Python. Он использует библиотеку `aiogram` для функциональности Telegram-бота и `pytube` для загрузки видео и плейлистов с YouTube. Загруженная музыка сохраняется в формате MP3 и может быть доступна через бота.

## Предварительная настройка

Перед запуском кода убедитесь, что у вас установлены следующие зависимости:

- `aiogram`
- `pytube`
- `eyed3`
- `ffmpeg`
- `youtube-search-python`

Вы можете установить эти зависимости с помощью `pip`:

```bash
pip install aiogram pytube eyed3 youtube-search-python
```

`ffmpeg` необходим для конвертации загруженных видео в формат MP3. Вы можете установить его, следуя инструкциям для вашей операционной системы.

## Настройка

1. Клонируйте репозиторий или загрузите файлы кода.

2. Создайте нового Telegram-бота и получите его API-токен. Вы можете сделать это, обратившись к BotFather в Telegram.

3. Откройте файл с кодом и замените переменную `token` на свой API-токен Telegram-бота:

   ```python
   token = 'ВАШ_ТОКЕН'
   ```

4. Запустите код с помощью интерпретатора Python:

   ```bash
   python main.py
   ```

## Использование

1. Начните диалог с ботом, отправив команду `/start`.
2. Вы можете отправить ссылку на песню или плейлист из YouTube, и бот загрузит их для вас.
3. Для управления плейлистами доступны следующие команды:
   - `/get` - показать все скаченные песни и плейлисты.
   - `/clear` - удалить все песни из плейлиста.
   - `/create` - создать новый плейлист.
   - `/del` - удалить плейлист.
   - `/search` - поиск музыки в Ютубе.
   
4. Для создания нового плейлиста введите команду `/create` или нажмите кнопку "➕Создать новый плейлист" и следуйте инструкциям бота.
5. Для получения списка песен из плейлиста используйте команду `/get` или нажмите кнопку "📂Показать всю скаченную музыку" и выберите плейлист.
6. Для удаления плейлиста используйте команду `/del` и выберите плейлист для удаления.
7. Для очистки плейлиста используйте команду `/clear` и выберите плейлист для очистки.
8. Вы можете отправить команду `/help`, чтобы получить справку по доступным командам.

## Примечания

- Загруженные песни сохраняются в каталоге с именем идентификатора чата пользователя. После отправки пользователю, они удаляются с локального сервера. ID файла храниться в файле `ids.txt` или может быть другое название для вашего плейлиста.
- Бот использует SQLite для хранения информации о пользователях, включая идентификатор чата и имя пользователя.
- Библиотека `eyed3` используется для добавления метаданных (названия песни и исполнителя) в загруженные файлы MP3.
- Утилита `ffmpeg` используется для конвертации загруженных видео в формат MP3.

Не стесняйтесь настраивать код в соответствии с вашими требованиями или добавлять дополнительные функции в бота. Наслаждайтесь загрузкой и прослушиванием любимой музыки!
