---
name: verifica-parti-gia-processate
description: >-
  Verifica, prima di lanciare il flusso completo su un PDF di Input,
  quali parti (DDT, certificato forgia, certificato acciaieria) sono già
  state archiviate in precedenza — anche solo in parte — così le skill
  successive (estrai-ddt-da-pdf, quality-steel, archivia-certificati-materiale)
  lavorano solo sulle parti mancanti invece di ripartire da zero. Usa
  SEMPRE questa skill come primo passo, prima delle altre, quando un PDF
  in Input contiene più certificati/DDT ed esiste il rischio che alcuni
  siano già stati elaborati in un run precedente incompleto, o che
  duplichino certificati/DDT già archiviati da un altro file.
---

# Verifica parti già processate

## Perché esiste questa skill

Il flusso di questo plugin dedup già l'intero PDF sorgente: se un file è
già in `Processed/`, è stato lavorato per intero e non va ritoccato. Ma
non copre due casi frequenti:

- un PDF resta in `Input/` perché un run precedente si è fermato a metà
  (es. `archivia-in-processed` non l'ha spostato perché solo DDT +
  certificato forgia1 + certificato acciaieria1 erano stati archiviati,
  ma forgia2/acciaieria2 no) — rilanciare il flusso da capo rielaborerebbe
  anche le parti già fatte, sprecando token e tempo;
- un PDF nuovo (nome diverso, magari lo stesso documento ricevuto o
  scansionato due volte) contiene pagine che duplicano certificati/DDT
  già archiviati da un file precedente.

Questa skill individua **quali parti del PDF sono già archiviate** e
produce un piano di lavorazione che indica alle skill successive di
occuparsi solo di quelle mancanti.

## Quando usare questa skill

Usala **sempre come primo passo**, prima di `estrai-ddt-da-pdf` e
`quality-steel`, quando si lavora su un PDF di `Input/` che contiene più
di un certificato/DDT, o quando l'utente chiede esplicitamente di
controllare/evitare doppioni ("verifica se questo è già stato
elaborato", "evita di rifare le parti già fatte", "controlla i
doppioni prima di ripartire"). Se il flusso completo viene chiesto in
un colpo solo ("lavora questi PDF in Input dall'inizio alla fine"),
applicala comunque per prima, in automatico, senza bisogno che l'utente
la nomini esplicitamente.

Non serve se il PDF proviene da un file appena caricato in chat senza
nessuna cartella di lavoro collegata (locale o Google Drive): senza una
cartella con `DDT/`, `Acciaierie/`, `Forgie/`, `Output/` da controllare
non c'è nulla con cui confrontare, quindi si passa direttamente alle
skill successive sull'intero file.

## Relazione con le altre skill

- Va usata **prima** di `estrai-ddt-da-pdf`, `quality-steel` e
  `archivia-certificati-materiale`: il suo output (l'elenco delle parti
  da fare, con i relativi intervalli di pagina) è l'input che restringe
  il lavoro di quelle skill al sottoinsieme di pagine ancora da
  elaborare, invece che all'intero PDF.
- Non sostituisce la logica di dedup di `archivia-in-processed` (che
  resta l'ultimo passo e verifica il completamento **di tutto** il
  file prima di spostarlo in `Processed/`): questa skill lavora
  **prima**, a livello di singola parte, non di intero file.
- Non legge né interpreta i dati tecnici completi dei certificati
  (composizione chimica, proprietà meccaniche): quella resta compito
  esclusivo di `quality-steel`. Questa skill estrae solo le chiavi
  identificative minime necessarie al confronto.
- Se il PDF è scansionato o di qualità incerta, richiama `prepara-pdf-per-ocr`
  come le altre skill del flusso, ma solo per le pagine i cui campi
  chiave non sono leggibili dal testo.

## Dove lavorare

Come le altre skill del plugin, funziona allo stesso modo qualunque sia
l'ambiente della cartella di lavoro:

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google
  Drive for Desktop, o cartella locale — tool `mcp__remote-devices__*`):
  verifica quale cartella è connessa con `get_device_info`. Il PDF di
  Input va messo in staging (`device_stage_files`) solo se serve leggere
  visivamente pagine senza layer di testo affidabile (tool Read,
  disponibile solo nel workspace cloud); il confronto con le cartelle
  di destinazione (`DDT/`, `Acciaierie/`, `Forgie/`, `Output/`) si fa
  invece con semplici `device_list_dir` — non serve mai mettere in
  staging i file già archiviati, basta leggerne i nomi.
