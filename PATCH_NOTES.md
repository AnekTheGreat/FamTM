# Patch notes

Delivered to installed apps **over the air (OTA)**: on launch the app downloads the
latest `app/src/main/assets/index.html` from `main` and applies it the next time it is
opened. Only native changes require a new APK.

Your family tree is stored on the device under a stable, versioned format and is
migrated when it loads, so your data carries over from version to version. As a
fallback you can always **Backup (JSON)** and **Restore from backup** — a backup made
in any version re-imports into any other.

## 2026-10-10 — Room to breathe in the tree boxes

### Changed
- **A couple's names no longer sit side by side and touch.** Each person in a box now gets
  their **own line** inside it, with their dates beside the name, so two names can never
  collide. Every box declares the same width **and** height, so boxes always line up evenly
  and can never creep into each other.
- Roomier, more even spacing: column gap 22px (was 16) and row pitch 136px (was 112) on a
  phone, with 44px between one family block and the next.

## 2026-10-10 — Related families are one tree, plus a ⟳ update button

### Added
- **⟳ in the top right, next to ⋮.** Tap it and the app checks for a newer version and
  applies it straight away. (Until now a downloaded update only took effect on the *next*
  launch; launching now says “Update ready – tap ⟳ to apply”.)

### Changed
- **Families joined by a marriage are drawn as one tree.** Each blood family used to get its
  own block, so a couple whose two sides were both recorded was drawn twice and their two
  families sat apart. People are now grouped into couples first, and a couple keeps the
  parents from **both** sides — so the whole related family becomes one diagram and **nobody
  is drawn twice**.
- A family only stays a separate block when there is genuinely no relationship between them.
- Because a combined tree is wider, the Tree still opens **fitted to the screen**. When it is
  too wide to read at a glance the hint says so — tap **+** to zoom in, or **Everyone** for
  readable names.

## 2026-10-10 — The tree fits a phone and shows every branch

### Fixed
- **The tree is a tree again, and the whole family is in it.** The Tree was drawn on one
  canvas about **4.5x wider than a phone screen**, so only the first branch was visible
  and the rest — including relatives who joined by marriage — sat off to the right. Each
  root family is now laid out on its own and **stacked vertically**, so the canvas is only
  as wide as the widest family instead of the sum of all of them.

### Changed
- Boxes are sized for a phone on narrow screens (132x66 instead of 176x72), and the Tree
  **auto-fits the remaining width** when it opens. A 23-person family now draws at about
  **80% scale, all at once**, with nothing clipped and no overlapping boxes.
- **Everyone** — an indented list of the whole family that never scrolls sideways — is
  still one tap away beside **Map**. **Fit**, **−** and **+** zoom the Map, and
  **Expand all** / **Collapse** fold branches in either view.

## 2026-10-10 — The tree always shows everyone

### Fixed
- **Everyone is visible in the Tree again.** The Tree was opening folded, so only the
  top-level people were drawn and most of the family (brothers, sisters, cousins) looked
  missing. The Tree now opens **fully expanded**, so every person in your tree is on
  screen — including people who are only linked as someone's partner, and anyone whose
  parent isn't recorded. Folding is still available, but only when you ask for it.

### Changed
- The **▾ / ▸** toggle now starts at ▾ (open); **Collapse** folds the whole tree and
  **Expand all** opens it again.

## 2026-10-10 — Easier relationships & a calmer tree

### Added
- **Children in the edit screen.** The Add/Edit person screen now has Parents,
  Partners **and Children**, so a person's whole immediate family can be set up in one
  go. Removing a child unlinks it from that person.
- **Expand all / Collapse** buttons on the Tree, plus a per-person ▸ / ▾ toggle that
  shows how many people are hidden under it.

### Changed
- ~~**The Tree opens collapsed.**~~ Superseded: the Tree now opens expanded so everyone
  is visible. See the entry above.

## 2026-10-10 — Faster entry, version-safe saves & a clearer tree

### Added
- **Save & another** button when adding a person, so you can enter several people in a
  row without reopening the form.
- **Enter now saves** the Add/Edit screen from any field (except Notes), and the Name
  field is focused automatically.

### Changed
- The Add/Edit screen is tidier — Name / Nickname, then Born / Died, then Notes, with
  the photo picker moved below — so adding someone takes fewer taps.
- The Tree shows **both** people in a couple with their years.
- The People list shows both parents with their years, e.g. `Child of Sam 1950– & Ada 1948–`.
- **Siblings are listed oldest to youngest.**

### Fixed
- Restoring a backup saved in the older `{ people, notes }` shape now brings the notes
  back as well.
- Backup files carry a version stamp and import tolerantly across versions.

## 2026-10-10 — Nicknames & a real tree

### Added
- **Nicknames**, shown beside the name everywhere and included in search and backups.
  A note like `John "Jack" Smith` is split into name + nickname.
- **Brother / Sister** when adding a relative, plus **siblings**, **grandparent** and
  **grandchild** on the Connect people screen — so more than just parent/partner/child.
- **A real tree.** The Tree tab draws a branching diagram — a box for each person
  (with photo and nickname) joined by connector lines — that scrolls and zooms.

## 2026-10-10 — Photos & richer relationships

### Added
- **A photo for each person** (shrunk on the device), shown on the person view and in
  the People list.
- **Edit any time** — a ✎ button on every People-list row.
- **More relatives shown** — Parents, Partners, Children, Siblings, Grandparents,
  Grandchildren, Aunts & Uncles, Nieces & Nephews and Cousins.

## 2026-10-10 — US date format

### Added
- Dates can be entered as **`MM/DD/YYYY`** (for example `01/13/1985`) alongside
  `YYYY`, `YYYY-MM` and `YYYY-MM-DD`.
