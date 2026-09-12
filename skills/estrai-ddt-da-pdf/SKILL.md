---
name: estrai-ddt-da-pdf
description: Trova le pagine DDT (Documento di Trasporto) dentro PDF di certificati/collaudo misti e le archivia in DDT/Anno/Mese e DDT/Fornitori/Fornitore.
---

# Estrazione DDT da PDF misti

## Quando usare questa skill

Usala quando l'utente chiede di analizzare una cartella (o dei PDF) contenenti certificati materiale/collaudo che possono includere anche pagine di DDT (Documento di Trasporto), e vuole che le pagine DDT vengano individuate, estratte e archiviate in cartelle per anno/mese e per fornitore. Frasi tipiche: "trova i DDT in questi PDF e archiviali", "estrai il documento di trasporto da questo certificato", "organizza i DDT di questa cartella".

Se l'utente vuole estrarre i dati tecnici (Heat/Colata, composizione chimica, proprietà meccaniche) da certificati materiale, quella è la skill `quality-steel`: le due possono essere usate in sequenza sullo stesso set di PDF ma fanno cose diverse, non vanno confuse.

## Contesto tipico

I file sono spesso PDF scansionati (nessun layer di testo) che mescolano certificati di collaudo (3.1/3.2), rapporti di prova e — a volte — 1-2 pagine di vero DDT (intestazione tipo "DOCUMENTO DI TRASPORTO D.P.R. 472 del 14/08/96", spesso con barcode/QR in alto). Molti certificati citano un numero di DDT solo come riferimento o timbro (es. "RIF. D.d.T. N° ...") senza contenere la pagina originale: quello NON va estratto, va solo segnalato.

## Dove lavorare

Questa skill funziona allo stesso modo su una cartella di lavoro locale, su una cartella sincronizzata via client desktop (OneDrive, Google Drive for Desktop), su Google Drive raggiunto solo via API, o su file caricati direttamente in chat:

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google Drive for Desktop, o cartella locale — tool `mcp__remote-devices__*`): verifica quale cartella è connessa con `get_device_info`, o chiedi all'utente di collegarla se manca. Leggere visivamente le pagine PDF richiede il tool Read, disponibile solo nel workspace cloud: metti quindi in staging i PDF (`device_stage_files`), lavora su di essi nel workspace cloud, poi crea le cartelle mancanti e riporta gli estratti sul computer con `SendUserFile` + `device_commit_files` (una chiamata per ciascuna delle due destinazioni), oppure sposta/organizza direttamente con `device_bash`.
- **Google Drive via API** (nessuna cartella sincronizzata sul computer — tipico di una schedulazione automatica senza computer collegato): usa i tool `mcp__Google_Drive__*` — `search_files` per individuare la cartella di lavoro e verificare se `DDT/<Anno>/<Mese>/` o `DDT/Fornitori/<Fornitore>/` esistono già, `download_file_content` per leggere i PDF, `create_file` per caricare gli estratti nelle cartelle giuste (creandole prima se mancanti). OneDrive non ha un connettore dedicato in questo plugin: se la cartella indicata è OneDrive e non risulta sincronizzata localmente, chiedi all'utente di sincronizzarla o di indicare un'alternativa raggiungibile.
- **File caricati direttamente in chat**: lavora nel workspace cloud e consegna gli estratti con `SendUserFile`; se una cartella di lavoro è comunque collegata (locale o Google Drive), riportali anche lì con `device_commit_files` o i tool Google Drive, così le altre skill del flusso li trovano nella struttura prevista.
- Se non è chiaro in quale ambiente si trovi la cartella di lavoro di questa conversazione, chiedi conferma prima di procedere invece di indovinare.

## Procedura

0. Se la skill `verifica-parti-gia-processate` è già stata eseguita su
   questo PDF e ha prodotto un piano con gli intervalli di pagina delle
   parti DDT ancora da elaborare, limita i passi seguenti **solo a quelle
   pagine**: non riesaminare né riestrarre i DDT già segnalati come
   archiviati. Se non è disponibile nessun piano di questo tipo, procedi
   normalmente sull'intero PDF.
1. Elenca i PDF nella cartella indicata (ricorsivo se serve).
2. Per ciascun PDF, controlla il numero di pagine (`pdfinfo`) e prova `pdftotext -layout` per vedere se ha un layer di testo. Se è vuoto o scarso (scansione), usa la skill `prepara-pdf-per-ocr` per rasterizzare le pagine alla risoluzione corretta, poi ispezionale con Read, una per una o a piccoli gruppi.
3. Riconosci le pagine DDT dall'intestazione "DOCUMENTO DI TRASPORTO" e/o "AVVISO DI SPEDIZIONE / PACKING LIST" (spesso con barcode in alto a destra). Un DDT può occupare più pagine consecutive (es. pagina di continuazione con lo stesso numero/data in testata): includile tutte nello stesso estratto. Per ciascun DDT trovato annota: numero documento, data (gg/mm/aaaa), fornitore/mittente (intestazione in alto del documento, non il destinatario), intervallo pagine nel file sorgente.
4. Estrai le pagine come PDF a sé stante con `qpdf "input.pdf" --pages . <da>-<a> -- "output.pdf"` (vedi skill `pdf` per altre opzioni). Nome file suggerito: `DDT <numero senza caratteri non validi> - <Fornitore> - <gg.mm.aaaa>.pdf`, sostituendo `/` o altri caratteri non ammessi nei nomi file con `-`.
5. Determina i nomi delle cartelle:
   - Anno: il numero a 4 cifre (es. `2026`), non "Anno 2026".
   - Mese: nome del mese in italiano con iniziale maiuscola (Gennaio…Dicembre).
   - Fornitore: il nome dell'azienda come appare nell'intestazione del DDT, senza forma societaria (togli "S.p.A.", "Srl", "SPA", punti nelle sigle) — es. "Acciaierie Valbruna S.p.A." → "Acciaierie Valbruna", "RO.LA.FER. SPA" → "Rolafer". Se il nome è ambiguo, chiedi conferma prima di creare la cartella.
6. Crea le cartelle mancanti per `DDT/<Anno>/<Mese>/` e `DDT/Fornitori/<Fornitore>/` (vedi "Dove lavorare" per gli strumenti da usare a seconda dell'ambiente). Se `DDT/...` esiste già con una convenzione diversa, rispetta quella esistente invece di crearne una parallela.
7. Salva il PDF estratto in entrambe le destinazioni (stesso file, due percorsi).
8. Riepiloga all'utente: quali DDT sono stati trovati (numero, data, fornitore, file sorgente e pagine), dove sono stati archiviati, e quali file NON contenevano un DDT vero (solo citazioni/timbri). Dichiara le convenzioni di naming usate e invita l'utente a correggerle se ne preferisce altre.
9. **Passo finale obbligatorio**: richiama **sempre** la skill `controllore` (se è collegata una cartella di lavoro strutturata, locale o Google Drive) per verificare la coerenza dell'archivio dopo l'archiviazione appena fatta, prima di considerare concluso questo passo — non è facoltativo, anche se questa skill è stata usata come passo isolato. Se il file proviene da chat senza nessuna cartella di lavoro collegata, non c'è archivio da controllare: salta questo passo.

## Attenzione

- Non inventare un DDT se non è presente nel PDF: le sole citazioni/timbri non contano.
- Se fornitore o data non sono leggibili con certezza, chiedi conferma piuttosto che indovinare.
