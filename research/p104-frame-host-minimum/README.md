# P104 frame-host minimum: exact hosting charges of the frame-indicator rows (no κ)

Result and claim type: **finite certificates** (exhaustive enumeration, direct
evaluation of every host) and a **scoped written proof** of the coset structure
(Lemma 1). No κ, no supplier admission, no selected-frontier change. This package
was produced by Nick Petalas.

## Setting

Open PR #7031 hosts frame 0 of the #7014 104-by-13 witness as a product of
root-line letters and charges its **40** monomials of degree at least 2 in the
simple-root chart; open PR #7047 asks (question 2) for the minimum charge among
the 2^16 functions of the four forms `p = 1 + x1 + x2 + x4`, `q = x0`, `r = x5`,
`s = x6 + x7`. This package keeps their charge model: a *host* of a row is a Boolean
function on `F_2^8` that equals the row's indicator on the root-line chart points;
its *charge* is the number of monomials of degree at least 2 in its algebraic normal
form (ANF); affine terms are free. A row is one of the 15 odd 8-cliques of #7014's
`frames.json` (13 P104 frames and the 2 excluded cliques). Scope is the 120 root
lines, or only the 104 P104 lines.

## Results

**1. Answer to #7047 question 2: exactly 16.** The 120 root lines attain only 15 of
the 16 values of `(p, q, r, s)`; the value `(0,0,0,1)` is missed, and each attained
value holds 8 lines. The frame-0 indicator is constant on every attained fibre, so
exactly two functions of the four forms host frame 0: the #7031 product
`(1+x0)(1+x1+x2+x4)(1+x5)(1+x6+x7)` with charge 40, and the product plus the
indicator of the missed fibre,

```text
(1 + x0)(1 + x5)(1 + x1 + x2 + x4 + x6 + x7)      charge 16, 24 monomials.
```

It is a product of three affine forms. Each is a sum of an odd number of letters, since
the 120 letters span every affine function, so its charge is 16 by the #7047
convention that sums of letters are free.

**2. Lemma 1 (structure of every row).** Let `Q = Σ x_i + Σ x_i x_j` over the 7 edges
`02, 13, 23, 34, 45, 56, 67` of the E8 diagram in the simple-root chart (the mod-2
value of `(v, v)/2`). The 120 chart points are exactly `{x : Q(x) = 1}`. Each of the
15 cliques is a coset `F = a + W` of a 3-dimensional subspace `W`. Let `B` be the polar
form of `Q`; it is nondegenerate because the Cartan matrix is unimodular. Then:

- the other 32 cosets of `W` split as 28 that hold exactly 4 lines, 3 that hold none,
  and `F` itself with 8 (8 + 28·4 = 120);
- the 3 empty cosets and `F` make the 5-flat `a + W^⊥`, so `(a + W^⊥) ∩ lines = F`;
- hence exactly 8 functions invariant under `W` host the row, and exactly 5 flats
  `G ⊇ F` meet the lines only in `F`: the subspaces between `W` and `W^⊥`
  (`F`, three 4-flats and `a + W^⊥`).

*Proof.* `Q = 1` on `F` gives `Q(a+w) = 1`, so `Q(w) = B(a,w)` on `W` and `W` is
totally isotropic. For a coset `c + W`, `Q(c+w) = Q(c) + B(a+c, w)`: constant when
`a + c ∈ W^⊥`, otherwise a non-constant affine function, which is 1 on exactly 4 of
the 8 points. `Q'(x) = Q(a+x) + Q(a)` has 120 zeros, so it is elliptic; `W` is totally
singular for `Q'`, hence maximal, and `W^⊥/W` is anisotropic, so `Q' = 1` on
`W^⊥ ∖ W`, i.e. `Q = 0` on the three other cosets of `a + W^⊥`. ∎ `verify.py`
checks every step on all 15 cliques.

