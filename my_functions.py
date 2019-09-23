import requests
from bs4 import BeautifulSoup


def scraping(input_text):
    # r = requests.get(input_text)
    # soup = BeautifulSoup(r.content, 'html.parser')
    # # 曲名取得
    # song_name = soup.find('title').text.split('ギ')[0]
    # song_name = song_name[:len(song_name) - 1]
    with open('./stafile.txt', 'r') as f:
        song_name = f.read()

    return song_name
