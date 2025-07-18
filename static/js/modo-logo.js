const IMG_BASE_PATH = window.IMG_BASE_PATH || '/static/img/';
const LOGOS = {
  dark: window.LOGO_DARK || IMG_BASE_PATH + 'Logo_tesis-pequeño_blanco.png',
  light: window.LOGO_LIGHT || IMG_BASE_PATH + 'Logo_tesis-pequeño.png',
  default: window.LOGO_DEFAULT || IMG_BASE_PATH + 'logo-default.png'
};

const DOM = {
  get logo() {
    const logo = document.getElementById('logo');
    if (!logo) console.error('Elemento con ID "logo" no encontrado');
    return logo;
  },
  get toggleSwitch() {
    const toggle = document.querySelector('.toggle-switch');
    if (!toggle) console.warn('Interruptor de modo no encontrado');
    return toggle;
  },
  body: document.body
};

// Función optimizada para cambiar el logo
async function cambiarLogoSegunModo() {
  if (!DOM.logo) return;

  const isDarkMode = DOM.body.classList.contains('dark'); // Cambiado a 'dark'
  const newSrc = isDarkMode ? LOGOS.dark : LOGOS.light;

  try {
    // Intenta cargar la imagen primero
    await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = () => reject(new Error(`No se pudo cargar la imagen: ${newSrc}`));
      img.src = newSrc;
    });
    
    DOM.logo.src = newSrc;
    DOM.logo.dataset.mode = isDarkMode ? 'dark' : 'light';
  } catch (error) {
    console.error('Error al cambiar el logo:', error);
    DOM.logo.src = LOGOS.default;
  }
}

class ColorModeController {
  constructor() {
    this.init();
    this.setupEventListeners();
  }

  init() {
    const savedMode = localStorage.getItem('darkMode');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialMode = savedMode !== null ? JSON.parse(savedMode) : systemPrefersDark;
    this.setMode(initialMode);
  }

  setMode(isDark) {
    // Aseguramos que solo la clase 'dark' se use
    DOM.body.classList.toggle('dark', isDark);
    DOM.body.classList.remove('dark-mode', 'light-mode'); // Limpia clases antiguas
    
    localStorage.setItem('darkMode', isDark);
    
    // Cambia el logo y maneja errores
    cambiarLogoSegunModo().catch(error => {
      console.error('Error al cambiar el modo:', error);
    });
  }

  toggleMode() {
    this.setMode(!DOM.body.classList.contains('dark'));
  }

  setupEventListeners() {
    if (DOM.toggleSwitch) {
      DOM.toggleSwitch.addEventListener('click', () => this.toggleMode());
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem('darkMode') === null) {
        this.setMode(e.matches);
      }
    });
  }
}

// Inicialización mejorada
document.addEventListener('DOMContentLoaded', () => {
  try {
    new ColorModeController();
    
    // Verificación inicial del logo
    const logo = document.getElementById('logo');
    if (logo && !logo.src) {
      const initialMode = document.body.classList.contains('dark');
      logo.src = initialMode ? LOGOS.dark : LOGOS.light;
    }
  } catch (error) {
    console.error('Error al inicializar el controlador de modo:', error);
  }
});