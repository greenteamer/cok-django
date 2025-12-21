# Production Deployment Guide

This guide covers deploying the application to production on an Ubuntu server.

## Prerequisites

Before deploying to production, ensure you have:

- **Ubuntu 20.04+** server with root or sudo access
- **Domain name** pointed to server IP (optional but recommended)
- **SSH access** to the server
- **At least 1GB RAM** (2GB+ recommended)
- **10GB+ disk space**

---

## Deployment Overview

Production deployment architecture:

```
Internet → Cloudflare → Nginx (Host) → Gunicorn (Container) → PostgreSQL (Container)
```

Key differences from development:
- `DEBUG=False`
- Nginx serves static files
- Strong secrets
- SSL/TLS enabled
- Security middleware active

---

## Step 1: Server Preparation

### 1.1 Install Docker

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Install additional tools
sudo apt install make git -y
```

**Log out and log back in** for group changes to take effect.

Verify installation:
```bash
docker --version
docker-compose --version
```

---

### 1.2 Configure Firewall

```bash
# Install UFW if not installed
sudo apt install ufw -y

# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## Step 2: Deploy Application

### 2.1 Clone Repository

```bash
# Create application directory
mkdir -p ~/apps
cd ~/apps

# Clone repository (replace with your repo URL)
git clone <your-repo-url> cokdjango
cd cokdjango

# Or upload files via scp/rsync
```

---

### 2.2 Configure Environment

```bash
# Create .env file
cp .env.example .env
nano .env
```

**Production `.env` configuration**:

```bash
# Django settings
SECRET_KEY=<GENERATE_STRONG_KEY>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,coreofkeen.com,www.coreofkeen.com

# Database settings
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=<GENERATE_STRONG_PASSWORD>
DB_HOST=db
DB_PORT=5432
```

**Generate strong secrets**:

```bash
# Generate SECRET_KEY
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generate DB_PASSWORD
openssl rand -base64 32
```

**Security checklist**:
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] Strong `DB_PASSWORD` (20+ random characters)
- [ ] Correct `ALLOWED_HOSTS` (your domain and server IP)

Set file permissions:
```bash
chmod 600 .env
```

---

### 2.3 Start Application

```bash
# Build and start containers
make build

# Apply migrations
make migrate

# Collect static files
make collectstatic

# Create superuser
make createsuperuser
```

**Verify containers are running**:
```bash
make status
```

Expected output:
```
NAME                 STATUS    PORTS
cokdjango-db-1       Up        0.0.0.0:5432->5432/tcp
cokdjango-web-1      Up        0.0.0.0:8000->8000/tcp
```

**Test application**:
```bash
curl http://localhost:8000/admin/
```

Should return HTML (not error).

---

## Step 3: Configure Nginx

### 3.1 Install Nginx

```bash
sudo apt install nginx -y
```

---

### 3.2 Copy Static Files to Host

```bash
# Create directory for static files
sudo mkdir -p /var/www/coreofkeen.com

# Copy static and media files
sudo cp -r staticfiles /var/www/coreofkeen.com/
sudo mkdir -p media
sudo cp -r media /var/www/coreofkeen.com/

# Set ownership
sudo chown -R www-data:www-data /var/www/coreofkeen.com
```

---

### 3.3 Configure Nginx (HTTP Only, for SSL setup)

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/coreofkeen.com
```

**Initial configuration** (HTTP only, for Let's Encrypt):

```nginx
server {
    listen 80;
    server_name coreofkeen.com www.coreofkeen.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/coreofkeen.com/staticfiles/;
    }

    location /media/ {
        alias /var/www/coreofkeen.com/media/;
    }
}
```

**Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/coreofkeen.com /etc/nginx/sites-enabled/
```

**Remove default site** (optional):
```bash
sudo rm /etc/nginx/sites-enabled/default
```

**Test configuration**:
```bash
sudo nginx -t
```

