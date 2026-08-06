# Note di progetto — regole di business validate

## Fonte dati
- `transazioni_raw`: copia 1:1 del foglio Excel "Lista Spese", nessuna logica applicata, MAI filtrata
- Tabelle pulite (`accounts`, `entrate`, `uscite`, `transazioni`): costruite da `transazioni_raw` tramite `costruisci_tabelle_pulite()` in `import_excel.py`

## Regole di calcolo saldi (validate al centesimo su 15+ conti)
- Transazione valida per saldi = colonna `Prev` vuota OPPURE `Prev == "chiusure"`
- Saldo conto = somma di `importo` (con segno originale, MAI valore assoluto) da 2023-01-01 in poi
- Nomi conto: case-insensitive, confronto sempre su `.strip().lower()`
- Il nome "ufficiale" di un conto è la variante di scrittura più frequente nell'Excel

## Colonna `direzione` (Entrata/Uscita)
- Usata SOLO per categorizzare/raggruppare (es. "quanto in Necessaria"), MAI per calcolare saldi
- Determinata da: causale_entrata valorizzata → Entrata; causale_uscita valorizzata → Uscita; altrimenti segno importo decide
- ATTENZIONE: causale e segno possono essere in disaccordo (storni/rimborsi) — l'importo mantiene sempre il segno vero

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