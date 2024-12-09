#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pythonjsonlogger import jsonlogger

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Setup logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


class TranscodeHistory:
    def __init__(self, history_file):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def is_transcoded(self, file_path):
        return str(file_path) in self.history

    def add_transcoded_file(self, file_path, output_path):
        self.history[str(file_path)] = {
            "output_path": str(output_path),
            "timestamp": time.time(),
        }
        self.save_history()


class VideoHandler(FileSystemEventHandler):
    def __init__(self, input_folder, output_folder, history):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.history = history

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if not any(
            file_path.name.lower().endswith(ext) for ext in config.VIDEO_EXTENSIONS
        ):
            return

        if self.history.is_transcoded(file_path):
            logger.info(f"File {file_path} already transcoded, skipping")
            return

        self._process_video(file_path)

    def _process_video(self, file_path):
        try:
            # Create relative output path
            rel_path = file_path.relative_to(self.input_folder)
            output_path = (
                self.output_folder
                / rel_path.parent
                / f"{rel_path.stem}{config.SUFFIX}{rel_path.suffix}"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Starting transcoding of {file_path}")

            # Prepare av1an command
            cmd = [
                "av1an",
                "-i",
                str(file_path),
                "-o",
                str(output_path),
                "--encoder",
                config.ENCODER,
                "--workers",
                str(config.WORKERS),
                "--target-quality",
                str(config.TARGET_QUALITY),
            ]

            # Run transcoding
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                logger.info(f"Successfully transcoded {file_path} to {output_path}")
                self.history.add_transcoded_file(file_path, output_path)

                if config.DELETE_ORIGINAL:
                    os.remove(file_path)
                    logger.info(f"Deleted original file {file_path}")
            else:
                logger.error(f"Failed to transcode {file_path}: {process.stderr}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")


def main():
    # Ensure input and output folders exist
    input_folder = Path(config.INPUT_FOLDER).absolute()
    output_folder = Path(config.OUTPUT_FOLDER).absolute()
    input_folder.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Initialize history
    history = TranscodeHistory(config.TRANSCODE_HISTORY)

    # Setup watchdog
    event_handler = VideoHandler(input_folder, output_folder, history)
    observer = Observer()
    observer.schedule(event_handler, str(input_folder), recursive=True)
    observer.start()

    logger.info(f"Started watching {input_folder} for new videos")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping video transcoder")

    observer.join()


if __name__ == "__main__":
    main()
