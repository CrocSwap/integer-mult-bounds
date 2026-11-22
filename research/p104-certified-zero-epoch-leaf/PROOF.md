# Proof boundaries and checks

## Source and computation domain

The literal graph is the 630-owner, 39,600-instruction binary source from #8027, compressed SHA-256 `74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`. The paired 798-event caller, compressed SHA-256 `757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b`, has 36 `LOCAL` calls and 18,906 separate productive jobs. The source archive is the exact predecessor retained by #8035, whose head is `ea776471bf8ed143a0625cf2d7532f65d15eb5f9`; #8035's overlay changes the allowed powers and pricing profiles, not the native input, instruction or bank semantics used here. The exact #8041 graph and caller are pinned in `pinned/`. Every source input may be an arbitrary whole field in the supplier's all-column contract. Address permutations, local XOR, swaps and initialization are linear on these fields.

The installed fixed-stock profile uses `v=268` and a productive rank floor `15^268`. `PoweredWord.native` allocates every target tuple below that floor as a separate live zero owner and retires it after the complete native execution. The full tensor is far too large for literal enumeration in this control. Algebraic identities about it are proved by finite induction on its factor count; the small cases are executable checks of the actual iterator and physical source.

## First paid tuple

The first four caller events are root-only `ADD`, `SWAP`, `ADD`, `SWAP`; event 4 is `LOCAL` and binds its own 408 distinct helpers. Before the first graph `MOVE`, the literal tape executes only

```
INIT 630, chart 0
ADD 630, 222, chart 0
MOVE 630, chart 0 -> chart 2
```

The first yielded paid label is therefore `('move', 4, 2, 630)` of rank 1. Its payload is a zero-preserving chart transform of the event-4 helper 222. The corresponding public helper has endpoint rank 8. No earlier paid action or root-only prelude reads that helper, and owner 630 is newly initialized. These statements do not require any restriction on the other inputs and hold for arbitrary field values.

In `PoweredWord.native`, each tensor level instantiates one raw frame for every remaining productive suffix, advances every frame to the next paid label in source order, and recursively serves the set of resulting requests. For the first paid label at every level, induction selects exactly the original productive path `(helper,4,222)` in every coordinate; all intermediate operations on that path are initialization, copying, and chart routing, which preserve the zero field. The terminal original path has rank `8^v`; for floor greater than 8 it was allocated by `fresh` as a distinct zero bank. Consequently the first powered yielded job is a full zero field at every physical column, not merely a binary constant or an assumed equality of particular inputs. All 268 paid ranks equal 1, so `blocks()` emits one rank-one block per column.

This argument is tied to the actual `PoweredWord.native`/`StrongBinarySource` prefix and its separate owned banks. A certificate based only on a matching label is insufficient for a different interpreter. The prototype stores a typed witness and checks the embedded sources and source-port lists; a production integration must also bind its runtime implementation and its bank, chart and owner contracts.

## Where the skip would occur

`epoch_tape.epoch` writes a chronological sequence of frame opens, `ISSUE`s, closes and `FINISH`es. `epoch_tape.run` advances the native iterator on every `ISSUE`; `FINISH` serves any unconsumed tail by calling `machine.leaf` once per remaining axis. Do not delete the `ISSUE`: it starts the required native request and keeps every source frame aligned.

A unit with no child that borrows its first issued loan has a zero field from its `ISSUE` through its `FINISH`. The first loan is a private live source owner; the bounded prototype also rejects a loan that was borrowed or shared with another active loan. Skipping a leaf permutation of a zero field preserves the complete data state. At any deepest unit of a nonempty finite band, the child-consumed count is zero and `columns=x//denominator-1` is at least `floor-1`, hence positive. Thus at least one actually scheduled elementary leaf exists under this conditional implementation argument. The prototype's one-unit finite plan exhibits exactly one such leaf without counting a tensor tuple itself as an elementary action.

`certified_epoch.py` keeps `ISSUE`, `CLOSE`, owner cleanup, and all other `FINISH` handling. It tracks each frame's paid ordinal and each first loan's borrowed/aliased status. This is not a drop-in patch of #8035: its certificate is a caller-supplied source binding, and the cost of its frame counters, loan flags, alias tracking, proof generation, tape operations and any physical routing must be included before claiming a complete compiler saving. It also conservatively declines the skip if the certified loan was borrowed, even if a separate proof could show it returned zero.

