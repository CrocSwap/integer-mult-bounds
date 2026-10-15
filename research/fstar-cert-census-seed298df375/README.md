# fstar-cert-census-seed298df375

**Scoped negative result (no new kappa, no frontier change).** An exact falsifier
census for open problem **F-star** of `research/root-unit-decoder-lemmas`
(section 7, OPEN): over 196 declared exact 3-total rational decoders on
v = 4..12 lines, every instance carries a machine-checked labelling/order
witness with `|S| >= floor(2v/3)`, and no falsifier was found. This is evidence
for F-star over the declared domain, not a proof of the statement.

## Scope and question

For a rational 3-total decoder `M = sum_{j=1..3} p_j q_j^T` on v lines with
`M_tt != 0` on every line, the source package defines an **L8 labelling**:
F2 vectors `a(t)` supported in `Omega(t) = {j : p_j(t) != 0}` and `b(s)`
supported in `Psi(s) = {j : q_j(s) != 0}`, with `K_ts = a(t) dot b(s) mod 2`.
`cert(M)` is the largest `|S|` admitting an order with `K_tt = 1` on S and
`K_ts = 0` at every incidence `M_ts = 0` with t before s. F-star states
`cert(M) >= floor(2v/3)` for every exact 3-total decoder. The source package's
proven consequence: F-star closes every open T = 3 window at once. The source
states F-star as OPEN with about 90 sampled configurations at `cert = v`
(RECORDED, not reproduced there).

Both bounds in this package are reading-independent: `cert(M)` does not depend
on any pairing B, and the witnesses prove `cert(M) >= |S|` for the sampled
decoders under any reading of "exact decoder on a root unit". A found falsifier
would have been a falsifier under the universal reading (any 0/1 unit-diagonal
B with ones only where M vanishes); the unit-attached reading needs unit Gram
tables and remains open question 2 in TASK.json.

## Method

Two exact sides, stdlib only, deterministic (fixed seeds `20261015 + 1000*family
index + 17*v + i`):

- **Side B (lower bound on `cert`).** Deterministic local search over labellings;
  each labelling is scored by the exact maximum acyclic subset of the incidence
  digraph (subset DP), and the maximizing subset and sink-peeling order are
  reconstructed and replayed by an independent witness checker.
- **Side A (upper bound on `cert`, falsifier hunt).** The source package's
  proven chain `cert(M) <= sum_j rank_F2 B[R_j, A_j]` for every admissible B
  (0/1, unit diagonal, `B_ts = 1` only where `M_ts = 0`, s != t; the chain's
  proof uses only these two properties, so asymmetric B are included). The cost
  is minimized by exhaustive enumeration when the admissible pair count is at
  most 10 (always at v <= 5) and by deterministic single-bit local search
  otherwise. Any instance with minimum cost below `floor(2v/3)` would falsify
  F-star.

Domain: v in 4..12, exactly 3 totals, factor entries in `{-2,-1,0,1,2}` with
nonzero diagonal; three families: **dense** (random factors), **config**
(`M = P Q^T` with `P,Q` over `{-1,0,1}`, the rank-3 configuration model of
https://github.com/CrocSwap/integer-mult-bounds/pull/2111), **tied** (a
2-adic-weighted alphabet, retained only when tied minimal valuations cover at
least half the lines: the obstruction named in the source section 7).

## Evidence

`python3 -B research/fstar-cert-census-seed298df375/verify.py` recomputes
everything and writes `CERTIFICATE.json` and `CENSUS-RECORDS.json`
(census digest `3237519deb9ec377f5a8a86b7b4b1e8197074ee8d0dd0e653cfcea1104c9e6e8`).

| family | instances | resolved with witness | falsifiers | min witness ratio |
|---|---:|---:|---:|---:|
| dense | 70 | 70 | 0 | 8/9 = 0.889 |
| config | 70 | 70 | 0 | 6/7 = 0.857 |
| tied | 56 | 56 | 0 | 7/8 = 0.875 |

