# Patch notes

Delivered to installed apps **over the air (OTA)**: on launch the app downloads the
latest `app/src/main/assets/index.html` from `main` and applies it the next time it is
opened. Only native changes require a new APK.

Your family tree is stored on the device under a stable, versioned format and is
migrated when it loads, so your data carries over from version to version. As a
fallback you can always **Backup (JSON)** and **Restore from backup** — a backup made
in any version re-imports into any other.

## 2026-10-10 — Faster entry, version-safe saves & a clearer tree

### Added
- **Save & another** button when adding a person, so you can enter several people in a
  row without reopening the form.
- **Enter now saves** the Add/Edit screen from any field (except Notes), and the Name
  field is focused automatically.

### Changed
- The Add/Edit screen is tidier — Name / Nickname, then Born / Died, then Notes, with
  the photo picker moved below — so adding someone takes fewer taps.
- The Tree shows **both** people in a couple with their years (before, only the first
  person's dates were shown).
- The People list shows both parents with their years, e.g. `Child of Sam 1950– & Ada 1948–`.
- **Siblings are listed oldest to youngest.**

### Fixed
- Restoring a backup saved in the older `{ people, notes }` shape now brings the notes
  back as well.
- Backup files carry a version stamp and import tolerantly across versions.

## 2026-10-10 — Nicknames & a real tree

### Added
- **Nicknames.** Every person can have a nickname, shown beside their name on the
  person view, in the People list and in the tree, and included in search and backups.
  A note like `John "Jack" Smith` is split into name + nickname.
- **Brother / Sister.** "+ Brother / Sister" is always offered when adding a relative.
  If there is no parent recorded yet the app creates a shared parent called "Unknown"
  so the two really are linked as siblings; rename it or swap in the real parent later.
- **A real tree.** The Tree tab draws an actual branching diagram — a box for each
  person (with photo and nickname) joined by connector lines — instead of the old
  collapsible list. It scrolls and zooms with − / +, and tapping anyone opens them.

## 2026-10-10 — Photos & richer relationships

### Added
- **A photo for each person.** Add, change or remove it in the Add/Edit screen.
  Images are shrunk on the device (max 240 px, JPEG) so many people fit easily, and
  the picture shows on the person view and beside every name in the People list.
- **Edit any time.** Every row in the People list has a ✎ button that opens the
  person directly for editing, in addition to the Edit button on the person view.
- **More relationships.** When connecting two people you can mark them as
  **siblings**, or as **grandparent / grandchild** (on top of parent, child and
  partners).
- **More relatives shown.** Each person lists Parents, Partners, Children, Siblings,
  **Grandparents**, **Grandchildren**, **Aunts & Uncles**, **Nieces & Nephews** and
  **Cousins** (derived automatically from the family links).

### Notes
- Photos are included in JSON backups and restored with them.
- Photos are not drawn into the PDF export.
- If device storage fills up with photos the app says so instead of silently failing.

## 2026-10-10 — US date format

### Added
- Dates can be entered as **`MM/DD/YYYY`** (for example `01/13/1985`) in the
  Born/Died fields, alongside the existing `YYYY`, `YYYY-MM` and `YYYY-MM-DD`.
- "Make people from notes" recognises `MM/DD/YYYY` dates too, e.g.
  `Jane Doe b. 01/13/1985`.

### Changed
- Dates are normalised to a single internal form when saved, so sorting, ages
  ("Lived 72") and the PDF export stay correct regardless of which format was typed.
- Invalid dates (for example a month above 12) are rejected with a clear message.
- Existing saved records are unaffected.
