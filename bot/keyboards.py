from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='Send Location', request_location=True))
    builder.row(KeyboardButton(text='Add Location'))
    return builder.as_markup(resize_keyboard=True)


def get_saved_locations_keyboard(locations):
    builder = InlineKeyboardBuilder()
    for location in locations:
        callback_data = f'delete_location:{location[0]}'
        button_text = f'{location[1]}'
        builder.button(text=button_text, callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()
