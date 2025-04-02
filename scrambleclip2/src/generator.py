import os, random
import warnings
import hashlib
import numpy as np
from collections import defaultdict
import traceback
import threading
import glob
import time
from datetime import datetime

# Try to import MoviePy components with better error handling
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, ImageClip, ColorClip
    # Import specific effects
    from moviepy.video.fx.loop import loop
    from moviepy.video.fx.fadein import fadein
    from moviepy.video.fx.fadeout import fadeout
    from moviepy.video.fx.colorx import colorx
    from moviepy.video.fx.mirror_x import mirror_x
    from moviepy.video.fx.mirror_y import mirror_y
    from moviepy.video.fx.time_symmetrize import time_symmetrize
    from moviepy.video.fx.invert_colors import invert_colors
    from moviepy.video.fx.blackwhite import blackwhite
    from moviepy.video.fx.crop import crop
    MOVIEPY_LOADED = True
except ImportError as e:
    print(f"Error importing MoviePy components: {e}")
    traceback.print_exc()
    MOVIEPY_LOADED = False

# Try to import internal modules with fallbacks
try:
    from .utils import get_video_files, get_random_clip, pad_clip_to_ratio, prepare_clip_for_concat
    UTILS_LOADED = True
except ImportError as e:
    print(f"Error importing utils module: {e}")
    traceback.print_exc()
    UTILS_LOADED = False
    
    # Simple fallback implementations
    def get_video_files(directory):
        return glob.glob(os.path.join(directory, "*.mp4"))
    
    def get_random_clip(*args, **kwargs):
        return None
    
    def pad_clip_to_ratio(clip, *args, **kwargs):
        return clip
    
    def prepare_clip_for_concat(clip, *args, **kwargs):
        return clip

try:
    from .video_analysis import VideoContentAnalyzer
    ANALYZER_LOADED = True
except ImportError as e:
    print(f"Error importing video_analysis module: {e}")
    traceback.print_exc()
    ANALYZER_LOADED = False
    
    # Simple fallback implementation
    class VideoContentAnalyzer:
        def __init__(self):
            pass
        
        def analyze_clip(self, *args, **kwargs):
            return {}

# Suppress MoviePy warnings that might confuse users
warnings.filterwarnings("ignore", category=UserWarning)

