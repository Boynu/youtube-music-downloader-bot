import sqlite3, datetime, asyncio, logging, os, eyed3, subprocess, traceback
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

def check_numb(path):
	with open(path) as file:
		ids = file.read()
	ids = ids.split(' ')
	del ids[-1]
	return len(ids)

class go(StatesGroup):
	newlist = State()
	get = State()
	dell = State()
	clear = State()
	cho = State()

global connect
connect = sqlite3.connect('users.db', check_same_thread=False)
global cursor
cursor= connect.cursor()

@dp.message_handler(state=None)
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
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(types.KeyboardButton(f'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ [{check_numb(f"{userid}/ids.txt")}]'))
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		try:
			for name in dirs:
				markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		except:
			pass
		await bot.send_message(message.chat.id, '👇Укажите в какой плейлист вы хотите загрузить песни','HTML', reply_markup = markup)
		async with state.proxy() as data:
			data['url'] = message.text
		await go.cho.set()

	elif message.text == '📂Показать всю скаченную музыку' or message.text == '/get':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(types.KeyboardButton(f'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ [{check_numb(f"{userid}/ids.txt")}]'))
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		for name in dirs:
			markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		await bot.send_message(message.chat.id,'⚠️Внимание, вы получите список всех песен которые когда либо скачивали в этом боте.\nЕсли вы хотите использовать этого бота для прослушивания музыки, то нажмите на кнопку <i>"🧹Очистить историю чата"</i> и выберете плейлист','HTML', reply_markup = markup)
		await go.get.set()

	elif message.text == '/del':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		for name in dirs:
			markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		await bot.send_message(message.chat.id, '🗑Выберете плейлист для удаления', reply_markup=markup)
		await go.dell.set()

	elif message.text == '/clear':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(types.KeyboardButton(f'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ [{check_numb(f"{userid}/ids.txt")}]'))
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		try:
			for name in dirs:
				markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		except:
			pass
		await bot.send_message(message.chat.id, '🧹Выберете плейлист для очистки', reply_markup=markup)
		await go.clear.set()

	elif message.text == '/help':
		await bot.send_message(message.chat.id, '📰Справка:\n\n/start - Запустить бота\n/get - Все скаченные песни\n/clear - Удалить все песни\n/create - Создать новый плейлист\n/del - Удалить плейлист')
	
	elif message.text == '/create' or message.text == '➕Создать новый плейлист':
		if len(os.listdir(f'{userid}/')) < 7:
			await bot.send_message(message.chat.id, '✍️Введите название плейлиста', reply_markup = types.ReplyKeyboardRemove())
			await go.newlist.set()
		else:
			await bot.send_message(message.chat.id, '❌У вас больше 5 плейлистов!')

async def mainmenu(message, state):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(types.KeyboardButton('📂Показать всю скаченную музыку'))
	markup.row(types.KeyboardButton('➕Создать новый плейлист'))
	
	userid = message.chat.id
	text = '🎵🔗Отправьте ссылку на музыку или плейлист (Из youtube.com или music.youtube.com)\nВы можете указать несколько песен через пробел\n\n📰Справка /help'
	await bot.send_message(message.chat.id, text, reply_markup=markup)

async def check(message, url, state, play):
	userid = message.chat.id
	if 'playlist' in url:
		await plalist(url, str(userid), message, play)
	else:
		for link in url.split(' '):
			try:
				await download(link, str(userid), message, play)
			except:
				await bot.send_message(message.chat.id, '❌Ошибка при скачивании песни')
	await mainmenu(message, state)


def matadata(path,name,author):
	audio_file = eyed3.load(path)
	audio_file.tag.title = name
	audio_file.tag.artist = author
	audio_file.tag.save()

