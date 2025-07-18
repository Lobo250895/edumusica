document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de comentarios iniciado');
    
    let currentProjectId = null;
    const commentTemplate = document.querySelector('.comment-template');

    if (!commentTemplate) {
        console.error('Error crítico: No se encontró la plantilla de comentarios');
        return;
    }

    function setupProjectButtons() {
        const buttons = document.querySelectorAll('.btn-ver-proyecto');
        
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                currentProjectId = this.getAttribute('data-id');
                const projectName = this.closest('tr').querySelector('td').textContent;
                
                console.log(`Proyecto seleccionado: ${projectName} (ID: ${currentProjectId})`);
                
                document.getElementById('current-project-name').textContent = projectName;
                document.getElementById('no-project-selected').style.display = 'none';
                document.getElementById('comments-content').style.display = 'block';

                loadComments(currentProjectId);
            });
        });
    }
    function createCommentElement(comment) {
        const commentClone = commentTemplate.cloneNode(true);
        commentClone.classList.remove('comment-template');
        commentClone.style.display = 'block';

        const avatarUrl = comment.avatar_autor
            ? `https://storage.googleapis.com/storage-edumusica/profile/${comment.avatar_autor}`
            : '/static/uploads/profile/default.png';
        commentClone.querySelector('.comment-avatar').src = avatarUrl;
        commentClone.querySelector('.comment-author').textContent = comment.nombre_autor || 'Anónimo';
        commentClone.querySelector('.comment-date').textContent = formatDate(comment.fecha_creacion);
        commentClone.querySelector('.comment-content').textContent = comment.contenido;

        // Configurar botón de responder
        setupReplyButton(commentClone, comment.id);

        // Renderizar respuestas (comentarios anidados)
        if (comment.respuestas && comment.respuestas.length > 0) {
            comment.respuestas.forEach(respuesta => {
                const respuestaElement = createCommentElement(respuesta);
                respuestaElement.classList.add('respuesta');
                respuestaElement.style.marginLeft = '30px';  // Sangría visual para respuestas
                commentClone.appendChild(respuestaElement);
            });
        }

        return commentClone;
    }

    // Cargar comentarios desde el servidor para el proyecto actual
    function loadComments(projectId) {
        console.log(`Cargando comentarios para proyecto ${projectId}`);
        
        const commentsList = document.getElementById('comments-list');
        commentsList.innerHTML = '<p class="loading">Cargando comentarios...</p>';
        
        fetch(`/proyectos/${projectId}/comentarios`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Comentarios recibidos:', data);
                renderComments(data);
            })
            .catch(error => {
                console.error('Error al cargar comentarios:', error);
                commentsList.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            });
    }

    // Renderizar comentarios en el contenedor
    function renderComments(comments) {
        try {
            const container = document.getElementById('comments-list');
            if (!container) {
                console.error('Error: No se encontró el contenedor de comentarios');
                return;
            }

            container.innerHTML = '';
            commentTemplate.style.display = 'none';

            if (!comments || comments.length === 0) {
                container.innerHTML = '<p class="no-comments">No hay comentarios aún</p>';
                return;
            }

            comments.forEach(comment => {
                const commentElement = createCommentElement(comment);
                container.appendChild(commentElement);
            });

        } catch (error) {
            console.error('Error en renderComments:', error);
            const container = document.getElementById('comments-list');
            if (container) {
                container.innerHTML = '<p class="error">Error al cargar los comentarios</p>';
            }
        }
    }

    // Configurar botón de responder para un comentario dado
    function setupReplyButton(commentElement, commentId) {
        const replyBtn = commentElement.querySelector('.btn-reply');
        const replyBox = commentElement.querySelector('.reply-box');
        const submitBtn = commentElement.querySelector('.btn-submit-reply');
        const cancelBtn = commentElement.querySelector('.btn-cancel-reply');
        const replyTextarea = commentElement.querySelector('.reply-text');
        
        replyBtn.addEventListener('click', () => {
            replyBox.style.display = 'block';
            replyTextarea.focus();
        });
        
        cancelBtn.addEventListener('click', () => {
            replyTextarea.value = '';
            replyBox.style.display = 'none';
        });
        
        submitBtn.addEventListener('click', () => {
            const replyText = replyTextarea.value.trim();
            if (!replyText) return;
            
            postComment(replyText, commentId);
            replyTextarea.value = '';
            replyBox.style.display = 'none';
        });
    }

    // Enviar nuevo comentario o respuesta al servidor
    function postComment(content, parentId = null) {
        fetch('/comentarios/nuevo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')  // Ajusta si usás otro método CSRF
            },
            body: JSON.stringify({
                proyecto_id: currentProjectId,
                contenido: content,
                comentario_padre_id: parentId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadComments(currentProjectId); // Recargar comentarios tras enviar
            } else {
                alert('No se pudo enviar el comentario');
            }
        })
        .catch(error => console.error('Error al enviar comentario:', error));
    }

    // Formatear fecha para mostrar
    function formatDate(dateString) {
        if (!dateString) return '';
        
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Date(dateString).toLocaleDateString('es-ES', options);
    }

    // Obtener cookie por nombre (para CSRF)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // --- NUEVO: Listener para enviar comentario raíz ---
    document.getElementById('submit-comment').addEventListener('click', () => {
        const contenido = document.getElementById('new-comment-text').value.trim();
        if (!contenido) return alert('Escribe un comentario antes de enviar');
        postComment(contenido, null);
        document.getElementById('new-comment-text').value = '';
    });

    // Inicialización
    setupProjectButtons();
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('Sistema de eliminación de proyectos iniciado');

    // Agregar eventos a todos los botones de eliminar
    document.querySelectorAll('.btn-eliminar-proyecto').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();  // Evita comportamiento por defecto si está en un form
            const proyectoId = button.getAttribute('data-id');

            if (confirm('¿Estás segura/o de que querés eliminar este proyecto?')) {
                eliminarProyecto(proyectoId);
            }
        });
    });

    function eliminarProyecto(proyectoId) {
        fetch('/proyectos/eliminar', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ proyecto_id: proyectoId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Proyecto eliminado correctamente');
                location.reload();  // Recargar la página para actualizar la lista
            } else {
                alert('No se pudo eliminar el proyecto: ' + (data.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error al eliminar el proyecto:', error);
            alert('Error al realizar la solicitud');
        });
    }
});