- **Google Drive via API** (nessuna cartella sincronizzata sul
  computer — tipico di una schedulazione automatica giornaliera): usa
  `mcp__Google_Drive__*` — `search_files` per elencare i file già
  presenti in `DDT/`, `Acciaierie/<Azienda>/`, `Forgie/<Azienda>/`,
  `Output/`, senza mai scaricarne il contenuto (`download_file_content`
  serve solo per leggere il PDF di Input, non i file già archiviati).
- **File caricati direttamente in chat, senza cartella collegata**: non
  c'è nulla da confrontare (vedi sopra), quindi questa skill non si
  applica e si passa direttamente alle skill successive.
- Se non è chiaro in quale ambiente si trovi la cartella di lavoro,
  chiedi conferma prima di procedere invece di indovinare.

## Procedura

### 1. Ricognizione leggera del PDF di Input

Per il PDF indicato, individuare — **senza fare l'estrazione dati
completa** — le parti che contiene e, per ciascuna, le chiavi minime
identificative:

1. Prova `pdftotext -layout input.pdf -` per pagina o piccolo gruppo di
   pagine. Se il testo è presente e leggibile, usalo per individuare:
   - **Tipo di pagina**: DDT (intestazione "DOCUMENTO DI TRASPORTO" /
     "AVVISO DI SPEDIZIONE"), certificato forgia (campo "Heat Code" o
     equivalente, es. "Ns. sigla"), certificato acciaieria (solo "Heat
     Number", senza Heat Code) — stessa euristica di `quality-steel` e
     `estrai-ddt-da-pdf`, usata qui solo per instradamento, non per
     l'estrazione completa.
   - **Chiavi identificative**: numero certificato o numero DDT,
     azienda/fornitore (nome da intestazione), Heat/Colata se
     facilmente leggibile dal testo.
   - **Intervallo di pagine** nel file sorgente occupato da quella
     parte (un certificato o un DDT può occupare più pagine
     consecutive: vanno trattate come un'unica parte).
2. Se il testo è assente o inaffidabile (scansione), usa
   `prepara-pdf-per-ocr` e poi il tool Read, ma **solo sulle pagine e
   sui campi necessari a stabilire tipo + chiavi identificative**
   (numero, azienda/fornitore, Heat/Colata) — non leggere/estrarre
   composizione chimica, proprietà meccaniche o altri dati tecnici in
   questa fase: quello, se la parte risulta nuova, spetta a
   `quality-steel`.
3. Se azienda/fornitore o numero non sono leggibili con certezza nemmeno
   a questo livello minimo, trattali come non determinabili: la parte
   corrispondente va considerata "da fare" (vedi punto 3 più sotto),
   non "già fatta" — non si può escludere dal lavoro qualcosa che non
   si riesce a identificare con certezza.

### 2. Confronto con l'archivio esistente

Per ciascuna parte individuata al passo 1, cerca — **solo tramite
listing delle cartelle di destinazione**, mai riaprendo o scaricando i
PDF già archiviati — un file corrispondente:

- **Certificato forgia o acciaieria**: normalizza il nome azienda con
  le stesse regole usate da `archivia-certificati-materiale` (togli
  forma societaria, punti nelle sigle — es. "RO.LA.FER. S.p.A." →
  "Rolafer"), poi cerca in `Forgie/<Azienda>/` o `Acciaierie/<Azienda>/`
  un file il cui nome contenga **sia** il numero certificato **sia** la
  colata (convenzione `Certificato <numero> - <Azienda> - Colata
  <Heat>.pdf`). Verifica anche che esista `Output/Scheda_Heat_<Heat>.pdf`.
- **DDT**: normalizza il nome fornitore con le stesse regole usate da
  `estrai-ddt-da-pdf`, poi cerca in `DDT/Fornitori/<Fornitore>/` un
  file il cui nome contenga **sia** il numero DDT **sia** la data
  (convenzione `DDT <numero> - <Fornitore> - <gg.mm.aaaa>.pdf`).

### 3. Decisione: già fatta o da fare

- Una parte è **"già completamente processata"** solo se il match è
  **netto e certo su tutte le chiavi rilevanti** (stesso numero +
  stessa azienda + stessa colata per i certificati; stesso numero +
  stesso fornitore + stessa data per i DDT) **e** l'eventuale output
  atteso (scheda Heat in `Output/`, per le parti forgia/acciaieria)
  esiste già. Solo in questo caso va esclusa dal lavoro successivo.
- **Qualunque caso ambiguo o match solo parziale** — nomi simili ma non
  identici, numero che coincide ma azienda no (o viceversa), colata
  diversa, dato non determinabile al passo 1 — va **sempre trattato
  come NON duplicato**: la parte resta "da fare" e viene rilavorata
  normalmente dalle skill successive. Non segnalare comunque il quasi-match
  nel riepilogo finale, così l'utente può verificarlo se vuole
  ricontrollare a mano un eventuale doppione.
- Nessun indice o file di stato dedicato viene mantenuto: il confronto
  si basa sempre e solo su ciò che è effettivamente presente nelle
  cartelle di destinazione al momento del controllo.

### 4. Piano di lavorazione

Costruisci un piano per il PDF analizzato:

- **Parti già archiviate** (escluse dal lavoro): tipo, intervallo
  pagine nel sorgente, chiavi identificative, percorso dove sono già
  archiviate.
- **Parti da elaborare**: tipo, intervallo pagine nel sorgente, chiavi
  identificative (se determinabili a questo stadio).

Passa il piano alle skill successive indicando esplicitamente di
operare **solo** sugli intervalli di pagina segnati come "da
elaborare": `estrai-ddt-da-pdf` per le parti DDT da fare,
`quality-steel` (e a seguire `archivia-certificati-materiale`) per le
parti forgia/acciaieria da fare. Se tutte le parti risultano già
archiviate, non richiamare le skill successive: passa direttamente a
verificare con `archivia-in-processed` se il file può essere spostato
in `Processed/`.

### 5. Riepilogo

Riepiloga sempre all'utente, prima di procedere: quali parti sono state
trovate nel PDF, quali risultano già archiviate (e dove), quali
verranno effettivamente elaborate. Se una parte non è stata identificata
con certezza (azienda o numero non leggibili), segnalalo esplicitamente
e chiedi conferma prima di deciderne la sorte, invece di indovinare.

## Passo finale obbligatorio: controllore

Al termine di questa skill, prima di passare alle skill successive del
flusso, richiama **sempre** la skill `controllore` — passo obbligatorio, non
facoltativo, anche se questa skill in sé non ha modificato nulla: serve a
intercettare eventuali incoerenze già presenti nell'archivio prima di
iniziare a lavorarci sopra. Unica eccezione: se il PDF proviene da un file
caricato in chat senza nessuna cartella di lavoro collegata (locale o Google
Drive), non esiste un archivio strutturato da controllare — in quel caso
salta questo passo.

## Attenzione

- Questa skill **non sposta, non elimina e non modifica mai nulla**: si
  limita a determinare il piano. Il PDF sorgente resta in `Input/` in
  ogni caso — lo spostamento finale resta compito esclusivo di
  `archivia-in-processed`, a flusso interamente concluso.
- Non fare mai l'estrazione dati completa (chimica/meccanica) in questa
  fase, nemmeno per le parti che risulteranno "da fare": è compito di
  `quality-steel`, chiamata dopo con il piano già pronto.
- In caso di dubbio sul match (nomi simili, dato parzialmente leggibile),
  tratta sempre la parte come "da fare": è preferibile un doppione
  occasionale da controllare a mano piuttosto che perdere un certificato
  per un falso positivo.
- Non creare né aggiornare nessun file di indice/log a parte: il
  controllo si basa solo sullo stato reale delle cartelle di
  destinazione al momento dell'esecuzione.
- Se le cartelle di destinazione (`DDT/`, `Acciaierie/`, `Forgie/`,
  `Output/`) non esistono ancora (prima elaborazione in questa cartella
  di lavoro), non c'è nulla con cui confrontare: tutte le parti sono
  "da fare", passa direttamente alle skill successive senza ulteriori
  controlli.
