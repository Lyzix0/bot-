from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import scripts.config as cfg

cancel_button = KeyboardButton(text="Отменить❌")
admin_menu_button = KeyboardButton(text="Проверить подписку пользователя👁")
admin_send_all = KeyboardButton(text="Отправить сообщение всем пользователям♾")
admin_send_subs = KeyboardButton(text="Отправить сообщение подписчикам💵")
admin_add = KeyboardButton(text='Добавить админа👤')

inline_keyboard_back = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться назад", callback_data="back")]
    ]
)

inline_apply_subs = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="send_subs"),
            InlineKeyboardButton(text="Нет", callback_data="back"),
        ]
    ]
)

inline_apply_all = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="send_all"),
            InlineKeyboardButton(text="Нет", callback_data="back"),
        ]
    ]
)

buttons = [[admin_menu_button], [admin_send_all], [admin_send_subs], [admin_add], [cancel_button]]

admin_menu_buttons = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
keyboard_cancel = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

buttons = [[KeyboardButton(text="Продлить подписку пользователю✅")], [cancel_button]]
admin_user_keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

button_text_append = "Продлить подписку пользователю✅"
button_text_remove = "Обнулить подписку↩️"
buttons = [
    [KeyboardButton(text=button_text_append)],
    [KeyboardButton(text=button_text_remove)],
    [cancel_button],
]
admin_user_keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

buttons = []
row = []

for key, value in cfg.dates.items():
    subscribe_button = KeyboardButton(text=key)
    row.append(subscribe_button)
    if len(row) == 2:
        buttons.append(row)
        row = []
if row:
    buttons.append(row)

exit_button = KeyboardButton(text="Выйти")
buttons.append([exit_button])
keyboard_subscribes = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
