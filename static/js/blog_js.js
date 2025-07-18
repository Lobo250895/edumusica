document.addEventListener('DOMContentLoaded', function() {
  const toggleFormBtn = document.getElementById('toggle-form');
const emptyNewPostBtn = document.getElementById('empty-new-post');
const cancelFormBtn = document.getElementById('cancel-form');
const createPostForm = document.getElementById('create-post-form');
    
toggleFormBtn.addEventListener('click', function() {
  createPostForm.style.display = createPostForm.style.display === 'none' ? 'block' : 'none';
  window.scrollTo({ top: createPostForm.offsetTop - 20, behavior: 'smooth' });
});
    
    emptyNewPostBtn?.addEventListener('click', function() {
      createPostForm.style.display = 'block';
      window.scrollTo({ top: createPostForm.offsetTop - 20, behavior: 'smooth' });
    });
    
    cancelFormBtn.addEventListener('click', function() {
      createPostForm.style.display = 'none';
    });

    // Vista previa de imagen seleccionada
    const selectImageBtn = document.querySelector('.btn-select-image');
    const fileInput = document.getElementById('file');
    const imgArea = document.querySelector('.img-area');
    
    selectImageBtn.addEventListener('click', function() {
      fileInput.click();
    });
    
    fileInput.addEventListener('change', function() {
      const file = fileInput.files[0];
      if (file) {
        if (file.size > 2 * 1024 * 1024) {
          alert('La imagen debe ser menor a 2MB');
          return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
          imgArea.innerHTML = '';
          const img = document.createElement('img');
          img.src = e.target.result;
          imgArea.appendChild(img);
          imgArea.classList.add('has-image');
        };
        reader.readAsDataURL(file);
      }
    });

    // Drag and drop para imágenes
    imgArea.addEventListener('dragover', function(e) {
      e.preventDefault();
      imgArea.classList.add('dragover');
    });
    
    imgArea.addEventListener('dragleave', function() {
      imgArea.classList.remove('dragover');
    });
    
    imgArea.addEventListener('drop', function(e) {
      e.preventDefault();
      imgArea.classList.remove('dragover');
      
      const file = e.dataTransfer.files[0];
      if (file && file.type.match('image.*')) {
        fileInput.files = e.dataTransfer.files;
        const event = new Event('change');
        fileInput.dispatchEvent(event);
      }
    });

    // Actualizar noticias
    document.getElementById('refresh-news')?.addEventListener('click', function() {
      location.reload();
    });
});


document.addEventListener('DOMContentLoaded', function() {
  // Toggle para formularios de respuesta
    document.querySelectorAll('.btn-reply').forEach(button => {
      button.addEventListener('click', function() {
        const commentId = this.getAttribute('data-comment-id');
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        
        // Ocultar todos los demás formularios de respuesta
        document.querySelectorAll('.reply-form').forEach(form => {
          if (form !== replyForm) {
            form.style.display = 'none';
          }
        });
        
        // Mostrar/ocultar el formulario correspondiente
        replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
        
        // Desplazarse al formulario si se muestra
        if (replyForm.style.display === 'block') {
          replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });
    });

    // Cancelar respuesta
    document.querySelectorAll('.btn-cancel-reply').forEach(button => {
      button.addEventListener('click', function() {
        const replyForm = this.closest('.reply-form');
        replyForm.style.display = 'none';
      });
    });

    // Animación al hacer like
    document.querySelector('.btn-like')?.addEventListener('click', function() {
      this.classList.add('animate-like');
      setTimeout(() => {
        this.classList.remove('animate-like');
      }, 1000);
    });
});

