# LAME - Gestione Certificati Qualità

Plugin per il Reparto Qualità di LAME Srl: automatizza la lavorazione dei PDF che arrivano insieme alla merce in ingresso (fusti/forgiati grezzi, tondi, barre, tubi...), quando questi PDF mescolano insieme più tipi di documento: DDT (Documento di Trasporto), certificati di collaudo acciaieria (3.1/3.2, EN 10204) e, quando presente, certificato di forgia.

## Cosa fa

Il plugin espone sette skill:

1. **`verifica-parti-gia-processate`** — passo preliminare: controlla se il PDF di Input contiene parti (DDT, certificato forgia, certificato acciaieria) già archiviate in un run precedente incompleto o da un altro file, e produce un piano che limita il lavoro delle skill successive alle sole parti mancanti — evitando di rielaborare da capo un intero file solo perché è rimasto parzialmente in `Input/`.
2. **`prepara-pdf-per-ocr`** — rasterizza le pagine di un PDF scansionato o di qualità incerta alla risoluzione ottimale (default 150 DPI) prima della lettura visiva, bilanciando accuratezza OCR e consumo di token. Richiamata come passo preliminare da `estrai-ddt-da-pdf` e `quality-steel` quando serve.
3. **`estrai-ddt-da-pdf`** — trova le pagine di vero DDT dentro il PDF misto (non le semplici citazioni/timbri) e le archivia per anno/mese e per fornitore.
4. **`quality-steel`** — identifica le pagine di certificato materiale (forgia e/o acciaieria), le raggruppa per Heat/Colata, ed estrae per ciascuna i dati generali, la composizione chimica e le proprietà meccaniche in una scheda PDF riepilogativa.
5. **`archivia-certificati-materiale`** — riprende la classificazione forgia/acciaieria già fatta da `quality-steel`, estrae le pagine di certificato originali come documenti PDF a sé stanti e le archivia per azienda produttrice, e tiene le schede generate in una cartella unica.
6. **`archivia-in-processed`** — ultimo passo del flusso: verifica che tutte le fasi precedenti si siano concluse senza errori e, solo in quel caso, sposta il PDF sorgente da `Input/` a `Processed/YYYY/MM/` (anno/mese di elaborazione completata).
7. **`controllore`** — controllo di coerenza a posteriori sull'intero archivio, indice Excel incluso: verifica che ogni file (e ogni riga di `Output/Indice_Heat_Certificati.xlsx`) abbia tutte le sue copie/derivati attesi in tutte le cartelle di destinazione (es. un DDT presente in `DDT/<Anno>/<Mese>/` ma assente dalla sua copia in `DDT/Fornitori/<Fornitore>/`) e ripara autonomamente le mancanze trovate — richiamando la skill giusta per quelle che richiedono ri-elaborazione (es. `quality-steel` per una scheda mancante, `lame-heat-index-excel` per una riga d'indice mancante o disallineata, `archivia-in-processed` per un PDF completo ma non ancora spostato) — risolvendo i casi non del tutto netti con l'ipotesi più probabile invece di fermarsi, e lasciando davvero in sospeso solo i conflitti irreversibili (contenuto diverso già presente). **È un passo obbligatorio, non facoltativo**: va eseguito in automatico alla fine di ciascuna delle altre sei skill (ognuna lo richiama come proprio ultimo passo quando è collegata una cartella di lavoro strutturata) e di nuovo a chiusura dell'intero flusso, oltre che su richiesta esplicita.

Le prime sei skill sono complementari e non si sovrappongono: la prima verifica cosa è già stato fatto, la seconda prepara le immagini per la lettura, la terza si occupa solo di DDT, la quarta solo di lettura/estrazione dati tecnici, la quinta solo di archiviazione dei documenti/schede, la sesta solo dello spostamento finale del sorgente. `verifica-parti-gia-processate` è sempre la prima (quando applicabile), `archivia-in-processed` è sempre l'ultima del flusso per-singolo-PDF, perché dipende dal completamento di tutte le altre. `controllore` sta a un livello sopra a tutte: non è un passo del flusso per-singolo-PDF, ma un controllo — obbligatorio, non un extra opzionale — sull'intero archivio già prodotto, eseguito dopo ciascuna skill e a chiusura del flusso, per intercettare e sanare subito le incoerenze che il flusso normale potrebbe aver lasciato (run interrotti, copie mancanti, schede orfane, indice Excel disallineato).

## Ambienti di lavoro supportati

Tutte le skill funzionano nello stesso modo, qualunque sia l'ambiente in cui vive la cartella di lavoro (`Input/`, `DDT/`, `Acciaierie/`, `Forgie/`, `Output/`, `Processed/`):

- **Cartella locale o sincronizzata sul computer dell'utente** — inclusa una cartella OneDrive o Google Drive sincronizzata con il client desktop, che dal punto di vista del plugin è indistinguibile da una cartella locale: le skill usano i tool del computer collegato (`mcp__remote-devices__*`, in particolare `device_bash`, `device_stage_files`, `device_commit_files`).
- **Google Drive raggiunto solo via API**, senza un computer collegato — il caso tipico di una schedulazione automatica giornaliera che analizza la cartella `Input/` su Drive: le skill usano i tool `mcp__Google_Drive__*` (`search_files`, `download_file_content`, `create_file`, `update_file`) e, per spostare un file, ne aggiornano la cartella padre invece di fare un `mv`.
- **File caricati direttamente in chat**, senza nessuna cartella collegata: le skill lavorano nel workspace cloud e consegnano i risultati con `SendUserFile`.

