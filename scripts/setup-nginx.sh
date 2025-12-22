#!/bin/bash

# Script to generate Nginx configuration from template
# This replaces {{PROJECT_PATH}} with the actual project directory

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Nginx Configuration Generator ===${NC}\n"

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${YELLOW}Project directory:${NC} $PROJECT_DIR"

# Check if template exists
TEMPLATE_FILE="$PROJECT_DIR/nginx/coreofkeen.com.conf.template"
OUTPUT_FILE="$PROJECT_DIR/nginx/coreofkeen.com.conf"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

# Generate configuration
echo -e "\n${YELLOW}Generating Nginx configuration...${NC}"
sed "s|{{PROJECT_PATH}}|$PROJECT_DIR|g" "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}✓${NC} Configuration generated: $OUTPUT_FILE"

# Show the static/media paths that were set
echo -e "\n${YELLOW}Static files path:${NC} $PROJECT_DIR/staticfiles/"
echo -e "${YELLOW}Media files path:${NC} $PROJECT_DIR/media/"

# Instructions
echo -e "\n${GREEN}=== Next Steps ===${NC}"
echo -e "1. Review the generated configuration:"
echo -e "   ${YELLOW}cat $OUTPUT_FILE${NC}"
echo -e "\n2. Copy to Nginx sites-available:"
echo -e "   ${YELLOW}sudo cp $OUTPUT_FILE /etc/nginx/sites-available/coreofkeen.com${NC}"
echo -e "\n3. Test Nginx configuration:"
echo -e "   ${YELLOW}sudo nginx -t${NC}"
echo -e "\n4. Reload Nginx:"
echo -e "   ${YELLOW}sudo systemctl reload nginx${NC}"

echo -e "\n${GREEN}Done!${NC}"
