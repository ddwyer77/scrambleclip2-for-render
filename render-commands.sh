#!/bin/bash

# Define service ID - you'll need to replace this with your actual service ID
# You can find this by running 'render list services' after authenticating
SERVICE_ID="srv-YOUR_SERVICE_ID_HERE"

# Define color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display command help
show_help() {
  echo -e "${BLUE}Render CLI Helper Commands:${NC}"
  echo -e "  ${GREEN}deploy${NC}      - Deploy the latest commit to Render"
  echo -e "  ${GREEN}status${NC}      - Check the deployment status"
  echo -e "  ${GREEN}logs${NC}        - Stream the service logs"
  echo -e "  ${GREEN}shell${NC}       - Start an interactive shell in the service"
  echo -e "  ${GREEN}list${NC}        - List all services in your account"
  echo -e "  ${GREEN}set-service${NC} - Set the service ID for this project"
  echo -e "  ${GREEN}help${NC}        - Show this help menu"
}

# Check if the user is authenticated
check_auth() {
  render whoami > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error:${NC} You are not authenticated with Render CLI."
    echo -e "Please run '${YELLOW}render login${NC}' to authenticate."
    exit 1
  fi
}

# Set the service ID
set_service_id() {
  if [ -z "$1" ]; then
    echo -e "${YELLOW}Available services:${NC}"
    render list services
    echo ""
    echo -e "Enter the service ID from the list above:"
    read new_service_id
  else
    new_service_id=$1
  fi
  
  # Update the SERVICE_ID variable in this file
  sed -i '' "s/SERVICE_ID=\"srv-YOUR_SERVICE_ID_HERE\"/SERVICE_ID=\"$new_service_id\"/" "$0"
  echo -e "${GREEN}Service ID set to:${NC} $new_service_id"
}

# Main function to handle commands
main() {
  # Check if at least one argument is provided
  if [ $# -eq 0 ]; then
    show_help
    exit 0
  fi

  # Process the command
  case "$1" in
    deploy)
      check_auth
      echo -e "${BLUE}Deploying latest commit to Render...${NC}"
      render deploy --service $SERVICE_ID
      ;;
    status)
      check_auth
      echo -e "${BLUE}Checking deployment status...${NC}"
      render services info $SERVICE_ID
      ;;
    logs)
      check_auth
      echo -e "${BLUE}Streaming logs...${NC}"
      render services logs $SERVICE_ID
      ;;
    shell)
      check_auth
      echo -e "${BLUE}Starting interactive shell...${NC}"
      render services shell $SERVICE_ID
      ;;
    list)
      check_auth
      echo -e "${BLUE}Listing all services...${NC}"
      render list services
      ;;
    set-service)
      check_auth
      set_service_id $2
      ;;
    help|--help|-h)
      show_help
      ;;
    *)
      echo -e "${RED}Unknown command:${NC} $1"
      echo -e "Run '${YELLOW}./render-commands.sh help${NC}' for usage information."
      exit 1
      ;;
  esac
}

# Execute the main function with all arguments
main "$@" 