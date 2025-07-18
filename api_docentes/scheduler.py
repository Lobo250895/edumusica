from apscheduler.schedulers.background import BackgroundScheduler
from api_docentes.scraper.scraper import obtener_fechas_cobro  


def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(obtener_fechas_cobro, 'interval', minutes=60)  # Ejecutar cada 60 minutos
    scheduler.start()
