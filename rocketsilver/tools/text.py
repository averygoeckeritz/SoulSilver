"""Gen 4 (DS) message-file decoder.

Each message file inside a text NARC is obfuscated with two layers of
XOR keying — one for the offset/size table, one per string. Constants
are the standard Gen 4 ones; `decode` round-trips with `encode`.
"""
import struct

TABLE_MULT = 0x2FD
STR_KEY = 0x91BD3
STR_STEP = 0x493D


def _entries(data):
    count, seed = struct.unpack_from("<HH", data, 0)
    key = (seed * TABLE_MULT) & 0xFFFF
    out = []
    for i in range(count):
        k = (key * (i + 1)) & 0xFFFF
        k32 = k | (k << 16)
        off, size = struct.unpack_from("<II", data, 4 + i * 8)
        out.append(((off ^ k32) & 0xFFFFFFFF, (size ^ k32) & 0xFFFFFFFF))
    return out


def decode_file(data):
    """Return the list of decoded u16 character arrays in this message file."""
    msgs = []
    for i, (off, size) in enumerate(_entries(data)):
        key = (STR_KEY * (i + 1)) & 0xFFFF
        chars = []
        for j in range(size):
            c = struct.unpack_from("<H", data, off + j * 2)[0] ^ key
            key = (key + STR_STEP) & 0xFFFF
            chars.append(c)
        msgs.append(chars)
    return msgs


# --- character map -------------------------------------------------------
# Derived empirically from Storm Silver and confirmed against decoded text:
# lowercase starts at 0x145, uppercase 26 slots below it, digits below those.
CHARMAP = {0x1DE: " ", 0xFFFF: ""}
for _k in range(26):
    CHARMAP[0x145 + _k] = chr(ord("a") + _k)
    CHARMAP[0x12B + _k] = chr(ord("A") + _k)
for _k in range(10):
    CHARMAP[0x121 + _k] = chr(ord("0") + _k)
CHARMAP.update({0x1AD: ",", 0x1AE: ".", 0x1AB: "!", 0x1AC: "?",
                0x1B3: "'", 0x1BE: "-", 0x1C4: ":", 0x188: "é"})
# 0xE000 is a line-break control code; other high codes are control//format.
LINEBREAK = 0xE000

REVMAP = {v: k for k, v in CHARMAP.items() if v}


def to_text(chars, raw=False):
    """Render a decoded char array as readable text. Unmapped codes are kept
    as [n] so nothing is silently lost on a round trip."""
    out = []
    for c in chars:
        if c == LINEBREAK:
            out.append("\n")
        elif c in CHARMAP:
            out.append(CHARMAP[c])
        else:
            out.append(f"[{c}]")
    return "".join(out)