def convert(mp4,mp3):
	command = ['ffmpeg', '-fflags', '+genpts','-i', mp4, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', mp3]
	subprocess.run(command)

async def download(url, name, message, play):
	userid = message.chat.id
	try:
		video = YouTube(url)
		start_d = await bot.send_message(message.chat.id, f'💾Началось скачивание <i>{video.title}</i>', 'HTML', reply_markup=types.ReplyKeyboardRemove())
		if video.length > 1800:
			await bot.send_message(message.chat.id, f'❌<i>{video.title}</i> длится более 30 минут!', 'HTML')
		else:
			await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VOICE)
			audio = video.streams.filter(only_audio = True).first()
			name_path = audio.download(name+'/')
			mp3 = f"{name}/{video.title}.mp3"
			convert(name_path, mp3)
			matadata(f"{name}/{video.title}.mp3",video.title,video.author)
			file = await bot.send_audio(message.chat.id,audio=open(f"{name}/{video.title}.mp3", 'rb'))
			file_id = file.audio.file_id
			with open(f'{userid}/{play}', 'a') as file:
				file.write(file_id+' ')
			os.remove(name_path)
			os.remove(f"{name}/{video.title}.mp3")
	except Exception:
		traceback.print_exc()
		raise ValueError('Ошибка')
	await start_d.delete()

async def plalist(url, name, message, play):
	p = Playlist(url)
	text = f'📥Скачивание плейлиста <i>{p.title}</i>'
	await bot.send_message(message.chat.id, text, 'HTML')
	for file in p.video_urls:
		try:
			await download(file, name, message, play)
		except ValueError:
			await bot.send_message(message.chat.id,'❌Ошибка скачивания')


@dp.message_handler(state=go.newlist)
async def newlist(message, state: FSMContext):
	userid = message.chat.id
	name = message.text
	if name+'.txt' in os.listdir(f'{userid}/'):
		await bot.send_message(message.chat.id, '❌Такой плейлист уже существует!')
	else:
		with open(f'{userid}/{name}.txt', 'w') as file:
			pass
		await bot.send_message(message.chat.id, f'✅Плейлист <i>{name}</i> создан', 'HTML')
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.get)
async def get(message, state: FSMContext):
	userid = message.chat.id
	name = (message.text).split(' [')[0] 
	name += '.txt'

	if name == 'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ.txt':
		with open(f'{userid}/ids.txt') as file:
			ids = file.read()
		ids = ids.split(' ')
		del ids[-1]
		for idd in ids:
			await bot.send_audio(message.chat.id, audio=idd, reply_markup=types.ReplyKeyboardRemove())
	elif name in os.listdir(f'{userid}/'):
		with open(f'{userid}/{name}') as file:
			ids = file.read()
		ids = ids.split(' ')
		del ids[-1]
		for idd in ids:
			await bot.send_audio(message.chat.id, audio=idd, reply_markup=types.ReplyKeyboardRemove())
	else:
		await bot.send_message(message.chat.id, '❌Ошибка. Вы указали неправильное название плейлиста')
	await state.finish()
	await mainmenu(message, state)


@dp.message_handler(state=go.dell)
async def dell(message, state: FSMContext):
	userid = message.chat.id
	name = (message.text).split(' [')[0] 
	name += '.txt'

	if name in os.listdir(f'{userid}/'):
		os.remove(f'{userid}/{name}')
		await bot.send_message(message.chat.id, '✅Плейлист успешно удалён')
	elif name == 'ids.txt':
		await bot.send_message(message.chat.id, '❌Ошибка. Так нельзя)')
	else:
		await bot.send_message(message.chat.id, '❌Ошибка. Вы указали неправильное название плейлиста')
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.clear)
async def clear(message, state: FSMContext):
	userid = message.chat.id
	name = (message.text).split(' [')[0] 
	name += '.txt'
	if name == 'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ.txt':
		with open(f'{userid}/ids.txt', 'w') as file:
			file.write('')
		await bot.send_message(message.chat.id, '✅Плейлист успешно очищен')
	elif name in os.listdir(f'{userid}/'):
		with open(f'{userid}/{name}', 'w') as file:
			file.write('')
		await bot.send_message(message.chat.id, '✅Плейлист успешно очищен')
	else:
		await bot.send_message(message.chat.id, '❌Ошибка. Вы указали неправильное название плейлиста')
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.cho)
async def cho(message, state: FSMContext):
	async with state.proxy() as data:
		url = data['url']
	await state.finish()
	userid = message.chat.id
	name = (message.text).split(' [')[0] 
	name += '.txt'
	if name == 'ПЛЕЙЛИСТ ПО УМОЛЧАНИЮ.txt':
		await check(message, url, state, 'ids.txt')
	elif name in os.listdir(f'{userid}/'):
		await check(message, url, state, name)
	else:
		await bot.send_message(message.chat.id, '❌Ошибка. Вы указали неправильное название плейлиста')




######
async def main():
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())