from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Requisicao(Base):
    __tablename__ = 'requisicoes'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    payload = Column(String) 
    formato = Column(String)
    tempo_limite = Column(Integer)
    status_code = Column(Integer)
    response = Column(String)
    resultado = Column(String)
    tempo = Column(Float)
    id_resumo = Column(Integer, ForeignKey('resumos.id'))

class Resumo(Base):
    __tablename__ = 'resumos'
    
    id = Column(Integer, primary_key=True)
    data_inicio = Column(DateTime)
    data_termino = Column(DateTime) 
    total = Column(Integer)
    sucessos = Column(Integer)
    falhas = Column(Integer)
    tempo_medio = Column(Float)
    tempo_maximo = Column(Float)
