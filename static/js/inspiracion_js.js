document.addEventListener('DOMContentLoaded', function() {
    // Código para el área de upload (se mantiene igual)
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('file-info');
    const infoText = document.querySelector('.info');
    const allowedExtensions = ['docx',"txt", 'pdf', 'jpg', 'jpeg', 'png', 'mp3'];
    const maxFileSize = 5 * 1024 * 1024; // 5MB

    // Eventos de drag and drop (se mantienen igual)
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('highlight'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            flashMessage(`Tipo de archivo no permitido. Extensiones permitidas: ${allowedExtensions.join(', ')}`, 'danger');
            resetFileInput();
            return;
        }

        if (file.size > maxFileSize) {
            flashMessage('El archivo excede el tamaño máximo permitido de 5MB.', 'danger');
            resetFileInput();
            return;
        }

        fileInfo.textContent = `Archivo seleccionado: ${file.name}`;

        if (['jpg', 'jpeg', 'png'].includes(fileExtension)) {
            showImagePreview(file);
        } else if (['mp3'].includes(fileExtension)) {
            showAudioPreview(file);
        } else {
            removePreview();
        }
    }

    function resetFileInput() {
        fileInput.value = '';
        fileInfo.textContent = 'Arrastra tu archivo Word, PDF, Imagen o MP3 aquí';
        removePreview();
    }

    function flashMessage(message, category) {
        const flashContainer = document.createElement('div');
        flashContainer.className = `alert alert-${category}`;
        flashContainer.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(flashContainer, container.firstChild);

        setTimeout(() => {
            flashContainer.remove();
        }, 5000);
    }

    function showImagePreview(file) {
        removePreview();
    
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            const previewContainer = document.createElement('div');
            previewContainer.className = 'preview-container';
    
            const img = document.createElement('img');
            img.src = reader.result;
            img.alt = 'Previsualización de la imagen';
            img.className = 'preview-img';
    
            previewContainer.appendChild(img);
            uploadArea.appendChild(previewContainer);
        }
    }
    
    function showAudioPreview(file) {
        removePreview();

        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = reader.result;
            audio.className = 'preview-audio';
            uploadArea.appendChild(audio);
        }
    }

    function removePreview() {
        const existingImg = document.querySelector('.preview-img');
        const existingAudio = document.querySelector('.preview-audio');
        if (existingImg) existingImg.remove();
        if (existingAudio) existingAudio.remove();
    }

    // Modal para visualización de archivos
    const modal = document.getElementById("archivoModal");
    const modalContent = document.getElementById("archivoDisplay");
    const closeModalBtn = document.querySelector(".close-modal");
    const viewButtons = document.querySelectorAll(".ver-archivo-btn");

    viewButtons.forEach(button => {
        button.addEventListener("click", async function () {
            const tipoArchivo = this.getAttribute("data-tipo").toLowerCase();
            const rutaArchivo = this.getAttribute("data-ruta");
            
            const fullPath = rutaArchivo;
            
            modalContent.innerHTML = "<div class='loading'>Cargando archivo...</div>";
            modal.style.display = "flex";

            try {
                if (tipoArchivo === "txt" || tipoArchivo === "texto") {
                    // Obtener URL segura desde el servidor
                const signedResponse = await fetch(`/url_firmada?ruta=${encodeURIComponent(fullPath)}`);
                const signedData = await signedResponse.json();
                if (!signedData.url) throw new Error("No se pudo generar la URL segura");

                const response = await fetch(signedData.url);
                if (!response.ok) throw new Error("No se pudo cargar el archivo");
                const texto = await response.text();
                    modalContent.innerHTML = `
                        <div class="text-editor-container">
                            <h3>${rutaArchivo.split('/').pop()}</h3>
                            <textarea id="textoCancion" style="width: 100%; height: 300px; font-family: monospace;">${texto}</textarea>
                            <div class="form-group">
                                <label for="copias">Copias por hoja:</label>
                                <select id="copias" style="padding: 5px;">
                                    <option value="8">8</option>
                                    <option value="16">16</option>
                                    <option value="32">32</option>
                                </select>
                            </div>
                            <div class="modal-actions">
                                <button id="guardarTxt">Guardar Cambios</button>
                                <button id="vistaPrevia"></button>
                                <button class="imprimir-btn" onclick="imprimirLetra()">Imprimir</button>
                            </div>
                        </div>
                        <div id="print-preview" style="display: none; margin-top: 20px;"></div>
                    `;
                    
                    document.getElementById("guardarTxt").addEventListener("click", () => {
                        const nuevoTexto = document.getElementById("textoCancion").value;
                        guardarCambiosTxt(rutaArchivo, nuevoTexto);
                    });
                    
                    document.getElementById("vistaPrevia").addEventListener("click", mostrarVistaPrevia);
                    
                } else if (tipoArchivo === "mp3") {
                    modalContent.innerHTML = `
                        <div class="audio-container">
                            <h3>${rutaArchivo.split('/').pop()}</h3>
                            <audio controls style="width: 100%;">
                                <source src="${fullPath}" type="audio/mpeg">
                                Tu navegador no soporta la reproducción de audio.
                            </audio>
                        </div>
                    `;
                } else if (tipoArchivo === "imagen" || tipoArchivo === "jpg" || tipoArchivo === "jpeg" || tipoArchivo === "png") {
                    modalContent.innerHTML = `
                        <div class="image-container">
                            <h3>${rutaArchivo.split('/').pop()}</h3>
                            <img src="${fullPath}" alt="Archivo" 
                                 style="max-width: 100%; max-height: 70vh; object-fit: contain;">
                        </div>
                    `;
                } else if (tipoArchivo === "pdf") {
                    modalContent.innerHTML = `
                        <div class="pdf-container">
                            <h3>${rutaArchivo.split('/').pop()}</h3>
                            <iframe src="${fullPath}" style="width: 100%; height: 70vh;" frameborder="0"></iframe>
                        </div>
                    `;
                } else {
                    modalContent.innerHTML = `
                        <div class="unsupported-file">
                            <p>Este tipo de archivo no puede mostrarse en el visor.</p>
                            <a href="${fullPath}" download class="download-btn">Descargar Archivo</a>
                        </div>
                    `;
                }
            } catch (error) {
                console.error("Error al cargar archivo:", error);
                modalContent.innerHTML = `
                    <div class="error-message">
                        <p>Error al cargar el archivo: ${error.message}</p>
                        <p>Ruta intentada: ${fullPath}</p>
                        <a href="${fullPath}" class="download-btn">Intentar descargar</a>
                    </div>
                `;
            }
        });
    });

    closeModalBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    async function guardarCambiosTxt(rutaRelativa, nuevoTexto) {
        try {
            const response = await fetch('/guardar_txt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    ruta: rutaRelativa,
                    contenido: nuevoTexto 
                })
            });

            if (response.ok) {
                alert("Archivo guardado exitosamente.");
                document.getElementById("archivoModal").style.display = "none";
            } else {
                alert("Error al guardar el archivo.");
            }
        } catch (error) {
            console.error("Error al guardar el archivo:", error);
            alert("Hubo un problema al guardar el archivo.");
        }
    }
});

