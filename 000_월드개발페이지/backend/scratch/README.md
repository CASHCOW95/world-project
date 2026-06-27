# Scratch Scripts

`scratch` contains ad hoc research and maintenance scripts. These scripts are not part of the web app runtime or the deploy build.

## Active Scratch

- `analyze_sung_srt.py`: analyzes `backend/research/coin/sung` subtitle source material and writes reports to `scratch/output`.
- `test_cleaner.py`: tests subtitle cleanup against one sample source file and writes outputs to `scratch/output`.
- `rewrite_books_*.py`, `clean_all_existing_subs.py`: research/book-generation utilities for source material under `backend/research/coin`.

## Local Outputs

- `input/`: local sample files moved out of `backend`.
- `output/`: generated reports and test outputs.

Both folders are ignored by git.

## Legacy

- `legacy_migration/`: one-off folder rename/move scripts from an earlier repository structure.
- `legacy_local/`: scripts with old machine-specific absolute paths, including legacy PDF/book generation utilities.

Review paths before running anything in the legacy folders.
