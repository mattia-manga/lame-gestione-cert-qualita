---
name: esperto-materiali-metallurgici
description: >-
  Verifica se i valori di composizione chimica e proprietà meccaniche
  riportati in un certificato materiale (o già estratti in una scheda
  Output/Scheda_Heat_*.pdf da quality-steel) rispettano i limiti di norma per
  i gradi SA-105/A105N, SA-182 F5, SA-182 F11 Cl.1, SA-182 F11 Cl.2, SA-350
  LF2 Cl.1, SA-182 F316, SA-182 F316L, A694 F52, SA-182 F53. Usa SEMPRE
  questa skill quando l'utente chiede di verificare/controllare/validare la
  conformità di un materiale o di una colata alla norma, quando chiede quali
  sono i limiti chimici/meccanici ammessi per uno di questi gradi, o subito
  dopo che `quality-steel` ha estratto i dati di un Heat con uno di questi
  gradi, per segnalare eventuali valori fuori specifica prima di considerare
  la scheda definitiva.
---

# Esperto materiali metallurgici — restrizioni chimiche e meccaniche

## Scopo

Riferimento tecnico sui gradi materiale che LAME Srl riceve più di frequente.
Confronta i valori di composizione chimica di colata e di prove meccaniche —
letti da un certificato originale oppure già estratti da `quality-steel` in
una scheda `Output/Scheda_Heat_<Heat>.pdf` — con i limiti previsti dalla
norma di riferimento, e segnala ogni valore fuori range.

Non è una skill di estrazione: i valori numerici devono già essere
disponibili (dal PDF del certificato o da una scheda già generata). Non
sostituisce `quality-steel`, la completa con un controllo di conformità.

## Quando usarla

- L'utente chiede di verificare/controllare/validare la conformità di un
  materiale o di una colata a una norma ("è conforme questo A182 F11?",
  "controlla se questa colata rispetta i limiti chimici dell'A105").
- L'utente chiede quali sono i limiti chimici o meccanici ammessi per uno
  dei gradi coperti sotto, anche senza un certificato specifico da
  controllare.
