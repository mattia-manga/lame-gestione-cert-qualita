---
name: quality-steel
description: >-
  Estrae dati da certificati materiale (forgia e/o acciaieria) di prodotti
  metallici (tondi, gomiti, tubi, barre) presenti in PDF che possono
  contenere anche DDT (documenti di trasporto) e altre pagine non
  pertinenti. Genera una scheda PDF riepilogativa per ogni Heat/Colata
  trovata, con dati generali, composizione chimica e proprietà meccaniche.
  Usa SEMPRE questa skill quando l'utente carica un PDF con certificati di
  collaudo, certificati acciaieria o certificati forgia (anche in inglese:
  certificate of inspection, test certificate, mill certificate), quando
  menziona Heat Number, Heat Code, Colata, certificato 3.1 o EN 10204,
  oppure quando chiede di estrarre dati da certificati materiale, anche
  senza usare esplicitamente la parola certificato (es. estrai i dati di
  questo PDF, fammi la scheda di questo materiale).
---

# QualitySteel — Estrazione dati da Certificati Materiale (Forgia / Acciaieria)

## Scopo

A partire da un PDF che contiene una o più pagine di certificati materiale
(più eventualmente DDT e altre pagine non pertinenti), produrre **una scheda
PDF per ogni Heat/Colata individuata**, con dati generali, composizione
chimica e proprietà meccaniche.

## Panoramica del workflow

1. Identificare tutte le pagine pertinenti (certificati forgia e/o acciaieria) e scartare il resto (DDT, fatture, bolle).
2. Raggruppare le pagine per Heat/Colata e classificare ciascuna come Forgia o Acciaieria.
3. Estrarre i dati generali, chimici e meccanici per ciascun Heat, applicando le regole di disambiguazione riportate sotto.
4. Generare una scheda PDF per ciascun Heat con lo script `scripts/genera_scheda_heat.py`.
5. Se un dato è incerto, ambiguo o dipende da una lettura poco chiara (annotazioni manoscritte, loghi, OCR incerto, campioni multipli in conflitto), **chiedere conferma all'utente prima di generare il PDF**, invece di indovinare. Meglio una domanda in più che un dato sbagliato in scheda.

## Dove lavorare

I PDF di certificati da analizzare possono arrivare da un file caricato in chat, da una cartella locale/sincronizzata sul computer, o da Google Drive raggiunto via API:

- **Cartella locale o sincronizzata sul computer** (OneDrive, Google Drive for Desktop, o cartella locale — tool `mcp__remote-devices__*`): verifica quale cartella è connessa con `get_device_info`. Leggere visivamente le pagine PDF richiede il tool Read, disponibile solo nel workspace cloud: metti in staging i certificati (`device_stage_files`), genera le schede nel workspace cloud, poi riportale nella cartella di lavoro con `SendUserFile` + `device_commit_files`, oppure con `device_bash` se il file è già stato scaricato sul computer.
- Se un certificato è scansionato o di qualità incerta (testo piccolo, fotocopia, layer di testo assente/inaffidabile), usa la skill `prepara-pdf-per-ocr` per rasterizzare le pagine alla risoluzione corretta prima di leggerle, invece di affidarti alla resa di default del tool Read.
- **Google Drive via API** (nessuna cartella sincronizzata sul computer): usa `mcp__Google_Drive__*` (`download_file_content` per leggere i certificati, `create_file` per caricare le schede generate). OneDrive non ha un connettore dedicato in questo plugin: se la cartella è OneDrive non sincronizzata localmente, chiedi all'utente di sincronizzarla o di indicare un'alternativa.
- **File caricati direttamente in chat**: lavora nel workspace cloud e consegna le schede con `SendUserFile`.
- Se nella conversazione è già in uso una cartella di lavoro condivisa (locale o Google Drive) con la struttura di questo plugin, salva/riporta sempre anche lì le schede generate, nella cartella `Output/` (vedi sezione 8): è lì che `archivia-certificati-materiale` si aspetta di trovarle per il passo successivo del flusso, evitando che restino solo come allegati di chat.

## 0. Se arriva già un piano da `verifica-parti-gia-processate`

