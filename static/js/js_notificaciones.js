document.addEventListener("DOMContentLoaded", function() {
    const notificationBtn = document.getElementById('notification-btn');
    if (!notificationBtn) {
        console.error("El botón de notificaciones no se encontró en el DOM.");
        return;
    }

    const notificationPanel = document.getElementById('notification-panel');
    const closeBtn = document.getElementById('close-notifications');
    const notificationList = document.getElementById('notification-list');
    const notificationCount = document.getElementById('notification-count');

    const id_profesor = JSON.parse(document.getElementById('notification-panel').dataset.idProfesor);


    function cargarNotificaciones() {
        fetch(`/notificaciones?id_profesor=${id_profesor}`)
            .then(response => response.json())
            .then(data => {
                notificationList.innerHTML = "";
                let count = data.length;
                notificationCount.textContent = count > 0 ? count : "";
    
                if (data.length === 0) {
                    notificationList.innerHTML = "<p>No hay nuevas notificaciones</p>";
                    return;
                }
    
                data.forEach(n => {
                    let notificacion = document.createElement('div');
                    notificacion.classList.add('notification');
                    notificacion.innerHTML = `
                        <img src="static/img/educar.png" alt="Avatar">
                        <div>
                            <div class="notification-text">${n.mensaje}</div>
                            <div class="notification-time">${n.fecha}</div>
                        </div>
                    `;
                    notificationList.appendChild(notificacion);
                });
            })
            .catch(error => console.error("Error obteniendo notificaciones:", error));
    
    
    }

    notificationBtn.addEventListener('click', () => {
        notificationPanel.classList.toggle('active');
        fetch(`/marcar_notificaciones?id_profesor=${id_profesor}`, { method: 'POST' });
        notificationCount.textContent = "0";
    });

    closeBtn.addEventListener('click', () => {
        notificationPanel.classList.remove('active');
    });

    setInterval(() => {
        if (notificationPanel.classList.contains('active')) {
            cargarNotificaciones();
        }
    }, 40000); // Se ejecuta cada 10 segundos solo si el panel está abierto
    
    cargarNotificaciones();
});

