import openpyxl
from database import SessionLocal, engine, Base
import models
from models import TransazioneRaw, Account, Entrata, Uscita, Transazione
from datetime import date
import calendar
from collections import Counter, defaultdict


CATEGORIA_CONTI = {
    "liquidità": [
        "marco cc ger", "marco cc ita", "marco cc ingdiba", "marco cc risp",
        "marco cc risp ingdiba", "marco libretto", "marco portafoglio",
        "linda cc ger", "linda cc ingdiba", "linda cc risp",
        "linda cc risp ingdiba", "linda portafoglio",
        "conto comune", "cassa anna", "tagesgeld",
    ],
    "investimento": [
        "marco investimento", "linda investimento", "linda invest.", "quirion",
    ],
    "carta di credito": [
        "marco carta credito", "linda carta credito", "american express",
    ],
    "debito": [
        "marco debito", "mutuo banca", "mutuo papa", "conto puntino", "conto virgola",
    ],
    "credito verso terzi": [
        "marco crediti a terzi", "marco credito pf",
        "linda credito is", "caparra",
    ],
}


def get_categoria_conto(nome_norm):
    for cat, nomi in CATEGORIA_CONTI.items():
        if nome_norm in nomi:
            return cat
    if nome_norm.startswith("app") or nome_norm == "haus":
        return "immobili"
    return "liquidità"


def prev_ok(p):
    if p is None:
        return True
    return str(p).strip().lower() == "chiusure"


# ── IMPORT RAW: copia 1:1 dell'Excel, nessuna logica ────────────────────────

def import_raw(path):
    Base.metadata.create_all(bind=engine)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Lista Spese"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))

    db = SessionLocal()
    db.query(TransazioneRaw).delete()
    db.commit()

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
    print(f"Righe copiate PIATTAMENTE in transazioni_raw: {count}")
    db.close()


# ── COSTRUISCI TABELLE PULITE: legge da transazioni_raw ─────────────────────

def costruisci_tabelle_pulite():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Ripulisci solo le tabelle pulite (non transazioni_raw)
    db.query(Transazione).delete()
    db.query(Account).delete()
    db.query(Entrata).delete()
    db.query(Uscita).delete()
    db.commit()

    raw = db.query(TransazioneRaw).all()

    # ── 1. Nome ufficiale per ogni conto normalizzato ──────────────────────
    varianti_conto = defaultdict(Counter)
    for r in raw:
        if not r.conto:
            continue
        norm = r.conto.strip().lower()
        varianti_conto[norm][r.conto.strip()] += 1

    nome_ufficiale = {
        norm: varianti.most_common(1)[0][0]
        for norm, varianti in varianti_conto.items()
    }

    # ── 2. Crea Accounts ────────────────────────────────────────────────────
    account_map = {}
    for norm, nome in nome_ufficiale.items():
        acc = Account(nome_conto=nome, categoria=get_categoria_conto(norm))
        db.add(acc)
        account_map[norm] = acc
    db.flush()
    print(f"✅ {len(account_map)} conti creati")

    # ── 3. Nome ufficiale per causali entrata/uscita ────────────────────────
    varianti_entrata = defaultdict(Counter)
    varianti_uscita = defaultdict(Counter)
    for r in raw:
        if r.causale_entrata:
            norm = r.causale_entrata.strip().lower()
            varianti_entrata[norm][r.causale_entrata.strip()] += 1
        if r.causale_uscita:
            norm = r.causale_uscita.strip().lower()
            varianti_uscita[norm][r.causale_uscita.strip()] += 1

    entrata_map = {}
    for norm, varianti in varianti_entrata.items():
        nome = varianti.most_common(1)[0][0]
        e = Entrata(nome_entrata=nome, categoria="Attive")
        db.add(e)
        entrata_map[norm] = e
    entrata_default = Entrata(nome_entrata="Trasferimento/Apertura", categoria="Extra")
    db.add(entrata_default)
    db.flush()
    entrata_map["__default__"] = entrata_default
    print(f"✅ {len(entrata_map)} causali entrata create")

    uscita_map = {}
    for norm, varianti in varianti_uscita.items():
        nome = varianti.most_common(1)[0][0]
        u = Uscita(nome_uscita=nome, categoria="Necessaria")
        db.add(u)
        uscita_map[norm] = u
    uscita_default = Uscita(nome_uscita="Trasferimento/Apertura", categoria="Necessaria")
    db.add(uscita_default)
    db.flush()
    uscita_map["__default__"] = uscita_default
    print(f"✅ {len(uscita_map)} causali uscita create")

    # ── 4. Crea Transazioni pulite (TUTTE, nessuna esclusa per Prev) ───────
    importate = 0
    skippate = 0

    for r in raw:
        if not r.conto or r.somma is None:
            skippate += 1
            continue

        conto_norm = r.conto.strip().lower()
        if conto_norm not in account_map:
            skippate += 1
            continue

        try:
            yyyy, mm, dd = int(r.yyyy), int(r.mm), int(r.dd)
            ultimo = calendar.monthrange(yyyy, mm)[1]
            dd = min(max(dd, 1), ultimo)
            data = date(yyyy, mm, dd)
        except:
            skippate += 1
            continue

        importo = float(r.somma)
        causale_in_norm = r.causale_entrata.strip().lower() if r.causale_entrata else None
        causale_out_norm = r.causale_uscita.strip().lower() if r.causale_uscita else None

        # Direzione = etichetta per categorizzazione, basata sulla causale
        # (usata per raggruppare/analizzare, NON per calcolare il saldo)
        if causale_in_norm and causale_in_norm in entrata_map:
            direzione = "Entrata"
            entrata_id = entrata_map[causale_in_norm].id
            uscita_id = None
        elif causale_out_norm and causale_out_norm in uscita_map:
            direzione = "Uscita"
            entrata_id = None
            uscita_id = uscita_map[causale_out_norm].id
        elif importo >= 0:
            direzione = "Entrata"
            entrata_id = entrata_map["__default__"].id
            uscita_id = None
        else:
            direzione = "Uscita"
            entrata_id = None
            uscita_id = uscita_map["__default__"].id

        t = Transazione(
            data=data,
            direzione=direzione,
            descrizione=r.descrizione,
            importo=importo,          # segno originale mantenuto, MAI abs()
            account_id=account_map[conto_norm].id,
            entrata_id=entrata_id,
            uscita_id=uscita_id,
            prev=r.prev,
        )
        db.add(t)
        importate += 1

    db.commit()
    print(f"✅ {importate} transazioni pulite create (TUTTE, segno originale mantenuto)")
    print(f"⚠️  {skippate} righe escluse (conto o importo mancante, data illeggibile)")
    db.close()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "dati.xlsx"
    import_raw(path)
    costruisci_tabelle_pulite()