**3. No host of degree at most 2, for any row.** For each clique `verify.py` finds a
3-flat `S` inside the root lines with `|S ∩ F| = 1`. A polynomial of degree at most 2
sums to 0 over a 3-flat, while the indicator sums to 1 over `S`, so no host of degree at
most 2 exists. The linear system over `F_2` agrees: it is inconsistent for degree 2 on
both scopes. Hosts of degree at most 3 form an affine space of dimension 9 on the
120-line scope (`f + (1+Q)·affine`, 512 hosts) and of dimension 11 on the 104-line scope.

**4. Exact minima in three named classes.** The classes are the 5 flat indicators, the 8
`W`-invariant hosts, and all hosts of degree at most 3. On the 120-line scope the flat
minimum equals the invariant minimum in every row. For frame 0 the minimum is 16 over
flats and invariant hosts, and 14 over all cubic hosts (a unique minimiser).

**5. Explicit sparser hosts (upper bounds).** A seeded randomized search
(`search.py`: information-set decoding over the 256 monomials, 3000 orders per row,
fixed seed) found hosts below the exact class minima in 10 of the 15 rows (F1, F2, F4,
F5, F7, F8, F9, F10, F12, X1) and equal to them in the other 5. Every host in
`data/hosts_*.json` is re-evaluated at every scope point by `verify.py`. The frame-0 host
of charge 14 is

```text
1 + x0 + x1 + x2 + x0*x2 + x0*x3 + x0*x1*x3 + x0*x2*x3 + x4 + x0*x3*x4 + x5 + x1*x5 +
x0*x1*x5 + x2*x5 + x0*x2*x5 + x4*x5 + x6 + x5*x6 + x7 + x5*x7 + x0*x5*x7 + x0*x6*x7
```

It has 8 free terms (the constant and `x0, x1, x2, x4, x5, x6, x7`) and 14 charged
terms (7 of degree 2 and 7 of degree 3). It is the same polynomial that `verify.py`
asserts.

Charge of the best host by row (monomials of degree at least 2). F0 to F12 are the 13 P104 frames and X0, X1 the two excluded cliques. "Letter product" is the #7031 hosting word, the indicator of `span(F)`. The two exact columns are minima over the named classes on the 120-line scope. The last two columns are the explicit hosts in `data/hosts_T120.json` and `data/hosts_P104.json`; the 104-line run starts from the 120-line hosts, which also host on 104 lines.

| row | letter product | exact flat/invariant min | exact cubic min | explicit host, 120 lines | explicit host, 104 lines |
|---|---:|---:|---:|---:|---:|
| F0 | 40 | 16 | 14 | 14 | 14 |
| F1 | 111 | 24 | 24 | 20 | 18 |
| F2 | 89 | 26 | 26 | 20 | 16 |
| F3 | 105 | 34 | 22 | 22 | 22 |
| F4 | 83 | 36 | 24 | 22 | 19 |
| F5 | 93 | 10 | 18 | 6 | 6 |
| F6 | 35 | 27 | 23 | 23 | 23 |
| F7 | 101 | 16 | 14 | 10 | 10 |
| F8 | 111 | 42 | 30 | 26 | 23 |
| F9 | 103 | 28 | 28 | 18 | 16 |
| F10 | 107 | 24 | 24 | 14 | 14 |
| F11 | 58 | 28 | 21 | 21 | 21 |
| F12 | 90 | 13 | 17 | 9 | 9 |
| X0 | 11 | 7 | 7 | 7 | - |
| X1 | 87 | 34 | 30 | 20 | - |

Exact class minima on the 104-line scope, as (W-invariant, cubic) for frames F0 to F12:

```text
[(15, 14), (24, 24), (26, 23), (34, 22), (36, 21), (10, 18), (27, 23), (16, 14), (42, 30), (28, 28), (24, 24), (28, 21), (13, 17)]
```


