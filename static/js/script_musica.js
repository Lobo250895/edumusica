document.addEventListener('DOMContentLoaded', function () {
   
    const selectedSongTitle = document.createElement('h4');
    selectedSongTitle.style.color = 'blue'; 
    selectedSongTitle.style.textAlign = 'center'; 
    selectedSongTitle.id = 'selected-song-title'; 
    document.querySelector('.audio-container').prepend(selectedSongTitle); 

    document.querySelectorAll('.square-button').forEach(button => {
        button.addEventListener('click', function () {
            const categoria = this.getAttribute('data-categoria');

            fetch(`/obtener_canciones?categoria=${categoria}`)
                .then(response => response.json())
                .then(data => {
                    const songList = document.getElementById('song-list');
                    songList.innerHTML = '';

                    data.canciones.forEach(cancion => {
                        const li = document.createElement('li');
                        li.className = 'song-item'; 
                        li.innerHTML = `
                            <strong>${cancion.titulo}</strong> - ${cancion.artista} <br>
                            <button class="play-button" data-src="${cancion.ruta_archivo}">${cancion.titulo}</button>
                        `;
                        songList.appendChild(li);
                    });

                    
                    document.querySelectorAll('.play-button').forEach(playButton => {
                        playButton.addEventListener('click', function () {
                            const audioPlayer = document.getElementById('audio-player');
                            const audioSource = document.getElementById('audio-source');

                            
                            audioPlayer.pause();
                            audioPlayer.currentTime = 0;

                            
                            audioSource.src = this.getAttribute('data-src');
                            audioPlayer.load();
                            audioPlayer.play();

                            
                            const songTitle = this.getAttribute('data-src').split('/').pop().split('.')[0]; 
                            selectedSongTitle.textContent = songTitle; 
                        });
                    });
                })
                .catch(error => console.error('Error al cargar las canciones:', error));
        });
    });
});


const cards = document.querySelectorAll('.card_play');

cards.forEach(card => {
  card.addEventListener('mouseover', () => {
    card.style.animation = "bounce 0.5s ease-out";
  });

  card.addEventListener('animationend', () => {
    card.style.animation = "";
  });
});


document.head.insertAdjacentHTML("beforeend", `
<style>
  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }
</style>
`);
