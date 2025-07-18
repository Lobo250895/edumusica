document.addEventListener('DOMContentLoaded', function() {
    // Sidebar navigation active state
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            navLinks.forEach(item => item.parentElement.classList.remove('active'));
            this.parentElement.classList.add('active');
            
            
        });
    });
    
    // Toggle sidebar on mobile (you can add a button for this)
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('collapsed');
    }
    
    // Search functionality
    const searchInput = document.querySelector('.search-bar input');
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            // Implement search functionality
            console.log('Searching for:', this.value);
        }
    });
    
    // Notifications dropdown (would be implemented with more detail)
    const notifications = document.querySelector('.notifications');
    notifications.addEventListener('click', function() {
        console.log('Show notifications dropdown');
    });
    
    // Messages dropdown (would be implemented with more detail)
    const messages = document.querySelector('.messages');
    messages.addEventListener('click', function() {
        console.log('Show messages dropdown');
    });
    
    // Logout button
    const logoutBtn = document.querySelector('.logout-btn');
    logoutBtn.addEventListener('click', function(e) {
        console.log('Cerrando Sesion...');
         window.location.href = 'login.html';
    });
    
    // Add animations to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-in');
    });
}); 


document.addEventListener('DOMContentLoaded', function() {
    // Enrollment Chart
    const enrollmentsCtx = document.getElementById('enrollmentsChart').getContext('2d');
    const enrollmentsChart = new Chart(enrollmentsCtx, {
        type: 'line',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            datasets: [{
                label: 'Inscripciones',
                data: [45, 60, 75, 82, 93, 105, 120, 95, 110, 125, 140, 160],
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 5,
                pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointHoverBorderColor: '#fff',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            return ' ' + context.parsed.y + ' inscripciones';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        maxTicksLimit: 5
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    // Popular Courses Chart
    const popularCoursesCtx = document.getElementById('popularCoursesChart').getContext('2d');
    const popularCoursesChart = new Chart(popularCoursesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Guitarra', 'Piano', 'Violín', 'Canto', 'Batería', 'Otros'],
            datasets: [{
                data: [35, 25, 15, 10, 8, 7],
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b',
                    '#858796'
                ],
                hoverBackgroundColor: [
                    '#2e59d9',
                    '#17a673',
                    '#2c9faf',
                    '#dda20a',
                    '#be2617',
                    '#6c757d'
                ],
                hoverBorderColor: 'rgba(234, 236, 244, 1)',
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
});