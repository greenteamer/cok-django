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

## 4. Настройте Cloudflare SSL/TLS

**ВАЖНО**: Если используете Cloudflare, установите SSL/TLS режим на **"Full (strict)"**:

1. Зайдите в Cloudflare Dashboard
2. Выберите ваш домен
3. SSL/TLS → Overview
4. Установите режим: **Full (strict)**

Это предотвратит бесконечные редиректы и обеспечит шифрование между Cloudflare и вашим сервером.

## 5. Настройте SSL сертификат (если еще нет)

Если SSL сертификат еще не установлен, получите его через certbot:

```bash
sudo certbot --nginx -d coreofkeen.com -d www.coreofkeen.com
```

## 6. Настройте nginx на хосте

Скопируйте финальную конфигурацию:

```bash
sudo cp nginx/coreofkeen.com.conf /etc/nginx/sites-available/coreofkeen.com
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

## 7. Обновление кода на сервере

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
