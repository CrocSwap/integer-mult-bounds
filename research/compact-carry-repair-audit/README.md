# Research audit: interior compact carries and exact exceptional repair

**The existing compact-control guard is sufficient. Its last source-control
saturation exclusion is conservative.** Under the retained temporary and target
guards, a later-source execution flips selected bit `i` by `c_i xor k_i`, where
`c_i` is the intended source bit and `k_i` is the incoming radix carry in the
compact source load. Only interior carries cause extra target flips. The carry
out of the final digit is harmless, so that digit may keep its complete range.
[PROOF.md](PROOF.md) gives the integer argument for arbitrary digit count and
radix, and a sharper source-dependent iff condition on the guarded domain.

This is a **research note / adversarial mathematical audit**, with an independent
finite checker and omitted-hypothesis controls. It does not claim a defect in
the stated construction, a new supplier, or a new κ. Production predicates,
selected frontier, and `upstream/` are unchanged.

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -B research/compact-carry-repair-audit/verify.py
```

Expected:

```text
PASS_COMPACT_CARRY_REPAIR_AUDIT: 1310720 representatives; 3072 source comparisons; 7 negative controls
```

The default command verifies all pinned source bytes, recomputes all evidence,
and compares it with [RESULT.json](RESULT.json). It writes no artifacts. To
explicitly regenerate a receipt, use `--write /path/to/result.json` and compare
it to the committed result. Verification uses explicit exceptions and also
runs with `python3 -O -B`; no mathematical check relies on Python `assert`.

## Concrete failure and the useful refinement

For `n=2, K=5, rho=4, G=1`, take

```text
(x, y, t, u, b) = (16, 4224, 0, 1, 2).
```

The temporary and target guards hold. Only the lower `u` digit is saturated.
The uncorrected map returns `y=4752`; the required low-selected XOR returns
`y=4240`. Every temporary restores. The extra bit is at position 9, caused by
a carry into the second compact control digit. Restoration alone cannot catch
this wrong target. There is no successor digit in the one-segment case, so
that case cannot exhibit this particular failure.

Under the same temporary and target guards, excluding saturation of just the
first `n-1` source-control digits is sufficient. If `B=2^G`, the admissible
`u` count increases from `(B-1)^n` to `B(B-1)^(n-1)`. The corresponding later-source
bad-fraction union bound is

```text
min(1, (2n-1)/B + 8nB/2^K).
```

The original has `2n/B` in its first term. This constant-level improvement
establishes no exponent gain. The expanded predicate is tested only in this
audit; a production change would also need consistent predicate use and source
binding throughout its callers and artifacts.

## Completed coverage and independence

The main finite domain is `n=2, K=5, rho=4, G=1`, with maximal selected offset,
both source orders, all three selected source bits, target bits 4 through 14,
and every value of the active two-bit compact fields. The top target bit is
retained because intermediate bad-address carries can reach it.

| Evidence | Earlier source | Later source |
|---|---:|---:|
| Exhaustively enumerated representatives | 262,144 | 1,048,576 |
| Original good addresses | 16,384 | 16,384 |
| Expanded good addresses | 16,384 | 32,768 |
| Guarded carry-law cases | not applicable | 65,536 |
| Guarded failures exactly predicted by interior carry | not applicable | 16,384 |

For each order the checker constructs the entire actual address permutation,
proves it injective on this finite domain, checks both bad-set invariants, and
sorts the correction keys into the actual marked holes. Record identities are
unique integers. Both original and expanded repairs must place every record
at its ideal destination. A separate elementary highest-bit XOR is materialized
and checked against the full `f=n+1` ideal map. Receipt hashes cover the actual,
repaired low-bit, and repaired full permutations using little-endian uint32
record identifiers in declared enumeration order.

Fixing `x,b` partitions the checks into invariant fibers. No partition is made
by mutable `t`. The proof explains why unused source bits, lower target bits,
and the earlier-source unused `u` are spectators. This lifts each representative
check to its particular complete `2^36`-address rectangle; it does **not** mean
`2^36` addresses were individually enumerated or all parameters were tested.

The new `Gadget` interpreter directly implements the four integer updates and
dirty back-field swap sandwiches. It imports no source operation generator or
arithmetic helper. The exhaustive checks use this interpreter. Separately,
3,072 seed-69 states across six parameter tuples compare its output with the
pinned source interpreter and compare the source predicate and inverse. Those
source comparisons are samples, not an exhaustive source execution. The
sorting checker uses the full forward permutation table to obtain inverse
addresses, independently of either inverse interpreter.

Seven negative controls cover lower-`u` saturation, `t` saturation, target
overflow, reversed repair composition, incorrect `T(q)` destination keys,
duplicate keys, and omission of the separate highest XOR. The first three
isolate one failed guard each. The `G=2` overflow control is necessary because
the main `G=1` good domain forces every temporary digit to zero. The incorrect
`T(q)` keys still fill all marked holes; record identities detect the error.
These controls are concrete failures of weakened hypotheses or mutated maps,
not failures of the original guarded lemma.

Exact product-density checks include nontrivial unclipped union bounds and an
empty-good-set boundary. The experiment stops at the fixed exhaustive domains,
3,072 specified seeded comparisons and seven controls. No unbounded search,
optimality claim, or negative search theorem is inferred.

## Pins, attribution and limitations

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins the audited note, executable and import
closure, prior tests, upstream source and baseline review context. The accepted
certificate at that base is conditional
`κ=51110230636731/31250000000000000 = 0.001635527380375392`, selecting #626 with
#543. Its audited construction head is
`660de893d27bb7abd1d5b01b1640207528a5c851`. It supplies context, not an input to
this local carry identity. The retained upstream manuscript is OpenAI's
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

Credit **Douglas Colkitt** for the compact-control construction, its guard and
repair proof, and earlier tests; **OpenAI** for the original manuscript's
selected-bit and exceptional-stream framework. The selected checkpoint's work
by Chafik Boukhalfa (#626), Jeremy Kothe and predecessors (#622/#623), eumemic
(#543), and the cumulative construction/verification lineage is unchanged.
The current audit claims no priority over that work.

The final overlap refresh found Aryan Sudhir's concurrent
[#735](https://github.com/CrocSwap/integer-mult-bounds/pull/735) at
`8d36139e49add1e55795e283b3bfa45e1cfe1bf0`. It tightens the original eight-rotation
wide-slot primitive's guard envelope; this audit treats the different compact
four-update primitive, its interior source-load carries and sorted-hole payload
checks. Both retain the exceptional-permutation argument. No #735 code or
result is consumed here, and its factor-40 bound is not transferred to compact
controls.

Contribution by **John-Michael Smith / @jp3isme**, with substantial **OpenAI
Codex assistance** in derivation, implementation, writing, and two scoped agent
reviews. This is not independent human peer review or a proof-assistant
formalization. New material is Apache-2.0 under the repository license; original
notices and the upstream CC0 license are retained.

This audit establishes address algebra and finite record correspondence.
Complete fields at recursive calls, fixed-tape movement/sorting costs, uniform
compilation, physical hosting, precision, analytic transfer and the full
multiplication theorem remain inherited obligations. It does not instantiate
an improved recursive supplier or infer runtime from Python measurements.
See [CLAIM.md](CLAIM.md) for track selection and sprint-overlap provenance.

## Validation recorded for this contribution

On macOS arm64 / CPython 3.11.2:

- Default receipt replay and `python3 -O -B` replay passed with identical evidence.
- Five `test_compact_controls.py` tests passed; twelve
  `test_compact_control_*.py` layer/patch tests passed.
- `make selected-record-check` passed; the selected certificate was unchanged.
- A clean dependency-only export replayed from an unrelated working directory
  using `python3 -I -B`; a deliberately altered source was rejected before replay.
- The integer proof and verifier received scoped agent review. Two test
  weaknesses (highest-bit materialization and unclipped density bounds) were
  corrected and the updated receipt replayed.

The repository-wide `make verify` and supplier cold replay were not run for this
isolated research addition. Remote CI status is separate from these local
checks. No generator or artifact outside this new directory was changed.
