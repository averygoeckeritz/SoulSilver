# Character art

Canon characters are converted from official artwork rather than drawn from
imagination. Sources are recorded here beside their converted sprites so a
conversion can always be redone or tuned.

## Process

    python3 rocketsilver/tools/convert_art.py SOURCE.png OUT.png
    tools/nitrogfx/nitrogfx OUT.png OUT.NCGR -bitdepth 4
    tools/nitrogfx/nitrogfx OUT.png OUT.NCLR -bitdepth 4

The converter edge-extends beneath the alpha mask so downscaling cannot drag
background into the outline, resizes with a high-quality filter, then picks an
exact-colour palette by weighted frequency. Averaging-based quantisation washes
colours out badly at this size, which is why it is avoided.

Output is 64x128 in 15 colours plus transparency, bottom-aligned on the same
floor line the replaced figure used, so the intro's layout still works. A
correct conversion produces `.NCGR` and `.NCLR` files byte-for-byte the same
size as the originals they replace.

## Installed

| Character | Replaces | Source |
|---|---|---|
| Iron-Masked Marauder | Professor Oak, intro figure (`intro_00000010/11`) | Bulbapedia |

The intro figure is selected in `src/oaks_speech.c` via `OakSpeechPic`, whose
graphics table is `sBgPicNCGR_NCLR`.

## Why the converter works the way it does

Downscaling with a smoothing filter blends neighbouring colours and invents
in-between shades. At 64x128 that scattered **908 one-pixel specks** through the
first attempt at this sprite. The converter instead quantises the artwork to its
final palette at full resolution and shrinks by majority vote per destination
cell, which cannot invent a colour and so keeps every boundary crisp.

A sprite also needs a solid dark outline to read against a background. The first
pass had one on only 30% of its silhouette. The converter now draws it
explicitly.

## Faces need a hand pass

No downscale can preserve a face that ends up around fourteen pixels wide; eye
slits and similar details smear into mud. Bodies convert acceptably on their own,
faces do not. The workflow is:

1. Run the converter.
2. Print the head as a character map to find its exact geometry.
3. Place the features deliberately, as `face_fix.py` does here.
4. Run `polish.py` to absorb leftover specks and drop unused palette slots.

Quality bar for a finished sprite: **no more than one or two specks, a fully
dark outline, no interior holes, and no wasted palette slots.**

| | First pass | Finished |
|---|---|---|
| Isolated specks | 908 | 1 |
| Outlined silhouette | 30% | 100% |
| Wasted palette slots | 2 | 0 |
