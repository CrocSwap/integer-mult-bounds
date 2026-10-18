# P112 two-total source-support thresholds

**Scoped exact support obstruction; no cheaper decoder or new κ.** With the
eight P112 coordinate readers retained, two added totals cannot lower the
separate-total COPY rank below 64 if the union of their source supports has
at most **43 of the 112 ports**. This holds for arbitrary complex
coefficients and even when both added factor matrices have rank two with
overlapping coordinate supports. The open unrestricted two-total case
remains open.

The exact source-deletion thresholds for one retained reader to lose
`d=1,...,8` rank units are

| Rank units lost | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Minimum deleted source ports | 24 | 36 | 44 | 48 | 52 | 54 | 55 | 56 |

Every coordinate has this same sequence. The first entry, 24, is the
erasure distance of a coordinate support found by @commdata2338's PR1375
(`research/p112-two-coordinate-small-rectangle/`); the higher entries
36..56 and the cross-reader statements are new here. Each of the 28 reader pairs
shares exactly one first-drop set of size 24; no such set hits three
readers. A freely chosen deletion set requires at least 40 ports to lower
three coordinate ranks. These are exact finite code properties, not
physical source costs. At union size below 44, at most four readers can
drop, and at most one can lose two rank units. The verifier finds exactly
42 four-reader cuts of size 40 and excludes a fifth reader with fewer
than four more ports.

The 43-port floor also charges both added totals. An exact
511-functional census (re-implemented here; the 503/8 split is Mihir
Srivastava's #845 premise, also rechecked by @adamgall's
`research/p112-gram-support-seed80/`) shows every nonzero added reader in
`col_C(X)` has binary dual span at least eight and sees every live source
label. If an added source has `m` nonzero sites, its COPY rank is at least
the smallest `r>=1` satisfying `m<=2^(r+1)`. This support-from-rank step
is the same rank-nullity argument as Hanson Sun / @bbMisk's PR1432
(`research/p112-two-product-compensation/`, "compensation rank controls
support size"), applied here to every on-column added reader. Through source union 43, this lower bill
strictly exceeds every possible retained-rank loss in the full-rank
on-column case. The predecessor covers rank-one and off-column cases;
this package uses that result rather than re-proving it.

The 24 threshold is sharp even with two full-rank added matrices and
overlapping coordinate coefficient supports: an explicit exact ten-term
fixture drops the retained ranks from `(8,8)` to `(7,7)`. Its added terms
cost 14, so its total COPY rank is **76**, versus the baseline 64.
Removing one source port restores both retained ranks to eight. See
[PROOF.md](PROOF.md) for the quantified reduction, enumeration proof,
fixture and limitations.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3.12 -I -B research/p112-two-total-support-threshold/verify.py
python3.12 scripts/research_package.py --package research/p112-two-total-support-threshold --check-only
python3.12 scripts/research_package.py --package research/p112-two-total-support-threshold
```

The verifier is read-only by default, compares every field with
`RESULT.json`, and remains active under `-O`. It pins the predecessor's
P112 geometry and exact root generator by SHA-256 and Git blob, rebuilds
the geometry, checks all 112² Gram/pairing entries, enumerates every
subspace of all eight 8-dimensional evaluation codes, replays the 511
exact rational-rank premises for the added-term bound, and recomputes the
cross-reader cuts and complete 112² fixture identity. Direct-rank witness
checks, all one-port-short controls, source drift and geometry consistency
checks are part of the same command. The final marker is
`PASS_P112_TWO_TOTAL_SUPPORT_THRESHOLD`.

To regenerate a receipt for comparison without replacing the submitted
one, run `verify.py --write /new/path.json`; the path must not exist.
`SOURCES.json` binds the exact base `a18b4b01`, predecessor proof and
geometry. `TASK.json` declares the scope change from the rank-shape card:
this package supplies a search-pruning algebraic side result, not the
card's physically priced 5% construction target. The selected #1094
record, predecessor packages, `upstream/` and frozen evidence are unchanged.

## Open next questions

1. **Can the remaining full-rank, overlapping two-total case beat COPY 64?**
   A physical decoder gain needs the total bill, including both added
   terms. Start a source-support-aware exact search at union support 44
   or higher, using the 24/36/40 thresholds and preserving the non-free
   choice of two-total basis.
   The present lower bound on added-term COPY ranks is insufficient to
   settle larger source unions.
2. **Do larger cross-reader erosion thresholds guide a paid design?**
   Search unions of minimal evaluation-code supports for four or more
   readers, then impose actual two-source coefficient constraints and
   charge preparation, frames and restoration. An arbitrary union need
   not be realizable by two complex source columns.

Credit: Philipp / @mightyOil's predecessor two-total reductions (#1197),
Mihir Srivastava's #845 single-lift floor and 511-functional census,
@woklerx's #998 complex extension, @commdata2338's PR1375 erasure
distance 24, Hanson Sun / @bbMisk's PR1432 support-from-rank lemma,
@adamgall's seed-80 census recheck, DreamingOfClouds' E8 decoder model
and Joel Pulikkan / GamingPuzzled's coordinate COPY-64 lineage.
Adjacent but distinct: @just-mn's PR1689 bounds masked Walsh totals
that leave `col(X)`, and PR1633 (Hanson Sun) classifies overcomplete
ten-term residual forms without a COPY floor. PR669
(the-missionary-company) computes generalized weights of signed
proper-star codes, a different code from these coordinate evaluation
codes. Prepared for Josie Elliston by OpenAI Codex (offline session 17
of an overnight donated run: mathematics, verifier, controls and
writing), then reviewed, corrected and published by Claude (Anthropic;
session 19). Substantial AI assistance; Apache-2.0; no independent
human review or full multiplication theorem is claimed.
