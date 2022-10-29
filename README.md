# What this is
Solid starting codebase for new Django(4.1) projects with useful features already included

- [x] Dockerized and easy to start adding new apps(code is using docker volumes, so django development server will autoreload on every code change)
- [x] PostgreSQL integration (+ optional PGAdmin, see docker-compose.yml)
- [x] Basic startup script that makes migrations and creates test users on each app container startup (username: admin, password: 1)
- [x] Django Rest Framework - for easier REST api development and browsable API
- [x] Authorization with Json web tokens with [simplejwt library](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) (you can create users with default django admin)
- [ ] django-debug-toolbar for easier performance tuning (not yet added)
- [x] Useful precommit hooks for Python development including Black, Flake8 and few others (see .pre-commit-config.yaml file)
- [x] Makefile to make our lifes easier, so that we can run common commands easier without need to create aliases in shell


# What it is not
Ready to use deployment version of code, but may become it in the future.

# how to install/run
## Prerequisites on Operating System Level
First make sure all of these are installed on your machine(most of them should be available even on fresh modern Linux installs)
- [x] Python3.8+ and pip (if not installed, visit python.org and download)
- [x] make (if not installed, try https://linuxhint.com/install-make-ubuntu/ or google steps based on your OS)
- [x] black (if not installed, try "python3 -m pip install black" and use it to format python files after, or during writing code, for example on each file save)
- [x] precommit (if not installed, run "python3 -m pip install pre-commit" )
- [x] docker and docker-compose (if not installed, try https://docs.docker.com/engine/install/)

## actual installation
1) initialize pre-commit
```bash
pre-commit install
```
2) start containers
```bash
make up
```
First time downloads and installs may take a while to finish.

# view live site
Visit http://localhost:8000/. You need to log in to access data, so use http://localhost:8000/admin or browsable api to login, use "admin" for username and "1" for password. Users list should now be visible.


# run tests
make test

# everything is working what to do next?
you can start creating new apps and doing whatever you want with them.
For example to create new Django app called posts, run
```bash
make app_exec manage.py startapp posts
```
You also do not want to have endpoint that lists users in base/urls.py file, so you can remove that part of code and corresponding tests.py file from base/tests.py

Look at Makefile for all shortcut commands.

Good Luck!


# things to improve/add
. More tests(including test that jwt part is working)
. github actions/workflows
. Gunicorn
. Coverage
. Redis
. Nginx
. replace pip with Poetry(?)
. some way to automatically update SECRET_KEY in settings.py (?)