- Subito dopo che `quality-steel` ha generato una scheda per un Heat il cui
  Grado Materiale rientra tra quelli coperti: prima di consegnare la scheda
  come definitiva, confronta i valori appena estratti con la tabella del
  grado corrispondente e segnala eventuali non conformità o dati mancanti
  richiesti dalla norma (es. prova d'urto assente su un LF2 Cl.1).
- Su richiesta di un controllo mirato sull'intero archivio già prodotto
  ("controlla se negli Heat già lavorati ci sono materiali fuori
  specifica"): in questo caso opera su tutte le schede
  `Output/Scheda_Heat_*.pdf`, con la stessa logica di `ricontrolla-ce-a105`
  (letture/scritture solo sui file coinvolti, mai un giro cieco su tutto
  l'archivio se non richiesto).

Se il Grado Materiale della scheda/certificato non rientra tra i gradi
coperti sotto, dillo esplicitamente: non improvvisare limiti per un grado
non documentato in questa skill.

## Dove lavorare

Stessa logica delle altre skill del plugin (vedi `quality-steel` per il
dettaglio): se il certificato è già in chat o nel workspace cloud, lavora
lì; se il flusso usa una cartella di lavoro locale/sincronizzata o Google
Drive, leggi le schede `Output/Scheda_Heat_*.pdf` e, se serve rileggere il
certificato originale (es. per un dato mancante), recuperalo da
`Acciaierie/<Azienda>/` o `Forgie/<Azienda>/` con gli stessi tool usati da
`ricontrolla-ce-a105` (`device_stage_files`/`mcp__Google_Drive__download_file_content`
solo sui file effettivamente coinvolti, mai l'intero archivio).

## Come riconoscere il grado in certificato/scheda

I certificati usano designazioni non uniformi: normalizza prima di cercare
nella tabella. Il campo Grado Materiale di `quality-steel` riporta la
designazione esattamente come scritta sul certificato originale, quindi
può comparire in forme diverse per lo stesso grado:

- "A105", "SA-105", "ASTM A 105" = stesso grado; la lettera "N" (A105N) NON
  cambia la chimica, indica solo che il pezzo è stato normalizzato
  (trattamento termico). Se il certificato non specifica la classe/il
  trattamento ma il cliente/ordine richiede A105N, verifica che nel
  certificato compaia "normalized"/"normalizzato" nel trattamento termico,
  non dedurlo dai soli valori chimici.
- "F11", "Gr. F11", "1.25Cr-0.5Mo" senza classe: la Classe (Cl.1 o Cl.2) si
  distingue dai valori meccanici (Cl.1 ha snervamento ~30 ksi/205 MPa, Cl.2
  ~40 ksi/275 MPa) o dal trattamento termico dichiarato. Se il certificato
  dichiara la classe, usa quella; altrimenti segnala l'ambiguità invece di
  scegliere a caso.
- "F316/F316L" doppia certificazione: il materiale deve rispettare i limiti
  più restrittivi di F316L (soprattutto C ≤0.030) per poter essere venduto
  come doppio grado; se il carbonio è tra 0.030 e 0.08 è valido solo come
  F316 semplice — segnalalo se la scheda riporta "F316/F316L" ma il C
  misurato è >0.030.
- "F53", "UNS S32750", "2507", "Super Duplex" = stesso grado.
- "A694 F52" può comparire anche come "ASME SA-694 Gr.F52".

## Tabelle di riferimento

Valori da specifica (limiti ammissibili); un certificato è conforme se OGNI
elemento chimico e OGNI proprietà meccanica riportata rientra nel range
indicato. Se un valore è fuori range, segnalalo esplicitamente come non
conformità (non arrotondare né "chiudere un occhio" su piccoli sforamenti).

### SA-105 / SA-105N — acciaio al carbonio per raccorderia forgiata
Chimica (%): C ≤0.35 · Mn 0.60–1.05 · P ≤0.035 · S ≤0.040 · Si 0.10–0.35 ·
Cu ≤0.40 · Ni ≤0.40 · Cr ≤0.30 · Mo ≤0.12 · V ≤0.08 ·
**Cu+Ni+Cr+Mo+V ≤1.00**
Meccanica: Rm ≥485 MPa (70 ksi) · Rp0.2 ≥250 MPa (36 ksi) · A ≥22% (provino
2in/50mm; 30% se provino ridotto per sezioni sottili — verifica quale usato)
· Z ≥30% · Durezza ≤197 HBW (alcuni PO per servizio sour richiedono
≤187 HBW: verifica sempre il PO, non solo la norma base)
Nota: A105 e A105N hanno gli stessi limiti chimici e meccanici; la
differenza è solo nel trattamento termico dichiarato.

### SA-182 F11 Cl.1 — 1.25Cr-0.5Mo (UNS K11597)
Chimica (%): C 0.05–0.15 · Mn 0.30–0.60 · P ≤0.030 · S ≤0.030 ·
Si 0.50–1.00 · Cr 1.00–1.50 · Mo 0.44–0.65
Meccanica: Rm ≥415 MPa (60 ksi) · Rp0.2 ≥205 MPa (30 ksi) · A ≥20% ·
Z ≥45% · Durezza 121–174 HBW

### SA-182 F11 Cl.2 — 1.25Cr-0.5Mo, bonificato
Chimica (%): C 0.10–0.20 · Mn 0.30–0.80 · P ≤0.040 · S ≤0.040 ·
Si 0.50–1.00 · Cr 1.00–1.50 · Mo 0.44–0.65
Meccanica: Rm ≥485 MPa (70 ksi) · Rp0.2 ≥275 MPa (40 ksi) · A ≥20% ·
Z ≥30% · Durezza 143–207 HBW

### SA-350 LF2 Cl.1 — C-Mn per bassa temperatura
Chimica (%): C ≤0.30 · Mn 0.60–1.35 · Si 0.15–0.30 (0.12 max se S4) ·
P ≤0.035 · S ≤0.040 · Ni ≤0.40 · Cr ≤0.30 · Mo ≤0.12 · Cu ≤0.40 · V ≤0.08 ·
Nb ≤0.02 (fino 0.05 per accordo). Restrizioni combinate: **Cr+Mo ≤0.32** ·
**Cu+Ni+Cr+Mo+V ≤1.00**
Meccanica: Rm 485–655 MPa (70–95 ksi) · Rp0.2 ≥250 MPa (36 ksi) · A ≥22%
(4D) / ≥30% (provino piatto 2in) · Z ≥30%
Impatto (obbligatorio, tipicamente CVN a −46 °C/−50 °F): media ≥20 J
(15 ft·lbf), minimo singolo ≥16 J (12 ft·lbf). Se il certificato non
riporta prove d'urto per un LF2 Cl.1, segnalalo: è quasi sempre richiesto.

### SA-182 F316
Chimica (%): C ≤0.08 · Mn ≤2.00 · P ≤0.045 · S ≤0.030 · Si ≤1.00 ·
Ni 10.0–14.0 · Cr 16.0–18.0 · Mo 2.00–3.00 · N ≤0.10
Meccanica: Rm ≥515 MPa (75 ksi) · Rp0.2 ≥205 MPa (30 ksi) · A ≥30% ·
Z ≥50%

### SA-182 F316L
Chimica (%): C ≤0.030 · Mn ≤2.00 · P ≤0.045 · S ≤0.030 · Si ≤1.00 ·
Ni 10.0–15.0 · Cr 16.0–18.0 · Mo 2.00–3.00 · N ≤0.10
Meccanica: Rm ≥485 MPa (70 ksi; ≥450 MPa/65 ksi per spessori >130 mm) ·
Rp0.2 ≥170 MPa (25 ksi) · A ≥30%

### A694 F52 — C-Mn alta resistenza (HSLA) per raccorderia grande diametro
Chimica: la norma A694 fissa limiti generali di specifica validi per tutti
i gradi (non limiti stretti per singolo grado): C ≤0.30 (tipicamente ≤0.22
per saldabilità) · Mn ≤1.60 · P ≤0.025 · S ≤0.025 · Si 0.15–0.35; altri
elementi (Cu, Ni, Cr, Mo, V, Cb, B) sono a discrezione del produttore e
vanno solo riportati, senza limite di norma — verifica sempre il PO per un
eventuale limite di Carbonio Equivalente (CE), spesso richiesto ≤0.43.
Meccanica: Rp0.2 ≥360 MPa (52 ksi) · Rm ≥455 MPa (66 ksi) · A ≥20%
Nota: per servizio sour molti PO richiedono durezza limitata (spesso
≤22 HRC / ≤237 HB): non è un limite della norma base A694, verificare
sempre il PO/spec cliente.

### SA-182 F53 — Super Duplex UNS S32750 / 2507
Chimica (%): C ≤0.030 · Mn ≤1.20 · P ≤0.035 · S ≤0.020 · Si ≤0.80 ·
Cr 24.00–26.00 · Ni 6.00–8.00 · Mo 3.00–5.00 · N 0.24–0.32 · Cu ≤0.50
PREN = %Cr + 3.3×%Mo + 16×%N — deve risultare ≥40; ricalcolalo sempre dai
valori di colata riportati invece di fidarti di un PREN eventualmente
scritto in certificato, e segnala discrepanze.
Meccanica: spessore ≤50 mm: Rm ≥800 MPa (116 ksi), Rp0.2 ≥550 MPa (80 ksi);
spessore >50 mm: Rm ≥730 MPa (106 ksi), Rp0.2 ≥515 MPa (75 ksi); A ≥15%;
Durezza ≤310 HBW (max). Per servizio sour (NACE MR0175/ISO 15156) spesso
richiesto ≤28 HRC: verificare PO.

### SA-182 F5 — 5Cr-0.5Mo
Chimica (%): C ≤0.15 · Mn 0.30–0.60 · P ≤0.030 · S ≤0.030 · Si ≤0.50 ·
Cr 4.00–6.00 · Mo 0.44–0.65
Meccanica: Rm ≥485 MPa (70 ksi) · Rp0.2 ≥275 MPa (40 ksi) · A ≥20% ·
Z ≥35% · Durezza 143–217 HBW

## Come applicarla

1. Identifica il grado materiale dichiarato (campo Grado Materiale della
   scheda, o designazione sul certificato) e normalizzalo secondo la
   sezione sopra per trovare la tabella corrispondente.
2. Per ogni elemento chimico riportato nella scheda/certificato, confronta
   con il range della tabella. Un elemento presente in scheda ma assente
   dalla tabella (es. elemento residuo) non è di per sé una non
   conformità, salvo che rientri in un vincolo combinato (es.
   Cu+Ni+Cr+Mo+V).
3. Per ogni proprietà meccanica riportata (Rm, Rp0.2, A%, Z%, durezza,
   energia d'urto), confronta con i minimi/massimi/range della tabella,
   convertendo le unità se necessario (ksi ↔ MPa: 1 ksi ≈ 6.895 MPa;
   ft·lbf ↔ J: 1 ft·lbf ≈ 1.356 J).
4. Elenca sempre TUTTI i valori fuori limite trovati (non fermarti al
   primo), indicando valore misurato, limite di norma e di quanto è fuori
   range.
5. Se un dato richiesto dalla norma (es. prova d'urto per LF2 Cl.1, PREN
   per F53) manca dalla scheda/certificato, segnalalo come dato mancante,
   non presumere conformità.
6. Se la classe/il grado non è determinabile con certezza dai dati
   disponibili, dillo esplicitamente invece di scegliere la tabella più
   permissiva.
7. Presenta il risultato come riepilogo: **Conforme** (nessuno scostamento
   trovato), **Non conforme** (elenco puntuale degli scostamenti), o **Dati
   insufficienti** (grado non riconosciuto o valori chiave mancanti per
   poter concludere).
8. Questa skill non modifica le schede `Output/Scheda_Heat_*.pdf`: si
   limita a segnalare le non conformità. Se una correzione della scheda si
   rende necessaria (es. dato riletto più a fondo su un certificato), segui
   lo stesso schema di `ricontrolla-ce-a105` (rigenerare con
   `scripts/genera_scheda_heat.py` di `quality-steel`, sovrascrivere lo
   stesso file in `Output/`) solo se l'utente lo richiede esplicitamente.

Questi limiti riflettono le edizioni più diffuse di ASTM/ASME A105, A182,
A350, A694 note al momento della stesura; se un certificato cita
un'edizione specifica della norma o un requisito di capitolato/PO più
restrittivo, quel documento prevale sui valori qui riportati.
