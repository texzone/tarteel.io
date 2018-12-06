"""
https://github.com/cpfair/quran-tajweed
"""

import io
import json
from restapi.models import AnnotatedRecording

TAJWEED_FILE = 'tajweed.hafs.uthmani-pause-sajdah.json'
UTHMANI_FILE = 'data-uthmani.json'
with io.open(TAJWEED_FILE) as file:
    tajweed_rules = json.load(file)
    file.close()

# with io.open(UTHMANI_FILE) as file:
#     qur = json.load(file)
#     qur = qur['quran']
#     file.close()
#
# a = qur['surahs'][0]['ayahs'][0]['text']
# rule_start = tajweed_rules[0]['annotations'][0]['start']
# a_list = a.split(" ")
# curr_word_ind = 0
# for i, word in enumerate(a_list):
#     position = len(word)
#     # If the start index is in the position we traversed, then its the applicable word
#     if position >= rule_start:
#         curr_word_ind = i
#
# # Make sure we avoid negative count
# prev_word_ind = curr_word_ind - 1 if curr_word_ind > 0 else None
# # Make sure we avoid overflow
# next_word_ind = curr_word_ind + 1 if curr_word_ind + 1 < len(a_list) else None

new_rules = {}
prev_surah = 1
prev_ayah = 1
for rule in tajweed_rules:
    curr_surah = tajweed_rules['surah']
    curr_ayah = tajweed_rules['ayah']

