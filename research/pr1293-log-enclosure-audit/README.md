# PR1293 logarithm cross-check: false singleton enclosure

**Result:** the default-precision `ln_exp_bisection` in Navinor's pending
[PR1293](https://github.com/CrocSwap/integer-mult-bounds/pull/1293), pinned at
`85a361233431befe4b11cf878f7b1b77a244d473`, can return a singleton that does
not contain the logarithm. This package supplies an exact rational
counterexample, an independently written enclosure oracle, semantic controls,
and a minimal repair. It does **not** find a failed selected supplier moment.

Base main is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The selected record,
frozen inputs and predecessor files are unchanged. This was initially prepared
and verified offline while GitHub was unauthenticated. The donor subsequently
authorized publication as `tennisbowling` (`tennisbowling@tennisbowling.com`).
The scoped [Discussion finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18911883)
records the proof, source pin, impact boundary and publication handoff. No
selected-frontier change, merge or closure is requested.

## Compact integer reproducer

With unchanged `CROSS_ORDER=48` and `CROSS_BITS=72`, call
`ln_exp_bisection(Fraction(1681))`. It returns `[q,q]`, where

```text
q = 4384212064881345387879 / 590295810358705651712.
```

At bisection step 72, `1681` lies **strictly inside** the Taylor exponential
interval at `q`. An independently evaluated finite rational sum proves
`1681 < T_49(q) < exp(q)`, so `log(1681)<q`: the singleton is false.
`RESULT.json` includes the exact positive rational `T_49(q)-1681`, branch
trace and a second, code-disjoint log enclosure. The repair reports unresolved
instead of returning a false point. No smallest-integer claim is needed.

This input exposes a false result from the logarithm routine, not a silent
successful whole-verifier certificate: its existing sqrt-log agreement check
would reject `1681`. The analytic companion below also demonstrates a case
that this agreement predicate misses.

## A transparent analytic companion

Use the original defaults: Taylor order 48 and 72 bisection steps. Set

```text
t = 1/2
x = T_48(t) = sum(t^j / j!, j=0,...,48)
  = 5760972749428118686052076041890045281435609968042713023281691357997683350689
    / 3494206602297140433494533968898794487257007658542775390603638210560000000000
```

The original routine brackets in `[0,1]`. Its first midpoint is `1/2`.
`exp_taylor(1/2,48)` returns `[x,U]` with `U>x`, so neither strict comparison
succeeds. The `else` branch assigns `lo = hi = mid` and returns `[1/2,1/2]`.

But every exponential-series term is positive at `t>0`. In particular

```text
x < T_49(1/2) = x + 1/(2^49 * 49!) < exp(1/2).
```

Since logarithm is strictly increasing, `log(x)<1/2`. The returned singleton
is false. This proof needs no floating-point approximation, primary moment
engine, higher bisection precision, or theorem about transcendence.

In addition to `1681`, `RESULT.json` records ten constructed rational fixtures.
Seven use `T_48(t)` at dyadic
midpoints from `1/4` through `11/2`, exercising initial brackets `[0,1]`,
`[0,2]`, `[0,4]` and `[0,8]`. The other three, at `t=1/2`, include both
**strict interior overlaps** and the upper endpoint of the exponential
interval. Thus the issue is not confined to equality with the Taylor lower
bound, and the erroneous midpoint can lie on either side of the true log.

For the upper-side fixtures define

```text
U_n(t) = T_n(t) + [t^(n+1)/(n+1)!] / [1 - t/(n+2)].
```

For `0<t<n+2`, the omitted positive terms are bounded by that geometric
series. The bound is strict because the actual ratios eventually decrease.
Thus `exp(t)<U_49(t)<U_48(t)`. Both `x=U_48(t)` and
`x=(U_49(t)+U_48(t))/2` lie above `exp(t)` but inside the original
order-48 exponential enclosure. The below-side interior fixture is
`x=T_48(t)+t^49/(2*49!)<T_49(t)<exp(t)`.

## Minimal repair and its boundary

[`repair.patch`](repair.patch) replaces the false singleton return with an
explicit `ValueError('ln_exp_bisection unresolved at current Taylor order')`.
The patch targets only PR1293's `verify.py`; it is provided for its
author/reviewer, not applied to the selected construction or any frozen file.
The auditor applies exactly this edit in memory to the byte-pinned subject.

For the routine's accepted logarithm domain `x>=1`, the invariant is
`lo <= log(x) <= hi`. Initially `lo=0`, and a successful
bracketing loop stops only when `T_48(hi)>=x`, which implies
`exp(hi)>=x`. During bisection:

* `exp_upper(mid)<x` certifies the new lower endpoint `mid`;
* `exp_lower(mid)>x` certifies the new upper endpoint `mid`;
* otherwise neither direction is certified, so no completed cross-check is
  reported.

Every returned bracket therefore retains the invariant; unresolved comparisons
fail closed. This does not extend the original input range: the exponential
helper still requires `0<=t<9`, and `x=3000` still fails its domain check during
initial bracketing. Refinement to a higher Taylor order is not implemented.

An independent reviewer pointed out why merely keeping the old, wider bracket
is a weaker repair here: the caller tests only overlap with `ln_sqrt` and the
*sqrt method's* width. It never checks the cross-check's width. Indeed, the
false singleton for `x=T_48(1/2)` passes that existing agreement predicate.
A wide valid interval could also pass almost vacuously. The final patch thus
raises explicitly instead of reporting that partial result as success.

## Independent evidence and selected-input scope

The independent oracle in `verify.py` imports no repository arithmetic engine
and does not call the subject's exponential, square-root or log routines. It
writes `x=2^k*y`, `1<=y<2`, and uses

```text
z=(y-1)/(y+1)
log(y) = 2 sum(z^(2j+1)/(2j+1), j>=0).
```

With `N` terms, the omitted tail is at most
`2*z^(2N+1)/((2N+1)*(1-z^2))`, since `0<=z<=1/3`. The same formula gives
`log(2)`, and `log(x)=k*log(2)+log(y)`. All operations are rational. The
128-term enclosures are rounded outward to a `2^-384` grid. For each
counterexample the entire resulting log interval lies strictly to one side
of the false singleton; the repaired subject explicitly refuses the unresolved
comparison. The finite Taylor-tail argument above is a second, simpler proof
of the constructed counterexamples;
it does not rely on this oracle implementation.

The eight complex and eight bit rank-log arguments are reconstructed from the
pinned selected `ASSEMBLY.json` and PR589 `EXPECTED.json`, not handwritten.
Every one completes 72 steps without an unresolved comparison. For each,
the original and repaired intervals are exactly equal and contain the
independent oracle interval. These are **16 rank-log arguments**, not a claim
to cover every call in PR1293's full program; the separate whole-program
regression records the larger call domain, including its controls.

The separate `full_replay.py` imports no code from `verify.py`. It executes
both complete predecessor `main` programs in temporary trees and records
**41 calls over 19 distinct arguments, 2,952 bisection steps, 1,480 lower
updates, 1,472 upper updates and zero ambiguous comparisons**. The extra
arguments beyond the selected 16 are `2`, `73/6` and `73/42`; the remaining
control calls repeat selected arguments. All 12 predecessor controls pass.
Exact invocation order, logical caller stacks, branch decisions and returns
match. A separate positive trace fixture observes an ambiguity in both versions:
the original returns `[4,4]`, while the strict repair raises.

Both generated RESULT files and stdout are byte-identical; parsed results also
match. Each RESULT is 115,431 bytes and has the pinned pending RESULT SHA256
`731f77e404c18e3c1329d1ad084b3e0e3752579ae83fcb4e48a2b749d405c7a1`.
`FULL-REPLAY.json` records the deterministic census and traces. It is mandatory
in default mode and checked with type-sensitive canonical JSON comparison;
duplicate keys are rejected. This is a complete replay of **PR1293's arithmetic
verifier**, not a cold replay of the selected construction.

The subject's `Bill.residual`, `de_bound` and screening computation consume
`ln_sqrt`, not `ln_cross`. The faulty routine supplies a supplementary
agreement check. A false general contract in that routine alone does not
refute the independently computed endpoint signs, the D/E argument, or the
selected conditional kappa. Neither supplier word is rebuilt here.

## Reproduction

Python 3.12, standard library only. From the repository root:

```sh
python3 -I -B research/pr1293-log-enclosure-audit/verify.py
python3 -I -O -B research/pr1293-log-enclosure-audit/test_verify.py
python3 -I -B research/pr1293-log-enclosure-audit/full_replay.py
python3 -I -O -B research/pr1293-log-enclosure-audit/test_full_replay.py
python3 scripts/research_package.py --package research/pr1293-log-enclosure-audit
```

The first command recomputes and compares the deterministic `RESULT.json`;
it does not overwrite it. `--write-receipt PATH` explicitly regenerates an
alternate receipt. The full runner likewise defaults to comparison without
writes; its explicit `--write-receipt PATH` requires a JSON path outside the
repository. The last command validates package metadata and source provenance,
then runs all four registered commands above. See `VALIDATION.json` for
completed commands and the measured environment; timings are not mathematical
guarantees.

Controls cover exact `log(1)=0`, the compact integer witness, both strict
interior overlaps, the existing agreement predicate's failure to detect the
false singleton, wrong lower
and upper updates, a missing exponential tail at a larger allowed argument,
oracle range reduction and tail necessity, source/receipt/input/patch drift,
unique patch anchors, a null-return mutant that must not be mistaken for an
exception, and a relocated `-I -O -B` replay. There are 25 focused test groups
and nine separate full-replay CLI/receipt groups. Semantic mutations
execute altered arithmetic after loading the real source; rejecting a
checksum is not counted as an arithmetic failure control.

`SUBJECT.json` pins the original Git head, file blob and SHA256. The single
unchanged vendored verifier permits offline execution of the actual subject;
its own attribution is retained. The auditor enforces the exact subject identity
and required live-input inventory even during receipt regeneration. It parses
only checked input bytes, rejects duplicate metadata keys and source rows,
requires an internal ordinary vendor file, and compares type-sensitive
canonical receipts. `SOURCES.json` pins the main-branch inputs
and task provenance. `VERIFY.json` opts into the repository's bounded replay
hook. The registered hook's provenance checks require the base Git history;
the direct auditor and tests also work in a source export with their declared
inputs.

## Overlap, attribution and limits

The task chooser selected `independent-verification`, seed
`dc19910bd4791a6c0bc582fbfa4950c3`, priority revision 2. The local `TASK.json`
records why the `independent-moment` card was refined from a raw rank-ledger
recount to this enclosure audit. Public overlap inspection found that
PR1262, PR1307 and PR1329 already audit nearby selected profiles, while
PR1293 supplies endpoint/D/E work. None is claimed as a new result here.

Credit **Navinor (with help from opencode)** for PR1293 and its two logarithm
methods. Credit **woklerx's [PR1182](https://github.com/CrocSwap/integer-mult-bounds/pull/1182)**
(`0213b8911bfeefd5c81ddf320bac6a0fb7e86215`) for the earlier PR1048
false-bracket audit and tri-state repair principle. This is a different
source-bound instance, not the invention of fail-closed bisection. No PR1182
implementation is imported. The selected construction retains Rohan Arun,
Jeremy Kothe, Hao Yan, DreamingOfClouds, eumemic and the repository's full
credited lineage; this audit transfers none of their construction authorship.

The contribution is entirely AI-generated by an OpenAI assistant with
isolated research, mathematical-review, whole-program-replay and adversarial
review subagents. Independent implementations/checks here mean code/method
separation, **not independent human review**. New material and the vendored
subject are Apache-2.0; the repository LICENSE and NOTICE remain in force.

No selected-frontier edit, supplier adoption, full cold replay, Lean build,
hosted-CI result, all-size/compiler/hosting/precision proof or complete integer
multiplication theorem is claimed. Live searches do not establish exhaustive
novelty; their coverage and final freshness are recorded in `TASK.json`.

## Open next questions

* Should PR1293 add adaptive Taylor refinement or a typed unresolved result?
  This could recover a precise cross-check when the proposed explicit exception
  stops, without manufacturing equality. First step: decide the consumer's
  required width and test a bounded adaptive-order or tri-state interface on
  the supplied interior fixtures. Blocker: the predecessor author's interface
  decision; a broad interval must not be relabelled as a precise answer.
* Does a later PR1293 head incorporate a sound repair? Before reusing this
  finding, refresh its head and compare only this function and its call sites.
  The pre-publication refresh is recorded in `TASK.json`. This source-pinned
  package cannot attest to future edits or review acceptance.
