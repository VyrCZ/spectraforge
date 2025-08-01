function selectAudio(audioFile) {
    sessionStorage.setItem('audioFile', audioFile);
    sessionStorage.removeItem('lightshowFile');
    document.location.href = '/';
}

function selectLightshow(lightshowFile) {
    sessionStorage.setItem('lightshowFile', lightshowFile);
    sessionStorage.removeItem('audioFile');
    document.location.href = '/';
}