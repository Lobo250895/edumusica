document.addEventListener('DOMContentLoaded', function() {
            // Pasar los eventos desde Flask a JavaScript
            const eventosDesdeBackend = JSON.parse(document.getElementById('events-data').textContent);
            let events = eventosDesdeBackend || [];
            let currentDate = new Date();
            let selectedDate = new Date();
            let isSynced = false;
            let editingEventId = null;

            // Elementos del DOM
            const calendarDays = document.getElementById('calendarDays');
            const currentMonthElement = document.querySelector('.current-month');
            const selectedDateElement = document.querySelector('.selected-date');
            const eventsList = document.getElementById('eventsList');
            const eventModal = document.getElementById('eventModal');
            const eventForm = document.getElementById('eventForm');
            const modalTitle = document.getElementById('modalTitle');
            const addEventBtn = document.getElementById('addEventBtn');
            const closeModal = document.getElementById('closeModal');
            const cancelBtn = document.getElementById('cancelBtn');
            const syncBtn = document.getElementById('syncBtn');

            // Inicializar calendario
            function initCalendar() {
                renderCalendar();
                renderEvents();
                updateSelectedDateDisplay();
            }

            // Renderizar calendario
            function renderCalendar() {
                calendarDays.innerHTML = '';
                
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                currentMonthElement.textContent = `${getMonthName(month)} ${year}`;
                
                const firstDay = new Date(year, month, 1);
                const lastDay = new Date(year, month + 1, 0);
                const daysInMonth = lastDay.getDate();
                const startingDay = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
                
                // Días del mes anterior
                const prevMonthLastDay = new Date(year, month, 0).getDate();
                for (let i = 0; i < startingDay; i++) {
                    const day = prevMonthLastDay - startingDay + i + 1;
                    const dayElement = document.createElement('div');
                    dayElement.classList.add('day-cell');
                    dayElement.textContent = day;
                    dayElement.style.opacity = '0.5';
                    calendarDays.appendChild(dayElement);
                }
                
                // Días del mes actual
                const today = new Date();
                for (let i = 1; i <= daysInMonth; i++) {
                    const dayElement = document.createElement('div');
                    dayElement.classList.add('day-cell');
                    dayElement.textContent = i;
                    
                    const date = new Date(year, month, i);
                    if (date.toDateString() === today.toDateString()) {
                        dayElement.classList.add('today');
                    }
                    
                    if (date.toDateString() === selectedDate.toDateString()) {
                        dayElement.classList.add('selected');
                    }
                    
                    // Marcar días con eventos
                    if (hasEventsOnDate(date)) {
                        dayElement.classList.add('has-events');
                    }
                    
                    dayElement.addEventListener('click', () => {
                        selectedDate = date;
                        renderCalendar();
                        renderEvents();
                        updateSelectedDateDisplay();
                    });
                    
                    calendarDays.appendChild(dayElement);
                }
                
                // Días del próximo mes
                const totalCells = startingDay + daysInMonth;
                const remainingCells = totalCells > 35 ? 42 - totalCells : 35 - totalCells;
                for (let i = 1; i <= remainingCells; i++) {
                    const dayElement = document.createElement('div');
                    dayElement.classList.add('day-cell');
                    dayElement.textContent = i;
                    dayElement.style.opacity = '0.5';
                    calendarDays.appendChild(dayElement);
                }
            }

            // Verificar si hay eventos en una fecha específica
            function hasEventsOnDate(date) {
                const dateStr = formatDateForComparison(date);
                return events.some(event => {
                    const eventDateStr = event.fecha; // Ya está en formato YYYY-MM-DD
                    return eventDateStr === dateStr;
                });
            }

            // Formatear fecha para comparación (YYYY-MM-DD)
            function formatDateForComparison(date) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }

            // Obtener nombre del mes
            function getMonthName(monthIndex) {
                const months = [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                ];
                return months[monthIndex];
            }

            // Actualizar la visualización de la fecha seleccionada
            function updateSelectedDateDisplay() {
                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                selectedDateElement.textContent = selectedDate.toLocaleDateString('es-ES', options);
            }

            // Renderizar eventos para la fecha seleccionada
            function renderEvents() {
                eventsList.innerHTML = '';
                
                const filteredEvents = events.filter(event => {
                    const eventDateStr = event.fecha; // Ya está en formato YYYY-MM-DD
                    const selectedDateStr = formatDateForComparison(selectedDate);
                    return eventDateStr === selectedDateStr;
                });
                
                if (filteredEvents.length === 0) {
                    eventsList.innerHTML = '<p>No hay eventos programados para este día.</p>';
                    return;
                }
                
                filteredEvents.sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
                
                filteredEvents.forEach(event => {
                    const eventElement = document.createElement('div');
                    eventElement.classList.add('event-card');
                    
                    const typeClass = event.tipo || 'class';
                    
                    eventElement.innerHTML = `
                        <div class="event-time">${formatTime(event.hora_inicio)} - ${formatTime(event.hora_fin)}</div>
                        <h3 class="event-title">${event.titulo}</h3>
                        <span class="event-type ${typeClass}">${getTypeName(event.tipo)}</span>
                        ${event.lugar ? `<span class="event-location">${event.lugar}</span>` : ''}
                        <div class="event-actions">
                            <button class="event-action material-icons" data-id="${event.id}">edit</button>
                            <button class="event-action material-icons" data-id="${event.id}">delete</button>
                        </div>
                    `;
                    
                    eventsList.appendChild(eventElement);
                });
                
                // Agregar event listeners a los botones de acción
                document.querySelectorAll('.event-action').forEach(button => {
                    button.addEventListener('click', function() {
                        const eventId = parseInt(this.getAttribute('data-id'));
                        if (this.textContent === 'edit') {
                            openEditModal(eventId);
                        } else {
                            deleteEvent(eventId);
                        }
                    });
                });
            }

            // Formatear hora para visualización
            function formatTime(timeString) {
                if (!timeString) return '';
                const [hours, minutes] = timeString.split(':');
                return `${hours}:${minutes}`;
            }

            // Obtener nombre del tipo de evento
            function getTypeName(type) {
                const types = {
                    'class': 'Clase',
                    'rehearsal': 'Ensayo',
                    'important': 'Importante'
                };
                return types[type] || type;
            }

            // Abrir modal para nuevo evento
            addEventBtn.addEventListener('click', () => {
                modalTitle.textContent = 'Nuevo Evento';
                eventForm.reset();
                document.getElementById('eventDate').value = formatDateForInput(selectedDate);
                editingEventId = null;
                eventModal.style.display = 'flex';
            });

            // Formatear fecha para input type="date" (YYYY-MM-DD)
            function formatDateForInput(date) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }

            // Cerrar modal
            function closeEventModal() {
                eventModal.style.display = 'none';
                editingEventId = null;
            }

            closeModal.addEventListener('click', closeEventModal);
            cancelBtn.addEventListener('click', closeEventModal);

            // Manejar envío del formulario
            eventForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const eventData = {
                    titulo: document.getElementById('eventTitle').value,
                    tipo: document.getElementById('eventType').value,
                    fecha: document.getElementById('eventDate').value,
                    hora_inicio: document.getElementById('startTime').value,
                    hora_fin: document.getElementById('endTime').value,
                    lugar: document.getElementById('eventLocation').value,
                    descripcion: document.getElementById('eventDescription').value
                };
                
                try {
                    let response, result;
                    
                    if (editingEventId) {
                        // Actualizar evento existente
                        response = await fetch(`/evento/actualizar/${editingEventId}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(eventData)
                        });
                        
                        result = await response.json();
                        if (!response.ok) throw new Error(result.error || 'Error al actualizar el evento');
                        
                        showAlert('Evento actualizado correctamente', 'success');
                    } else {
                        // Crear nuevo evento
                        response = await fetch('/evento/crear', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(eventData)
                        });
                        
                        result = await response.json();
                        if (!response.ok) throw new Error(result.error || 'Error al crear el evento');
                        
                        showAlert('Evento creado correctamente', 'success');
                    }
                    
                    // Recargar la página para actualizar los eventos
                    window.location.reload();
                    
                } catch (error) {
                    console.error('Error:', error);
                    showAlert('Error al guardar el evento: ' + error.message, 'error');
                }
            });

            // Abrir modal para editar evento
            function openEditModal(eventId) {
                const event = events.find(e => e.id === eventId);
                if (!event) return;
                
                modalTitle.textContent = 'Editar Evento';
                document.getElementById('eventTitle').value = event.titulo;
                document.getElementById('eventType').value = event.tipo;
                document.getElementById('eventDate').value = event.fecha;
                document.getElementById('startTime').value = event.hora_inicio;
                document.getElementById('endTime').value = event.hora_fin;
                document.getElementById('eventLocation').value = event.lugar || '';
                document.getElementById('eventDescription').value = event.descripcion || '';
                
                editingEventId = eventId;
                eventModal.style.display = 'flex';
            }

            // Eliminar evento
            async function deleteEvent(eventId) {
                if (confirm('¿Estás seguro de que quieres eliminar este evento?')) {
                    try {
                        const response = await fetch(`/evento/eliminar/${eventId}`, {
                            method: 'DELETE'
                        });
                        
                        const result = await response.json();
                        if (!response.ok) throw new Error(result.error || 'Error al eliminar el evento');
                        
                        showAlert('Evento eliminado correctamente', 'success');
                        
                        // Recargar la página para actualizar los eventos
                        window.location.reload();
                    } catch (error) {
                        console.error('Error:', error);
                        showAlert('Error al eliminar el evento: ' + error.message, 'error');
                    }
                }
            }

            // Mostrar alerta
            function showAlert(message, type) {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert alert-${type}`;
                alertDiv.textContent = message;
                
                document.body.appendChild(alertDiv);
                
                setTimeout(() => {
                    alertDiv.remove();
                }, 3000);
            }

            // Sincronización con Google Calendar (simulada)
           syncBtn.addEventListener('click', function() {
                if (isSynced) {
                    isSynced = false;
                    syncBtn.classList.remove('synced');
                    syncBtn.innerHTML = '<span class="material-icons">sync</span> Sincronizar con Google';
                    showAlert('Se ha desconectado de Google Calendar', 'info');
                } else {
                    if (confirm('¿Quieres conectar tu agenda con Google Calendar?')) {
                        // Redirige al backend Flask que inicia el login con Google
                        window.location.href = '/sync';
                    }
                }
            });


            // Navegación entre meses
            document.querySelectorAll('.nav-btn').forEach(button => {
                button.addEventListener('click', function() {
                    if (this.textContent === 'chevron_left') {
                        currentDate.setMonth(currentDate.getMonth() - 1);
                    } else {
                        currentDate.setMonth(currentDate.getMonth() + 1);
                    }
                    renderCalendar();
                });
            });

            // Inicializar la aplicación
            initCalendar();
        });