  document.addEventListener('DOMContentLoaded', function() {
      const fileInput = document.getElementById('file');
      const fileDropArea = document.getElementById('fileDropArea');
      const fileInfo = document.getElementById('file-info');
      
      // Manejar arrastrar y soltar
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          fileDropArea.addEventListener(eventName, preventDefaults, false);
      });
      
      function preventDefaults(e) {
          e.preventDefault();
          e.stopPropagation();
      }
      
      ['dragenter', 'dragover'].forEach(eventName => {
          fileDropArea.addEventListener(eventName, highlight, false);
      });
      
      ['dragleave', 'drop'].forEach(eventName => {
          fileDropArea.addEventListener(eventName, unhighlight, false);
      });
      
      function highlight() {
          fileDropArea.classList.add('highlight');
      }
      
      function unhighlight() {
          fileDropArea.classList.remove('highlight');
      }
      
      // Manejar archivos soltados
      fileDropArea.addEventListener('drop', handleDrop, false);
      
      function handleDrop(e) {
          const dt = e.dataTransfer;
          const files = dt.files;
          fileInput.files = files;
          updateFileInfo(files[0]);
      }
      
      // Manejar selección de archivos
      fileInput.addEventListener('change', function() {
          if(this.files && this.files[0]) {
              updateFileInfo(this.files[0]);
          }
      });
      
      // Actualizar la información del archivo
      function updateFileInfo(file) {
          fileInfo.textContent = file.name;
          fileInfo.style.fontWeight = 'bold';
          fileInfo.style.color = '#2c3e50';
      }
      
      // Validación antes de enviar
      document.getElementById('uploadForm').addEventListener('submit', function(e) {
          if(!fileInput.files.length) {
              e.preventDefault();
              alert('Por favor selecciona un archivo');
          }
      });


    const parrafos = [
            "La música es parte de nuestra vida, está en todas partes: en un pájaro que canta, en el agua que corre. Vivimos rodeados de sonidos, música, ruidos y armonías. Los seres humanos poseemos cinco sentidos: oído, vista, olfato, gusto y tacto. El primero que empieza a funcionar es el auditivo.",
            "Te proponemos una actividad para reconocer sonidos: siéntate en un lugar tranquilo, acomódate y cierra los ojos ¿Qué oyes? Escucha atentamente. ¿Puedes reconocer los sonidos? Escúchalos hasta poder distinguir unos de otros. Escuchar es como mirar en una pieza en penumbra: primero, los sonidos parecen un ruido sin sentido, nada diferenciado. Luego, como cuando abrimos los ojos en la oscuridad, el oído comenzará a distinguir unos de otros.",
            "Pídeles que escriban una letra original sobre un tema actual usando una base rítmica que elijan.",
            "Analicen juntos cómo cambia el estilo de una canción si se interpreta con distintos instrumentos.",
            "Invitá a los estudiantes a hacer una pequeña performance de una canción con expresión escénica.",
            "Comparen versiones de la misma canción en distintos géneros y analicen qué cambia.",
            "Practiquemos Ondas Sonoras: Para que puedas entender cómo es una onda sonora, te sugerimos dos actividades. Busca un compañero y consigan una cuerda. Tomen una punta de cada uno y pónganse uno frente al otro midiendo una distancia que permita estirar la cuerda para que no quede tensa. Ahora comienza a hacer un leve movimiento con la cuerda, de manera que se forme una pequeña ondulación. Observa la forma en que se mueve la soga, ese dibujo de una ola moviéndose de una punta a la otra es la representación gráfica de lo que ocurre con el sonido. Llena con agua un recipiente de boca ancha y poca profundidad. Busca una piedra y lánzala con suavidad dentro del frasco. Al caer la piedra se dibujará sobre el agua una onda que se expanderá hacia los costados. Ese dibujo es la representación gráfica del sonido al transmitirse."
        ];

        let indiceActual = 0;
        const contenedor = document.getElementById("carruselTexto");
        const btnAnterior = document.getElementById("btnAnterior");
        const btnSiguiente = document.getElementById("btnSiguiente");
        const indicadoresContainer = document.getElementById("indicadores");
        let intervalo;
        
        // Crear indicadores
        function crearIndicadores() {
            indicadoresContainer.innerHTML = '';
            parrafos.forEach((_, index) => {
                const indicador = document.createElement("div");
                indicador.classList.add("indicator");
                if (index === indiceActual) {
                    indicador.classList.add("active");
                }
                indicador.addEventListener("click", () => {
                    cambiarParrafo(index);
                });
                indicadoresContainer.appendChild(indicador);
            });
        }
        
        // Actualizar indicadores
        function actualizarIndicadores() {
            const indicadores = document.querySelectorAll(".indicator");
            indicadores.forEach((ind, index) => {
                if (index === indiceActual) {
                    ind.classList.add("active");
                } else {
                    ind.classList.remove("active");
                }
            });
        }
        
        // Mostrar párrafo actual
        function mostrarParrafo() {
            contenedor.textContent = parrafos[indiceActual];
            actualizarIndicadores();
            
            // Deshabilitar botón anterior si estamos en el primer párrafo
            btnAnterior.disabled = indiceActual === 0;
            
            // Deshabilitar botón siguiente si estamos en el último párrafo
            btnSiguiente.disabled = indiceActual === parrafos.length - 1;
        }
        
        // Cambiar párrafo
        function cambiarParrafo(nuevoIndice) {
            // Animación de desvanecimiento
            contenedor.style.opacity = '0';
            
            setTimeout(() => {
                indiceActual = nuevoIndice;
                mostrarParrafo();
                contenedor.style.opacity = '1';
                
                // Reiniciar el intervalo automático
                reiniciarIntervalo();
            }, 300);
        }
        
        // Siguiente párrafo
        function siguienteParrafo() {
            if (indiceActual < parrafos.length - 1) {
                cambiarParrafo(indiceActual + 1);
            }
        }
        
        // Párrafo anterior
        function anteriorParrafo() {
            if (indiceActual > 0) {
                cambiarParrafo(indiceActual - 1);
            }
        }
        
        // Reiniciar intervalo automático
        function reiniciarIntervalo() {
            clearInterval(intervalo);
            intervalo = setInterval(siguienteParrafo, 15000);
        }
        
        // Event listeners
        btnSiguiente.addEventListener("click", siguienteParrafo);
        btnAnterior.addEventListener("click", anteriorParrafo);
        
        // Inicializar
        crearIndicadores();
        mostrarParrafo();
        reiniciarIntervalo();
        
        // Pausar el carrusel cuando el mouse está sobre él
        contenedor.addEventListener("mouseenter", () => {
            clearInterval(intervalo);
        });
        
        contenedor.addEventListener("mouseleave", reiniciarIntervalo);
        
});

  // Función para mostrar/ocultar pestañas
