import os
import sys
import time
import traceback

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from src.generator import generate_batch, create_text_overlay
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
except Exception as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def download_sample_video():
    """Download a sample video for testing if none exists."""
    import requests
    
    # Create a samples directory
    os.makedirs("samples", exist_ok=True)
    
    # Check if we already have a sample
    if os.path.exists("samples/sample.mp4"):
        print("Sample video already exists.")
        return "samples/sample.mp4"
    
    # Download a small sample video from a public source
    try:
        url = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"
        print(f"Downloading sample video from {url}")
        
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open("samples/sample.mp4", 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded sample video to samples/sample.mp4")
            return "samples/sample.mp4"
        else:
            print(f"Failed to download video: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading sample video: {e}")
        return None

def test_text_overlay():
    """Test the text overlay functionality directly."""
    print("\n--- Testing Text Overlay ---")
    
    try:
        # Try to create a text overlay
        sample_path = download_sample_video()
        if not sample_path:
            print("No sample video available to use for text test.")
            return False
        
        # Load a video to get dimensions
        clip = VideoFileClip(sample_path)
        
        print("Testing standard text overlay...")
        text_overlay = create_text_overlay(
            "Test Text Overlay",
            size=(clip.w, clip.h),
            color="#FFFFFF",
            font_size=60,
            opacity=1.0,
            stroke_color="#000000",
            stroke_width=2
        )
        
        if text_overlay is None:
            print("ERROR: Text overlay creation failed.")
            return False
        
        print(f"Text overlay created successfully! Size: {text_overlay.size}, Duration: {text_overlay.duration}")
        
        # Try to composite
        try:
            print("Testing compositing text with video...")
            text_overlay = text_overlay.set_duration(clip.duration)
            composite = CompositeVideoClip([clip, text_overlay])
            print(f"Composite created! Size: {composite.size}, Duration: {composite.duration}")
            
            # Save a small test
            output_dir = "test_output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "text_test.mp4")
            
            print(f"Saving test video to {output_path}...")
            composite.write_videofile(
                output_path,
                codec='libx264',
                audio_codec=None,
                verbose=False
            )
            
            print(f"Text overlay test video saved to {output_path}")
            composite.close()
            
            return True
        except Exception as e:
            print(f"Error compositing text overlay: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"ERROR in text overlay test: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            clip.close()
        except:
            pass

def test_full_generator():
    """Test the full video generation pipeline."""
    print("\n--- Testing Full Generator ---")
    
    try:
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get a sample video
        sample_path = download_sample_video()
        if not sample_path:
            print("No sample video available.")
            return False
        
        # Create multiple copies of the same video for testing
        input_videos = [sample_path] * 3  # Use the same video multiple times
        
        print(f"Starting video generation with {len(input_videos)} videos...")
        start_time = time.time()
        
        output_paths = generate_batch(
            input_videos=input_videos,
            num_videos=1,
            output_dir=output_dir,
            use_effects=True,
            use_text=True,
            custom_text="Test Generator Text",
            text_color="#FFFFFF",
            stroke_color="#000000",
            font_size=60,
            stroke_width=2,
            text_opacity=1.0
        )
        
        elapsed = time.time() - start_time
        
        if output_paths and len(output_paths) > 0:
            print(f"SUCCESS: Generated {len(output_paths)} videos in {elapsed:.2f} seconds:")
            for path in output_paths:
                if os.path.exists(path):
                    size_kb = os.path.getsize(path) / 1024
                    print(f"  - {path} ({size_kb:.1f} KB)")
                else:
                    print(f"  - {path} (FILE NOT FOUND)")
            return True
        else:
            print(f"FAILED: No videos generated after {elapsed:.2f} seconds")
            return False
    
    except Exception as e:
        print(f"ERROR in generator test: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== TESTING VIDEO GENERATOR ===")
    print(f"Current directory: {os.getcwd()}")
    
    # Test individual components
    text_result = test_text_overlay()
    print(f"\nText overlay test {'PASSED' if text_result else 'FAILED'}")
    
    # Test full generator
    generator_result = test_full_generator()
    print(f"\nFull generator test {'PASSED' if generator_result else 'FAILED'}")
    
    # Overall result
    if text_result and generator_result:
        print("\nAll tests PASSED! ✅")
        return 0
    else:
        print("\nSome tests FAILED! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 