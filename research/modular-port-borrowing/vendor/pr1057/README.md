# Borrowing ancestor ports for exact additive echoes

**Research note / recursive interface, seed 56.** Exact additive leaves allow
the binary/ternary dirty echo to run with at most **three dirty length-L arrays,
at any tree depth**, in addition to its input, output and separately charged
leaf workspace. The external input stays read-only at every prefix. Each
completed call restores its other rows, but an ancestor's input or output may
be temporary scratch inside a descendant. This changes the contract relative
to PR822, whose stronger nonlinear restoration guarantee excludes those ports.

For the selected 56-factor tree, the literal word still contains **1,568 leaf
calls**. PR822's sibling allocator requires **five** dirty arrays; the fully
reserved allocator requires nine for this same tree. The new allocator uses
three. PR822's pinned optimizer independently returns 1,568 calls at cap five
and rejects cap four. These are comparisons within explicit allocator and
echo-template classes, not a lower bound for arbitrary reversible programs.

This applies the classical constant-register algebraic principle to the
repository's concrete allocator, contract and accounting. It claims no
priority for that principle. There is **no new kappa**, physical tape compiler,
rounded-leaf guarantee or wall-time speedup claim. At the exact base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`, the selected conditional kappa is
`1661960547713947 / 1000000000000000000` from PR942.

Run from the repository root, with Python 3.12 or newer and no dependencies:

```sh
python3 -B research/linear-port-borrowing/verify.py
python3 -B research/linear-port-borrowing/test_package.py
```

Expected: `PASS`, 861 exhaustive small trees, 1,752 free-module checks,
1,568 primary calls, three primary dirty rows, and `kappa_changed: false`.
The second command rejects 13 deliberately corrupted packages. Verification
reads committed sources and regenerates every proof-relevant receipt field;
it writes nothing unless an explicit `--receipt PATH` is supplied. `--write`
is an author-only certificate regeneration option, not part of cold replay.

The finite domain is all ordered binary/ternary trees through seven factors,
and the unit-optimal trees at 1, 2, 3, 4, 5, 8, 16, 27, 56 and 64 factors.
The independent free-module interpreter retains noncommuting factor words
and a different formal symbol for every initial dirty row. Both orientations
are checked. Dense integer matrices of dimensions two and three provide
120 further signed allocator/layout replays. This evidence supports the
all-tree induction in [PROOF.md](PROOF.md); it is not a machine-checked proof
of the full multiplication theorem.

The main exact dense example has `L = 2`, factor norm at most two, initial
norm at most seven and a common sufficient signed width of **119 bits**:

| Charged item | Borrow ancestor ports | PR822 sibling pool | Reserved pool |
| --- | ---: | ---: | ---: |
| Dirty arrays | 3 | 5 | 9 |
| Leaf calls | 1,568 | 1,568 | 1,568 |
| Data bits, including input/output | 1,190 | 1,666 | 2,618 |
| Intercell head travel, in cells | 1,609,024 | 1,614,016 | 1,666,048 |
| Head travel, including within-cell scans, in bits | 195,914,432 | 196,508,480 | 202,700,288 |
| Unrolled program bits | 20,384 | 20,384 | 23,520 |

All three additionally pay 6,272 scalar multiplies, 9,408 additions or
subtractions, **9,408 scalar zero assignments**, 15,680 reads, 3,136 writes,
four startup scalar zero assignments, 476 scalar-work bits, 26,656 coefficient
bits, program preparation/dispatch and address calculation. The 43,904
primitive commands include returning all four clean scalar work registers to
zero after every leaf. The routing bill includes a data-head return to home
after every leaf. These are explicit counts for the described abstract dense
backend, not a certified implementation on the paper's fixed-tape machine.
The common width is a sufficient proof majorant, not an optimal precision.
Ancestor borrowing can enlarge intermediate values; array counts alone do
not prove an improvement in the best possible bit-space or running time.

The nonlinear boundary is concrete. For the eight-factor fixture and
`f_i(z) = (z mod 17)^2 + (i+1)(z mod 7) - 3`, initial rows
`[-7, -4, -1, 2, 5]` become `[-7, 23, 5, 2, 5]`: a helper is corrupted.
PR822 restores all helpers on that same input. Reversing the new literal word
still restores the entire initial state; reversibility alone is insufficient
for the completed-call restoration contract. Rounded and nonlinear leaves
must retain their original obligations and cannot be substituted here.

Source pins and original notices are in [SOURCES.json](SOURCES.json) and
[NOTICE.md](NOTICE.md). [VALIDATION.md](VALIDATION.md) records environments,
receipt hashes and remaining obligations. The selected construction and
`upstream/` are unchanged.
