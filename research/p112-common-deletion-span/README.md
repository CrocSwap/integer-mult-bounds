# A sharp common-deletion bound for the P112 quantifier fixture

For the two literal six-dimensional label spaces in [FIXTURE.json](FIXTURE.json),
let `X = Lambda(V1) union Lambda(V2)` inside the 112 E8 root lines `P112`.
For a nonzero real direction `h`, define

```text
Off(h) = {r in P112 : h dot r != 0}
H(P)   = {h : binary_rank(labels(Off(h) minus (X union P))) <= 7}.
```

**Result.** For every common set `P` of at most four lines,
`dim_R span H(P) <= 3`. Equality is attained. Allowing a different four-line
set for each direction instead gives a sharp span of five. The theorem also
holds over the complex numbers, by the argument below.

There are exactly ten admissible projective directions in the separate-set
relaxation. This package classifies **all real directions**, not only the 5,680
records in the predecessor's direction catalogue. All ten are rational root
directions. [RESULT.json](RESULT.json) lists them and their unique minimal cuts.

This completes one fixed-space common-set problem left by the
[PR3158 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-18997271).
It does not settle C5 for other pairs of spaces, refute the common-P S66+P
conjecture, construct a supplier, or improve the selected kappa.

## Proof and finite checks

The eight omitted roots and both bases are literal inputs. Roots have squared
length eight because coordinates are doubled. If `c` is a root's integral
coordinate vector in the displayed Bourbaki simple basis, its label is
`256 + sum_j ((c_j mod 2) * 2^j)`. The verifier reconstructs every root from
these coordinates and checks that positive roots have nonnegative simple
coordinates. It does not read predecessor code or tables.

1. **Cardinality bound.** The two spaces contain 20 and 16 live lines, with
   intersection four, so `|X| = 32`. Enumeration of all 43,435 codimension-two
   subspaces of `F2^9` proves that a rank-at-most-seven set of live labels has
   at most 36 lines. The enumeration uses the unique ordered representatives
   `0 < a < b < a xor b` of each two-dimensional annihilator. Thus a qualifying
   `h` has `|Off(h)| <= 32 + 4 + 36 = 72`. At least 40 live roots are orthogonal
   to it.
2. **Coverage of arbitrary directions.** The E8 reflection group is finite
   because it permutes the 240 roots. Choose a vector `rho` having positive
   pairing with each simple root. Maximizing `rho dot w(h)` over the finite
   orbit moves `h` into the closed dominant chamber: reflecting a negative
   simple pairing would increase this maximum. A positive root has zero
   pairing exactly when its simple support lies in the zero simple pairings.
   Its orthogonal root system is therefore a Weyl translate of a proper
   parabolic subsystem.

   Check all 255 proper simple-support subsets. Those with at least 40 root
   lines are the E7 and D7 orbits. Their closures under all eight simple
   reflections have 120 and 1,080 members. Intersecting with this P112 leaves
   exactly 248 systems with at least 40 live lines. The other D7 systems have
   only 36 or 39 live lines and cannot qualify. Each retained system has rank
   seven, hence determines one rational projective normal. No generic plane
   of directions or unenumerated irrational direction remains.
3. **Deletion supports.** Forty of the 248 residual label sets have rank eight;
   208 have rank nine. Enumerate all 512 binary characters. At rank eight,
   a cut lowers rank to seven exactly when it contains a nonzero restricted
   character support. At rank nine, it must contain the union of two distinct
   nonzero restricted supports. These supports are independent because the
   restricted character code is injective at rank nine. Retain only unions
   of size at most four, then remove inclusion-dominated cuts.

   Exactly ten normals qualify. Each has residual rank eight and exactly one
   minimal cut of size at most four. The ten normals together span five.
4. **One common set.** For any `P`, take the union `P0` of the minimal cuts of
   every direction it admits. Then `P0` is a subset of `P` and admits exactly
   the same directions. Enumerating these cut unions is therefore complete,
   even though it does not list every irrelevant four-line superset. There
   are exactly six unions of size at most four:

   | Deleted labels | Dimension of admitted directions |
   |---|---:|
   | empty | 0 |
   | 279, 341 | 2 |
   | 275, 337 | 2 |
   | 275, 279, 337, 341 | **3** |
   | 409, 411, 473, 475 | 2 |
   | 317, 319, 381, 383 | 2 |

   Exact rational elimination proves the claimed upper bound and its sharpness.

For a complex `h = a + ib`, a generic real linear combination of `a` and `b`
has exactly the same zero pairings on the finite root set. Its orthogonal roots
are one of the rank-seven systems just classified. Both `a` and `b` annihilate
that system, so `h` is a complex multiple of its rational normal. The same ten
projective directions and the same dimension bound apply over `C`.

## Reproduction

Python 3.12 or later, standard library only. Run from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p112-common-deletion-span
```

Direct commands also work without Git or predecessor files:

```sh
python3.12 -B research/p112-common-deletion-span/verify.py
python3.12 -O -B research/p112-common-deletion-span/test_verify.py
```

Expected marker:

```text
PASS_P112_COMMON_DELETION_SPAN real_directions=10 separate_span=5 common_span=3 states=6
```

The direct proof check takes about 0.12 seconds on the recorded host. To preserve
an external receipt, pass `--output "$RUN/receipt.json"`. Set `TMPDIR="$RUN/tmp"`
for tests and the generic package launcher, with an existing session-owned
external `RUN/tmp` directory. The verifier never rewrites committed evidence.

[Evidence and implementation limits](EVIDENCE.md) lists the separate oracles,
rejection controls and bounded-resource decisions. The written argument and
finite checks are author-checked, not proof-assistant or independent human
verification. No native supplier, physical implementation, outer transfer or
full selected-result replay was run.

## Open next questions

- Can the same common-cut method finish a complete V1-orbit slice of C5?
  Start with the exact minimal-support representation here, then enumerate its
  V2 partners with source-bound coverage. The number of space pairs and the
  applicable per-cell target must be specified before claiming a full result.
- Which C5 cells actually need a bound of four or more? Bind the relevant
  S66+P basis-kill application to its numerical target before another census.
  This theorem is only a calibration fixture, not that dependency audit.

## Sources and credit

- DreamingOfClouds, [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
  at `708f0ad8928c383de8294aea3c126e9461d2066d`, supplies the C5 handoff,
  FINITE/FINITE2 and the retained decoder-floor lineage.
- Nick Petalas, [PR3158](https://github.com/CrocSwap/integer-mult-bounds/pull/3158)
  at `8e2167bac550bd653bb74c50c1f7c3f14b6c1f70`, supplies these literal spaces,
  simple-root labelling convention and the five-direction quantifier witness.
  Its twelve-common-deletion result concerns its five specified directions.
  This package instead classifies every direction at common budget four.

The new Weyl-coverage and shared-cut computation imports neither predecessor
implementation. Exact Git blobs, SHA-256 values and the fixture extraction are
recorded in [SOURCES.json](SOURCES.json). Canonical main at assignment is
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
Apache-2.0. Development and internal checking used substantial automated
assistance. No independent human review is claimed.
