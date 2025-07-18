document.addEventListener('DOMContentLoaded', function() {
    // -------- Carrusel de Videos --------
    const carousel = document.querySelector('.video-carousel');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const videoCards = document.querySelectorAll('.video-card');
    const videoModal = document.getElementById('video-modal');
    const modalVideo = document.getElementById('modal-video');
    const closeModal = document.getElementById('close-modal');
    const videoTitle = document.getElementById('video-title');

    let currentIndex = 0;
    const cardWidth = videoCards[0]?.offsetWidth + 20;

    function getVisibleCardCount() {
        const container = document.querySelector('.video-carousel-container');
        return Math.floor(container.offsetWidth / cardWidth);
    }

    function updateCarousel() {
        carousel.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
    }

    nextBtn.addEventListener('click', () => {
        const visibleCount = getVisibleCardCount();
        if (currentIndex < videoCards.length - visibleCount) {
            currentIndex++;
            updateCarousel();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    videoCards.forEach(card => {
        card.addEventListener('click', () => {
            const videoUrl = card.getAttribute('data-video-url');
            const videoName = card.querySelector('h3').textContent;
            modalVideo.src = videoUrl;
            videoTitle.textContent = videoName;
            videoModal.classList.add('active');
            document.body.style.overflow = 'hidden';
            modalVideo.play().catch(e => console.log('Autoplay prevented:', e));
        });
    });

    closeModal.addEventListener('click', () => {
        videoModal.classList.remove('active');
        document.body.style.overflow = 'auto';
        modalVideo.pause();
        modalVideo.currentTime = 0;
    });

    videoModal.addEventListener('click', (e) => {
        if (e.target === videoModal || e.target.classList.contains('modal-overlay')) {
            videoModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            modalVideo.pause();
            modalVideo.currentTime = 0;
        }
    });

    // -------- Subida y preview de video con miniatura automática --------
    const videoInput = document.getElementById('video');
    const videoUploadArea = document.getElementById('video-upload-area');
    const uploadProgress = document.getElementById('upload-progress');
    const progressBar = uploadProgress.querySelector('.progress-bar');
    const progressText = uploadProgress.querySelector('.progress-text');
    const thumbnailPreview = document.getElementById('thumbnail-preview');

    // Click para seleccionar archivo
    videoUploadArea.addEventListener('click', () => videoInput.click());

    // Cambio en el input file
    videoInput.addEventListener('change', function() {
        handleFileUpload(this.files[0]);
    });

    // Drag and drop
    videoUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        videoUploadArea.classList.add('dragover');
    });

    videoUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        videoUploadArea.classList.remove('dragover');
    });

    videoUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        videoUploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // Función para manejar la subida del archivo
    function handleFileUpload(file) {
        if (!file) return;
        
        if (!file.type.match('video.*')) {
            alert('Por favor, sube solo archivos de video (MP4, WebM, Ogg)');
            return;
        }

        if (file.size > 100 * 1024 * 1024) {
            alert('El video no puede ser mayor a 100MB');
            return;
        }

        // Actualizar la interfaz
        videoUploadArea.innerHTML = `
            <i class='bx bx-check-circle'></i>
            <p>${file.name}</p>
            <span>${(file.size / (1024 * 1024)).toFixed(2)} MB</span>
        `;
        videoUploadArea.classList.add('file-selected');
        uploadProgress.style.display = 'flex';

        // Simular progreso de carga
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                // Aquí iría la lógica real de subida al servidor
            }
            progressBar.style.width = `${progress}%`;
            progressText.textContent = `${Math.round(progress)}%`;
        }, 300);

        // Generar miniatura del video
        generateVideoThumbnail(file);
    }

    // Función para generar miniatura del video
    function generateVideoThumbnail(file) {
        const videoElement = document.createElement('video');
        const dataURL = URL.createObjectURL(file);
        videoElement.src = dataURL;
        videoElement.muted = true;
        videoElement.playsInline = true;

        videoElement.addEventListener('loadeddata', () => {
            // Tomar un frame a la mitad del video para la miniatura
            videoElement.currentTime = Math.min(1, videoElement.duration / 2);
        });

        videoElement.addEventListener('seeked', () => {
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            const thumbnailDataURL = canvas.toDataURL('image/jpeg');
            
            // Mostrar preview de la miniatura (si existe el elemento)
            if (thumbnailPreview) {
                thumbnailPreview.innerHTML = `<img src="${thumbnailDataURL}" style="max-width:100%; border-radius:10px;">`;
            }

            // Crear input hidden para la miniatura
            let input = document.getElementById('miniatura_generada');
            if (!input) {
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'miniatura_generada';
                input.id = 'miniatura_generada';
                document.querySelector('.video-upload-form').appendChild(input);
            }
            input.value = thumbnailDataURL;
        });

        videoElement.load();
    }

    // Redimensionar el carrusel cuando cambie el tamaño de la ventana
    window.addEventListener('resize', () => {
        updateCarousel();
    });
});