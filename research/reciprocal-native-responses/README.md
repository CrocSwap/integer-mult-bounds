# Reciprocal responses and native words on 112 ports

This package gives an integer reciprocal response with minimum correction
rank two in every dimension `n>=3`. It classifies the invariant diagonal
metrics of this family for `n>=5`. A diagonal metric of dyadic units exists
exactly for `n=4+2^h`, where `h>=0`.

The actual construction has eight six-mode blocks and eight eight-mode
blocks. Its 112-port response is `E=P R`, with `P^2=R^2=I`,
`rank(E-P)=16`, and `rank(E-I)=32`. Both `E` and `E^-1` have zero
diagonal in the physical basis and the native mode basis.

The package also supplies the complete local native words. Each word
acts on 640 arbitrary input fields and leaves the 416 fields outside
the two data banks unchanged. The coalesced word removes unused native
cuts and reduces the child count from 1,632 to 1,292. It retains rank
mass 1,792 and the direct scalar price of 6,440 real primitives.

These results do not improve the complete kappa calculation. Productive
helper progress, routed record access and restoration, a terminal
decoder, recursive admission, and a complete precision and supplier
calculation remain open. Correction rank is not a native cost.

Read [the proof](PROOF.md), [the native contracts and prices](NATIVE.md),
[the conditional three-call application](APPLICATION.md), and
[the source notice](SOURCE-NOTICE.md). The exact input list is
[SOURCES.json](SOURCES.json). The completed extraction replay is in
[VALIDATION.json](VALIDATION.json).

The [low-displacement supplement](annex/README.md) retains the exact
rank-30 and rank-16 responses, their local native words and coded exits,
and two scoped obstructions. It has a separate source manifest and
replay command. Its matrix classes and inverse-grid limits are explicit.

## Replay

Use Python 3.10 or later. The replay uses the standard library, one
process at a time, and no network or Git checkout. Run from this directory:

```sh
python3 -I -B replay.py --out /tmp/reciprocal-native-responses-replay
```

The output directory must not exist. The replay copies the frozen inputs
into that directory. It runs nine checks in normal Python and nine checks
with `-O`. It compares every result with its pinned receipt or payload.
The final line must be:

```text
PASS_RECIPROCAL_NATIVE_RESPONSES
```

`REPLAY.json` in the output directory records the environment, commands
by check name, times, and comparison hashes. The replay uses exact bytes
for plain receipts and decompressed bytes for regenerated gzip artifacts.
It verifies the immutable input bytes before and after all checks.

The checks cover the general-family regression, independent rank-two
review, actual model, original native emission, independent native
review, coalesced native emission with 206 new phase checks, ordered
three-call algebra, and conditional clean-reflection algebra. The
negative controls include a deleted nonzero transfer in each principal
direction, a changed inherited recipe, a wrong reciprocal direction,
and omitted pair-code restoration.

The original native review inherits the phases of 1,561 pinned recipes
and 224 endpoint adapters from its accepted predecessor. It does not
repeat the predecessor's spatial replay. The coalesced emitter gives
an exact Pauli and reference-column check for its 206 new recipes.
The clean-reflection checker is a matrix check. It does not emit a
native clean service. No complete supplier target runs here.

The files in `frozen/` retain their original bytes, dates, and local
scope statements. Their historical permission statements do not govern
this extracted package. The current claim limits are stated here.

## Open next questions

- Can the three 16-row source records be retained and restored by a
  paid invertible code? The first step is an explicit schedule at the
  three read cuts in `APPLICATION.md`. Arbitrary borrowed baselines
  and later frame progress are the current blockers.
- Can the rank-48 ordered residual be removed with a complete native
  terminal invoice? Start with the three inverse shears in
  `APPLICATION.md`. The output `Q` factors and ordinary hole access
  must remain in the calculation.
- Can the lower native moment of the coalesced words improve a complete
  supplier? Start with an admitted recursive host and include all
  helpers, views, scalars, side maps, and precision guards. The local
  child count alone does not answer this question.

OpenAI Codex gave substantial assistance in the construction, proofs,
code, checks, independent agent reviews, and package extraction.

