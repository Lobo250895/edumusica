document.addEventListener('DOMContentLoaded', function () {
    // Manejo del modal de detalles
    document.querySelectorAll('.view-details').forEach(btn => {
        btn.addEventListener('click', function () {
            const trabajoId = this.getAttribute('data-id');
            const card = this.closest('.luthier-card');
            const title = card.querySelector('.luthier-title').textContent;
            const desc = card.querySelector('.full-desc').textContent; // descripción completa
            const imageSrc = card.querySelector('.luthier-img').src;
            const author = card.querySelector('.luthier-author span').textContent;
            const date = card.querySelector('.luthier-meta span:last-child').textContent;

            let videoUrl = null;
            const videoBadge = card.querySelector('.media-badge i.bx-video');
            if (videoBadge) {
                videoUrl = "https://www.youtube.com/embed/ejemplo";
            }

            let pdfUrl = null;
            const pdfBtn = card.querySelector('.luthier-actions a[download]');
            if (pdfBtn) {
                pdfUrl = pdfBtn.href;
            }

            
            document.getElementById('modal-desc').textContent = desc;


            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-desc').textContent = desc;
            document.getElementById('modal-image').src = imageSrc;
            document.getElementById('modal-author').textContent = author;
            document.getElementById('modal-date').textContent = date;

            const videoContainer = document.getElementById('modal-video-container');
            if (videoUrl) {
                videoContainer.style.display = 'block';
                document.getElementById('modal-video').src = videoUrl;
            } else {
                videoContainer.style.display = 'none';
            }

            const pdfLink = document.getElementById('modal-pdf-link');
            if (pdfUrl) {
                pdfLink.style.display = 'inline-block';
                pdfLink.href = pdfUrl;
            } else {
                pdfLink.style.display = 'none';
            }

            document.getElementById('luthier-modal').classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    document.getElementById('close-modal').addEventListener('click', function () {
        document.getElementById('luthier-modal').classList.remove('active');
        document.body.style.overflow = 'auto';
        const iframe = document.getElementById('modal-video');
        if (iframe) {
            iframe.src = '';
        }
    });

    document.getElementById('luthier-modal').addEventListener('click', function (e) {
        if (e.target === this || e.target.classList.contains('modal-overlay')) {
            this.classList.remove('active');
            document.body.style.overflow = 'auto';
            const iframe = document.getElementById('modal-video');
            if (iframe) {
                iframe.src = '';
            }
        }
    });

    const openFormBtn = document.getElementById('open-form-btn');
    const formContainer = document.getElementById('upload-form-container');
    const cancelFormBtn = document.getElementById('cancel-form');

    if (openFormBtn && formContainer) {
        openFormBtn.addEventListener('click', function () {
            formContainer.style.display = 'block';
            window.scrollTo({
                top: formContainer.offsetTop - 20,
                behavior: 'smooth'
            });
        });

        cancelFormBtn.addEventListener('click', function () {
            formContainer.style.display = 'none';
            document.getElementById('luthier-form').reset();
            document.getElementById('image-preview').style.display = 'none';
        });
    }

    const imageUploadArea = document.getElementById('image-upload-area');
    const imageInput = document.getElementById('imagen');
    const imagePreview = document.getElementById('image-preview');
    const previewImage = document.getElementById('preview-image');

    imageUploadArea.addEventListener('click', function () {
        imageInput.click();
    });

    imageInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                imagePreview.style.display = 'block';
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    imageUploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.style.borderColor = '#4a148c';
        this.style.backgroundColor = 'rgba(74, 20, 140, 0.1)';
    });

    imageUploadArea.addEventListener('dragleave', function () {
        this.style.borderColor = '';
        this.style.backgroundColor = '';
    });

    imageUploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.style.borderColor = '';
        this.style.backgroundColor = '';

        if (e.dataTransfer.files.length) {
            imageInput.files = e.dataTransfer.files;
            const event = new Event('change');
            imageInput.dispatchEvent(event);
        }
    });

    const pdfUploadArea = document.getElementById('pdf-upload-area');
    const pdfInput = document.getElementById('pdf');

    pdfUploadArea.addEventListener('click', function () {
        pdfInput.click();
    });

    pdfUploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.style.borderColor = '#4a148c';
        this.style.backgroundColor = 'rgba(74, 20, 140, 0.1)';
    });

    pdfUploadArea.addEventListener('dragleave', function () {
        this.style.borderColor = '';
        this.style.backgroundColor = '';
    });

    pdfUploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.style.borderColor = '';
        this.style.backgroundColor = '';

        if (e.dataTransfer.files.length) {
            pdfInput.files = e.dataTransfer.files;
            this.innerHTML = `
                <i class='bx bx-check-circle'></i>
                <p>${e.dataTransfer.files[0].name}</p>
                <span>${(e.dataTransfer.files[0].size / (1024 * 1024)).toFixed(2)} MB</span>
            `;
        }
    });

    document.getElementById('luthier-form').addEventListener('submit', function (e) {
        const imageFile = document.getElementById('imagen').files[0];
        const pdfFile = document.getElementById('pdf').files[0];

        if (!imageFile) {
            alert('Por favor selecciona una imagen principal');
            e.preventDefault();
            return;
        }

        if (imageFile.size > 5 * 1024 * 1024) {
            alert('La imagen no puede ser mayor a 5MB');
            e.preventDefault();
            return;
        }

        const validImageTypes = ['image/jpeg', 'image/png'];
        if (!validImageTypes.includes(imageFile.type)) {
            alert('Solo se permiten imágenes JPG o PNG');
            e.preventDefault();
            return;
        }

        if (pdfFile) {
            if (pdfFile.size > 10 * 1024 * 1024) {
                alert('El PDF no puede ser mayor a 10MB');
                e.preventDefault();
                return;
            }

            if (pdfFile.type !== 'application/pdf') {
                alert('El archivo debe ser un PDF válido');
                e.preventDefault();
                return;
            }
        }

        const videoUrl = document.getElementById('video_url').value;
        if (videoUrl && !isValidUrl(videoUrl)) {
            alert('Por favor ingresa una URL de video válida');
            e.preventDefault();
            return;
        }
    });

    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

});
