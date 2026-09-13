# Overworld sprites

## The game's format

An NPC is 12 frames of 32x32 in 16 colours: three animation steps for each of
four facings. The player is 24, because walking and running are separate sets.
Frames are stored as one 32x384 strip, 4 bits per pixel, inside an `NSBTX`
container of exactly 6760 bytes, in `files/data/mmodel/`. HGSS draws overworld
characters as textured billboards in 3D, which is why these are textures rather
than ordinary sprites. `tools/nsbtx.py` reads them.

## Recovering upscaled sheets

The supplied sheets had been enlarged about 2.44x by a phone, which destroys the
pixel grid. `tools/recover_sheet.py` undoes this by treating the enlargement as
what it is, a linear operation, and solving for the original pixels
(`tools/deconv.py`), then snapping the result to a palette rebuilt from the art.

Measured against the one sheet whose original survived:

| Method | Character pixels recovered exactly |
|---|---|
| Plain resize back | 23% |
| Centre-sample block centres, then snap | 38% |
| **Invert the resize, then snap** | **94%** |

Two traps, both of which cost time here:

- **Judge accuracy on foreground only.** These sheets are ~78% white page, so an
  overall score flatters any method. The first attempt looked like 86% and was
  actually 38% on the character.
- **Build the palette from foreground pixels with a diversity constraint.**
  Taking the most frequent colours of the whole image spends every slot on
  near-white page gradients and snaps the character to black and white.

## Sheet layout

Facings are grouped in column-blocks, and the first row of each is the walk
cycle. Column starts on the recovered 449x590 sheet:

| Facing | Columns |
|---|---|
| Down | 8, 31, 54 |
| Up | 133, 156, 179 |
| Left | 249, 273, 298 |
| Right | 361, 386, 410 |

Walk row starts at y=188; cells are 23 wide by 32 tall.

## Pipeline

    python3 rocketsilver/tools/recover_sheet.py SHEET.png rec.png 449 590
    python3 rocketsilver/tools/extract_ow.py    rec.png frames.png
    python3 rocketsilver/tools/write_ow.py      frames.png TEMPLATE.NSBTX out.NSBTX

`write_ow.py` clones a real NPC's container so every header field stays valid
and replaces only the texture payload and palette. A correct result is exactly
6760 bytes and reads back through `nsbtx.py` as 12 frames.
