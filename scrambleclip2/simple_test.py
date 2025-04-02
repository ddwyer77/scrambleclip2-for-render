#!/usr/bin/env python3
import os
import sys
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting simple test...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Try to import our generator
try:
    from src.generator import VideoGenerator
    print("Successfully imported VideoGenerator")
except Exception as e:
    print(f"Error importing VideoGenerator: {e}")
    traceback.print_exc()
    sys.exit(1)

# Path to a test video file - replace this with an actual test file path
TEST_VIDEO_PATH = "test_runner/samples/sample.mp4"

def test_generator():
    """Test basic generator functionality"""
    try:
        # Check if test file exists
        test_video_path = TEST_VIDEO_PATH  # Use the global variable
        
        if not os.path.exists(test_video_path):
            print(f"Test file not found: {test_video_path}")
            print("Checking for any MP4 file...")
            
            # Search for any MP4 file
            mp4_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".mp4"):
                        mp4_files.append(os.path.join(root, file))
            
            if not mp4_files:
                print("No MP4 files found for testing")
                return False
                
            test_video_path = mp4_files[0]
            print(f"Using test file: {test_video_path}")
        
        # Initialize generator
        print(f"Initializing generator with {test_video_path}")
        generator = VideoGenerator(test_video_path)
        
        # Set output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a simple video without text
        print("Generating video without text...")
        output_paths = generator.generate_scrambled_videos(
            num_videos=1,
            segment_duration=3.0,
            output_dir=output_dir,
            use_effects=False,
            text_overlay=None
        )
        
        if not output_paths or len(output_paths) == 0:
            print("Failed to generate video without text")
            return False
            
        print(f"Successfully generated video without text: {output_paths[0]}")
        
        # Generate a video with text overlay
        print("\nGenerating video with text overlay...")
        text_overlay = {
            'text': 'Test Text Overlay',
            'color': '#FFFFFF',
            'stroke_color': '#000000',
            'font_size': 60,
            'stroke_width': 2,
            'opacity': 1.0
        }
        
        output_paths_with_text = generator.generate_scrambled_videos(
            num_videos=1,
            segment_duration=3.0,
            output_dir=output_dir,
            use_effects=False,
            text_overlay=text_overlay
        )
        
        if output_paths_with_text and len(output_paths_with_text) > 0:
            print(f"Successfully generated video with text: {output_paths_with_text[0]}")
            return True
        else:
            print("Failed to generate video with text")
            return False
        
    except Exception as e:
        print(f"Error in test_generator: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generator()
    print(f"Test {'passed' if success else 'failed'}")
    sys.exit(0 if success else 1) 