The product-of-letters column is the charge of the indicator of `span(F) = F ∪ W`:
a letter of line `l` is `1 + B(l, x)`, it equals 1 on all of `F` only when `l ∈ F`, and
the common-1 set of the eight frame letters is `span(F)`. The column reproduces
#7031's 40 (frame 0) and #7046's 111 (frame 1) and totals **1126** over the 13
frames. The best explicit hosts total **225** on the 120-line scope and **211** on
the 104-line scope. Rows are chosen independently, so these are separate bills, not a
joint minimisation.

## Evidence and reproduction

Python 3.12, standard library only. The verifier runs in under one second and each
generator command takes about 3 minutes. From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-frame-host-minimum/verify.py --table
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B research/p104-frame-host-minimum/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-frame-host-minimum
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-frame-host-minimum --check-source-history
# optional: regenerate the explicit hosts (deterministic; about 3 minutes each)
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-frame-host-minimum/search.py --scope T120 --iterations 3000 --seed 20261110 --write /tmp/hosts_T120.json
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-frame-host-minimum/search.py --scope P104 --iterations 3000 --seed 20261110 --incumbent /tmp/hosts_T120.json --write /tmp/hosts_P104.json
```

`verify.py` prints `PASS_P104_FRAME_HOST_MINIMUM` with the key numbers. Its failure
controls reject a corrupted host and a wrong form. The ANF of the two four-form hosts
is computed twice, by polynomial multiplication and by the subset-sum transform, and
both must appear in the enumerations built by two other methods (cosets and a linear
system over `F_2`). `data/frames.json` is #7014's witness as vendored by #7031 and
#7047 (sha256 `c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d`,
checked); the chart convention and the root-line map follow #7031 and #6933.

## Limitations

- The minimum over **all** Boolean functions is not claimed. The class minima are
  exact only inside their classes, and the explicit hosts are the best found by a
  heuristic of fixed budget (a failed search below them is not a lower bound). Several
  rows' explicit hosts lie below every exact class minimum, so those minima are not
  the true minima.
- The charge counts ANF monomials of degree at least 2 in the simple-root chart, as
  in #7031 and #7047. It is not a signed invoice, a gate count or a supplier cost.
  The 40 frame-0 monomials of #7031 and the hosts here are not named as primitives of
  the selected #6030 invoice (open question of #7048), so no κ follows.
- Hosts here are Boolean functions, not shown to be realised by circuits of letters
  beyond the three-form host in result 1. The joint thirteen-row bill with shared
  monomials (#7046 question 2) is not minimised.
- No predecessor result is replayed; the 40 and 111 appear as outputs of this package's
  own census.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. **True per-row minimum.** What is the minimum charge over all Boolean hosts? The
   explicit hosts of frame 5 (6), frame 12 (9) and frame 7 (10) are below every exact class
   minimum. First step: enumerate all hosts of degree at most 4 for one small row
   (2^37 hosts, compiled), or prove a coset-leader lower bound for excluded clique
   X0 (best known 7). Blocked by the size of the search; no cheap certificate is known.
2. **Joint thirteen-row bill.** If a shared monomial is charged once, what is the
   smallest union over the rows? First step: take the 8 invariant and 512 cubic hosts
   per row, which are exactly enumerable, and minimise the union of supports by exact
   search. Blocked by the charging rule for a joint circuit (#7046 question 2).
3. **Invoice primitives.** Can the chart monomials of these hosts be named as
   primitives of the selected #6030 invoice? First step: make one constructor read one
   exponent and check the image of all monomials of the charge-14 host. Blocked as in
   #7048: the present constructors read frame dimensions, idle lengths and a diagonal
   popcount only.

## Credit

This package was produced by Nick Petalas. Predecessors, cited and not replayed:
unpaidmoon, #7031 (product hosting and the 40-monomial charge, the chart convention
and the four forms), #7046 (frame 1, 111 new monomials), #7047 (the question answered
in result 1) and #7014 (the 104-by-13 frame partition, `frames.json`); DreamingOfClouds,
#6933 (ports and the E8 line map, merged). New work is Apache-2.0.
