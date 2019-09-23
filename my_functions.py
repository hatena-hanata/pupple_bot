import requests
from bs4 import BeautifulSoup
import pandas as pd
from music_class import *
import pickle

def scraping(input_text):
    r = requests.get(input_text)
    soup = BeautifulSoup(r.content, 'html.parser')
    # 曲名取得
    song_name = soup.find('title').text.split('ギ')[0]
    song_name = song_name[:len(song_name) - 1]

    # Songインスタンス作成
    song = Song(song_name, Chord('C'))

    # コードを読み取る
    chord_lst = soup.find_all('rt')
    for c in chord_lst:
        chord_str = c.text
        if c.text[0] == 'N':
            continue
        chord = Chord(chord_str)
        song.append_chord(chord)

    # 学習データ作成
    df = song.to_DataFrame()
    df = df[df.columns[2:]]
    for col in df.columns:
        df[col] = df[col].astype(float)

    # 学習済みモデル読み込み
    loaded_model = pickle.load(open('./staticfiles/model.pkl', 'rb'))
    le = pickle.load(open('staticfiles/le.pkl', 'rb'))

    # 予測
    pred_y_value = loaded_model.predict(df)
    pred_y_label = le.inverse_transform(pred_y_value)[0]

    if pred_y_label.split('_')[-1] == 'Major':
        answer = pred_y_label.split('_')[0]
    else:
        answer = pred_y_label.split('_')[0] + 'm'

    result = '{} のキーは {} です！'.format(song_name, answer)

    return result


def other_scraping(input_text):
    url = 'https://www.ufret.jp/search.php?key=' + input_text
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # 検索結果あるかチェック
    if 'お探しのキーワードに一致する結果はありませんでした。' in soup.find_all('div', class_='card card-body bg-light p-2')[1].text:
        return 'error'

    tags = soup.find_all('a', class_='list-group-item list-group-item-action')
    if len(tags) > 4:
        tags = tags[:4]
    result = {}
    for tag in tags:
        song_name = tag.find('strong').text
        artist_name = tag.find('span', style='font-size:12px;').text
        if len(song_name) > 8:
            song_name = song_name[:8]
        if len(artist_name) > 8:
            artist_name = artist_name[:8]
        key_name = '{} - {}'.format(song_name, artist_name)
        result[key_name] = 'https://www.ufret.jp' + tag.get('href')

    return result
