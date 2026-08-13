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
- Records here: 243
- Filtered to StateName = TELANGANA and these districts:
  KAMAREDDY (90), WARANGAL (60), WARANGAL RURAL (30), NIRMAL (63)
- License: Government Open Data License - India
  https://www.data.gov.in/government-open-data-license-india

Modifications: column headers were re-cased inconsistently, a small
fraction of cells were blanked, and rows were filtered by district.
Query and answer text is unmodified.

## Everything else in this directory is SYNTHETIC

`district_calendar.csv`, `pesticide_labels.csv`,
`package_of_practices/`, and `faq_dump.txt` were written for this
exercise. The values are internally consistent and shaped like real
agronomic references, but they are **not transcribed from the CIB&RC
pesticide register, from any state package of practices, or from any
other authority**.

**Do not use anything in those four files as agricultural advice.**
They exist so that a scoring system has a fixed, known target to test
unit handling, sourcing discipline, and decline behavior against.

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
