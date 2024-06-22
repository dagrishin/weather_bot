from aiogram.fsm.state import StatesGroup, State


class AddLocation(StatesGroup):
    name = State()
    location = State()


class WeatherState(StatesGroup):
    location = State()
