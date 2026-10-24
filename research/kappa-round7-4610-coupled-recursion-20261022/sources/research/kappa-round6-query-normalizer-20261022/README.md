# Pauli-controlled boundary research

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

**Result:** the finite controller extensions below yield no new Gaussian
supplier. A global-Pauli pair adapter is proved in Lean, and an even-column
complex-Gaussian/Walsh conversion is checked exactly. The adapter has a
precise coordinate-major tape-layout premise that has not been bound to
the whole inherited compiler. No new kappa is claimed here.

## Finite controller screens

The round5 native involution is `T=I+UV`, with
`U=[-B;12I]`, `V=[C,I]`, and `VU=-2I`. Thus `T-I` has rank eight. The
negative-bank correction still needs the operator-valued query `VQ` and
update `Q^-1U`. Neither is replaced by an unpriced scalar query here.

This round instead permits reversible boundary coefficients `a+bP`, where
`P=Q^2` is the actual global Pauli translation. On its two eigensectors,
`Q^-1=P Q` combines the old positive and negative Q coefficient matrices.
An ordinary Gaussian endpoint is considered only when both sectors have
the same multiset of complete Gaussian-word parities, up to field
permutation. Matching numerical rank alone is insufficient.

| Exact finite menu | Trials | Both sectors factor with matching words | New over the constant Laurent basis |
|---|---:|---:|---:|
| p2, all idle and thick-stage masks | 256 | 165 | 0 |
| p3, all idle and thick-stage masks | 8192 | 3024 | 0 |

`pauli_boundaries.py` checks all rational coefficient matrices and their
dyadic boundary programs. The data are in `PAULI-BOUNDARIES.json.gz`.

A changed p2 role program additionally varies its three paired bridge
coefficients independently in `{-1,0,1}` and permits different choices on
the two P sectors. All 6912 idle/thick/bridge programs are checked. The
1980 successful sector factorizations yield 165 matched Gaussian-word
cases; all 165 were already available in the canonical retained DAG.
`CONTROLLED-BRIDGES.json.gz` records this scope. Q exponents are compared
modulo two when checking equivalence, so a free Q-squared Pauli does not
create an apparent new case.

These are finite screens of the stated role programs. They do not exclude
other native constructions, larger role DAGs, or a new funded joint-query
compiler.

## A concrete global-Pauli adapter

Let `Q_f=C_q^(tensor f)`, with q nonzero, and put
`P=Q_f^2=T_(q tensor ones_f)`. This P is one translation on the entire
payload; it is not a product expansion requiring a number of field ADDs
that grows with f. Define

```
E_plus=(I+P)/2, E_minus=(I-P)/2
S(P)=E_plus+i E_minus.
```

On each P orbit `(x,y)`, S is the following invertible pair operation:

```
a = x+y
b = -2y+a
b = i b
a = a+b
b = -2b+a
(x,y) = (a/2,b/2).
```

It uses four complex ADDs, four signed-power-of-two SCALEs, and one exact
i phase. Its square swaps the pair, and replacing i by -i gives its
inverse. All registers in the logical pair are updated in place. Lean
proves the emitted macro, its general composition law, its square, and
its inverse for arbitrary complex inputs. These are four separate
theorems with standard axioms and no `sorryAx`.

## Exact even-column Walsh conversion

Put `R=S(P) Q_f`. Its Fourier multiplier on the f q-coordinates is

```
i^(weight(y)+parity(y)) = (-1)^(weight(y)(weight(y)+1)/2).
```

Consequently `R^2=I`. For even f, define

```
A x = x + parity(x)*ones_f
d(x)=weight(Ax)(weight(Ax)+1)/2 mod 2
sigma=(-1)^((f/2)(f/2+1)/2).
```

The polar matrix of the displayed quadratic form is the f by f matrix
with zero diagonal and one off the diagonal. For even f this is A and
`A^2=I`. Its quadratic Gauss sum is `sigma*2^(f/2)`. The exact kernel is
therefore

```
R[x,y] = sigma * 2^(-f/2) * (-1)^(d(x)+x dot A(y)+d(y)).
```

Thus `R=sigma D H_f P_A D`, where H_f is the normalized real Walsh
transform, D is the explicit quadratic sign diagonal, and P_A is the
binary coordinate permutation A. Finally
`Q_f=S(P)^-1 sigma D H_f P_A D`. There is no dropped global phase.

`real_gauge.py` checks every kernel entry for f=2,4,6,8, as well as every
basis column of the pair macro, its square/inverse, and the A route. This
conversion is a phase-gauge identity; it is not presented as a novel
Fourier-transform result or a kappa improvement.

## Pinned tape layout and owned workspace

The new tape lemma assumes **coordinate-major payload layout**: the f
bits of a chosen q coordinate form a contiguous least-significant digit
inside each spectator block. An already admitted fixed q-to-axis map may
be used only after checking that its tape implementation supports this
same layout. A column-major representation does not satisfy this premise
merely because its logical coordinates can be renamed. No growing bit
transpose is declared free.

In the pinned layout P reverses the `2^f` entries of one coordinate
block. Its orbit pairs are x and bitwise-complement(x). The explicit tape
schedule copies the first half of a block to one owned coefficient
stream, reads that stream backward against the second half, performs the
pair operations, then copies the updated first half back. The work
stream is zero initialized and erased, and receives no productive job
credit. Its peak size is half one coordinate block, plus constant scalar
word scratch space. The instrumented word-head schedule, including
initialization/erasure and head returns, is bounded by `8*2^f+4` word
moves per block; fixed-width pair arithmetic adds only a constant number
of linear scans of each coefficient.

For even f, A swaps exactly the odd-weight complement pairs and fixes the
even-weight pairs, so the same schedule implements it. The quadratic
signs need only weight modulo four. A binary counter generates them with
fewer than `2*2^f` total bit toggles per coordinate block. With `b>=f`, the
pinned-layout adapter uses `O(2^n b)` bitwork with constants independent
of f, including workspace copying and erasure.

This is a **new conditional layout lemma**. The compatibility of that
layout with all inherited row views, whole-job boundary matching, and
finite-precision recursion is open. The old monomial-only normalizer
hypothesis does not automatically admit this nonmonomial pair adapter.

## Reproduction

From the repository root in PowerShell:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-query-normalizer-20261022/pauli_boundaries.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-query-normalizer-20261022/controlled_bridges.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round6-query-normalizer-20261022/real_gauge.py
```

The third command uses the retained Lean 4.21.0/mathlib runtime and writes
`REAL-GAUGE.json`. Its Lean scope is the arbitrary-input pair algebra;
the full f-uniform Fourier derivation and tape-layout lemma above have
not been formalized in Lean. The finite controller searches have no
Lean supplier or kappa theorem attached to them.
