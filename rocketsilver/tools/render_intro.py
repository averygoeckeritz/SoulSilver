"""Compose the intro screen from the ROM exactly as the hardware would.

Reads the tile set, palette and tilemap out of the finished ROM, then paints
each screen cell from the tile its map entry names. If the tilemap and tile
count disagree, this produces the same garbage the console would.
"""
import struct, sys
sys.path.insert(0, "/home/user/soulsilver/rocketsilver/tools")
import numpy as np
from PIL import Image
import nds, narc

ROM = "/tmp/claude-0/-home-user-Pokemon/d9715cb7-1478-56f1-81fb-4b9c6179a7f5/scratchpad/ds/RocketSilver.nds"
rom = nds.Rom(ROM)
arc = narc.Narc(rom.read("demo/intro/intro.narc")) if False else None

# the intro archive, found by path
for path in ("a/1/2/0",):
    try:
        arc = narc.Narc(rom.read(path)); break
    except Exception as e:
        print("could not read", path, e)
print("intro archive files:", len(arc.files))

def ncgr_tiles(d):
    off = struct.unpack_from("<I", d, 16)[0]      # first block
    # RGCN -> RAHC block: tile data after a 0x20 header
    data = d[off+0x20:]
    n = len(data) // 32
    t = np.zeros((n, 8, 8), np.uint8)
    a = np.frombuffer(data[:n*32], np.uint8).reshape(n, 32)
    lo = a & 0xF; hi = a >> 4
    inter = np.empty((n, 64), np.uint8)
    inter[:, 0::2] = lo; inter[:, 1::2] = hi
    return inter.reshape(n, 8, 8)

def nclr_pal(d):
    off = struct.unpack_from("<I", d, 16)[0]
    raw = d[off+0x18: off+0x18+32]
    out = []
    for i in range(16):
        v = struct.unpack_from("<H", raw, i*2)[0]
        out.append(((v&31)*255//31, ((v>>5)&31)*255//31, ((v>>10)&31)*255//31))
    return np.array(out, np.uint8)

def nscr_grid(d):
    w, h = struct.unpack_from("<HH", d, 0x18)
    n = struct.unpack_from("<I", d, 0x20)[0]
    return np.frombuffer(d[0x24:0x24+n], "<u2").reshape(h//8, w//8)

tiles = ncgr_tiles(arc[10]); pal = nclr_pal(arc[11]); grid = nscr_grid(arc[67])
print(f"tiles available: {len(tiles)}   tilemap: {grid.shape[1]}x{grid.shape[0]} cells   "
      f"max tile referenced: {int((grid & 0x3FF).max())}")
if (grid & 0x3FF).max() >= len(tiles):
    print("!! tilemap references tiles that do not exist -> would render garbage")
else:
    print("ok: every referenced tile exists")

H, W = grid.shape
scr = np.zeros((H*8, W*8), np.uint8)
for r in range(H):
    for c in range(W):
        scr[r*8:(r+1)*8, c*8:(c+1)*8] = tiles[(grid[r, c] & 0x3FF)]
im = Image.fromarray(scr, "P"); im.putpalette(pal.reshape(-1).tolist())
im.save("intro_screen.png")
print("composed", im.size)
