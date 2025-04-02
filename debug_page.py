import os
import sys
import streamlit as st
import traceback

st.set_page_config(
    page_title="ScrambleClip2 Debug Page",
    page_icon="🔍",
    layout="wide"
)

st.title("ScrambleClip2 Debug Page")

st.markdown("## System Information")
st.write(f"Platform: {sys.platform}")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {os.path.abspath('.')}")
st.write(f"Files in current directory: {os.listdir('.')}")

# Check for scrambleclip2 directory
if os.path.exists('scrambleclip2'):
    st.write(f"Files in scrambleclip2 directory: {os.listdir('scrambleclip2')}")
else:
    st.write("scrambleclip2 directory not found")

# Check for src directory
if os.path.exists('src'):
    st.write(f"Files in src directory: {os.listdir('src')}")
else:
    st.write("src directory not found")

st.markdown("## Python Path")
for path in sys.path:
    st.write(f"- {path}")

st.markdown("## Environment Variables")
env_vars = {k: v for k, v in os.environ.items() if not k.startswith('_')}
st.write(env_vars)

st.markdown("## Import Tests")

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try different import paths
import_paths = [
    "scrambleclip2.src.generator",
    "src.generator",
]

for path in import_paths:
    try:
        st.write(f"Attempting to import from {path}...")
        module = __import__(path, fromlist=['VideoGenerator'])
        VideoGenerator = module.VideoGenerator
        st.success(f"Successfully imported VideoGenerator from {path}")
    except Exception as e:
        st.error(f"Failed to import from {path}: {e}")
        st.code(traceback.format_exc())

st.markdown("## ImageMagick Configuration")

# Try to determine the best path for ImageMagick
if 'IMAGEMAGICK_BINARY' in os.environ:
    IMAGEMAGICK_BINARY = os.environ['IMAGEMAGICK_BINARY']
elif sys.platform == 'darwin':  # macOS
    IMAGEMAGICK_BINARY = "/opt/homebrew/bin/convert"
elif sys.platform.startswith('linux'):  # Linux
    IMAGEMAGICK_BINARY = "/usr/bin/convert"
else:  # Windows or other platforms
    IMAGEMAGICK_BINARY = "convert"  # Assume it's in the PATH

st.write(f"ImageMagick path: {IMAGEMAGICK_BINARY}")
st.write(f"ImageMagick exists: {os.path.exists(IMAGEMAGICK_BINARY)}")

# Try to configure MoviePy
try:
    import moviepy.config as moviepy_config
    moviepy_config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY
    st.success(f"Successfully configured MoviePy to use ImageMagick at: {IMAGEMAGICK_BINARY}")
except Exception as e:
    st.error(f"Failed to configure MoviePy: {e}")
    st.code(traceback.format_exc()) 