# Patch notes

Delivered to installed apps **over the air (OTA)**: on launch the app downloads the
latest `app/src/main/assets/index.html` from `main` and applies it the next time it is
opened. Only native changes require a new APK.

## 2026-10-10 — US date format

### Added
- Dates can now be entered as **`MM/DD/YYYY`** (for example `01/13/1985`) in the
  Born/Died fields, alongside the existing `YYYY`, `YYYY-MM` and `YYYY-MM-DD`.
- "Make people from notes" recognises `MM/DD/YYYY` dates too, e.g.
  `Jane Doe b. 01/13/1985`.

### Changed
- Dates are normalised to a single internal form when saved, so sorting, ages
  ("Lived 72") and the PDF export stay correct regardless of which format was typed.
- Invalid dates (for example a month above 12) are rejected with a clear message.
- Existing saved records are unaffected.
