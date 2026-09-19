---
name: ricontrolla-ce-a105
description: >-
  Ricontrolla, su tutto l'archivio già elaborato, le schede Heat
  (`Output/Scheda_Heat_*.pdf`) dei materiali con Grado Materiale A105: per
  ciascuna verifica che il campo chimico CE (Carbonio Equivalente) sia
  valorizzato. Se è vuoto, rilegge più a fondo il certificato originale già
  archiviato (Acciaierie/Forgie), cercando CE anche sotto nomi alternativi
  (CEV, Exp.4, CEQ, C EQ. LONG FORMULA) o rileggendolo a risoluzione più alta,
  e rigenera la scheda sostituendo il file precedente in Output. Usa SEMPRE
  questa skill quando l'utente chiede di ricontrollare/verificare il CE (o
  "carbonio equivalente") sui materiali A105 già lavorati, o di correggere
  schede A105 con CE mancante.
---

# Ricontrolla CE sui materiali A105 già archiviati

## Scopo

Passata correttiva a posteriori, mirata: sui materiali con **Grado Materiale
A105** già completamente elaborati dal flusso `quality-steel` (scheda già
presente in `Output/`), verifica che il campo chimico **CE (Carbonio
Equivalente)** sia valorizzato. Per l'acciaio A105 il CE è un dato che deve
sempre comparire sul certificato: **se risulta vuoto in scheda, nella grande
maggioranza dei casi non è perché il certificato non lo riporta, ma perché è
sfuggito in una prima estrazione** (nome di campo non standard, tabella
secondaria, OCR incerto). Questa skill non si accontenta del campo vuoto come
farebbe `quality-steel` su un dato genuinamente assente: rilegge il
certificato più a fondo prima di arrendersi.

Questa skill **non** rielabora l'intera scheda né ridecide dati già corretti
(Heat Code, Product, proprietà meccaniche, altri elementi chimici): tocca
**solo** il campo CE e solo quando risulta vuoto.

## Quando usarla

Su richiesta esplicita: "ricontrolla il CE degli A105", "verifica che i
materiali A105 abbiano il carbonio equivalente valorizzato", "controlla se
manca il CE sulle schede A105 e correggile", "gli A105 in Output hanno tutti
il CE?". Non fa parte del flusso automatico per-singolo-PDF (non viene
richiamata da `quality-steel` o dal `controllore`): è un controllo mirato,
da lanciare quando serve, sull'intero archivio già prodotto.

## Ambito: tutto l'archivio, non un singolo PDF

Come `controllore`, opera su tutta la cartella `Output/`, non su un
documento alla volta.

## Dove lavorare

Stessa logica delle altre skill del plugin:

- **Cartella locale o sincronizzata sul computer** (tool
  `mcp__remote-devices__*`): verifica quale cartella è connessa con
  `get_device_info`. Elenca `Output/` con `device_list_dir`. Per rileggere
  visivamente un certificato serve il tool Read, disponibile solo nel
  workspace cloud: metti in staging con `device_stage_files` solo i file
  effettivamente coinvolti (la scheda da ricontrollare e il/i certificato/i
  originale/i corrispondenti), mai l'intero archivio. Riporta la scheda
  rigenerata con `SendUserFile` + `device_commit_files` (stesso nome file,
  `force: true`, così sovrascrive quella precedente).
- **Google Drive via API** (nessuna cartella sincronizzata): usa
  `mcp__Google_Drive__*` — `search_files` per elencare `Output/`,
  `Acciaierie/`, `Forgie/`; `download_file_content` solo sui file coinvolti
  in una correzione; `update_file` per sovrascrivere la scheda in `Output/`
  con lo stesso nome.
- Se non è chiaro l'ambiente della cartella di lavoro, chiedi conferma prima
  di procedere invece di indovinare.

## Procedura

### 1. Individuare le schede A105

Elenca tutte le schede `Output/Scheda_Heat_*.pdf`. Per ciascuna, leggi il
campo **Grado Materiale**: seleziona quelle in cui compare "A105" (anche con
suffisso, es. "A105", "A105 Gr.2", "A105N") — confronto sul testo esatto
riportato in scheda, non solo una corrispondenza esatta della stringa
"A105" isolata.

Se nessuna scheda ha Grado Materiale A105, segnalalo e concludi: non c'è
nulla da controllare.

### 2. Verificare il campo CE su ciascuna scheda A105 selezionata

Nella sezione "Composizione chimica" della scheda, controlla il valore di
**CE**. Due casi:

- **CE valorizzato** → nessuna azione, passa alla scheda successiva
  (conteggiala in "Già a posto" nel riepilogo finale).
- **CE vuoto** → aggiungi questo Heat alla lista da correggere (passo 3).

### 3. Rileggere il certificato originale per ogni Heat con CE vuoto

Per ciascun Heat Number con CE vuoto:

1. Individua il/i certificato/i originale/i già archiviati per quell'Heat:
   cerca in `Acciaierie/<Azienda>/Certificato ... - Colata <Heat>*.pdf` e in
   `Forgie/<Azienda>/Certificato ... - Colata <Heat>*.pdf` (nome file secondo
   la convenzione di `archivia-certificati-materiale`). Se esistono sia
   acciaieria sia forgia, controlla entrambi: la composizione chimica può
   comparire sull'uno o sull'altro a seconda del certificato.