class VideoGenerator:
    def __init__(self, input_video_path):
        """
        Initialize the VideoGenerator with an input video path.
        
        Args:
            input_video_path (str): Path to the input video file
        """
        self.input_video_path = input_video_path
        self.video_analyzer = VideoContentAnalyzer()
        
    def generate_scrambled_videos(self, num_videos=5, segment_duration=0.5, output_dir="outputs", 
                                 additional_videos=None, audio_path=None, text_overlay=None, use_effects=True):
        """
        Generate multiple unique scrambled versions of the input video(s).
        
        Parameters:
            num_videos (int): Number of videos to generate
            segment_duration (float): Duration of each segment in seconds (Note: Overridden internally to ensure proper TikTok-style output)
            output_dir (str): Directory to save output videos
            additional_videos (list): List of additional video paths to use
            audio_path (str): Path to audio file to add to videos
            text_overlay (dict): Dictionary containing text overlay parameters:
                - text: The text to display
                - color: Text color in hex format
                - stroke_color: Stroke color in hex format
                - font_size: Size of the text
                - stroke_width: Width of the stroke
                - opacity: Text opacity (0-1)
            use_effects (bool): Whether to apply random visual effects to segments
        """
        try:
            # Check if MoviePy is loaded
            if not MOVIEPY_LOADED:
                print("MoviePy is not available. Cannot generate videos.")
                return []
            
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Combine input video paths
            video_paths = [self.input_video_path]
            if additional_videos:
                video_paths.extend(additional_videos)
                
            # Verify video paths
            valid_paths = []
            for path in video_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    valid_paths.append(path)
                else:
                    print(f"Warning: Video path does not exist: {path}")
            
            if not valid_paths:
                print("Error: No valid video paths found.")
                return []
                
            # Prepare text overlay
            text_params = {}
            if text_overlay:
                try:
                    # Handle various text overlay parameters with fallbacks
                    text_params = {
                        'text': text_overlay.get('text', 'ScrambleClip'),
                        'color': text_overlay.get('color', '#FFFFFF'),
                        'stroke_color': text_overlay.get('stroke_color', '#000000'),
                        'font_size': int(text_overlay.get('font_size', 60)),
                        'stroke_width': int(text_overlay.get('stroke_width', 2)),
                        'opacity': float(text_overlay.get('opacity', 1.0))
                    }
                except Exception as e:
                    print(f"Error preparing text overlay parameters: {e}")
                    traceback.print_exc()
                    text_params = {}
                    
            # Log key parameters for debugging
            print(f"Generating videos with parameters: num_videos={num_videos}")
            print(f"Using {len(valid_paths)} video paths, audio: {audio_path is not None}, text: {bool(text_params)}")
            print(f"Using AI effects: {use_effects}")
            print("Note: Using fixed segment durations of 3-4 seconds for optimal TikTok-style output")
            
            # Generate the videos with fixed segment durations for optimal output
            # These parameters create the proper 16-second TikTok-style scrambled videos
            return generate_batch(
                valid_paths,
                audio_files=[audio_path] if audio_path and os.path.exists(audio_path) else None,
                num_videos=num_videos,
                min_clips=4,  # Fewer clips with longer duration
                max_clips=6,  # Enough for ~16 second videos
                min_clip_duration=3.0,  # 3-4 second segments work better
                max_clip_duration=4.0,  # for TikTok-style videos
                target_duration=16.0,  # Target 16 second total duration
                output_dir=output_dir,
                use_effects=use_effects,
                use_text=bool(text_params),
                custom_text=text_params.get('text') if text_params else None,
                text_color=text_params.get('color', '#FFFFFF'),
                stroke_color=text_params.get('stroke_color', '#000000'),
                font_size=text_params.get('font_size', 60),
                stroke_width=text_params.get('stroke_width', 2),
                text_opacity=text_params.get('opacity', 1.0)
            )
        except Exception as e:
            print(f"Error in generate_scrambled_videos: {e}")
            traceback.print_exc()
            return []

# Create text overlay using PIL/Pillow instead of TextClip
def create_text_overlay(text, size, color='white', font_size=60, opacity=1.00, stroke_color='black', stroke_width=2):
    """
    Create a text overlay using PIL/Pillow instead of TextClip.
    
    Args:
        text (str): Text to display
        size (tuple or VideoClip): Size as (width, height) or a clip to match
        color (str): Text color
        font_size (int): Font size
        opacity (float): Text opacity (0-1)
        stroke_color (str): Color of text outline
        stroke_width (int): Width of text outline
        
    Returns:
        ImageClip: The text overlay or None if creation failed
    """
    try:
        # Get dimensions
        if isinstance(size, tuple):
            width, height = int(size[0]), int(size[1])
        else:
            width, height = int(size.w), int(size.h)
            
        # Create a simple colored background with text using PIL
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a transparent background
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Use default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text in center (approximate)
        text_width = len(text) * font_size * 0.5  # Rough estimate
        x = (width - text_width) / 2
        y = height / 2 - font_size
        
        # Draw the text
        if font:
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Convert PIL image to numpy array for ImageClip
        img_array = np.array(img)
        
        # Create ImageClip from numpy array
        from moviepy.editor import ImageClip
        clip = ImageClip(img_array)
        
        # Set duration and position
        clip = clip.set_duration(10)
        clip = clip.set_fps(24)  # Set FPS explicitly
        
        return clip
        
    except Exception as e:
        print(f"Error creating text overlay: {e}")
        traceback.print_exc()
        return None

