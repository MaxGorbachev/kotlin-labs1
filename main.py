# -*- coding: utf-8 -*-
import codecs

from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle

from aiogram.utils.markdown import link

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from modules import start as start
from db_connection import *
from settings import *

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)

added_info = {}
for elem in admin_ids:
    added_info[elem] = {}


async def reg(user_id):
    user = await get_user_data(user_id)
    if user is None:
        user = await create_user(user_id)
    return dict(user)


@dp.message_handler(commands=['admin'])
async def send_welcome(message):
    await reg(str(message.from_user.id))

    if message.from_user.id in admin_ids:
        inline_kb = InlineKeyboardMarkup()

        inline_btn_1 = InlineKeyboardButton('📈Статистика', callback_data='statistics')

        inline_btn_2 = InlineKeyboardButton('📄Список каналов', callback_data='channel_list')

        inline_btn_3 = InlineKeyboardButton('📄Список фильмов', callback_data='film_list')

        inline_btn_4 = InlineKeyboardButton('🎥Добавить фильм', callback_data='add_film')

        inline_btn_5 = InlineKeyboardButton('📌Удалить номер фильма', callback_data='delete_film_number')

        inline_btn_6 = InlineKeyboardButton('📌Добавить канал', callback_data='add_channel')

        inline_btn_7 = InlineKeyboardButton('📌Удалить канал', callback_data='delete_channel')

        inline_btn_8 = InlineKeyboardButton('📌Сделать рассылку ', callback_data='mailing')


        inline_kb.add(inline_btn_1)
        inline_kb.add(inline_btn_2)
        inline_kb.add(inline_btn_3)
        inline_kb.add(inline_btn_4)
        inline_kb.add(inline_btn_5)
        inline_kb.add(inline_btn_6)
        inline_kb.add(inline_btn_7)
        inline_kb.add(inline_btn_8)

        await bot.send_message(chat_id=message.from_user.id, text='*Админ панель*', parse_mode='Markdown',
                               reply_markup=inline_kb)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    user = await reg(str(message.from_user.id))

    if user['status'] == "mailing":
        file = await bot.get_file(message.photo[-1].file_id)

        await message.photo[-1].download(destination_dir='')

        await change_user_status(message.from_user.id, "0")

        all_users = await get_users()

        for user in all_users:
            user = dict(user)
            try:
                await bot.send_photo(chat_id=user['tg_id'], photo=open(file.file_path, 'rb'),
                                     caption=str(message.caption))
            except Exception as ex:
                print(ex)
                await bot.send_message(chat_id=message.from_user.id, text=f'{ex}\nЧто-то пошло не так')

        await bot.send_message(chat_id=message.from_user.id, text='Рассылка прошла успешно.')


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await reg(str(message.from_user.id))

    if await check_follow(message):
        await bot.send_message(message.from_user.id,
                               text='*Привет это 🍿КИНОМОЛОКО - БОТ | Поиск🔍\nЧтобы узнать название фильмов из ЮТУБ | ТИК ТОК вам нужно ввести код фильма.\nНажмите на «🔎Поиск» 👇*',
                               parse_mode='Markdown', reply_markup=start.greet_kb1)


@dp.callback_query_handler(text='statistics')
async def vote_up_cb_handler(call):
    await reg(str(call.from_user.id))

    users = await get_users()

    await bot.send_message(call.from_user.id, text='*📈Количество людей в боте: ' + str(len(users)) + '*',
                           parse_mode='Markdown')


@dp.callback_query_handler(text='add_channel')
async def vote_up_cb_handler(call):
    await reg(str(call.from_user.id))

    await change_user_status(call.from_user.id, 'add_channel_link')

    await bot.send_message(call.from_user.id,
                           text='*Введите ссылку на канал без @\n\nПример: для добавления канала @twochannel, введите twochannel*',
                           parse_mode='Markdown')


@dp.callback_query_handler(text='delete_film_number')
async def vote_up_cb_handler(call):
    await reg(str(call.from_user.id))

    await change_user_status(call.from_user.id, 'delete_film_number')

    await bot.send_message(call.from_user.id, text='*Введите номер фильма, который необходимо удалить*',
                           parse_mode='Markdown')


