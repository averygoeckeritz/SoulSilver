"""Write an NSCR tilemap that draws a TWxTH tile figure on the intro screen."""
import struct, sys
import numpy as np

OUT, TW, TH = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
SCR_W, SCR_H = 32, 24                      # 256x192 in tiles
COL0 = (SCR_W - TW) // 2                   # centred horizontally
ROW1 = 17                                  # keep the feet on vanilla's floor line
ROW0 = ROW1 - TH + 1
assert ROW0 >= 0, f"{TH} tiles is taller than the area above the text box"

grid = np.zeros((SCR_H, SCR_W), np.uint16)
for r in range(TH):
    for c in range(TW):
        grid[ROW0 + r, COL0 + c] = r * TW + c

data = grid.tobytes()
blk = b"NRCS" + struct.pack("<IHHII", len(data) + 20, SCR_W*8, SCR_H*8, 0, len(data)) + data
out = b"RCSN" + struct.pack("<HHIHH", 0xFEFF, 1, 16 + len(blk), 16, 1) + blk
open(OUT, "wb").write(out)
print(f"{OUT}: {len(out)}b, {TW}x{TH} tiles at cols {COL0}-{COL0+TW-1}, rows {ROW0}-{ROW1}")
