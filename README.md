# LAME - Quality Certificate Management

A plugin for LAME Srl's Quality Department: automates processing of PDFs that arrive with incoming goods (rough drums/forgings, rounds, bars, tubes...), when these PDFs mix together several document types: DDT (Transport Document), mill test certificates (3.1/3.2, EN 10204) and, when present, forging certificates.

## What it does

The plugin exposes seven skills:

1. **`verifica-parti-gia-processate`** — preliminary step: checks whether the Input PDF contains parts (DDT, forging certificate, mill certificate) already archived in a previous incomplete run or from another file, and produces a plan that limits the subsequent skills' work to only the missing parts — avoiding reprocessing an entire file from scratch just because it was left partially in `Input/`.
2. **`prepara-pdf-per-ocr`** — rasterizes the pages of a scanned or uncertain-quality PDF at the optimal resolution (default 150 DPI) before visual reading, balancing OCR accuracy against token usage. Called as a preliminary step by `estrai-ddt-da-pdf` and `quality-steel` when needed.
3. **`estrai-ddt-da-pdf`** — finds the actual DDT pages within the mixed PDF (not simple references/stamps) and archives them by year/month and by supplier.
4. **`quality-steel`** — identifies material certificate pages (forging and/or mill), groups them by Heat/Cast, and extracts general data, chemical composition, and mechanical properties for each into a summary PDF sheet.
5. **`archivia-certificati-materiale`** — picks up the forging/mill classification already done by `quality-steel`, extracts the original certificate pages as standalone PDF documents and archives them by manufacturer, and keeps the generated sheets in a single folder.
6. **`archivia-in-processed`** — final step of the flow: verifies that all previous phases completed without errors and, only then, moves the source PDF from `Input/` to `Processed/YYYY/MM/` (year/month of completed processing).
7. **`controllore`** — a posteriori consistency check across the entire archive, including the Excel index: verifies that every file (and every row of `Output/Indice_Heat_Certificati.xlsx`) has all its expected copies/derivatives in all destination folders (e.g. a DDT present in `DDT/<Year>/<Month>/` but missing from its copy in `DDT/Fornitori/<Supplier>/`) and autonomously repairs any gaps found — calling the right skill for those that require reprocessing (e.g. `quality-steel` for a missing sheet, `lame-heat-index-excel` for a missing or misaligned index row, `archivia-in-processed` for a complete PDF not yet moved) — resolving not-entirely-clear cases with the most likely hypothesis instead of stopping, and truly leaving pending only irreversible conflicts (different content already present). **This is a mandatory step, not optional**: it must run automatically at the end of each of the other six skills (each one calls it as its own last step when a structured working folder is connected) and again at the close of the entire flow, as well as on explicit request.

The first six skills are complementary and don't overlap: the first checks what's already been done, the second prepares images for reading, the third handles only DDT, the fourth only reads/extracts technical data, the fifth only archives documents/sheets, the sixth only handles the final move of the source. `verifica-parti-gia-processate` is always first (when applicable), `archivia-in-processed` is always last in the per-single-PDF flow, since it depends on the completion of all the others. `controllore` sits at a level above all of them: it's not a step in the per-single-PDF flow, but a check — mandatory, not an optional extra — on the entire archive already produced, run after each skill and at the close of the flow, to catch and fix right away any inconsistencies the normal flow may have left behind (interrupted runs, missing copies, orphaned sheets, misaligned Excel index).

## Supported working environments

All skills work the same way, regardless of the environment the working folder (`Input/`, `DDT/`, `Acciaierie/`, `Forgie/`, `Output/`, `Processed/`) lives in:

- **Local folder or folder synced on the user's computer** — including a OneDrive or Google Drive folder synced with the desktop client, which from the plugin's point of view is indistinguishable from a local folder: the skills use the connected computer's tools (`mcp__remote-devices__*`, in particular `device_bash`, `device_stage_files`, `device_commit_files`).
- **Google Drive reached only via API**, with no computer connected — the typical case of a daily automatic schedule that analyzes the `Input/` folder on Drive: the skills use the `mcp__Google_Drive__*` tools (`search_files`, `download_file_content`, `create_file`, `update_file`) and, to move a file, update its parent folder instead of doing an `mv`.
- **Files uploaded directly in chat**, with no folder connected: the skills work in the cloud workspace and deliver results with `SendUserFile`.

