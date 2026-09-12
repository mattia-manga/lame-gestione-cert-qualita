---
name: archivia-certificati-materiale
description: Archivia i certificati materiale (forgia/acciaieria) estratti da PDF misti in cartelle Acciaierie/Azienda e Forgie/Azienda, e tiene le schede di quality-steel in Output. Lo spostamento finale del PDF sorgente da Input è gestito dalla skill archivia-in-processed.
---

# Archiviazione certificati forgia/acciaieria e schede Heat

## Quando usare questa skill

Usala quando l'utente ha già chiesto (o chiede contestualmente) di applicare `quality-steel` a dei PDF di certificati materiale misti, e vuole che oltre alla scheda riepilogativa per Heat/Colata vengano archiviati anche **i documenti originali** (le pagine di certificato non elaborate), smistati per azienda produttrice. Frasi tipiche: "archivia anche i certificati originali", "smista i certificati in una cartella acciaierie e una forgie", "metti gli output della skill in una cartella Output e i documenti di partenza divisi per fornitore".

Questa skill NON legge né interpreta i dati tecnici dei certificati (composizione chimica, proprietà meccaniche): quella parte resta compito esclusivo di `quality-steel`. Questa skill si occupa della fase successiva di **archiviazione file**: dove salvare cosa, e quando spostare il sorgente.

## Relazione con le altre skill

- Va usata DOPO (o subito insieme a) `quality-steel`: quella skill identifica le pagine di certificato nel PDF, decide per ciascuna se è forgia o acciaieria (vedi le sue regole di disambiguazione: campo "Heat Code" presente → quasi sempre forgia; un'unica pagina/certificato totale → acciaieria di default, tipico quando il fornitore è un distributore/rivenditore es. "Papani Acciai", "Ro.La.Fer"; ecc.) e genera una scheda PDF (`Scheda_Heat_<HeatNumber>.pdf`) per ciascun Heat/Colata. Questa skill riprende quella stessa classificazione pagina-per-pagina già fatta e la usa solo per decidere in quale cartella archiviare il documento originale.
- Se lo stesso PDF contiene anche pagine di DDT (Documento di Trasporto), quelle vanno gestite dalla skill `estrai-ddt-da-pdf`, non da questa.
- Questa skill NON sposta il PDF sorgente fuori da `Input/`: quel passo finale, verso `Processed/YYYY/MM/`, è compito della skill `archivia-in-processed`, da usare solo dopo che tutte le altre fasi (DDT se pertinente, quality-steel, archiviazione qui descritta) sono concluse.

## Convenzione cartelle di lavoro

- I PDF sorgente (certificati misti da elaborare) si trovano sempre nella cartella `Input/`.
- Questa skill non sposta il PDF sorgente da `Input/`: se ne occupa `archivia-in-processed`, una volta che tutte le fasi del flusso (DDT, quality-steel, archiviazione) sono state completate.

## Dove lavorare

Questa skill funziona allo stesso modo su una cartella di lavoro locale/sincronizzata, su Google Drive raggiunto via API, o su file caricati direttamente in chat:

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google Drive for Desktop, o cartella locale — tool `mcp__remote-devices__*`): verifica quale cartella è connessa con `get_device_info`, o chiedi all'utente di collegarla se manca. Leggere/estrarre pagine PDF (`qpdf`) può essere fatto lato cloud dopo aver messo in staging i file sorgente (`device_stage_files`); crea le cartelle e riporta i file estratti sul computer con `SendUserFile` + `device_commit_files` (una chiamata per ciascuna destinazione), oppure crea/sposta cartelle e file direttamente con `device_bash`. Questa skill non tocca mai `Input/<file>.pdf`: lo spostamento del sorgente è compito di `archivia-in-processed`.
- **Google Drive via API** (nessuna cartella sincronizzata sul computer — tipico di una schedulazione automatica): usa `mcp__Google_Drive__*` — `search_files` per verificare se `Acciaierie/<Azienda>/`, `Forgie/<Azienda>/` o `Output/` esistono già, `create_file` per caricarci i documenti estratti e le schede. OneDrive non ha un connettore dedicato in questo plugin: se la cartella è OneDrive non sincronizzata localmente, chiedi all'utente di sincronizzarla o di indicare un'alternativa.
- **File caricati direttamente in chat**: lavora nel workspace cloud e consegna gli estratti con `SendUserFile`; se una cartella di lavoro è comunque collegata (locale o Google Drive), riportali anche lì nelle destinazioni sotto con `device_commit_files` o i tool Google Drive.
- Se non è chiaro in quale ambiente si trovi la cartella di lavoro di questa conversazione, chiedi conferma prima di procedere invece di indovinare.

## Procedura

