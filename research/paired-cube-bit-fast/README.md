# Faster paired-cube bit-word generator

Drop-in `paired_cube_bit_word.py` (pure Python, stdlib only): `--p 12` takes about 12 s instead of about 110 s (about 9x).
Its outputs are byte-identical to those of the original pinned in `SOURCE.json` (PR #182 at `af90b94`; the
generator is not on main yet).

    python3 -B research/paired-cube-bit-fast/verify.py                  # about 12 s
    python3 -B research/paired-cube-bit-fast/verify.py --original PATH  # also runs the pinned original (about 2 min)

Only the exact linear algebra changed. Interning order and every tie-break are preserved, because frame ids
appear in the output: built-in modular inverse (`pow(x, -1, P)`), incremental joins, a cheaper Gram test (on the
annihilator when it is shorter, using G^-1 = I - J/(9-h)), a direct `perp` formula, per-space caches.

Scope: equivalence is checked by byte-identical regeneration of the p=12 default word, not proved. The
`perp` formula and the "input contained in join" cache rest on standard algebra and have not been reviewed by
hand. The generator is untrusted either way: its output is checked by the original package's independent
`check_paired_cube_bit.py`.
