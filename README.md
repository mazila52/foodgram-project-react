![example workflow](https://github.com/mazila52//foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)
# Foodgram
## Описание проекта
 
Foodgram - онлайн-сервис и API для него, пыполнящие роль "продуктового помощника".
В этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 
### Стэк технологий 
 
-   Python 
-   Django 
-   Django Rest Framework
-   Docker
 
## Установка 
 
Для локальной установки прежде всего нужно убедится, что установлен docker-compose с версии 1.25 Далее следует: 
 
-   Клонировать репозиторий: 
 
```bash  
git clone https://github.com/mazila52/foodgram-project-react 
``` 

- Перейдите в папку infra:

```bash  
cd foodgram-project-react

cd infra

docker-compose up -d --build
```
- Создайте в ней файл .env с переменными окружения
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # имя пользователя
POSTGRES_PASSWORD=postgres # пароль
DB_HOST=db
DB_PORT=5432
SECRET_KEY=.... # секретный ключ Django

- Собираем образы и запускаем контейнеры

```bash  
sudo docker-compose up -d --build
```

- Применяем миграции и собираем статику

```bash  
docker-compose exec backend python manage.py migrate

docker-compose exec web python manage.py collectstatic --no-input
```

- Создать суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```
 
-   Эндпойнты будут доступны по адресу: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/) 
 
### Авторы
 
- **Backend** Чубаров Сергей ([@mazila52](https://github.com/mazila52))  
- **Frontend** - [Яндекс.Практикум] (https://github.com/yandex-praktikum/)


### Запущенный проект - [тут](http://51.250.75.67)
