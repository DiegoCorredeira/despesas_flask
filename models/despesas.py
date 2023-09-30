from sql_alchemy import db
from sqlalchemy import Column, Numeric
from sqlalchemy.ext.declarative import declarative_base

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(200), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    valor = db.Column(Numeric(precision=10, scale=2), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    
