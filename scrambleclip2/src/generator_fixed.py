import os, random
import warnings
import hashlib
import numpy as np
from collections import defaultdict
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, ColorClip
# Import specific effects
from moviepy.video.fx.loop import loop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
