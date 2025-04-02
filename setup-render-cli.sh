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

# Check version
echo -e "${YELLOW}Render CLI version:${NC}"
render version || { echo -e "${RED}Failed to get render version${NC}"; exit 1; }

# Perform login
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Run '${GREEN}render login${NC}' to authenticate"
echo -e "2. After authentication, you can use '${GREEN}render logs${NC}' and other commands"
echo
echo -e "${YELLOW}Would you like to authenticate now? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Opening browser for authentication...${NC}"
    render login
    echo -e "${GREEN}Authentication complete. You can now use Render CLI commands.${NC}"
else
    echo -e "${YELLOW}Skipping authentication. Remember to run 'render login' before using other commands.${NC}"
fi 