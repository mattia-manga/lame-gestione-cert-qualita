---
name: archivia-in-processed
description: "Sposta il documento sorgente da Input a Processed/YYYY/MM (anno/mese di elaborazione completata) SOLO quando l'intero workflow di elaborazione documentale (quality-steel, classificazione pagine, archiviazione DDT/certificati forgia/acciaieria, generazione schede Heat) è concluso senza errori. È sempre l'ultimo passo del flusso: usala quando l'utente chiede di archiviare, spostare, o 'chiudere' un documento già elaborato, o quando hai appena completato tutte le fasi previste su un file di Input e devi decidere se/dove spostarlo."
---

# Archiviazione file elaborati in Processed

## Scopo

Gestisce l'archiviazione finale dei documenti presenti nella cartella `Input/` dopo il completamento del processo di elaborazione documentale. Il documento va spostato in `Processed/YYYY/MM/`, organizzato per anno e mese di elaborazione completata.

Questa skill **non modifica il contenuto del documento** e **non esegue** estrazione, classificazione o analisi tecnica: quella parte resta compito di `quality-steel`, `estrai-ddt-da-pdf` ed `archivia-certificati-materiale`.

## Relazione con le altre skill del flusso

Questa skill è l'**ultimo passo** della sequenza sullo stesso PDF sorgente:

1. `estrai-ddt-da-pdf` (se il file contiene pagine DDT)
2. `quality-steel` (estrazione dati, generazione schede Heat)
3. `archivia-certificati-materiale` (smistamento certificati originali in Acciaierie/Forgie e schede in Output)
4. **questa skill** — sposta il PDF sorgente ormai completamente lavorato da `Input/` a `Processed/YYYY/MM/`

## Condizione di esecuzione

Esegui lo spostamento da `Input/` a `Processed/` **solo se tutte** le condizioni seguenti sono vere:

- l'elaborazione `quality-steel` è terminata;
- le pagine del documento sono state correttamente classificate;
- DDT, certificati di forgia e certificati di acciaieria sono stati archiviati nelle rispettive cartelle previste;
- eventuali schede Heat previste sono state generate (e si trovano in `Output/`, non solo come allegati di chat);
- non risultano errori o condizioni che richiedano una verifica manuale.

Se anche una sola fase manca o il processo non è concluso correttamente, **il documento deve restare in `Input/`** (o essere gestito dal processo previsto per i documenti da verificare) — non spostarlo, e segnala all'utente cosa manca.

## Dove lavorare

Questa skill funziona allo stesso modo su una cartella di lavoro locale/sincronizzata (usata da un computer collegato) e su Google Drive raggiunto via API (tipico di una schedulazione automatica giornaliera senza computer collegato):

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google Drive for Desktop, o cartella locale — tool `mcp__remote-devices__*`): verifica quale cartella è connessa con `get_device_info`. Usa `device_bash` per creare le directory mancanti (`mkdir -p`) e spostare il file con `mv`, oppure `device_stage_files`/`device_commit_files` se il lavoro passa dal workspace cloud.
- **Google Drive via API** (nessuna cartella sincronizzata sul computer): usa `mcp__Google_Drive__*` — `search_files` per verificare l'esistenza di `Processed/<anno>/` e `Processed/<anno>/<mese>/`, `create_file` per crearle se mancanti, e `update_file` per spostare il file sorgente aggiornandone il parent (non esiste un vero "mv": lo spostamento su Drive è un cambio di cartella padre, non una copia+cancellazione). OneDrive non ha un connettore dedicato in questo plugin: se la cartella è OneDrive non sincronizzata localmente, chiedi all'utente di sincronizzarla o di indicare un'alternativa.
- Se non è chiaro in quale ambiente si trovi la cartella `Input/` di questa conversazione, chiedi conferma prima di procedere invece di indovinare.

## Regola di archiviazione

```text
Processed/
└── YYYY/
    └── MM/
```

- `YYYY` = anno, `MM` = mese a due cifre.
- Anno e mese corrispondono alla **data in cui l'elaborazione del documento è stata completata** (di norma la data odierna in cui esegui questo passo), salvo diversa regola definita dal processo.

Esempio: documento elaborato correttamente in data 11/09/2026 →
`Input/Documento.pdf` diventa `Processed/2026/09/Documento.pdf`.

## Procedura

1. Verifica che tutte le condizioni di esecuzione elencate sopra siano soddisfatte. In caso contrario fermati e segnala cosa manca, senza spostare nulla.
2. Determina anno e mese di elaborazione completata (di norma la data odierna).
3. Verifica se esistono già `Processed/<anno>/` e `Processed/<anno>/<mese>/`. Crea automaticamente le cartelle mancanti (anche entrambe, se manca pure quella dell'anno).
4. Controlla se nella cartella di destinazione esiste già un file con lo stesso nome:
   - se è identico al documento da archiviare, non duplicarlo (considera lo spostamento già avvenuto);
   - se è diverso, **interrompi lo spostamento** e segnala il conflitto per verifica manuale — non usare mai suffissi automatici come `(1)`, `(2)`.
5. Sposta il file da `Input/` a `Processed/<anno>/<mese>/` mantenendo **invariati** nome e contenuto del documento (nessuna rinomina automatica, salvo diversa istruzione esplicita).
6. Verifica che il file sia effettivamente presente nella cartella di destinazione prima di considerare lo spostamento concluso e il file rimosso da `Input/`.
7. Riepiloga all'utente: quale file è stato spostato, il percorso finale (`Processed/YYYY/MM/...`), quali cartelle sono state create ex novo, ed eventuali conflitti segnalati.
8. **Passo finale obbligatorio**: richiama **sempre** la skill `controllore`, senza eccezioni — questa skill è l'ultimo passo del flusso per-singolo-PDF, quindi è anche il punto in cui il controllo di coerenza sull'intero archivio è più utile, incluso l'indice Excel. Non è facoltativo, anche se lo spostamento è appena stato bloccato per un conflitto al punto 4: in quel caso il controllore serve comunque a verificare che il resto dell'archivio sia a posto.

## Attenzione

- Non spostare mai un documento la cui elaborazione non sia certificata come completa in tutte le sue fasi.
- Non sovrascrivere mai un file esistente in `Processed/`: identico → salta, diverso → blocca e segnala.
- Non usare suffissi automatici (`(1)`, `(2)`, ecc.) per risolvere conflitti di nome.
- Non rinominare il documento durante lo spostamento.
- Non creare cartelle `Processed/<anno>/<mese>/` per mesi/anni diversi da quello di elaborazione effettiva, "per sicurezza" o in anticipo.
- Usa sempre `Processed/YYYY/MM/` come destinazione finale del flusso, mai una cartella diversa creata ad hoc.
