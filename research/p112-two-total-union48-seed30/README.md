# P112 two-total correction at source union 48

**Negative result / research note. No new κ, supplier or decoder.**

At source union **48**, the deletion geometry of the eight P112 coordinate
readers changes. One deletion set can remove **eight** rank units (up from
five at 44–47). A two-column correction `ZA^t` can realize retained loss
**exactly 5** there. PR2382's bound of 4 was stated only through 47 and does
not extend to 48.

- **Upper bound (5).** Every configuration with loss 6 or more contains a
  fully specified column subset of rank 3, which a rank-two correction cannot
  match.
- **Attainment (5).** An explicit full-rank two-column decoder attains it,
  with total bill 74. Its representative `A = [e_0, e_1]` lies in PR1197's
  disjoint-coefficient class; the same `W` in an overlapping basis
  (`Z -> ZG`, `A -> A G^{-t}`) keeps retained loss 5, but that
  representative's added bill was not computed.

Charging both added terms with the inherited price lemma gives a
**provable lower bound of 65 on the full-rank on-column (PR1197 residual)
fixed-reader two-total COPY sum at union 48** (attainment open; the explicit
loss-5 witness costs 74). The provable bound is one less than the 66 that
holds for unions 44..47, but still above 64; this does not mean a cheaper
decoder exists. For the realized
`4+1` shape, a further support argument raises the bill to at least 66; the
other loss-5 shapes are not analysed this way (written argument in
PROOF.md; verify.py machine-checks its premise P3, the 12/12 cut sign
balance, not the constrained price minimum 7). With PR1197's complementary
reductions inherited unchanged, the fixed-reader two-total no-saving
statement (COPY rank sum at least 64) **extends to union 48**. The chain is:
PR1787 (merged) and PR1827 for unions of at most 43; this package's
independent cap-47 replay (price minimum 6 for `M = 44..47`) for 44..47; the
new band-48 result; and PR1197. It does not rely on PR2382, which is open. The 65 floor is a relaxation; its attainment is open, since the
explicit witness costs 74. This closes band 48 of PR2382's open next
question 1. It is not a route to a cheaper decoder.

## What is checked

[verify.py](verify.py) is an independent stdlib re-implementation that
imports no predecessor checker. It uses exact `Fraction` and F2 arithmetic.

1. It builds the reader codes `C_j` from the **literal pairing rows** and
   checks P1–P3 of [PROOF.md](PROOF.md): weights, dual-span dimension 8,
   unique cut word with 12-port margin, and distinct labels.
2. It enumerates all closed supports up to 48 ports for every reader. The
   census at dimension 4 has 315 supports, all of size 48.
3. It enumerates every retained-loss configuration with union at most 47 or
   at most 48, using the lead-support case split of PROOF.md. For each
   configuration it computes the geometric loss and applies the rank-two
   **condition N** (exact rational rank of every fully specified column
   subset of size at least 3).
4. It builds the explicit loss-5 witness: readers 0 and 1, `U` a
   four-dimensional 48-port support of reader 0 containing the cut `C_01`.
   It checks the identity `XX^t = XY^t + (XA)Z^t` on all 12,544 pairs and
   computes exact retained and added COPY ranks, `(4,7,8,8,8,8,8,8)` and
   `(8,7)`.
5. It computes the PR1432/PR845 price relaxation for `M = 44..48`. The
   minimum is 6 for each.

| union cap | geometric max loss | two-column loss bound | full-rank floor |
|---|---|---|---|
| ≤ 47 (positive control; floor for `M = 44..47`, PR1827 below 44) | 5 | 4 | 66 |
| ≤ 48 | **8** | **5** (attained) | **65** |

The cap-47 run reproduces PR2382 independently. It matches the geometric
maximum 5, the rank-two bound 4, the floor 66 and the single-word union
census `2032, 280252, 9072, 42, 0`.

New at 48:

- 8-loss sets, such as `(4,0,1,1,1,1,0,0)` and seven 8-reader single-word
  unions, all excluded by a rank-3 minor;
- N-passing loss-5 shapes `4+1`, `3+1+1`, `2+1+1+1` and `1^5`.

Only `4+1` is realized explicitly. Sufficiency is not decided for the other
shapes.

