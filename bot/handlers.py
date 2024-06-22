from datetime import datetime, timezone, timedelta

from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.db import Database
from bot.weather import get_current_weather, get_weather_forecast, convert_month

db = Database('database/weather_bot.db')
router = Router()


class AddLocation(StatesGroup):
    name = State()
    location = State()


def get_location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Отправить геолокацию', request_location=True))
    builder.row(types.KeyboardButton(text='Добавить локацию'))
    builder.row(types.KeyboardButton(text='Мои локации'))
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


@router.message(Command(commands=["start", "help"]))
async def cmd_start(message: types.Message):
    keyboard = get_location_keyboard()
    await message.answer("Привет! Я бот погоды. Что бы вы хотели сделать?", reply_markup=keyboard)


@router.message(or_f(Command("locations"), F.text == "Мои локации"))
async def show_saved_locations(message: types.Message):
    locations = db.get_locations_by_chat_id(message.chat.id)
    if locations:
        keyboard = get_saved_locations_keyboard(locations)
        await message.answer("Ваши сохраненные локации:", reply_markup=keyboard)
    else:
        await message.answer("У вас пока нет сохраненных локаций.")


def get_location_request_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Отправить геолокацию', request_location=True))
    return builder.as_markup(resize_keyboard=True)


@router.message(or_f(Command("add_location"), F.text == "Добавить локацию"))
async def add_location_start(message: types.Message, state: FSMContext):
    await state.set_state(AddLocation.name)
    await message.answer("Введите название для новой локации:", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(AddLocation.name))
async def add_location_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddLocation.location)
    keyboard = get_location_request_keyboard()
    await message.answer("Теперь отправьте геолокацию для этой локации.", reply_markup=keyboard)


@router.message(StateFilter(AddLocation.location), F.location)
async def add_location_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    latitude = message.location.latitude
    longitude = message.location.longitude

    db.add_location(message.chat.id, name, latitude, longitude)
    await state.clear()

    keyboard = get_location_keyboard()
    await message.answer(f"Локация '{name}' успешно добавлена!", reply_markup=keyboard)


def convert_timezone(time, timezone_offset):
    tz = timezone(timedelta(seconds=timezone_offset))
    forecast_time = datetime.strptime(time, '%H:%M')
    forecast_time_with_timezone = forecast_time.replace(tzinfo=tz)
    return forecast_time_with_timezone.strftime('%H:%M')


