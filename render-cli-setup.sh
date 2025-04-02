#!/bin/bash

# Install Render CLI
echo "Installing Render CLI..."
curl -s https://render.com/download-cli/stable | bash

# Add completion for zsh
if [ -f ~/.zshrc ]; then
  echo "Adding Render CLI completion to .zshrc..."
  echo 'eval "$(render completion -s zsh)"' >> ~/.zshrc
fi

# Add completion for bash
if [ -f ~/.bashrc ]; then
  echo "Adding Render CLI completion to .bashrc..."
  echo 'eval "$(render completion -s bash)"' >> ~/.bashrc
fi

echo "Render CLI installation complete!"
echo "Please run 'render login' to authenticate with your Render account." 