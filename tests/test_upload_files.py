import io
import subprocess

from werkzeug.datastructures import FileStorage

from modules import upload_files


def make_upload(filename, content):
    return FileStorage(stream=io.BytesIO(content), filename=filename)


def test_recognize_script_type_variants():
    effect_stream = io.BytesIO(b"class Demo(LightEffect):\n    pass\n")
    lightshow_stream = io.BytesIO(b"class Demo(LightshowEffects):\n    pass\n")
    bad_stream = io.BytesIO(b"\xff\xfe")
    assert upload_files.recognize_script_type(effect_stream) == upload_files.FileType.EFFECT
    assert upload_files.recognize_script_type(lightshow_stream) == upload_files.FileType.LIGHTSHOW_EFFECTS
    assert upload_files.recognize_script_type(bad_stream) is None


def test_recognize_file_type_variants():
    assert upload_files.recognize_file_type(make_upload("song.mp3", b"a")) == upload_files.FileType.AUDIO
    assert upload_files.recognize_file_type(make_upload("show.json", b"{}")) == upload_files.FileType.LIGHTSHOW
    assert upload_files.recognize_file_type(make_upload("image.png", b"a")) == upload_files.FileType.IMAGE
    assert upload_files.recognize_file_type(make_upload("video.mp4", b"a")) == upload_files.FileType.VIDEO
    assert upload_files.recognize_file_type(make_upload("unknown.bin", b"a")) is None


def test_extract_audio_from_video_success_failure_and_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_files.Log, "warning", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(upload_files.subprocess, "run", lambda *args, **kwargs: object())
    assert upload_files.extract_audio_from_video("input.mp4", str(tmp_path / "audio" / "out.mp3")) is True

    def raise_called_process_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "ffmpeg", stderr=b"fail")

    monkeypatch.setattr(upload_files.subprocess, "run", raise_called_process_error)
    assert upload_files.extract_audio_from_video("input.mp4", str(tmp_path / "audio" / "out.mp3")) is False

    monkeypatch.setattr(upload_files.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    assert upload_files.extract_audio_from_video("input.mp4", str(tmp_path / "audio" / "out.mp3")) is False


def test_handle_file_upload_saves_files_and_marks_unknown(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_files.Log, "warning", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(upload_files, "DESTINATION_DIR", {
        upload_files.FileType.AUDIO: str(tmp_path / "audio"),
        upload_files.FileType.VIDEO: str(tmp_path / "videos"),
    })
    monkeypatch.setattr(upload_files, "extract_audio_from_video", lambda video_path, output_path: True)

    audio = make_upload("song.mp3", b"sound")
    video = make_upload("clip.mp4", b"video")
    unknown = make_upload("note.txt", b"text")

    result = upload_files.handle_file_upload([audio, video, unknown])
    assert result is False
    assert (tmp_path / "audio" / "song.mp3").exists()
    assert (tmp_path / "videos" / "clip.mp4").exists()


def test_handle_file_upload_marks_video_extract_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_files.Log, "warning", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(upload_files, "DESTINATION_DIR", {upload_files.FileType.VIDEO: str(tmp_path / "videos")})
    monkeypatch.setattr(upload_files, "extract_audio_from_video", lambda video_path, output_path: False)
    video = make_upload("clip.mp4", b"video")
    assert upload_files.handle_file_upload([video]) is False