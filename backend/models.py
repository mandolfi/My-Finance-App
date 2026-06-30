from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    nome_conto = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    # categoria valida: Liquidità / Investimento / Carta di credito / Debito / Credito verso terzi

    transazioni = relationship("Transazione", back_populates="account")


class Entrata(Base):
    __tablename__ = "entrate"

    id = Column(Integer, primary_key=True)
    nome_entrata = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    # categoria valida: Passive / Attive / Extra

    transazioni = relationship("Transazione", back_populates="entrata")


class Uscita(Base):
    __tablename__ = "uscite"

    id = Column(Integer, primary_key=True)
    nome_uscita = Column(String, unique=True, nullable=False)
    categoria = Column(String, nullable=False)
    # categoria valida: Necessaria / Divertimenti / Investimenti

    transazioni = relationship("Transazione", back_populates="uscita")


class Transazione(Base):
    __tablename__ = "transazioni"

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    direzione = Column(String, nullable=False)  # "Entrata" oppure "Uscita"
    descrizione = Column(String)
    importo = Column(Numeric(12, 2), nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    entrata_id = Column(Integer, ForeignKey("entrate.id"), nullable=True)
    uscita_id = Column(Integer, ForeignKey("uscite.id"), nullable=True)

    account = relationship("Account", back_populates="transazioni")
    entrata = relationship("Entrata", back_populates="transazioni")
    uscita = relationship("Uscita", back_populates="transazioni")

    __table_args__ = (
        CheckConstraint(
            "(direzione = 'Entrata' AND entrata_id IS NOT NULL AND uscita_id IS NULL) OR "
            "(direzione = 'Uscita' AND uscita_id IS NOT NULL AND entrata_id IS NULL)",
            name="check_direzione_coerente"
        ),
    )