1. Se non è già stato fatto in questa conversazione, applica (o richiama i risultati di) `quality-steel` sui PDF indicati (attesi in `Input/`): per ciascuna pagina/certificato individuato servono numero certificato, azienda (nome come appare in intestazione/logo), ruolo (forgia o acciaieria), Heat/Colata, e l'intervallo di pagine nel file sorgente a cui corrisponde.
2. Raggruppa le pagine che appartengono allo stesso certificato (un certificato può occupare più pagine consecutive, es. pagina dati tecnici + pagina dichiarazioni di conformità): vanno estratte insieme come un unico PDF.
3. Determina il nome della cartella azienda con le stesse regole di normalizzazione già usate per i fornitori nella skill DDT: il nome come appare nell'intestazione/logo del certificato, **senza forma societaria** (togli "S.p.A.", "Srl", "SpA", "S.n.c.", i punti nelle sigle) — es. "RO.LA.FER. S.p.A." → "Rolafer", "ACCIAIERIE BERTOLI SAFAU SpA" → "Acciaierie Bertoli Safau", "RIVA ACCIAIO S.p.A." → "Riva Acciaio", "FORG.MAES. S.n.c." → "Forgmaes". Se il nome è ambiguo o poco leggibile, chiedi conferma prima di creare la cartella.
4. Estrai le pagine del certificato come PDF a sé stante con `qpdf "input.pdf" --pages . <da>-<a> -- "output.pdf"`. Nome file suggerito: `Certificato <numero senza caratteri non validi> - <Azienda> - Colata <Heat>.pdf`. Se più certificati distinti condividono la stessa colata (es. stesso getto ridotto a diametri diversi), aggiungi un suffisso distintivo tra parentesi (es. "(Diam.32)", "(Diam.38)") così ogni certificato resta un file separato anche se la colata è la stessa.
5. Crea — solo se effettivamente necessaria — la cartella di destinazione:
   - `Acciaierie/<Azienda>/` se la pagina è stata classificata come acciaieria;
   - `Forgie/<Azienda>/` se la pagina è stata classificata come forgia.
   Crea ciascuna cartella (Acciaierie, Forgie, e le relative sottocartelle azienda) solo quando esiste almeno un certificato di quel tipo da archiviarci: **non creare `Forgie/` "per simmetria" se nel set di PDF analizzato non compare nessun certificato di forgia**, anche se il prodotto finale è un forgiato — in quel caso il nome della forgia va solo annotato nel campo "Forgia" della scheda corrispondente in `quality-steel` (con una nota che spiega che non ha emesso certificato proprio), non archiviato come documento qui.
6. Salva il PDF estratto nella cartella determinata al punto 5. Se `Acciaierie/...` o `Forgie/...` esistono già con una convenzione diversa (nomi cartella diversi, struttura diversa), rispetta quella esistente invece di crearne una parallela.
7. Le schede riepilogative generate da `quality-steel` (`Scheda_Heat_<...>.pdf`) vanno **tutte insieme in un'unica cartella `Output/`** (crearla se non esiste), separata da `Acciaierie/` e `Forgie/` e senza suddivisione per azienda: `Output/` contiene solo gli elaborati (le schede), mai i documenti originali; `Acciaierie/` e `Forgie/` contengono solo i documenti originali (le pagine di certificato non elaborate), mai le schede. Se `quality-steel` è stato eseguito solo in chat e le schede non risultano ancora in `Output/`, riportacele prima di procedere (vedi "Dove lavorare").
8. Non spostare il PDF sorgente da `Input/`: quando tutte le fasi del flusso sono complete (DDT se pertinente, quality-steel, archiviazione qui descritta), passa la mano alla skill `archivia-in-processed`, che verifica le condizioni e sposta il file in `Processed/YYYY/MM/`.
9. Riepiloga all'utente: quali certificati sono stati trovati (numero, azienda, colata, pagine del file sorgente) e dove sono stati archiviati (percorso Acciaierie/Forgie), dove sono state salvate le schede (Output), e quali cartelle sono state create ex novo. Dichiara le convenzioni di naming usate e invita l'utente a correggerle se ne preferisce altre. Se il flusso è concluso, ricorda che il passo finale di spostamento del sorgente spetta ad `archivia-in-processed`.
10. **Passo finale obbligatorio**: richiama **sempre** la skill `controllore` (se è collegata una cartella di lavoro strutturata, locale o Google Drive) per verificare la coerenza dell'archivio dopo l'archiviazione appena fatta, prima di considerare concluso questo passo — non è facoltativo, anche se questa skill è stata usata come passo isolato. Se il file proviene da chat senza nessuna cartella di lavoro collegata, non c'è archivio da controllare: salta questo passo.

## Attenzione

- Non generare né modificare le schede PDF qui: se mancano dati tecnici o la classificazione forgia/acciaieria non è ancora stata fatta, è compito di `quality-steel`, non di questa skill.
- Non creare cartelle vuote "per simmetria" (es. `Forgie/` senza nessun certificato di forgia da mettere dentro).
- Non mescolare mai schede ed originali nella stessa cartella: `Output/` = elaborati, `Acciaierie/`+`Forgie/` = originali.
- Non spostare mai il PDF sorgente da `Input/` in questa skill: quel passo è compito esclusivo di `archivia-in-processed`, da eseguire solo a flusso interamente concluso.
- Se un'azienda o un numero di certificato non è leggibile con certezza, chiedi conferma piuttosto che indovinare.
- **Non duplicare mai file già elaborati**: prima di (ri)estrarre un certificato o rigenerare una scheda, verifica se esiste già un file equivalente nelle cartelle di destinazione (`Acciaierie/`, `Forgie/`, `Output/`) — se il PDF sorgente risulta già archiviato in `Processed/`, è già stato lavorato per intero e non va ritoccato.
