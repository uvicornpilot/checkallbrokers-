# Инструкции по развертыванию Broker Control

## Локальная разработка

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd BrokerControl

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### 4. Запуск сервера разработки

```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## Продакшен развертывание

### 1. Подготовка сервера

#### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server -y

# Установка Node.js (для сборки статических файлов)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### CentOS/RHEL

```bash
# Обновление системы
sudo yum update -y

# Установка необходимых пакетов
sudo yum install python3 python3-pip nginx postgresql postgresql-server redis -y

# Установка Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### 2. Настройка PostgreSQL

```bash
# Инициализация базы данных
sudo postgresql-setup initdb

# Запуск PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создание пользователя и базы данных
sudo -u postgres psql

CREATE DATABASE brokercontrol;
CREATE USER brokercontrol_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE brokercontrol TO brokercontrol_user;
ALTER USER brokercontrol_user CREATEDB;
\q
```

### 3. Настройка Redis

```bash
# Запуск Redis
sudo systemctl start redis
sudo systemctl enable redis

# Проверка работы
redis-cli ping
```

### 4. Развертывание приложения

```bash
# Создание пользователя для приложения
sudo useradd -m -s /bin/bash brokercontrol
sudo usermod -aG sudo brokercontrol

# Переключение на пользователя приложения
sudo su - brokercontrol

# Клонирование репозитория
git clone <repository-url> /home/brokercontrol/brokercontrol
cd /home/brokercontrol/brokercontrol

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание файла .env
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://brokercontrol_user:your_secure_password@localhost/brokercontrol
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
STATIC_ROOT=/home/brokercontrol/brokercontrol/staticfiles
MEDIA_ROOT=/home/brokercontrol/brokercontrol/media
EOF

# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic --noinput

# Создание директорий для медиа файлов
mkdir -p media
chmod 755 media
```

### 5. Настройка Gunicorn

```bash
# Создание файла конфигурации Gunicorn
sudo tee /etc/systemd/system/brokercontrol.service > /dev/null << EOF
[Unit]
Description=Broker Control Gunicorn daemon
After=network.target

[Service]
User=brokercontrol
Group=brokercontrol
WorkingDirectory=/home/brokercontrol/brokercontrol
Environment="PATH=/home/brokercontrol/brokercontrol/venv/bin"
ExecStart=/home/brokercontrol/brokercontrol/venv/bin/gunicorn --workers 3 --bind unix:/home/brokercontrol/brokercontrol/brokercontrol.sock broker_control.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Запуск Gunicorn
sudo systemctl start brokercontrol
sudo systemctl enable brokercontrol
```

### 6. Настройка Nginx

```bash
# Создание конфигурации Nginx
sudo tee /etc/nginx/sites-available/brokercontrol > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/brokercontrol/brokercontrol;
    }
    
    location /media/ {
        root /home/brokercontrol/brokercontrol;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/brokercontrol/brokercontrol/brokercontrol.sock;
    }
}
EOF

# Активация сайта
sudo ln -s /etc/nginx/sites-available/brokercontrol /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Автоматическое обновление сертификата
sudo crontab -e
# Добавить строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Настройка Celery (опционально)

```bash
# Создание файла конфигурации Celery
sudo tee /etc/systemd/system/brokercontrol-celery.service > /dev/null << EOF
[Unit]
Description=Broker Control Celery Worker
After=network.target

[Service]
Type=forking
User=brokercontrol
Group=brokercontrol
EnvironmentFile=/home/brokercontrol/brokercontrol/.env
WorkingDirectory=/home/brokercontrol/brokercontrol
ExecStart=/bin/sh -c '\${WorkingDirectory}/venv/bin/celery multi start worker1 \\
  -A broker_control -l info --pidfile=\${WorkingDirectory}/celery/%n.pid \\
  --logfile=\${WorkingDirectory}/celery/%n%I.log'