// FUNCIONES GLOBALES
// FUNCIÓN PARA MOSTRAR VISTA PREVIA (actualizada)
function mostrarVistaPrevia() {
    const texto = document.getElementById("textoCancion").value;
    const copias = parseInt(document.getElementById("copias").value);
    const preview = document.getElementById("print-preview");
    
    preview.innerHTML = '';
    preview.style.display = 'block';
    
    const pageContainer = document.createElement('div');
    pageContainer.className = 'page-container';
    
    // Determinar número de columnas
    const columns = copias <= 2 ? 1 : 2;
    const rows = Math.ceil(copias / columns);
    
    // Crear columnas
    const column1 = document.createElement('div');
    column1.className = 'column';
    const column2 = columns > 1 ? document.createElement('div') : null;
    if (column2) column2.className = 'column';
    
    // Ajustar tamaño de fuente
    const fontSize = copias > 4 ? '10pt' : '11pt';
    const lineHeight = copias > 4 ? '1.3' : '1.4';
    
    // Distribuir copias
    for (let i = 0; i < copias; i++) {
        const copia = document.createElement('div');
        copia.className = 'letra-copia';
        copia.style.fontSize = fontSize;
        copia.style.lineHeight = lineHeight;
        copia.textContent = texto;
        
        if (columns === 1 || i < rows) {
            column1.appendChild(copia);
        } else {
            column2.appendChild(copia);
        }
        
        // Agregar línea de corte si no es la última copia
        if (i < copias - 1) {
            const corte = document.createElement('div');
            corte.className = 'linea-corte';
            corte.textContent = '✄-------------------------------------------✄';
            
            if (columns === 1 || i < rows - 1) {
                column1.appendChild(corte);
            } else if (column2 && i < copias - 1) {
                column2.appendChild(corte);
            }
        }
    }
    
    pageContainer.appendChild(column1);
    if (column2) pageContainer.appendChild(column2);
    preview.appendChild(pageContainer);
}

