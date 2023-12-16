import os.path
import json
import keep_alive
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN_API, send
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
import os
from aiogram.types import ParseMode
import texts
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class Group(StatesGroup):
    waiting_for_group = State()

keyboard_user = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_admin = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton('✍️Отказаться от уведомлений')
button2 = KeyboardButton('🚀Начать общение')
button3 = KeyboardButton('❌Закончить общение')
keyboard_user.add(button1).add(button2).insert(button3)
keyboard_admin.add('⚙️Комманды админа')

bot = Bot(token=TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

is_stopped = True
photo_admin = 0
async def on_start_up(_):
    print('Бот запущен успешно')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    file_path = 'users.txt'
    user_id = str(message.from_user.id)
    if os.path.exists(file_path):
        with open('users_ban.txt', 'r') as f:
            ban_users = f.read().splitlines()
        with open('users.txt', 'r')as f:
            users1 = f.read().splitlines()
        with open('admins_id.txt', 'r') as f:
            admin = f.read().splitlines()
        if user_id in ban_users:
            await message.answer('Вы заблокированы')

        if user_id in admin:
            await message.answer(text=texts.meeting_admin, reply_markup=keyboard_admin, parse_mode="HTML")
        else:
            if user_id not in users1:
                with open(file_path, 'a') as f:
                    f.write(user_id + '\n')
                await Group.waiting_for_group.set()
                await message.reply("Привет! Введите название группы:")
            if user_id in users1:
                await message.answer(text=texts.how_to_write, reply_markup=keyboard_user, parse_mode="HTML")

@dp.message_handler(state=Group.waiting_for_group)
async def process_group(message: types.Message, state: FSMContext):

    with open('groups.txt', 'r', encoding='utf-8') as f:
        groups = f.read().splitlines()
    # Проверяем, есть ли название группы в списке
    if message.text in groups:
        # Отправляем сообщение с приветствием
        with open('personal.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        group = data['personal']
        id_user = str(message.from_user.id)
        ready_list = {}
        for dictionary in range(len(group)):
            ready_list.update(group[dictionary])
        if str(message.from_user.id) in ready_list:
                await message.answer('Вы уже подписаны')
                await state.finish()
        else:
            new_data = {message.from_user.id: message.text}
            with open('personal.json', encoding='utf-8')as f:
                data = json.load(f)
                data['personal'].append(new_data)
                with open('personal.json', 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, ensure_ascii=False, indent=2)
                await message.reply(f"Привет! Добро пожаловать в группу {message.text}!", reply_markup=keyboard_user)
                await state.finish()
    else:
        # Отправляем сообщение с просьбой попробовать еще раз
        await message.reply("Название группы не найдено. Попробуйте еще раз:")

@dp.message_handler(commands=['ban'])
async def ban_command(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        id = message.text[5:]
        file_block_path = 'users_ban.txt'
        with open(file_block_path, 'a') as f:
            f.write(id + '\n')
        await bot.send_message(chat_id=int(id), text='Вы были забанены в данном боте')
        await message.reply(text=f'Вы успешно забанили пользователя {id}')


@dp.message_handler(commands=['unban'])
async def unban_command(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        text = message.text[7:]
        f = open("users_ban.txt").readlines()
        user_id = ('\n'.join(f).split())
        f.pop(user_id.index(str(text)))
        with open("users_ban.txt", 'w') as F:
            F.writelines(f)
        await bot.send_message(chat_id=int(text), text='Вы были разблокированы в данном боте')
        await message.reply(text=f'Вы успешно разбанили пользователя {text}')


@dp.message_handler(commands=['post'])
async def post(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    text = message.text[6:]
    if str(message.from_user.id) in admin:
        file_path = 'users.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                users = f.read().splitlines()
            for user_id in users:
                await bot.send_message(user_id, text=text, parse_mode=ParseMode.HTML)
            await message.answer(f'Сообщение: {text} отправлено всем подписчикам')
        else:
            await message.answer('Подписчиков еще нет')
    else:
        pass

@dp.message_handler(commands=['send'])
async def send_cmd(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        args = message.get_args().split()
        user_id = args[0]
        text = ' '.join(args[1:])
        with open('personal.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        group = data['personal']
        ready_list = {}
        for dictionary in range(len(group)):
            ready_list.update(group[dictionary])
        for key, value in ready_list.items():
            if value == user_id:  # условие для значения
                # Получаем айди пользователя и текст сообщения из объекта message
                # Отправляем сообщение пользователю
                await bot.send_message(chat_id=key, text=''+text)
        await bot.send_message(chat_id=send, text=f'Ваше сообщение: {text} было успешно доставлено до данной группы')

@dp.message_handler(commands=['answer'])
async def answer_message(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        global id, k
        text = message.text[8:]
        for i in range(14):
            if text[:i].isdigit():
                id = text[:i]
                k = i
        await bot.send_message(id, 'Администратор:' + text[k:])
        await message.reply("Сообщение успешно отправлено пользователю!")

@dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        id = message.text[7:]
        file_block_path = 'admins_id.txt'
        with open(file_block_path, 'a') as f:
            f.write(id + '\n')
        await bot.send_message(chat_id=send, text=f'Вы добавили пользователя {id} в качестве админа')

@dp.message_handler(content_types=ContentType.PHOTO)
async def photo_id(message: types.Message):
    with open('admins_id.txt', 'r') as f:
        admin = f.read().splitlines()
    if str(message.from_user.id) in admin:
        # Получаем информацию о фотографии
        photo = message.photo[-1]
        file_id = photo.file_id

        # Получаем текст, приложенный к фотографии
        caption = int(message.caption)

        # Выводим текст, приложенный к фотографии
        await bot.send_message(chat_id=caption, text='Админ вам отправил фотографию')
        await bot.send_photo(chat_id=caption, photo=file_id)
    else:
        user_id = str(message.from_user.id)
        file_path = 'users_ban.txt'

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                ban_users = f.read().splitlines()
            if user_id in ban_users:
                await message.answer('Вы заблокированы')
            else:
                username = str(message.from_user.username)
                global is_stopped
                if not is_stopped:
                    await bot.send_photo(send, photo=message.photo[-1].file_id, caption=message.text)
                    await message.reply(text='Фото успешно отправлено администратору!')
                    id = (f'ID: ' + f'<code>{str(message.from_user.id)}</code>')
                    username = 'Username: ' + str(message.from_user.username)
                    text = 'Вам прислали фотографию' + '\n' + id + '\n' + username + '\n\n' + f'Пример отправки сообщения: <code>/answer {str(message.from_user.id)} текст сообщения </code>' + '\n' + 'Чтобы отправить фото, в качестве вложения добавьте id-пользователя'
                    await bot.send_message(send, text=text, parse_mode="HTML")
                else:
                    await message.reply(
                        'Вы должны нажатать на <code>🚀Начать общение</code>, чтобы активировать возможность писать в поддержку!',
                        parse_mode="HTML")


@dp.message_handler()
async def echo_message(message: types.Message):
    id = 'ID: ' + f'<code>{str(message.from_user.id)}</code>'
    username = 'Username: ' + str(message.from_user.username)
    text = 'Вам прислали сообщение' + '\n' + id + '\n' + username + '\n\n' + 'Text: ' + str(
        message.text) + '\n' + f'Пример отправки сообщения: <code>/answer {str(message.from_user.id)} текст сообщения </code>' + '\n' + 'Чтобы отправить фото, в качестве вложения добавьте id-пользователя'
    global is_stopped
    if message.text == '✍️Отказаться от уведомлений':
        with open('users.txt', 'r')as f:
            userr = f.read().splitlines()
        if str(message.from_user.id) in userr:
            f = open("users.txt").readlines()
            user_id = ('\n'.join(f).split())
            f.pop(user_id.index(str(message.from_user.id)))
            with open("users.txt", 'w') as F:
                F.writelines(f)
            with open('personal.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data["personal"]:
                    if str(message.from_user.id) in item:
                        data["personal"].remove(item)
                        with open('personal.json', 'w', encoding='utf-8') as outfile:
                            json.dump(data, outfile, ensure_ascii=False, indent=2)
            await message.answer(text='Вы отключили функцию оповещения, чтобы включить снова, введите комманду <code>/start</code>', parse_mode='HTML')
        else:
            await bot.send_message(chat_id=message.from_user.id, text='Вы уже отключили функцию оповещения, чтобы включить снова, введите комманду <code>/start</code>', parse_mode='HTML')

    elif message.text == '⚙️Комманды админа':
        with open('admins_id.txt', 'r') as f:
            admin = f.read().splitlines()
        if str(message.from_user.id) in admin:
            await bot.send_message(chat_id=send, text=texts.help_command, parse_mode="HTML")

    elif message.text == '🚀Начать общение':
        user_id = str(message.from_user.id)
        with open('users_ban.txt', 'r') as f:
            ban_users = f.read().splitlines()
        if user_id in ban_users:
            await message.answer('Вы заблокированы')
        else:
            is_stopped = False
            await message.answer('Теперь вы можете писать в поддержку')
    elif message.text == '❌Закончить общение':
        user_id = str(message.from_user.id)
        with open('users_ban.txt', 'r') as f:
            ban_users = f.read().splitlines()
        if user_id in ban_users:
            await message.answer('Вы заблокированы')
        else:
            is_stopped = True
            await message.answer(
                'Вы прекратили общение с поддержкой, если хотите снова начать, то нажмите на <code>🚀Начать общение</code> и '
                'напишите свою проблему',
                parse_mode="HTML")

    else:
        user_id = str(message.from_user.id)
        file_path = 'users_ban.txt'

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                ban_users = f.read().splitlines()
            if user_id in ban_users:
                await message.answer('Вы заблокированы')
            else:
                if not is_stopped:
                    await bot.send_message(send, text=text, parse_mode='HTML')
                    await message.reply("Текст успешно отправлен администратору!")

                if is_stopped:
                    await message.reply(
                        'Вы должны нажатать на <code>🚀Начать общение</code>, чтобы начать писать в поддержку!',
                        parse_mode="HTML")

keep_alive.keep_alive()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up)

