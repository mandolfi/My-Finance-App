# Note di progetto — regole di business validate

## Fonte dati
- `transazioni_raw`: copia 1:1 del foglio Excel "Lista Spese", nessuna logica applicata, MAI filtrata
- Tabelle pulite (`accounts`, `entrate`, `uscite`, `transazioni`): costruite da `transazioni_raw` tramite `costruisci_tabelle_pulite()` in `import_excel.py`

## Regole di calcolo saldi (validate al centesimo su 15+ conti)
- Transazione valida per saldi = colonna `Prev` vuota OPPURE `Prev == "chiusure"`
- Saldo conto = somma di `importo` (con segno originale, MAI valore assoluto) da 2023-01-01 in poi
- Nomi conto: case-insensitive, confronto sempre su `.strip().lower()`
- Il nome "ufficiale" di un conto è la variante di scrittura più frequente nell'Excel

## Colonna `direzione` (Entrata/Uscita/Movimento)
- Determinata ESCLUSIVAMENTE da quale colonna causale è valorizzata nell'Excel originale:
  - `causale_entrata` valorizzata → direzione = "Entrata"
  - `causale_uscita` valorizzata → direzione = "Uscita"
  - NESSUNA delle due valorizzata → direzione = "Movimento" (trasferimento tra conti propri)
- MAI dedotta dal segno di `importo` — un trasferimento tocca due conti con segni opposti
  ma non è né un guadagno né una spesa economica
- Le righe "Movimento" ESISTONO nella tabella `transazioni` (servono per il saldo dei conti)
  ma vengono escluse dalle query di cashflow/summary tramite `direzione.in_(["Entrata", "Uscita"])`
- Errore commesso e corretto: inizialmente il codice faceva "fallback sul segno" quando
  mancava la causale, gonfiando enormemente Entrate/Uscite mensili con vendite di azioni,
  trasferimenti tra conti propri, ecc. Corretto in data [oggi] — vedi commit
  "Fix critico: direzione Entrata/Uscita basata solo su causale, mai sul segno"

## Endpoint cashflow
- `/dashboard/cashflow?mesi=N` — default 12 mesi, calcolati a ritroso dall'ultima
  transazione reale disponibile nel DB (non da "oggi" di calendario, che può essere
  oltre l'ultimo dato importato)

## Categorie conti
- liquidità, investimento, carta di credito, debito, immobili
- Immobili: nome conto inizia con "app" (case-insensitive) o è "haus"
- Debito include: mutui reali + "Conto Puntino"/"Conto Virgola" (soldi dovuti ai figli, anomalia: segno storicamente positivo invece di negativo — nota, non correggere)
- Patrimonio liquido = liquidità + investimento (esclude immobili e debiti)
- Patrimonio netto totale = patrimonio liquido + valore immobili + debiti (debiti già negativi)

## Struttura app
- Backend: FastAPI + SQLite, cartella `backend/`
- Frontend: React + Vite, cartella `frontend/`
- File chiave: `backend/models.py`, `backend/import_excel.py`, `backend/main.py`