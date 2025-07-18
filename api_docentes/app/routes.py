from flask import Blueprint, request, jsonify, render_template, current_app
from . import db
from .models import Cobro
from api_docentes.scraper.scraper import obtener_fechas_cobro  # ✅
from flask_cors import cross_origin

# Blueprint para API
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

@api_blueprint.route('/pago_haberes', methods=['POST'])
@cross_origin()
def api_pago_haberes():
    try:
        # Obtener provincia del request
        if request.is_json:
            data = request.get_json()
            provincia = data.get('provincia', '').strip()
        else:
            provincia = request.form.get('provincia', '').strip()
        
        if not provincia:
            return jsonify({'error': 'Provincia es requerida', 'status': 400}), 400
        
        # Buscar en la base de datos
        resultados = Cobro.query.filter(Cobro.provincia.ilike(f'%{provincia}%')).all()
        
        if not resultados:
            obtener_fechas_cobro()  # Actualizar datos
            resultados = Cobro.query.filter(Cobro.provincia.ilike(f'%{provincia}%')).all()
            if not resultados:
                return jsonify({'message': 'No se encontraron resultados', 'status': 404}), 404
        
        # Formatear respuesta
        return jsonify({
            'status': 200,
            'results': [{
                'id': r.id,
                'provincia': r.provincia,
                'fecha_pago': r.fecha_pago.strftime('%Y-%m-%d'),
                'fuente': r.fuente
            } for r in resultados]
        })
    
    except Exception as e:
        current_app.logger.error(f"Error en API: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'status': 500}), 500

# Blueprint para Web
web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/', methods=['GET', 'POST'])
def pago_haberes_web():
    if request.method == 'POST':
        provincia = request.form.get('provincia', '').strip()
        if provincia:
            # Usar current_app para acceder al contexto
            with current_app.test_client() as client:
                response = client.post(
                    '/api/pago_haberes',
                    json={'provincia': provincia},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    return render_template('pago_haberes.html', 
                                        resultados=response.json['results'])
                return render_template('pago_haberes.html', 
                                    error="No se encontraron resultados")
    
    return render_template('pago_haberes.html')