Se la skill `verifica-parti-gia-processate` è già stata eseguita su questo
PDF e ha prodotto un piano con gli intervalli di pagina delle parti forgia/
acciaieria ancora da elaborare, limita l'identificazione e l'estrazione
**solo a quelle pagine**: non riclassificare né rileggere le parti già
segnalate come archiviate, e non rigenerare le relative schede Heat (già
presenti in `Output/`). Se non è disponibile nessun piano di questo tipo,
procedi normalmente sull'intero PDF come descritto sotto.

## 1. Identificazione delle pagine rilevanti

Cercare le pagine che contengono un campo **"Heat N°"**, **"Heat Number"**,
**"Colata"** o equivalenti — è il segnale che identifica una pagina di
certificato materiale (forgia o acciaieria). Scartare DDT, fatture, bolle di
accompagnamento e fogli riepilogativi interni del cliente (vedi punto 7).

### Disambiguazione Forgia vs Acciaieria

- Pagina con campo **"Heat Code"** (o equivalente per funzione, es. "Ns.
  sigla" — vedi punto 2) → è quasi sempre la **forgia**.
- Pagina con **solo Heat Number**, senza Heat Code → è la **acciaieria**.
- Se c'è **una sola pagina/certificato totale** → è considerata acciaieria di
  default (tipico quando il fornitore è un distributore/rivenditore, es.
  "Papani Acciai", "Ro.La.Fer", e non un forgiatore).
- Se ci sono più di 2 pagine candidate → applicare la stessa regola a
  ciascuna.
- Per i tubi senza saldatura (seamless tube), il produttore del tubo
  (acciaieria) può fondere e lavorare direttamente la colata: in questo caso
  non esiste una forgia separata.

## 2. Dati generali da estrarre

| Campo | Note |
|---|---|
| Heat Code | Se assente sul certificato, default = Heat Number. **Prima di dare per scontato che sia assente**, controllare: (a) campi equivalenti per funzione anche se con nome diverso (es. "Ns. sigla"); (b) **annotazioni manoscritte** sul DDT o sul certificato (es. sigle tipo "RL-HB", "TL-GS") — spesso rappresentano il vero Heat Code interno e vanno usate al posto del default. |
| Heat Number | — |
| Product | Descrizione articolo. Preferibilmente da DDT quando presente, incrociando per Heat Number/Colata (**attenzione**: un DDT può avere più righe/articoli con Heat diversi — abbinare sempre la riga corretta, mai prendere la prima disponibile). Se il DDT non è disponibile, usare la descrizione/profilo del certificato. |
| Forgia | Spesso è un logo, non testo → leggerlo come immagine per estrarne il nome. Lasciare vuoto se non presente (nessuna nota tipo "non presente"). |
| Acciaieria | Sempre presente; anche qui spesso logo → stessa logica di lettura visiva. |
| Grado Materiale | Riportare la designazione **esattamente come scritta sul certificato originale** (es. "A105", "F316", "F11 CL.3", "Grade 6 ASTM A333/A333M-24; X52 PSL1", "X2CrNiMo17-12-2/1.4404 Type 316L"), anche se estesa. Non semplificare. |
| Numero certificato | Se presenti sia forgia sia acciaieria: formato `[N. acciaieria] - [N. forgia]` (es. acciaieria 554, forgia 32 → **554-32**). Se presente solo acciaieria (nessuna forgia): riportare solo il numero acciaieria, senza trattino. |
| Data certificato acciaieria | Dalla pagina identificata come acciaieria (di solito data di emissione/firma del certificato). |

## 3. Proprietà chimiche (%)

Estrarre quando presenti: **C, Mn, P, S, Si, Cr, Ni, Mo, Ti, Cu, Nb, Co, V,
CE, N, Al, Ca, B**.

- **CE (Carbonio Equivalente)**: può comparire con nomi diversi a seconda del
  certificato — "CE", "CEV", "Exp.4", "C EQ. LONG FORMULA" — sono
  concettualmente equivalenti, usare il valore trovato.
- **Unità non standard**: se un elemento è riportato in **ppm** invece che in
  **%** (es. "N/ppm: 58"), convertire sempre in percentuale dividendo per
  10.000 (58 ppm = 0,0058%). Non lasciare mai il valore in ppm nella scheda.

## 4. Proprietà meccaniche

Campi: **Elongation, Reduction of Area, Yield Strength (Snervamento),
Tensile Strength (Rottura), Hardness (HBW), Impact Test (resilienza)**. Per i
tubi, in aggiunta: **Hydraulic Test, Bending Test**.

### Regole fondamentali

- **Fonte dati**: le proprietà meccaniche vanno **sempre e solo dal
  certificato di FORGIA**, mai dall'acciaieria — **a meno che** sia presente
  solo il certificato di acciaieria (nessuna forgia), nel qual caso si usano
  quelle dell'acciaieria.
- **Yield Strength**: usare sempre il valore **Rp0,2%** quando disponibile
  (non Rp1% o altri).
- **Campioni multipli sulla stessa colata**: quando il certificato riporta
  più campioni/provini con set di valori diversi per la stessa colata:
  1. Identificare il campione con lo **Yield Strength più basso**.
  2. Riportare in scheda **tutti** i valori (Yield, Tensile, Elongation,
     Reduction of Area) di **quello stesso campione**, coerentemente.
     **Non mischiare mai** il valore minimo di proprietà diverse presi da
     campioni diversi (es. Yield minimo da un campione ed Elongation minima
     da un altro: SBAGLIATO).
  3. Indicare tra parentesi il criterio usato, es. "418 N/mm² (min su 4
     campioni)".
