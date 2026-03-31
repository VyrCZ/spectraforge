let playing = false;
let audioDuration = 0;
const socket = io();

function hideEffectContainers() {
    document.getElementById('effect_module_container').style.display = 'none';
    const currentEffectContainer = document.getElementById('current_effect_container');
    if (currentEffectContainer) currentEffectContainer.style.display = 'none';
}

document.addEventListener("DOMContentLoaded", () => {
    const audioFileName = sessionStorage.getItem('audioFile');
    const lightshowFileName = sessionStorage.getItem('lightshowFile');
    if (audioFileName) {
        hideEffectContainers();
        socket.emit('audio_client_connected', { audio_file: audioFileName });
    }
    else if (lightshowFileName) {
        hideEffectContainers();
        socket.emit('lightshow_client_connected', { lightshow_file: lightshowFileName });
    }
    else if(sessionStorage.getItem('videoFile')) {
        hideEffectContainers();
        socket.emit('video_client_connected', { video_file: sessionStorage.getItem('videoFile') });
    }
});

// audio player is shared for both audio and lightshow
socket.on('audio_ready', (data) => {
    console.log('🔥 audio_ready received');
    let storedAudioFile = sessionStorage.getItem('audioFile')
    if (!storedAudioFile) {
        storedAudioFile = data.audio_file;
    }
    let audioPath = `/audio/${storedAudioFile}`;
    if(sessionStorage.getItem('videoFile')) {
        audioPath = "/video_audio/" + sessionStorage.getItem('videoFile') + ".mp3";
    }
    fetch(audioPath)
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