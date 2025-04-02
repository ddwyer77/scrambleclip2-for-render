import streamlit as st
import os
import sys
import tempfile
import shutil
import traceback
import platform
import subprocess
from io import StringIO
from datetime import datetime
import zipfile
import io
import json
import psutil

# Add the project root directory to the Python path
# Make sure we have the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Log environment details for debugging
def get_system_info():
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_path": sys.executable,
        "cwd": os.getcwd(),
        "module_path": sys.path,
        "memory_available": f"{psutil.virtual_memory().available / (1024 * 1024):.1f} MB",
        "memory_total": f"{psutil.virtual_memory().total / (1024 * 1024):.1f} MB",
        "cpu_count": psutil.cpu_count(),
        "temp_dir": tempfile.gettempdir(),
        "user_home": os.path.expanduser("~"),
    }
    
    # Check for FFmpeg
    try:
        ffmpeg_version = subprocess.check_output(["ffmpeg", "-version"], universal_newlines=True)
        info["ffmpeg"] = ffmpeg_version.split('\n')[0]
    except:
        info["ffmpeg"] = "Not found or not working"
    
    # Check for MoviePy
    try:
        import moviepy
        info["moviepy"] = moviepy.__version__
    except:
        info["moviepy"] = "Not found or not working"
        
    return info

# Try to import using a more robust approach
try:
    from src.generator import VideoGenerator
    print("Successfully imported VideoGenerator")
except ImportError as e:
    print(f"Error importing VideoGenerator: {e}")
    traceback.print_exc()
    # Fallback to a simpler implementation if needed
    class VideoGenerator:
        def __init__(self, input_video_path):
            self.input_video_path = input_video_path
            
        def generate_scrambled_videos(self, **kwargs):
            # Simplified implementation for testing
            return []

try:
    from src.utils import get_video_duration
    print("Successfully imported get_video_duration")
except ImportError as e:
    print(f"Error importing get_video_duration: {e}")
    traceback.print_exc()
    # Fallback implementation
    def get_video_duration(video_path):
        return 10.0  # Default duration

