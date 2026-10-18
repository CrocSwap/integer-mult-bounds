# A fixed 3D coordinate-CNOT target cannot share calls across two roles

**Exact scoped negative result; no new κ.** In the formal group algebra
`F2[GL_3(F2)]`, the target `diag([A],[A])` below needs exactly six paid
coordinate-CNOT calls when there are exactly two scalar registers and every
rank-one scalar idempotent is available. The direct word uses six calls. An
exact meet-in-the-middle search found no word of length at most five in the
complete declared alphabet. This is one fixed target and register count; it
does not settle other three-dimensional targets or extra dirty registers.

The experiment tests a concrete higher-dimensional branch left open by the
two-dimensional [coordinate-CNOT register result](../coordinate-cnot-register-bound/README.md).
It changes the target and address dimension, not just the search seed. The
result is an abstract paid-call fact. The selected bit supplier uses a different
rational-address model, and the complex supplier still binds, so this gives no
immediate κ change.

## Exact model and target

Let `G = GL_3(F2)`. For each ordered pair `i != j`, the only paid address label
is the coordinate CNOT

```text
Tij = I + Eij, acting by row i <- row i + row j.
```

There are six labels. A paid call has unit cost and is
`D_N([g]) = I + ([g] + 1)N` in characteristic two, where `N = xy^T` is a
rank-one idempotent on the two scalar registers (`x,y ∈ F2^2`, `y^T x = 1`).
There are six such idempotents. Free scalar `GL_2(F2)` basis changes normalize
to this full set of six projectors, as in the cited predecessor work. No
address operation outside the six coordinate CNOTs, extra register, copy,
erasure or free address transformation is allowed.

Fix

```text
A = T12 T13 T21
```

with the product order shown. In row-bit encoding its matrix is `(6,3,4)`.
Exact binary row reduction gives `rank(A-I)=2`. A complete Cayley BFS over all
168 matrices in `G` gives coordinate-CNOT distance 3, with layer counts
`[1,6,24,51,60,24,2]`. The direct two-role word uses the three factors for
`A` with projector `E11`, followed by the same three factors with projector
`E22`; it realizes `diag([A],[A])` at cost six.

The broader [binary-affine rank-priced model](../binary-affine-register-bound/README.md)
supplies an optimistic four-call floor for two copies because their total
displacement rank is four. The test
therefore asks whether register mixing can use five or fewer coordinate-CNOT
calls, saving at least one from the direct bill of six. All costs inside this
abstract model are included: every label application is one paid call, and
there are no auxiliary roles or hidden cleanup calls. No physical bit-supplier
cost is inferred.

## Exact bounded result

The formal address algebra is the full group algebra of the finite group `G`.
Each of the four scalar-matrix entries is stored as an exact 168-bit coefficient
vector. The verifier enumerates the complete 36-factor alphabet: six address
labels times six rank-one idempotents.

Every coordinate-CNOT label is an involution, so each paid factor is
involutive. Any word of length at most five splits as a prefix of length at
most two and a suffix of length at most three. The verifier enumerates the
exact formal-matrix state balls at those radii, retains one shortest word for
each state, and checks for every prefix `P` whether `P^-1 diag([A],[A])` is in
the suffix ball. No match exists. Since the explicit direct word has length
six, the exact minimum in this fixed two-register model is six.

The replay records these deterministic receipts:

| State set | Layer sizes, including radius zero | Distinct states | SHA-256 |
|---|---:|---:|---|
| Formal-matrix prefix ball, radius 2 | `1, 36, 924` | 961 | `aedf570c8cd33c107fad63ce967cb06618e8d171081007e4eea851f16659cd48` |
| Formal-matrix suffix ball, radius 3 | `1, 36, 924, 21112` | 22,073 | `8455d502835c5a4bed62f8521061065e787248651462f374b444caa178e4ea96` |

The zero intersection is an exhaustive statement for the declared finite
formal alphabet and the five-call cutoff, not a natural-representation or
finite-column test. The verifier also compares 252 one-factor updates against
a separate sparse generic matrix-product implementation. The direct two-copy
word and the one-copy/one-identity three-call word are positive controls. All
six one-call omissions from the direct word and a wrong-label mutation are
rejected. Admitting `A` itself as an extra paid address label gives the
expected two-call endpoint and confirms that the six-label boundary matters.

## Scope, overlap and limits

The nearest result is the exact two-dimensional two-SWAP theorem in
[coordinate-cnot-register-bound](../coordinate-cnot-register-bound/README.md).
That package leaves a genuinely three-dimensional target with a rank-versus-
word-length gap as an open question. This note tests one such fixed target
using all six `GL_3(F2)` coordinate CNOTs, rather than its `GL_2(F2)` target
and two-label algebra. PR #1333 prices all binary affine labels by displacement
rank, so its alphabet is broader and its direct cost for `A` is different.
The active Discussion #1738 claim concerns a third dirty register for a D8
central target; it does not cover this target, dimension or register count.
Immediately before submission, the overlap helper refreshed 465 open PR records
and 444 Discussion records with complete pagination and no warnings. The exact
scope search returned this claim and this local package only; the helper does
not inspect code diffs or arbitrary nested files. Other pinned predecessor and
selected-record context is listed in [SOURCES.json](SOURCES.json). The claim
and its expiry are recorded in
[CLAIM.md](CLAIM.md) and [Discussion #1798](https://github.com/CrocSwap/integer-mult-bounds/discussions/1798).
The focused package is submitted as [PR #1804](https://github.com/CrocSwap/integer-mult-bounds/pull/1804).

The finite search does not address `r > 2`, other target matrices, translation
labels, general affine labels, arbitrary free address maps, rational frames,
physical scalar or hosting costs, compiler realization or selected-supplier
admission. It is not a multiplication construction and does not improve the
selected bound. The selected
`κ=836330098538459/500000000000000000` remains unchanged; the selected complex
side still binds. No new κ is claimed.

## Reproduce

From the repository root:

```sh
python3 -I -B research/gl3-coordinate-cnot-pair-seed1385e243/verify.py
python3 -I -O -B research/gl3-coordinate-cnot-pair-seed1385e243/verify.py
python3 scripts/research_package.py --package research/gl3-coordinate-cnot-pair-seed1385e243 --check-only
```

The exact expected summary begins:

```text
PASS_GL3_COORDINATE_CNOT_TWO_ROLE gl3=168 address_layers=[1, 6, 24, 51, 60, 24, 2] target_rank=2 target_length=3
```

Python 3.12 is registered in `VERIFY.json`. The local replay interpreter and
version are recorded in `VALIDATION.md` after final checks.

## Open next questions

Does adding one restored dirty register permit a five-call realization of this
same `GL_3(F2)` target? This isolates whether the only missed sharing resource
is an extra scalar role. First derive a pruning invariant for three-register
formal matrices, then use an exact search only if its precomputed state bound
fits a declared memory budget. The 168 scalar rank-one idempotents make a
direct radius-three expansion too large for this cycle.

## Credit

Credit commdata2338 for the preceding two-dimensional coordinate-CNOT target
and its explicit three-dimensional open question; credit Gareth Davidson's
PR #1333 for the rank-priced binary-affine model and augmentation normalization.
This package does not claim either operation alphabet or general register
mixing as new. Prepared by Cinna Davis with substantial OpenAI Codex
assistance. No independent human review or supplier adoption is claimed.
Apache-2.0.
