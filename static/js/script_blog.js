function addComment() {
    const commentText = document.getElementById("new-comment").value;
    if (commentText.trim() === "") {
        alert("El comentario no puede estar vacío.");
        return;
    }

    const commentContainer = document.createElement("div");
    commentContainer.classList.add("blog-post");
    
    // Crear el contenido del nuevo comentario
    commentContainer.innerHTML = `
        <div class="d-flex">
            <div class="profile-photo">
                <!-- Imagen de perfil en publicación (se puede añadir aquí) -->
            </div>
            <div class="flex-grow-1 ms-3">
                <p>${commentText}</p>
                <span>${new Date().toLocaleString('es-ES')} - Posteado por: Usuario Actual</span>
                <div class="interaction-buttons mt-2">
                    <button class="btn btn-primary btn-sm like-button"><i class="fas fa-thumbs-up"></i> Me gusta</button>
                    <span class="like-count">0</span>
                    <button class="btn btn-primary btn-sm reply-button"><i class="fas fa-reply"></i> Responder</button>
                    <button class="btn btn-danger btn-sm delete-button"><i class="fas fa-trash"></i> Borrar</button>
                    <button class="btn btn-outline-danger btn-sm report-button mt-2"><i class="fas fa-flag"></i> Reportar</button>
                </div>
                <div class="reply-box mt-3" style="display: none;">
                    <textarea class="form-control mb-2" rows="2" placeholder="Escribe tu respuesta aquí"></textarea>
                    <button onclick="sendReply(this)" class="btn btn-share btn-sm"><i class="fas fa-share"></i> Enviar respuesta</button>
                </div>
            </div>
        </div>
    `;

    // Añadir el nuevo comentario al contenedor de comentarios
    document.getElementById("comments-container").appendChild(commentContainer);
    document.getElementById("new-comment").value = ""; // Limpiar el campo de entrada

    // Añadir funcionalidad a los botones del nuevo comentario
    addCommentInteractions(commentContainer);
}

function addCommentInteractions(commentContainer) {
    // Funcionalidad del botón Me gusta
    const likeButton = commentContainer.querySelector(".like-button");
    likeButton.addEventListener("click", function() {
        let likeCount = this.nextElementSibling;
        let currentLikes = parseInt(likeCount.textContent);
        likeCount.textContent = currentLikes + 1;
    });

    // Funcionalidad del botón Responder
    const replyButton = commentContainer.querySelector(".reply-button");
    replyButton.addEventListener("click", function() {
        let replyBox = this.closest(".blog-post").querySelector(".reply-box");
        replyBox.style.display = replyBox.style.display === "none" ? "block" : "none";
    });

    // Funcionalidad del botón Borrar
    const deleteButton = commentContainer.querySelector(".delete-button");
    deleteButton.addEventListener("click", function() {
        if (confirm("¿Seguro que deseas borrar este comentario?")) {
            this.closest(".blog-post").remove();
        }
    });

    // Funcionalidad del botón Reportar
    const reportButton = commentContainer.querySelector(".report-button");
    reportButton.addEventListener("click", function() {
        alert("Este comentario ha sido reportado.");
    });
}

function sendReply(button) {
    const replyText = button.previousElementSibling.value;
    if (replyText.trim() === "") {
        alert("La respuesta no puede estar vacía.");
        return;
    }

    const replyContainer = document.createElement("div");
    replyContainer.classList.add("reply");
    replyContainer.innerHTML = `<p>${replyText}</p><span>${new Date().toLocaleString('es-ES')} - Respondido por: Usuario Actual</span>`;

    // Agregar la respuesta después de la caja de respuesta
    button.parentElement.parentElement.appendChild(replyContainer);
    button.previousElementSibling.value = ""; // Limpiar el campo de respuesta
}


document.addEventListener("DOMContentLoaded", function() { //API de novedades Musicales
    const apiKey = '0695ed95086650662f3daea8ce48f55c'; // Reemplaza esto con tu API Key de Last.fm

    fetch(`http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&api_key=${apiKey}&format=json&limit=10`)
        .then(response => response.json())
        .then(data => {
            const tracks = data.tracks.track;
            const carouselItems = document.getElementById('carouselItems');

            tracks.forEach((track, index) => {
                const isActive = index === 0 ? 'active' : '';
                const item = document.createElement('div');
                item.className = `carousel-item ${isActive}`;
                item.innerHTML = `
                    <img src="${track.image[2]['#text']}" class="d-block w-100" alt="${track.name}">
                    <div class="carousel-caption d-none d-md-block">
                        <h5>${track.name} - ${track.artist.name}</h5>
                        <p>Escuchas: ${track.playcount}</p>
                    </div>
                `;
                carouselItems.appendChild(item);
            });
        })
        .catch(error => console.error('Error fetching data from Last.fm API:', error));
});

