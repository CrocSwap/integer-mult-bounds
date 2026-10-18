# Sharp COPY69 for the A2+E6 nine-normal P112 decoder

**Scoped exact optimum, including arbitrary complex row shifts. No new supplier
or kappa.** The fixed A2-weight plus E6-root-basis family proposed by joaqcoo in
[PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224) has minimum
separate-term COPY cost **69** on the standard coordinate-frame P112. All nine
terms can be active at the minimum, with costs

```text
(1, 8, 8, 8, 8, 9, 9, 9, 9).
```

This resolves the **A2+E6 / named-P112** branch of the explicit handoff in
[a8-one-pair-frame-floor](../a8-one-pair-frame-floor/README.md#open-next-questions).
PR1224 supplied the family, normal form and a bounded heuristic search, not this
optimum. The A8 simplex floors, retained-coordinate sparse ninth-normal
PR1325, and fixed-partition PR1962/1988 do not cover these changed normals and
arbitrary independent row parameters. The result is not an enlargement of a
finite coefficient box: every complex parameter is covered by the proof below.
The usual coordinate decoder costs 64 but has a different normal family.

## Exact model and source binding

Let `r_i` be the 120 norm-two E8 root-line representatives, in the ordering of
PR1224's pinned `e8lab.py`. Remove the greedy orthogonal frame with indices
`[0,13,90,99,108,113,118,119]`, leaving 112 live lines. Write

```text
G_ij = <r_i,r_j>,       N_ij = (G_ij+1) mod 2.
```

The nine column normals `b_k` are precisely the output named
`A2 weights + E6 root basis` in PR1224's `build_frames()`. Their doubled
coordinates, the puncture, the binary character basis and the witness supports
are recorded in [RESULT.json](RESULT.json). A separately implemented checker
uses explicit rational coordinates and independently reconstructs the roots;
it imports no predecessor or primary-verifier code.

The family consists of every `D` over the real or complex numbers satisfying

```text
T_jk = <r_j,b_k>,             D T^transpose = 2G.
```

Transpose is ordinary transpose. Each term is charged
`rank_F2 N[X_k,Y_k]` for its **actual nonzero** row and column supports. Terms
are charged separately, even when their scalar contributions cancel.

The normals have rank eight and unique dependency
`b_0+b_1+b_2=0`; the remaining six have zero dependency coefficient. Let
`c_i` be the unique representation of `2r_i` with `c_i0=0`. Since the live
roots span eight-space, PR1224's normal-form argument gives exactly

```text
D_ik = c_ik - t_i  for k=0,1,2;
D_ik = c_ik        for k=3,...,8;       t_i arbitrary in C.
```

Thus only the first three row supports vary. The finite geometric check gives
column-label ranks `(9,9,9,8,8,9,9,9,9)`. The six fixed terms cost
`(8,8,9,9,9,9)`, totaling **52**. In particular, charging all fixed terms by
their row-label rank would be wrong: term 4 has row rank nine but pairing rank
eight. Both checkers calculate the actual support-pair ranks.

## Proof of the sharp bound

The following finite lemma and elementary argument apply to every complex
choice of the 112 independent parameters, not merely the displayed witness.

### Binary deficiency formulation

The live labels span a nondegenerately paired nine-dimensional binary space.
For variable term `k`, let `K_k` be the subspace of binary characters vanishing
on its row support `X_k`, and put `delta_k=dim K_k`. Because `Y_k` has full
label span, its cost is exactly `9-delta_k`.

For `k<l`, define the live conflict set
`S_kl={i:c_ik != c_il}`. If `u in K_k` and `v in K_l`, the supports of their
character codewords cannot intersect on `S_kl`: such a root would force both
`D_ik=D_il=0`, requiring `t_i=c_ik=c_il`, a contradiction. Define

```text
R_kl(u) = {v : supp(u) intersect supp(v) intersect S_kl is empty}.
```

This is a binary subspace, since it imposes linear vanishing conditions on
`v`. The necessary compatibility is `K_l subset R_kl(u)` for every `u in K_k`.
It is also sufficient to realize any proposed compatible kernel subspaces:
for each root, the coefficients forced to zero have equal `c_ik`, so choose
that common value for `t_i`; if none is forced, choose any value.

### Complete finite compatibility lemma

There are exactly 512 characters, including zero. The primary checker uses
PR1224's ordered character basis; the independent checker uses low-pivot
Gauss-Jordan elimination and a different basis. Both enumerate every character
pair and every compatible pair of nonzero partner characters.

For each pair, the table lists the sizes of `R_kl(u)` for all 511 nonzero `u`:

| Pair | Complete size census | Unique size greater than four |
|---|---|---|
| 0,1 | 508 of size 4; 2 of size 2; 1 of size 512 | `u=1`, dimension 9 |
| 0,2 | 255 of size 2; 254 of size 4; 1 of size 1; 1 of size 256 | `u=446`, dimension 8 |
| 1,2 | 255 of size 2; 254 of size 4; 1 of size 1; 1 of size 256 | `u=256`, dimension 8 |

Next fix a possible large side `k`, with other sides `j,l`. For each nonzero
compatible pair `(u,v)` on those other sides, inspect
`R_kj(u) intersect R_kl(v)`. There is **exactly one** pair whose intersection
has dimension greater than two:

| Large side | Other sides | Exceptional `(u,v)` | Intersection dimension |
|---|---|---|---|
| 0 | 1,2 | 1,446 | 8 |
| 1 | 0,2 | 1,256 | 8 |
| 2 | 0,1 | 446,256 | 7 |

The full triple histograms, not just the maxima, are retained in RESULT.json.
Character IDs depend on the primary basis; the independent implementation
re-derives the same unique-exception dimensions without assuming those IDs.
These are exact finite facts about this geometry, not a floating-point search
or an external classification theorem.

### Deficiency sum is at most ten

If all three `K_k` are nonzero and each has dimension at most two, their sum
of dimensions is at most six. Otherwise choose a side with dimension at least
three. **Every** nonzero pair of vectors on the other two sides must be the
unique exceptional pair in the second table. Hence each other side is
one-dimensional. The large side has dimension at most eight (seven for side
2), so the total is at most ten.

If one `K_k` is zero, only two subspaces remain. If both have dimension at
most two, their sum is at most four. Otherwise the first table forces every
nonzero vector in the partner to be its unique exceptional character, so
that partner has dimension at most one and the other at most nine. If the
partner is also zero, the remaining dimension is at most nine. Thus in every
case `delta_0+delta_1+delta_2 <= 10`.

Consequently the variable terms cost at least `27-10=17`, and the complete
bill is at least **52+17=69**.

### All-active attainment

Take `K_0=R_01(1) intersect R_02(446)`, `K_1=span(1)` and
`K_2=span(446)`. Their dimensions are `(8,1,1)`, and they are compatible.
The resulting rational witness is particularly small: relative to the
`c_i0=0` base, set **`t_45=-4` and all other `t_i=0`**. It satisfies all
12,544 all-pairs identities, and actual support-pair ranks give
`(1,8,8,8,8,9,9,9,9)`. All nine terms are nonzero. The first term has a
singleton row support, so discarding it as a cancelling or inactive term
would give a false invoice.

## Full optimistic conditional screen

Before the compatibility optimization, the elementary support-union bounds
`rank X_k + rank X_l >= rank span S_kl` give `(8,9,9)` on the three pairs,
hence variable cost at least 13 and total cost at least **65**. This already
fails the assigned five-percent improvement gate in the following deliberately
favorable **conditional substitution model**:

- Keep every selected noncentre paid child: `{1:2412,2:418,3:432,4:142,5:82}`,
  mass 5,522, including their original source/target and restoration work.
- Replace the selected eight rank-eight centre children by total centre cost
  `C`; allow *all* that mass as fractional rank-nine children, even though the
  actual witness has a rank-one term.
- Retain width 73, 896 families / 9 calls, one unpaid coordinate per family,
  rank-51 idle cap and the conditional coverage law `mass=72W+C N`.
- Set **all additional** gather, frame, restoration, hosting and precision
  overhead to zero. No physical implementation of this substitution is asserted.

Idle mass remains exactly 1,646 per call. Since centre ranks are at most nine,
per-mass child cost decreases with rank, and `C>=69`, the exact result gives
this lower bound on the complete conditional moment:

```text
(9/896) [ sum_noncentre n_r (r/73)^(1-a)
          + (69/9)(9/73)^(1-a) + (1646/51)(51/73)^(1-a) ].
```

The pinned rational-interval engine certifies the root bracket
`[1452819253108,1452819253109] / 10^15`, giving conditional kappa cap below
**0.001450712**. Even the preliminary COPY65 screen has root upper bound
`1643089627792/10^15`, below the selected word's ceiling
`0.001690054109089`, rather than five percent above it. An independent
integer-power computation proves the final relaxation already exceeds one at
`a=1/625`; it uses no logarithm or exponential engine.

This closes physical construction effort for this **fixed-noncentre model**.
It does not exclude reorganizing other work, another coverage law or shared
physical copies. COPY69 alone is not a universal moment bound.

## Reproduce and evidence

From the repository root, standard library only:

```sh
uv run --python 3.12 --no-project python -I -B research/a2-e6-nine-normal-floor/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/a2-e6-nine-normal-floor
```

`verify.py --write` explicitly regenerates RESULT.json; default replay is
read-only. The registered replay also runs `independent.py`, six focused
semantic test groups, and optimized (`-O`) primary replay. Controls reject a
wrong coefficient, a false binary compatibility, an altered executable source,
and a one-coordinate pseudo-kernel shift; they also exercise genuinely complex
parameters and the incorrect full-column-rank shortcut. Every external input
is declared and SHA256/Git-blob pinned in SOURCES.json. Executable predecessor
bytes are authenticated **before** import. SELECTION.json retains the full
independent chooser draw, and TASK.json records scope and overlap.

The universal argument is written, not proof-assistant checked. No independent
human review, selected cold replay, physical supplier admission or hosted-CI
success is claimed.

## Open next questions

- **A7+A1 with arbitrary row shifts:** does the other explicit PR1224 family
  improve COPY on a named P112? Derive its fixed bill and complete ratio-class
  constraints first. Eight variable terms make the three-subspace exceptional
  pair proof inapplicable; this is a genuinely different compatibility problem.
- **Changing the E6 basis or puncture:** can a specified normal/puncture change
  reduce the six forced terms and the variable floor enough to pass a complete
  budget? First calculate the fixed support-pair bill and the elementary
  support-union floor before attempting synthesis. The present theorem only
  covers the pinned basis and standard puncture; physical realization remains
  an additional blocker.

## Provenance and credit

Base `e112d71c8d7bb32435debcc54df932593dd8223a`; independent chooser seed
`814c825e12629ac65e009a4beab63757`, complex-mechanisms / complex-rank-shape-decoder.
The scope is explicitly **changed** from physical synthesis to the named
support-family obstruction. Coordination:
[round3 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931181).

Credit **joaqcoo / PR1224** (`00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`)
for the family, model implementation, normal form and ratio classes;
**Philipp / mightyOil / PR1248**, **commdata2338 / PR1304** and
**Hanson Sun / bbMisk / a8-one-pair-frame-floor** for the deficiency method and
explicit follow-up; **DreamingOfClouds / PR717/595/446** for the decoder and
COPY model; **Joel Pulikkan / GamingPuzzled / PR620** for coordinate COPY64;
**themilkman216 / PR968** and **woklerx / PR1077** for surrounding eight-term
bounds; **Sagar Thakrar / PR1012** and **Douglas Colkitt / PR1240** for the
coverage and ceiling model. Their frozen files are unchanged.

Prepared for **Adam Gall** with substantial **OpenAI Codex assistance** in
research, proof, implementation, checking and writing. Apache-2.0.
