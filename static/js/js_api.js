document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.form-consulta');
  if (!form) return;  

  const btn = form.querySelector('button');

  form.addEventListener('submit', () => {
    btn.textContent = 'Buscando...';
    btn.disabled = true;
    btn.style.opacity = '0.6';
  });
});
