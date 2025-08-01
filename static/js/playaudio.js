let playing = false;
let audioDuration = 0;
let durationString = "00:00";
const socket = io();

document.addEventListener("DOMContentLoaded", () => {
    const audioFileName = sessionStorage.getItem('audioFile');
    const lightshowFileName = sessionStorage.getItem('lightshowFile');
    if (audioFileName) {
        const effectContainer = document.getElementById('effect_module_container');
        effectContainer.style.display = 'none';
        socket.emit('audio_client_connected', { audio_file: audioFileName });
    }
    else if (lightshowFileName) {
        const effectContainer = document.getElementById('effect_module_container');
        effectContainer.style.display = 'none';
        socket.emit('lightshow_client_connected', { lightshow_file: lightshowFileName });
    }
});

// audio player is shared for both audio and lightshow
socket.on('audio_ready', () => {
    console.log('🔥 audio_ready received');
    fetch(`/audio/${sessionStorage.getItem('audioFile')}`)
        .then(response => response.blob())
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            const audioElement = document.getElementById('audio_player');
            const audioContainer = document.getElementById('audio_modules_container');
            audioElement.src = audioUrl;
            audioContainer.style.display = 'block';

            audioElement.onplay = () => {
                socket.emit('audio_play');
            };

            audioElement.onpause = () => {
                socket.emit('audio_pause');
                console.log("Audio paused");
            };

            audioElement.onseeked = () => {
                socket.emit('audio_seek', { time: audioElement.currentTime });
            };
        })
        .catch(error => console.error('Error fetching audio:', error));
});