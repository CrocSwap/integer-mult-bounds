# P104 K17: type-A invoice and mask-dependent correction

## Result and scope

This is an accounting and finite-arithmetic check of the K17 formulas in
PR #7852 at `41beda1d6435760dc99e38bd7e65f36798aad212`, with the caller
from PR #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d` as a separate
control. The existing `SchemaCostB.repo_eq` already proves the general exact
correction under its stated tight/block hypotheses. `SchemaCostC` proves the
two stage facts needed to specialize it to type A: four charged singleton
contacts and two odd host columns per stage (`GramA.jm`, `GramA.jc`). The
draft `the local draft Lean wrapper` writes out this specialization and the type-A
real-invoice headlines; **the draft has not been run through Lean**.

The independently checked #7113 arithmetic gives a zero correction for
type A and a positive ports-weighted correction for type B. This does not
prove that the JSON is represented by a `Legal` Lean word, establish an
unconditional caller ceiling, or make a new κ claim. The `k >= 77` K16/K17
bound does not apply to this 17-stage control.

## Exact accounting

Fix `s = 99/100`. For each integer `d >= 1`, put

```
δ(d) = 1 + (8d)^s - (8d + 1)^s,     δ(0) = 0.
```

Consider a `GramA n k` or `GramB n k` block, with `k > 0`, `PlainOK` for
all plain pre/post events, and `n + 2 = |Iota word|`. Let `N_d` count
occurrences of plain `IDLE_ODD` events whose stage set has size `d`, with
repetitions counted. Let `Q = n - (2k - 2)`, regarded as the number of
plain thin columns; `excess_eq` supplies this equality. It follows that
`sum_{d>=0} N_d <= Q` because each odd idle contributes one thin, and QUERY
can contribute additional thins.

The pinned theorem `repo_eq` and its definitions give

```
repo = (k/104) * cHatQ + sum_{d>=1} N_d * δ(d).
```

There is **no** contribution to this correction from QUERY, IDLE_ONE,
arithmetic events, or an odd idle with empty stage set. For type A,
`repo` subtracts `4 k 8^s` in native contacts, while type B subtracts
`2 k 8^s`. That factor of 4 versus 2 must be distinguished from the two
odd host columns of either schema. If additionally the existing `gramA_hpq`
or `gramB_hpq` hypotheses hold, including legal grammar, tightness, each
K-block unit, every role of positive degree, and `k >= 77`, the corresponding
formal reduction implies

```
104/k * repo < 128.891 + 104/k * sum_{d>=1} N_d * δ(d).
```

This inequality is a mathematical consequence of the pinned Lean statements;
the new wrapper in `the local draft Lean wrapper` is not independently kernel checked.
For Q = 0 the existing `repo_eq_q0` specializes to type A with contact
constant 4. The model invoice and this repo quantity are then exactly equal
after normalization, under the same accounting hypotheses.

## Monotonicity and exact quantifiers for the mask cap

For real `x > 0`, `g(x) = 1 + x^s - (x+1)^s` has
`g'(x) = s * (x^(s-1) - (x+1)^(s-1)) > 0` because `0 < s < 1`.
Hence `δ(d)` is strictly increasing for positive integer `d`. Also
`δ(0) = 0` and concavity gives `δ(d) >= 0`. These are ordinary mathematical
arguments, not new Lean proofs.

Every stage set `S : Finset (Fin k)` in the **generic** Lean block satisfies
`|S| <= k`. Thus, for `k >= 1`, the exact per-event upper bound is `δ(k)`;
without further hypotheses one cannot impose a fixed numerical cap below 1
as `k` increases. The upper value is attained by the full stage set at the
level of an individual plain odd-idle event. This statement does **not**
assert that a full-set event occurs in any word satisfying all legal-word,
frame, degree, and K-block conditions.

There is an additional, explicitly conditional packed-data cap: if each
odd-idle event has a corresponding packed value `x` satisfying the
`SchemaCostC.price_eq_item` hypothesis
`CertCaller.popc (CertCaller.evSt x) 26 = |S|`, then
`|S| <= min(k, 26)`. Write `m = min(k, 26)` and let `N = sum_{d>=1} N_d`.
Under that matching hypothesis,

```
sum N_d δ(d) <= N δ(m) <= Q δ(m) < 0.062 Q   (when Q > 0),
sum N_d δ(d) = 0                               (when Q = 0).
```

