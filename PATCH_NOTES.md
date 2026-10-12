# Patch notes

Delivered to installed apps **over the air (OTA)**: on launch the app downloads the
latest `app/src/main/assets/index.html` from `main` and applies it the next time it is
opened. Only native changes require a new APK.

Your family tree is stored on the device under a stable, versioned format and is
migrated when it loads, so your data carries over from version to version. As a
fallback you can always **Backup (JSON)** and **Restore from backup** — a backup made
in any version re-imports into any other.

## 2026-10-12 — A birthday reminder for everyone who is alive

Half a page change and half a native one: the page arrives over the air, but a notification is the
phone's own work, so this one also needs the new APK (**1.2**, versionCode 3).

### Added
- **Birthdays** in the menu (⋮): everyone alive whose born date has a day and month, soonest first, with
  how far off it is — *today*, *tomorrow*, *in 12 days* — and the age they turn when a year was given.
  Tapping a name opens that person.
- **Remind me on the day** in that page. Turned on, the phone puts one quiet notification on the screen
  in the morning of each living person's birthday — *“🎂 Neelu Chopra’s birthday · Turning 46 today”* —
  whether the app is open or not.
  - Only the **day and month** of each living person is handed to the phone, so the date comes round on
    its own every year and nothing has to be sent again. The names never leave the phone.
  - Someone with a **Died** date is never included. A born date with only a year (or none) has no day to
    keep, so it is skipped, and the page says how to give one.
  - Android 13 and later asks for notification permission at the moment reminders are turned on;
    nothing is asked for at install time. The daily check runs shortly after 9am (the exact minute is
    the phone's own choice), and the phone may hold it back a while on a battery-saving day.
- An app older than this page says *Update the app first (⟳ in the top bar)* instead of offering a
  toggle that could not work.

### Changed
- The list the phone holds is refreshed whenever the family changes — adding, editing, deleting, or
  restoring a backup — so a birthday added today is reminded from the next morning on.

## 2026-10-12 — Cousins, aunts and uncles, nieces and nephews, and no example dates in the form

A page change: it arrives over the air, nothing to install.

### Added
- **The rest of the family.** A person's own page now offers, beside **+ Parent / + Partner / + Child /
  + Brother / Sister**:
  - **+ Aunt / Uncle** — a brother or sister of one of their parents. With two parents it asks which side.
  - **+ Niece / Nephew** — a child of one of their brothers or sisters.
  - **+ Cousin** — a child of one of their aunts or uncles.
  - **+ Grandparent** — a parent of one of their parents.
  - **+ Grandchild** — a child of one of their children.

  Every one of these is only the links a family already has (a parent, or a shared parent), so nothing
  new is ever stored: the new person appears straight away in the right section of *both* pages — a new
  cousin is listed under **Cousins** on their page and on yours.
- **Link someone already added** gained **Pick an aunt / uncle**, **Pick a niece / nephew** and **Pick a
  cousin** for people who are already in the tree. A brother or sister is never offered as an aunt, a
  niece or a cousin.
- **Connect people** on the tree now also offers "is an aunt or uncle of", "is a niece or nephew of" and
  "They are cousins".
- When more than one relative could hold the new person, the app asks which one (e.g. *Whose brother or
  sister?*) instead of guessing; when the family has nobody for them to hang off yet it says what to add
  first (e.g. *Add Neelu's father or mother first – a cousin is their child*) rather than inventing one.

### Changed
- **No example dates in the form.** Born no longer shows *7/4, 4 Jul 1950 (year optional)* and Died no
  longer shows *7/4 or 4 Jul 1950 – blank if living* (which was being cut off mid-word in the
  half-width box); Nickname's hint is just **optional**. Dates read exactly as before, year or no year,
  and a date it cannot read is still refused with the formats spelled out.
- A message about something done inside a dialog is now shown **over** the dialog instead of behind it,
  so a refusal is actually readable.
- Tapping a person, a name or a **▾** in the tree with a mouse now works: while the panel is watching for
  a drag the browser can send it the click itself, and the panel hands that click to whoever is really
  under the pointer.

### Unchanged
- The stored format. Every new relative is written as the ordinary parent links the family already uses,
  so a backup from any earlier version restores into this one and this one's backups restore into it.

Verified on the delivered bytes:
- **36 checks driving the real page in a real browser** (a seeded family, the real buttons): the new
  relatives are offered; an aunt asks which parent and is stored as that parent's brother or sister; a
  niece or nephew is stored as the child of the brother or sister; a cousin as the child of the aunt or
  uncle, and listed under Cousins on both pages; a grandparent as a parent of the parent chosen; a
  grandchild as a child of the child chosen; the "pick someone already added" path for a cousin; a
  brother or sister is not offered as an aunt; the tree's Connect people can say two people are cousins
  (and refuses the way round that has nothing to hang off); and the family still draws. 0 failed. The
  same suite fails the same way on the previous build, so it is measuring the change and not the page.
- **11 checks on the form itself:** no example in Born, *blank if living* in Died, *optional* in
  Nickname, nothing saved from a hint, a bare "7/4" still saved and written out as *Jul 4*, editing
  shows the date in the box, and a bad date still names the formats it accepts. 0 failed.
- **10 checks measuring the page** (rendered at 390px and at 320px): all eight new buttons fit inside the
  dialog, none lands on another, and each is exactly the size of the chips that were already there. 0
  failed.
- **The 105 existing model suites are byte-for-byte unchanged**, and all **39 existing browser suites**
  give the same result as before (the same pass counts, or the same pre-existing failures), apart from
  the new ones, which fail on the previous build as a control.

## 2026-10-11 — Take a photo with the camera, and change a picture from the person's own page

This one has two halves: **the page comes over the air as usual, and the camera needs the new APK**
(the camera is part of the app, not the page).

### Added
- **Take photo.** The Photo section of the Add/Edit form and a person's own page both offer **Take
  photo**, which opens the phone's camera and puts the picture straight into the person — shrunk to the
  same small picture as every other photo. **No camera permission and no storage permission is asked
  for**: the camera app is handed a one-off writable address into the app's own files, and the page
  reads the picture back from that same private place. Nothing is written into the phone's gallery.
- **Change photo from the person's own page.** Their page now has **Add photo / Change photo** and
  **Take photo** right under their dates, so a picture can be changed without going into Edit first.
  The new picture is saved and shown the moment it arrives.
- The taken picture is kept only as long as it takes the page to read it: only the newest one is kept
  and the folder is emptied on every launch, so the app does not slowly fill the phone.

### Notes
- **Version 1.1 (versionCode 2).** Install the new APK from Actions to get the camera; until then the
  page updated over the air simply hides the Take photo buttons rather than offering a camera it cannot
  open, and everything else keeps working. In a plain phone browser the same button uses the browser's
  own camera input.
- The picture is an ordinary photo like the ones you already have: pick a new one and the old one is
  replaced, or use Remove to drop it.

Verified on the delivered bytes:
- **12 checks driving the real page** with the app's side of the camera played back exactly as
  `MainActivity` does it (a real portrait 900×1200 JPEG standing in for the camera's file, served from
  the same private address the app serves): the form offers Take photo, asks the camera once, shows the
  picture before saving and keeps it on save at the usual small size; the person's own page takes a new
  picture and shows it; Change photo from that page still comes from photos/Files and does not open the
  camera; and the form's original photo button still works. 0 failed.
- **7 checks for the two older worlds:** an app installed before this change (no camera bridge) hides
  the Take photo buttons on both surfaces and still takes a picture from photos/Files; and a plain
  phone browser offers Take photo and sends it to the camera input (`capture="environment"`). 0 failed.
- **8 checks on where the buttons actually land** (measured on the rendered page at a 390px panel):
  Add photo and Take photo sit side by side and on the panel, Remove stays hidden until there is a
  picture to remove and then joins them on a second line, and the person's own page fits Change photo
  and Take photo with their picture above them — none of them on top of another. 0 failed. Screenshots
  taken of both.
- **The 105 existing suites are unchanged**, and the earlier suites all still pass on this page — 71
  checks (9 nickname, 5 nickname paths, 41 dates, 12 note dates, 4 PDF).
- **Could not be run here:** this sandbox has no JDK and no Android SDK, so the Android half (the
  FileProvider, the camera intent, the private photo address) is reviewed rather than compiled; the CI
  builds the APK on push. The page half above was executed in a real browser.

## 2026-10-11 — A date with no year is fine, and it is written out in full

This is a page change, so it arrives over the air.

### Changed
- **The Born and Died boxes take a date however it is written, and the year can be left out.** "7/4"
  is the 4th of July and is accepted on its own — so are "4 Jul", "4th July", "July 4", "July 1950",
  "7/4/1950", "4 Jul 1950", "7-4-1950", "7/1950", "1950-07", "1950", and a month by itself for
  "some time in July". A first number over 12 can only be a day, so "21/7" is 21 July; with both
  numbers 12 or under it is month first (7/4 is July 4), the same order the form has always asked for.
  Anything it still cannot read is refused, and the refusal now says what is allowed:
  *"Dates look like 7/4, 4 Jul 1950 or 1950 – the year can be left out."*
- **A date is written out in full wherever it is shown** — the person's page ("Born 4 Jul"), the people
  list, the cards on the map and the exported PDF: a day and a month when no year was given, "Jul 1950"
  when only the month and the year are known, and the year whenever there is one. The stored code is
  never shown.
- **Opening a person for editing shows the date written out** ("4 Jul"), and saving it again keeps the
  date exactly as it was — a date with no year stays a date with no year.
- **Notes read the same dates.** "Mary Smith b. 7/4", "born July 4 1950" and "b. 21/7" now give the
  person a real date, and a month written out is no longer swallowed into the name — "born July 4 1950"
  used to make the name "Mary Smith born July 4".
- A date with no year is kept as itself (`--07-04`, the standard way to write a date without a year), so
  **no year is ever invented for it**: ages, the year range on a card and the A–Z ordering all treat it
  as "year unknown".

### The wife's parents, measured
- On the build on your phone her father's box is centred over the **couple** — measured on your shape at
  phone zoom he sits **11.5 canvas px from the middle of the pair** and only **21 px from the husband's
  card**, which is why he reads as the husband's parents. This file lines him up on **her own card**
  (**9.4 px** off it), with her line ending on her card.
- Where the husband's own parents' box is in the same row and the row has no slack, her father's box
  leans as close as the row allows instead of being drawn over the family beside it — his line still
  ends on her own card.

Verified on the delivered bytes:
- **41 checks driving the real form in a real browser** (headless Chrome, 390×844, the real buttons):
  17 ways of writing a date each saved and read back, editing a date with no year and saving it
  unchanged, a date with no year showing on the people list, a blank date still fine, and three
  unreadable dates refused with the new message and adding nobody. **Control, the build on the phone:
  26 of the 41 fail.**
- **12 checks on the notes path** — "b. 7/4", "born July 4 1950", "b. 21/7", "b. 1950", "born July
  1950", "b. 4 Jul" all give the right name and the right date. **Control: 7 of the 12 fail.**
- **4 checks reading the exported PDF**, taken from the real Menu → Export PDF: it says "4 Jul", not the
  stored code.
- **The 105 existing suites are unchanged** — the same result line and exit code per suite as the build
  you already have (82 exit 0, 23 exit 1).

## 2026-10-11 — If all you know is a nickname, that is enough

This is a page change, so it arrives over the air.

### Changed
- **A person can now be saved with only a nickname.** The Add/Edit form insisted on a **Name** and
  refused the save with *"Name is required."*, so someone you only know by a nickname could not be
  added at all. Either box is now enough: type the nickname, save, and the person is added and shown
  under it. The Nickname box reads *"optional – fine on its own"* to say so, and the refusal you still
  get — when **both** boxes are blank — now reads *"Add a name or a nickname."*
- **When a nickname is all there is, it becomes the person's name.** Nothing is left with an empty
  name and the nickname trailing behind it as a quoted afterthought (a card reading just `“Bobby”`).
  If you do know the full name, both are kept exactly as before and the card reads
  **Robert Singh “Bobby”**.
- **People made from a note work the same way.** A note like `“Bobby” b. 1950` — via **Make person** or
  **Make people from all** — used to produce somebody with no name at all, drawn as a blank card with
  `“Bobby”` beside it. They now come out named **Bobby**. Records already saved that way, and backups
  restored from them, are named from the nickname as they load, so blank cards you may already have
  disappear.

Verified on the delivered bytes:
- **9 checks driving the real form in a real browser** (headless Chrome, 390×844, clicking the real
  buttons): typing only a nickname saves a person shown as **Bobby**, with no empty name and no
  duplicated *“Bobby”* nickname; a full name **and** a nickname still store and display as
  `Robert Singh “Bobby”`; and a save with both boxes blank is still refused, with the new message, and
  adds nobody. **Control:** the shipped build fails 7 of the same checks — it stores 0 people.
- **5 checks on the note path** in the same browser: the form opens holding the nickname from the note,
  saving it makes **Bobby**, **Make people from all** names them from their nicknames, nobody is left
  with an empty name, and both appear on the People list. **Control:** the shipped build fails 4 of the
  same checks — both people come out with no name.
- **2 checks for a record already stored with a nickname and no name** (as an older backup could hold):
  it loads and shows as **Rosie** instead of a blank card reading `“Rosie”`. **Control:** the shipped
  build fails both.
- **All 105 existing suites keep their result** — 82 exit 0, 23 exit 1, the same per-suite output line
  as the shipped build.

## 2026-10-11 — The girl's parents are drawn over the girl

This is a page change, so it arrives over the air.

### Changed
- **A couple's in-law parents now sit over their own child inside the box, not over the middle of the
  pair.** When a mother and father have just the one child in a couple box — a daughter who married into
  the family above her — their box was drawn centred on the *pair*, so the family over the couple read as
  the parents of both of them. It is now lined up on **her own card**: directly over the girl, with her
  line coming down onto her. Measured on the drawn page at phone zoom, the parents' box went from
  **54px off her card to 0px** on the two-family shape, and on the 66-person two-sided family from
  **164px to 19px** — 19px being the closest the row could carry it without touching the family next
  door; the line still ends on her own card either way.
- Nothing else moved: the couple still stays with the family it is read through, the family next door is
  never shifted to make room, and no box ever overlaps another. If the room on the row is not there, the
  box leans as close as it can and the **page grows instead** — it is never drawn over its neighbour.

### Unchanged
- **The map still opens at the readable zoom** (names around 9–10px on a phone), not fitted to the whole
  family. **Fit** shows everyone when you want the overview.

Verified on the delivered bytes:
- **9 checks, 0 failed** across four shapes — two families with one marriage; the same with a
  grandchild; the reported two-sides family with in-law parents who have brothers and sisters of their
  own; and that family with the girl's parents having only her — measuring, for every parent box whose
  only child on its row is one half of a couple, how far it sits from **that child's own card**, plus
  that no two boxes overlap and none leaves the page. **Control:** the build that was shipped fails 2 of
  the same checks (16px and 164px off her card).
- **Measured on the real page** (headless Chrome, 390×844 phone, rendered markup, not the model): the
  parents' box centre is **0.0px** from the girl's own card on the two-family shape, and **18.6px** on the
  66-person family — the closest the row allows. Screenshots taken of both.
- **All 105 existing suites keep their result**, and the earlier folding and Fit work still passes
  (10 checks × 2 phone panel sizes, and 7 checks in a real browser driving the real buttons).

Two diagnostics report the trade this feature makes, and both still pass: `health2`'s *child-off-column*
metric reads **2** instead of 0 — an in-law box is now over the child's own card rather than exactly in
its column — and `shape`'s *not-under* count for the 17-person joined family reads **4** instead of 5,
because one box that was not under its parents now is.

## 2026-10-11 — Folding a branch keeps your place, and Fit really shows everyone

This is a page change, so it arrives over the air.

### Fixed
- **Folding a branch no longer leaves you somewhere else on the page.** Folding a box can cut a family
  loose — the married couple that joined two sides is drawn inside one of them — and the page is then
  laid out with that family as its own block, below the first. The view, though, was left exactly where
  it had been, so you were looking at a corner of the page where your family no longer was and the rest
  of it sat off the panel: it read as the tree breaking and hiding people. Now the box you folded is
  **kept on the panel** — the view is slid only as far as it needs to be — so a branch folds where you
  are looking and everything else stays where it was.
- **Collapse no longer opens in the middle of itself.** Pressing **Collapse** (or folding with a box's
  **▾**) used to leave the view clamped into whatever part of the old, much larger page you had last
  scrolled to — on a family of 76 that meant the folded tree opened with its start 119px off the left of
  the panel and, on a short phone, 9px above the top of it. The view is now put back on the **first box
  of what you are left with**, so a folded tree starts at its own beginning and reads downwards from
  there.
- **Fit now really shows everyone.** It only ever fitted the *width*: on a 390px phone panel it left a
  folded 76-person family 334×2188px (55% of it on the panel) and a whole 68-person family 628px wide on
  a 390px panel — so pressing it repeatedly never showed the bottom or the far side. It now fits **both
  ways round** (width and height), and its floor no longer stops it fitting a big family: 60% of the tree
  on the panel before, **100% after** — folded or whole, every person drawn.

### Changed
- **Expand all** returns you to the readable view the map opens with, instead of leaving the zoom you
  were using on a page that has just changed size.
- Opening the map is unchanged: a big family still opens at the readable zoom, so on a phone you are
  looking at part of it until you press **Fit**, which is what Fit is for.

Verified on the delivered bytes:
- **10 checks in the browser layout, 0 failed**, at two phone panel sizes (390×640 and 390×1200), on a
  68-person family in the reported shape — two whole sides, each child's in-law parents and brothers and
  sisters, joined by **one** marriage. **Control:** the same checks against the build that was shipped
  fail **4 and 3** of them — the folded box left 2,986px off the panel, the folded family opening in the
  middle of itself, and Fit leaving the folded family and the whole family off the panel.
- **7 checks in a real browser** (headless Chrome, 390×844 phone) driving the real buttons and the real
  ▾: drag the map 3,000px away, fold the marriage, zoom in three steps, drag deep, then **Collapse** and
  **Fit** — the folded box stays on the panel, the collapsed family starts at the panel, and Fit puts
  **20 of 20** people of the folded family and **68 of 68** people of the whole family on the panel.
- **105 existing suites are unchanged** — same result line and same exit code as on the previously
  shipped build (space 24, link 28, zoom 25, combine 18, badlink 28, badload 11, sidefamily 27,
  anchoring 18, groups 96, the sweeps, the fuzzers and the shape dumps), so nothing about the drawing,
  the spacing or the connectors moved.

Two assertions in `space` were restated rather than loosened. They ask *“the default view keeps names
readable (≥9px)”* and *“and never zooms out past the readable floor”*, but reached the default view by
pressing **Fit** — which passed only because Fit used to be capped at the readable floor on the first
render. Now that Fit does its job and may be smaller than that floor, both checks measure the view the
map actually opens with, with the same thresholds (≥9px, ≥0.78). The new behaviour they had to state —
that Fit is smaller than the readable default and still inside the panel — is asserted separately.

## 2026-10-11 — The Menu no longer offers to delete everyone

### Removed
- **“Delete everything” is gone.** The Menu now offers **Export PDF**, **Backup (JSON)**, **Restore from backup** and
  **Close**, and nothing else. The code behind it is gone as well, so nothing on the page can empty your family any
  more — not the button, and not a mistap on where it used to be. Removing one person from their own card
  (**Edit → Delete**) is unchanged, and **Restore from backup** still replaces your tree on purpose, after asking.

This is a page change, so it arrives over the air like the rest.

Verified on the delivered bytes:
- **9 checks in a real browser, 0 failed** — the menu opens with the ways back and out, no button on it asks to
  delete, no element anywhere in the page carries a delete-everything action, the app's own script contains no
  delete-everything code at all, nobody is deleted while the menu is open, **Close** closes it, **Backup** still works
  and no error is thrown while using the menu. **Control:** the same checks against the build before this change fail
  three of them — the button, the wording, and the code — so they really do test this change.
- everything else is unchanged: 87 layout checks, 154 photo checks, 78 geometry checks with no clipped text, 414
  consistency checks, 10 pixel checks, and link 28, zoom 25, combine 18, space 24, badlink 28, badload 11,
  sidefamily 27, anchoring 18, groups 96 — **0 failed**.

## 2026-10-11 — A picture can come from your photos, not only from Files

**This one needs a new APK** (it is a phone-side change), built from this commit. It is not an over-the-air update.

### Added
- **“Add photo” now offers the phone's own pictures.** The app used to open the file browser for every picture
  choice, so the photo gallery was never on the list. For a page asking for an image it now opens a sheet with
  **Photos** (Android 13+ system photo picker) and **Gallery** (the phone's gallery app on older Android) as well as
  **Files**, and the picture you tap in the picker comes straight back to the card and is saved as before. Restores
  and any other kind of file still open the file browser directly, with no extra screen in the way.
- If a phone has no gallery and no photo picker at all, the choice falls back to the file browser, so Add photo can
  never end up doing nothing.

### Fixed (delivered over the air)
- **A picture that cannot be opened now says so.** If the phone hands back a picture the app cannot decode — a HEIC
  photo on a phone without a decoder, or a gallery that returns a photograph we are not allowed to read — the card
  used to stay exactly as it was, with no message at all, so it looked as though the tap had been ignored. It now
  says *“That picture couldn’t be opened – if it is a HEIC photo, pick it from Files as a JPEG instead”*, and no
  half-set picture is saved.

Verified:
- **9 browser checks, 0 failed** on the page as a phone sees it — a real picture picked through the card's file
  input is taken, shrunk and saved on the person, and a picture the phone cannot hand over says so, keeps no
  half-set picture and writes no photo. **Control:** the same checks against the build before this change fail
  exactly the new one (*“the app tells you the picture could not be opened”* reads empty), so the check really does
  test the new behaviour.
- the rest of the battery is unchanged on these bytes: 87 layout checks, 154 photo checks, 78 geometry checks with
  no clipped text, 414 consistency checks, 10 pixel checks, and link 28, zoom 25, combine 18, space 24, badlink 28,
  badload 11, sidefamily 27, anchoring 18, groups 96 — **0 failed**.

The phone-side change follows Android's own rules: the system photo picker needs no permission and no manifest
entry (Android 13+, `MediaStore.ACTION_PICK_IMAGES`), and older phones use `ACTION_PICK` against the pictures
library. It could not be compiled in this workspace — there is no JDK, Gradle or Kotlin here — so it is compiled
and packaged by the repository's own CI workflow on push.

## 2026-10-11 — Everyone who has a picture shows it, in their own card

### Fixed
- **A box holding a couple drew only one of the two pictures, and never inside a card.** The picture was drawn
  once per box, for the person the box is read through (the earliest born of the pair), floating at the box's left
  edge — so a husband's or wife's own picture was simply dropped and no card ever showed the picture of the person
  it belonged to. On the reported shape (two of the five people pictured, one of them the second person in a
  couple) the tree drew **1 of 2** pictures, and on a couple where only the *younger* partner has one it drew
  **none**. Now **each person's own picture is drawn inside their own card, immediately before their name**, so
  everyone who was given a picture shows it: 1 of 2 before, **2 of 2 after**; 0 before, **1 after**; and on the
  23-person family with everyone pictured, **14 of 23 before, 23 of 23 after**.
- **A picture no longer eats the room a name was given.** A column is now a whole name column (CW: 64px on a
  phone, 96px on a wider screen) *plus* the 34px picture and the 6px gap after it whenever that person has one, so
  no name is narrowed to fit a picture. In a couple where the first person had a picture, both names used to share
  **39px** of column each (the picture's room was taken out of the names); each column is now **104px** — the full
  name column, with the picture alongside it. A box with nobody pictured is unchanged (a lone box is still
  122×84 on a phone).

### Changed
- A box grows by the picture's width (40px) for each of its columns when anyone in it has a picture: a couple
  where both are pictured is 282px wide (with a ▾ button) instead of 194. The page therefore gets wider as pictures
  are added — with all 23 people pictured it grows from 1050px to 1448px — so the tree opens a little smaller in
  that case; nothing is clipped and **Fit** still shows the whole family at once.

Verified on the exact bytes delivered:
- **87 new layout checks, 0 failed** — a picture is drawn for each person who has one and for nobody else, inside
  their own card, before their own name, never outside a card; and a pictured box keeps a whole name column plus
  the picture's width, so no name is narrowed to fit a picture;
- **154 browser checks, 0 failed** in a real browser at a 390px-wide phone viewport, both colour schemes — each
  picture is drawn inside the person's own card and beside (never over) their name, at its full 34px page size at
  the current zoom, the name is not clipped, and the picture is really painted on the screen (a marker-coloured
  photo: the centre pixel and at least 55% of its circle are that colour, and a blank picture is refused).
  **Control:** the same checks against the previously shipped build find **4 pictures for 5 people, none of them
  inside a card** — that is the bug, and the check catches it;
- everything else still passes: **78 geometry checks, 0 failed** with **no clipped text**, **414 consistency
  checks, 0 failed**, **10 pixel checks, 0 failed** in dark and light, and on the layout side **link 28, zoom 25,
  combine 18, space 24, badlink 28, badload 11, sidefamily 27, anchoring 18, groups 96 — 0 failed**; the
  4,260-operation sweep introduced no violation, and over 250 random families and the shape sweeps still draw with
  nothing overlapping, no connector running upward, none through a box and none off the canvas.

Three assertions were restated rather than loosened, and the new behaviour they had to state was verified directly:
- `space` measured a couple's spare width (`box − lone − gap ≥ 60`) — a proxy that came from an estimate of the
  box's padding, and which reported 60 even while a pictured couple's names really had only 39px each. It now asks
  for what it is named after: **every person's own column is at least a whole name column (CW)**;
- `zoom`'s “dragging up moves the canvas up” assumed the page overhangs the panel by more than the drag; the tree
  getting slightly narrower left the fitted page only 0.57px taller than a 600px panel, so the check now first
  requires (and asserts) at least 300px of overhang in both directions, then the drag must still move by exactly
  the drag distance — the panning itself is unchanged;
- `pixels` measured how much of a 3px band the card's 1px outline covers, which is decided by where the fractional
  zoom puts that pixel: it read 0.20 after this change (0.33 before) on a ring that is drawn *exactly*. It now asks
  for a pixel matching the outline colour anywhere in the band — measured at **difference 0** on both the top and
  the left edge, where the previous build only reached a blended value.

The picture is drawn from the same 34px circle the card already had; the People list and a person's own card are
unchanged.

## 2026-10-10 — Brothers and sisters are drawn in one run, under their own mother and father

### Changed
- **Each family's children now sit in one run on their row.** A child who married into another family is
  drawn at the end of their own brothers and sisters nearest the family they married into, so a family
  reads as a block: mother and father above, their sons and daughters side by side, and their children on
  the row below theirs — branching out and going down.
- **A mother and father are drawn over their own children**, and over the ones the family is read through
  (children who went on to have children of their own), instead of over a block that belongs to a family
  which merely married into theirs. In the reported tree `Parmjit Singh` and `Gurjit Kaur` were drawn above
  `Baljit Singh` & `Deepa Kaur` — another family's children — with `Maninder Kaur Singh` three boxes away;
  they now sit over their own three children (`Kulvinder`, `Ranbir` and `Maninder`) with `Maninder`'s box
  next to her brother's.
- **A row is settled after every column in it is known**, so a parent follows the columns its children
  actually got. `S Grandad` was a full box-width off his own son; he is now directly above him.
- Nothing else moved: same canvas for the 23-person family (1850×812), same box widths and row spacing, no
  text clipped, and the tree still opens at the same readable zoom.

### Fixed
- Families could interleave: two families' children were woven together, so a parent's lines fanned across
  the whole row and you could not see whose sons and daughters were whose. Measured on the 23-person
  family, the sideways travel from a mother and father to a child fell from **average 249px and worst
  748px** to **average 156px and worst 374px**, and both families' children are now unbroken runs.

Verified on the drawn page and in the layout itself:
- **96 new layout checks, 0 failed** — every box's children are drawn below it, no other family's box sits
  inside a family's run of brothers and sisters, and every mother and father is drawn over their own
  children (the in-law side of a marriage, whose child can only be drawn under one of the two families, is
  drawn beside it with its line coming in sideways);
- **78 geometry checks, 0 failed** in a real browser at a 390px phone viewport, **414 consistency checks,
  0 failed** and **10 pixel checks, 0 failed** in dark and light mode, with **no clipped text** in six
  families;
- **177 existing assertions, 0 failed** (link 28, zoom 24, combine 18, space 23, badlink 28, badload 11,
  sidefamily 27, anchoring 18), the 4,260-operation sweep introduced no violation, and over 250 random
  families and 6 set shapes no box overlaps, no connector runs upward, none crosses a box and none leaves
  the canvas; cyclic and 120-generation families still terminate.

Three assertions were restated rather than loosened: `sidefamily` previously required a married brother's
couple to be drawn in the *same column* as his parents and each of a wife's parents' children to be within
half a box of them — that is not possible once a family's children share one run, so those checks now state
the requested rule instead (the couple is drawn inside its own family's run, and a parent is drawn between
its own children rather than under the family it married into). Everything `sidefamily` was written to
protect — the couple not being dragged under the wife's parents, her family set beside them, the children
under their own parents — still passes.

## 2026-10-10 — Each person fills their own cell, so a couple stops looking like a half-empty box

### Changed
- **The two people in a couple now fill their box.** Before, each person's card hugged its own text and sat
  at the top of the box: one card came out taller than the other, the names were stranded at the top and the
  rest of the box was empty — which read as the tree glitching out. Both cards are now exactly as tall as the
  box's inside, so the pair is a tidy two-cell block and every box in a row is the same height.
- **A card is now the same colour as a single person's box** (`--card`, with a 1px outline), instead of a
  darker tint: on one row a person on their own and a person in a couple now look like the same thing drawn
  once or twice, rather than two different kinds of box.
- **The name is centred in its card**, so a one-line name sits level with a two-line one beside it.
- **The marriage bar moved down to the middle of the box** (it was 17px below the top, which on the taller
  card read as a stray dash). It now sits in the middle of the 10px gap between the two cards.

Measured on the rendered page (headless Chrome, 390px-wide phone viewport, six families, both colour
schemes):
- **414 consistency checks, 0 failed** — every card in every couple is the same height as its partner, fills
  the box's inside exactly (78px of an 84px box), is flush with the box's top and bottom, carries the same
  fill as a single person's box, has its name centred, and the marriage bar is centred in the gap between
  the two cards and on the vertical middle of the box;
- **78 geometry checks, 0 failed** and **0 clipped text** — every connector still leaves and arrives on the
  right person's card, and long names still wrap instead of being cut;
- **10 pixel checks, 0 failed** in dark and light mode — each card is still filled and ringed and the line's
  last pixel still sits on the target card's top edge;
- **177 Node assertions, 0 failed** (link 28, zoom 24, combine 18, space 23, badlink 28, badload 11,
  sidefamily 27, anchoring 18), the 4,260-operation sweep introduced no violation, and over 250 random
  families and 6 set shapes nothing overlaps, no connector runs upward and none crosses a box.

## 2026-10-10 — Each person in a couple sits in their own card, so a line can be seen to touch one of them

### Changed
- **A box that holds a couple now draws each person in their own card**, joined by a short marriage bar,
  instead of two names loose in one box. Each card has its own outline and a slightly darker fill, so the
  pair reads as **two separate people at a glance** — and the line that arrives at the box can be seen to
  land on **one** person's card. On the couple in the reported tree (`Rinku Singh` + `Maninder Kaur
  Singh`) the drop from `Parmjit Singh` used to reach the middle of the box; it now ends on **Maninder
  Kaur Singh's** own card, measured from the rendered pixels on a 390px-wide phone at 87% zoom.
- **The connector reaches the card itself**, not just the edge of the box: a couple's box reserves only 2px
  above the cards, so the line ends exactly on the top edge of the person's card.
- **Everything else is where it was.** The card is drawn with `outline`, which takes up no space, so the
  canvas, box widths, wrapping, row spacing and every connector position are unchanged (1050×896 for the
  23-person family, opening at 78%) and no text is clipped.

Verified in a real browser — headless Chrome at a 390px-wide phone viewport, both colour schemes:
- the rendered markup was measured, not modelled: **78 geometry checks, 0 failed** — every connector's two
  ends fall inside the right person's own card, and a line shared by both parents still leaves the middle
  of the pair;
- **10 pixel checks, 0 failed** — each card is filled and ringed (its outline and fill colours are present
  in 33–72% of the band sampled along its edges and face), the marriage bar is inked between the cards, and
  the line's last pixel sits on the target card's top edge;
- **no clipped text** anywhere in six families (the card adds no inset, so a long name wraps as before),
  and the canvas, scale and card widths are identical to the previous build.

The existing suites still pass: link 28, zoom 24, combine 18, space 23, badlink 28, badload 11,
sidefamily 27 = **159 assertions, 0 failed**, plus the 18 connector-anchoring assertions; the
4,260-operation sweep introduced no violation; cyclic and 120-generation families terminate; over 250
random families (2,325 connectors) and 6 set shapes nothing overlaps, no connector runs upward and no
connector crosses a box it does not join.

## 2026-10-10 — A connector points at the person it belongs to, not at the couple

### Fixed
- **A parent's line into a box that holds a couple no longer lands between the two names.** Every
  connector used to be drawn from the middle of the parent's box to the middle of the child's box, so a
  line belonging to **one** spouse arrived between the pair — and with both names under one line the
  family above read as **the parents of the couple**, when they are only the parents of one of them.
  A connector now **leaves the name of the parent and arrives at the name of the child**, measured on
  the name's own column (the column sits between the photo on the left and the ▾ button on the right,
  so a name's place is measured from that). On the couple box in the reported tree — `Rinku Singh` and
  `Maninder Kaur Singh` — the line from `Parmjit Singh` used to land on the box centre, four pixels
  short of where the two names meet; it now lands on the middle of **Maninder Kaur Singh's** own name,
  so the line visibly belongs to her.
- **A line both parents share still leaves the middle of the pair.** When the two people in the box are
  both the child's parents the two ends average out, so the couple's own line down to their children is
  unchanged — the change only separates the one-parent case from the two-parent case.

Verified: 18 new assertions on the rendered markup — every connector's two ends land inside the right
person's own name column, and nearer that person than anyone else in the box — on the reported family
and on a couple in every box. The 159 existing assertions still pass (link 28, zoom 24, combine 18,
space 23, badlink 28, badload 11, sidefamily 27); the 4,260-operation sweep is unchanged; over 250
random families (2,325 connectors) and 6 set shapes, nothing overlaps, no connector runs upward and no
connector crosses a box it does not join.

## 2026-10-10 — Brothers and sisters share a row, and a family sits above its children

### Fixed
- **A brother or sister who married into a family that goes back further no longer leaves the rest of
  the family a row higher.** The married sibling is drawn deep in the other family's line, and the
  unmarried brothers and sisters used to stay where their own parents left them, so the family looked
  split — and the parents sat a row above the sibling who stayed home while their married child was
  drawn rows below. Now **every child of a family is drawn on one row**, and the parents are drawn on
  the **row just above their children**, following them down. Measured on a family where the son marries
  a girl whose line goes back two more generations: the brothers and sisters were spread over **1 row,
  now 0** — son, his wife and his sister share a row, with the parents directly above them.
- **A girl's parents are no longer left rows up the page.** Even when their own parents are recorded — so
  they have a fixed generation to sit on — the parents now move down to the row above the couple their
  child married, one generation at a time, instead of staying where they were with a long line reaching
  down to their child.

The two rules feed each other (a family that moves down moves its own parents down, which moves their
brothers and sisters), so they are repeated until nothing moves. A link that loops back on itself
cannot push a box past its own row, so a saved tree with a crossed link still draws and still finishes.

Verified on the exact bytes shipped: link 28, zoom 24, combine 18, space 23, badlink 28, badload 11,
sidefamily 27 — **159 assertions, 0 failed**; the 4,260-operation fuzz sweep introduced no violation;
cyclic and 120-generation families terminate; nothing overlaps, nothing goes upward and nothing is
drawn outside the canvas; the 23-person family is unchanged at **1050×896**.

## 2026-10-10 — A new branch goes down the page, not up it

### Fixed
- **A relative who arrives with a family of his own is no longer dragged across into it.** Adding a
  brother with a wife, children **and her parents** used to shuffle your own family sideways and file
  everyone into the other family's columns — the brother was hung under *her* parents instead of his
  own, and his children ended up beneath the grandparents' box. Measured on that family: his box used
  to be drawn **374px out to the side**, under her parents; now it is **straight below his parents**.
  A child used to be drawn **449px from under its own parents**, under the grandparents' box; now every
  child hangs under its parents. Her family is set **beside** yours — clear of every box of your own
  family, with her brother under her parents — instead of being threaded through it.
- **The same holds a generation down: your children's in-laws.** When a child marries and the spouse's
  parents (and their other children) are recorded, the child's couple used to be drawn **374px out**
  under those in-laws and a grandchild **449px away** under the great-grandparents' box; now the
  child's couple is **straight below you**, each grandchild **hangs under its own parents**, and the
  in-laws are set **aside as their own little branch**, with the spouse's brother under them.
- **A family that marries into another is now laid out right beside the couple it joins**, inside their
  parents' span, instead of at the far end of the page — so the two halves of a related family stay
  together and the connecting lines stay short. Across 40 generated families with marriages at every
  depth the average sideways drift of a connector fell from **425px to 365px**, with nothing overlapping
  and nothing drawn outside the canvas.
- Each family is laid out as its own **block**: a box is drawn above its children and centred on them,
  and each child stays under its parent, so a branch reads straight down the page. A family that joins
  by marriage is placed next to the one it joins rather than between its rows. (A wife's parents are
  still drawn **above** the couple, as parents are — they are simply kept to the side, out of your own
  family's columns, instead of pulling your brother and his children in with them.)
- A saved tree whose rows do not start at the top (which a link crossed by mistake could produce) is
  now **drawn instead of throwing the tree away** — the layout walks the rows that are actually there.

Same family, same size: on the 23-person family the canvas is **1050×896** and the tree still opens at
**78%** with 9.4px names, exactly as before this change.

## 2026-10-10 — A couple sits side by side in the tree

### Changed
- **Partners are drawn next to each other instead of one above the other.** In a box holding a
  couple each person now gets their own **column**, so the two names sit **side by side**; the box
  makes room by growing **wider** rather than taller. A box only grows taller when a single name is
  too long for its column and wraps.
- Each person's column is as wide as the name column of a box holding one person, so no partner is
  squeezed into half the room. On a phone a couple's box is **194px** wide instead of 122, and a
  single-person box is unchanged at 122.
- A box holding a long marriage chain (up to 10 people) now spreads **across** the width instead of
  stacking ten lines high, so the tree is shorter as well as wider.

Measured on the 23-person family: 9 of 14 boxes hold a couple and are now 194px wide (was 122 flat),
all boxes are 84px tall (was 84 or 96), and the canvas is **1050×896** instead of **708×944**. The
Tree still opens at a readable zoom and **Fit** still shows the whole family at once.

## 2026-10-10 — A link that would break the tree is refused instead

### Fixed
- Linking a relative you had already added could save a link that made the family impossible to
  draw — for instance a son's wife becoming his father's parent, or a great-granddaughter being
  made a brother or sister. The tree then **stopped redrawing**, so it looked frozen and went on
  showing the relationships from before the link. Links like that are now **refused with a message
  naming both people**, nothing is written, and the tree always redraws.
- A family **already saved** with such a link is **repaired when the app opens** — just those links
  are undone, nothing else is touched, and the app says so.
- **Names in a crowded box no longer run into each other.** A box that holds several people gives
  each one their own **column** (and a second line for a long name), so no name is ever drawn over
  another and a parent is never hidden inside their child's box.

### Changed
- The pickers now only offer people who could really hold the place you tapped: never yourself,
  never your partner and never someone already in that place, and never anyone straight up or
  down your own line — so a mis-tap cannot quietly wreck the family.

## 2026-10-10 — The tree opens readable instead of shrunk to a speck

### Changed
- The tree used to open zoomed all the way out so every box fitted, which made the names too
  small to read once the family grew. It now opens at a **readable size** (never below 78%)
  and you **drag** to the rest — **Fit** still shows the whole family at once.
- **Zoomed out, the clutter is hidden.** Below 90% zoom the boxes show **names only**, with
  the dates and nicknames dropped and the names drawn slightly larger, so the wide view stays
  legible. Zoom in and the dates come back.
- Boxes are a little narrower and taller on a phone (122×84) so more of the family fits per
  screen.

Measured on a 23-person family whose two sides are joined by a marriage: names now draw at
about **10px** instead of **5.6px**, with around two thirds of the tree on screen when it
opens and the rest one drag away.

## 2026-10-10 — Link people you already added

### Added
- Someone's card now has a **Link someone already added** section: **Pick a parent / partner /
  child / brother or sister / grandparent / grandchild**, then choose the person from a
  searchable list. No new person is created and nothing is typed twice — the relationship is
  made between two people you already have.
- The card and the tree update immediately afterwards.

### Changed
- The old create-new-person chips now sit under a clear **Add a new person** heading, so it is
  obvious which row adds someone and which one links someone.
- Verified the usual guards still hold when linking: no loops, no self-links, no third parent,
  no duplicate links — each is refused with a message instead of quietly duplicating.

## 2026-10-10 — Drag the tree, pinch to zoom

### Added
- The tree is now a **pannable, zoomable canvas**: **drag** with one finger to move around,
  **pinch** with two fingers to zoom, **− / +** to zoom a step at a time, and **Fit** to jump
  back to the whole family. On a desktop browser the mouse drags and the wheel zooms.
- Panning is clamped, so the family can never be thrown off the screen.

### Changed
- The tree is a fixed-height panel you move around inside instead of a page you scroll, so
  zooming in and sliding sideways both work. A drag no longer opens a person's card by
  accident — only a tap does.

## 2026-10-10 — Room to breathe in the tree boxes

### Changed
- ~~**A couple's names no longer sit side by side and touch.** Each person in a box now gets
  their **own line** inside it, with their dates beside the name, so two names can never
  collide.~~ Superseded: partners are **side by side** again (see the entry at the top). The two
  names still can never collide, because each now gets its own equal-width **column** that clips
  and wraps its own text rather than overlapping its partner's.
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
