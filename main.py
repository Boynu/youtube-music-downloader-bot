import sqlite3, datetime, asyncio, logging, os, eyed3, subprocess, traceback
from pytube import YouTube
from pytube import Playlist
from pytube import exceptions

from youtubesearchpython import VideosSearch

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import RestrictChatMember
from aiogram.types import ChatActions
from aiogram.utils.markdown import hlink

import langs

token = '5338717802:AAFe_Jg86ubkv_F6DViEbjuFrVcqIKqCvSQ'

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

def check_error(userid):
	files = os.listdir(f'{userid}/')
	for file in files:
		if file[-4:] != '.txt':
			os.remove(f'{userid}/{file}')
async def get_ln(userid):
	cursor.execute(f"SELECT lang FROM users WHERE id = {userid}")
	data = cursor.fetchone()
	ln = data[0]
	if ln is None:
		await bot.send_message(userid, '/start')
	else:
		return ln

class go(StatesGroup):
	newlist = State()
	get = State()
	dell = State()
	clear = State()
	cho = State()
	lang = State()
	search = State()

global connect
connect = sqlite3.connect('users.db', check_same_thread=False)
global cursor
cursor= connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
		id INTEGER, username TEXT, lang TEXT
	)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS data(
		link TEXT, t_id TEXT
	)""")
connect.commit()

@dp.message_handler(state=None)
async def start(message: types.Message,state: FSMContext):
	userid = message.chat.id
	if message.text == '/start':
		today = datetime.datetime.today()
		f = 'Старт '+ str(message.chat.id) + ' ' + today.strftime("%Y-%m-%d-%H.%M.%S")
		print(f)
		cursor.execute(f"SELECT * FROM users WHERE id = {userid}")
		data = cursor.fetchone()
		if data is None:
			cursor.execute("INSERT INTO users(id, username) VALUES(?,?);", (message.chat.id, message.chat.username,))
			connect.commit()
			os.mkdir(str(userid))
			with open(f'{userid}/ids.txt', 'w') as file:
				pass
			await leng(message, state)
		elif data[2] is None:
			await leng(message, state)
		else:
			await mainmenu(message, state)

	elif 'youtube' in message.text or 'youtu.be' in message.text:
		userid = message.chat.id
		ln = await get_ln(userid)
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(types.KeyboardButton(f'{langs.default[ln]} [{check_numb(f"{userid}/ids.txt")}]'))
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		try:
			for name in dirs:
				markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		except:
			pass
		await bot.send_message(message.chat.id, langs.ch_play[ln],'HTML', reply_markup = markup)
		urls = message.text
		urls = urls.replace('youtu.be/','www.youtube.com/watch?v=')
		async with state.proxy() as data:
			data['url'] = urls
		await go.cho.set()

	elif message.text == langs.menu1['RU'] or message.text == langs.menu1['EN'] or message.text == '/get':
		userid = message.chat.id
		ln = await get_ln(userid)
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		plays=[]
		markup.row(types.KeyboardButton(f'{langs.default[ln]} [{check_numb(f"{userid}/ids.txt")}]'))
		plays.append(f'<code>{langs.default[ln]}</code>')
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		for name in dirs:
			plays.append(f'<code>{name[:-4]}</code>')
			markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		dirss = '\n'.join(plays)
		await bot.send_message(message.chat.id, f'{langs.warn[ln]}\n\n{dirss}</i>','HTML', reply_markup = markup)
		await go.get.set()

	elif message.text == langs.menu0['RU'] or message.text == langs.menu0['EN'] or message.text == '/search':
		userid = message.chat.id
		ln = await get_ln(userid)
		await bot.send_message(message.chat.id, langs.ch_search[ln], reply_markup=types.ReplyKeyboardRemove())
		await go.search.set()

	elif message.text == '/del':
		userid = message.chat.id
		ln = await get_ln(userid)
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		for name in dirs:
			markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		await bot.send_message(message.chat.id, langs.ch_del[ln], reply_markup=markup)
		await go.dell.set()

	elif message.text == '/clear':
		userid = message.chat.id
		ln = await get_ln(userid)
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(types.KeyboardButton(f'{langs.default[ln]} [{check_numb(f"{userid}/ids.txt")}]'))
		dirs = os.listdir(f'{userid}/')
		dirs.remove('ids.txt')
		try:
			for name in dirs:
				markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
		except:
			pass
		await bot.send_message(message.chat.id, langs.ch_clean[ln], reply_markup=markup)
		await go.clear.set()

	elif message.text == '/help':
		userid = message.chat.id
		ln = await get_ln(userid)
		await bot.send_message(message.chat.id, langs.helpp[ln])
	
	elif message.text == '/create' or message.text == langs.menu2['RU'] or message.text == langs.menu2['EN']:
		userid = message.chat.id
		ln = await get_ln(userid)
		if len(os.listdir(f'{userid}/')) < 7:
			await bot.send_message(message.chat.id, langs.ch_name[ln], reply_markup = types.ReplyKeyboardRemove())
			await go.newlist.set()
		else:
			await bot.send_message(message.chat.id, langs.er_len[ln])
	elif message.text == '🇬🇧Change the language':
		cursor.execute(f"UPDATE users SET lang = 'EN' WHERE id = " + str(userid))
		connect.commit()
		await mainmenu(message, state)
	elif message.text == '🇷🇺Изменить язык':
		cursor.execute(f"UPDATE users SET lang = 'RU' WHERE id = " + str(userid))
		connect.commit()
		await mainmenu(message, state)
	
async def mainmenu(message, state):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(types.KeyboardButton(langs.menu0[ln]))
	markup.row(types.KeyboardButton(langs.menu1[ln]))
	markup.row(types.KeyboardButton(langs.menu2[ln]))
	markup.row(types.KeyboardButton(langs.menu3[ln]))
	
	await bot.send_message(message.chat.id, langs.menu[ln], reply_markup=markup)

async def check(message, url, state, play):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	if 'playlist' in url:
		await plalist(url, str(userid), message, play)
	else:
		for link in url.split(' '):
			try:
				await download(link, str(userid), message, play)
			except Exception:
				traceback.print_exc()
				await bot.send_message(message.chat.id, langs.err_down[ln])
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
	ln = await get_ln(userid)
	check_error(userid)
	link_id = url.split('watch?v=')[1].split('&')[0]
	cursor.execute(f"SELECT * FROM data WHERE link = '{link_id}'")
	data = cursor.fetchone()
	if data is None:
		try:
			video = YouTube(url)
			start_d = await bot.send_message(message.chat.id, f'{langs.start_m[ln]} <i>{video.title}</i>', 'HTML', reply_markup=types.ReplyKeyboardRemove())
			if video.length > 1800:
				await bot.send_message(message.chat.id, f'❌<i>{video.title}</i> {langs.err_min[ln]}', 'HTML')
			else:
				await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VOICE)
				audio = video.streams.filter(only_audio = True).first()
				name_path = audio.download(name+'/')
				name_song = video.title.replace('/','')
				mp3 = f"{name}/{name_song}.mp3"
				await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VOICE)
				convert(name_path, mp3)
				await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_VOICE)
				matadata(f"{name}/{name_song}.mp3",video.title,video.author)
				file = await bot.send_audio(message.chat.id,audio=open(f"{name}/{name_song}.mp3", 'rb'))
				file_id = file.audio.file_id
				with open(f'{userid}/{play}', 'a') as file:
					file.write(file_id+' ')
				cursor.execute("INSERT INTO data(link, t_id) VALUES(?,?);", (link_id, file_id,))
				connect.commit()
				os.remove(name_path)
				os.remove(f"{name}/{name_song}.mp3")
		except exceptions.AgeRestrictedError:
			await bot.send_message(message.chat.id, langs.err_age[ln])
		except exceptions.LiveStreamError:
			await bot.send_message(message.chat.id, langs.err_live[ln])
		except exceptions.VideoRegionBlocked:
			await bot.send_message(message.chat.id, langs.err_region[ln])
		except exceptions.VideoUnavailable:
			await bot.send_message(message.chat.id, langs.err_ava[ln])
		except Exception:
			traceback.print_exc()
			raise ValueError('Ошибка')
		await start_d.delete()
	else:
		file = await bot.send_audio(message.chat.id, audio=data[1])
		file_id = file.audio.file_id
		with open(f'{userid}/{play}', 'a') as file:
			file.write(file_id+' ')

async def plalist(url, name, message, play):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	p = Playlist(url)
	text = f'{langs.start_p[ln]} <i>{p.title}</i>'
	await bot.send_message(message.chat.id, text, 'HTML')
	for file in p.video_urls:
		try:
			await download(file, name, message, play)
		except ValueError:
			await bot.send_message(message.chat.id, langs.err_down[ln])

@dp.message_handler(state=go.search)
async def search(message, state: FSMContext):
	userid = message.chat.id
	ln = await get_ln(userid)
	await bot.send_message(message.chat.id, langs.start_s[ln])
	rez = []
	q = message.text + ' music'
	videosSearch = VideosSearch(q, limit = 5)
	for i in range(5):
		temp = []
		try:
			time = videosSearch.result()['result'][i]['duration'].split(':')
			if len(time) == 3:
				h, m, s = map(int, time)
				m += h*60
			else:
				m,s = map(int, time)
			if m <= 30:
				temp.append(videosSearch.result()['result'][i]['title'])
				temp.append(videosSearch.result()['result'][i]['duration'])
				temp.append(videosSearch.result()['result'][i]['link'])
				temp.append(videosSearch.result()['result'][i]['thumbnails'][-1]['url'])
				rez.append(temp)
		except:
			continue
	keyboard = types.InlineKeyboardMarkup()
	keyboard.add(types.InlineKeyboardButton(text=langs.start_d[ln], callback_data="download"))
	for i in range(len(rez)):
		text = f"""
		<b>{rez[i][0]}</b>
		<i>{rez[i][1]}</i>

		{rez[i][2]}
		"""
		try:
			await bot.send_photo(chat_id = message.chat.id, photo = rez[i][3], caption=text, parse_mode='HTML', reply_markup=keyboard)
		except:
			continue
	await state.finish()
	await mainmenu(message,state)

@dp.callback_query_handler(text="download")
async def download_keyboard(call: types.CallbackQuery,state: FSMContext):
	data = call.message
	urls = data['caption'].split('\n  ')[-1]
	userid = int(call['from']['id'])
	ln = await get_ln(userid)
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(types.KeyboardButton(f'{langs.default[ln]} [{check_numb(f"{userid}/ids.txt")}]'))
	dirs = os.listdir(f'{userid}/')
	dirs.remove('ids.txt')
	try:
		for name in dirs:
			markup.row(types.KeyboardButton(f'{name[:-4]} [{check_numb(f"{userid}/{name}")}]'))
	except:
		pass
	await call.message.answer(langs.ch_play[ln],'HTML', reply_markup = markup)
	
	async with state.proxy() as data:
		data['url'] = urls
	await go.cho.set()



@dp.message_handler(state=go.newlist)
async def newlist(message, state: FSMContext):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	name = message.text
	if name+'.txt' in os.listdir(f'{userid}/'):
		await bot.send_message(message.chat.id, langs.err_name[ln])
	else:
		with open(f'{userid}/{name}.txt', 'w') as file:
			pass
		await bot.send_message(message.chat.id, langs.create[ln], 'HTML')
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.get)
async def get(message, state: FSMContext):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	name = (message.text).split(' [')[0] 
	name += '.txt'

	if name == f'{langs.default[ln]}.txt':
		with open(f'{userid}/ids.txt') as file:
			ids = file.read()
		ids = ids.split(' ')
		del ids[-1]
		for idd in ids:
			await bot.send_audio(message.chat.id, audio=idd, reply_markup=types.ReplyKeyboardRemove())
			await asyncio.sleep(0.5)
	elif name in os.listdir(f'{userid}/'):
		with open(f'{userid}/{name}') as file:
			ids = file.read()
		ids = ids.split(' ')
		del ids[-1]
		for idd in ids:
			await bot.send_audio(message.chat.id, audio=idd, reply_markup=types.ReplyKeyboardRemove())
			await asyncio.sleep(0.5)
	else:
		await bot.send_message(message.chat.id, langs.err_p[ln])
	await state.finish()
	await mainmenu(message, state)


@dp.message_handler(state=go.dell)
async def dell(message, state: FSMContext):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	name = (message.text).split(' [')[0] 
	name += '.txt'

	if name in os.listdir(f'{userid}/'):
		os.remove(f'{userid}/{name}')
		await bot.send_message(message.chat.id, langs.delite[ln])
	elif name == 'ids.txt':
		await bot.send_message(message.chat.id, langs.err_p[ln])
	else:
		await bot.send_message(message.chat.id, langs.err_p[ln])
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.clear)
async def clear(message, state: FSMContext):
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	name = (message.text).split(' [')[0] 
	name += '.txt'
	if name == f'{langs.default[ln]}.txt':
		with open(f'{userid}/ids.txt', 'w') as file:
			file.write('')
		await bot.send_message(message.chat.id, langs.clean[ln])
	elif name in os.listdir(f'{userid}/'):
		with open(f'{userid}/{name}', 'w') as file:
			file.write('')
		await bot.send_message(message.chat.id, langs.clean[ln])
	else:
		await bot.send_message(message.chat.id, langs.err_p[ln])
	await state.finish()
	await mainmenu(message, state)

@dp.message_handler(state=go.cho)
async def cho(message, state: FSMContext):
	async with state.proxy() as data:
		url = data['url']
	await state.finish()
	userid = message.chat.id
	ln = await get_ln(userid)
	check_error(userid)
	name = (message.text).split(' [')[0] 
	name += '.txt'
	if name == f'{langs.default[ln]}.txt':
		await check(message, url, state, 'ids.txt')
	elif name in os.listdir(f'{userid}/'):
		await check(message, url, state, name)
	else:
		await bot.send_message(message.chat.id, langs.err_p[ln])

async def leng(message, state):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(types.KeyboardButton('🇷🇺Русский язык'))
	markup.row(types.KeyboardButton('🇬🇧English language'))
	await bot.send_message(message.chat.id,'🇷🇺Пожалуйста выберите язык\n\n🇬🇧Please select a language',reply_markup=markup)
	await go.lang.set()

@dp.message_handler(state=go.lang)
async def lang(message, state: FSMContext):
	userid = message.chat.id
	if message.text == '🇷🇺Русский язык':
		ln = 'RU'
	elif message.text == '🇬🇧English language':
		ln = 'EN'
	else:
		await leng(message, state)
	await state.finish()
	cursor.execute(f"UPDATE users SET lang = '{ln}' WHERE id = " + str(userid))
	connect.commit()
	await mainmenu(message, state)



######
async def main():
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())
