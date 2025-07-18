document.addEventListener('DOMContentLoaded', function() {
       const keys = document.querySelectorAll('.key_juego');
    const startBtn = document.getElementById('startBtn');
    const scoreSpan = document.getElementById('score');
    const levelSpan = document.getElementById('level');

    let sequence = [];
    let playerIndex = 0;
    let level = 1;
    let score = 0;
    let playing = false;

    const playNote = note => {
        const key = document.querySelector(`.key_juego[data-note="${note}"]`);
        const audio = document.getElementById(`audio-${note}`);
        if (key && audio) {
            key.classList.add('active');
            audio.currentTime = 0;
            audio.play();
            setTimeout(() => key.classList.remove('active'), 500);
        }
    };

    const playSequence = async () => {
        playing = true;
        startBtn.disabled = true;
        
        // Mostrar mensaje de nivel
        const nivelMsg = document.createElement('div');
        nivelMsg.className = 'nivel-msg';
        nivelMsg.textContent = `Nivel ${level}`;
        document.querySelector('.juego-container').appendChild(nivelMsg);
        
        setTimeout(() => {
          nivelMsg.classList.add('show');
        }, 10);
        
        setTimeout(() => {
          nivelMsg.classList.remove('show');
          setTimeout(() => {
            document.querySelector('.juego-container').removeChild(nivelMsg);
          }, 300);
        }, 1500);
        
        // Esperar antes de reproducir la secuencia
        await new Promise(res => setTimeout(res, 2000));
        
        for (let note of sequence) {
            await new Promise(res => setTimeout(res, 800));
            playNote(note);
        }
        playing = false;
        startBtn.disabled = false;
    };

    const nextLevel = () => {
        level++;
        levelSpan.textContent = level;
        sequence.push(randomNote());
        playerIndex = 0;
        playSequence();
    };

    const randomNote = () => {
        const notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
        return notes[Math.floor(Math.random() * notes.length)];
    };

    const startGame = () => {
        sequence = [randomNote()];
        playerIndex = 0;
        level = 1;
        score = 0;
        scoreSpan.textContent = score;
        levelSpan.textContent = level;
        playSequence();
    };

    keys.forEach(key => {
        key.addEventListener('click', () => {
            if (playing) return;

            const note = key.dataset.note;
            playNote(note);

            if (note === sequence[playerIndex]) {
                playerIndex++;
                if (playerIndex === sequence.length) {
                    score += 10 * level;
                    scoreSpan.textContent = score;
                    setTimeout(nextLevel, 1000);
                }
            } else {
                const msg = document.createElement('div');
                msg.className = 'game-over-msg';
                msg.innerHTML = `
                  <h4>¡Juego terminado!</h4>
                  <p>Puntaje final: ${score}</p>
                  <p>Nivel alcanzado: ${level}</p>
                  <button class="btn btn-primary btn-sm mt-2" onclick="this.parentElement.remove()">OK</button>
                `;
                document.querySelector('.juego-container').appendChild(msg);
                
                fetch('/guardar_puntaje', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ puntaje: score, nivel: level })
                });
            }
        });
    });
    
    startBtn.addEventListener('click', startGame);


});