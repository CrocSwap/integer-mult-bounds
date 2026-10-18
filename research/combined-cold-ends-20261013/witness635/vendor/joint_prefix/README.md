# Conditional κ = 0.001600770286423653

This package extends PR571's joint-prefix construction to its nine remaining
ordinary calls. All 72 complex calls now use complete eight-cold joint-prefix
providers: 63 retain the width-seven version and nine use the ordinary version.
The native exact-complex assembly gives **κ = 0.001600770286423653**, approximately
**0.00549033407% above PR571**. The separately admitted conservative assembly
gives κ = 0.001600770283642087.

The 63 width-seven providers reproduce PR571's canonical word and both program
hashes exactly. In each of the other nine calls, four helper-label swaps match
the new provider to the existing physical slots. Exactly 72 of 36,288 helper
labels change; every physical owner, window, offset and family stays fixed.
The complete profile improves by −108e2 + 72e3 relative to PR571.

## Complete providers and accounting

Both providers include all eight rank-five pivots, eight cold kernels, 504
helper roles, both reflected local programs and the literal 57-gate A-prefix.
The ordinary provider preserves its own actual event frames.

| Provider | Calls | Width inventory | Paid local profile |
| --- | ---: | --- | --- |
| Ordinary joint-prefix | 9 | 8×4, 48×5, 160×8, 288×9 | 2320e1 + 420e2 + 464e3 + 192e4 + 56e5 + 56e6 + 8e8 |
| Width-seven joint-prefix | 63 | 8×4, 48×5, 32×7, 128×8, 288×9 | 2352e1 + 580e2 + 336e3 + 192e4 + 56e5 + 56e6 + 8e8 |

The complete global profile, including idle remainders, is

~~~text
169056e1 + 40320e2 + 26544e3 + 13824e4 + 4032e5 + 4032e6
  + 48e7 + 576e8 + 1808e48.
~~~

The idle profile is 1200e3 + 48e7 + 1808e48. Rank mass is 520704, deficit is
2560, dimension is 73, live stock is 7168, and physical stock is 7682.
The emitted controller has 6390 actual orthogonal chart types, 27,468
cross-replica roles and 3056 positive idle remainders. The native complex rate
is 0.001603336860428956057970; the conservative complex rate is
0.001603336857638463195522. The unchanged, cited PR543 bit rate
0.001653826988146798944268 remains nonbinding.

## Reproduction

From the repository root, using Python 3.12 or newer and an unused output path:

~~~sh
python3 -B research/complex-joint-prefix/verify.py --work /tmp/joint-prefix-replay
~~~

The package is self-contained and needs only Python's standard library. It
reconstructs the retained baseline and both complete providers before admitting
the global controller. It checks its source manifest before and after the run,
checks every immutable source pin before creating the output directory, and
refuses optimized Python mode. Generated artifact identity binds decompressed
contents and every proof-relevant field. Only the phase receipt's root timing
field is excluded from semantic identity. Packing replay reconstructs the
literal owner payload from the pinned PR571 source without an optimizer.

The replay checks:

- All 728 scalar input columns, arbitrary dirty restoration, both orientations,
  native frames, normalized wrappers and 11 local rejection controls per provider.
- The retained intermediate cold, 44-kernel and rank-five checks; then 135 fresh
  omission cases per final word, covering 103 distinct omitted-position sets,
  all 40 current prefix kernels and all eight cold kernels. Each case rejects
  in both orientations. Eight final rank-five omissions are also rejected.
- Independent literal-prefix, frame, cleanup and receipt coverage checks, with
  15 rejection controls per provider. Old 44-kernel recipes are not transferred
  to the new 40-kernel prefix.
- Every directed phase edge (2928 ordinary, 3004 width-seven) and all 224 endpoint
  adapters per provider, including global phase.
- All 144 source-derived owner windows, complete family uniqueness, active-data
  exclusion, residual offsets, actual charts, spectators and idle remainders.
- Seven packing, 16 physical-controller and 93 assembly mutation controls.
- Generated-artifact recompression acceptance (2), semantic rejection (18),
  reference/metadata rejection (18), and promotion-identity controls (4 accepted,
  8 rejected).
- The fresh finite invoice, both exact rational moment engines, adjacent endpoint
  rejection, seven bootstrap steps and all 47 strict outer inequalities in each
  conservative/native assembly.

Frozen-source replay receipts are kept in the sibling
complex-joint-prefix-validation directory. They identify the exact source
manifest and runtime tested. The historical selected certificate is unchanged.

## Construction and scope

See [the composition argument](proof/CONSTRUCTION.md) and
[the literal packing witness](proof/PACKING-CONSTRUCTION.md). Shortening the
prefix changes the paid child profile and increases scalar compensation work;
the fresh invoice includes that work. No global optimality claim is made.

The native recurrence uses PR559's exact full-cover complex argument after
complete conservative admission. The PR543 bit profile is repriced with its
bad-residue surcharge retained; this package does not freshly rebuild the bit
circuit. All-size compiler realization, common-label/mutable-source interfaces,
correlated whole-call hosting, normalized residual interfaces, precision/tape
bounds, analytic transfer and PR543's H1-H5 remain conditional. Finite replay
is not an unconditional multiplication theorem, full Lean proof or measured
practical speedup.

## Sources

- [PR571](https://github.com/CrocSwap/integer-mult-bounds/pull/571), head
  b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3: literal joint prefix, complete
  width-seven composition and 63/9 whole-owner geometry.
- [PR568](https://github.com/CrocSwap/integer-mult-bounds/pull/568), head
  71c99ac935a33bb7b59a1b4a7af8725a939b0b90: eight cold kernels.
- [PR569](https://github.com/CrocSwap/integer-mult-bounds/pull/569), head
  f20a68b4b126780419c292571411022bb1d006d6: paid width-seven entrances.
  PR571's source records its later f1db606a mathematical and 1424da81 evidence heads.
- [PR567](https://github.com/CrocSwap/integer-mult-bounds/pull/567), head
  7f452897d67282a76ada6df0162d34a751d5f3e6: portable reconstruction and complete
  generated-artifact identity checks.

All retained predecessors, contributor credits, licenses and AI disclosures
remain in [NOTICE.md](NOTICE.md), SOURCE-PINS.json and the unchanged vendor tree.
The nine-call extension, independent audits and packaging were prepared for
Jonathan with OpenAI Codex assistance under Apache-2.0.
