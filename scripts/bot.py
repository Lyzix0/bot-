import types
from datetime import datetime

from aiogram import Dispatcher, Bot, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import scripts.config as cfg
import scripts.database
import scripts.keyboards as kbd

TOKEN = cfg.config['bot_api']
dp = Dispatcher()
db = scripts.database.Database("users.db")
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


class Form(StatesGroup):
    enter_message_all = State()
    enter_message = State()
    admin = State()
    enter_name = State()
    select_action = State()
    select_time = State()


@dp.message(F.text == "Отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
    await bot.send_message(
        message.from_user.id,
        cfg.config['start_text']
    )


@dp.message(Command("admin"))
async def command_admin(message: Message, state: FSMContext):
    if message.from_user.id in cfg.config['admins']:
        await bot.send_message(
            message.from_user.id,
            "Вы зашли в админ панель!😊",
            reply_markup=kbd.admin_menu_button,
        )
        await state.set_state(Form.admin)
    else:
        await bot.send_message(
            message.from_user.id,
            "Вы не являетесь админом!",
        )


@dp.message(F.text == "Проверить подписку пользователя", Form.admin)
async def renew_subscription(message: Message, state: FSMContext):
    if message.from_user.id in cfg.config["admins"]:
        await bot.send_message(
            message.from_user.id,
            "Введите имя пользователя",
            reply_markup=kbd.keyboard_cancel,
        )
        await state.set_state(Form.enter_name)


@dp.message(Form.enter_name)
async def enter_username(message: Message, state: FSMContext):
    check_user = db.check_username(message.text)

    if check_user is not False:
        await state.update_data(user_id=check_user[0])
        await state.update_data(username=message.text)
        if check_user[2] is not None:
            date = datetime.strftime(
                datetime.strptime(check_user[2], "%Y-%m-%d %H:%M:%S.%f"), "%d.%m.%Y"
            )
            if datetime.strptime(date, "%d.%m.%Y") > datetime.now():
                await bot.send_message(
                    message.from_user.id,
                    text=f"Пользователь {check_user[1]}.\nПодписка действительна до {date}.\nВыберите действие.",
                    reply_markup=kbd.admin_user_keyboard2,
                )
            else:
                await bot.send_message(
                    message.from_user.id,
                    text=f"Пользователь {check_user[1]}.\nПодписка недействительна.\nВыберите действие.",
                    reply_markup=kbd.admin_user_keyboard1,
                )
        else:
            await bot.send_message(
                message.from_user.id,
                text=f"Пользователь {check_user[1]}.\nПодписка недействительна.\nВыберите действие.",
                reply_markup=kbd.admin_user_keyboard1,
            )
        await state.set_state(Form.select_action)
    else:
        await bot.send_message(
            message.from_user.id,
            text="Мы не нашли такого пользователя. Попробуйте снова.\nЕсли у пользователя нет никнейма, введите его "
                 "id.\nПолучить id можно у @username_to_id_bot",
        )


@dp.message(Form.select_action)
async def select_action(message: Message, state: FSMContext):
    if message.text == kbd.button_text_append:
        await bot.send_message(
            message.from_user.id,
            text="На сколько пользователю нужно продлить подписку?",
            reply_markup=kbd.keyboard_subscribes,
        )
        await state.set_state(Form.select_time)

    elif message.text == kbd.button_text_remove:
        data = await state.get_data()
        db.remove_time(data["user_id"])
        await bot.send_message(
            message.from_user.id,
            text="Подписка обнулена",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()


@dp.message(Form.select_time)
async def select_time(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text in cfg.dates:
        db.add_time(data["user_id"], cfg.dates[message.text])
        await bot.send_message(
            message.from_user.id, text=f"Добавил пользователю: {message.text}"
        )
        await bot.send_message(
            data["user_id"],
            text=cfg.format_notification(data["username"], message.text),
        )
    elif message.text == "Выйти":
        await bot.send_message(
            message.from_user.id,
            "Вы вышли из админ панели",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()


@dp.message(F.text == "Отправить сообщение подписчикам", Form.admin)
async def send_message_to_subscribers(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        "Введите текст сообщения, который хотите отправить подписчикам:",
        reply_markup=kbd.keyboard_cancel,
    )
    await state.set_state(Form.enter_message)


@dp.message(Form.enter_message)
async def enter_message_to_send(message: Message, state: FSMContext):
    subscribers = db.get_subscriptions()

    for subscriber in subscribers:
        if db.get_status(int(subscriber[1])):
            await bot.send_message(
                int(subscriber[1]),
                message.text
            )

    await bot.send_message(
        message.from_user.id,
        "Сообщение успешно отправлено всем подписчикам.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()


@dp.message(F.text == "Отправить сообщение всем пользователям", Form.admin)
async def send_message_to_all_users(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        "Введите текст сообщения, который хотите отправить всем пользователям:",
        reply_markup=kbd.keyboard_cancel,
    )
    await state.set_state(Form.enter_message_all)


@dp.message(Form.enter_message_all)
async def enter_message_to_send_all(message: Message, state: FSMContext):
    users = db.get_subscriptions()

    for user in users:
        await bot.send_message(
            int(user[1]),
            message.text
        )

    await bot.send_message(
        message.from_user.id,
        "Сообщение успешно отправлено всем пользователям.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()
