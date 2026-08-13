# SOURCE

What is in this directory, where it came from, and what was changed.
Read this before trusting any number in here.

## kcc_extract.csv

Real data. Kisan Call Centre transcripts of farmers' queries and
answers, Ministry of Agriculture and Farmers Welfare, published on
data.gov.in.

- Resource ID: `cef25fe2-9231-4128-8aec-2c948fedd43f`
- Landing page: https://www.data.gov.in/resource/kisan-call-centre-kcc-transcripts-farmers-queries-answers
- API: `https://api.data.gov.in/resource/cef25fe2-9231-4128-8aec-2c948fedd43f`
- Records here: 360
- Filtered to StateName = TELANGANA and these districts:
  KAMAREDDY (90), WARANGAL (90), WARANGAL RURAL (90), NIRMAL (90)
- License: Government Open Data License - India
  https://www.data.gov.in/government-open-data-license-india

Modifications: column headers were re-cased inconsistently, a small
fraction of cells were blanked, and rows were filtered by district.
Query and answer text is unmodified.

## pesticide_labels.csv

Real data. Extracted from "MAJOR USES OF PESTICIDES (Registered under
the Insecticides Act, 1968)", Central Insecticide Board & Registration
Committee, Directorate of Plant Protection, Quarantine & Storage,
Ministry of Agriculture & Farmers Welfare, edition **upto
01/06/2023**.

- Source PDF: https://web.archive.org/web/20231019064956/https://ppqs.gov.in/sites/default/files/1._major_use_of_pesticides_insecticides_as_on_01.06.2023.pdf
- The official host, ppqs.gov.in, returns HTTP 403 to all traffic we
  have tried, which is why the citation points at the Internet
  Archive snapshot of the official URL.
- `label_ref` gives the page in that PDF, so every row is checkable.
- `pre_harvest_interval_days` is the register's "waiting period".

Modifications: doses are the formulated product dose per hectare as
printed. A small number of rows were converted to a **per-acre**
basis using 1 hectare = 2.4711 acres. Those conversions are
arithmetically correct and the `unit` column states the basis
honestly. No dose value was altered.

Two caveats that matter:

- This edition is dated 01/06/2023 and registrations change. It is
  not a statement of what is currently registered.
- The source document carries its own disclaimer: compiled for
  guidance, not for legal purposes.

## The rest of this directory is SYNTHETIC

`district_calendar.csv`, `package_of_practices/`, and `faq_dump.txt`
were written for this exercise. They are internally consistent and
shaped like real agronomic references, but they are **not transcribed
from any state package of practices or other authority**.

**Do not use those three files as agricultural advice.** They exist
so that a scoring system has a fixed, known target to test unit
handling, sourcing discipline, and decline behavior against.

## Deliberate properties

These are not defects. Do not fix them.

- `JAGTIAL` and `PEDDAPALLI` appear in `district_calendar.csv` and in
  no other file.
- Cotton's sowing window in `district_calendar.csv` disagrees with
  `package_of_practices/cotton_kharif.txt`.
- `pesticide_labels.csv` mixes per-acre and per-hectare rows.
- District spellings differ across files: `WARANGAL` /
  `WARANGAL RURAL` / `Warangal (Urban)` / `Warangal Dist.`
- `faq_dump.txt` contains duplicated questions with different
  answers, and contradicts the CSVs in at least two places.
- `package_of_practices/soybean_kharif_extract.txt` is a two-column
  layout flattened badly, as a naive PDF text extraction produces.

## Pull date

Extract built from a cached pull covering 2025-07-22 to 2025-07-29.
