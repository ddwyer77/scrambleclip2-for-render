#!/bin/bash
set -e  # Exit immediately if a command fails

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Render CLI...${NC}"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo -e "${RED}Homebrew is not installed. Please install Homebrew first.${NC}"
    echo -e "Visit: https://brew.sh"
    exit 1
fi

# Install Render CLI
echo -e "${YELLOW}Installing Render CLI with Homebrew...${NC}"
brew tap render-oss/render || { echo -e "${RED}Failed to tap render-oss/render${NC}"; exit 1; }
brew install render || { echo -e "${RED}Failed to install render${NC}"; exit 1; }

# Verify installation
RENDER_PATH=$(which render || echo "")
if [ -z "$RENDER_PATH" ]; then
    echo -e "${RED}Render CLI was not properly installed. Check installation.${NC}"
    exit 1
else
    echo -e "${GREEN}Render CLI installed at: $RENDER_PATH${NC}"
fi

# Check CLI info
echo -e "${YELLOW}Render CLI info:${NC}"
$RENDER_PATH --version

# Provide instructions for authentication
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}IMPORTANT: Authentication must be done outside of Cursor${NC}"
echo -e "1. Open a terminal window outside of Cursor"
echo -e "2. Run: ${GREEN}$RENDER_PATH login${NC}"
echo -e "3. Complete the browser authentication"
echo -e "4. Return to Cursor and use the helper scripts"
echo
echo -e "${YELLOW}After authenticating, you can use:${NC}"
echo -e "- ${GREEN}./render-commands.sh list${NC}"
echo -e "- ${GREEN}./render-commands.sh logs${NC}"
echo -e "- ${GREEN}./render-commands.sh deploy${NC}" 