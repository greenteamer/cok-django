# Развертывание на сервере Ubuntu

## 1. Запустите Docker контейнеры

```bash
make build
```

Django приложение будет доступно на `localhost:8000`

## 2. Миграции и суперпользователь

```bash
make migrate
make createsuperuser
```

## 3. Настройте статические файлы

Соберите статические файлы:

```bash
make collectstatic
```

Создайте директорию для статики на хосте:

```bash
sudo mkdir -p /var/www/coreofkeen.com
sudo cp -r staticfiles /var/www/coreofkeen.com/
sudo cp -r media /var/www/coreofkeen.com/
sudo chown -R www-data:www-data /var/www/coreofkeen.com
```

## 4. Настройте nginx на хосте (без SSL сначала)

Используйте временную конфигурацию без SSL:

```bash
sudo cp nginx/coreofkeen.com.temp.conf /etc/nginx/sites-available/coreofkeen.com
sudo ln -s /etc/nginx/sites-available/coreofkeen.com /etc/nginx/sites-enabled/
```

Проверьте конфигурацию:

```bash
sudo nginx -t
```

Перезапустите nginx:

```bash
sudo systemctl reload nginx
```

## 5. Настройте SSL (HTTPS)

Получите SSL сертификат через certbot:

```bash
sudo certbot --nginx -d coreofkeen.com -d www.coreofkeen.com
```

Certbot автоматически обновит конфигурацию nginx и добавит HTTPS.

**ИЛИ** обновите на финальную конфигурацию вручную:

```bash
sudo cp nginx/coreofkeen.com.conf /etc/nginx/sites-available/coreofkeen.com
sudo nginx -t
sudo systemctl reload nginx
```

## 6. Обновление кода на сервере

После git pull или изменений:

```bash
# Пересобрать контейнер
make build

# Применить миграции
make migrate

# Собрать статику
make collectstatic
sudo cp -r staticfiles /var/www/coreofkeen.com/
```

## Проверка статуса

```bash
make status
make logs
```

## Важные настройки для продакшена

В `.env` на сервере должно быть:

```bash
DEBUG=False
SECRET_KEY=<сгенерируйте длинный случайный ключ>
ALLOWED_HOSTS=localhost,127.0.0.1,coreofkeen.com,www.coreofkeen.com
```
