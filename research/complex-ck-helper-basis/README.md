# Restored helper pairs in CK frame-zero compensation

**Status: finite complex-supplier circuit construction; no new κ.**

The selected #626/#622 CK word's compensation can use 124 disjoint temporary
helper shears. Its complete scalar program saves **35,872 real-component
primitives per orientation**, including preparation, rational coefficient work,
source reads and restoration. All 716 arbitrary live input columns are checked
in both orientations, with separate primitive replay of the replacement and
arbitrary incoming coefficient-work input. Every helper is restored before
entry adapters or any paid recursive child.

| Quantity | Selected CK | Replacement |
|---|---:|---:|
| Compensation additions (including basis changes) | 8,704 | 5,804 |
| Compensation real primitives | 99,248 | 63,376 |
| Full scalar macros, either orientation | 21,936 | 19,036 |
| Forward real primitives | 224,938 | 189,066 |
| Backward real primitives | 224,986 | 189,114 |
| Forward conservative prefix bits | 40 | 41 |
| Backward conservative prefix bits | 62 | 63 |

This is a different finite circuit, not a faster implementation of its checker.
The conservative positive prefix envelopes grow, but remain below the inherited
192-bit allowance. No practical runtime or improved outer exponent is asserted.

## Reproduce

From the repository root, with Python 3.11+ and no third-party packages:

```sh
python3 -I -B research/complex-ck-helper-basis/verify.py --out /tmp/ck-helper-replay
```

The output directory must be fresh. Expected final line:

```text
PASS_CK_RESTORED_HELPER_BASIS pairs=124 real_saved=35872 columns=716+1 orientations=2 controls=6+25 kappa=unchanged
```

The command validates pinned inputs, exhausts the search, reconstructs both
programs with the retained emitter, runs the retained frame/wrapper auditor and
its 25 negative controls, and checks all proof-relevant fields against
[CERTIFICATE.json](CERTIFICATE.json). Generated words, programs, audit receipts,
logs and `EVIDENCE.json` go only in the chosen directory. Existing output is
never overwritten. `--write-certificate` is an explicit maintainer regeneration
option; normal verification never changes the committed certificate.

The independent search census and mathematical failure-mode tests are:

```sh
TEST_SKIP_LOG=/tmp/test-skips.log python3 -B research/complex-ck-helper-basis/test_circuit.py
```

Eleven tests; zero expected skips. The runner writes the actual skipped tests
and reasons to `TEST_SKIP_LOG`. The certificate replay also works under `-I -O`
and `PYTHONOPTIMIZE=2`: new checks use explicit exceptions, and retained native
subprocesses run with assertions enabled (`-E`, without optimization flags).

## Exact local identity and cost

Write the frame-zero compensation as `y <- y + C h`. For a chosen ordered
helper pair `(a,b)` and `s` in `{−1,+1}`, replace its contribution by:

1. Prepare `h_a <- h_a + s h_b`.
2. For every target, use coefficients `C_a` and `C_b − s C_a` on the new
   `h_a` and unchanged `h_b`, omitting zero coefficients.
3. Restore `h_a <- h_a − s h_b`.

For arbitrary dirty helpers and arbitrary targets,
`C_a(h_a+s h_b) + (C_b−s C_a)h_b = C_a h_a + C_b h_b`.
The preparation/restoration product is the identity on helpers. Pairs are
disjoint, so the column substitutions compose without cross terms. The six
unpaired eligible helpers keep their original coefficients. Unused entering
and cold-ended helpers are untouched.

Every used helper has `start=0` and `final=FULL`. In particular it is not a
wrapped helper, so this temporary change occurs entirely before all entry
adapters and wrappers. All other canonical-word fields and every emitted
non-scalar event are unchanged. The native auditor rechecks the common frames,
wrapper lifetimes, paid children, private centres and complete scalar endpoints.

For the backward orientation, apply inverse transpose to each gate, in the
same chronological order, exactly as the native emitter does. This is valid
because inverse transpose is a group homomorphism. Forward helper preparation
becomes its dual helper shear, and target updates become source/target-swapped
updates with negated coefficients. Both full emitted programs pass exact replay;
independent dense three-coordinate maps check every pair/target in both
orientations. No commutation through the unchanged intervening word is needed.

For nonzero reduced dyadic `q=n/d`, the retained binary-Horner real price is

```text
P(q) = 2 [3 + (bit_length(|n|)−1) + popcount(|n|) + (bit_length(d)−1)].
P(0) = 0.
```

