Проект развернут по адресу:
`http://foodgram-project.zapto.org`

### Описание:

«Фудграм» — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Как запустить проект:

1. Установить на сервер docker и docker-compose
2. Создать файл `.env` и заполнить его по аналогии с `.env.example` 
3. Добавить в Secrets на Github следующие данные:
```
DB_ENGINE=postgresql #  Тип БД:postgresql, иначе sqlite3
DB_NAME=postgres # Имя базы данных
POSTGRES_USER=postgres # Имя пользователя БД
POSTGRES_PASSWORD=postgres # Пароль пользователя БД
DB_HOST=db # Имя конейнера с БД
DB_PORT=5432 # Порт БД
DOCKER_USERNAME= # Имя пользователя DockerHub
DOCKER_PASSWORD= # Пароль DockerHub
HOST= # IP сервера
USER= # Имя пользователя на удалённом сервере
SSH_KEY= # Закрытый SSH-ключ для подключения к серверу
PASSPHRASE= # Passphrase к закрытому ключу SSH
```
4. Отправить изменения в Git-репозиторий


### Стек технологий:

`Django`
`Django REST framework`
`nginx`
`PostgreSQL`
`Docker`

### Наполнение БД стартовыми данными:

Для наполнения БД стартовыми данными необходимо выполнить `python manage.py load_tags` и `python manage.py load_ingredients` в контейнере `backend`:

```
docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
```

### Документация:

Документация доступна по ссылке `http://<ваше-доменное-имя>/api/docs/`

### Примеры запросов:

Регистрация
```
[POST ](/api/users/)

{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
}
```

Ответ:
```
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов"
}
```


Добавление аватара
```
[PUT ](/api/users/me/avatar/)

{
      "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
}
```

Ответ:
```
{
    "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

Изменение пароля
```
[POST ](/api/users/set_password/)

{
    "new_password": "string",
    "current_password": "string"
}
```

Получить токен авторизации
```
[POST ](/api/auth/token/login/)

{
    "password": "string",
    "email": "string"
}
```

Ответ:
```
{
    "auth_token": "string"
}
```

Создание рецепта
```
[POST ](/api/recipes/)

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Ответ:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

Получение списка тегов.
```
[GET ](/api/tags/)
```

Получение списка ингредиентов.
```
[GET ](/api/ingredients/)
```

Добавить рецепт в избранное.
```
[POST ](/api/recipes/{id}/favorite/)
```

Удалить рецепт из избранного.
```
[DELETE ](/api/recipes/{id}/favorite/)
```

Добавить рецепт в список покупок.
```
[POST ](/api/recipes/{id}/shopping_cart/)
```

Удалить рецепт из списка покупок.
```
[DELETE ](/api/recipes/{id}/shopping_cart/)
```

Скачать список покупок.
```
[GET ](/api/recipes/download_shopping_cart/)
```

Мои подписки.
```
[GET ](/api/users/subscriptions/)
```

Подписаться на пользователя.
```
[POST ](/api/users/{id}/subscribe/)
```

Отписаться от пользователя.
```
[DELETE ](/api/users/{id}/subscribe/)
```

### Автор:

Андрей Владимиров