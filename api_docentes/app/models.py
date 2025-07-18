from . import db

class Cobro(db.Model):
    __tablename__ = 'cobro'
    
    id = db.Column(db.Integer, primary_key=True)
    provincia = db.Column(db.String(100), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    fuente = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Cobro {self.provincia} - {self.fecha_pago}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'provincia': self.provincia,
            'fecha_pago': self.fecha_pago.strftime('%Y-%m-%d'),
            'fuente': self.fuente
        }