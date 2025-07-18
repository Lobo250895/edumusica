function showTab(index) {
    document.querySelectorAll(".content").forEach((tab, i) => {
        tab.classList.toggle("active", i === index);
    });
    document.querySelectorAll(".tab-button").forEach((btn, i) => {
        btn.classList.toggle("active", i === index);
    });
}

function filterTable() {
    let input = document.getElementById("search").value.toLowerCase();
    let tables = document.querySelectorAll(".content.active table tr");
    tables.forEach((row, index) => {
        if (index === 0) return; // Omitir encabezados
        let text = row.innerText.toLowerCase();
        row.style.display = text.includes(input) ? "" : "none";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    let modal = document.getElementById("miModal");
    let btnAbrir = document.getElementById("abrirModal");
    let btnCerrar = document.getElementById("cerrarModal");

    

    // Mostrar el modal
    btnAbrir.onclick = function () {
        modal.classList.add("mostrar");
        modal.style.display = "flex";
    };

    

    // Ocultar el modal al hacer clic en el botón de cerrar
    btnCerrar.onclick = function () {
        modal.classList.remove("mostrar");
        setTimeout(() => modal.style.display = "none", 300);
    };

    // Cerrar el modal al hacer clic fuera del contenido
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.classList.remove("mostrar");
            setTimeout(() => modal.style.display = "none", 300);
        }
    };
});


//js guitarra//

/* Cargar los sonidos */
var s1 = new Audio('/static/sounds_guitarra/guitar-string-1.mp3');
var s2 = new Audio('/static/sounds_guitarra/guitar-string-2.mp3');
var s3 = new Audio('/static/sounds_guitarra/guitar-string-3.mp3');
var s4 = new Audio('/static/sounds_guitarra/guitar-string-4.mp3');
var s5 = new Audio('/static/sounds_guitarra/guitar-string-5.mp3');
var s6 = new Audio('/static/sounds_guitarra/guitar-string-6.mp3');

/* Obtener elemento por ID */
function elem(id) {
    return document.getElementById(id);
}

/* Función para tocar la cuerda */
function clickString(thisString) {
    var stringAudio = window[thisString]; // Obtiene el sonido de la cuerda

    if (stringAudio) {
        stringAudio.currentTime = 0; // Reinicia el audio
        stringAudio.play().catch(error => console.error("Error al reproducir el sonido:", error));
    }

    // Agregar vibración visual
    elem(thisString).classList.add("vibrating");
    setTimeout(() => {
        elem(thisString).classList.remove("vibrating");
    }, 500);

    // Iluminar la nota
    var thisNote = thisString + "Note";
    elem(thisNote).classList.add("lightOn");

    // Apagar la nota después de un tiempo
    setTimeout(() => {
        elem(thisNote).classList.remove("lightOn");
    }, 1000);
}

/* Permitir que los navegadores desbloqueen el sonido */
document.addEventListener("click", function enableAudio() {
    s1.play().then(() => {
        s1.pause();
        s1.currentTime = 0;
    }).catch(() => {});

    document.removeEventListener("click", enableAudio);
});

/* Asegurar compatibilidad en móviles */
document.body.addEventListener("touchstart", () => {
    s1.play().then(() => s1.pause());
}, { once: true });

/* Función de hover (para vibración cuando se pasa el mouse) */
function pickString(thisString) {
    if (pick == true) clickString(thisString);
}



//js piano//

const DO4 = new Audio("/static/sounds_piano/DO4.mp3");
      const REb4 = new Audio("/static/sounds_piano/REb4.mp3");
      const RE4 = new Audio("/static/sounds_piano/RE4.mp3");
      const MIb4 = new Audio("/static/sounds_piano/MIb4.mp3");
      const MI4 = new Audio("/static/sounds_piano/MI4.mp3");
      const FA4 = new Audio("/static/sounds_piano/FA4.mp3");
      const SOLb4 = new Audio("/static/sounds_piano/SOLb4.mp3");
      const SOL4 = new Audio("/static/sounds_piano/SOL4.mp3");
      const LAb4 = new Audio("/static/sounds_piano/LAb4.mp3");
      const LA4 = new Audio("/static/sounds_piano/LA4.mp3");
      const SIb4 = new Audio("/static/sounds_piano/SIb4.mp3");
      const SI4 = new Audio("/static/sounds_piano/SI4.mp3");
      const DO5 = new Audio("/static/sounds_piano/DO5.mp3");
      const REb5 = new Audio("/static/sounds_piano/REb5.mp3");
      const RE5 = new Audio("/static/sounds_piano/RE5.mp3");
      const MIb5 = new Audio("/static/sounds_piano/MIb5.mp3");
      const MI5 = new Audio("/static/sounds_piano/MI5.mp3");
        document.querySelectorAll(".white-key, .black-key").forEach(tecla => {
    tecla.addEventListener("click", () => {
        let nota = tecla.getAttribute("data-note");
        reproducirNota(nota);
    });
});

function reproducirNota(nota) {
    const sonido = new Audio(`/static/sounds_piano/${nota}.mp3`);
    sonido.play();
}


window.addEventListener("keydown", ({ keyCode }) => {
    const teclas = {
        65: "A3", 87: "A#3", 83: "B3", 68: "C4", 69: "C#4", 
        70: "D4", 84: "D#4", 71: "E4", 72: "F4", 85: "F#4", 
        74: "G4", 79: "G#4", 75: "A4", 80: "A#4", 76: "B4", 
        186: "C5", 222: "C#5"
    };
    
    let nota = teclas[keyCode];
    if (nota) {
        reproducirNota(nota);
    }
});


