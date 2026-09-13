"""Load the official HGSS character map from the pokeheartgold decomp."""
import os

DEFAULT_PATH = "/home/user/pokeheartgold/charmap.txt"
ESCAPES = {r"\n": "\n", r"\r": "\r", r"\f": "\f"}


def load(path=DEFAULT_PATH):
    """code -> character. Codes whose value is \\xNNNN or {cmd} are skipped;
    callers render those structurally instead."""
    cmap = {}
    if not os.path.exists(path):
        return cmap
    for line in open(path, encoding="utf-8"):
        line = line.split("//")[0].rstrip("\n")
        if "=" not in line:
            continue
        code, val = line.split("=", 1)
        code = code.strip()
        if not code or any(c not in "0123456789abcdefABCDEF" for c in code):
            continue
        if val.startswith(r"\x") or val.startswith("{"):
            continue
        cmap[int(code, 16)] = ESCAPES.get(val, val)
    return cmap
