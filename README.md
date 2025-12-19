# Django Docker Project

Django проект с Docker и docker-compose для легкого развертывания на Ubuntu сервере.

## Стек технологий

- Django 5.0
- PostgreSQL 15
- Gunicorn
- Nginx
- Docker & Docker Compose

## Быстрый старт (локальная разработка)

### 1. Инициализация Django проекта

Если Django проект еще не создан, выполните:

```bash
# Создайте временный контейнер для инициализации проекта
docker run --rm -v $(pwd):/app -w /app python:3.11-slim sh -c "pip install Django==5.0.1 && django-admin startproject config ."
```

### 2. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и установите свои значения, особенно:
- `SECRET_KEY` - сгенерируйте новый секретный ключ
- `DB_PASSWORD` - установите надежный пароль
- `ALLOWED_HOSTS` - добавьте ваш домен

### 3. Настройка Django settings

После создания проекта, отредактируйте `config/settings.py`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise для обслуживания статики
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Добавьте эту строку
    # ... остальные middleware
]
```

### 4. Запуск проекта

```bash
# Сборка и запуск контейнеров
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

Приложение будет доступно по адресу `http://localhost`

## Развертывание на Ubuntu сервере

### Требования

- Ubuntu 20.04+ сервер
- Docker и Docker Compose установлены
- Домен, направленный на IP сервера (опционально)

### Шаги развертывания

#### 1. Установка Docker (если не установлен)

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin -y
```

Выйдите и войдите снова для применения изменений группы.

#### 2. Клонирование проекта

```bash
# Создайте директорию для проекта
mkdir -p ~/apps/django-app
cd ~/apps/django-app

# Склонируйте ваш репозиторий или скопируйте файлы
# git clone <your-repo-url> .
```

#### 3. Настройка окружения

```bash
# Создайте .env файл
cp .env.example .env
nano .env
```

Установите production настройки:
- `SECRET_KEY` - сгенерируйте новый ключ
- `DEBUG=False`
- `ALLOWED_HOSTS` - ваш домен и IP сервера
- `DB_PASSWORD` - надежный пароль

#### 4. Запуск приложения

```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

#### 5. Настройка SSL (опционально, но рекомендуется)

Для production рекомендуется использовать SSL. Можно использовать Certbot:

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d your-domain.com
```

## Полезные команды

```bash
# Остановка контейнеров
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f web

# Выполнение команд Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser

# Создание нового приложения
docker-compose exec web python manage.py startapp myapp

# Бэкап базы данных
docker-compose exec db pg_dump -U django_user django_db > backup.sql

# Восстановление базы данных
docker-compose exec -T db psql -U django_user django_db < backup.sql

# Очистка (удаление контейнеров и volumes)
docker-compose down -v
```

## Структура проекта

```
.
├── config/              # Django настройки проекта
├── nginx/
│   └── nginx.conf      # Конфигурация Nginx
├── staticfiles/        # Собранные статические файлы
├── .env                # Переменные окружения (не в git)
├── .env.example        # Пример переменных окружения
├── .gitignore
├── docker-compose.yml  # Конфигурация Docker Compose
├── Dockerfile          # Dockerfile для Django
├── entrypoint.sh       # Entrypoint скрипт
├── requirements.txt    # Python зависимости
└── README.md
```

## Troubleshooting

### Проблемы с подключением к БД

Если возникают проблемы с подключением к PostgreSQL, проверьте:

```bash
# Проверьте логи базы данных
docker-compose logs db

# Убедитесь, что контейнер БД запущен
docker-compose ps
```

### Проблемы с статическими файлами

```bash
# Пересоберите статические файлы
docker-compose exec web python manage.py collectstatic --noinput
```

### Проблемы с правами доступа

```bash
# Проверьте права на entrypoint.sh
chmod +x entrypoint.sh
```

## Безопасность

Для production окружения:

1. Используйте сильный `SECRET_KEY`
2. Установите `DEBUG=False`
3. Настройте правильные `ALLOWED_HOSTS`
4. Используйте SSL сертификат
5. Регулярно обновляйте зависимости
6. Настройте firewall (UFW)
7. Используйте надежные пароли для БД
8. Регулярно делайте бэкапы

## Лицензия

MIT
