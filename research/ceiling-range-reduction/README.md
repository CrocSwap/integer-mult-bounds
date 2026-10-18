# Opt-in range reduction for the ceiling planner

The frozen planner fails `child_cost(16, 1024, Fraction(1,1000))` with
`RecursionError` at Python's normal recursion limit: its logarithm computes
every preceding integer recursively. Repairing only that logarithm still
leaves `ceiling({1:1},32768,10,1,0)` failing at the fixed upper probe `a=1/20`,
because the retained exponential accepts arguments only through one half.

This package provides one source-authenticated, opt-in adapter fixing both
limitations through exact range reduction. It leaves every frozen source file
unchanged. The complete retained selected and lever replays produce the same
ten exact grid brackets, byte-identical stdout and original selected receipt.
The new intermediate logarithm intervals need not equal the old intervals.

The logarithm regression is inside the existing exponential domain. The
exponential extension deliberately **enlarges an explicitly bounded helper
contract**; it does not claim that the old Taylor routine was wrong on its
documented interval. Neither change constructs a large-base decoder or proves
that a hypothetical planning profile is physically realizable.

## Interface

```python
import sys
from fractions import Fraction
sys.path.insert(0, "research/ceiling-range-reduction")
from adapter import load

C, _ = load()
print(C.child_cost(16, 1024, Fraction(1, 1000)))
print(C.ceiling({1: 1}, 32768, 10, 1, 0))
```

`load()` authenticates all declared live source bytes before compiling the
retained engine into a fresh private module. It replaces only that module's
logarithm and exponential functions. It does not alter an imported global
engine, write files, change precision, or migrate source pins. The same bytes
that are authenticated are compiled. `original=True` and `log_only=True` are
explicit comparison modes used by the regression checker.

All quantities are exact rational numbers or integers. The logarithm takes a
positive integer; the extended exponential takes a nonnegative ordered
rational interval. The inherited model's other premises, positive-saving
search window, grid separation and outer rank guard remain in force. Extremely
large values can still exhaust resources or produce intervals too wide for a
requested grid; this is not an unlimited-runtime or arbitrary-profile promise.

## Exact enclosure proof

For integer `k>=2`, set `e=k.bit_length()-1` and `b=2^e`. Then
`b<=k<2b`, so `t=(k-b)/(k+b)` lies in `[0,1/3)`, and

```
log(k) = e*log(2) + 2*atanh(t),  log(2)=2*atanh(1/3).
```

The retained atanh engine supplies outward rational bounds for positive
arguments through one third. The t=0 term is handled exactly. Multiply the
log-two interval by the nonnegative integer e, add the nonnegative reduced
term interval, and round outward on the same 256-bit dyadic grid. Every step
preserves enclosure. This requires at most two atanh evaluations, independently
of k's numeric value, and no recursion through preceding integers. Integer
arithmetic costs still depend on the input bit length.

For `0<=lo<=hi`, choose s by halving until `hi/2^s<=1/2`. The original Taylor
enclosure gives `[L,U]` containing `exp([lo/2^s,hi/2^s])`. Its bounds are
nonnegative. Repeatedly replace the interval by

```
[ down(L*L), up(U*U) ]
```

s times. Squaring is increasing on nonnegative numbers; each outward rounding
therefore encloses the next square. The final interval encloses
`exp([lo,hi])`. Inputs already within the retained domain delegate directly,
with exactly the original output. This is standard scaling and squaring; no
new numerical-analysis algorithm is claimed.

## Evidence and limits

The registered replay uses two independent arithmetic oracles: a positive
Mercator logarithm series with geometric tail, and an **unscaled** Taylor
exponential series with its own geometric tail. They do not call the adapted
atanh or exponential implementation. Their finer rational enclosures must be
contained in the adapter's returned intervals.

* 141 logarithm cases cover small integers, either side of binary boundaries,
  the original failure and `2^1000`.
* Seven exponential intervals exercise delegation, scaling, non-singleton
  inputs and repeated squaring through exponent eight.
* Eleven exact rational-power child costs include
  `(1/64)^(1-1/2)=1/8` and `(1/73)^(1-1)=1`.
* The original valid-input call actually raises `RecursionError` with the
  recursion limit temporarily fixed at 1000 and restored afterward. The
  log-only adapter actually rejects the full m=32768 ceiling probe.
* Complete original and adapted `levers.py` and `verify.py` entry points run,
  including the selected receipt, previous record and retained semantic
  controls. All ten grid brackets and complete stdout agree exactly.
* Fully declared hypothetical profiles certify strict moment brackets at
  m=1024 and m=32768. They are arithmetic planning fixtures, not circuits.

The m=32768 example has local profile `{1:1}`, ten families, one stage and zero
centre charge. Its saving bracket is
`[8804345729/10^14, 88043457291/10^15]`. `RESULT.json` records all parameters
and both strict endpoint checks. No new scientific bound is inferred from it.

Default replay is read-only, and source/receipt corruption and existing-output
controls are exercised on a Git-free export, including rejection of Boolean and
floating-point substitutions for integer receipt counts. Hosted CI, the selected cold
multiplication replay, native execution and production pin migration are not
claimed. There is no wall-clock speed claim.

## Reproduce

```sh
python3.12 -I -B scripts/research_package.py --package research/ceiling-range-reduction
python3.12 -I -O -B research/ceiling-range-reduction/verify.py
```

`--out NEW.json` explicitly writes a freshly recomputed receipt and refuses an
existing path. The adapter is intentionally opt-in; frozen users retain their
original behavior until a separately reviewed migration.

## Provenance and decision

Douglas Colkitt and the original Claude-assisted ceiling engine retain credit
for the model, atanh/Taylor bounds, selected fixture and controls. Earlier
repository packages already use binary logarithm reduction. PR2441 caches
child intervals; PR2552 replaces the bounded Taylor loop with bit-identical
integer arithmetic. Those are distinct performance changes. This result
repairs the demonstrated larger-domain interface and preserves the frozen
source inventory. The adjacent exponential limitation was independently
identified by another Codex agent and is included in this one contribution.

The original picker nonce `bb9f853220a03e57e0cfc933b855eedc` selected P104.
During that work PR2640 published the same proposed cut theorem. The duplicate
was retired, and the independent checks were credited in
[the handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2640#issuecomment-6197406963).
`TASK.json` records the changed scope. The decision is to finish this concrete
planner repair, without expanding an unresolved P104 construction.

Scientific source bytes and provenance remain pinned to `b4560d9e`; the branch
was refreshed to `bd0f9667` before submission. The newer reconciliation leaves
these nine live inputs and the priority-five instructions unchanged.

## Open next questions

Should this adapter be promoted through an explicit source-pin migration?
First identify every affected consumer and compare its complete receipt at its
own declared precision. The present opt-in module supplies no such migration.
An actual new large-base local word must separately state and pay its coverage,
ownership, restoration and consumer costs; a numerical bracket is only its
planning screen.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review or new supplier admission is claimed.