ExecStop=/bin/sh -c '\${WorkingDirectory}/venv/bin/celery multi stopwait worker1 \\
  --pidfile=\${WorkingDirectory}/celery/%n.pid'
ExecReload=/bin/sh -c '\${WorkingDirectory}/venv/bin/celery multi restart worker1 \\
  -A broker_control -l info --pidfile=\${WorkingDirectory}/celery/%n.pid \\
  --logfile=\${WorkingDirectory}/celery/%n%I.log'

[Install]
WantedBy=multi-user.target
EOF

# Создание директории для Celery
mkdir -p /home/brokercontrol/brokercontrol/celery

# Запуск Celery
sudo systemctl start brokercontrol-celery
sudo systemctl enable brokercontrol-celery
```

## Мониторинг и обслуживание

### 1. Логирование

```bash
# Просмотр логов Gunicorn
sudo journalctl -u brokercontrol

# Просмотр логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Просмотр логов приложения
tail -f /home/brokercontrol/brokercontrol/logs/debug.log
```

### 2. Резервное копирование

```bash
# Создание скрипта резервного копирования
sudo tee /home/brokercontrol/backup.sh > /dev/null << EOF
#!/bin/bash
BACKUP_DIR="/home/brokercontrol/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Создание резервной копии базы данных
pg_dump brokercontrol > \$BACKUP_DIR/db_backup_\$DATE.sql

# Создание резервной копии медиа файлов
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz /home/brokercontrol/brokercontrol/media

# Удаление старых резервных копий (старше 30 дней)
find \$BACKUP_DIR -name "*.sql" -mtime +30 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

# Создание директории для резервных копий
mkdir -p /home/brokercontrol/backups

# Установка прав на выполнение
chmod +x /home/brokercontrol/backup.sh

# Добавление в cron (ежедневное резервное копирование)
crontab -e
# Добавить строку:
# 0 2 * * * /home/brokercontrol/backup.sh
```

### 3. Обновление приложения

```bash
# Создание скрипта обновления
sudo tee /home/brokercontrol/update.sh > /dev/null << EOF
#!/bin/bash
cd /home/brokercontrol/brokercontrol

# Остановка сервисов
sudo systemctl stop brokercontrol
sudo systemctl stop brokercontrol-celery

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Установка новых зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic --noinput

# Запуск сервисов
sudo systemctl start brokercontrol
sudo systemctl start brokercontrol-celery

echo "Обновление завершено"
EOF

chmod +x /home/brokercontrol/update.sh
```

## Безопасность

### 1. Настройка файрвола

```bash
# Установка UFW
sudo apt install ufw -y

# Настройка правил
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Включение файрвола
sudo ufw enable
```

### 2. Настройка fail2ban

```bash
# Установка fail2ban
sudo apt install fail2ban -y

# Создание конфигурации
sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF

# Перезапуск fail2ban
sudo systemctl restart fail2ban
```

## Производительность

### 1. Оптимизация Nginx

```bash
# Редактирование конфигурации Nginx
sudo nano /etc/nginx/nginx.conf

# Добавить в http блок:
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 2. Кэширование

```bash
# Установка Redis для кэширования
sudo apt install redis-server -y

# Настройка в settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Устранение неполадок

### 1. Проверка статуса сервисов

```bash
sudo systemctl status brokercontrol
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

### 2. Проверка логов

```bash
# Логи Gunicorn
sudo journalctl -u brokercontrol -f

# Логи Nginx
sudo tail -f /var/log/nginx/error.log

# Логи PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 3. Проверка прав доступа

```bash
# Проверка прав на файлы
ls -la /home/brokercontrol/brokercontrol/

# Установка правильных прав
sudo chown -R brokercontrol:brokercontrol /home/brokercontrol/brokercontrol/
sudo chmod -R 755 /home/brokercontrol/brokercontrol/
```

---

**Примечание**: Замените `yourdomain.com`, `your_secure_password` и другие параметры на ваши реальные значения. 