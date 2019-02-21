## Contributions

Tarteel is an open-source project, which means you can help us make it better! 
Check out the Issues tab to see open issues. 
You're welcome to start with those issues that are tagged with `Good First Issue`, 
tackle other issues, or create your own issues.

## Getting started
Thank you for considering contributing to Tarteel! Here are step-by-step instructions.

### Dependencies
Before starting, you will need to install a few dependencies.

#### Python Dependencies
Tarteel.io uses Python 3.6.7. Run the following command from the root directory.
```commandline
pip3 install -r requirements.txt
```

### Setup
Tarteel uses a `.env` to manage the development environment. You will find a `.env.example` file under the 
`tarteel` folder. Make a copy and rename it to `.env` (`cp .env.example .env`).

#### Database
The default configuration has you setup an sqlite3 database for local testing. 
If you have PostgreSQL installed already, change the `PSQL_URL` in your `.env` file accordingly and the
`DATABASES` string in `tarteel/settings.py` (`DATABASES = { 'default': env.db('PSQL_URL') }`.
 
#### Django
First, setup your Django environment and apply migrations
```commandline
python3 manage.py migrate --run-syncdb
```
Make sure you can run the server by running
```commandline
python3 manage.py runserver
```

### Conventions

#### Pull Requests
Whenever submitting a new PR, create a new branch named using the convention `<username>/<issue>`.
Make sure to include descriptive and clear commit messages, while also referencing any issues your
PR addresses. Your pull request will be reviewed by the maintainers of this repository, and upon approval, will be merged into the master branch. 

#### Documentation
Tarteel uses the [reST Documentation Standard](http://docutils.sourceforge.net/rst.html). 
All changes should be well documented and follow the reST convention.