All 196 instances resolved: `cert(M) >= witness >= floor(2v/3)`. No falsifier
and no unresolved instance. The worst instance (lowest witness ratio) is the
config instance at `v = 7`, seed `20262138`: witness 6 against threshold 4, so
`cert(M) in [6, 7]` there (12 is its exact admissible-B cost minimum,
which is a weaker upper bound than the seven-line cardinality cap). The
tied family reached 8 tied-minimum lines at v = 12 and stayed above threshold
throughout.

Controls (all in `verify.py`, all required to pass):

1. Three tiny-domain instances (v = 3) are certified by exhaustive enumeration
   of every labelling; the search engine must reproduce those exact values
   (3/3 agree).
2. A corrupted witness (one `K_tt` broken) and a wrong order at a binding pair
   are both rejected by the independent witness checker.
3. The `floor(2v/3)` threshold table is checked against hand values for
   v = 4..12.
4. A hand-checkable diagonal decoder (`p_j = q_j = e_j`) gives `cert = 3`.
5. The proven chain `cert(M) <= cost(B)` is rechecked on every census instance,
   and an exact-chain control pins `brute_cert = 4 <= min_cost = 7`.

## What is not claimed

F-star is **not** proved: witnesses are lower bounds on `cert(M)`, and only the
recorded 196 instances are covered. The census is not exhaustive over decoders;
it is exhaustive over labellings only for the tiny controls. `cert(M)` values
are not pinned exactly above v = 3 (the worst instance above has `cert` in
[6, 7]). Nothing here changes kappa, any supplier, the selected record, or any
window; the T = 3 window closure remains conditional on F-star. The universal
versus unit-attached readings of the quantifier are not separated.

## Reproduce

From the repository root, Python 3.10+ standard library only:

```sh
python3 -B research/fstar-cert-census-seed298df375/verify.py
python3 scripts/research_package.py --package research/fstar-cert-census-seed298df375 --check-only
python3.12 scripts/research_package.py --package research/fstar-cert-census-seed298df375
```

Expected markers:

```text
PASS_FSTAR_CERT_CENSUS instances=196 resolved=196 falsifiers=0 unresolved=0 min_ratio=0.8571 digest=3237519deb9ec377
PASS_FSTAR_CERT_CONTROLS bruteforce=3 diagonal_cert=3 chain_cert=4
```

The registered CPython 3.12 replay prints `PASS_REGISTERED_RESEARCH_PACKAGE
research/fstar-cert-census-seed298df375 outcome=completed`. `make` is not
installed on the authoring host; the scripts above are the underlying commands.

## Open next questions

1. **Exact `cert(M)` for the worst instance** (config, v = 7, seed 20262138,
   `cert` in [6, 7]). Why it matters: it is the smallest witness ratio seen and
   the natural place to look for sub-v certificates, which would sharpen what
   F-star can promise. First step: branch-and-bound over labellings at v = 7
   with the maximum-acyclic-subset bound, or a larger deterministic search
   budget. Blocker: none structural; needs a longer exact run.
2. **Universal versus unit-attached readings.** Why it matters: a separation
   decides whether a future falsifier refutes the lemma as stated or only its
   universal reading. First step: wire A3/A4/D4 Gram tables into `min_cost_pairing`
   and compare admissible-B minima on the same decoders. Blocker: unit tables
   are not in this package.
3. **Tied-minima family at v = 13..18** (see TASK.json). The named obstruction
   accumulates with v; the census stops at v = 12.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged package
`research/root-unit-decoder-lemmas` (root units, Lemmas A and B, the L8 lemma;
[PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds, with Claude Opus 5.5 (Anthropic) via Claude Code
assistance). The rank-3 configuration
model, the `tied_min` / `cex_min_1` examples and their certificate limits are
DreamingOfClouds' work in https://github.com/CrocSwap/integer-mult-bounds/pull/2111
and https://github.com/CrocSwap/integer-mult-bounds/pull/2162 (one-copy
certificates stopping at 11 and 18 there; this package does not restate those
examples). The adjacent independent CR2/B2 audit is
https://github.com/CrocSwap/integer-mult-bounds/pull/2293 (Aaron Wang). The
source README is pinned as an input in SOURCES.json.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review claimed). New work in this package is Apache-2.0.
