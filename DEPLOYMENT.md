# Развертывание на сервере Ubuntu

## 1. Запустите Docker контейнеры

```bash
make build
```

Теперь Django приложение будет доступно на `localhost:8000`

## 2. Настройте статические файлы

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

## 3. Настройте nginx на хосте

Скопируйте конфигурацию nginx:

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

## 4. Настройте SSL (HTTPS)

```bash
sudo certbot --nginx -d coreofkeen.com -d www.coreofkeen.com
```

## 5. Миграции и суперпользователь

```bash
make migrate
make createsuperuser
```

## 6. Обновление статики после изменений

После изменения статических файлов:

```bash
make collectstatic
sudo cp -r staticfiles /var/www/coreofkeen.com/
```

## Проверка статуса

```bash
make status
make logs
```
