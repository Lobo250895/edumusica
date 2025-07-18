document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    const schoolForm = document.getElementById('schoolForm');
    const reportForm = document.getElementById('reportForm');
    const schoolModal = document.getElementById('schoolModal');
    const reportModal = document.getElementById('reportModal');
    const viewReportModal = document.getElementById('viewReportModal');
    const addSchoolBtn = document.getElementById('addSchoolBtn');
    const addReportBtn = document.getElementById('addReportBtn');
    const closeSchoolModal = document.getElementById('closeSchoolModal');
    const closeReportModal = document.getElementById('closeReportModal');
    const closeViewReportModal = document.getElementById('closeViewReportModal');
    const cancelSchoolBtn = document.getElementById('cancelSchoolBtn');
    const cancelReportBtn = document.getElementById('cancelReportBtn');
    const closeViewReportBtn = document.getElementById('closeViewReportBtn');
    
    // Event Listeners para abrir modales
    addSchoolBtn.addEventListener('click', () => openSchoolModal());
    addReportBtn.addEventListener('click', () => openReportModal());
    
    // Event Listeners para cerrar modales
    closeSchoolModal.addEventListener('click', () => closeModal(schoolModal));
    closeReportModal.addEventListener('click', () => closeModal(reportModal));
    closeViewReportModal.addEventListener('click', () => closeModal(viewReportModal));
    cancelSchoolBtn.addEventListener('click', () => closeModal(schoolModal));
    cancelReportBtn.addEventListener('click', () => closeModal(reportModal));
    closeViewReportBtn.addEventListener('click', () => closeModal(viewReportModal));
    
    // Event Listeners para formularios
    schoolForm.addEventListener('submit', handleSchoolSubmit);
    reportForm.addEventListener('submit', handleReportSubmit);
    
    // Delegación de eventos para botones de acción en las tablas
    document.getElementById('schoolsTableBody').addEventListener('click', function(e) {
        const row = e.target.closest('tr');
        if (!row) return;
        
        const id = row.dataset.id;
        
        if (e.target.classList.contains('edit-school')) {
            editSchool(id);
        } else if (e.target.classList.contains('delete-school')) {
            deleteSchool(id);
        }
    });
    
    document.getElementById('reportsTableBody').addEventListener('click', function(e) {
        const row = e.target.closest('tr');
        if (!row) return;
        
        const id = row.dataset.id;
        
        if (e.target.classList.contains('view-report')) {
            viewReport(id);
        } else if (e.target.classList.contains('edit-report')) {  // Asegúrate de que los botones tengan esta clase
            openReportModal(id);
        } else if (e.target.classList.contains('delete-report')) {
            deleteReport(id);
        }
    });

    // Funciones para manejar los formularios
    async function handleSchoolSubmit(e) {
        e.preventDefault();
        
        const formData = {
            nombre_escuela: document.getElementById('schoolName').value,
            direccion: document.getElementById('schoolAddress').value,
            telefono: document.getElementById('schoolPhone').value,
            fecha_inicio: document.getElementById('startDate').value,
            fecha_cese: document.getElementById('endDate').value || null
        };
        
        const schoolId = document.getElementById('schoolId').value;
        const url = schoolId ? `/escuela/actualizar/${schoolId}` : '/escuela/crear';
        const method = schoolId ? 'PUT' : 'POST';
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload(); // Recargar la página para ver los cambios
            } else {
                alert(data.error || 'Error al guardar la escuela');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al guardar la escuela');
        }
    }
    
    async function handleReportSubmit(e) {
        e.preventDefault();
        
        const formData = {
            tipo: document.getElementById('reportType').value,
            descripcion: document.getElementById('reportDescription').value,
            fecha_reporte: document.getElementById('reportDate').value,
            id_escuela: document.getElementById('reportSchool').value,
            nombre_alumno: document.getElementById('studentName').value,
            apellido_alumno: document.getElementById('studentLastName').value
        };
        
        const reportId = document.getElementById('reportId').value;
        const url = reportId ? `/reporte/actualizar/${reportId}` : '/reporte/crear';
        const method = reportId ? 'PUT' : 'POST';
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload(); // Recargar la página para ver los cambios
            } else {
                alert(data.message || data.error || 'Error al guardar el reporte');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al guardar el reporte');
        }
    }
    
    // Funciones para abrir modales
    async function openSchoolModal(id = null) {
        const modalTitle = document.getElementById('schoolModalTitle');
        const schoolIdInput = document.getElementById('schoolId');
        
        if (id) {
            modalTitle.textContent = 'Editar Escuela';
            schoolIdInput.value = id;
            await fillSchoolForm(id);
        } else {
            modalTitle.textContent = 'Agregar Escuela';
            schoolIdInput.value = '';
            schoolForm.reset();
            // Establecer fecha actual como fecha de inicio por defecto
            document.getElementById('startDate').valueAsDate = new Date();
        }
        
        schoolModal.style.display = 'block';
    }
    
    async function openReportModal(id = null) {
        const modalTitle = document.getElementById('reportModalTitle');
        const reportIdInput = document.getElementById('reportId');
        
        if (id) {
            modalTitle.textContent = 'Editar Reporte';
            reportIdInput.value = id;
            await fillReportForm(id);
        } else {
            modalTitle.textContent = 'Nuevo Reporte';
            reportIdInput.value = '';
            reportForm.reset();
            // Establecer fecha actual por defecto
            document.getElementById('reportDate').valueAsDate = new Date();
        }
        
        reportModal.style.display = 'block';
    }
    
    // Funciones para cerrar modales
    function closeModal(modal) {
        modal.style.display = 'none';
    }
    
    // Funciones para llenar formularios
    async function fillSchoolForm(id) {
        try {
            const response = await fetch(`/escuela/${id}`);
            if (!response.ok) throw new Error('Escuela no encontrada');
            
            const escuela = await response.json();
            
            document.getElementById('schoolName').value = escuela.nombre_escuela;
            document.getElementById('schoolAddress').value = escuela.direccion;
            document.getElementById('schoolPhone').value = escuela.telefono || '';
            document.getElementById('startDate').value = escuela.fecha_inicio;
            document.getElementById('endDate').value = escuela.fecha_cese || '';
        } catch (error) {
            console.error('Error al obtener los datos de la escuela:', error);
            alert('Error al cargar los datos de la escuela');
        }
    }
    
    async function fillReportForm(id) {
        try {
            const response = await fetch(`/reporte/${id}`);
            if (!response.ok) throw new Error('Reporte no encontrado');
            
            const reporte = await response.json();
            
            document.getElementById('reportSchool').value = reporte.id_escuela;
            document.getElementById('studentName').value = reporte.nombre_alumno;
            document.getElementById('studentLastName').value = reporte.apellido_alumno;
            document.getElementById('reportType').value = reporte.tipo;
            document.getElementById('reportDate').value = reporte.fecha_reporte;
            document.getElementById('reportDescription').value = reporte.descripcion;
        } catch (error) {
            console.error('Error al obtener los datos del reporte:', error);
            alert('Error al cargar los datos del reporte');
        }
    }
    
    // Funciones para ver detalles
    async function viewReport(id) {
        try {
            const response = await fetch(`/reporte/${id}`);
            if (!response.ok) throw new Error('Reporte no encontrado');
            
            const reporte = await response.json();
            
            // Formatear la fecha
            const fecha = new Date(reporte.fecha_reporte);
            const fechaFormateada = fecha.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
            
            // Crear el HTML con los detalles del reporte
            const reportDetails = document.getElementById('reportDetails');
            reportDetails.innerHTML = `
                <div class="report-detail">
                    <h3>${reporte.nombre_alumno} ${reporte.apellido_alumno}</h3>
                    <p><strong>Escuela:</strong> ${reporte.nombre_escuela || 'No especificada'}</p>
                    <p><strong>Fecha:</strong> ${fechaFormateada}</p>
                    <p><strong>Tipo:</strong> ${formatReportType(reporte.tipo)}</p>
                    <div class="description-box">
                        <p><strong>Descripción:</strong></p>
                        <p>${reporte.descripcion}</p>
                    </div>
                </div>
            `;
            
            // Mostrar el modal
            document.getElementById('viewReportTitle').textContent = `Reporte de ${reporte.nombre_alumno}`;
            viewReportModal.style.display = 'block';
        } catch (error) {
            console.error('Error al obtener los datos del reporte:', error);
            alert('Error al cargar los detalles del reporte');
        }
    }
    
    function formatReportType(type) {
        const types = {
            'conducta': 'Problema de Conducta',
            'academico': 'Problema Académico',
            'asistencia': 'Problema de Asistencia',
            'felicitacion': 'Felicitación',
            'otro': 'Otro'
        };
        return types[type] || type;
    }
    
    // Funciones para eliminar
    async function deleteSchool(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar esta escuela? También se eliminarán todos sus reportes asociados.')) {
            return;
        }
        
        try {
            const response = await fetch(`/escuela/eliminar/${id}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload(); // Recargar la página para ver los cambios
            } else {
                alert(data.error || 'Error al eliminar la escuela');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar la escuela');
        }
    }
    
    async function deleteReport(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este reporte?')) {
            return;
        }
        
        try {
            const response = await fetch(`/reporte/eliminar/${id}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload(); // Recargar la página para ver los cambios
            } else {
                alert(data.error || 'Error al eliminar el reporte');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar el reporte');
        }
    }
    
    // Función para editar escuela (ya está implementada en openSchoolModal)
    async function editSchool(id) {
        await openSchoolModal(id);
    }
    
    // Inicialización: Cargar datos si es necesario
    // (En este caso, los datos ya vienen renderizados desde el servidor)
});