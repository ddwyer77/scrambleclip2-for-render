#!/bin/bash

# Find Render CLI
if command -v /opt/homebrew/bin/render &> /dev/null; then
    RENDER_CMD="/opt/homebrew/bin/render"
elif command -v render &> /dev/null; then
    RENDER_CMD="render"
else
    echo "Error: Render CLI not found. Please install it first."
    echo "Run ./setup-render-cli.sh to install Render CLI"
    exit 1
fi

# Define colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service ID - will be set by the set-service function or loaded from .render-service-id
SERVICE_ID=""
SERVICE_ID_FILE=".render-service-id"

# Load service ID if file exists
if [ -f "$SERVICE_ID_FILE" ]; then
    SERVICE_ID=$(cat "$SERVICE_ID_FILE")
fi

# Check if user is authenticated
check_auth() {
    if ! $RENDER_CMD whoami &> /dev/null; then
        echo -e "${RED}Error: You are not authenticated with Render CLI.${NC}"
        echo -e "Please run '${GREEN}$RENDER_CMD login${NC}' to authenticate."
        exit 1
    fi
}

# Display help message
help() {
    echo -e "${BLUE}Render CLI Helper Script${NC}"
    echo -e "${YELLOW}Usage:${NC} ./render-commands.sh [command]"
    echo
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}deploy${NC}        - Deploy the latest changes"
    echo -e "  ${GREEN}status${NC}        - Check deployment status"
    echo -e "  ${GREEN}logs${NC}          - Stream logs from the service"
    echo -e "  ${GREEN}shell${NC}         - Open a shell on the service"
    echo -e "  ${GREEN}list${NC}          - List all services"
    echo -e "  ${GREEN}set-service${NC}   - Set the service ID for future commands"
    echo -e "  ${GREEN}help${NC}          - Display this help message"
    echo
    echo -e "${YELLOW}Example:${NC}"
    echo -e "  ./render-commands.sh deploy"
}

# Set service ID
set_service() {
    echo -e "${YELLOW}Listing available services...${NC}"
    $RENDER_CMD list
    echo
    echo -e "${YELLOW}Enter the service ID to use:${NC}"
    read -r service_id
    echo "$service_id" > "$SERVICE_ID_FILE"
    SERVICE_ID="$service_id"
    echo -e "${GREEN}Service ID set to: $SERVICE_ID${NC}"
}

# Check service ID
check_service_id() {
    if [ -z "$SERVICE_ID" ]; then
        echo -e "${YELLOW}No service ID set. Choose a service:${NC}"
        set_service
    fi
}

# Deploy the latest changes
deploy() {
    check_auth
    check_service_id
    echo -e "${YELLOW}Deploying latest changes to $SERVICE_ID...${NC}"
    $RENDER_CMD deploy --service "$SERVICE_ID"
}

# Check deployment status
status() {
    check_auth
    check_service_id
    echo -e "${YELLOW}Checking status of $SERVICE_ID...${NC}"
    $RENDER_CMD status --service "$SERVICE_ID"
}

# Stream logs from the service
logs() {
    check_auth
    check_service_id
    echo -e "${YELLOW}Streaming logs from $SERVICE_ID...${NC}"
    $RENDER_CMD logs --service "$SERVICE_ID"
}

# Open a shell on the service
shell() {
    check_auth
    check_service_id
    echo -e "${YELLOW}Opening shell on $SERVICE_ID...${NC}"
    $RENDER_CMD ssh --service "$SERVICE_ID"
}

# List all services
list_services() {
    check_auth
    echo -e "${YELLOW}Listing all services...${NC}"
    $RENDER_CMD list
}

# Parse command line arguments
case "$1" in
    deploy)
        deploy
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    shell)
        shell
        ;;
    list)
        list_services
        ;;
    set-service)
        set_service
        ;;
    help|--help|-h)
        help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        help
        exit 1
        ;;
esac 