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