The sharp constant for the isolated local event under this cap is `δ(m)`;
no sharpness of the aggregate over legal words is claimed. Merely defining a
generic `GramA` or `GramB` does **not** establish the 26-bit matching
hypothesis. The finite certificate checks `δ(d) < 0.062` for each
`1 <= d <= 26` using rational bounds; it does not replace a generic Lean
proof of the 26-bit bound.

The #7852 body suggests that `|S| >= 1` might yield a `~0.05` cap. Taken
literally as a universal upper bound of `0.05`, this is false: exact
rational interval checks give

```
δ(1)  in [0.030955909132874445, 0.030955909132874448]
δ(7)  in [0.049143964763191081, 0.049143964763191084]
δ(8)  in [0.050402327701513170, 0.050402327701513173]
δ(17) in [0.057494533251727738, 0.057494533251727741]
δ(26) in [0.061478689829624903, 0.061478689829624906]
δ(77) in [0.071598434150368199, 0.071598434150368202].
```

The size-8 control is an admissible **local event** with `k >= 8`; it is not
offered as a complete legal-word counterexample. The size-77 control belongs
to the generic model, not to a 26-bit-matched packed record.

## #7113 event alignment

The exact caller JSON has SHA-256
`255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`,
4,783 records and 17 ordered J records. Each type has 36 target roles with
odd exponent -1 and positive binary stage masks. Each type has Q = 4 by
its modeled odd-column count: `|Iota| = 2*17 + 4 = 38 = n+2`. The check
validates the explicit J field distinctness, gauge, and input record shapes;
it does not independently prove the word's Lean `Legal` field or its
K-block-unit hypothesis.

| Type | Ports | Plain thin events | Nonempty odd-idle masks | Exact correction per port |
| --- | ---: | --- | --- | --- |
| A | 96 | four odd QUERY | none | 0 |
| B | 8 | four IDLE_ODD | four masks of size 1 | `4 δ(1)` |

The B odd idles occur at JSON event indices 1339, 1340, 2970, 2971
(zero-based), with stage sets `{8}`, `{8}`, `{9}`, `{9}` in the 1-based JSON
notation. They are charged at rank 9, while the event form subtracts rank 8
and the excess-role term subtracts 1. After ports weighting and division by
17, the correction is `32 δ(1)/17`, in
`[0.05826994660305777882, 0.05826994660305778448]`.

The recounted weighted target and plain-paid histograms exactly match
`UniCaller7113Facts.CallerFacts.hT` and `.hP`. In particular, type A pays
four rank-1 QUERY items per port; type B pays four rank-9 odd-idle items
per port. With all native contacts included as `17*(96*4 + 8*2)*8^s`, the
weighted real repo quantity divided by 17 is in
`[105.94741840800697563764, 105.94741840800697647624]`. This is a caller
invoice component, not the complete multiplication cost or κ.

## Replay and controls

Run `python3 -B check_invoice.py` in this directory. The script reads the
pinned caller JSON, verifies its SHA-256, validates relevant shape and gauge
fields, recounts the two histograms and compares them with the pinned Lean
facts, checks the symbolic equality of repo-minus-model to the exact delta
histogram by type, and certifies power intervals using integer arithmetic:
for denominator `D=10^18` it verifies `L^100 <= n^99 D^100 < (L+1)^100`.
It checks `δ(7)<0.05<δ(8)`, the empty-set zero control, all adjacent
intervals for `d=1..26`, and `δ(26)<0.062`. Printed decimals are rounded
outward from the rational intervals. This replay is not a Lean proof.

Independent adjacent control: `the adjacent thin-window checker`
constructs an abstract LawQ configuration with a size-1 odd-idle correction
at k=77; it is not a signed-Gram frame or a legal caller. It supplies a
useful warning about transferring a model-invoice threshold to the corrected
repo invoice, not a counterexample to a legal-word theorem.

## Attribution and provenance

The accounting lemmas, grammar form, `CertCallerCore`, and pinned caller
facts are by PR #7852's authors DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code; the #7113 caller and replay are credited in
their own upstream package. This check adds the event recount, elementary
monotonicity argument, quantified caps, and independent exact-arithmetic
controls. Exact paths and SHA-256 pins are in `SOURCE-MANIFEST.txt`.

## Open next questions

Derive a sharper signed-product restriction on the sum of odd-idle mask sizes.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
