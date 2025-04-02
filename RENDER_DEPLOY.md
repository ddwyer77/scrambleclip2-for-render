# Deploying ScrambleClip2 on Render

This guide explains how to deploy the ScrambleClip2 application on Render.com.

## Prerequisites

1. A Render.com account
2. GitHub repository with your ScrambleClip2 code

## Option 1: Deploy using Render Blueprint (Recommended)

1. Fork or push this repository to your GitHub account
2. Log in to your Render account
3. Click "New" and select "Blueprint"
4. Connect your GitHub account if you haven't already
5. Select the repository with your ScrambleClip2 code
6. Render will automatically detect the `render.yaml` file and configure the service
7. Click "Apply" to deploy the application

## Option 2: Manual Deployment

1. Log in to your Render account
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service with the following settings:
   - **Name**: scrambleclip2 (or whatever you prefer)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && apt-get update && cat packages.txt | xargs apt-get install -y`
   - **Start Command**: `streamlit run explicit_path_app.py --server.port $PORT --server.enableCORS false`
5. Add the following environment variables:
   - `PYTHONUNBUFFERED`: `true`
   - `IMAGEMAGICK_BINARY`: `/usr/bin/convert`
   - `FFMPEG_BINARY`: `/usr/bin/ffmpeg`
6. Click "Create Web Service" to deploy

## Troubleshooting

If you encounter issues with ImageMagick or other dependencies:

1. Check the app logs in Render
2. Verify that the system packages in `packages.txt` are being installed correctly
3. Make sure that `/usr/bin/convert` exists on the server by checking the environment info in the app's sidebar

## Known Limitations

1. Free tier Render services have memory and CPU limitations which might affect video generation performance
2. Free tier services spin down after inactivity, which may cause a delay on first access
3. Large video files (>50MB) might cause issues due to Render's upload limitations

## Additional Notes

The app is configured to look for ImageMagick at `/usr/bin/convert` on Render's servers. If this path changes in the future, you may need to update the `IMAGEMAGICK_BINARY` environment variable. 