@router.callback_query(F.data.startswith("location:"))
async def location_callback(callback: types.CallbackQuery):
    location_id = int(callback.data.split(":")[1])
    locations = db.get_locations_by_chat_id(callback.message.chat.id)
    location = next((loc for loc in locations if loc[0] == location_id), None)

    if location:
        current_weather_data = get_current_weather(location[2], location[3])
        forecast_data = get_weather_forecast(location[2], location[3])

        current_city = current_weather_data['name']
        current_temperature = current_weather_data['main']['temp']
        current_description = current_weather_data['weather'][0]['description']

        current_weather_message = f"Текущая погода в {current_city}: {current_description}, {current_temperature}°C"

        await callback.message.answer(current_weather_message)

        current_date = datetime.now().date()
        forecast_message = ""
        max_temperatures = {}  # Словарь для хранения максимальных температур по дням
        min_temperatures = {}  # Словарь для хранения минимальных температур по дням

        for forecast in forecast_data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()

            if forecast_date != current_date:
                current_date = forecast_date

            temperature = forecast['main']['temp']

            # Обновляем максимальную и минимальную температуру для каждого дня
            if forecast_date not in max_temperatures:
                max_temperatures[forecast_date] = temperature
            else:
                max_temperatures[forecast_date] = max(max_temperatures[forecast_date], temperature)

            if forecast_date not in min_temperatures:
                min_temperatures[forecast_date] = temperature
            else:
                min_temperatures[forecast_date] = min(min_temperatures[forecast_date], temperature)

        for forecast in forecast_data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()

            if forecast_date != current_date:
                current_date = forecast_date
                forecast_message += f"\n{forecast_date.strftime('%d.%m.%Y')}:\n"

            forecast_time = datetime.fromtimestamp(forecast['dt']).strftime('%H:%M')
            forecast_time_with_timezone = convert_timezone(forecast_time, current_weather_data['timezone'])
            temperature = forecast['main']['temp']
            description = forecast['weather'][0]['description']

            if temperature == max_temperatures[forecast_date]:
                forecast_message += f"<b>{forecast_time_with_timezone}</b>: {description}, {temperature}°C\n"
            elif temperature == min_temperatures[forecast_date]:
                forecast_message += f"<i>{forecast_time_with_timezone}</i>: {description}, {temperature}°C\n"
            else:
                forecast_message += f"{forecast_time_with_timezone}: {description}, {temperature}°C\n"

        await callback.message.answer(forecast_message, parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer("Локация не найдена.")


@router.message(Command('delete'))
async def delete_location_start(message: types.Message):
    locations = db.get_locations_by_chat_id(message.chat.id)
    if locations:
        builder = InlineKeyboardBuilder()
        for location in locations:
            builder.button(text=f"Удалить {location[1]}", callback_data=f"confirm_delete:{location[0]}")
        builder.adjust(1)
        await message.answer("Выберите локацию для удаления:", reply_markup=builder.as_markup())
    else:
        await message.answer("У вас нет сохраненных локаций для удаления.")


@router.callback_query(F.data == "delete_location")
async def delete_location_start(callback: types.CallbackQuery):
    locations = db.get_locations_by_chat_id(callback.message.chat.id)
    if locations:
        builder = InlineKeyboardBuilder()
        for location in locations:
            builder.button(text=f"Удалить {location[1]}", callback_data=f"confirm_delete:{location[0]}")
        builder.adjust(1)
        await callback.message.answer("Выберите локацию для удаления:", reply_markup=builder.as_markup())
    else:
        await callback.message.answer("У вас нет сохраненных локаций для удаления.")


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_location(callback: types.CallbackQuery):
    location_id = int(callback.data.split(":")[1])
    db.delete_location(location_id)
    await callback.message.answer("Локация успешно удалена.")
    await show_saved_locations(callback.message)


@router.message(F.location)
async def handle_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    current_weather_data = get_current_weather(latitude, longitude)
    forecast_data = get_weather_forecast(latitude, longitude)

    current_city = current_weather_data['name']
    current_temperature = current_weather_data['main']['temp']
    current_description = current_weather_data['weather'][0]['description']

    current_weather_message = f"Текущая погода в {current_city}: {current_description}, {current_temperature}°C"

    await message.answer(current_weather_message)

    current_date = datetime.now().date()
    forecast_message = ""

    max_temp = float('-inf')
    min_temp = float('inf')

    for forecast in forecast_data['list']:
        forecast_date = datetime.fromtimestamp(forecast['dt']).date()

        if forecast_date != current_date:
            current_date = forecast_date
            forecast_message += f"\n{forecast_date.strftime('%d.%m.%Y')}:\n"

        forecast_time = datetime.fromtimestamp(forecast['dt']).strftime('%H:%M')
        forecast_time_with_timezone = convert_timezone(forecast_time, current_weather_data['timezone'])
        temperature = forecast['main']['temp']
        description = forecast['weather'][0]['description']

        max_temp = max(max_temp, temperature)
        min_temp = min(min_temp, temperature)

        if temperature == max_temp:
            forecast_message += f"<b>{forecast_time_with_timezone}</b>: {description}, {temperature}°C\n"
        elif temperature == min_temp:
            forecast_message += f"<i>{forecast_time_with_timezone}</i>: {description}, {temperature}°C\n"
        else:
            forecast_message += f"{forecast_time_with_timezone}: {description}, {temperature}°C\n"

    await message.answer(forecast_message, parse_mode=ParseMode.HTML)


def register_handlers(bot):
    return router
