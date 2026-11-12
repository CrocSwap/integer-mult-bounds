# A sharper rational for one section-6 threshold step

**Proof, with one exhaustive exponent census and two further witnesses.
Selected κ stays `363005817/100000000000`.**

The one-step hypothesis `m ≥ ceil(8 d0 b / (5 a))` may be replaced by
`m ≥ ceil(27 d0 b / (17 a))`. The new rational is `27/17`, from the integer
pair `3^17 = 129140163 < 134217728 = 2^27`, and `27 · 5 = 135 < 136 = 17 · 8`.
The binomial bound stays `(1+1/m)^m < 3`. At the assigned test point
`(d0, a, b) = (1, 2, 5)` the ceiling remains `4`: the step fails at `m = 3`
and holds for every integer `m ≥ 4`. No pair `3^p < 2^q` lowers that ceiling.
The argument is [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `uniform-transfer-audit`. Scope status: **refined**. The card
asks for one assumption and one quantified implication, and says to stop at
that obligation. The implication is the rational constant inside the section-6
one-step comparison, which is open question 2 of the persistence note at
`8e0124415604b89a1cfc842cb6dc6da96ea87ac5`. This package does not prove
`precision_tape`. It does not compute the least `j` for the section-6 pairs,
and it does not use the record count in open PR #7286.

The predecessor proved persistence, including the explicit index `j*`, and
showed that one less than the `8/5` ceiling already fails at `(1, 2, 5)`.
This package takes only the sharper-rational step. The one-step lemma is
written in full here, so the replacement does not depend on that unmerged
note being present in the tree. The construction of `j*` is not repeated.

Evidence classes:

1. **Proof.** [PROOF.md](PROOF.md): every pair `3^p < 2^q` gives the one-step
   constant `q/p`; `27/17` is strictly below `8/5`; the ceiling at
   `(1, 2, 5)` is exactly `4`; no admissible pair lowers it; the same floor
   keeps every such pair from including the true `m = 7` step at `(1, 1, 5)`.
2. **Exhaustive finite census.** For each `p` from `1` through `17`, the least
   `q` with `3^p < 2^q`. The domain is finite, the search stops by
   `4^p > 3^p`, and `(17, 27)` is the only sharper pair in that range.
3. **Witnesses only.** `(29, 46)` and `(41, 65)` are admissible and strictly
   below `27/17`. They are not a claim that either ratio is minimal. The
   rectangle and binomial rows in `verify.py` are finite checks, not the proof.

Pins are in [SOURCES.json](SOURCES.json). Base commit
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/threshold-ratio-sharper-pair/verify.py
python3 -O -B research/threshold-ratio-sharper-pair/verify.py
python3 -I -B research/threshold-ratio-sharper-pair/verify.py
python3 -B scripts/research_package.py --package research/threshold-ratio-sharper-pair --check-only
python3 -B scripts/research_package.py --package research/threshold-ratio-sharper-pair
```

Expected direct marker:

```text
PASS_THRESHOLD_RATIO_SHARPER_PAIR rational=27/17 previous=8/5 test=1,2,5 ceiling=4 sharp_below=3 census_p=17 unique_least_exponent=17,27 witness_pairs=2 rectangle_rows=320 persistence_rows=18 binomial_rows=48 kappa=363005817/100000000000 no_new_kappa=true
```

The registered replay is
`python3 -B scripts/research_package.py --package research/threshold-ratio-sharper-pair`.
`python3 -B scripts/research_selected_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and is not a scientific replay.
`make frontier7000-verify`, Lean and Docker were not run.

## Open next questions

1. Can a bound stricter than `(1+1/m)^m < 3` certify the one-step comparison
   at `m = 7` for `(d0, a, b) = (1, 1, 5)`? The integer step already holds
   there (`32768 < 33614`), but every pair `3^p < 2^q` has ceiling at least
   `8`, so a sharper pair of the present shape cannot include `m = 7`. The
   same attempt has to keep the `(1, 2, 5)` ceiling at `4`, since `m = 3`
   fails by `1024 > 972`. The first step is to prove or refute
   `4 (m+1)^m < 11 m^m` for every integer `m ≥ 1`, then derive the resulting
   ceiling at both triples. Nothing external blocks that calculation. This
   package keeps the bound `3`.
2. Can the review factor `4` be replaced by a smaller positive integer once
   the one-step constant is `27/17`? A smaller sufficient factor would shrink
   the region the #7000 application review asks the reader to clear. The
   first step is to repeat the comparison of `j > c d0/δ` with
   `ceil(27 d0 b / (17 a))` and either prove a smaller `c` for every positive
   integers `d0, a, b` or give a triple where `c = 3` fails. This package only
   shows that `4` remains sufficient, because the new ceiling is at most the
   old one. It does not compute the least `j` for the section-6 pairs, and it
   does not use open PR #7286.

## Credit

The comparison and the factor `4` are section 6 of the #7000 application
review. The constant `8/5`, the test triple `(1, 2, 5)`, and the decision not
to retune the binomial bound are open question 2 of the persistence note at
`8e0124415604b89a1cfc842cb6dc6da96ea87ac5`. The five assumption ids are the
selected record. The monomial record count is open PR #7286 and is not an
input. Prepared by unpaidmoon with substantial Cursor Grok assistance. No
formal-kernel review and no independent human review are claimed. New work
is Apache-2.0.
