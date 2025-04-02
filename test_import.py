import os
import sys
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Print current sys.path
print("Python path:")
for path in sys.path:
    print(f"  - {path}")

# Try different import paths
import_paths = [
    "scrambleclip2.src.generator",
    "src.generator",
]

for path in import_paths:
    try:
        print(f"\nAttempting to import from {path}...")
        module = __import__(path, fromlist=['VideoGenerator'])
        VideoGenerator = module.VideoGenerator
        print(f"✓ Successfully imported VideoGenerator from {path}")
    except Exception as e:
        print(f"✗ Failed to import from {path}: {e}")
        print(traceback.format_exc())

# Check if ImageMagick is properly configured
try:
    print("\nChecking ImageMagick configuration...")
    
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
        
    print(f"ImageMagick path: {IMAGEMAGICK_BINARY}")
    print(f"ImageMagick exists: {os.path.exists(IMAGEMAGICK_BINARY)}")
    
    # Try to configure MoviePy
    try:
        import moviepy.config as moviepy_config
        moviepy_config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY
        print(f"Successfully configured MoviePy to use ImageMagick at: {IMAGEMAGICK_BINARY}")
    except Exception as e:
        print(f"Failed to configure MoviePy: {e}")

except Exception as e:
    print(f"Error checking ImageMagick: {e}") 