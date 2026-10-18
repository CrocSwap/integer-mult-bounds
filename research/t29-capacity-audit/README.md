# Capacity-tagged pattern feasibility of PR992's sharp T=29 profile

**Scoped adversarial audit; no new kappa.** woklerx's
[PR992](https://github.com/CrocSwap/integer-mult-bounds/pull/992)
(`research/t37-integrality-audit`) exhibits the aggregate remainder profile
`{1:4, 2:1, 48:8689}` at `T=29` as the sharp case of its integer penalty and
states that it constructs no owner assignment for it. This package checks the
next necessary condition that PR992's arithmetic relaxation omits: whether
nonnegative integer counts of legal, capacity-tagged whole-helper bin patterns
meet the fixed U8 capacity quotas `(672,448,448,448)*29`, the width demands
`(720,288,486,1098,1944)*29` for widths `(4,5,7,8,9)`, and that exact
remainder profile including all 49770 rank-zero bins.

**Result: feasible, and not unique.** A ten-pattern integer witness exists
(`WITNESS.json`), reconstructed in closed form and checked exactly; a second
realization with eight different pattern counts, the reviewer's blind hand
construction from `REVIEW.md`, is checked by the same census. The zero credit
slack forces every bin of every realization to attain `u(r)`; this pins all
8352 fives into `32:{9,9,9,5}` bins, all 4303 full capacity-48 bins to
four-nine patterns, and makes the width-nine demand a consequence of the
width-seven demand. See [PROOF.md](PROOF.md). No obstruction arises at this
level; nothing is claimed about count vectors other than the two checked
realizations. Chronology, owner geometry, the physical schedule, the
controller invoice and the selected PR1042 supplier are outside scope.

## Reproduce

Standard-library Python 3.9+ only, no network, writes nothing:

```sh
python3 -I -O -B research/t29-capacity-audit/verify.py
```

Expected final line:

```text
PASS_T29_CAPACITY_TAGGED_PATTERN_WITNESS patterns=1163 witness_bins=58464 witness_patterns=10 realizations=2 controls=31 no_new_kappa
```

The checker pins the consumed predecessor files by sha256 (`SOURCES.json`,
base `ba82555c64e1879e4b7decce28186f208fcb8262`), enumerates all 1163 legal
patterns once by Cartesian product, recomputes the price table `u(r)`
independently by a maximum-price dynamic program over exact fills (the two
tables must agree), checks the bin-count, rank-mass and zero-slack identities,
verifies the forced structure, checks every quota, demand and remainder of
both realizations, validates the witness's declared `remainder_profile`
against the recomputed census (canonical decimal keys, positive integer
values, no booleans, no missing or extra classes) before any acceptance or
`--write`, and compares the complete certificate with `EXPECTED.json`. All
checks raise explicit exceptions and remain active under `python -O`.
`--json` prints the certificate; `--write NEW_PATH` writes a fresh
certificate only after every check has passed and refuses to overwrite;
`--repository ROOT` points at another checkout of the same base.

## Negative controls (all 31 must be rejected)

**Seven inventory mutations of the witness.** For each, `verify.py` recomputes
the change in bin count, residual mass, dual credit `sum (48u(r)+13r) n_r` and
actual signed price, and records which inventory the mutation violates; the
values below are copied from `EXPECTED.json`.

| Mutation | bins | mass | dual credit | actual price | violates | rejected at |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `16:{9,7}` to `16:{8,8}` | 0 | 0 | 0 | 0 | widths 7,8,9 | width demand |
| `32:{9,9,9,5}` to `32:{9,9,7,7}` | 0 | 0 | 0 | 0 | widths 5,7,9 | width demand |
| `32:{9,9,8,4}` to `32:{9,9,4,4,4}` | 0 | 0 | 0 | 0 | widths 4,8 | width demand |
| `8:{8}` to `16:{8,8}` | 0 | 0 | 0 | 0 | quotas 8,16; width 8 | capacity quota |
| `48:{}` to `48:{9,9,9,9,8,4}` | 0 | −48 | 0 | +13 | profile 0,48; widths 4,8,9 | remainder profile |
| `32:{9,9,9,4}` to `32:{8,8,8,7}` | 0 | 0 | 0 | −25 | widths 4,7,8,9 | width demand |
| one `8:{8}` bin fewer | −1 | 0 | 0 | 0 | quota 8; profile 0; width 8 | capacity quota |

Only the first four preserve all of bin count, mass, dual credit and actual
price while violating the inventory. The empty-to-full capacity-48 retag
preserves bin count and dual credit but changes mass by −48 and actual price
by +13; the untight rank-one swap preserves bins, mass and dual credit but
changes actual price by −25; the missing bin changes only the bin count.

**Eighteen invalid-witness documents:** overfull pattern, negative, fractional
or boolean count, unknown width or capacity, duplicate entry, false
per-pattern remainder; header replicas given as float or boolean, wrong
hypothesis; declared `remainder_profile` missing, false rank-zero count,
missing class, extra zero-count class, boolean value, non-canonical key
`"01"`, swapped class counts. **Six tampered-proof controls:** altered
`u(2)`, wrong replica count, off-by-one profile, same-bin same-mass profiles
with positive and with negative slack, altered source pin. Each rejection
reason is recorded in `EXPECTED.json`.

## Files and ownership

- `verify.py`, `WITNESS.json`, `EXPECTED.json`, `SOURCES.json`, `PROOF.md`,
  `README.md`: this audit (Claude Fable 5.1, implementation).
- `CLAIM.json`, `OVERLAP.json`, `ACCEPTANCE.json`: sprint leader coordination.
  `review.py`, `REVIEW.md`, `FINAL-REVIEW.json`, `POSTFIX-REVIEW.json`: Astra's
  independent review records. The original findings are preserved in
  `FINAL-REVIEW.json`; all four are resolved by the accepted post-fix review
  in `POSTFIX-REVIEW.json`. During
  the blind phase the implementation read neither the review nor Gemini's
  brainstorming notes; the corrections R1 to R4 listed in `FINAL-REVIEW.json`
  were made after the review was released, and the second realization is
  transcribed from `REVIEW.md`. Exploratory control notes are retained
  separately by the coordinator and are not part of this certificate.

## Attribution and scope

Prices, bonuses and the fixed family are Chafik Boukhalfa's (PR795, PR890);
the all-replica relaxation is Jonathan Capalbo's (PR942); the integer slack
lattice and the sharp T=29 profile are woklerx's (PR992); the T16 owner lineage
is Hao Yan's (PR858). This package adds only the capacity-tagged feasibility
statement, its forced-structure lemma and the two checked realizations.
Prepared with substantial AI assistance (Anthropic Claude Fable 5.1 as
implementation lead, with separate AI review and control drafting); no
independent human peer review is claimed. Apache-2.0. Finite checks here are
not a proof of the multiplication theorem and do not change the selected
result.
