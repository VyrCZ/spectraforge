import os
import ast
from werkzeug.utils import secure_filename
from modules.log_manager import Log

# This is a placeholder, adjust the path to your actual upload folder
UPLOAD_FOLDER = ".temp/uploads"

class FileType:
    EFFECT = "effect"
    AUDIO = "audio"
    LIGHTSHOW = "lightshow"
    LIGHTSHOW_EFFECTS = "lightshow_effects"

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
    filename = secure_filename(file.filename)
    if filename.endswith((".wav", ".ogg", ".mp3")):
        return FileType.AUDIO
    elif filename.endswith(".json"):
        return FileType.LIGHTSHOW
    elif filename.endswith(".py"):
        return recognize_script_type(file.stream)
    return None


# It's the same values as in the FileType class, but I want to keep the directories separate if it ever changes
DESTINATION_DIR = {
    FileType.EFFECT: "effects",
    FileType.AUDIO: "audio",
    FileType.LIGHTSHOW: "lightshows",
    FileType.LIGHTSHOW_EFFECTS: "lightshow_effects"
}


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
            file.save(os.path.join(dest_dir, filename))
        else:
            Log.warning("FileUpload", f"Could not determine file type for {filename}. Skipping.")
            all_successful = False
    return all_successful