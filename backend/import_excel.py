import openpyxl
from database import SessionLocal
from models import Account, Entrata, Uscita, Transazione
from datetime import date

# ─── Mappatura categorie conti (normalizzati in minuscolo) ─────────────────
# Aggiorniamo insieme dopo aver visto la lista reale dei conti
CATEGORIA_CONTI = {
    "liquidità": [
        "marco cc ger", "marco cc ita", "marco cc ingdiba", "marco cc risp",
        "marco cc risp ingdiba", "marco libretto", "marco portafoglio",
        "linda cc ger", "linda cc ingdiba", "linda cc risp",
        "linda cc risp ingdiba", "linda portafoglio",
        "conto comune", "conto puntino", "conto virgola",
        "cassa anna", "tagesgeld",
    ],
    "investimento": [
        "marco investimento", "linda investimento", "quirion",
    ],
    "carta di credito": [
        "marco carta credito", "linda carta credito", "american express",
    ],
    "debito": [
        "marco debito", "mutuo banca", "mutuo papa",
    ],
    "credito verso terzi": [
        "marco crediti a terzi", "marco credito pf",
        "linda credito is", "caparra",
    ],
}

def get_categoria_conto(nome_normalizzato):
    for categoria, nomi in CATEGORIA_CONTI.items():
        if nome_normalizzato in nomi:
            return categoria
    return "liquidità"  # default se non trovato

def normalizza_conto(nome):
    return nome.strip().lower() if nome else ""

def parse_data(anno, mese, giorno):
    try:
        return date(int(str(anno)[:4]), int(str(mese)[4:6]), int(giorno))
    except:
        return None

def import_excel(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    db = SessionLocal()

    try:
        # ── 1. Leggi conti da Lista Spese (tutti i conti reali distinti) ──
        print("📋 Lettura conti...")
        ws_spese = wb["Lista Spese"]
        rows = list(ws_spese.iter_rows(min_row=2, values_only=True))

        # Filtra solo transazioni reali (Prev vuoto) ed escludi immobili
        reali = [
            r for r in rows
            if not r[5]  # Prev vuoto
            and r[6]     # ha un conto
            and not normalizza_conto(r[6]).startswith("app")
        ]

        # Conti distinti
        nomi_conti = sorted(set(normalizza_conto(r[6]) for r in reali if r[6]))
        
        # Crea gli Account nel DB
        account_map = {}  # nome_normalizzato -> oggetto Account
        for nome in nomi_conti:
            categoria = get_categoria_conto(nome)
            acc = Account(nome_conto=nome.title(), categoria=categoria)
            db.add(acc)
            account_map[nome] = acc
        db.flush()
        print(f"  ✅ {len(account_map)} conti creati")

        # ── 2. Leggi Causali Entrata/Uscita da Elenchi ───────────────────
        print("📋 Lettura causali entrata/uscita...")
        ws_elenchi = wb["Elenchi"]
        elenchi_rows = list(ws_elenchi.iter_rows(min_row=2, values_only=True))

        # Mappa causali dalle transazioni reali (fonte più affidabile)
        causali_entrata = set()
        causali_uscita = set()
        
        for r in reali:
            causale_in = r[7]   # colonna Causale Entrata
            causale_out = r[8]  # colonna Causale Uscita
            if causale_in and str(causale_in).strip():
                causali_entrata.add(str(causale_in).strip())
            if causale_out and str(causale_out).strip():
                causali_uscita.add(str(causale_out).strip())

        # Crea Entrate nel DB (categoria default "Attive", aggiorniamo dopo)
        entrata_map = {}
        for nome in sorted(causali_entrata):
            e = Entrata(nome_entrata=nome, categoria="Attive")
            db.add(e)
            entrata_map[nome] = e
        db.flush()
        print(f"  ✅ {len(entrata_map)} causali entrata create")

        # Crea Uscite nel DB (categoria default "Necessaria", aggiorniamo dopo)
        uscita_map = {}
        for nome in sorted(causali_uscita):
            u = Uscita(nome_uscita=nome, categoria="Necessaria")
            db.add(u)
            uscita_map[nome] = u
        db.flush()
        print(f"  ✅ {len(uscita_map)} causali uscita create")

        # ── 3. Importa transazioni (ultimi 2 anni) ────────────────────────
        print("📋 Importazione transazioni 2024-2026...")
        importate = 0
        skippate = 0

        for r in reali:
            anno = r[4]
            if not r[0] or int(r[0]) < 2024:
                continue

            conto_norm = normalizza_conto(r[6])
            causale_in = str(r[7]).strip() if r[7] else None
            causale_out = str(r[8]).strip() if r[8] else None
            descrizione = str(r[9]).strip() if r[9] else None
            importo = r[10] if r[10] else None

            if not importo:
                skippate += 1
                continue

            # Determina direzione
            if causale_in and causale_in in entrata_map:
                direzione = "Entrata"
                entrata_id = entrata_map[causale_in].id
                uscita_id = None
            elif causale_out and causale_out in uscita_map:
                direzione = "Uscita"
                entrata_id = None
                uscita_id = uscita_map[causale_out].id
            else:
                skippate += 1
                continue

            # Costruisci data dalle colonne YYYY, MM, DD
            try:
                data = date(int(r[0]), int(r[1]), int(r[2]))
            except:
                skippate += 1
                continue

            t = Transazione(
                data=data,
                direzione=direzione,
                descrizione=descrizione,
                importo=abs(float(importo)),
                account_id=account_map[conto_norm].id,
                entrata_id=entrata_id,
                uscita_id=uscita_id,
            )
            db.add(t)
            importate += 1

        db.commit()
        print(f"  ✅ {importate} transazioni importate")
        print(f"  ⚠️  {skippate} righe skippate (senza causale o importo)")
        print("\n🎉 Import completato!")

    except Exception as e:
        db.rollback()
        print(f"❌ Errore: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "dati.xlsx"
    import_excel(path)