// FUNCIÓN PARA IMPRIMIR (actualizada)
function imprimirLetra() {
    const texto = document.getElementById("textoCancion").value;
    const copias = parseInt(document.getElementById("copias").value);
    
    // Configuración de diseño
    const columns = copias <= 2 ? 1 : 2;
    const rows = Math.ceil(copias / columns);
    const fontSize = copias > 4 ? '10pt' : '11pt';
    const lineHeight = copias > 4 ? '1.3' : '1.4';
    
    const ventanaImpresion = window.open('', '_blank');
    ventanaImpresion.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Imprimir Letra</title>
            <style>
                @page {
                    size: A4;
                    margin: 0.5cm;
                }
                body {
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }
                .page-container {
                    display: flex;
                    width: 100%;
                    height: 100%;
                    padding: 5mm;
                    box-sizing: border-box;
                }
                .column {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    padding: 0 3mm;
                }
                .letra-copia {
                    white-space: pre-wrap;
                    padding: 3mm;
                    font-size: ${fontSize};
                    line-height: ${lineHeight};
                    page-break-inside: avoid;
                    height: ${100/rows}%;
                    box-sizing: border-box;
                }
                .linea-corte {
                    text-align: center;
                    color: #999;
                    font-size: 10px;
                    margin: 2mm 0;
                }
                @media print {
                    body {
                        padding: 0;
                        margin: 0;
                    }
                    .page-container {
                        padding: 0;
                    }
                    .column {
                        padding: 0 2mm;
                    }
                    .letra-copia {
                        border: none;
                        padding: 2mm;
                    }
                    .linea-corte {
                        visibility: visible;
                    }
                }
            </style>
        </head>
        <body>
            <div class="page-container">
                <div class="column">
    `);
    
    // Distribuir copias en columnas
    for (let i = 0; i < copias; i++) {
        // Cambiar a segunda columna cuando corresponda
        if (columns > 1 && i === rows) {
            ventanaImpresion.document.write(`
                </div>
                <div class="column">
            `);
        }
        
        ventanaImpresion.document.write(`
            <div class="letra-copia">
                ${texto.replace(/\n/g, '<br>')}
            </div>
        `);
        
        // Agregar línea de corte si no es la última copia
        if (i < copias - 1) {
            if (columns === 1 || (columns > 1 && i !== rows - 1 && i !== copias - 1)) {
                ventanaImpresion.document.write(`
                    <div class="linea-corte">
                        ✄-------------------------------------------✄
                    </div>
                `);
            }
        }
    }
    
    ventanaImpresion.document.write(`
                </div>
            </div>
            <script>
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 300);
                };
            </script>
        </body>
        </html>
    `);
    ventanaImpresion.document.close();
}

function imprimirArchivo(button) {
    const rutaGCS = button.getAttribute('data-ruta'); 
    const ventana = window.open(rutaGCS, '_blank');
    ventana.onload = function() {
        ventana.print();
    };
}