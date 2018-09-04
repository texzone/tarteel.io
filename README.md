# hifz.io

https://tarteel.io/

Running instructions in development:

- At the project dir you can make a virtualenv or not it's up to you
- If you made a venv make sure it's activated then run this.
- Copy and paste the `example-settings.py` file from /docs/ to /hifz_django/ and rename it to `settings.py`

```
pip install -r requirements.txt
```
- Run `python manage.py migrate` to apply previous migrations, otherwise server won't start.
- You've now installed the dependencies and you're ready to run the server: 
```
python manage.py runserver 
```
