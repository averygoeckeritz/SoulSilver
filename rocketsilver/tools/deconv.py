"""Undo an image upscale by solving for the original pixels.

Resizing is a linear operation: every enlarged pixel is a fixed weighted sum of
original pixels. Build that weight matrix by enlarging basis vectors, then solve
the least-squares system for the original. Because resizing is separable, this
is two small 1-D problems rather than one enormous 2-D one.

Far better than sampling block centres, which at a 2.4x scale still picks up a
lot of the neighbouring pixels through the filter's tails.
"""
import numpy as np
from PIL import Image

def build(n_small, n_big, filt):
    """Column j = how source pixel j spreads across the enlarged row."""
    # 32-bit float mode, because bicubic and lanczos have negative lobes that
    # an 8-bit basis would clip, which silently breaks linearity
    A = np.zeros((n_big, n_small), np.float64)
    for j in range(n_small):
        e = np.zeros((1, n_small), np.float32); e[0, j] = 1.0
        row = np.array(Image.fromarray(e, "F").resize((n_big, 1), filt), np.float64)[0]
        A[:, j] = row
    return A

def solve_axis(data, A, reg=1e-3):
    """data: (n_big, k) -> (n_small, k), one least-squares solve reused."""
    AtA = A.T @ A + reg * np.eye(A.shape[1])
    AtB = A.T @ data
    return np.linalg.solve(AtA, AtB)

def deconvolve(big, W, H, filt):
    b = np.asarray(big, np.float64)
    BH, BW, C = b.shape
    Ax = build(W, BW, filt)
    mid = np.stack([solve_axis(b[:, :, c].T, Ax).T for c in range(C)], -1)   # (BH, W, C)
    Ay = build(H, BH, filt)
    out = np.stack([solve_axis(mid[:, :, c], Ay) for c in range(C)], -1)     # (H, W, C)
    return np.clip(out, 0, 255)
