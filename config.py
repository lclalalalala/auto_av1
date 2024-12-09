import os

# Folder settings
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
TRANSCODE_HISTORY = "transcode_history.json"

# Transcode settings
DELETE_ORIGINAL = False  # Whether to delete original file after successful transcode
SUFFIX = "_transcoded"  # Suffix to add to transcoded files

# AV1AN settings
WORKERS = os.cpu_count()  # Number of workers for av1an
TARGET_QUALITY = 30  # Target quality for AV1 encoding (lower is better)
ENCODER = "aom"  # AV1 encoder to use (aom, rav1e, svt-av1)

# File patterns to watch
VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]

# Advanced settings
CHECK_INTERVAL = 60  # How often to check for new files (in seconds)
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed transcodes
RETRY_DELAY = 300  # Delay between retry attempts (in seconds)
