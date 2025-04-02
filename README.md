# ScrambleClip2 - Render Deployment

This repository contains the code for deploying ScrambleClip2 on Render.com.

## What is ScrambleClip2?

ScrambleClip2 is a video editing tool that lets you create unique remixed videos by scrambling clips from existing videos. Features include:

- Upload multiple videos to create a mix of content
- Add custom text overlays to your videos
- Use AI-powered effects to enhance your videos
- Download the generated videos in MP4 format

## Deployment

This repository is configured for easy deployment on Render.com. See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for detailed instructions.

## Local Development

To run this application locally:

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install system dependencies (ImageMagick and ffmpeg)
4. Run the application:
   ```
   streamlit run app.py
   ```

## License

See the original repository for license information.

## Acknowledgements

This is a deployment-ready version of [ScrambleClip2](https://github.com/ddwyer77/scrambleclip2-streamlit-server) adapted for the Render.com platform. 