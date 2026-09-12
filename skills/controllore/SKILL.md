---
name: controllore
description: >-
  Controllo di coerenza a posteriori sull'intero archivio del plugin (Input,
  DDT, Acciaierie, Forgie, Output, Processed, incluso l'indice Excel
  Indice_Heat_Certificati.xlsx): verifica che ogni file e ogni riga
  dell'indice abbiano tutte le copie/derivati attesi e siano aggiornati, e
  colma da sola le mancanze scegliendo l'ipotesi più probabile, senza
  fermarsi ad aspettare conferma salvo veri conflitti irrisolvibili. Passo
  OBBLIGATORIO, non facoltativo: va richiamata sempre alla fine di ciascuna
  delle altre skill di questo plugin e di nuovo a chiusura dell'intero
  flusso, senza bisogno che l'utente lo chieda. Usala anche su richiesta
  esplicita di un controllo generale ("controlla che sia tutto a posto",
  "verifica che non manchi niente", "controlla anche l'excel", "il
  controllore"). Non è un passo per-singolo-PDF: opera sull'intero albero
  di cartelle della cartella di lavoro.
---

# Controllore — Verifica di coerenza e riparazione dell'archivio

## Quando usare questa skill — passo obbligatorio, non facoltativo

Questa skill **deve** essere richiamata automaticamente, senza bisogno che
l'utente lo chieda:

1. **Alla fine di ogni altra skill del plugin** (`verifica-parti-gia-processate`,
   `estrai-ddt-da-pdf`, `quality-steel`, `archivia-certificati-materiale`,
   `archivia-in-processed`), come ultimo passo della loro procedura — vedi
   la sezione "Passo finale obbligatorio" che ciascuna di quelle skill
   riporta. Unica eccezione: nessuna cartella di lavoro strutturata è
   collegata (solo file caricati in chat), nel qual caso non c'è nulla da
   controllare.
2. **Alla fine dell'intero flusso**, quando le skill del plugin vengono
   applicate in sequenza a uno o più PDF ("lavora questi PDF in Input
   dall'inizio alla fine"): oltre alle chiamate intermedie del punto 1, va
   comunque eseguita una volta in più a chiusura di tutto il lavoro, per
   avere una verifica d'insieme sull'intero archivio appena aggiornato.
3. **Su richiesta esplicita** di un controllo generale, anche a freddo e
   indipendentemente da una sessione di lavoro appena conclusa — per
   esempio a inizio giornata o dopo una schedulazione automatica. Frasi
   tipiche: "controlla che sia tutto a posto", "verifica che non manchi
   niente nell'archivio", "controlla anche che l'excel sia aggiornato",
   "fai un controllo generale", "il DDT di Valbruna non compare in
   Fornitori, controlla anche il resto", "esegui il controllore".

Non saltare mai questo passo per risparmiare tempo o token: è pensata per
essere economica quando l'archivio è già coerente (si limita a un listing
delle cartelle) e diventa utile esattamente nei casi in cui qualcosa è
sfuggito alle skill precedenti.

Non serve invocarla per singole domande su un solo PDF appena caricato in
chat senza cartella di lavoro collegata (locale o Google Drive): senza un
archivio strutturato (`DDT/`, `Acciaierie/`, `Forgie/`, `Output/`,
`Processed/`) da controllare non c'è nulla con cui confrontare.

## Filosofia: risolvere, non bloccare

A differenza delle altre skill del flusso — che su un dato ambiguo si
fermano e chiedono conferma perché stanno processando un documento nuovo,
mai visto prima — il controllore lavora **su un archivio già in gran parte
corretto**, dove quasi ogni mancanza ha un'unica spiegazione plausibile
ricostruibile dal contesto (nomi file già usati altrove, cartelle già
esistenti, dati già estratti in un'altra scheda/riga). Per questo la regola
di default qui è: **individua l'ipotesi più probabile e applicala**, invece
di fermarti. Usa sempre la stessa gerarchia di evidenze, dalla più forte alla
più debole:

1. Un file o una cartella già esistenti altrove nell'archivio con lo stesso
   numero (certificato/DDT) o lo stesso Heat: quella è la fonte di verità,
   usala per determinare fornitore/azienda/dati mancanti invece di rileggere
   o indovinare da capo.
2. Corrispondenza quasi esatta di nome cartella/fornitore già presente
   nell'archivio (es. maiuscole/spazi diversi, una sigla abbreviata in modo
   leggermente diverso ma riconducibile senza dubbio alla stessa azienda):
   usa la cartella/il nome già esistente, non crearne uno nuovo leggermente
   diverso.
3. Se restano più ipotesi ugualmente plausibili e nessuna evidenza le
   distingue (es. due fornitori diversi con nomi altrettanto simili al file
   ambiguo, e nessuno dei due già presente in archivio) — solo in questo
   caso, davvero residuale, segnala la scelta più probabile che hai comunque
   applicato e nota nel riepilogo finale che andrebbe ricontrollata, invece
   di lasciare la mancanza non colmata.

Per i **file archiviati** (PDF), l'unico caso in cui il controllore si
**ferma davvero** senza applicare nulla è un conflitto reale: un file già
esistente nella destinazione con **contenuto diverso** da quello che
dovresti copiare (vedi "Vincolo trasversale" più sotto) — lì sovrascrivere
sarebbe una perdita di dati, non un'ipotesi da scegliere, e non esiste un
modo sicuro per duplicare un PDF senza rompere le convenzioni di naming del
plugin.

Per le **righe dell'indice Excel** il caso è diverso, perché lì duplicare
non rompe nulla: se la riga già esistente per un Heat Number ha valori in
conflitto con quelli che dovresti scrivere, verifica prima se si tratta
davvero della **stessa colata/dello stesso documento** (stesso numero
certificato, stessa azienda, stesso numero DDT, stessi file già archiviati
coerenti con entrambe le fonti). Se sei **assolutamente certo** che sia lo
stesso file, **sovrascrivi** la riga aggiornandola sul posto (è un
aggiornamento, non un conflitto). Se resta un dubbio ragionevole — potrebbe
trattarsi di due colate diverse che condividono per errore lo stesso Heat
Number, o di dati discordanti che non riesci a ricondurre con certezza allo
stesso documento — **non sovrascrivere**: aggiungi una **seconda riga**
con lo stesso Heat Number, così nessun dato viene perso, e segnala il caso
nel riepilogo finale come duplicato da verificare manualmente. Non lasciare
mai questo caso "in sospeso senza fare nulla": o sei certo e aggiorni, o non
lo sei e aggiungi la seconda riga — il fermarsi senza applicare nessuna
delle due è riservato solo ai conflitti sui file PDF descritti sopra.

## Relazione con le altre skill

Questa skill sta **un livello sopra** a tutte le altre: non ripete il loro
lavoro, lo verifica a posteriori sull'intero archivio, indice Excel incluso.

- Non duplica `verifica-parti-gia-processate`: quella opera **prima** del
  flusso, per singolo PDF in ingresso in `Input/`, a fini di dedup. Il
  controllore opera **dopo**, su tutto l'archivio già esistente.
- Non duplica `archivia-in-processed`: quando trova un PDF in `Input/` ormai
  completo in tutte le sue parti, richiama semplicemente quella skill invece
  di reimplementarne la logica.
- Non duplica `lame-heat-index-excel`: non genera righe dell'indice con una
  logica propria, richiama quella skill per creare/aggiornare le righe
  mancanti o disallineate, così l'indice resta sempre prodotto con le stesse
  regole (stile, colonne, colonne di compilazione manuale mai toccate).
- Quando trova un buco o un'incoerenza, il controllore **non rielabora mai da
  capo** un PDF già archiviato correttamente: richiama la skill giusta e
  minima per sanare esattamente quel buco, oppure — se la riparazione è solo
  meccanica (es. ricopiare un file già esistente da una destinazione
  all'altra) — la esegue direttamente senza richiamare nessuna skill:
  - manca solo la seconda copia di un file già presente altrove → copia
    diretta del file, nessuna skill coinvolta;
  - manca una scheda in `Output/` per un certificato già archiviato →
    richiama `quality-steel` (e a seguire `archivia-certificati-materiale`
    se serve rimettere a posto anche l'archiviazione) solo su quel singolo
    certificato;
  - un PDF in `Input/` risulta completo in tutte le parti ma non ancora
    spostato → richiama `archivia-in-processed`;
  - manca o è disallineata una riga dell'indice Excel per un Heat già
    completamente archiviato → richiama `lame-heat-index-excel`.

## Controlli di coerenza da eseguire

Esegui, nell'ordine, tutti i controlli seguenti sull'intero albero della
cartella di lavoro.

### a. Doppia copia dei DDT

Ogni file in `DDT/<Anno>/<Mese>/<file>.pdf` deve avere una copia **identica**
(stesso nome) in `DDT/Fornitori/<Fornitore>/<file>.pdf`, e viceversa: sono lo
stesso documento salvato in doppia destinazione da `estrai-ddt-da-pdf`, non
due file diversi.

- Il fornitore atteso si deduce dal nome file stesso, che segue la
  convenzione `DDT <numero> - <Fornitore> - <gg.mm.aaaa>.pdf`.
- Se il file esiste da un lato e manca dall'altro, **copia** il file
  esistente nella destinazione mancante (operazione meccanica: mai
  rigenerare il DDT dal PDF sorgente originale, che potrebbe anche non
  essere più reperibile in `Input/`).
- Se il nome file non segue esattamente la convenzione attesa, o il
  fornitore sembra scritto in modo leggermente diverso, applica la
  gerarchia di evidenze sopra: se in `DDT/Fornitori/` esiste già una
  cartella riconducibile senza dubbio a quel fornitore, usa quella. Solo se
  restano due o più cartelle ugualmente plausibili e nessuna evidenza le
  distingue, applica comunque la più probabile e segnalala nel riepilogo.

### b. Scheda mancante per un certificato archiviato

Ogni certificato in `Acciaierie/<Azienda>/` o `Forgie/<Azienda>/` (nome file
`Certificato <numero> - <Azienda> - Colata <Heat>.pdf`) deve avere una scheda
corrispondente `Output/Scheda_Heat_<Heat>.pdf`.

- Se manca, il certificato originale è già disponibile in archivio: non
  serve tornare a `Input/`. Richiama `quality-steel` leggendo quel singolo
  PDF già archiviato per rigenerare solo la scheda mancante, poi verifica
  che finisca in `Output/` (vedi anche `archivia-certificati-materiale` se
  serve sistemare anche una struttura di cartelle incompleta).
- Non rigenerare mai schede già esistenti "per sicurezza": tocca solo gli
  Heat per cui la scheda risulta davvero assente.

### c. Scheda orfana

Ogni scheda `Output/Scheda_Heat_<Heat>.pdf` deve corrispondere ad almeno un
certificato realmente archiviato in `Acciaierie/` o `Forgie/` con quello
stesso Heat.

- Se nessun certificato archiviato ha quell'Heat con lo stesso nome atteso,
  cerca comunque — prima di arrenderti — un certificato il cui Heat compaia
  nel contenuto/nome con variazioni minime (es. zeri iniziali, spazi): se lo
  trovi, quella è l'ipotesi più probabile, usala per confermare la
  corrispondenza. Solo se davvero non esiste alcun certificato riconducibile
  a quell'Heat, segnala la scheda come orfana senza cancellarla: potrebbe
  essere l'unico caso in cui mancano dati sufficienti a un'azione sicura
  (il certificato potrebbe non essere mai stato archiviato).

### d. PDF ancora in Input completi ma non spostati

Per ogni PDF ancora presente in `Input/`, valuta con la stessa logica di
`verifica-parti-gia-processate` e `archivia-in-processed` se risulta
**interamente completo** in tutte le sue parti (DDT se presenti, certificati
con relative schede in `Output/`, riga indice Excel presente — controlli a,
b e f già verificati per quelle parti).

- Se risulta completo, richiama `archivia-in-processed` per spostarlo in
  `Processed/<Anno>/<Mese>/`.
- Se risulta incompleto, lascialo in `Input/` e segnala esattamente cosa
  manca ancora. Non è compito del controllore avviare l'estrazione dati da
  zero su un PDF mai processato: questa skill ripara solo le fasi di
  archiviazione/scheda/indice quando i dati sono già stati estratti altrove;
  se invece il PDF non è mai stato toccato dal flusso, segnalalo come "da
  lavorare da capo" e basta.

### e. Cartelle vuote o anomale

Segnala eventuali cartelle create per errore e rimaste vuote (es.
`Forgie/<Azienda>/` senza alcun file dentro), ma **non cancellarle** senza
conferma esplicita dell'utente: cancellare è un'azione irreversibile, non
un'ipotesi da applicare — qui vale l'eccezione della sezione "Filosofia".

### f. Indice Excel non aggiornato

Ogni Heat/Colata che risulta completamente archiviato (certificato in
`Acciaierie/` o `Forgie/`, scheda in `Output/Scheda_Heat_<Heat>.pdf`) deve
avere una riga corrispondente e aggiornata in
`Output/Indice_Heat_Certificati.xlsx`, con gli stessi dati e link della
scheda/dei documenti archiviati.

- Apri (senza riscriverlo da zero) `Indice_Heat_Certificati.xlsx` se esiste,
  e confronta per ciascun Heat archiviato la riga corrispondente (chiave:
  HEAT NUMBER, fallback LAME - HEAT CODE) con i dati attualmente in
  `Output/`, `Acciaierie/`, `Forgie/`, `DDT/Fornitori/`.
- Manca la riga per un Heat già archiviato → richiama `lame-heat-index-excel`
  per crearla.
- La riga esiste ma un campo non di compilazione manuale risulta vuoto o
  disallineato rispetto ai documenti già archiviati (es. link rotto,
  numero certificato diverso da quello del file realmente archiviato,
  colonna DATA/ANNO non coerente col DDT trovato):
  - se riesci a verificare con **assoluta certezza** che la riga si
    riferisce alla stessa colata/allo stesso documento già archiviato (es.
    stesso numero certificato, stessa azienda, stesso numero DDT — solo
    alcuni campi risultano stati aggiornati/corretti rispetto a quando la
    riga era stata scritta) → richiama `lame-heat-index-excel` per
    **aggiornare quella riga sul posto**, come un normale aggiornamento;
  - se invece resta un dubbio ragionevole che la riga esistente si riferisca
    a un documento diverso (stesso Heat Number ma dati non riconducibili con
    certezza allo stesso certificato/DDT) → **non sovrascriverla**: fai
    aggiungere a `lame-heat-index-excel` una **seconda riga** con lo stesso
    Heat Number per i dati corretti che hai trovato, lasciando intatta la
    riga preesistente, e segnala il caso nel riepilogo finale come
    possibile duplicato da verificare manualmente.
- Se il file `Indice_Heat_Certificati.xlsx` non esiste affatto ma ci sono
  Heat già completamente archiviati, richiama `lame-heat-index-excel` per
  crearlo da zero indicizzando tutte le schede già presenti in `Output/`.
- **Non toccare mai** le sei colonne di compilazione manuale (1A/2A PROVA,
  MEDIA), esattamente come prescritto da `lame-heat-index-excel`: questo
  controllo verifica solo le colonne popolate automaticamente.
- Se un link della riga punta a un file che risulta ancora mancante secondo
  i controlli a/b sopra, prima applica la riparazione di quel controllo (a
  o b), poi ricontrolla/aggiorna la riga Excel corrispondente — non
  aggiornare un link puntandolo a un file che non esiste ancora.

### Vincolo trasversale: file vs righe Excel in conflitto

- **File PDF**: se nella destinazione esiste già un file con lo stesso nome
  ma contenuto **realmente diverso** da quello che dovresti scrivere,
  fermati su quel singolo elemento e segnala il conflitto per verifica
  manuale, senza usare mai suffissi automatici tipo `(1)`, `(2)` e senza
  sovrascrivere nulla. Questo resta l'unico tipo di caso che il controllore
  lascia davvero in sospeso senza applicare nulla.
- **Righe dell'indice Excel**: mai lasciare un conflitto in sospeso senza
  agire. Se sei assolutamente certo che la riga in conflitto si riferisce
  alla stessa colata/allo stesso documento, **sovrascrivi** aggiornandola
  sul posto (vedi controllo f). Se non sei certo, **non sovrascrivere**:
  aggiungi una **seconda riga** con lo stesso Heat Number per i dati nuovi,
  senza toccare la riga preesistente, e segnala il possibile duplicato nel
  riepilogo finale. In nessun caso cancellare o fondere righe esistenti di
  tua iniziativa.

## Dove lavorare

Come le altre skill del plugin, funziona allo stesso modo qualunque sia
l'ambiente della cartella di lavoro:

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google Drive
  for Desktop, o cartella locale — tool `mcp__remote-devices__*`): verifica
  quale cartella è connessa con `get_device_info`. Il confronto tra le
  cartelle di destinazione per trovare le mancanze si fa **sempre** con un
  listing ricorsivo dell'intero albero (`device_list_dir` su `Input/`,
  `DDT/`, `Acciaierie/`, `Forgie/`, `Output/`, `Processed/`) — mai riaprendo
  o mettendo in staging i PDF già archiviati solo per controllarne
  l'esistenza: basta confrontare i nomi file. Per l'indice Excel, metti in
  staging solo `Output/Indice_Heat_Certificati.xlsx` (se esiste) per
  leggerne il contenuto con `openpyxl` nel workspace cloud e confrontarlo
  con quanto trovato nelle altre cartelle. Metti in staging (o leggi con
  `device_bash`) solo i file effettivamente coinvolti in una riparazione:
  una copia meccanica di file può essere fatta direttamente con `device_bash`
  (`cp`), mentre la rigenerazione di una scheda o di una riga Excel richiede
  di mettere in staging il singolo documento interessato per poterlo
  leggere/riscrivere nel workspace cloud.
- **Google Drive via API** (nessuna cartella sincronizzata sul computer —
  tipico di una schedulazione automatica giornaliera): usa
  `mcp__Google_Drive__*` — `search_files` per elencare ricorsivamente il
  contenuto di `DDT/`, `Acciaierie/`, `Forgie/`, `Output/`, `Input/`,
  `Processed/` e confrontare i nomi file, senza mai scaricare
  (`download_file_content`) i file già archiviati per il solo confronto;
  `create_file` per copiare un file mancante da una destinazione all'altra
  (Drive non ha un vero "copia": scarica il contenuto della copia esistente
  e ricrealo nella destinazione mancante, oppure usa la funzione di copia
  nativa se disponibile); `download_file_content` solo sui file che vanno
  effettivamente riletti per una riparazione (es. rigenerare una scheda o
  l'indice Excel).
- Se non è chiaro in quale ambiente si trovi la cartella di lavoro, applica
  comunque la logica della sezione "Filosofia": se l'ambiente è deducibile
  da come si sta già lavorando in questa conversazione, usa quello; chiedi
  conferma solo se non c'è alcun indizio a disposizione.

## Procedura

1. Elenca ricorsivamente l'intero albero della cartella di lavoro:
   `Input/`, `DDT/<Anno>/<Mese>/`, `DDT/Fornitori/<Fornitore>/`,
   `Acciaierie/<Azienda>/`, `Forgie/<Azienda>/`, `Output/` (inclusi
   `Scheda_Heat_*.pdf` e `Indice_Heat_Certificati.xlsx`), `Processed/`.
2. Esegui il controllo **a** (doppia copia DDT) su tutti i file trovati in
   `DDT/`: per ogni mancanza, applica la gerarchia di evidenze e copia il
   file nella destinazione mancante, applicando sempre l'ipotesi più
   probabile quando il nome non è netto.
3. Esegui il controllo **b** (schede mancanti) su tutti i certificati
   trovati in `Acciaierie/` e `Forgie/`: per ogni scheda mancante, richiama
   `quality-steel` sul certificato già archiviato per rigenerarla, poi
   verifica che sia comparsa in `Output/`.
4. Esegui il controllo **c** (schede orfane) su tutte le schede trovate in
   `Output/`.
5. Esegui il controllo **f** (indice Excel) per ogni Heat risultato
   completamente archiviato dopo i punti 2-3: richiama `lame-heat-index-excel`
   per creare o aggiornare le righe mancanti/disallineate.
6. Esegui il controllo **d** sui PDF ancora in `Input/`: per ognuno,
   determina se è completo (usando gli esiti già raccolti ai punti 2-5 per
   le sue parti) e, se sì, richiama `archivia-in-processed`; altrimenti
   annota cosa manca ancora.
7. Segnala il controllo **e** (cartelle vuote) trovate durante la
   ricognizione al punto 1.
8. Presenta all'utente un riepilogo strutturato in tre parti:
   - **Riparato automaticamente**: cosa mancava e come è stato colmato
     (file copiato da → a, scheda rigenerata per quale Heat, riga Excel
     creata/aggiornata per quale Heat, PDF spostato in Processed), incluse
     le ipotesi applicate nei pochi casi non del tutto netti (con una riga
     di motivazione per ciascuna).
   - **Lasciato in sospeso**: solo i veri conflitti irreversibili sui file
     PDF (contenuto diverso già presente) e le cartelle vuote anomale — con
     il dettaglio di cosa serve per sbloccarli. Le righe Excel in conflitto
     non rientrano qui: vanno elencate tra le riparazioni automatiche, con
     nota se sono state aggiornate sul posto o aggiunte come seconda riga da
     verificare.
   - **Tutto a posto**: se non è stato trovato nulla da riparare o
     segnalare, dichiaralo esplicitamente invece di restare silenzioso.

## Attenzione

- Non cancellare mai un file o una cartella di propria iniziativa: è
  l'unica azione davvero irreversibile, va sempre segnalata e confermata
  dall'utente.
- Su tutto il resto — nomi ambigui, fornitori scritti in modo leggermente
  diverso, corrispondenze non nettissime — **non fermarti**: applica la
  gerarchia di evidenze della sezione "Filosofia" e scegli l'ipotesi più
  probabile, segnalandola nel riepilogo finale invece di lasciarla in
  sospeso. L'obiettivo è che, a fine esecuzione, non restino casi ambigui
  irrisolti se non i veri conflitti di contenuto.
- Non rigenerare mai da zero un certificato o un'intera lavorazione se il
  dato di partenza (il PDF già archiviato) è sufficiente a colmare solo il
  buco specifico individuato: ogni riparazione deve essere la più piccola
  possibile.
- Non spostare mai in `Processed/` un file la cui completezza non è certa al
  100% in tutte le sue parti, indice Excel incluso.
- Non toccare mai le sei colonne di compilazione manuale dell'indice Excel
  (1A/2A PROVA, MEDIA): sono l'unico dato inserito a mano dal reparto
  Qualità.
- Non sovrascrivere mai un file PDF esistente con contenuto realmente
  diverso durante una riparazione: fermati e segnala il conflitto, come fa
  `archivia-in-processed`.
- Per le righe dell'indice Excel il vincolo è diverso: sovrascrivi sul posto
  solo se sei assolutamente certo che si tratti della stessa colata/dello
  stesso documento; altrimenti aggiungi una seconda riga con lo stesso Heat
  Number invece di sovrascrivere o di non fare nulla, e segnalala come
  possibile duplicato da verificare.
- Questa skill è pensata per essere **rieseguibile più volte senza effetti
  collaterali**: una seconda esecuzione su un archivio già coerente non deve
  trovare né modificare nulla, e va comunque riepilogata come "tutto a
  posto" invece di restare senza risposta.
