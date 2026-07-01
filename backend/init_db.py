from database import Base, engine
import models  # importa tutti i modelli così SQLAlchemy li conosce

def init():
    print("Creazione tabelle...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database creato correttamente!")
    print("Tabelle create:", Base.metadata.tables.keys())

if __name__ == "__main__":
    init()