import sqlite3, datetime, asyncio, logging, os, eyed3, subprocess
from pytube import YouTube
from pytube import Playlist

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import RestrictChatMember
from aiogram.types import ChatActions
from aiogram.utils.markdown import hlink

token = ''

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

'''
class go(StatesGroup):
	newlist = State()
'''
global connect
connect = sqlite3.connect('users.db', check_same_thread=False)
global cursor
cursor= connect.cursor()

@dp.message_handler()
async def start(message: types.Message,state: FSMContext):
	userid = message.chat.id
	if message.text == '/start':
		today = datetime.datetime.today()
		f = 'Старт '+ str(message.chat.id) + ' ' + today.strftime("%Y-%m-%d-%H.%M.%S")
		print(f)
		
		cursor.execute("""CREATE TABLE IF NOT EXISTS users(
				id INTEGER, username TEXT
			)""")
		connect.commit()

		cursor.execute(f"SELECT * FROM users WHERE id = {userid}")
		data = cursor.fetchone()
		if data is None:
			cursor.execute("INSERT INTO users(id, username) VALUES(?,?);", (message.chat.id, message.chat.username,))
			connect.commit()
			os.mkdir(str(userid))
			with open(f'{userid}/ids.txt', 'w') as file:
				pass

		await mainmenu(message, state)


	elif 'youtube' in message.text:
		await check(message, message.text, state)
	elif message.text == '📂Показать всю скаченную музыку' or message.text == '/get':
		await bot.send_message(message.chat.id,'⚠️Внимание, вы получите список всех песен которые когда либо скачивали в этом боте.\nЕсли вы хотите использовать этого бота для прослушивания музыки, то нажмите на кнопку <i>"🧹Очистить историю чата"</i> и отправьте боту это: \n\n<code>1!</code>','HTML')
	elif message.text == '1!':
		with open(f'{userid}/ids.txt') as file:
			ids = file.read()
		ids = ids.split(' ')
		del ids[-1]
		for idd in ids:
			await bot.send_audio(message.chat.id, audio=idd)
	elif message.text == '/clear':
		with open(f'{userid}/ids.txt', 'w') as file:
			file.write('')
		await bot.send_message(message.chat.id, '✅Все песни удаленны!')
	elif message.text == '/help':
		await bot.send_message(message.chat.id, '📰Справка:\n\n/start - Запустить бота\n/get - Все скаченные песни\n/clear - Удалить все песни')
async def mainmenu(message, state):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(types.KeyboardButton('📂Показать всю скаченную музыку'))
	userid = message.chat.id
	text = '🎵🔗Отправьте ссылку на музыку или плейлист (Из youtube.com или music.youtube.com)\n\n📰Справка /help'
	await bot.send_message(message.chat.id, text, reply_markup=markup)

async def check(message, url, state):
	userid = message.chat.id
	if 'playlist' in url:
		await plalist(url, str(userid), message)
	else:
		try:
			await download(url, str(userid), message)
		except:
			await bot.send_message(message.chat.id,'❌Ошибка')


def matadata(path,name,author):
	audio_file = eyed3.load(path)
	audio_file.tag.title = name#['Song']
	audio_file.tag.artist = author
	audio_file.tag.save()

def convert(mp4,mp3):
	command = ['ffmpeg', '-fflags', '+genpts','-i', mp4, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', mp3]
	subprocess.run(command)

async def download(url, name, message):
	userid = message.chat.id
	try:
		video = YouTube(url)
		start_d = await bot.send_message(message.chat.id, f'💾Началось скачивание <i>{video.title}</i>', 'HTML')
		audio = video.streams.filter(only_audio = True).first()
		name_path = audio.download(name+'/')
		mp3 = f"{name}/{video.title}.mp3"
		convert(name_path, mp3)
		matadata(f"{name}/{video.title}.mp3",video.title,video.author)
		file = await bot.send_audio(message.chat.id,audio=open(f"{name}/{video.title}.mp3", 'rb'))
		file_id = file.audio.file_id
		with open(f'{userid}/ids.txt', 'a') as file:
			file.write(file_id+' ')
		os.remove(name_path)
		os.remove(f"{name}/{video.title}.mp3")
	except:
		raise ValueError('Ошибка')
	await start_d.delete()

async def plalist(url, name, message):
	p = Playlist(url)
	text = f'📥Скачивание плейлиста <i>{p.title}</i>'
	await bot.send_message(message.chat.id, text, 'HTML')
	for file in p.video_urls:
		try:
			await download(file, name, message)
		except ValueError:
			await bot.send_message(message.chat.id,'❌Ошибка скачивания')
			#break




######
async def main():
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())