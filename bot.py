import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import requests

API_TOKEN = "YourTokenHere"
nicknames = ["peach_lasagna", "cha1ned", "mrFOXY", "Vaneshik",
             "someone12469", "NeketmanX", "Slonser", "himichka", "qumu"]

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def get_user_data(ses, name):
    url = f"https://cryptohack.org/api/user/{name}"

    async with ses.get(url) as response:
        result_data = await response.json()
        result = result_data["score"]
        return (name, result)


async def get_board():
    async with aiohttp.ClientSession() as ses:
        tasks = [asyncio.ensure_future(get_user_data(ses, name))
                 for name in nicknames]

        board_tuple = await asyncio.gather(*tasks)
        return board_tuple


def format_board(board):
    text = ""
    for i, (nick, score) in enumerate(sorted(board, key=lambda x: x[1], reverse=True), 1):
        text += f"{i}) {nick}: {score}\n"
    return text


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("CryptoHack bot by @Vaneshik")


@dp.message_handler(commands=['get_board'])
async def send_board(message: types.Message):
    """
    Send formated board
    """
    board = await get_board()
    text = format_board(board)
    await message.answer(text)



def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
