#!/usr/bin/env python3
import os
import sys
import traceback
from PIL import Image, ImageDraw, ImageFont
import numpy as np

print("Starting test script")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Try to load required libraries
try:
    import moviepy
    print(f"MoviePy version: {moviepy.__version__}")
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
    print("Successfully imported MoviePy components")
except Exception as e:
    print(f"Error importing MoviePy: {e}")
    traceback.print_exc()

# Create a simple colored frame for testing
def create_test_frame(width=1080, height=1920, color=(0, 0, 255)):
    """Create a simple colored frame for testing"""
    try:
        print(f"Creating test frame with dimensions {width}x{height}")
        # Create a solid color image
        img = Image.new('RGB', (width, height), color)
        
        # Add some text
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            # Try different fonts
            fonts_to_try = ["Arial", "DejaVuSans", "FreeSans"]
            font = None
            
            for font_name in fonts_to_try:
                try:
                    font = ImageFont.truetype(font_name, 60)
                    print(f"Using font: {font_name}")
                    break
                except:
                    pass
                    
            if font is None:
                font = ImageFont.load_default()
                print("Using default font")
                
            # Draw text
            draw.text((width//2, height//2), "Test Frame", fill=(255, 255, 255), font=font)
        except Exception as e:
            print(f"Error adding text to frame: {e}")
            
        return np.array(img)
    except Exception as e:
        print(f"Error creating test frame: {e}")
        traceback.print_exc()
        return None

# Create text overlay (simplified version of our main function)
def create_simple_text_overlay(text="Test Text", width=1080, height=1920):
    """Create a simple text overlay using PIL"""
    try:
        print(f"Creating text overlay with dimensions {width}x{height}")
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to use a basic font
        try:
            font = ImageFont.load_default()
            print("Using default font for text overlay")
        except:
            font = None
            print("Failed to load even default font")
        
        # Draw text in the center
        if font:
            text_width = len(text) * 30  # Rough estimate
            x = (width - text_width) // 2
            y = height // 2
            
            # Draw text with white color
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            print("Text drawn successfully")
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Create ImageClip from numpy array
        from moviepy.editor import ImageClip
        clip = ImageClip(img_array)
        
        # Set duration and position
        clip = clip.set_duration(3)
        clip = clip.set_fps(24)  # Set FPS explicitly
        
        print("Text overlay clip created successfully")
        return clip
    except Exception as e:
        print(f"Error creating simple text overlay: {e}")
        traceback.print_exc()
        return None

# Create a simple test video
def create_test_video(output_path="test_output.mp4", use_text=True):
    """Create a simple test video to check if video generation works"""
    try:
        print(f"Creating test video at {output_path}")
        
        # Create a solid color clip
        frame = create_test_frame()
        
        if frame is None:
            print("Failed to create test frame")
            return False
        
        # Create a clip from the frame
        from moviepy.editor import ImageClip
        base_clip = ImageClip(frame).set_duration(3)
        base_clip = base_clip.set_fps(24)  # Set FPS explicitly
        print(f"Created base clip with duration {base_clip.duration}s")
        
        final_clip = base_clip
        
        # Add text overlay if requested
        if use_text:
            try:
                text_clip = create_simple_text_overlay()
                
                if text_clip is not None:
                    # Create composite clip
                    final_clip = CompositeVideoClip([base_clip, text_clip])
                    print("Added text overlay to video")
                else:
                    print("Text overlay creation failed, continuing without text")
            except Exception as e:
                print(f"Error adding text overlay: {e}")
                traceback.print_exc()
        
        # Write the video file
        try:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            print(f"Writing video to {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec=None,
                fps=24,  # Set FPS explicitly
                verbose=False
            )
            
            if os.path.exists(output_path):
                print(f"Test video created successfully: {output_path}")
                return True
            else:
                print(f"Failed to create video file: {output_path}")
                return False
        except Exception as e:
            print(f"Error writing video file: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"Error in create_test_video: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n--- Testing Simple Video Generation ---")
    success = create_test_video("test_output_no_text.mp4", use_text=False)
    print(f"Simple video test {'passed' if success else 'failed'}")
    
    print("\n--- Testing Video with Text Overlay ---")
    success = create_test_video("test_output_with_text.mp4", use_text=True)
    print(f"Video with text overlay test {'passed' if success else 'failed'}") 