# Anchored split frames with profile-cost live reclamation

This finite conditional witness gives
**κ = 51414646104039 / 10^18 = 5.1414646104039×10^-5**, with bit saving
**12854322426487 / 250000000000000000**. It is **0.7463402960%** above the
complete pinned PR67 witness. It combines an aligned split-pair scalar graph,
PR65's schedules and refined arithmetic, PR67's profile-cost reclamation,
and PR68's pending live controls. The new score uses each pending control's
known next-use frame when choosing among eligible clearing expressions.

| Quantity | Pinned PR67 | This witness |
|---|---:|---:|
| h23 auxiliary roles | 27,918 | 27,455 |
| h25 auxiliary roles | 36,586 | 36,015 |
| Physical width W | 137,151,806 | 135,075,665 |
| Total recursive rank | 78,860,441,550 | 77,666,660,475 |
| Rank deficit | 1,846,900 | 1,846,900 |

At each common point, start with the inherited alternating point order and
move the lowest intact global pair to the front, preserving all other points'
relative order. Use split choices `[1,1,2]`: split the first pair at the first
two recursive levels and the middle group at the third level when it is a
pair. Later levels use the ordinary grouping. The small-size guard keeps the
recursion strictly decreasing. This aligns the initial split pair across
common-point copies and changes opportunities for sharing scalar sums.

The h23 region schedule is PR65's `cover-core`; h25 uses `reverse-node`.
Every incoming dependency and retained carrier must still point forward in
the selected order. Every auxiliary role, copy, frame raise, and clearing XOR
is paid by the complete serialized words and their actual profiles.

Live controls enter the clearing basis only when their current frame is
contained in the present region and the present region is contained in their
next-use frame. Their values remain unchanged as XOR controls. The integer
profile score is a deterministic discovery heuristic; only the full paid
physical profile and exact recurrence establish the reported saving.

```sh
make split-pair-verify
make verify
```

The focused target checks the pinned source closure, deterministically
regenerates both words, compares their decompressed bytes, replays every
input and dirty basis column in both orientations, reconstructs frame changes
from literal XORs, and recomputes every fixed-I+J profile using the inherited
bounded-minor/CRT checks. It then reconstructs the full recursive child list,
checks exact logarithm/exponential enclosures and an independent enclosure,
and verifies 47 strict assembly constraints and seven positive margins.
The next bit-saving and κ grid points at denominator 10^18 are rejected.
The **complete** PR67 recursive profile fails at the new bit saving.

The [proof and scope](PROOF.md) distinguish this finite certificate from the
inherited all-size compiler, routing, prime selection, recovery, fixed-tape
and analytic transfer hypotheses. The reported arithmetic cutoff is not a
full operational threshold. There is no claim of global optimality, a fully
formalized multiplication theorem, or measured practical speedup.

The original contributor source closure, published words, transition records,
profiles, complete arithmetic certificate, licenses and notices are preserved
under `references/frame-compiler/pr65`, pinned to
`49e84f939d15b618b50714eb039cabf97c74256a`. The earlier split operation and
notices are preserved under `references/frame-compiler/pr59-split-operation`.
PR67's original compiler, profile oracle and complete comparison profile are
preserved at `b3745601e947a94316bf25c2c6263d93c06e3364`; PR68's original
pending-carrier compiler, driver and proof are preserved at
`734c58e225e9d2254570c3b50296ed96943f62ea`. The local engine's exact change
from PR67 appears in `engine-changes.patch` and its provenance record.
The prior numerical certificates and maintainer-reviewed statement remain
available. This package adds its own namespace and verification target.

Credits: Avi Eisenberg supplied the interval-strip/core-aware pair graph in
PR62; Dominik Scholz supplied PR63's ranked-frame composition and PR68's
pending live controls; Rohan Arun supplied PR65's schedules/refined arithmetic
and PR67's profile-cost reclamation; Rohan Garg supplied the
split-pair operation in PR59; eumemic supplied PR57's joint reversible
compiler and independent physical/profile checkers. Chafik Boukhalfa, with
OpenAI Codex assistance, supplied PR60's ranked reclamation and this selected
split vector, aligned point order, next-use profile score, composition and
reproducible package.
All inherited notices remain applicable.

`certificates/split-pair-validation.json` records the focused verification.
`certificates/split-pair-repository-validation.json` separately records the
full repository result. Maintainers explicitly freeze reviewed source and
finite inputs with `scripts/experiments/pin_split_pair_sources.py`;
verification never refreshes the source pins. Arithmetic certificates and run
receipts are derived outputs and are not circular inputs to that freeze.
