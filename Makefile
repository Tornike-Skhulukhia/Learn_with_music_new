
# start containers and view their logs
up:
	docker-compose up --build -d && docker-compose logs -f

# stop containers
down:
	docker-compose down -t 1

logs:
	docker-compose logs -f --tail=100

# stop containers and then start
down_up:
	docker-compose down && docker-compose up --build -d && docker-compose logs -f

make app_log:
	docker-compose logs -f app

# log into django app container(useful to debug things lets say in tests)
app_bash:
	docker-compose exec app bash

# start django shell
app_shell:
	docker-compose exec ./manage.py shell

# execute django tests
test:
	docker-compose exec app ./manage.py test

# run make migrations command
app_makemigrations:
	docker-compose exec app ./manage.py makemigrations

# run migrate command
app_migrate:
	docker-compose exec app ./manage.py migrate
