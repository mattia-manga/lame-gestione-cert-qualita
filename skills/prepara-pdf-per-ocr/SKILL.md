---
name: prepara-pdf-per-ocr
description: >-
  Rasterizza le pagine di un PDF in immagini PNG alla risoluzione ottimale
  per la lettura OCR/visiva di Claude, bilanciando accuratezza e consumo di
  token. Usa questa skill prima di leggere visivamente un PDF scansionato o
  di qualità incerta (testo piccolo, fotocopie, layer di testo assente o
  inaffidabile), sia come passo autonomo sia richiamata da altre skill del
  flusso certificati (quality-steel, estrai-ddt-da-pdf) quando il PDF di
  input non ha un layer di testo affidabile.
---

# Prepara PDF per OCR

## Perché

Quando Claude legge le pagine di un PDF come immagini, il costo in token è
circa proporzionale ai pixel dell'immagine (larghezza×altezza/750). Il
modello inoltre ridimensiona internamente ogni immagine il cui lato più
lungo supera ~1568px: renderizzare a una risoluzione più alta di quella
soglia spreca token senza migliorare l'accuratezza, perché l'immagine viene
comunque compressa prima dell'analisi. Il punto ottimale è quindi la
risoluzione più bassa che resta leggibile, non la più alta disponibile.

## Risoluzione consigliata

- **Default: 150 DPI.** Per un foglio A4 (210×297mm) o Letter, 150 DPI
  produce un'immagine di circa 1240×1754px — sotto la soglia di
  downscaling del modello, quindi nessun token sprecato — ed è sufficiente
  per la maggior parte dei certificati stampati.
- **200 DPI** solo se, dopo una prima lettura a 150 DPI, alcuni campi
  restano illeggibili (testo molto piccolo, fotocopie di scarsa qualità,
  annotazioni manoscritte sottili). Rigenera **solo le pagine
  problematiche** a risoluzione più alta, non l'intero documento.
- Evita di salire oltre 200 DPI: il guadagno di leggibilità è marginale
  rispetto al costo aggiuntivo, e il modello ridimensiona comunque.

## Procedura

1. **Verifica se serve rasterizzare.** Prova prima `pdftotext -layout
   input.pdf -` (vedi skill `pdf`). Se il PDF ha già un layer di testo
   completo e leggibile, spesso non serve rasterizzare: si può lavorare sul
   testo estratto o lasciare che il tool Read legga il PDF direttamente.
   Rasterizza solo se il testo è assente/inaffidabile, oppure se il
   documento contiene loghi o annotazioni manoscritte da leggere
   visivamente (es. forgia/acciaieria identificate da un logo, sigle
   scritte a mano).
2. **Rasterizza a 150 DPI:**
   ```
   pdftoppm -png -r 150 input.pdf pagina
   ```
   Esegui questo comando nell'ambiente dove si trova il PDF: nel workspace
   cloud se il file è stato caricato in chat o messo in staging da una
   cartella locale, oppure con `mcp__remote-devices__device_bash` se stai
   lavorando direttamente su file di una cartella collegata sul computer
   (vedi la sezione "Dove lavorare" della skill chiamante per i dettagli su
   staging/commit tra i due ambienti).
3. **Ispeziona le pagine generate** con il tool Read (disponibile solo nel
   workspace cloud — se stai lavorando su `device_bash`, metti prima in
   staging i PNG generati).
4. **Se un campo resta illeggibile**, rigenera solo quella pagina a 200
   DPI:
   ```
   pdftoppm -png -r 200 -f <numero_pagina> -l <numero_pagina> input.pdf pagina_hires
   ```
5. **Se anche a 200 DPI il dato resta incerto** (es. annotazione
   manoscritta poco chiara), non insistere con risoluzioni più alte: segui
   la regola delle skill chiamanti — chiedere conferma all'utente invece di
   indovinare.

## Nota per le skill che richiamano questa procedura

`estrai-ddt-da-pdf` e `quality-steel` richiamano questa skill come passo
preliminare quando il PDF di input è scansionato o di qualità incerta,
invece di applicare parametri di rasterizzazione diversi in ciascuna.

## Passo finale obbligatorio: controllore

Il controllo di coerenza `controllore` va richiamato sempre alla fine di ogni
skill del plugin — ma quando questa skill viene invocata come **passo
interno** di `estrai-ddt-da-pdf` o `quality-steel` (il caso più comune), non
richiamarlo qui: il passo obbligatorio è già previsto alla fine della skill
chiamante, e ripeterlo a metà del loro flusso sarebbe ridondante. Richiamalo
qui solo se questa skill è stata usata **come azione autonoma** richiesta
direttamente dall'utente (es. "rasterizza questo PDF"), e solo se è collegata
una cartella di lavoro strutturata su cui verificare qualcosa.
