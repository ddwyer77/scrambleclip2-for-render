# Render CLI Integration Guide

This guide explains how to use the Render CLI integration with Cursor to manage your ScrambleClip2 deployment.

## Setup

1. **Install Render CLI**:
   - Make the setup script executable:
     ```bash
     chmod +x render-cli-setup.sh
     ```
   - Run the setup script:
     ```bash
     ./render-cli-setup.sh
     ```
   - Alternatively, in Cursor, use the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and search for "Tasks: Run Task", then select "Render: Install CLI"

2. **Authenticate with Render**:
   ```bash
   render login
   ```
   This will open a browser window where you can log in to your Render account.

3. **Configure Your Service ID**:
   - Make the commands script executable:
     ```bash
     chmod +x render-commands.sh
     ```
   - Set your service ID:
     ```bash
     ./render-commands.sh set-service
     ```
   - This will display a list of your services and prompt you to enter the ID of your ScrambleClip2 service.
   - Alternatively, in Cursor, use the Command Palette and run the "Render: Set Service ID" task.

## Using Render CLI from Cursor

You can access all Render commands directly from Cursor's Command Palette:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the Command Palette
2. Type "Tasks: Run Task" and press Enter
3. Select one of the Render tasks:
   - **Render: Deploy** - Deploy the latest commit
   - **Render: Status** - Check deployment status
   - **Render: Logs** - Stream service logs
   - **Render: Shell** - Open a shell in your deployed service
   - **Render: List Services** - List all your Render services
   - **Render: Set Service ID** - Configure which service to control

## Using Render CLI from Terminal

You can also use the helper script directly from the terminal:

```bash
# Deploy the latest commit
./render-commands.sh deploy

# Check deployment status
./render-commands.sh status

# Stream logs
./render-commands.sh logs

# Open shell in your deployed service
./render-commands.sh shell

# List all services
./render-commands.sh list

# Show help
./render-commands.sh help
```

## Advanced Usage

### Direct Render CLI Commands

You can also use the Render CLI directly for more advanced operations:

```bash
# List all available commands
render help

# List services in your account
render list services

# View a specific service's environment variables
render services env get YOUR_SERVICE_ID

# Set an environment variable
render services env set YOUR_SERVICE_ID KEY=VALUE
```

### CI/CD Integration

For continuous integration/continuous deployment:

1. Generate an API key in the Render dashboard
2. Add the API key to your CI/CD platform's secrets
3. Use the Render CLI with the API key in your CI/CD pipeline

Example GitHub Actions workflow:
```yaml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Render CLI
        run: curl -s https://render.com/download-cli/stable | bash
      - name: Deploy to Render
        run: render deploy --service ${{ secrets.RENDER_SERVICE_ID }}
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
```

## Troubleshooting

- **Command not found**: Ensure the render CLI is in your PATH
- **Authentication issues**: Run `render login` again
- **Permission denied**: Ensure script files are executable with `chmod +x *.sh`
- **Deploy failing**: Check logs with `./render-commands.sh logs` 