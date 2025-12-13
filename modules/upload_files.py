import os
import ast
import subprocess
from werkzeug.utils import secure_filename
from modules.log_manager import Log

# This is a placeholder, adjust the path to your actual upload folder
UPLOAD_FOLDER = ".temp/uploads"

class FileType:
    EFFECT = "effect"
    AUDIO = "audio"
    LIGHTSHOW = "lightshow"
    LIGHTSHOW_EFFECTS = "lightshow_effects"
    IMAGE = "image"
    VIDEO = "video"

def recognize_script_type(file_stream) -> FileType | None:
    """Recognizes script type from a file stream."""
    try:
        # Read content from the stream and decode it
        source = file_stream.read().decode("utf-8")
        # Reset stream position to the beginning for later use (e.g., saving)
        file_stream.seek(0)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "LightEffect":
                        return FileType.EFFECT
                    elif isinstance(base, ast.Name) and base.id == "LightshowEffects":
                        return FileType.LIGHTSHOW_EFFECTS
    except (SyntaxError, UnicodeDecodeError):
        # Not a valid python file or cannot be decoded
        return None
    return None

def recognize_file_type(file) -> FileType | None:
    """Recognizes file type based on filename and content."""
    filename = secure_filename(file.filename).lower()
    if filename.endswith((".wav", ".ogg", ".mp3")):
        return FileType.AUDIO
    elif filename.endswith(".json"):
        return FileType.LIGHTSHOW
    elif filename.endswith(".py"):
        return recognize_script_type(file.stream)
    elif filename.endswith((".mp4", ".mkv", ".mov", ".webm", ".avi", ".flv")):
        return FileType.VIDEO
    return None


# It's the same values as in the FileType class, but I want to keep the directories separate if it ever changes
DESTINATION_DIR = {
    FileType.EFFECT: "effects",
    FileType.AUDIO: "audio",
    FileType.LIGHTSHOW: "lightshows",
    FileType.LIGHTSHOW_EFFECTS: "lightshow_effects",
    FileType.IMAGE: "media/images",
    FileType.VIDEO: "media/videos"
}

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extracts audio from a video file using ffmpeg and writes it to output_audio_path.
    The output filename will be whatever you pass (we'll create directories as needed).
    Returns True on success, False otherwise.
    """
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-b:a",
        "192k",
        output_audio_path,
    ]
    try:
        completed = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Log.info("FileUpload", f"Extracted audio to {output_audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        # ffmpeg returned a non-zero exit status
        stderr = e.stderr.decode("utf-8", errors="ignore") if e.stderr else ""
        Log.warning("FileUpload", f"ffmpeg failed extracting audio from {video_path}: {stderr}")
        return False
    except FileNotFoundError:
        # ffmpeg is not installed / not on PATH
        Log.warning("FileUpload", "ffmpeg not found on PATH — cannot extract audio. Install ffmpeg.")
        return False

def handle_file_upload(files) -> bool:
    """Handles file uploads, recognizes their types, and saves them."""
    Log.info("FileUpload", "Handling uploaded files")
    all_successful = True
    for file in files:
        filename = secure_filename(file.filename)
        file_type = recognize_file_type(file)
        Log.info("FileUpload", f"Recognized file type for {filename}: {file_type}")

        dest_dir = DESTINATION_DIR.get(file_type, None)

        if dest_dir:
            # Ensure the destination directory exists
            os.makedirs(dest_dir, exist_ok=True)
            saved_path = os.path.join(dest_dir, filename)
            file.save(saved_path)
            Log.info("FileUpload", f"Saved uploaded file to {saved_path}")

            # If it's a video, attempt to extract audio into media/videos/audio/<filename>.mp4.mp3
            if file_type == FileType.VIDEO:
                audio_dir = os.path.join(dest_dir, "audio")
                os.makedirs(audio_dir, exist_ok=True)
                # Create the requested filename with the original full name plus .mp3 appended
                audio_filename = filename + ".mp3"
                audio_path = os.path.join(audio_dir, audio_filename)
                if not extract_audio_from_video(saved_path, audio_path):
                    Log.warning("FileUpload", f"Failed to extract audio for {filename}")
                    all_successful = False
        else:
            Log.warning("FileUpload", f"Could not determine file type for {filename}. Skipping.")
            all_successful = False
    return all_successful