- **Impact Test / resilienza (valori KV multipli)**: quando il certificato
  riporta più letture KV per lo stesso provino/test (tipicamente 3 valori),
  NON riportare solo il minimo. Riportare **tutti e tre i valori**, separati
  da spazio, seguiti dall'unità e dalla temperatura di prova **una sola
  volta in coda** (quando la temperatura è la stessa per tutte le letture,
  caso più comune), nel formato `<valore1> <valore2> <valore3> J <temp>` —
  es. "42 45 38 J -20°C". **Non** ripetere l'unità o la temperatura dopo
  ogni singolo valore. Se invece le letture hanno temperature di prova
  diverse tra loro, riportare ogni coppia valore/temperatura separatamente
  nello stesso ordine, es. "42 J -20°C, 45 J -40°C, 38 J -20°C".
  Questo è un caso diverso dai campioni multipli su colate diverse (vedi
  sopra): qui le letture appartengono allo stesso test/provino, quindi si
  riportano tutte, non se ne sceglie una.
- **Hardness**: se il certificato riporta più valori di durezza (es. "in
  pelle" e "sul provino"), preferire il valore che coincide anche con
  l'eventuale certificato di forgia collegato, se disponibile. Se non è
  presente una vera misura di durezza (solo un limite/requisito, es. "HRC
  max 22"), lasciare il campo vuoto — non riportare un requisito come se
  fosse un valore misurato.
- **Hydraulic Test** (solo tubi): riportare l'esito dal certificato
  originale se presente (es. "API 5L, 5 sec, 20,5 MPa — superato (100%)").
- **Bending Test** (solo tubi): se il certificato riporta un test
  concettualmente equivalente ma con nome diverso (es. "Flattening Test /
  Prova di schiacciamento") con esito positivo, riportare semplicemente
  **"OK"** nel campo Bending Test.

## 5. Campi mancanti

Ogni campo (generale, chimico o meccanico) non trovato nel certificato o non
determinabile con certezza deve comparire **come spazio vuoto** nella scheda
finale — mai testo tipo "N/A", "non presente" o simili. Questo permette
all'utente di distinguere a colpo d'occhio un dato assente da un dato
recuperato.

**Attenzione particolare**: se Heat Code è vuoto per assenza di annotazioni
o campi equivalenti, ricordarsi comunque di applicare la regola di default
(Heat Code = Heat Number) prima di generare il PDF finale — non lasciarlo
vuoto per errore.

## 6. Priorità tra fonti in caso di conflitto

Quando lo stesso dato compare in più punti del PDF con valori diversi
(tipicamente: certificato originale del produttore vs. foglio riepilogativo
interno del cliente, es. "Stampa colate"), **il certificato originale ha
sempre priorità**. I fogli riepilogativi interni vanno ignorati per i valori
tecnici — possono però essere utili per confermare la mappatura Heat Code ↔
Heat Number.

Errori sistematici osservati nei fogli riepilogativi interni da tenere a
mente (non fidarsi ciecamente):
- Campo "Material type"/Grado Materiale non coerente con lo standard
  tecnico indicato nel certificato originale (es. riepilogo indica "A106
  Gr.B" mentre il certificato dice "A333 Gr.6/X52 API 5L" — standard
  diversi con proprietà diverse).
- Campo "Hardness" che in realtà contiene valori di **resilienza/Impact
  Test (KV)** travasati per errore, mentre il campo "Impact test" resta
  vuoto. Se si nota questo pattern, ricostruire i dati corretti dal
  certificato originale.

## 7. Annotazioni manoscritte

Sigle manoscritte su DDT o certificati (es. "RL-HB", "RL-HDV", "TL-GS")
rappresentano tipicamente il vero **Heat Code** interno del cliente e vanno
riportate come tali, **non ignorate**. Altri numeri manoscritti isolati
(es. possibili conversioni di unità fatte a mano, spunte, timbri di
controllo) sono generalmente irrilevanti. In caso di dubbio sulla lettura di
un'annotazione manoscritta (grafia poco chiara), **chiedere conferma
all'utente** prima di usarla, mostrando la lettura tentativa.

## 8. Generazione della scheda PDF

Usare lo script `scripts/genera_scheda_heat.py`, che espone la funzione
`crea_scheda_heat(dati, output_path)`. Il dizionario `dati` ha tre chiavi
principali — `generali`, `chimiche`, `meccaniche` — più una chiave opzionale
`tubo` (solo se il prodotto è un tubo, con `Hydraulic Test` e `Bending
Test`). Vedere il blocco `if __name__ == "__main__":` nello script per lo
schema completo dei campi attesi.

Workflow pratico:

1. Copiare `scripts/genera_scheda_heat.py` nella working directory (o
   importarlo direttamente se già presente).
2. Costruire un dizionario `dati` per ciascun Heat individuato nel PDF,
   applicando tutte le regole sopra.
3. Chiamare `crea_scheda_heat(dati, "/mnt/user-data/outputs/Scheda_Heat_<HeatNumber>.pdf")`
   per ciascun Heat.
4. Consegnare tutti i PDF generati all'utente con `SendUserFile`.
5. Se questa conversazione lavora già su una cartella condivisa (locale o
   Google Drive) con la struttura del plugin, riportare le stesse schede
   anche in `Output/` di quella cartella (vedi "Dove lavorare" sopra), così
   `archivia-certificati-materiale` le trova già al loro posto invece di
   doverle recuperare dalla chat.

Se un PDF di input contiene più Heat (es. un unico DDT con più colate, o un
certificato con più tubi/colate distinte), generare **una scheda separata
per ciascun Heat**, mai una scheda cumulativa.

## 9. Checklist finale prima di generare il PDF

- [ ] Ho identificato correttamente forgia vs acciaieria per ogni pagina?
- [ ] Ho verificato annotazioni manoscritte per un possibile vero Heat Code?
- [ ] Se Heat Code è vuoto, l'ho impostato uguale a Heat Number?
- [ ] Il Product è stato abbinato alla riga corretta del DDT (per Heat/Colata)?
- [ ] Il Grado Materiale viene dal certificato originale, non da un riepilogo interno?
- [ ] Le proprietà meccaniche vengono dalla forgia (o dall'acciaieria solo se la forgia non esiste)?
- [ ] Se c'erano più campioni, ho usato lo stesso campione (quello con Yield minimo) per tutti i valori collegati?
- [ ] Eventuali valori in ppm sono stati convertiti in %?
- [ ] I campi non trovati sono vuoti, non "N/A" o simili?
- [ ] In caso di dubbio/ambiguità reale, ho chiesto conferma prima di generare il PDF?

## 10. Passo finale obbligatorio: controllore

Dopo aver generato e consegnato le schede, se questa conversazione lavora su
una cartella di lavoro strutturata (locale o Google Drive), richiama
**sempre** la skill `controllore` per verificare la coerenza dell'archivio —
passo obbligatorio, non facoltativo, anche se questa skill è stata usata come
passo isolato. Se i PDF provengono solo da chat senza nessuna cartella di
lavoro collegata, non c'è archivio da controllare: salta questo passo.