# Set page config with updated theme
st.set_page_config(
    page_title="ScrambleClip2 by ClipModeGo",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white and black theme with enhanced error display
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F8F8F8;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #333333;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* File uploader */
    .stFileUploader>div {
        background-color: #F8F8F8;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Slider */
    .stSlider>div>div>div {
        background-color: #000000;
    }
    
    /* Number input */
    .stNumberInput>div>div>input {
        background-color: #F8F8F8;
        color: #000000;
        border: 1px solid #DDDDDD;
    }
    
    /* Progress bar */
    .stProgress>div>div>div {
        background-color: #000000;
    }
    
    /* Success message */
    .stSuccess {
        background-color: #F8F8F8;
        border-left: 4px solid #000000;
        padding: 1rem;
        border-radius: 5px;
    }
    
    /* Error message */
    .stError {
        background-color: #F8F8F8;
        border-left: 4px solid #FF4444;
        padding: 1rem;
        border-radius: 5px;
    }
    
    /* Video container */
    .stVideo {
        background-color: #F8F8F8;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Download button */
    .stDownloadButton>button {
        background-color: #F8F8F8;
        color: #000000;
        border: 1px solid #000000;
    }
    
    .stDownloadButton>button:hover {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background-color: #F8F8F8;
        color: #000000;
        border: 1px solid #DDDDDD;
    }
    
    /* Checkbox */
    .stCheckbox>label {
        color: #000000;
    }
    
    /* Debug section styling */
    .debug-section {
        margin-top: 2rem;
        padding: 1rem;
        border: 1px solid #DDD;
        border-radius: 5px;
        background-color: #FAFAFA;
    }
    
    /* System info table */
    .system-info-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .system-info-table th, .system-info-table td {
        border: 1px solid #DDD;
        padding: 0.5rem;
        text-align: left;
    }
    
    .system-info-table th {
        background-color: #F0F0F0;
    }
    
    /* Error log styling */
    .error-log {
        background-color: #FFF8F8;
        border: 1px solid #FF4444;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
        font-size: 0.9rem;
        color: #FF4444;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .error-log pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
    }
    
    .error-log .timestamp {
        color: #888888;
    }
    
    .error-log .message {
        color: #FF4444;
        font-weight: bold;
    }
    
    .error-log .details {
        color: #FF8888;
        margin-left: 1rem;
    }
    
    /* File information styling */
    .file-info {
        background-color: #F8F8FF;
        border: 1px solid #DDDDDD;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

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

# Create a custom error handler
class ErrorLogger:
    def __init__(self):
        self.errors = []
        self.log_buffer = StringIO()
        self.debug_info = {}
    
    def log_error(self, error_msg, error_details=None, debug_info=None):
        timestamp = datetime.now().strftime('%H:%M:%S')
        error_entry = {
            'timestamp': timestamp,
            'message': error_msg,
            'details': error_details
        }
        
        if debug_info:
            error_entry['debug_info'] = debug_info
            self.debug_info.update(debug_info)
            
        self.errors.append(error_entry)
        
        self.log_buffer.write(f"[{timestamp}] {error_msg}\n")
        if error_details:
            self.log_buffer.write(f"Details: {error_details}\n")
        if debug_info:
            self.log_buffer.write(f"Debug Info: {json.dumps(debug_info, indent=2)}\n")
    
    def get_logs(self):
        return self.log_buffer.getvalue()
    
    def clear(self):
        self.errors = []
        self.log_buffer = StringIO()
        self.debug_info = {}

# Create a global error logger
error_logger = ErrorLogger()

# Add system info to the error logger
system_info = get_system_info()
error_logger.log_error("System information collected", None, system_info)

# Collect source directory information
try:
    src_files = os.listdir(os.path.join(current_dir, 'src'))
    error_logger.log_error("Source directory contents", None, {"src_files": src_files})
except Exception as e:
    error_logger.log_error("Error listing source directory", str(e))

# File uploader for multiple videos
uploaded_files = st.file_uploader(
    "Choose video files", 
    type=['mp4', 'mov', 'avi'],
    accept_multiple_files=True
)

# Audio file uploader
uploaded_audio = st.file_uploader(
    "Choose an audio file (optional)",
    type=['mp3', 'wav'],
    accept_multiple_files=False
)

if uploaded_files:
    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Check temp dir permissions
            error_logger.log_error("Temporary directory created", None, {
                "temp_dir": temp_dir,
                "writable": os.access(temp_dir, os.W_OK),
                "exists": os.path.exists(temp_dir)
            })
            
            # Save all uploaded videos
            video_paths = []
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Verify file was written correctly
                file_size = os.path.getsize(temp_path)
                video_paths.append(temp_path)
                
                # Log the file info
                error_logger.log_error(f"Video file saved", None, {
                    "filename": uploaded_file.name,
                    "path": temp_path,
                    "size": file_size,
                    "exists": os.path.exists(temp_path)
                })
        
            # Save audio file if provided
            audio_path = None
            if uploaded_audio:
                audio_path = os.path.join(temp_dir, uploaded_audio.name)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                
                # Log audio file info
                audio_size = os.path.getsize(audio_path)
                error_logger.log_error(f"Audio file saved", None, {
                    "filename": uploaded_audio.name,
                    "path": audio_path,
                    "size": audio_size,
                    "exists": os.path.exists(audio_path)
                })
        
            # Get the shortest video duration for the slider
            durations = []
            for path in video_paths:
                try:
                    duration = get_video_duration(path)
                    durations.append(duration)
                    error_logger.log_error(f"Video duration", None, {
                        "path": path,
                        "duration": duration
                    })
                except Exception as e:
                    error_logger.log_error(f"Error getting video duration", str(e), {
                        "path": path
                    })
            
            if durations:
                min_duration = min(durations)
            else:
                min_duration = 10.0  # Default if no durations could be determined
                st.warning("Could not determine video durations. Using default value of 10 seconds.")
        
            # Create two columns for controls
            col1, col2 = st.columns(2)
        
            with col1:
                # Slider for segment duration
                segment_duration = st.slider(
                    "Segment Duration (seconds)",
                    min_value=0.1,
                    max_value=float(min_duration),
                    value=0.5,
                    step=0.1
                )
        
            with col2:
                # Number of output videos
                num_outputs = st.number_input(
                    "Number of Output Videos",
                    min_value=1,
                    max_value=10,
                    value=1,
                    help="Generate multiple unique versions of the scrambled video"
                )
            
            # Create new row of controls for effects
            fx_col1, fx_col2 = st.columns(2)
            
            with fx_col1:
                # Add AI fx toggle
                use_ai_fx = st.checkbox(
                    "Use AI effects",
                    value=True,
                    help="Apply random visual effects to some segments for more variety"
                )
                
            with fx_col2:
                # Reserved for future options
                pass
        
            # Text overlay options
            st.subheader("Text Overlay Options")
            use_text = st.checkbox("Add text overlay to videos", value=False)
        
            if use_text:
                text_col1, text_col2 = st.columns(2)
            
                with text_col1:
                    # Text input
                    overlay_text = st.text_input(
                        "Enter text to display",
                        placeholder="Your text here...",
                        help="Text will be displayed in the center of the video"
                    )
                
                    # Text color
                    text_color = st.color_picker(
                        "Text Color",
                        "#FFFFFF",
                        help="Choose the color of the text"
                    )
                
                    # Stroke color
                    stroke_color = st.color_picker(
                        "Stroke Color",
                        "#000000",
                        help="Choose the color of the text stroke (outline)"
                    )
            
                with text_col2:
                    # Font size
                    font_size = st.slider(
                        "Font Size",
                        min_value=20,
                        max_value=100,
                        value=60,
                        help="Adjust the size of the text"
                    )
                
                    # Stroke width
                    stroke_width = st.slider(
                        "Stroke Width",
                        min_value=0,
                        max_value=10,
                        value=2,
                        help="Adjust the thickness of the text stroke"
                    )
                
                    # Text opacity
                    text_opacity = st.slider(
                        "Text Opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.00,
                        step=0.1,
                        help="Adjust the transparency of the text"
                    )
            
                # Add debug information
                with st.expander("Text Overlay Debug Information"):
                    st.write(f"""
                        - Text: {overlay_text}
                        - Color: {text_color}
                        - Stroke Color: {stroke_color}
                        - Font Size: {font_size}
                        - Stroke Width: {stroke_width}
                        - Opacity: {text_opacity}
                        - Enabled: {use_text}
                    """)
            
            # Add debug toggle to help troubleshoot issues
            debug_mode = st.checkbox("Enable Debug Mode", value=False, help="Show detailed system information and error logs")
            
            # Button to generate scrambled videos
            if st.button("Generate Scrambled Videos"):
                with st.spinner("Generating scrambled videos..."):
                    try:
                        # Clear previous errors
                        error_logger.clear()
                        
                        # Log system info again
                        error_logger.log_error("Starting video generation", None, get_system_info())
                        
                        # Create output directory
                        output_dir = os.path.join(temp_dir, "output")
                        os.makedirs(output_dir, exist_ok=True)
                        error_logger.log_error("Created output directory", None, {
                            "output_dir": output_dir,
                            "exists": os.path.exists(output_dir),
                            "writable": os.access(output_dir, os.W_OK)
                        })
                        
                        # Generate scrambled videos using all uploaded videos
                        generator = VideoGenerator(video_paths[0])  # Use first video as base
                        error_logger.log_error("VideoGenerator initialized", None, {
                            "base_video": video_paths[0],
                            "generator_type": type(generator).__name__
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
                            error_logger.log_error("Text overlay parameters prepared", None, text_params)
                        
                        # Log all parameters
                        generation_params = {
                            "num_videos": num_outputs,
                            "segment_duration": segment_duration,
                            "output_dir": output_dir,
                            "additional_videos": video_paths[1:],
                            "audio_path": audio_path,
                            "text_overlay": text_params,
                            "use_effects": use_ai_fx
                        }
                        error_logger.log_error("Starting video generation with parameters", None, generation_params)
                        
                        # Start video generation
                        output_paths = generator.generate_scrambled_videos(
                            num_videos=num_outputs,
                            segment_duration=segment_duration,
                            output_dir=output_dir,
                            additional_videos=video_paths[1:],  # Pass all other videos as additional
                            audio_path=audio_path,  # Pass the audio file path
                            text_overlay=text_params,  # Pass text overlay parameters
                            use_effects=use_ai_fx  # Pass effects toggle
                        )
                        
                        # Check output
                        if output_paths:
                            # Log success
                            error_logger.log_error(f"Successfully generated videos", None, {
                                "num_videos": len(output_paths),
                                "output_paths": output_paths,
                                "sizes": [os.path.getsize(p) for p in output_paths if os.path.exists(p)]
                            })
                            
                            st.success(f"Successfully generated {len(output_paths)} videos!")
                            
                            # Create a container for video thumbnails
                            st.subheader("Generated Videos")
                            
                            # Use 3 columns for thumbnails
                            num_cols = 3
                            cols = st.columns(num_cols)
                            
                            # Display all generated videos as thumbnails
                            for i, output_path in enumerate(output_paths, 1):
                                col_idx = (i-1) % num_cols
                                
                                with cols[col_idx]:
                                    # Create a card-like container for each video
                                    st.markdown(f"""
                                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 15px;">
                                            <h4 style="text-align: center;">Video {i}</h4>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Thumbnail (use the actual video)
                                    st.video(output_path, start_time=0)
                                    
                                    # Single download button (replace the view/download columns)
                                    with open(output_path, "rb") as file:
                                        st.download_button(
                                            label=f"Download Video {i}",
                                            data=file,
                                            file_name=f"scrambled_video_{i}.mp4",
                                            mime="video/mp4",
                                            key=f"download_btn_{i}"
                                        )
                                    
                                    # Add file info in debug mode
                                    if debug_mode:
                                        video_size = os.path.getsize(output_path)
                                        st.markdown(f"""
                                            <div class="file-info">
                                                <p><strong>File:</strong> {os.path.basename(output_path)}</p>
                                                <p><strong>Size:</strong> {video_size/1024/1024:.2f} MB</p>
                                                <p><strong>Path:</strong> {output_path}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                            
                            # Add a "Download All Videos" button after displaying all thumbnails
                            st.markdown("---")
                            
                            # Create a zip file in memory
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for i, output_path in enumerate(output_paths, 1):
                                    # Add each video to the zip file
                                    with open(output_path, "rb") as video_file:
                                        video_data = video_file.read()
                                        zip_file.writestr(f"scrambled_video_{i}.mp4", video_data)
                            
                            # Reset buffer position to the beginning
                            zip_buffer.seek(0)
                            
                            # Create a download button centered in the page
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.download_button(
                                    label="📥 Download All Videos",
                                    data=zip_buffer,
                                    file_name="all_scrambled_videos.zip",
                                    mime="application/zip",
                                    help="Download all generated videos as a ZIP file",
                                    key="download_all_btn"
                                )
                                
                                # Add some space after the button
                                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate videos. Please try again.")
                            
                    except Exception as e:
                        error_msg = f"An error occurred: {str(e)}"
                        error_details = traceback.format_exc()
                        error_logger.log_error(error_msg, error_details)
                        
                        # Show a simpler error message with a button to copy logs
                        st.error(f"Error: {str(e)}")
                        
                        # Show detailed error information
                        with st.expander("Show Error Details"):
                            st.error(error_details)
                    
                    # Always show logs in debug mode
                    if debug_mode:
                        st.subheader("Debug Information")
                        
                        # System information table
                        st.markdown("<h3>System Information</h3>", unsafe_allow_html=True)
                        system_info_html = "<table class='system-info-table'><tr><th>Property</th><th>Value</th></tr>"
                        for key, value in system_info.items():
                            system_info_html += f"<tr><td>{key}</td><td>{value}</td></tr>"
                        system_info_html += "</table>"
                        st.markdown(system_info_html, unsafe_allow_html=True)
                        
                        # Error log
                        if error_logger.errors:
                            st.markdown("<h3>Error Logs</h3>", unsafe_allow_html=True)
                            st.markdown(f"""
                                <div class="error-log">
                                    <pre>{error_logger.get_logs()}</pre>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Add a copy button for error logs
                            logs_json = json.dumps(error_logger.get_logs())
                            
                            # JavaScript to copy text to clipboard
                            copy_js = f"""
                            <script>
                            function copyErrorLogs() {{
                                const el = document.createElement('textarea');
                                el.value = JSON.parse('{logs_json}');
                                document.body.appendChild(el);
                                el.select();
                                document.execCommand('copy');
                                document.body.removeChild(el);
                                alert('Error logs copied to clipboard!');
                            }}
                            </script>
                            <button 
                                onclick="copyErrorLogs()" 
                                style="background-color: #F8F8F8; color: #FF4444; border: 1px solid #FF4444; border-radius: 5px; padding: 0.5rem 1rem; cursor: pointer; margin-top: 10px;"
                            >
                                📋 Copy Error Logs
                            </button>
                            """
                            st.markdown(copy_js, unsafe_allow_html=True)
        except Exception as e:
            # Catch-all for any errors in the file handling process
            st.error(f"An error occurred during file processing: {str(e)}")
            st.write(traceback.format_exc())

# Add some helpful information
with st.sidebar:
    st.header("About")
    st.write("""
    Scramble Clip is a tool that takes your videos and creates remixed scrambled versions by:
    1. Breaking them into small segments
    2. Using AI to analyze and select unique segments
    3. Randomly reordering these segments
    4. Adding your chosen background music
    5. Adding custom text overlays (optional)
    
    The result is multiple unique, scrambled versions that combine elements from all your input videos with your chosen audio and text!
    """)
    
    st.header("Instructions")
    st.write("""
    1. Upload multiple video files (MP4, MOV, or AVI)
    2. Upload an audio file (MP3 or WAV) for background music (optional)
    3. Adjust the segment duration using the slider
    4. Choose how many unique videos to generate
    5. Add text overlay (optional)
    6. Click 'Generate Scrambled Videos'
    7. Download your scrambled videos
    """)
    
    # Add debug button in sidebar too
    if st.checkbox("Show System Information", value=False):
        st.subheader("System Information")
        for key, value in system_info.items():
            st.text(f"{key}: {value}") 