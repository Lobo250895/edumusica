document.querySelectorAll('.vinyl-container').forEach(vinyl => {
            vinyl.addEventListener('mouseenter', function() {
                this.querySelector('.vinyl-disc').style.animationPlayState = 'running';
            });
            
            vinyl.addEventListener('mouseleave', function() {
                this.querySelector('.vinyl-disc').style.animationPlayState = 'paused';
            });
});