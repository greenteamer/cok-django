# Nginx Configuration

This directory contains Nginx configuration files for the project.

## Files

### Tracked in Git

- **`coreofkeen.com.conf.template`** - Configuration template with `{{PROJECT_PATH}}` placeholder
- **`README.md`** - This documentation file

### Generated (ignored by Git)

- **`coreofkeen.com.conf`** - Generated configuration with actual paths (created by `make setup-nginx`)
- **`nginx.conf`** - Legacy file (not used, safe to ignore)

## Usage

### Generate Configuration

To generate Nginx configuration with correct project path:

```bash
# From project root
make setup-nginx

# Or run script directly
./scripts/setup-nginx.sh
```

This will:
1. Detect your project directory automatically
2. Replace `{{PROJECT_PATH}}` with actual path
3. Generate `coreofkeen.com.conf`

### Install Configuration

```bash
# Copy generated config to Nginx
sudo cp nginx/coreofkeen.com.conf /etc/nginx/sites-available/coreofkeen.com

# Enable site (if not already enabled)
sudo ln -s /etc/nginx/sites-available/coreofkeen.com /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Why Templates?

Using templates instead of hardcoded paths provides several benefits:

- ✅ No user-specific paths in version control
- ✅ Works on any server/user automatically
- ✅ Easy to regenerate if project moves
- ✅ Follows best practices for configuration management

## Customization

If you need to customize the configuration:

1. Edit `coreofkeen.com.conf.template`
2. Run `make setup-nginx` to regenerate
3. Copy to Nginx and reload

**Do not edit `coreofkeen.com.conf` directly** - your changes will be lost when regenerating from template.
