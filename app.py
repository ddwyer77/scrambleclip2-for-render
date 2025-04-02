import os
import sys
import streamlit as st
import tempfile
import shutil
from datetime import datetime
import traceback
from io import StringIO
import json
import zipfile

# Set page config FIRST - this must be the first Streamlit command
st.set_page_config(
    page_title="ScrambleClip2 by ClipModeGo",
    page_icon="🎬",
    layout="wide"
)

# Try to determine the best path for ImageMagick
if 'IMAGEMAGICK_BINARY' in os.environ:
    # Use the environment variable if available (this works for Render)
    IMAGEMAGICK_BINARY = os.environ['IMAGEMAGICK_BINARY']
elif sys.platform == 'darwin':  # macOS
    IMAGEMAGICK_BINARY = "/opt/homebrew/bin/convert"
elif sys.platform.startswith('linux'):  # Linux
    IMAGEMAGICK_BINARY = "/usr/bin/convert"
else:  # Windows or other platforms
    IMAGEMAGICK_BINARY = "convert"  # Assume it's in the PATH

# Configure environment variables
os.environ['IMAGEMAGICK_BINARY'] = IMAGEMAGICK_BINARY
os.environ['FFMPEG_BINARY'] = os.environ.get('FFMPEG_BINARY', 'ffmpeg')

# Display platform information in the sidebar
st.sidebar.markdown("## Environment Info")
st.sidebar.write(f"Platform: {sys.platform}")
st.sidebar.write(f"Python version: {sys.version.split()[0]}")
st.sidebar.write(f"ImageMagick path: {IMAGEMAGICK_BINARY}")
st.sidebar.write(f"ImageMagick exists: {os.path.exists(IMAGEMAGICK_BINARY)}")

# Try to manually configure MoviePy
try:
    # Import the config module first and patch it
    import moviepy.config as moviepy_config
    # Override the settings
    moviepy_config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY
    
    # Check if the binary exists
    if os.path.exists(IMAGEMAGICK_BINARY):
        st.sidebar.success(f"ImageMagick found at: {IMAGEMAGICK_BINARY}")
    else:
        st.sidebar.warning(f"ImageMagick binary not found at: {IMAGEMAGICK_BINARY}")
except Exception as e:
    st.sidebar.warning(f"Could not configure MoviePy: {e}")

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Title with custom styling
st.markdown("""
    <h1 style='text-align: center; font-size: 3rem; margin-bottom: 1rem; color: #000000;'>
        ScrambleClip2 by ClipModeGo
    </h1>
    <p style='text-align: center; color: #555555; margin-bottom: 2rem;'>
        Create unique scrambled video remixes with AI-powered clip selection
    </p>
""", unsafe_allow_html=True)

st.write("Upload multiple videos and an audio file to create remixed scrambled versions!")

# Create a temporary directory for uploads
temp_dir = tempfile.mkdtemp()
st.session_state['temp_dir'] = temp_dir

# Create error logging
class ErrorLogger:
    def __init__(self):
        self.errors = []
        self.log_buffer = StringIO()
    
    def log_error(self, error_msg, error_details=None):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.errors.append({
            'timestamp': timestamp,
            'message': error_msg,
            'details': error_details
        })
        
        # Add to log buffer
        self.log_buffer.write(f"[{timestamp}] {error_msg}\n")
        if error_details:
            if isinstance(error_details, dict):
                try:
                    details_str = json.dumps(error_details, indent=2)
                    self.log_buffer.write(f"Debug Info: {details_str}\n")
                except:
                    self.log_buffer.write(f"Debug Info: {str(error_details)}\n")
            else:
                self.log_buffer.write(f"Details: {str(error_details)}\n")
    
    def clear(self):
        self.errors = []
        self.log_buffer = StringIO()
    
    def get_log(self):
        return self.log_buffer.getvalue()
    
    def show(self):
        if not self.errors:
            return
            
        st.markdown("### Error Logs")
        st.code(self.get_log())

error_logger = ErrorLogger()

