#!/bin/bash

# Script to fix permissions for static and media files
# This ensures nginx can read files created by Docker containers

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Fixing File Permissions ===${NC}\n"

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${YELLOW}Project directory:${NC} $PROJECT_DIR"

# Check if staticfiles directory exists
if [ ! -d "$PROJECT_DIR/staticfiles" ]; then
    echo -e "${YELLOW}Creating staticfiles directory...${NC}"
    mkdir -p "$PROJECT_DIR/staticfiles"
fi

# Check if media directory exists
if [ ! -d "$PROJECT_DIR/media" ]; then
    echo -e "${YELLOW}Creating media directory...${NC}"
    mkdir -p "$PROJECT_DIR/media"
fi

# Fix ownership and permissions for staticfiles
echo -e "\n${YELLOW}Setting permissions for staticfiles/...${NC}"
sudo chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
sudo chmod -R 755 "$PROJECT_DIR/staticfiles"
echo -e "${GREEN}✓${NC} staticfiles/ permissions fixed"

# Fix ownership and permissions for media
echo -e "\n${YELLOW}Setting permissions for media/...${NC}"
sudo chown -R www-data:www-data "$PROJECT_DIR/media"
sudo chmod -R 755 "$PROJECT_DIR/media"
echo -e "${GREEN}✓${NC} media/ permissions fixed"

# Show current permissions
echo -e "\n${YELLOW}Current permissions:${NC}"
ls -lhd "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"

echo -e "\n${GREEN}=== Done! ===${NC}"
echo -e "Nginx should now be able to serve static and media files."
echo -e "\nIf you still get 403 errors, check:"
echo -e "  1. SELinux: ${YELLOW}sudo setenforce 0${NC} (temporary)"
echo -e "  2. Nginx logs: ${YELLOW}sudo tail -f /var/log/nginx/error.log${NC}"
