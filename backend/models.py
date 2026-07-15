from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    nome_conto = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    transazioni = relationship("Transazione", back_populates="account")


class Entrata(Base):
    __tablename__ = "entrate"
    id = Column(Integer, primary_key=True)
    nome_entrata = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    transazioni = relationship("Transazione", back_populates="entrata")


class Uscita(Base):
    __tablename__ = "uscite"
    id = Column(Integer, primary_key=True)
    nome_uscita = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    transazioni = relationship("Transazione", back_populates="uscita")


class Transazione(Base):
    __tablename__ = "transazioni"
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    direzione = Column(String, nullable=False)
    descrizione = Column(String)
    importo = Column(Numeric(12, 2), nullable=False)
    prev = Column(String, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    entrata_id = Column(Integer, ForeignKey("entrate.id"), nullable=True)
    uscita_id = Column(Integer, ForeignKey("uscite.id"), nullable=True)
    account = relationship("Account", back_populates="transazioni")
    entrata = relationship("Entrata", back_populates="transazioni")
    uscita = relationship("Uscita", back_populates="transazioni")


class TransazioneRaw(Base):
    __tablename__ = "transazioni_raw"
    id = Column(Integer, primary_key=True)
    yyyy = Column(Integer)
    mm = Column(Integer)
    dd = Column(Integer)
    prev = Column(String)
    conto = Column(String)
    causale_entrata = Column(String)
    causale_uscita = Column(String)
    descrizione = Column(String)
    somma = Column(Numeric(14, 2))