The factor two is for the real and imaginary components. The three constant
operations are the initial work clear, signed target accumulation and final
work clear. The remaining terms charge all source additions, doubles and
halves. Each unit preparation or restoration costs eight real primitives;
every chosen pair pays sixteen. The primitive interpreter independently
executes those operations and clears arbitrary incoming private work.

There are 5,556 nonzero middle additions and 248 preparation/restoration gates.
The ordinary Horner lowering is unchanged. No new scratch register, recursive
child, helper allocation, frame transition or uncharged copy is introduced.
The complete native prefix bounds, including coefficient work, are
`1258556220792` forward and `153667580418596477857/32` backward. The native
positive-bound method does not cancel restoration terms, so it is conservative.

## Completed search and rejection evidence

OS seed **24** assigns the complex-supplier track. Three candidates and the
local-only claim are in [CLAIM.md](CLAIM.md). The seed also sets the cyclic
helper-index tie break. This is a new helper-column search class, distinct
from prior fixed-middle cleanup searches and JP8 target-row factorization.

The domain is all **254 × 253 × 2 = 128,524** legal ordered helper pairs and
signs. Exact integer quarter-unit coefficients suffice. **9,756** candidates
have positive complete savings. Sort by descending saving, then helper indices
cyclically shifted by 24, then sign; accept the first pair whose helpers are
both unused. This one deterministic greedy pass selects 124 pairs. The
certificate lists every selected pair and binds the entire sorted profitable
list by SHA-256. No timeout, randomized sampling, additional rounds or matching
optimality claim is involved. Different matchings and general bases remain open.

The test census reconstructs sparse coefficient columns and prices all pairs
using joint coefficient histograms and repeated integer division, independently
of the production search and its `bit_length`/`bit_count` cost formula.
It reproduces the complete positive-candidate digest and chosen pairs.

Six new semantic controls reject omitted preparation/restoration, either wrong
basis sign, a wrong middle coefficient and an aliased preparation. Tests also
reject duplicate pairs, nonzero-frame and cold-wrapped helpers, favorable cost
corruption, a wrong dual sign and corrupt source bytes. Gzip recompression is
accepted by binding decompressed payloads. Twenty-five retained native controls
remain active, including cold-wrapper and frame errors. Finite matrix replay
is not a formal proof of the full multiplication theorem.

## Source pins, attribution and limits

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
Construction #622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
[SOURCE-PINS.json](SOURCE-PINS.json) pins every consumed source, including the
native emitter and auditor. Native word/program payloads are additionally
checked against the selected #626 SPEC. The selected κ remains
`51110230636731/31250000000000000 = 0.001635527380375392`.

Credit to Jeremy Kothe and the #622 Claude Code contributors, Chafik Boukhalfa's
#626 packaging, DreamingOfClouds' native cold-helper construction and checks,
icekylinx's direct-delivery/emitter and Horner invoice lineage, and all retained
predecessors. The inherited bit supplier is eumemic's #543. Original source
notices and licenses remain in their packages.

The conceptual relation to pending **#749** (Sricharan Vagvala / @theon199,
Codex-assisted) is explicit: it factors JP8 target rows through target bases;
this contribution factors CK helper columns and checks temporary helper dirt
and restoration. **#719** proves a fixed-middle CK cleanup obstruction;
**#750** moves a cleanup scale; **#696/#734** change individual coefficient
lowering. None of their implementations is imported, and no additive saving
relative to any pending PR is claimed. Initial overlap inspection covered all
585 open PRs through #764; the only open non-PR issue was #650, not a sprint
coordination issue. The final refresh reaches #773; new **#769**
(`e891b2b19e3185ec91bcf001e255af87f42389ce`) shares varying-magnitude CK
coefficient preparation while retaining the macro word. It is distinct from
this helper-basis replacement; no combined saving is asserted. Main remains
the exact base commit.

This isolated package changes neither the selected certificate nor production
supplier sources. Production use would require an admitted typed compensation
rewrite, refreshed bindings and global owner/invoice/assembly receipts. The
paid profile and rank deficit are unchanged, so this scalar saving alone does
not supply a better recurrence exponent. The all-size compiler, common-label
and mutable-basis realization, whole-call hosting, normalized residuals,
precision/tape/recovery, bit and analytic assumptions remain inherited. Global
assembly, full cold supplier regeneration, repository-wide `make verify`,
remote CI and Lean are not claimed by this local result.

Contributed by David Awad. Prepared with substantial AI assistance (OpenAI Codex)
throughout. No independent human review is claimed. New work is Apache-2.0
under the repository license.
