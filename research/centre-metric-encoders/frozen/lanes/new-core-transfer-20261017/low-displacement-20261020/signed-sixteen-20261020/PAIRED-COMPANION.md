# A pair-closed signed code and its transpose

The first signed code leaves the selected large readers uncombined.
Its transpose has 32 ordinary mode rows outside the original vertex
blocks. The old transfer grammar does not admit those rows directly.

This packet applies the inverse of the four selected physical pair
codes as a paid suffix. If the first code is `C`, define

```text
Cbar = H_P^-1 C = H^-1 C_m H.
```

The suffix costs 80 real scalar primitives in 13 instructions.
Both `Cbar` and `Cbar^T` now have zero ordinary diagonals and the
original six-mode or eight-port block support. This statement is
checked on the actual 112-port matrices.

The sixteen centre readers are retained in the selected row space.
Apply the actual selected pair code `H_P` to recover them. The
packet includes that recovery matrix. It does not count that
recovery as free when a caller needs the individual readers.

The input metric `K` stays unchanged. For `Gbar=Cbar K Cbar^T`,
the eight large centre norms are now two. All physical entries of
`Gbar` remain diagonal dyadic units. Therefore

```text
Cbar^-1 = K Cbar^T Gbar^-1,
Cbar^T Gbar^-1 Cbar = K^-1.
```

The second identity is the signed-metric contract for the
transpose code. A native clean service for that code can have
a literal inverse-adjoint whose mixed-source block is
`Cbar^-1`. This packet proves its scalar and support conditions;
it does not itself emit the native service.

All four complete words pass on 640 independent complex fields.
The other 528 fields remain unchanged.

| Word | Real scalar primitives | Instructions | Prefix row one-norm | Binary height |
| --- | ---: | ---: | ---: | ---: |
| Cbar | 5644 | 752 | 24 | 3 |
| Cbar transpose | 5644 | 752 | 8 | 3 |
| Cbar inverse | 5644 | 752 | 10 | 3 |
| Cbar inverse-transpose | 5644 | 752 | 6 | 3 |

The checker is [check_paired_companion.py](check_paired_companion.py).
It pins the [first signed-code freeze](FREEZE.json).
Run it with `python3 -I -B` and `--out <new-directory>`.
The expected status is `PASS_PAIRED_SIGNED_SIXTEEN_CODE`.
The normal and `-O` outputs must match byte for byte.

The bridge access lane requested the transpose service. This lane
found the actual support defect and supplied the paid pair suffix.
AI assistance was used. No routed inverse cancellation, terminal
decoder, or supplier improvement is asserted.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
