# Patch notes

Delivered to installed apps **over the air (OTA)**: on launch the app downloads the
latest `app/src/main/assets/index.html` from `main` and applies it the next time it is
opened. Only native changes require a new APK.

Your family tree is stored on the device under a stable, versioned format and is
migrated when it loads, so your data carries over from version to version. As a
fallback you can always **Backup (JSON)** and **Restore from backup** — a backup made
in any version re-imports into any other.

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
