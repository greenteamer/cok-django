# Quick Fix: 403 Forbidden on Static Files

## Problem
After running `make deploy` or `make deploy-static`, you get 403 errors when loading static/media files.

## Root Cause
Docker containers create files with root ownership. Nginx (running as `www-data`) cannot read them.

## Solution (On Production Server)

### Option 1: Automatic Fix
```bash
make fix-permissions
```

### Option 2: Manual Fix
```bash
# Fix staticfiles
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Fix media
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/

# Reload nginx
sudo systemctl reload nginx
```

### Option 3: SELinux Issue (If above doesn't help)
```bash
# Check if SELinux is blocking nginx
sudo tail -f /var/log/nginx/error.log

# Temporary disable SELinux
sudo setenforce 0

# Permanent fix: Set correct SELinux context
sudo chcon -Rt httpd_sys_content_t staticfiles/
sudo chcon -Rt httpd_sys_content_t media/
```

## Prevention

From now on, **always use**:
```bash
make deploy-static  # Automatically fixes permissions
```

Instead of:
```bash
docker-compose exec web python manage.py collectstatic  # ❌ Wrong on production
```

## Verification

Test that static files are accessible:
```bash
curl -I https://your-domain.com/static/admin/css/base.css
# Should return: HTTP/2 200
```

Check nginx error log:
```bash
sudo tail -f /var/log/nginx/error.log
```

## Related Documentation
- Full deployment guide: `docs/guides/deployment.md`
- Static files handling: `docs/architecture/data-flow.md`