# Debug information
debug_info = {
    "platform": sys.platform,
    "python_version": sys.version.split()[0],
    "python_path": sys.executable,
    "cwd": os.getcwd(),
    "imagemagick_path": IMAGEMAGICK_BINARY,
    "imagemagick_exists": os.path.exists(IMAGEMAGICK_BINARY)
}
error_logger.log_error("Starting app with debug info", debug_info)

# Add file upload sections
uploaded_videos = st.file_uploader("Upload Videos", type=["mp4", "mov"], accept_multiple_files=True)
uploaded_audio = st.file_uploader("Upload Audio (optional)", type=["mp3", "wav", "m4a"])

# Save uploaded files
video_paths = []

if uploaded_videos:
    st.write(f"Received {len(uploaded_videos)} video files")
    
    for video in uploaded_videos:
        try:
            # Save video file
            video_path = os.path.join(temp_dir, video.name)
            with open(video_path, "wb") as f:
                f.write(video.getbuffer())
            video_paths.append(video_path)
            st.write(f"Saved: {video.name}")
        except Exception as e:
            error_logger.log_error(f"Error saving video {video.name}", str(e))
            st.error(f"Failed to save video: {video.name}")

audio_path = None
if uploaded_audio:
    try:
        # Save audio file
        audio_path = os.path.join(temp_dir, uploaded_audio.name)
        with open(audio_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        st.write(f"Saved audio: {uploaded_audio.name}")
    except Exception as e:
        error_logger.log_error("Error saving audio", str(e))
        st.error(f"Failed to save audio: {uploaded_audio.name}")

# Control options
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        segment_duration = st.slider("Segment Duration (seconds)", min_value=0.5, max_value=5.0, value=0.5, step=0.1)
        num_videos = st.number_input("Number of Output Videos", min_value=1, max_value=10, value=1)
        
    with col2:
        use_effects = st.checkbox("Use AI effects", value=True)
        use_text = st.checkbox("Add text overlay", value=False)

# Text overlay options
overlay_text = None
if use_text:
    with st.expander("Text Overlay Options", expanded=True):
        overlay_text = st.text_input("Text to Display", "WATCH TILL THE END 😱")
        text_color = st.color_picker("Text Color", "#FFFFFF")
        stroke_color = st.color_picker("Outline Color", "#000000")
        font_size = st.slider("Font Size", min_value=20, max_value=100, value=60)
        stroke_width = st.slider("Outline Width", min_value=0, max_value=5, value=2)
        text_opacity = st.slider("Text Opacity", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
        
        # Add debug information
        st.markdown("### Text Overlay Debug Information")
        st.markdown(f"""
            - Text: {overlay_text}
            - Color: {text_color}
            - Stroke Color: {stroke_color}
            - Font Size: {font_size}
            - Stroke Width: {stroke_width}
            - Opacity: {text_opacity}
            - Enabled: {use_text}
        """)

# Generation button
if st.button("Generate Scrambled Videos"):
    if not video_paths:
        st.error("Please upload at least one video")
    else:
        with st.spinner("Generating videos..."):
            try:
                # Clear previous errors
                error_logger.clear()
                error_logger.log_error("Starting video generation", debug_info)
                
                # Create output directory
                output_dir = os.path.join(temp_dir, "output")
                os.makedirs(output_dir, exist_ok=True)
                error_logger.log_error("Created output directory", {
                    "output_dir": output_dir,
                    "exists": os.path.exists(output_dir),
                    "writable": os.access(output_dir, os.W_OK)
                })
                
                try:
                    # Import here, after we've configured the path
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    
                    # Override configuration for current process
                    import moviepy.config
                    moviepy.config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY
                    moviepy.config.change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
                    
                    # Try to find the generator module
                    generator_paths = [
                        "scrambleclip2.src.generator",  # Original path
                        "src.generator",                # Alternative path
                    ]
                    
                    VideoGenerator = None
                    for path in generator_paths:
                        try:
                            module = __import__(path, fromlist=['VideoGenerator'])
                            VideoGenerator = module.VideoGenerator
                            error_logger.log_error(f"Successfully imported VideoGenerator from {path}")
                            break
                        except ImportError as e:
                            error_logger.log_error(f"Failed to import from {path}: {e}")
                    
                    if VideoGenerator is None:
                        raise ImportError("Could not find VideoGenerator in any of the expected modules")
                    
                    # Generate scrambled videos
                    generator = VideoGenerator(video_paths[0])
                    error_logger.log_error("VideoGenerator initialized", {
                        "base_video": video_paths[0],
                        "generator_type": "VideoGenerator"
                    })
                    
                    # Prepare text overlay parameters if enabled
                    text_params = None
                    if use_text and overlay_text:
                        text_params = {
                            'text': overlay_text,
                            'color': text_color,
                            'stroke_color': stroke_color,
                            'font_size': font_size,
                            'stroke_width': stroke_width,
                            'opacity': text_opacity
                        }
                        error_logger.log_error("Text overlay parameters prepared", text_params)
                    
                    # Run generation
                    output_videos = generator.generate_scrambled_videos(
                        num_videos=num_videos,
                        segment_duration=segment_duration,
                        output_dir=output_dir,
                        additional_videos=video_paths[1:] if len(video_paths) > 1 else None,
                        audio_path=audio_path,
                        text_overlay=text_params,
                        use_effects=use_effects
                    )
                    
                    # Display results
                    if output_videos and len(output_videos) > 0:
                        st.success(f"Generated {len(output_videos)} videos!")
                        
                        # Function to create a zip file of all videos
                        def create_zip_of_videos(video_paths):
                            zip_path = os.path.join(temp_dir, "all_videos.zip")
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for video_path in video_paths:
                                    zipf.write(video_path, arcname=os.path.basename(video_path))
                            return zip_path
                        
                        # Display download all button if multiple videos
                        if len(output_videos) > 1:
                            try:
                                zip_path = create_zip_of_videos(output_videos)
                                with open(zip_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download All Videos",
                                        data=f,
                                        file_name="all_videos.zip",
                                        mime="application/zip",
                                        key="download_all_button"
                                    )
                            except Exception as e:
                                st.error(f"Error creating zip file: {e}")
                        
                        # Display videos in a grid
                        num_cols = 3  # Number of columns in the grid
                        rows = [output_videos[i:i + num_cols] for i in range(0, len(output_videos), num_cols)]
                        
                        for row in rows:
                            cols = st.columns(num_cols)
                            
                            for i, video_path in enumerate(row):
                                with cols[i]:
                                    # Display video with reduced height
                                    st.video(video_path, start_time=0)
                                    
                                    # Get just the filename
                                    video_name = os.path.basename(video_path)
                                    
                                    # Display download button
                                    with open(video_path, "rb") as file:
                                        st.download_button(
                                            label=f"⬇️ Download {video_name}",
                                            data=file,
                                            file_name=video_name,
                                            mime="video/mp4",
                                            key=f"download_button_{video_name}"
                                        )
                    else:
                        st.error("No videos were generated. Check the error log.")
                        
                except Exception as e:
                    error_msg = f"Error in video generation: {e}"
                    st.error(error_msg)
                    st.code(traceback.format_exc())
                    error_logger.log_error(error_msg, traceback.format_exc())
                    
            except Exception as e:
                error_msg = f"Error during app execution: {e}"
                st.error(error_msg)
                st.code(traceback.format_exc())
                error_logger.log_error(error_msg, traceback.format_exc())
            
            # Show any errors
            error_logger.show()

# Cleanup on session end
def cleanup():
    if 'temp_dir' in st.session_state:
        try:
            shutil.rmtree(st.session_state['temp_dir'])
            print(f"Cleaned up temporary directory: {st.session_state['temp_dir']}")
        except Exception as e:
            print(f"Error cleaning up: {e}")

# Register cleanup
import atexit
atexit.register(cleanup) 