**OneDrive has no dedicated API connector in this plugin.** It's supported only when the folder is synced to the user's computer via the OneDrive desktop client (falling under the first case above, like any local folder). If a OneDrive folder isn't synced locally and needs to be reached via API, a dedicated connector would need to be added.

If it's not clear which of these environments the conversation's working folder is in, each skill asks for confirmation before proceeding instead of guessing.

## Resulting folder structure

Starting from a shared working folder (e.g. the Quality Department's folder, local or on Drive/OneDrive), the flow produces this structure:

```
<working folder>/
├── Input/                          # Source PDFs to process (mixed certificate scans + DDT)
├── DDT/
│   ├── <Year>/<Month>/             # DDTs found, organized by year and month
│   └── Fornitori/<Supplier>/       # same DDT, also organized by supplier
├── Acciaierie/<Company>/           # original mill certificates, by company
├── Forgie/<Company>/               # original forging certificates, by company (only if present)
├── Output/                         # summary sheets Scheda_Heat_<Heat>.pdf generated by quality-steel
└── Processed/<Year>/<Month>/       # source PDFs, moved here once all flow phases are complete
```

Important rules applied by the skills:

- A `DDT` or a certificate can span several consecutive pages: they are always extracted together as a single PDF.
- Company/supplier folder names are normalized by stripping the legal form (S.p.A., Srl, S.n.c., dots in abbreviations) — e.g. "RO.LA.FER. S.p.A." → `Rolafer`, "FORG.MAES. S.n.c." → `Forgmaes`.
- `Forgie/` is created only if the analyzed PDF set actually contains at least one forging certificate — not for symmetry with `Acciaierie/`.
- `Output/` contains only the generated sheets (the processed outputs); `Acciaierie/` and `Forgie/` contain only the original documents; they must never be mixed.
- A source PDF is moved from `Input/` to `Processed/<Year>/<Month>/` only after all relevant phases have been completed on it without errors (this check and the move are always the responsibility of `archivia-in-processed`, never the other skills). If a phase is missing, the file stays in `Input/`.
- No file is ever duplicated, either as a whole document or as a single part: if a source PDF is already in `Processed/`, it has already been fully processed. If instead it remains in `Input/` with only some parts (DDT, forging, mill) already archived — typically because a previous run stopped halfway — `verifica-parti-gia-processate` identifies which parts are already present in `DDT/`, `Acciaierie/`, `Forgie/` and `Output/` and has the subsequent skills reprocess only the missing ones.
- In case of ambiguous or hard-to-read data (supplier, date, certificate number, cast), the skills ask for confirmation instead of guessing.

## How to use it

Just ask in natural language, for example:

- "Check if this PDF has already been partly processed" / "avoid redoing parts already done" → `verifica-parti-gia-processate`
- "Analyze the PDFs in Input and archive the DDTs" → `estrai-ddt-da-pdf`
- "Extract the material certificate data from these PDFs" → `quality-steel`
- "Archive the original certificates too" → `archivia-certificati-materiale`
- "Archive/move/close this already processed document" → `archivia-in-processed`
- "Check that the archive is all in order" / "verify nothing is missing, Excel included" → `controllore`

or ask directly for the complete flow ("process these PDFs in Input from start to finish") and the skills will be applied in sequence, with `verifica-parti-gia-processate` as the first step (to avoid reworking already archived parts) and `archivia-in-processed` as the final step.

## Technical requirements

The skills rely on common command-line tools (`pdfinfo`, `pdftotext`, `pdftoppm`, `qpdf`) and, for `quality-steel`, on the Python script included in `skills/quality-steel/scripts/genera_scheda_heat.py` (requires the `reportlab` package). Google Drive via API requires the `Google Drive` connector to be connected; a local or synced folder (OneDrive/Google Drive for Desktop) requires a computer connected via the Claude desktop app.