@dp.callback_query_handler(text='channel_list')
async def vote_up_cb_handler(call):
    channels = await get_channels()
    inline_kb = InlineKeyboardMarkup()
    for channel in channels:
        inline_btn = InlineKeyboardButton(str(channel['title']), url='https://t.me/' + str(channel['url']))
        inline_kb.add(inline_btn)
    await bot.send_message(chat_id=call.from_user.id,
                           text='*📝 Список каналов для подписки:*',
                           reply_markup=inline_kb, parse_mode='Markdown')


@dp.callback_query_handler(text='delete_channel')
async def vote_up_cb_handler(call):
    user = await reg(str(call.from_user.id))

    await change_user_status(user['tg_id'], 'delete_channel')

    channels = await get_channels()

    message = ""
    for channel in channels:
        channel = dict(channel)
        message += str(channel['url']) + '\n'

    await bot.send_message(call.from_user.id,
                           text='*Список ваших каналов:\n' + message + '\n\nВведите одно из них, чтобы удалить.*',
                           parse_mode='Markdown')


@dp.callback_query_handler(text='mailing')
async def vote_up_cb_handler(call):
    user = await reg(str(call.from_user.id))

    await change_user_status(user['tg_id'], 'mailing')

    await bot.send_message(call.from_user.id, text='*❗️Введите сообщение для рассылки (можно с фото)*', parse_mode='Markdown')


@dp.callback_query_handler(text='add_film')
async def vote_up_cb_handler(call):
    user = await reg(str(call.from_user.id))

    await change_user_status(user['tg_id'], 'add_film_title')

    await bot.send_message(call.from_user.id, text='*Введите название нового фильма*', parse_mode='Markdown')


@dp.callback_query_handler(text='film_list')
async def vote_up_cb_handler(call):
    await reg(str(call.from_user.id))
    films = await get_films()
    if films:
        films = list(map(dict, films))
    message = ""
    i = 0
    while len(message) < 900 and i < len(films):
        message += "#" + str(films[i]['id']) + " " + films[i]['title'] + "\n"
        i += 1
    await bot.send_message(call.from_user.id,
                           text='Фильмы:\n' + message,
                           parse_mode='Markdown')


@dp.callback_query_handler(text='check')
async def vote_up_cb_handler(call):
    await reg(call.from_user.id)

    if await check_follow(call):
        await bot.send_message(call.from_user.id,
                               text='*Привет это 🍿КИНОМОЛОКО - БОТ | Поиск🔍\nЧтобы узнать название фильмов из ЮТУБ | ТИК ТОК вам нужно ввести код фильма.\nНажмите на «🔎Поиск» 👇*',
                               parse_mode='Markdown', reply_markup=start.greet_kb1)


