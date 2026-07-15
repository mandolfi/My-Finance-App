import openpyxl
from database import SessionLocal, engine, Base
import models
from models import TransazioneRaw

def import_excel(path):
    Base.metadata.create_all(bind=engine)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Lista Spese"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))

    db = SessionLocal()
    count = 0
    for r in rows:
        t = TransazioneRaw(
            yyyy=r[0],
            mm=r[1],
            dd=r[2],
            prev=r[5],
            conto=r[6],
            causale_entrata=r[7],
            causale_uscita=r[8],
            descrizione=r[9],
            somma=r[10],
        )
        db.add(t)
        count += 1

    db.commit()
    print(f"Righe nel foglio Excel: {len(rows)}")
    print(f"Righe copiate PIATTAMENTE: {count}")
    db.close()

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "dati.xlsx"
    import_excel(path)