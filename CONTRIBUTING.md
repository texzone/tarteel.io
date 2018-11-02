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

#### JS Dependencies
1. NodeJS

Download NodeJS v10.13 LTS from [here](https://nodejs.org/en/).
You can also install via a package manager [here](https://nodejs.org/en/download/package-manager/). 
Make sure it is installed globally, not locally.

Check your NodeJS version by running `node -v`.

2. NPX

Use the `npm` to install `npx`
```commandline
npm install npx
```

3. Babel Minify Preset

Install the minify preset for `babel-cli`
```commandline
npm install babel-preset-minify --save-dev
```

### Setup
#### Django
First, setup your Django environment and apply migrations
```commandline
python3 manage.py migrate
```
Make sure you can run the server by running
```commandline
python3 manage.py runserver
```

#### Minifying
Set the minify script as an executable
```commandline
chmod +x minify.sh
```
Run `minify.sh` in the root directory
```commandline
./minify.sh
```

### Conventions
#### Development vs. Production Environment
Minified JS/CSS files should be used when in a production environment, while regular JS/CSS 
files should be used in a development environment. You can change where the script tags are 
pointing to  in the HTML template you are working on. For example, when changing a JS file, you can have
```html
<script src="{% static 'js/api.js' %}"></script>
```
but after making all your changes, you need to run the minify script and change the tag to
```html
<script src="{% static 'js/api.min.js' %}"></script>
```

All PRs should have script tags that point to the minified files. 

#### Pull Requests
Whenever submitting a new PR, create a new branch named using the convention `<username>/<issue>`.
Make sure to include descriptive and clear commit messages, while also referencing any issues your
PR addresses. Your pull request will be reviewed by the maintainers of this repository, and upon approval, will be merged into the master branch. 

All PRs should have their JS/CSS files minified, otherwise it will be rejected.

#### Documentation
Tarteel uses the [reST Documentation Standard](http://docutils.sourceforge.net/rst.html). 
All changes should be well documented and follow the reST convention.