Expected output:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**Reload Nginx**:
```bash
sudo systemctl reload nginx
```

---

## Step 4: SSL/TLS Setup

### 4.1 Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

### 4.2 Obtain SSL Certificate

```bash
sudo certbot --nginx -d coreofkeen.com -d www.coreofkeen.com
```

You'll be prompted:
1. Enter email address (for renewal notifications)
2. Agree to Terms of Service
3. Choose whether to redirect HTTP to HTTPS (choose "2" for redirect)

Certbot will:
- Validate domain ownership
- Obtain certificate from Let's Encrypt
- Modify Nginx configuration to use HTTPS
- Set up automatic renewal

**Verify certificate**:
```bash
sudo certbot certificates
```

---

### 4.3 Update Nginx Configuration (SSL)

Certbot should have modified the config. Verify:

```bash
sudo nano /etc/nginx/sites-available/coreofkeen.com
```

Should include:
```nginx
server {
    listen 443 ssl;
    server_name coreofkeen.com www.coreofkeen.com;

    ssl_certificate /etc/letsencrypt/live/coreofkeen.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/coreofkeen.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... rest of configuration
}

server {
    listen 80;
    server_name coreofkeen.com www.coreofkeen.com;
    return 301 https://$host$request_uri;
}
```

**Reload Nginx**:
```bash
sudo systemctl reload nginx
```

---

## Step 5: Cloudflare Configuration

If using Cloudflare as CDN/DDoS protection:

### 5.1 Cloudflare SSL/TLS Mode

**CRITICAL**: Set SSL/TLS encryption mode to **"Full (strict)"**

1. Go to Cloudflare Dashboard
2. Select your domain
3. Navigate to **SSL/TLS** → **Overview**
4. Set mode to **"Full (strict)"**

**Why**: This prevents infinite redirect loops. Modes explained:
- **Flexible**: Cloudflare ↔ Origin is HTTP (insecure, causes redirect loop)
- **Full**: Cloudflare ↔ Origin is HTTPS with self-signed cert (insecure)
- **Full (strict)**: Cloudflare ↔ Origin is HTTPS with valid cert (correct)

---

### 5.2 Verify HTTPS

Visit your domain:
```
https://coreofkeen.com/admin/
```

Should:
- ✅ Load without errors
- ✅ Show valid SSL certificate
- ✅ Redirect HTTP to HTTPS
- ✅ No infinite redirect loop

---

## Step 6: Post-Deployment Verification

### 6.1 Run Deployment Checklist

```bash
docker-compose exec web python manage.py check --deploy
```

This checks for common security issues. Fix any warnings.

---

### 6.2 Verify Static Files

```bash
curl https://coreofkeen.com/static/admin/css/base.css
```

Should return CSS content (not 404 or error).

---

### 6.3 Verify Admin Access

1. Visit `https://coreofkeen.com/admin/`
2. Login with superuser credentials
3. Check that admin interface loads correctly

---

### 6.4 Check Logs

```bash
make logs
```

Look for:
- No errors or warnings
- Gunicorn workers started
- No database connection errors

---

## Maintenance Tasks

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild containers
make build

# Apply new migrations
make migrate

# Collect static files
make collectstatic

# Copy static files to Nginx directory
sudo cp -r staticfiles /var/www/coreofkeen.com/

# Restart containers
make restart
```

---

### Database Backups

**Create backup**:
```bash
make backup
```

This creates `backup_YYYYMMDD_HHMMSS.sql`.

**Automated backups** (cron job):
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd ~/apps/cokdjango && make backup

# Keep backups for 7 days
0 3 * * * find ~/apps/cokdjango/backup_*.sql -mtime +7 -delete
```

**Restore from backup**:
```bash
docker-compose exec -T db psql -U django_user django_db < backup.sql
```

---

### SSL Certificate Renewal

Certbot automatically renews certificates. Verify:

```bash
# Test renewal
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

Certificates renew automatically when they have 30 days or less remaining.

---

### View Logs

```bash
# Application logs
make logs

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

---

### Restart Services

```bash
# Restart application containers
make restart

# Restart Nginx
sudo systemctl restart nginx

# Restart Docker daemon (if needed)
sudo systemctl restart docker
```

---

## Monitoring and Observability

### Basic Health Check

Create a health check endpoint:

```python
# In config/urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('health/', health_check),
    # ... other patterns
]
```

Test:
```bash
curl https://coreofkeen.com/health/
```

---

### Resource Monitoring

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check Docker container resources
docker stats

# Check Nginx status
sudo systemctl status nginx

# Check Docker service
sudo systemctl status docker
```

---

## Scaling Considerations

### Horizontal Scaling (Multiple Web Workers)

Scale the `web` service:

```bash
docker-compose up --scale web=3 -d
```

Update Nginx to load balance:

```nginx
upstream django {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    # ... rest of config
    location / {
        proxy_pass http://django;
        # ...
    }
}
```

Update `docker-compose.yml` to expose different ports:
```yaml
services:
  web:
    ports:
      - "8000-8002:8000"
```

---

### External Database

For production at scale, consider managed PostgreSQL (AWS RDS, DigitalOcean, etc.):

1. Create managed PostgreSQL instance
2. Update `.env` with external database credentials:
   ```bash
   DB_HOST=db.example.com
   DB_PORT=5432
   ```
3. Remove `db` service from `docker-compose.yml`
4. Ensure firewall allows connection from server to database

---

## Troubleshooting Production Issues

### 502 Bad Gateway

**Cause**: Nginx can't connect to Gunicorn

**Solutions**:
1. Check web container is running: `docker-compose ps`
2. Check Gunicorn is listening: `docker-compose logs web`
3. Verify proxy_pass in Nginx config points to `http://localhost:8000`

---

### Static Files Not Loading (404)

**Cause**: Nginx can't find static files

**Solutions**:
1. Verify files exist: `ls /var/www/coreofkeen.com/staticfiles/`
2. Check permissions: `sudo chown -R www-data:www-data /var/www/coreofkeen.com`
3. Verify Nginx config `alias` path is correct
4. Recollect static files: `make collectstatic`

---

### Infinite Redirect Loop

**Cause**: Cloudflare SSL mode misconfigured

**Solution**:
1. Set Cloudflare SSL/TLS to "Full (strict)"
2. Ensure Let's Encrypt certificate is valid: `sudo certbot certificates`
3. Check `SECURE_PROXY_SSL_HEADER` in settings.py

---

### Database Connection Errors

**Cause**: PostgreSQL container not running or wrong credentials

**Solutions**:
1. Check db container: `docker-compose ps db`
2. Check logs: `docker-compose logs db`
3. Verify `.env` credentials match database
4. Restart containers: `make restart`

---

### High Memory Usage

**Solutions**:
1. Reduce Gunicorn workers (edit `docker-compose.yml`, change `--workers 3` to `--workers 2`)
2. Add swap space:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

## Security Hardening

### Additional Security Measures

1. **Disable root SSH login**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PermitRootLogin no
   sudo systemctl restart sshd
   ```

2. **Install fail2ban** (blocks brute force attacks):
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

3. **Automatic security updates**:
   ```bash
   sudo apt install unattended-upgrades -y
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

4. **Hide Nginx version**:
   ```bash
   sudo nano /etc/nginx/nginx.conf
   # Add: server_tokens off;
   sudo systemctl reload nginx
   ```

---

## Rollback Procedure

If deployment fails:

```bash
# Rollback code
git revert HEAD
# Or
git reset --hard <previous-commit>

# Rebuild
make build
make migrate
make collectstatic
sudo cp -r staticfiles /var/www/coreofkeen.com/

# Restart
make restart
```

---

Last Updated: 2025-12-21
