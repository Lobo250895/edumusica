const body = document.querySelector("body"),
  sidebar = body.querySelector("nav"),
  toggle = body.querySelector(".toggle"),
  searchBtn = body.querySelector(".search-box"),
  modeSwitch = body.querySelector(".toggle-switch"),
  modeText = body.querySelector(".mode-text");

// Cambiar el estado de la barra lateral
toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
});

// Mostrar la barra lateral al hacer clic en el cuadro de búsqueda
searchBtn.addEventListener("click", () => {
  sidebar.classList.remove("close");
});

// Cambiar entre el modo oscuro y claro
modeSwitch.addEventListener("click", () => {
  body.classList.toggle("dark");

  if (body.classList.contains("dark")) {
    modeText.innerText = "Light mode";
    // Guardar la preferencia en localStorage
    localStorage.setItem("theme", "dark");
  } else {
    modeText.innerText = "Dark mode";
    // Guardar la preferencia en localStorage
    localStorage.setItem("theme", "light");
  }
});

// Recuperar la preferencia de tema al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    body.classList.add("dark");
    modeText.innerText = "Light mode";
  } else {
    body.classList.remove("dark");
    modeText.innerText = "Dark mode";
  }
});


// Cambiar imagen de perfil
function changeProfileImage() {
  const fileInput = document.getElementById('imageUpload');
  const profileImage = document.getElementById('profileImage');
  const file = fileInput.files[0];
  const reader = new FileReader();

  reader.onloadend = function () {
    profileImage.src = reader.result;
  }

  if (file) {
    reader.readAsDataURL(file);
  }
}

// Validación de formulario
(function () {
  'use strict'
  var forms = document.querySelectorAll('.needs-validation')
  Array.prototype.slice.call(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
      }, false)
    })
})()

function previewImage(event) {
  const reader = new FileReader();
  reader.onload = function() {
      const output = document.getElementById('profileImagePreview');
      output.src = reader.result;
  }
  reader.readAsDataURL(event.target.files[0]);
}


// Capturamos el evento de arrastrar el archivo
const uploadArea = document.querySelector('.upload-area');
const fileInput = document.querySelector('#fileUpload');
const form = document.querySelector('#uploadForm');

// Cuando el usuario arrastra un archivo sobre el área de carga
uploadArea.addEventListener('dragover', function (event) {
    event.preventDefault();
    uploadArea.classList.add('drag-over');
});

// Cuando el usuario deja caer un archivo
uploadArea.addEventListener('dragleave', function () {
    uploadArea.classList.remove('drag-over');
});

// Cuando el archivo se deja caer en el área
uploadArea.addEventListener('drop', function (event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
    }
});

// Validación del archivo (peso y tipo)
form.addEventListener('submit', function (event) {
    const file = fileInput.files[0];
    const maxSize = 5 * 1024 * 1024; // 5MB en bytes
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

    if (file) {
        if (file.size > maxSize) {
            alert('El archivo es demasiado grande. El peso máximo permitido es 5MB.');
            event.preventDefault();
        } else if (!allowedTypes.includes(file.type)) {
            alert('El archivo debe ser un documento Word o PDF.');
            event.preventDefault();
        }
    }
});

// Asignar la fecha automáticamente
document.getElementById('fecha_subida').value = new Date().toISOString().split('T')[0];

document.querySelectorAll('.icon').forEach(icon => {
  icon.addEventListener('click', () => {
    alert(`Has presionado el botón: ${icon.classList[1]}`);
  });
});



 // Añade funcionalidad a los botones de añadir y descargar
 document.querySelectorAll('.add-button').forEach(button => {
  button.addEventListener('click', () => {
      alert('Añadido a la playlist');
  });
});

document.querySelectorAll('.download-button').forEach(button => {
  button.addEventListener('click', () => {
      alert('Descarga iniciada');
  });
});


//paginacion//
const rowsPerPage = 4;
    let currentPage = 1;
    const table = document.getElementById('myTable');
    const rows = table.getElementsByTagName('tr');
    const pagination = document.getElementById('pagination');

    function paginate() {
      // Determinar las filas a mostrar
      for (let i = 1; i < rows.length; i++) {
        rows[i].style.display = 'none';  // Ocultar todas las filas
      }

      const startIndex = (currentPage - 1) * rowsPerPage + 1;
      const endIndex = startIndex + rowsPerPage - 1;

      // Mostrar solo las filas de la página actual
      for (let i = startIndex; i <= endIndex && i < rows.length; i++) {
        rows[i].style.display = '';
      }

      // Actualizar los botones de paginación
      document.getElementById('page-' + currentPage).classList.add('active');
      if (currentPage === 1) {
        document.getElementById('prev').classList.add('disabled');
      } else {
        document.getElementById('prev').classList.remove('disabled');
      }
      if (currentPage * rowsPerPage >= rows.length - 1) {
        document.getElementById('next').classList.add('disabled');
      } else {
        document.getElementById('next').classList.remove('disabled');
      }
    }

    // Manejar el clic en los botones de página
    pagination.addEventListener('click', (event) => {
      if (event.target.tagName === 'A') {
        const target = event.target;
        if (target.classList.contains('prev')) {
          currentPage--;
        } else if (target.classList.contains('next')) {
          currentPage++;
        } else if (target.parentElement.classList.contains('page-item')) {
          currentPage = parseInt(target.innerText);
        }
        paginate();
      }
    });

    // Inicializar la paginación
    paginate();