**Negative controls** (must be rejected): a one-byte corrupted geometry
(sha256 pin), a perturbed minor (third column replaced by the sum of the
first two, rank 3 → 2), a three-column fake profile (retained loss 6 but
`rank W = 3`, so not a two-column correction), and a corrupted receipt (the
same `receipt_matches` function used for the real comparison must reject a
copy of RESULT.json with the floor field incremented; an end-to-end mutation
of RESULT.json on disk was also checked by review to give `FAIL RESULT.json
mismatch`).

## Reproduce

From the repository root (CPython 3.12+, standard library only; measured on CPython 3.14,
Linux x86-64, one core: about 165 s and peak RSS about 175 MB):

```sh
python3 -I -B research/p112-two-total-union48-seed30/verify.py
```

Expected final line:

```
PASS_P112_TWO_TOTAL_UNION48 geometric_max_47=5 geometric_max_48=8 two_column_loss_bound_47=4 two_column_loss_bound_48=5 loss5_witness_bill=74 full_rank_copy_floor_48=65 no_new_kappa
```

Package metadata: `python3 scripts/research_package.py --package research/p112-two-total-union48-seed30`.
A fresh receipt can be written with `--write /new/path.json`; overwriting is
refused.

## Scope, inherited assumptions, unresolved obligations

- **Base commit:** `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- **Input pin:** `research/p112-single-lift/reference-geometry.json`, sha256
  `4f44af36…7a080`; see [SOURCES.json](SOURCES.json).
- **Selected record:** unchanged (`certificates/selected-result.json`,
  κ 0.001672660197076918).
- **Inherited:** the separate-total COPY model; the PR845/PR1432 added-term
  price lemma `r >= p(m)`, which is not re-proved here; and PR1197's rank-one,
  off-column and disjoint-coefficient reductions for the general ≥64
  statement.
- **Proved here:** the two-column retained-loss bound uses only
  `rank(ZA^t) <= 2`. It holds for complex, off-column or rank-deficient
  factors.
- **Not shown:**
  - that the 65 floor is attained;
  - whether the N-passing shapes other than `4+1` are realizable;
  - anything about unions of 49 or more, changed readers, masked exactness,
    power sums or physical delivery.
- **Unchanged and out of scope:** the inherited all-size/compiler,
  mutable-source/hosting, precision/tape, analytic-transfer and bit H1–H5
  obligations listed by PR1197 and the selected record.

  All helper, access, frame, restoration and recursive costs are free in this
  screen.
- **Status of the argument:** the written argument in PROOF.md, together with
  the finite enumeration, is not a formal proof.

## Open next questions

Structured versions with relevance, first steps and blockers are in
[TASK.json](TASK.json).

1. **Is the 65 relaxation floor attained at 48?** This needs a loss-5
   two-column correction one of whose sources has at most four active
   labels. If none exists, the 66 floor extends to 48. For shape `4+1` it
   cannot happen: by the 12/12 sign balance of `x_j x_k` on every cut, every
   nonzero vector of `col W` has at least 12 ports, so that shape costs at
   least 66 (PROOF.md). The remaining shapes `3+1+1`, `2+1+1+1` and `1^5`
   need the same minimum-support analysis of `col W` from their patterns.
   Blocker: their free entries make this a joint price/realizability
   question.
2. **Bands 49–51.** The census has no closed supports of size 37–39, so at
   49 every lead with `s > 36` has `s >= 40` and budget at most 9 < 12, and
   that branch stays cut-only. What changes is the `s = 36` branch (budget
   13) and any new supports of size 49 or more, so extend the census past 48
   and widen the `s = 36` enumeration. Geometric losses already reach 8.
3. **Realizability of `3+1+1`, `2+1+1+1` and `1^5` at 48.** First step:
   solve the per-row conditions `x_r|K_r in col(A[K_r,:])` exactly in `A`.

## Credit

This package continues PR2382 by Sricharan Vagvala (@theon199), head
`2d7807f6`, which is open. PR2382 is cited, and its numbers at ≤47 are
reproduced independently; its code is not imported.

Further predecessors:

- Philipp/mightyOil: PR1827 (joint losses through 43) and PR1197
  (complementary reductions);
- Josie Elliston: PR1787 (support threshold);
- Mihir Srivastava: PR845 (P112 geometry and added-reader premise);
- woklerx: PR998;
- Hanson Sun/bbMisk: PR1432 (price from rank);
- commdata2338: PR1375;
- DreamingOfClouds: the separate-total COPY model and the PR717 geometry
  arrays (pinned via PR845's snapshot);
- Joel Pulikkan/GamingPuzzled: PR620 (COPY-64 lineage).

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
