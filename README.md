# Tarteel.io

Web app: https://tarteel.io/

Tarteel is an open-source project designed to help build digital tools to analyze the recitation of the Quran. Given the important place of reciting the Quran in the lives of Muslims, it is important to build software tools that can help ordinary Muslims recite the Quran with greater accuracy and appreciation. The name tarteel comes from the Quran itself, where God commands us to "recite the Quran with tarteel (slow, measured rhythmic tones)" (73:4).

## Running Instructions in Development:

Prerequisite: Python 3

- (Optional) create a python virtual environment and activate it

1. Install dependencies:

```
pip3 install -r requirements.txt
```
- Note: for step 1, you may need to replace `pip3` with `pip` depending on the name of your pip installation, but regardless, you should be using pip for python version 3.

2. Apply migrations (this sets creates the tables in the local database):

```
python3 manage.py migrate
```

3. Run server:

```
python3 manage.py runserver
```

- Note: for steps 2 and 3, you may need to replace `python3` with `python` depending on the name of your python 3 installation, but regardless, you should be using python version 3.
