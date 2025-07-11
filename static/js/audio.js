function selectAudio(audioFile) {
    sessionStorage.setItem('audioFile', audioFile);
    document.location.href = '/';
}