2. Se il certificato è scansionato o di qualità incerta (o la prima lettura
   potrebbe essere stata compromessa da questo), usa `prepara-pdf-per-ocr`
   per rileggerlo a risoluzione più alta prima di procedere, invece di
   fidarti della resa di default.
3. Rileggi **l'intero certificato**, non solo la tabella di composizione
   chimica principale: cerca il valore di CE anche in tabelle secondarie,
   note a piè pagina, o accanto a formule di calcolo. Il campo può comparire
   sotto nomi diversi — cercali tutti prima di concludere che sia assente:
   **CE, CEV, Exp.4, CEQ, C EQ. LONG FORMULA, C.E., CE (IIW)**, ed eventuali
   varianti testuali equivalenti (es. "Carbon Equivalent", "Equiv. Carbonio").
   Se il valore è in **ppm** invece che in %, convertilo dividendo per
   10.000, come da regola generale di `quality-steel`.
4. **Se trovi il valore**: vai al passo 4 (correzione).
5. **Se, dopo aver riletto l'intero certificato (comprese eventuali pagine
   aggiuntive) e provato tutti i nomi alternativi sopra, il CE risulta
   davvero non presente**: **non trattarlo come un campo genuinamente
   assente e non lasciarlo vuoto in silenzio** — a differenza della regola
   generale di `quality-steel` sui campi mancanti, per l'A105 l'assenza del
   CE è considerata un'anomalia da segnalare, non un dato normale. Aggiungi
   questo Heat alla lista "Da verificare manualmente" del riepilogo finale,
   indicando che è stato riletto a fondo (certificati controllati, nomi
   alternativi cercati) senza trovare il dato, e lascia la scheda esistente
   invariata (non rigenerarla senza un valore da inserire).

### 4. Correggere la scheda quando il CE viene trovato

Per ogni Heat per cui il passo 3 ha trovato il valore di CE:

1. Recupera tutti gli altri dati già corretti per quell'Heat leggendo la
   scheda `Output/Scheda_Heat_<Heat>.pdf` esistente (dati generali,
   composizione chimica già presente esclusa CE, proprietà meccaniche): non
   ri-estrarli da capo dal certificato, per non rischiare di alterare dati
   già validati che non sono oggetto di questa correzione.
2. Copia `scripts/genera_scheda_heat.py` (dalla skill `quality-steel` del
   plugin) nella working directory, o importalo se già presente. Costruisci
   il dizionario `dati` con le tre chiavi `generali`, `chimiche`,
   `meccaniche` (più `tubo` se pertinente), identico all'esistente tranne il
   campo `CE` in `chimiche`, ora valorizzato.
3. Rigenera il PDF con `crea_scheda_heat(dati, "Scheda_Heat_<Heat>.pdf")`
   nel workspace cloud.
4. **Sostituisci il file precedente in `Output/`**: stesso nome file
   (`Scheda_Heat_<Heat>.pdf`), nessun suffisso — riporta il file rigenerato
   nella cartella di lavoro sovrascrivendo quello esistente (`force: true`
   su `device_commit_files`, oppure `update_file` su Google Drive).
5. Annota nel riepilogo finale: Heat corretto, valore di CE trovato, e su
   quale certificato/campo era stato individuato (utile per capire perché
   era sfuggito la prima volta).

### 5. Riepilogo finale

Presenta all'utente un riepilogo in tre parti:

- **Corretti**: Heat per cui il CE era vuoto ed è stato trovato e inserito,
  con il valore e la fonte (nome campo sul certificato, es. "trovato come
  'CEV' sul certificato acciaieria n. ...").
- **Già a posto**: quanti A105 avevano già il CE valorizzato (solo il
  conteggio, non serve dettagliarli uno per uno).
- **Da verificare manualmente**: Heat A105 per cui, nonostante la rilettura
  approfondita, il CE non è stato trovato su nessun certificato archiviato —
  con l'elenco dei certificati controllati, così l'utente può verificare a
  mano se manca davvero sul documento originale o se il certificato
  archiviato è incompleto.

Se non c'era nulla da correggere (tutti gli A105 avevano già il CE), dichiaralo esplicitamente invece di restare silenzioso.

## Attenzione

- Tocca **solo** il campo CE: non modificare altri elementi chimici, dati
  generali o proprietà meccaniche già presenti in scheda, anche se notassi
  possibili imprecisioni — non è l'oggetto di questa skill.
- Non rigenerare mai una scheda per cui il CE era già valorizzato, anche se
  il valore ti sembra sospetto: questa skill corregge solo campi vuoti.
- Non inventare né stimare un valore di CE: se dopo la rilettura approfondita
  non lo trovi scritto sul certificato, segnalalo in "Da verificare
  manualmente", non lasciare la scheda con un valore indovinato.
- Non spostare né rinominare i PDF dei certificati originali in
  `Acciaierie/`/`Forgie/`: questa skill li rilegge soltanto.
- Dopo aver rigenerato una o più schede, valuta di richiamare `controllore`
  se sono stati toccati file in `Output/`: verifica che l'indice Excel non
  faccia riferimento a dati disallineati (l'indice non ha comunque una
  colonna CE, quindi in genere non richiede aggiornamenti da questa
  correzione, ma è comunque il passo che chiude in coerenza ogni modifica
  all'archivio).
