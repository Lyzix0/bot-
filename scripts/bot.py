import types
from datetime import datetime

from aiogram import Dispatcher, Bot, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import scripts.config as cfg
import scripts.database
import scripts.keyboards as kbd

TOKEN = cfg.config["bot_api"]
dp = Dispatcher()
db = scripts.database.Database("users.db")
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


class Form(StatesGroup):
    enter_admin_username = State()
    enter_message_all = State()
    enter_message = State()
    admin = State()
    enter_name = State()
    select_action = State()
    select_time = State()


@dp.message(F.text == kbd.cancel_button.text)
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Отменено✅",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
    await bot.send_message(message.from_user.id, cfg.config["start_text"])


@dp.message(Command("admin"))
async def command_admin(message: Message, state: FSMContext):
    if message.from_user.id in cfg.config["admins"]:
        await bot.send_message(
            message.from_user.id,
            "Вы зашли в админ панель!😊",
            reply_markup=kbd.admin_menu_buttons,
        )
        await state.set_state(Form.admin)
    else:
        await bot.send_message(
            message.from_user.id,
            "Вы не являетесь админом!❌",
        )


@dp.message(F.text == kbd.admin_menu_button.text, Form.admin)
async def renew_subscription(message: Message, state: FSMContext):
    if message.from_user.id in cfg.config["admins"]:
        await bot.send_message(
            message.from_user.id,
            "Введите имя пользователя:",
            reply_markup=kbd.inline_keyboard_back,
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
            text="К сожалению, мы не смогли найти указанного пользователя. Пожалуйста, попробуйте снова.\n"
                 "Если у пользователя нет никнейма, введите его ID.\n"
                 "Вы можете получить ID пользователя с помощью бота @username_to_id_bot",
            reply_markup=kbd.inline_keyboard_back,
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
            text="Подписка обнулена✅",
            reply_markup=kbd.admin_menu_buttons,
        )
        await state.set_state(Form.admin)


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
            "Вы вышли из админ панели✅",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()


@dp.message(F.text == kbd.admin_send_subs.text, Form.admin)
async def send_message_to_subscribers(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        "Введите текст сообщения, который хотите отправить подписчикам:",
        reply_markup=kbd.inline_keyboard_back,
    )
    await state.set_state(Form.enter_message)


@dp.message(Form.enter_message)
async def apply_to_send_subs(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        f"Отправлять сообщение: {message.text}?",
        reply_markup=kbd.inline_apply_subs,
    )
    await state.update_data(text=message.text)
    await state.set_state(Form.admin)


@dp.message(Form.enter_message_all)
async def apply_to_send_all(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        f"Отправлять сообщение: {message.text}?",
        reply_markup=kbd.inline_apply_all,
    )
    await state.update_data(text=message.text)
    await state.set_state(Form.admin)


@dp.message(F.text == kbd.admin_send_all.text, Form.admin)
async def send_message_to_all_users(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        "Введите текст сообщения, который хотите отправить всем пользователям:",
        reply_markup=kbd.inline_keyboard_back,
    )
    await state.set_state(Form.enter_message_all)


@dp.message(Form.enter_message)
async def apply_to_send_all(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        f"Отправлять сообщение: {message.text}?",
        reply_markup=kbd.inline_apply_all,
    )
    await state.update_data(text=message.text)
    await state.set_state(Form.admin)


@dp.message(F.text == kbd.admin_add.text, Form.admin)
async def add_admin(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        "Введите никнейм пользователя, которого вы хотите добавить в администраторы:",
        reply_markup=kbd.inline_keyboard_back,
    )
    await state.set_state(Form.enter_admin_username)


@dp.message(Form.enter_admin_username)
async def enter_admin_username(message: types.Message, state: FSMContext):
    admin_username = message.text

    if db.is_admin(admin_username):
        db.add_admin(admin_username)

        await bot.send_message(
            message.from_user.id,
            f"Пользователь с никнеймом {admin_username} успешно добавлен в список администраторов✅",
            reply_markup=kbd.admin_menu_buttons,
        )
    else:
        await bot.send_message(
            message.from_user.id,
            f"Пользователь с никнеймом {admin_username} не найден. Попробуйте еще раз.",
            reply_markup=kbd.inline_keyboard_back,
        )

    await state.set_state(Form.admin)


@dp.callback_query(lambda query: query.data.startswith("send"))
async def send_subs(query: types.CallbackQuery, state: FSMContext):
    users = db.get_subscriptions()

    texts = await state.get_data()

    if query.data == "send_subs":
        for user in users:
            if db.get_status(int(user[1])):
                await bot.send_message(
                    int(user[1]),
                    texts["text"],
                )

        await bot.send_message(
            query.from_user.id,
            "Сообщение успешно отправлено всем подписчикам✅",
            reply_markup=kbd.admin_menu_buttons,
        )
    elif query.data == "send_all":
        for user in users:
            await bot.send_message(
                int(user[1]),
                texts["text"],
            )

        await bot.send_message(
            query.from_user.id,
            "Сообщение успешно отправлено всем пользователям✅",
            reply_markup=kbd.admin_menu_buttons,
        )

    await query.answer()


@dp.callback_query(lambda query: query.data == "back")
async def button_click(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.admin)
    await query.message.edit_text("Вы вернулись назад")
