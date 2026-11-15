# CONDITIONAL κ = 0.00365760025222 — two courier (funded-return) moves on #7616 (premises: exactly #7616's)

**κ = 0.003657600252223259…, ×1.0002658 (+0.026580%) over
[#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616)** (SYLforge's W2 stationary follow-up, conditional κ 0.003656628302607).
The official `evaluate_recursive_power` bracket (256 bits) is
[0.0036576002522, 0.0036576002523]; the claim 0.00365760025222 is below the exact crossing 0.00365760025222326.

> **Premises (inherited, nothing new).** Conditional on exactly #7616's premises:
> its five framework assumptions (`native_all_columns`, `owned_erasure`, `compiler`,
> `precision_tape`, `analytic_recovery`), its reading of the 113 CLEARs (74 original + 39
> stationary lifetimes), and its fixed allocation of 17·68 = 1,156 owned banks. This word's
> rows, end charts, owned data (113 lifetimes, peak 50, 68 labels) and all 113 CLEARs are
> identical to #7616's. If #7616's premises are refused, this word is void with #7616.

## The moves

The courier (funded-return) pattern is the crowd's, not ours: Clear1nsight's
#7244/#7274/#7314/#7334/#7481 funded-return chain with determinant-one
co-encoding, rohanarun's #7480 bypass (and #7277), CubeJerry's #7577 analysis
and petalas's #7326 (see [NOTICE](NOTICE)). The same two moves were applied on
#7613 in our [#7615](https://github.com/CrocSwap/integer-mult-bounds/pull/7615)
(built on Clear1nsight's #7612 and our #7613/#7612-lineage packages); this package
carries them to the #7616 word.

In each move a transit register S drops a mid-chart visit (merging two hops).
A courier D, present with S at chart a, carries S's content through an
invertible shear re-basis, stops at S's next chart b, and the inverse shear
decodes there. Nothing is deleted; the pair (S, D) is only re-based.

| S / D | a | dropped by S | b | courier stop |
|---|---|---|---|---|
| 532 / 1464 | 3 | 744 | 746 | none (1464 already stops at 746) |
| 226 / 990 | 719 | 907 | 127 | none (990 already stops at 127) |

The 226/990 move needs 226's MOVE 260→719 slid earlier, to just after its last
chart-260 op, so that courier 990 is co-present at chart 719.

On #7616's word (76,896 events, unchanged in count; per native call ADD +2, MOVE −2):
one new public chart pair, (719,127) (dimension 6→9), strictly nested. (3,746) already
exists in #7616. Rows (all 1,569), end charts, header, owned MOVEs (47), the 113 lifetimes,
the peak (50), the 68 labels, and all 113 CLEARs equal #7616's. [data/edits.json](data/edits.json)
lists every event by #7616 index (9 deletions, 5 insertion groups). Word SHA256 (compressed
`data/word.json.gz`) 8bc9799174f377239bc0bf18611c5bab1ffdf95613fb60e5db684efb6ffbed2a.

Coefficients: no non-dyadic event is added (5,901, as in #7616). All coefficient
denominators are 5-smooth and the word passes main's merged #7000 alphabet check; the
common grid (odd denominator lcm 1125, 2-adic exponent 25, 40 numerator bits) is #7616's.

## Price

Native paid delta per call {1:−1, 2:−1, 3:−1, 6:+1}; over 17 calls:
- paid positions 110,213 → 110,179; productive 22,461; rank surplus S = 1,424 unchanged.

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` against #7616: `uniformly_better`,
  strictly negative for r^(1−C), paid {1:−17, 2:−17, 3:−17, 6:+17}, targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits): `new_cost_lower` at
  C = 0.00365760025222, 0.0036566283026 (#7616) and 0.0036545537006 (#7615);
  `new_cost_higher` at C = 0.0036576002523.

Ordinary bill (17 calls) 781,329,388 < 10^9 (#7616 run under the #7000 formula: 781,362,776);
precision bit bounds 303 / 299 / 299 unchanged. Strictification gate (run offline, not in this
package): γ 0.941241, δ 0.908154, both below 31/32. An independent read-only audit found the
word sound relative to #7616 (exact replay, official #7000 native with bad_inputs 0, 20/20
rejecting controls).

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-couriers-on7616
```

`check.py` (standard library; `core` and `columns` modes are registered as two commands, `all` runs both; the column tests use worker processes) authenticates the vendored #7616 word, rebuilds
the new word from the edit list, replays both exactly over the rationals with legality
checks, requires every row, end chart, owned MOVE, lifetime and the header to equal #7616's
and all 113 CLEARs to erase #7616's content, checks that only registers 226 and 532 change
their MOVE chains (endpoints kept; S drops one chart), locates the encode/decode shears and
checks they are exact inverses in reverse order around S's move, requires exactly the one
new strictly nested chart pair, recomputes the invoice and κ and reproduces #7616's crossing,
and runs rejecting controls (wrong coefficients, dropped or sign-flipped decodes or encodes,
226 slide undone, transit MOVE after its decode, flipped ownership flag, reversed or
non-nested MOVE, retagged encode, bare hop deletion without a courier) plus a tampered invoice.

**Affected-pair column tests.** #7616's native adapter pins an exact census of affected chart
pairs (442) and the candidate hash, and tests every such pair with 512 forward and 512 adjoint
Gaussian columns plus absolute-phase checks. This package carries the equivalent tests, written
independently in `check.py` (nothing from #7616 or its dependencies is executed): the 442
pinned pairs (`data/affected-pairs-7616.json`, copied as data from #7616's adapter) plus every
pair on the old and new routes of the two registers whose route changed here (226, 532) —
six further pairs, of which (719,127) is new; 448 pairs in all. For each pair the check builds
F_a† F_b from the two nine-bit stabilizer frames, compiles it to a child recipe
monomial·Fourier^r·monomial, requires exact public ascent rank r = dim b − dim a, equality of signed Pauli action and exact
absolute phase with the direct circuit, equality of all 512 forward and 512 adjoint Gaussian
columns (458,752 columns), and rejection of a wrong absolute phase. Controls: a non-nested pair, a shifted-offset
recipe and a global-phase error are rejected. The pinned #7616 census is 442 pairs; this
package's census is 448 (442 + 6), covering the 443 that the new route requires.
The new word's hash and event census (76,896) are pinned in `check.py`.
`price.py` runs the repository tools above.

## Conditional premises and what is not rerun

The claim carries exactly #7616's premises (above) and the signed #7113 caller and BIT
premise of the base. This package does not rerun #7616's full native/signed 17-stage
application, signed catalogue, outer predicates or precision/tape counts (header, rows, grid and
owned data are unchanged); the audit above ran the official #7000 native engines on the
word. No upstream maintainer has reviewed the package.

## Credit

The base word is SYLforge's #7616 (itself built on #7605, #7611, #7612 and the packages
named in its notices); the move pattern is the crowd's (credits above); the two moves were first
applied to a base in our #7615 (on #7613, #7612). See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

**The premises.** A ruling on #7616's inherited assumptions and its 113-CLEAR reading (`owned_erasure`, clear-form-gap Q1) decides #7616 and this word together. See [TASK.json](TASK.json).
