from aiogram.dispatcher.filters.state import StatesGroup, State


class Start(StatesGroup):
    memory_loop = State()