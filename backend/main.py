from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models import Account, Entrata, Uscita, Transazione
from datetime import date

app = FastAPI(title="Patrimonio API", version="1.0")

# Permette al frontend (React) di chiamare le API da un dominio diverso
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ACCOUNTS ────────────────────────────────────────────────────────────────

@app.get("/accounts")
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).order_by(Account.categoria, Account.nome_conto).all()
    return [
        {"id": a.id, "nome": a.nome_conto, "categoria": a.categoria}
        for a in accounts
    ]

# ── DASHBOARD SUMMARY ───────────────────────────────────────────────────────

@app.get("/dashboard/summary")
def get_summary(anno: int = None, mese: int = None, db: Session = Depends(get_db)):
    # Default: mese corrente
    oggi = date.today()
    anno = anno or oggi.year
    mese = mese or oggi.month

    base = db.query(Transazione).filter(
        extract("year", Transazione.data) == anno,
        extract("month", Transazione.data) == mese,
    )

    totale_entrate = base.filter(
        Transazione.direzione == "Entrata"
    ).with_entities(func.sum(Transazione.importo)).scalar() or 0

    totale_uscite = base.filter(
        Transazione.direzione == "Uscita"
    ).with_entities(func.sum(Transazione.importo)).scalar() or 0

    risparmio = totale_entrate - totale_uscite
    tasso_risparmio = (risparmio / totale_entrate * 100) if totale_entrate > 0 else 0

    return {
        "anno": anno,
        "mese": mese,
        "totale_entrate": round(float(totale_entrate), 2),
        "totale_uscite": round(float(totale_uscite), 2),
        "risparmio": round(float(risparmio), 2),
        "tasso_risparmio": round(float(tasso_risparmio), 1),
    }

# ── CASHFLOW ULTIMI 6 MESI ──────────────────────────────────────────────────

@app.get("/dashboard/cashflow")
def get_cashflow(db: Session = Depends(get_db)):
    risultati = db.query(
        extract("year", Transazione.data).label("anno"),
        extract("month", Transazione.data).label("mese"),
        Transazione.direzione,
        func.sum(Transazione.importo).label("totale"),
    ).group_by("anno", "mese", Transazione.direzione)\
     .order_by("anno", "mese")\
     .all()

    # Costruiamo un dizionario anno-mese -> {entrate, uscite}
    cashflow = {}
    for r in risultati:
        chiave = f"{int(r.anno)}-{int(r.mese):02d}"
        if chiave not in cashflow:
            cashflow[chiave] = {"periodo": chiave, "entrate": 0, "uscite": 0}
        if r.direzione == "Entrata":
            cashflow[chiave]["entrate"] = round(float(r.totale), 2)
        else:
            cashflow[chiave]["uscite"] = round(float(r.totale), 2)

    return sorted(cashflow.values(), key=lambda x: x["periodo"])

# ── TRANSAZIONI ─────────────────────────────────────────────────────────────

@app.get("/transazioni")
def get_transazioni(
    anno: int = None,
    mese: int = None,
    conto_id: int = None,
    direzione: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Transazione)

    if anno:
        query = query.filter(extract("year", Transazione.data) == anno)
    if mese:
        query = query.filter(extract("month", Transazione.data) == mese)
    if conto_id:
        query = query.filter(Transazione.account_id == conto_id)
    if direzione:
        query = query.filter(Transazione.direzione == direzione)

    totale = query.count()
    transazioni = query.order_by(Transazione.data.desc()).offset(offset).limit(limit).all()

    return {
        "totale": totale,
        "offset": offset,
        "limit": limit,
        "transazioni": [
            {
                "id": t.id,
                "data": t.data.isoformat(),
                "direzione": t.direzione,
                "importo": float(t.importo),
                "descrizione": t.descrizione,
                "conto": t.account.nome_conto,
                "causale": t.entrata.nome_entrata if t.entrata else t.uscita.nome_uscita if t.uscita else None,
            }
            for t in transazioni
        ],
    }

# ── ENTRATE E USCITE PER CATEGORIA ─────────────────────────────────────────

@app.get("/dashboard/per-categoria")
def get_per_categoria(anno: int = None, mese: int = None, db: Session = Depends(get_db)):
    oggi = date.today()
    anno = anno or oggi.year
    mese = mese or oggi.month

    # Uscite per categoria
    uscite = db.query(
        Uscita.categoria,
        func.sum(Transazione.importo).label("totale")
    ).join(Transazione, Transazione.uscita_id == Uscita.id)\
     .filter(
        extract("year", Transazione.data) == anno,
        extract("month", Transazione.data) == mese,
     ).group_by(Uscita.categoria).all()

    # Entrate per categoria
    entrate = db.query(
        Entrata.categoria,
        func.sum(Transazione.importo).label("totale")
    ).join(Transazione, Transazione.entrata_id == Entrata.id)\
     .filter(
        extract("year", Transazione.data) == anno,
        extract("month", Transazione.data) == mese,
     ).group_by(Entrata.categoria).all()

    return {
        "uscite_per_categoria": [
            {"categoria": r.categoria, "totale": round(float(r.totale), 2)}
            for r in uscite
        ],
        "entrate_per_categoria": [
            {"categoria": r.categoria, "totale": round(float(r.totale), 2)}
            for r in entrate
        ],
    }