function showTab(index) {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.content');
    
    tabs.forEach((tab, i) => {
        if (i === index) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    contents.forEach((content, i) => {
        if (i === index) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    // Actualizar la URL con el parámetro de categoría
    let categoria = '';
    if (index === 0) categoria = 'web';
    if (index === 1) categoria = 'peliculas';
    if (index === 2) categoria = 'libros';
    
    window.history.pushState({}, '', `?categoria=${categoria}`);
}


// Funciones para el modal
function openModal(tipo, id) {
    const modal = document.getElementById('resourceModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalNombre = document.getElementById('modalNombre');
    const modalTipo = document.getElementById('modalTipo');
    const modalTamanio = document.getElementById('modalTamanio');
    const modalFecha = document.getElementById('modalFecha');
    const modalUrl = document.getElementById('modalUrl');
    const modalFile = document.getElementById('modalFile');
    const modalUrlContainer = document.getElementById('modalUrlContainer');
    const modalFileContainer = document.getElementById('modalFileContainer');
    const modalActionBtn = document.getElementById('modalActionBtn');
    
    // Simular datos según el tipo
    if (tipo === 'web') {
        modalTitle.textContent = 'Detalles del Enlace Web';
        modalTipo.textContent = 'Enlace Web';
        modalUrlContainer.style.display = 'flex';
        modalFileContainer.style.display = 'none';
        
        // Simular datos de un recurso web
        modalNombre.textContent = `Recurso Web ${id}`;
        modalTamanio.textContent = 'N/A';
        modalFecha.textContent = '2025-05-09';
        modalUrl.textContent = 'www.coursera.org';
        modalUrl.innerHTML = '<a href="www.coursera.org" target="_blank">www.coursera.org</a>';
        
        modalActionBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> Visitar Enlace';
        modalActionBtn.onclick = function() {
            window.open('www.coursera.org', '_blank');
        };
    } 
    else  if (tipo === 'pelicula') {
        modalActionBtn.innerHTML = '<i class="fas fa-play"></i> Ver Película';
        modalActionBtn.onclick = function() {
            closeModal();
            openVideoModal('/ver-pelicula?id=' + id, modalNombre.textContent);
        };
    } 
    else if (tipo === 'libro') {
        modalActionBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Ver PDF';
        modalActionBtn.onclick = function() {
            closeModal();
            openPdfModal('/ver-libro?id=' + id, modalNombre.textContent);
        };
    }
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('resourceModal').style.display = 'none';
}

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
    const modal = document.getElementById('resourceModal');
    if (event.target === modal) {
        closeModal();
    }
}


// Funciones para el modal de video
function openVideoModal(videoUrl, title) {
    const modal = document.getElementById('videoModal');
    const titleElement = document.getElementById('videoModalTitle');
    const frame = document.getElementById('videoFrame');

    titleElement.textContent = title;
    modal.style.display = 'block';

    // Mostrar carga
    frame.src = '';
    frame.style.display = 'none';

    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.textContent = 'Cargando video...';
    frame.parentElement.appendChild(loading);

    frame.onload = function () {
        loading.remove();
        frame.style.display = 'block';
    };

    frame.src = videoUrl;
}



function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const frame = document.getElementById('videoFrame');
    
    frame.src = ''; // Detener el video
    modal.style.display = 'none';
}

// Funciones para el modal de PDF
function openPdfModal(pdfUrl, title) {
    const modal = document.getElementById('pdfModal');
    const titleElement = document.getElementById('pdfModalTitle');
    const frame = document.getElementById('pdfFrame');

    titleElement.textContent = title;
    modal.style.display = 'block';

    // Mostrar mensaje de carga
    frame.src = '';
    frame.style.display = 'none';

    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.textContent = 'Cargando PDF...';
    frame.parentElement.appendChild(loading);

    // Cargar el PDF
    frame.onload = function () {
        loading.remove();
        frame.style.display = 'block';
    };

    frame.src = pdfUrl;
}


function closePdfModal() {
    const modal = document.getElementById('pdfModal');
    const frame = document.getElementById('pdfFrame');
    
    frame.src = ''; // Limpiar el PDF
    modal.style.display = 'none';
}

function mostrarTooltip(link) {
    const tooltip = link.querySelector('.tooltip-msg');
    tooltip.style.visibility = 'visible';
    tooltip.style.opacity = '1';
}

function ocultarTooltip(link) {
    const tooltip = link.querySelector('.tooltip-msg');
    tooltip.style.visibility = 'hidden';
    tooltip.style.opacity = '0';
}


window.onclick = function(event) {
    const resourceModal = document.getElementById('resourceModal');
    const videoModal = document.getElementById('videoModal');
    const pdfModal = document.getElementById('pdfModal');
    
    if (event.target === resourceModal) {
        closeModal();
    }
    if (event.target === videoModal) {
        closeVideoModal();
    }
    if (event.target === pdfModal) {
        closePdfModal();
    }
}

// juego musical
const preguntas = [
    {
        audio: "https://storage.googleapis.com/storage-edumusica/musica/violin.mp3",
        opciones: ["Trompeta", "Violín", "Batería"],
        respuestaCorrecta: "Violín"
    },
    {
        audio: "https://storage.googleapis.com/storage-edumusica/musica/guitarra.mp3",
        opciones: ["Guitarra", "Batería", "Trompeta"],
        respuestaCorrecta: "Guitarra"
    },
    {
        audio: "https://storage.googleapis.com/storage-edumusica/musica/bateria.mp3",
        opciones: ["Violín", "Batería", "Flauta"],
        respuestaCorrecta: "Batería"
    },
    {
        audio: "https://storage.googleapis.com/storage-edumusica/musica/trompeta.mp3",
        opciones: ["Piano", "Trompeta", "Guitarra"],
        respuestaCorrecta: "Trompeta"
    }
];

let indiceActual = 0;
let puntaje = 0;

function cargarPregunta() {
    const pregunta = preguntas[indiceActual];
    document.getElementById("audioInstrumento").src = pregunta.audio;

    const opcionesDiv = document.getElementById("opcionesRespuestas");
    opcionesDiv.innerHTML = "";

    pregunta.opciones.forEach(opcion => {
        const boton = document.createElement("button");
        boton.textContent = opcion;
        boton.onclick = () => verificarRespuesta(opcion);
        opcionesDiv.appendChild(boton);
    });

    document.getElementById("resultado").textContent = "";
}

function verificarRespuesta(seleccionado) {
    const correcta = preguntas[indiceActual].respuestaCorrecta;
    const resultado = document.getElementById("resultado");

    if (seleccionado === correcta) {
        resultado.textContent = "¡Correcto! 🎉";
        resultado.style.color = "green";
        puntaje++;
    } else {
        resultado.textContent = `Incorrecto. Era ${correcta} 🙁`;
        resultado.style.color = "red";
    }

    document.getElementById("puntaje").textContent = `Puntaje: ${puntaje}`;

    // Espera 2 segundos y pasa a la siguiente
    setTimeout(() => {
        indiceActual++;
        if (indiceActual < preguntas.length) {
            cargarPregunta();
        } else {
            resultado.textContent = `Juego terminado 🎵 ¡Puntaje final: ${puntaje}/${preguntas.length}!`;
            document.getElementById("opcionesRespuestas").innerHTML = "";
        }
    }, 2000);
}

function reiniciarJuego() {
    indiceActual = 0;
    puntaje = 0;
    document.getElementById("puntaje").textContent = "Puntaje: 0";
    cargarPregunta();
}

// Inicia juego
window.onload = cargarPregunta;

