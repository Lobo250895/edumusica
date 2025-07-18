import requests
from bs4 import BeautifulSoup
from datetime import datetime
from api_docentes.app import db
from api_docentes.app.models import Cobro

# Función para hacer scraping a paginas y obtener la fecha de cobro 
def obtener_fechas_cobro():
    url = 'https://www.ejemplo.gob.ar/cobros'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        fechas = soup.find_all('p', class_='fecha')
        
        for fecha in fechas:
            provincia = fecha.find_previous('h2').text
            fecha_pago = datetime.strptime(fecha.text, '%d/%m/%Y')
            cobro_existente = Cobro.query.filter_by(provincia=provincia).first()
            if cobro_existente:
                cobro_existente.fecha_pago = fecha_pago
            else:
                nuevo_cobro = Cobro(provincia=provincia, fecha_pago=fecha_pago, fuente=url)
                db.session.add(nuevo_cobro)
                
            db.session.commit()
    else:
        print("Error al obtener datos")
