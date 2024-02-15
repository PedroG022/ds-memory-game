import os.path
from os import path
from threading import Thread
from typing import Callable

import requests
from bs4 import BeautifulSoup

cards_amount = 20
pokemon_cards_url = 'https://pokemondb.net/pokedex/national'
output_path = path.join(os.getcwd(), './out/')
delay = 2

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
}


def download(image_url: str, pokemon_name: str):
    with open(path.join(output_path, f'{pokemon_name}.png'), 'wb') as file:
        image_url = requests.get(image_url).content

        file.write(image_url)
        file.close()


def run(on_done: Callable):
    print(os.getcwd())
    print('Parsing and downloading images...')

    if not path.exists(output_path):
        os.mkdir(output_path)
    else:
        print('Skipping download!')
        on_done()
        return

    page_source = requests.get(pokemon_cards_url, headers)
    soup = BeautifulSoup(page_source.text, 'html.parser')

    cards = soup.select('div.infocard')

    print(f'Found {len(cards)} info cards')
    print(f'Downloading {cards_amount} images...')

    pokemon_images = {}

    for card in cards[:cards_amount]:
        name = card.select_one('a.ent-name').text
        url = card.select_one('img.img-fixed').attrs.get('src')

        pokemon_images[name] = url

    dl_threads: list[Thread] = []

    for pokemon in pokemon_images.keys():
        url = pokemon_images[pokemon]
        dl_threads.append(Thread(target=download, args=(url, pokemon)))

    for thread in dl_threads:
        thread.start()

    for thread in dl_threads:
        thread.join()

    print('Done!')
    on_done()
