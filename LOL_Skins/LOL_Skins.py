import requests
import asyncio
import os
import aiohttp
from aiohttp import ClientSession
import json
from datetime import datetime

async def skins_downloader(semaphore, hero_id, hero_name):
    async with semaphore:
        url = 'https://game.gtimg.cn/images/lol/act/img/js/hero/{}.js'.format(hero_id)
        dir_name = 'skins/{}'.format(hero_name)
        os.makedirs(dir_name, exist_ok=True)
        async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url) as response:
                response = await response.read()
                for skin in json.loads(response)['skins']:
                    if skin['mainImg']:
                        img_url = skin['mainImg']
                        path = os.path.join(dir_name, '{}.jpg'.format(skin['name'].replace('/', ''), ))
                        async with session.get(img_url) as skin_response:
                            with open(path, 'wb') as f:
                                print('\rDownloading[{:^10}] {:<20}'.format(hero_name, skin['name']), end='')
                                f.write(await skin_response.read())

def hero_list():
    return requests.get('https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js').json()['hero']

async def run():
    semaphore = asyncio.Semaphore(30)
    heroes = hero_list()
    tasks = []
    for hero in heroes:
        tasks.append(asyncio.ensure_future(skins_downloader(semaphore, hero['heroId'], hero['title'])))
    await asyncio.wait(tasks)

if __name__ == '__main__':
    start_time = datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
    end_time = datetime.now()
    time_diff = (end_time - start_time).seconds
    print('\nTime cost: {}s'.format(time_diff))