# Modify the generate_batch function to include simpler handling
def generate_batch(input_videos, audio_files=None, num_videos=5, min_clips=4, max_clips=6, 
                   min_clip_duration=3.0, max_clip_duration=4.0, target_duration=16.0, output_dir="outputs", 
                   use_effects=False, use_text=False, custom_text=None, text_color='#FFFFFF',
                   stroke_color='#000000', font_size=60, stroke_width=2, text_opacity=1.00, 
                   progress_callback=None):
    """
    Generate a batch of videos by randomly selecting clips from input videos.
    
    Parameters:
        target_duration: Target duration for output videos (default 16 seconds)
    """
    if not MOVIEPY_LOADED:
        print("MoviePy is not available. Cannot generate videos.")
        return []
        
    if not input_videos:
        print("No input videos provided")
        return []
        
    output_paths = []
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try to load videos one by one with error handling
        input_clips = []
        for i, video_path in enumerate(input_videos):
            try:
                if not os.path.exists(video_path):
                    print(f"Video file does not exist: {video_path}")
                    continue
                    
                print(f"Loading video {i+1}/{len(input_videos)}: {video_path}")
                clip = VideoFileClip(video_path)
                input_clips.append(clip)
                
            except Exception as e:
                print(f"Error loading video {video_path}: {e}")
        
        if not input_clips:
            print("No valid input videos could be loaded")
            return []
        
        # Generate videos one by one
        for i in range(num_videos):
            try:
                output_path = os.path.join(output_dir, f"scrambled_{timestamp}_{i+1}.mp4")
                print(f"Generating scrambled video {i+1}/{num_videos} to {output_path}")
                
                # Calculate how many segments to ensure ~16 second video
                avg_segment_length = (min_clip_duration + max_clip_duration) / 2
                ideal_num_segments = round(target_duration / avg_segment_length)
                
                # Ensure we stay within min_clips and max_clips
                num_segments = max(min_clips, min(ideal_num_segments, max_clips))
                print(f"Creating video with {num_segments} segments to target {target_duration} seconds duration")
                
                # Generate list of random segments from input videos
                segments = []
                total_duration = 0  # Track accumulated duration
                
                for j in range(num_segments):
                    try:
                        # Progress reporting
                        if progress_callback:
                            progress_pct = 20 + int((j / num_segments) * 60)
                            progress_callback(progress_pct, f"Creating segment {j+1}/{num_segments}")
                        
                        # Choose a random source clip
                        source_idx = random.randint(0, len(input_clips) - 1)
                        source_clip = input_clips[source_idx]
                        
                        # Calculate ideal segment duration for remaining time
                        remaining_segments = num_segments - j
                        remaining_target_duration = target_duration - total_duration
                        
                        if remaining_segments > 0:
                            # Adjust segment duration to hit target total duration
                            ideal_segment_duration = remaining_target_duration / remaining_segments
                            # Keep within bounds
                            adjusted_min = max(min_clip_duration, min(ideal_segment_duration * 0.8, max_clip_duration))
                            adjusted_max = min(max_clip_duration, max(min_clip_duration, ideal_segment_duration * 1.2))
                        else:
                            # Default to standard range
                            adjusted_min = min_clip_duration
                            adjusted_max = max_clip_duration
                            
                        # Choose random segment duration within bounds
                        segment_duration = random.uniform(adjusted_min, adjusted_max)
                        
                        # Ensure we don't exceed the clip's duration
                        max_start_time = max(0, source_clip.duration - segment_duration)
                        if max_start_time <= 0:
                            # Skip clips that are too short
                            continue
                            
                        # Choose a random start time
                        start_time_val = random.uniform(0, max_start_time)
                        
                        # Extract segment
                        segment = source_clip.subclip(start_time_val, start_time_val + segment_duration)
                        
                        # Set FPS directly (simpler approach)
                        segment.fps = 24
                        
                        # Apply random effects if enabled (reduce probability)
                        if use_effects and random.random() < 0.2:  # 20% chance of effect
                            try:
                                # Simple color adjustment
                                color_factor = random.uniform(0.85, 1.15)  # Slight adjustment
                                segment = colorx(segment, color_factor)
                            except Exception as e:
                                print(f"Effect application failed: {e}")
                        
                        # Ensure consistent dimensions - always convert to 9:16 ratio
                        try:
                            # Use fixed 9:16 dimensions for TikTok-style videos
                            target_width = 1080
                            target_height = 1920
                            
                            # Calculate current aspect ratio
                            current_ratio = segment.h / segment.w
                            target_ratio = target_height / target_width  # 16:9 vertical (1.78)
                            
                            print(f"Resizing segment from {segment.w}x{segment.h} to 9:16 ratio")
                            
                            if abs(current_ratio - target_ratio) < 0.1:
                                # Already close to target ratio, just resize
                                segment = segment.resize(width=target_width, height=target_height)
                            elif current_ratio < target_ratio:
                                # Too wide for target ratio - resize by height then crop width
                                resized = segment.resize(height=target_height)
                                # Calculate center crop
                                excess_width = resized.w - target_width
                                if excess_width > 0:
                                    segment = crop(resized, 
                                                  x1=excess_width//2, 
                                                  y1=0, 
                                                  x2=resized.w - excess_width//2, 
                                                  y2=target_height)
                                else:
                                    segment = resized.resize(width=target_width, height=target_height)
                            else:
                                # Too tall for target ratio - resize by width then crop height
                                resized = segment.resize(width=target_width)
                                # Calculate center crop
                                excess_height = resized.h - target_height
                                if excess_height > 0:
                                    segment = crop(resized, 
                                                  x1=0, 
                                                  y1=excess_height//2, 
                                                  x2=target_width, 
                                                  y2=resized.h - excess_height//2)
                                else:
                                    segment = resized.resize(width=target_width, height=target_height)
                            
                            # Final check to ensure exact dimensions
                            if segment.w != target_width or segment.h != target_height:
                                segment = segment.resize(width=target_width, height=target_height)
                                
                            print(f"Resized segment to {segment.w}x{segment.h}")
                        except Exception as e:
                            print(f"Resize operation failed: {e}")
                            # Try direct resize as fallback
                            try:
                                segment = segment.resize(width=1080, height=1920)
                            except:
                                print("Fallback resize also failed")
                        
                        segments.append(segment)
                        total_duration += segment.duration
                        print(f"Added segment {j+1}: {segment.duration:.1f}s, total so far: {total_duration:.1f}s")
                        
                    except Exception as e:
                        print(f"Error creating segment {j+1}: {e}")
                
                if not segments:
                    print("Failed to create any valid segments")
                    continue
                
                if len(segments) < 2:
                    print("Not enough segments to create a proper video")
                    continue
                
                print(f"Created {len(segments)} segments with total duration: {total_duration:.1f}s")
                    
                # Create the final composite video
                try:
                    print(f"Concatenating {len(segments)} segments")
                    final_clip = concatenate_videoclips(segments, method="compose")
                    
                    # Set FPS directly (simpler approach)
                    final_clip.fps = 24
                    
                    print(f"Final clip duration: {final_clip.duration:.1f}s")
                    
                    # Ensure final clip is exactly 9:16 ratio
                    if final_clip.w != 1080 or final_clip.h != 1920:
                        try:
                            print(f"Final clip dimensions need adjustment: {final_clip.w}x{final_clip.h}")
                            
                            # Fixed dimensions for 9:16 vertical format
                            target_width = 1080
                            target_height = 1920
                            
                            # Calculate current aspect ratio
                            current_ratio = final_clip.h / final_clip.w
                            target_ratio = target_height / target_width  # 16:9 vertical
                            
                            if abs(current_ratio - target_ratio) < 0.1:
                                # Already close to target ratio, just resize
                                final_clip = final_clip.resize(width=target_width, height=target_height)
                            elif current_ratio < target_ratio:
                                # Too wide for target ratio - resize by height then crop width
                                resized = final_clip.resize(height=target_height)
                                # Calculate center crop
                                excess_width = resized.w - target_width
                                if excess_width > 0:
                                    final_clip = crop(resized, 
                                                     x1=excess_width//2, 
                                                     y1=0, 
                                                     x2=resized.w - excess_width//2, 
                                                     y2=target_height)
                                else:
                                    final_clip = resized.resize(width=target_width, height=target_height)
                            else:
                                # Too tall for target ratio - resize by width then crop height
                                resized = final_clip.resize(width=target_width)
                                # Calculate center crop
                                excess_height = resized.h - target_height
                                if excess_height > 0:
                                    final_clip = crop(resized, 
                                                     x1=0, 
                                                     y1=excess_height//2, 
                                                     x2=target_width, 
                                                     y2=resized.h - excess_height//2)
                                else:
                                    final_clip = resized.resize(width=target_width, height=target_height)
                            
                            # Final verification
                            if final_clip.w != target_width or final_clip.h != target_height:
                                final_clip = final_clip.resize(width=target_width, height=target_height)
                                
                            print(f"Final clip resized to 9:16 ratio: {final_clip.w}x{final_clip.h}")
                        except Exception as e:
                            print(f"Error resizing final clip: {e}")
                            # Try direct resize as absolute fallback
                            try:
                                final_clip = final_clip.resize(width=1080, height=1920)
                                print("Used fallback direct resize")
                            except:
                                print("All resize attempts failed")
                    
                    # Load audio if provided
                    audio_clip = None
                    if audio_files and len(audio_files) > 0 and audio_files[0]:
                        try:
                            audio_path = audio_files[0]
                            print(f"Loading audio: {audio_path}")
                            if os.path.exists(audio_path):
                                audio_clip = AudioFileClip(audio_path)
                                
                                # Trim audio to match video length
                                if audio_clip.duration > final_clip.duration:
                                    audio_clip = audio_clip.subclip(0, final_clip.duration)
                                else:
                                    # Loop audio to match video duration
                                    repeat_count = int(final_clip.duration / audio_clip.duration) + 1
                                    audio_clip = audio_clip.loop(n=repeat_count)
                                    audio_clip = audio_clip.subclip(0, final_clip.duration)
                                
                                # Set audio to the final clip
                                final_clip = final_clip.set_audio(audio_clip)
                            else:
                                print(f"Audio file does not exist: {audio_path}")
                        except Exception as e:
                            print(f"Error applying audio: {e}")
                    
                    # Create text overlay if requested - simple approach
                    if use_text and custom_text:
                        try:
                            print(f"Creating text overlay for video {i+1}")
                            
                            # Only attempt text overlay if we're not using it already
                            if not hasattr(final_clip, 'text_overlay_applied'):
                                # Simple text overlay creation
                                text_overlay = create_text_overlay(
                                    custom_text,
                                    size=(final_clip.w, final_clip.h),
                                    font_size=font_size
                                )
                                
                                if text_overlay is not None:
                                    # Make sure text overlay has same duration as video
                                    text_overlay = text_overlay.set_duration(final_clip.duration)
                                    
                                    # Create composite clip
                                    try:
                                        composite = CompositeVideoClip([final_clip, text_overlay])
                                        composite.fps = 24  # Set FPS directly
                                        
                                        # Mark as having text overlay
                                        composite.text_overlay_applied = True
                                        
                                        # Replace final clip
                                        final_clip = composite
                                        print("Successfully added text overlay to video")
                                    except Exception as e:
                                        print(f"Error compositing text with video: {e}")
                                else:
                                    print("Text overlay creation failed, continuing without text")
                        except Exception as e:
                            print(f"Error in text overlay process: {e}")
                            # Continue without text if there's an error
                    
                    # Write the final video
                    try:
                        print(f"Writing video to {output_path}")
                        
                        final_clip.write_videofile(
                            output_path,
                            codec='libx264',
                            audio_codec='aac' if audio_clip else None,
                            fps=24,  # Set FPS explicitly
                            temp_audiofile=os.path.join(output_dir, f"temp_audio_{i}.m4a"),
                            remove_temp=True,
                            verbose=False,
                            logger=None
                        )
                        
                        # Verify output file
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            print(f"Successfully generated video: {output_path}")
                            output_paths.append(output_path)
                        else:
                            print(f"Failed to generate video or output file is empty: {output_path}")
                            
                    except Exception as e:
                        print(f"Error writing video: {e}")
                        
                    # Clean up final clip and segments
                    try:
                        final_clip.close()
                        for segment in segments:
                            segment.close()
                        if audio_clip:
                            audio_clip.close()
                    except Exception as e:
                        print(f"Error during cleanup: {e}")
                        
                except Exception as e:
                    print(f"Error concatenating segments: {e}")
                    # Clean up segments
                    for segment in segments:
                        try:
                            segment.close()
                        except:
                            pass
                
            except Exception as e:
                print(f"Error generating video {i+1}: {e}")
                
        # Clean up input clips
        for clip in input_clips:
            try:
                clip.close()
            except:
                pass
                
        return output_paths
        
    except Exception as e:
        print(f"Error in generate_batch: {e}")
        return output_paths
