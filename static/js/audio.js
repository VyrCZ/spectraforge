function selectAudio(audioFile) {
    clearSelection();
    sessionStorage.setItem('audioFile', audioFile);
    document.location.href = '/';
}

function selectLightshow(lightshowFile) {
    clearSelection();
    sessionStorage.setItem('lightshowFile', lightshowFile);
    document.location.href = '/';
}

function selectVideo(videoFile) {
    clearSelection();
    sessionStorage.setItem('videoFile', videoFile);
    document.location.href = '/';
}

function clearSelection() {
    sessionStorage.removeItem('audioFile');
    sessionStorage.removeItem('lightshowFile');
    sessionStorage.removeItem('videoFile');
}

function isAudioEngineSelected() {
    return (
        sessionStorage.getItem('audioFile') !== null ||
        sessionStorage.getItem('lightshowFile') !== null ||
        sessionStorage.getItem('videoFile') !== null
    )
}