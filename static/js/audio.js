function selectAudio(audioFile) {
    sessionStorage.setItem('audioFile', audioFile);
    sessionStorage.removeItem('lightshowFile');
    sessionStorage.removeItem('videoFile');
    document.location.href = '/';
}

function selectLightshow(lightshowFile) {
    sessionStorage.setItem('lightshowFile', lightshowFile);
    sessionStorage.removeItem('audioFile');
    sessionStorage.removeItem('videoFile');
    document.location.href = '/';
}

function selectVideo(videoFile) {
    sessionStorage.setItem('videoFile', videoFile);
    sessionStorage.removeItem('audioFile');
    sessionStorage.removeItem('lightshowFile');
    document.location.href = '/';
}