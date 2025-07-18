from app import create_app
from scheduler import iniciar_scheduler

app = create_app()
if __name__ == '__main__':
    iniciar_scheduler()  
    app.run(host='0.0.0.0', port=5001, debug=True)