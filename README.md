# hifz.io

https://tarteel.io/

Running instructions in development:

- At the project dir you can make a virtualenv or not it's up to you
- If you made a venv make sure it's activated then run this.

```
pip install -r requirements.txt
```

- You now Installed the dependencies now you're ready to apply the migrations:

```
python manage.py migrate
```

- then run server:

```
python manage.py runserver
```