**OneDrive non ha un connettore API dedicato in questo plugin.** È supportato solo quando la cartella è sincronizzata sul computer dell'utente tramite il client desktop OneDrive (ricade quindi nel primo caso, come una qualunque cartella locale). Se una cartella OneDrive non è sincronizzata localmente e serve raggiungerla via API, va aggiunto un connettore apposito.

Se non è chiaro in quale di questi ambienti si trovi la cartella di lavoro della conversazione, ogni skill chiede conferma prima di procedere invece di indovinare.

## Struttura cartelle risultante

A partire da una cartella di lavoro condivisa (es. la cartella del Reparto Qualità, locale o su Drive/OneDrive), il flusso produce questa struttura:

```
<cartella di lavoro>/
├── Input/                          # PDF sorgente da lavorare (scansioni certificati + DDT misti)
├── DDT/
│   ├── <Anno>/<Mese>/              # DDT trovati, organizzati per anno e mese
│   └── Fornitori/<Fornitore>/      # stesso DDT, organizzato anche per fornitore
├── Acciaierie/<Azienda>/           # certificati acciaieria originali, per azienda
├── Forgie/<Azienda>/               # certificati forgia originali, per azienda (solo se presenti)
├── Output/                         # schede riepilogative Scheda_Heat_<Heat>.pdf generate da quality-steel
└── Processed/<Anno>/<Mese>/        # PDF sorgente, spostati qui una volta completate tutte le fasi del flusso
```

Regole importanti applicate dalle skill:

- Un `DDT` o un certificato può occupare più pagine consecutive: vengono sempre estratte insieme come un unico PDF.
- I nomi delle cartelle azienda/fornitore sono normalizzati togliendo la forma societaria (S.p.A., Srl, S.n.c., punti nelle sigle) — es. "RO.LA.FER. S.p.A." → `Rolafer`, "FORG.MAES. S.n.c." → `Forgmaes`.
- `Forgie/` viene creata solo se nel set di PDF analizzato esiste davvero almeno un certificato di forgia — non per simmetria con `Acciaierie/`.
- `Output/` contiene solo le schede generate (gli elaborati); `Acciaierie/` e `Forgie/` contengono solo i documenti originali; non vanno mai mescolati.
- Un PDF sorgente si sposta da `Input/` a `Processed/<Anno>/<Mese>/` solo dopo che tutte le fasi pertinenti sono state completate su di esso e senza errori (questo controllo e lo spostamento spettano sempre ad `archivia-in-processed`, mai alle altre skill). Se manca una fase, il file resta in `Input/`.
- Nessun file viene mai duplicato, né a livello di intero documento né di singola parte: se un PDF sorgente è già in `Processed/`, è già stato lavorato per intero. Se invece resta in `Input/` con solo alcune parti (DDT, forgia, acciaieria) già archiviate — tipicamente perché un run precedente si è fermato a metà — `verifica-parti-gia-processate` individua quali parti sono già presenti in `DDT/`, `Acciaierie/`, `Forgie/` e `Output/` e fa rielaborare alle skill successive solo quelle mancanti.
- In caso di dato ambiguo o poco leggibile (fornitore, data, numero certificato, colata), le skill chiedono conferma invece di indovinare.

## Come usarlo

Basta chiedere in linguaggio naturale, ad esempio:

- "Verifica se questo PDF è già stato elaborato in parte" / "evita di rifare le parti già fatte" → `verifica-parti-gia-processate`
- "Analizza i PDF in Input e archivia i DDT" → `estrai-ddt-da-pdf`
- "Estrai i dati dei certificati materiale da questi PDF" → `quality-steel`
- "Archivia anche i certificati originali" → `archivia-certificati-materiale`
- "Archivia/sposta/chiudi questo documento già elaborato" → `archivia-in-processed`
- "Controlla che l'archivio sia tutto a posto" / "verifica che non manchi niente, excel compreso" → `controllore`

oppure chiedere direttamente il flusso completo ("lavora questi PDF in Input dall'inizio alla fine") e le skill verranno applicate in sequenza, con `verifica-parti-gia-processate` come primo passo (per non rilavorare parti già archiviate) e `archivia-in-processed` come passo finale.

## Requisiti tecnici

Le skill si appoggiano a strumenti da riga di comando comuni (`pdfinfo`, `pdftotext`, `pdftoppm`, `qpdf`) e, per `quality-steel`, allo script Python incluso in `skills/quality-steel/scripts/genera_scheda_heat.py` (richiede il pacchetto `reportlab`). Per Google Drive via API serve il connettore `Google Drive` connesso; per una cartella locale o sincronizzata (OneDrive/Google Drive for Desktop) serve un computer collegato tramite l'app desktop Claude.
