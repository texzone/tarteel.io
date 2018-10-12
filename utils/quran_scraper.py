import requests
from collections import OrderedDict
from bs4 import BeautifulSoup
import csv
import json

MAIN_SITE = "https://sahih-bukhari.com/Pages/Quran/Quran_transliteration.php?id="
QURAN_TABLE = 6
QURAN_DICT = OrderedDict()

# JSON Writer
QURAN_JSON = {'quran': []}

print("Starting...")
# Iterate over all surahs
for surah_num in range(1, 115):
    surah_url = MAIN_SITE + str(surah_num)
    page = requests.get(surah_url)
    # Parse
    soup = BeautifulSoup(page.content, 'html.parser')
    # Get all the tables on the page
    tables = soup.find_all("table")
    quran_table = tables[QURAN_TABLE]
    surah = OrderedDict()
    QURAN_JSON['quran'].append({'num': surah_num, 'name': '', 'ayahs': []})
    # Go Over all Ayahs
    for row in quran_table.find_all('tr'):
        txt = row.find_all('td')
        # num_full is '<surah_num>.<ayah_num>'
        num_full = txt[0].text
        # num_splt is [<surah_num>, <ayah_num>]
        num_split = num_full.split('.')
        ayah_num = num_split[1]
        # Get ayah text and encode properly
        ayah_text = txt[1].text.encode('utf-8')
        # Add to the surah
        surah[ayah_num] = ayah_text
        QURAN_JSON['quran'][surah_num - 1]['ayahs'].append({'num': ayah_num, 'text': ayah_text})
    # Add to the quran
    QURAN_DICT[surah_num] = surah
    print("Finished surah {}".format(surah_num))

# CSV Writer
# print("Writing to CSV...")
# with open("quran_translit.csv", "wb") as csv_file:
#     fields = ["ayah_num", "ayah_text"]
#     w = csv.writer(csv_file)
#     w.writerow(fields)
#     for surah_key in QURAN_DICT:
#         w.writerows(QURAN_DICT[surah_key].items())
#         print("Finished surah {}".format(surah_key))

with open('data-translit.json', 'w') as outfile:
    json.dump(QURAN_JSON, outfile)
