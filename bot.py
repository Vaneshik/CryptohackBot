import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import requests
import time
from datetime import datetime
from collections import Counter

API_TOKEN = "API_TOKEN_HERE"
NICKNAMES = ["peach_lasagna", "cha1ned", "mrFOXY", "Vaneshik",
             "someone12469", "NeketmanX", "Slonser", "himichka", "qumu"]
LAST_REQUEST_TIME = 0
JSON_DATA = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def get_user_data(ses, name):
    url = f"https://cryptohack.org/api/user/{name}"

    async with ses.get(url) as response:
        result_data = await response.json()
        return result_data


async def get_all_data():
    global JSON_DATA, LAST_REQUEST_TIME
    if time.time() - LAST_REQUEST_TIME >= 3600:
        async with aiohttp.ClientSession() as ses:
            tasks = [asyncio.ensure_future(get_user_data(ses, name))
                     for name in NICKNAMES]

            JSON_DATA = await asyncio.gather(*tasks)
            LAST_REQUEST_TIME = time.time()
            return JSON_DATA
    else:
        return JSON_DATA


def format_tasks(fulldata):
    text = "name,    points,    local solves,    all solves\n\n"
    all_data = []
    for user in fulldata:
        solved = user["solved_challenges"]
        all_data.extend(
            [(i["name"], i["category"], i["points"], i["solves"]) for i in solved])
    aboba = Counter(all_data).items()
    sorted_aboba = list(filter(lambda x: x[1] <= int(
        len(NICKNAMES)*0.6), sorted(aboba, key=lambda x: (x[1], x[0][3]), reverse=True)))
    for i, (data, count) in enumerate(sorted_aboba[:30], 1):
        text += f"{i}) {data[0]}, {data[2]}, {count}, {data[3]}\n"
    return text


def format_solves(fulldata):
    text = ""
    all_data = []
    for user in fulldata:
        solved = user["solved_challenges"]
        all_data.extend(
            [(solved[i]["name"], solved[i]["date"], solved[i]["points"], user["username"], i) for i in range(len(solved))])
    sorted_aboba = list(sorted(
        all_data, key=lambda x: (-datetime.strptime(x[1], "%d %b %Y").timestamp(), x[-1])))
    for i, data in enumerate(sorted_aboba[:10], 1):
        text += f"{i}) {data[3]}: {data[0]} +{data[2]}p\n"
    return text


def format_board(fulldata):
    text = ""
    for i, data in enumerate(sorted(fulldata, key=lambda x: x["score"], reverse=True), 1):
        text += f"{i}) {data['username']}: {data['score']}\n"
    return text


@dp.message_handler(commands=['popular_tasks'])
async def send_popular_tasks(message: types.Message):
    fulldata = await get_all_data()
    text = format_tasks(fulldata)
    await message.answer(text)


@dp.message_handler(commands=['last_solves'])
async def send_last_solves(message: types.Message):
    fulldata = await get_all_data()
    text = format_solves(fulldata)
    await message.answer(text)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("CryptoHack bot by @Vaneshik")


@dp.message_handler(commands=['board'])
async def send_board(message: types.Message):
    fulldata = await get_all_data()
    text = format_board(fulldata)
    await message.answer(text)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
