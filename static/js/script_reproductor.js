document.addEventListener('DOMContentLoaded', function() {
    // Elementos del reproductor
    const audioElement = document.getElementById('audio-element');
    const playPauseButton = document.getElementById('play-pause-button');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeElement = document.getElementById('current-time');
    const durationElement = document.getElementById('duration');
    const songTitleElement = document.getElementById('player-song-title');
    const songArtistElement = document.getElementById('player-song-artist');
    const albumCoverElement = document.getElementById('player-album-cover');
    
    // Estado del reproductor
    let isPlaying = false;
    let currentTrackIndex = 0;
    let tracks = [];
    
    // Obtener todas las canciones de la lista
    function loadTracks() {
        const trackElements = document.querySelectorAll('.track');
        tracks = Array.from(trackElements).map(track => ({
            file: track.dataset.file,
            title: track.dataset.title,
            artist: track.dataset.artist,
            element: track
        }));
        
        // Si hay canciones, cargar la primera
        if (tracks.length > 0) {
            loadTrack(currentTrackIndex);
        }
    }
    
    // Cargar una canción específica
    function loadTrack(index) {
        const track = tracks[index];
        audioElement.src = track.file;
        songTitleElement.textContent = track.title;
        songArtistElement.textContent = track.artist;
        
        // Resaltar la canción que se está reproduciendo
        tracks.forEach(t => t.element.classList.remove('active'));
        track.element.classList.add('active');
        
        // Cuando los metadatos estén cargados
        audioElement.addEventListener('loadedmetadata', function() {
            durationElement.textContent = formatTime(audioElement.duration);
        }, { once: true });
    }
    
    // Formatear tiempo (mm:ss)
    function formatTime(seconds) {
        if (isNaN(seconds)) return "0:00";
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }
    
    // Actualizar barra de progreso
    function updateProgress() {
        const currentTime = audioElement.currentTime;
        const duration = audioElement.duration || 1; // Evitar división por cero
        
        progressBar.value = (currentTime / duration) * 100;
        currentTimeElement.textContent = formatTime(currentTime);
    }
    
    // Controlar la reproducción
    function togglePlay() {
        if (isPlaying) {
            audioElement.pause();
            playPauseButton.innerHTML = '<i class="fas fa-play"></i>';
        } else {
            audioElement.play()
                .then(() => {
                    playPauseButton.innerHTML = '<i class="fas fa-pause"></i>';
                })
                .catch(error => {
                    console.error("Error al reproducir:", error);
                });
        }
        isPlaying = !isPlaying;
    }
    
    // Cambiar a la siguiente canción
    function nextTrack() {
        currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) {
            audioElement.play();
        }
    }
    
    // Cambiar a la canción anterior
    function prevTrack() {
        // Si la canción lleva más de 3 segundos, reiniciarla
        if (audioElement.currentTime > 3) {
            audioElement.currentTime = 0;
        } else {
            currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
            loadTrack(currentTrackIndex);
            if (isPlaying) {
                audioElement.play();
            }
        }
    }
    
    // Event listeners
    playPauseButton.addEventListener('click', togglePlay);
    nextButton.addEventListener('click', nextTrack);
    prevButton.addEventListener('click', prevTrack);
    
    // Barra de progreso
    progressBar.addEventListener('input', function() {
        const seekTime = (progressBar.value / 100) * audioElement.duration;
        audioElement.currentTime = seekTime;
    });
    
    // Actualizar progreso mientras se reproduce
    audioElement.addEventListener('timeupdate', updateProgress);
    
    // Cuando termina una canción
    audioElement.addEventListener('ended', nextTrack);
    
    // Reproducir canción al hacer clic en ella
    document.querySelectorAll('.track').forEach((track, index) => {
        track.addEventListener('click', function() {
            currentTrackIndex = index;
            loadTrack(currentTrackIndex);
            if (!isPlaying) {
                togglePlay();
            } else {
                audioElement.play();
            }
        });
    });
    
    // Reproducir canción al hacer clic en el botón "Reproducir"
    document.querySelectorAll('.play-button').forEach((button, index) => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Evitar que se active el evento del track
            currentTrackIndex = index;
            loadTrack(currentTrackIndex);
            if (!isPlaying) {
                togglePlay();
            } else {
                audioElement.play();
            }
        });
    });
    
    // Cargar las canciones al iniciar
    loadTracks();
});