from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_location_request_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='Отправить геолокацию', request_location=True)).row(
        KeyboardButton(text='Отменить')
    )
    return builder.as_markup(resize_keyboard=True)


def get_name_request_keyboard_cancel():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='Отменить'),
    )
    return builder.as_markup(resize_keyboard=True)


def get_location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text='Отправить геолокацию', request_location=True))
    builder.row(KeyboardButton(text='Добавить локацию'))
    builder.row(KeyboardButton(text='Мои локации'))
    return builder.as_markup(resize_keyboard=True)


def get_saved_locations_keyboard(locations):
    builder = InlineKeyboardBuilder()
    for location in locations:
        callback_data = f'location:{location[0]}'
        button_text = f'{location[1]}'
        builder.button(text=button_text, callback_data=callback_data)
    builder.button(text="Удалить локацию", callback_data="delete_location")
    builder.adjust(1)
    return builder.as_markup()