The bounded fixture uses one hand-constructed unit and a source wrapper that exposes only the first block to the epoch. It still executes every subsequent real graph/caller paid block inside the same frame in its original chronological order. It uses two symbolic field positions and represents each leaf as their transposition. It does not claim to reconstruct the actual full rational chart. All 5,772 independent symbolic input bits are propagated in one run, so equality of every public output form proves equality for all inputs in that finite model. The positive input control puts nonzero data into helper 222 at floor 8, where the helper is no longer fresh; an unsafe skip then changes 109 outputs. The certificate explicitly rejects that floor.

## Forward map and transpose

For any given compiled execution, a skipped leaf applied to a zero bank is the identity on the full current state. By induction, all later operations, outputs, and cleanup match the old forward execution. This applies to every admitted input when the zero-source proof applies. Thus the complete linear public maps are equal, and their transposes are algebraically equal. The retained target permutation is an involution, so a correctly implemented forward service run again gives its inverse. This statement does not provide a legal literal reverse schedule for the private `CLEAR` instructions, whose dirty-bank erasures remain charged and require their inherited physical treatment.

## Single-source family

The census propagates unions of public input labels and a Boolean paid-taint flag. `ADD` unions the labels and ORs taint; `SWAP` exchanges both; `INIT` supplies the empty set; a `MOVE` records its state and then sets taint. The outer caller's paid `QUERY` and `IDLE_ONE` are likewise marked. This conservative analysis never uses cancellations and counts a label only if its payload has exactly one input and its entire dependency has no earlier paid action.

The per-factor census is:

| Target rank | Paid rank | Labels |
| ---: | ---: | ---: |
| 4 | 1 | 288 |
| 4 | 2 | 108 |
| 8 | 1 | 7,848 |
| 8 | 2 | 5,508 |
| 8 | 4 | 72 |

All 13,824 labels use a single helper. Any tensor product of these labels depends on a single original target tuple of ranks at most 8, with no prior paid operation on the contributing path. Its target rank is at most `8^268 < 15^268`, so it begins as a fresh zero field. Its paid rank is at most `4^268 < 12^268`, so the corresponding paid tuple has exactly one block, of rank equal to the product of its factors. The dataflow conditions apply separately at each synchronized tensor level and permit unrelated field operations before the selected label. The prototype certifies only the first tuple, not the entire census family.

At κ = `0.00389046`, write `t=1-κ`. The family's complete raw rank moment is `(8136 + 5616·2^t + 72·4^t)^268`. The price reader produces outward integer-root enclosures for the pinned target and paid histograms. Integer arithmetic checks that this family is less than `10^-300` of the full, unpruned target moment. It also checks that, after removing the entire family with no offsetting costs, the raw paid moment exceeds the full target moment by more than `10^-4` of the full target moment. The productive cutoff and paid splits only make that optimistic comparison harder. Thus this family cannot establish the trial κ; no model-wide ceiling follows from this local arithmetic.

#8034's ordered support transport already rules out a positive raw moment at or above its pinned rate for the broader, explicitly stated rule that bills full paid tuples whenever their conservative Cartesian dependency support meets the retained target set. Each selected single-source tuple here has singleton support and misses that set. The present result does not challenge #8034, and #8034 does not by itself install this particular physical `FINISH` check or price its control overhead.

## Existing clean versus retained helper inputs

The graph's raw helper coordinates are separate productive jobs, not uniformly zero. With all other 267 productive factors at rank 127, `4·127^267 > 15^268`; all first-factor jobs are retained. The complete-caller constant-field witnesses use only this allowed source-service subdomain. The chart-510 one-export variants fail, and the named pair has two independent input kernel vectors. The chart-531 relay fails on a retained root input even with the event-4 helpers all zero. This does not prove those source assignments arise from particular integer operands at the public multiplication entry.

Conversely, 186 suffix factors of rank 8 and 81 of rank 64 yield `A=2^1044` with `8A < 15^268 <= 15A`. All first-factor rank-8 and rank-4 targets are already fresh zero; 34 root roles of rank at least 15 remain productive. On their 3,774-dimensional binary constant-field subspace, the full caller replay agrees after both chart-510 local export deletions. This is a local slice observation: the stock powered interpreter synchronizes all suffixes, so it is not by itself a deleted charged tensor job.
