import requests
from collections import OrderedDict
from bs4 import BeautifulSoup
import csv

MAIN_SITE = "https://sahih-bukhari.com/Pages/Quran/Quran_transliteration.php?id="
QURAN_TABLE = 6
QURAN_DICT = OrderedDict()

print "Starting..."
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
    # Go Over all Ayahs
    for row in quran_table.find_all('tr'):
        txt = row.find_all('td')
        # ayah_num_full is <surah_num>.<ayah_num>
        # ayah_num_full = txt[0].text
        # Get only the ayah_num
        # ayah_num = ayah_num_full.split('.')[1]
        ayah_num = txt[0].text
        # Get ayah text and encode properly
        ayah_text = txt[1].text.encode('utf-8')
        # Add to the surah
        surah[ayah_num] = ayah_text
    # Add to the quran
    QURAN_DICT[surah_num] = surah
    print "Finished surah {}".format(surah_num)

print "Writing to CSV..."
with open("quran_translit.csv", "wb") as csv_file:
    fields = ["ayah_num", "ayah_text"]
    w = csv.writer(csv_file)
    w.writerow(fields)
    for surah_key in QURAN_DICT:
        w.writerows(QURAN_DICT[surah_key].items())
        print "Finished surah {}".format(surah_key)
