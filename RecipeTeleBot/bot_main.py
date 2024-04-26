# the main Bot file

import asyncio
import logging
import sys
from aiogram import Dispatcher, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import (Bold, as_list, as_marked_section)
from aiogram.client.bot import DefaultBotProperties
from recipes_handler import router
from utils import start_menu, MAX_MEALS
from token_data import TOKEN

dp = Dispatcher()
dp.include_router(router)


# processes "/start"
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    text = ('Привет! Вижу, Вы желаете приготовить что-нибудь вкусное и удивить своих близких. '
            'Ознакомьтесь с моими возможностями по кнопкам ниже')
    await start_menu(message, text=text)


# processes "описание бота" and "/description"
@dp.message(lambda message: message.text.lower() in ("описание бота", "/description"))
async def description(message: types.Message):
    await message.answer(text='Я предоставлю информацию о рецептах. '
                              'Выбор случайный, но на основе ваших предпочтений. \n'
                              'Надеюсь оказаться Вам полезным.')


# processes "команды" and "/commands"
@dp.message(lambda message: message.text.lower() in ("команды", "/commands"))
async def commands(message: types.Message):
    response = as_list(
        as_marked_section(
            Bold('commands:'),
            '/start - возвращает Вас на первую страницу Бота',
            f'/category_search_random N - предоставить N случайных блюд на выбор (от 1 до {MAX_MEALS})',
            '/commands - доступные команды',
            '/description - получить описание бота',
            marker="✅ ",
        ),
    )
    await message.answer(**response.as_kwargs())


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