@dp.message_handler()
async def send_welcome(message):
    global added_info
    user = await reg(str(message.from_user.id))

    if await check_follow(message):
        if str(message.text) == '🔎Поиск':
            await bot.send_message(chat_id=message.from_user.id, text='*🔎 Для поиска отправьте КОД фильма/сериала*',
                                   parse_mode='Markdown')
        elif user['status'] == 'add_film_title':
            added_info[message.from_user.id]['title'] = str(message.text)
            await change_user_status(message.from_user.id, "add_film_link")
            await bot.send_message(chat_id=message.from_user.id, text='*Введите ссылку на фотографию для фильма*',
                                   parse_mode='Markdown')
        elif user['status'] == "add_film_link":
            await change_user_status(message.from_user.id, "add_film_description")
            added_info[message.from_user.id]['link'] = str(message.text)
            await bot.send_message(chat_id=message.from_user.id,
                                   text='*Введите описание для фильма("-" если хотите оставить пустым)*',
                                   parse_mode='Markdown')
        elif user['status'] == "add_film_description":
            await change_user_status(message.from_user.id, "0")
            description = str(message.text).strip()
            print(message.text)
            print(message)
            if description == "-":
                description = " "
            await add_film(added_info[message.from_user.id]['title'], added_info[message.from_user.id]['link'],
                           description)
            added_info[message.from_user.id] = {}
            await bot.send_message(chat_id=message.from_user.id, text='*Фильм успешно добавлен!*',
                                   parse_mode='Markdown')
        elif user['status'] == 'mailing':

            await change_user_status(message.from_user.id, "0")
            users = await get_users()
            send_to = 0
            all_users_quantity = len(users)
            for user in users:
                user = dict(user)
                try:
                    await bot.send_message(chat_id=user['tg_id'], text=str(message.text))
                    send_to += 1
                except:
                    pass

            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'*Рассылка прошла успешно.*\n Отправлено {send_to} сообщений, всего пользователей: {all_users_quantity} ',
                                   parse_mode='Markdown')

        elif user['status'] == 'add_channel_link':
            added_info['link'] = str(message.text)

            await change_user_status(message.from_user.id, 'add_channel_title')

            await bot.send_message(chat_id=message.from_user.id, text='*Хорошо. Теперь укажите название канала*',
                                   parse_mode='Markdown')

        elif user['status'] == 'add_channel_title':

            await change_user_status(message.from_user.id, '0')

            await add_channel(str(message.text), added_info['link'])

            added_info = {}

            await bot.send_message(chat_id=message.from_user.id, text='*Канал успешно добавлен!*',
                                   parse_mode='Markdown')

        elif user['status'] == 'delete_film_number':

            result = await delete_film(str(message.text))

            if result:
                await change_user_status(message.from_user.id, '0')

                await message.reply('Номер успешно удалён')
            else:
                await message.reply('Данный номер отсутствует')

        elif user['status'] == 'delete_channel':

            result = await delete_channel(str(message.text))

            if result:
                await change_user_status(user['tg_id'], "0")
                await bot.send_message(chat_id=message.from_user.id, text='*Канал успешно удалён из списка!*',
                                       parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text='*Убедитесь в правильности написания канала!*', parse_mode='Markdown')
        elif user['status'] == '0':
            film = await get_film(str(message.text))
            if film is not None:
                film = dict(film)
                try:
                    description = film['description']
                    if len(description) == 1:
                        description = ""
                    elif len(description) > 850:
                        description = "*Описание*:\n" + film['description'][:850] + "..."
                    else:
                        description = "*Описание*:\n" + description
                    await bot.send_photo(chat_id=message.from_user.id, photo=film['image_url'],
                                         caption='*🎬 Название фильма "' + film['title'] + '"*\n' + description,
                                         parse_mode='Markdown')

                except Exception as ex:
                    print(ex)
                    await bot.send_message(chat_id=message.from_user.id,
                                           text=f'Возникла ошибка {ex}. \nПопробуйте снова', parse_mode='Markdown')

            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text='*Убедитесь в правильности кода фильма!*', parse_mode='Markdown')


async def check_follow(message):
    channels = await get_channels()

    inline_kb = InlineKeyboardMarkup()
    channels_to_follow = []
    for channel in channels:
        channel = dict(channel)
        user_channel_status = await bot.get_chat_member(chat_id="@" + str(channel['url']), user_id=message.from_user.id)
        if user_channel_status["status"] == 'left':
            channels_to_follow.append(channel)
    if len(channels_to_follow) != 0:
        for channel in channels_to_follow:
            inline_btn = InlineKeyboardButton(str(channel['title']), url='https://t.me/' + str(channel['url']))
            inline_kb.add(inline_btn)
        inline_btn = InlineKeyboardButton('Поиск', callback_data='check')
        inline_kb.add(inline_btn)
        bot_message = await bot.send_message(chat_id=message.from_user.id,
                                             text='*📝 Для использования бота, вы должны быть подписаны на наши каналы:*',
                                             reply_markup=inline_kb, parse_mode='Markdown')
        await add_message(tg_id=message.from_user.id, message_id=bot_message.message_id)
        return False
    messages = await get_messages(message.from_user.id)
    if messages:
        for message_id in messages:
            try:
                await bot.delete_message(message.from_user.id, int(message_id))
            except Exception as ex:
                print('deleting error :', ex)
        await clear_messages(message.from_user.id)
    return True


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