document.getElementById('file').addEventListener('change', function(event) {
            const fileInfo = document.getElementById('file-info');
            if (event.target.files.length > 0) {
                const fileName = event.target.files[0].name;
                fileInfo.textContent = `Archivo seleccionado: ${fileName}`;
                fileInfo.style.color = 'green';
            } else {
                fileInfo.textContent = 'Arrastra tu archivo Word o PDF aquí';
                fileInfo.style.color = 'black';
            }
        });

        document.addEventListener('DOMContentLoaded', () => {
            const visor = document.getElementById('visor');
            const iframe = document.getElementById('iframe-proyecto');
            const btnCerrar = document.getElementById('cerrar-visor');

            // Manejar clics en botones "Ver Proyecto"
            document.querySelectorAll('.btn-ver-proyecto').forEach(button => {
                button.addEventListener('click', () => {
                    const url = button.getAttribute('data-url');
                    const extension = url.split('.').pop().toLowerCase();
                    
                    
                    if (extension === 'pdf') {
                        iframe.src = `${url}#toolbar=0`;
                    } else if (extension === 'docx') {
                        iframe.src = `https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`;
                    } else {
                        iframe.src = url;
                    }

                    visor.classList.add('mostrar');
                });
            });

            // Cerrar visor
            btnCerrar.addEventListener('click', () => {
                visor.classList.remove('mostrar');
                iframe.src = '';
            });

            async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
            // No necesitas headers para FormData, el navegador los setea automáticamente
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 1. Mostrar mensaje de éxito
            alert('Proyecto subido correctamente');
            
            // 2. Actualizar la lista de proyectos sin recargar
            await updateProjectsList();
            
            // 3. Resetear el formulario
            form.reset();
            document.getElementById('file-info').textContent = 'Arrastra tu archivo Word o PDF aquí';
            document.getElementById('file-info').style.color = 'black';
        } else {
            alert('Error: ' + (result.message || 'Error al subir el proyecto'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión');
    }
}

async function updateProjectsList() {
    try {
        const response = await fetch('/proyectos/get-projects');
        const data = await response.json();
        
        // Actualizar las tres tablas de proyectos
        updateTable('mis-proyectos', data.propios);
        updateTable('proyectos-publicos', data.publicos);
        updateTable('ayuda-proyectos', data.admin);
    } catch (error) {
        console.error('Error al actualizar proyectos:', error);
    }
}

function updateTable(tableType, projects) {
    const tableBody = document.querySelector(`#${tableType} tbody`);
    tableBody.innerHTML = '';
    
    projects.forEach(project => {
        const row = document.createElement('tr');
        // Construye la fila según tus necesidades
        row.innerHTML = `
            <td>${project.nombre}</td>
            <td>${project.fecha_subida}</td>
            <td>${project.estado}</td>
            <td>${project.es_publico ? 'Público' : 'Privado'}</td>
            <td>
                <button class="btn-ver-proyecto" data-id="${project.id}" data-url="${project.proyecto}">
                    Ver Proyecto
                </button>
                ${tableType === 'mis-proyectos' ? 
                `<button class="btn-eliminar-proyecto" data-id="${project.id}" title="Eliminar proyecto">
                    <i class="fas fa-trash"></i> Eliminar
                </button>` : ''}
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Reasignar eventos a los nuevos botones
    assignProjectEvents();
}
});