# No saving from an orthogonal binary basis and one bridge

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

Take all projectors of any even-dimensional binary orthogonal basis
on an old coordinate space. Add one fresh pairing-one bridge whose
incidences with all old projectors are one. Coordinate old projectors
are allowed. Every type must occur; extra types are excluded.

Let k be the actual off-diagonal pattern dimension. Over the
paid-generated torsion-free abelian exponent group, a word with at most k
saturated exponent relations and a full diagonal monomial endpoint
has one consecutive cancelling bridge block. That block can be deleted
on all ambient inputs. Physical target exponents are sums of disjoint
paid subsets, so total rational target rank cannot exceed paid rank.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [CREDITS.md](CREDITS.md)
and [TASK.json](TASK.json). The new proof identifies the full diagonal
kernel by a Boolean partition and proves star independence for any
old basis. It keeps the physical target multiplicities explicit.
The normal-form basis change is not a free operation.

As a corollary, the no-edge pattern-five, irreducible-image-seven
family classified in
[PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691)
cannot save rank at five exponent relations. This family is outside
the extremal edge-core hypothesis of
[PR #7694](https://github.com/CrocSwap/integer-mult-bounds/pull/7694).

## Reproduce

Use CPython 3.12 and its standard library, from the repository root.

```sh
python3.12 -I -W error -B research/orthogonal-basis-bridge-obstruction/verify.py
python3.12 -I -W error -B -O research/orthogonal-basis-bridge-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/orthogonal-basis-bridge-obstruction
```

Expected markers are `PASS_ORTHOGONAL_BASIS_BRIDGE_OBSTRUCTION` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier compares all results
with the committed receipt and writes no file.

It checks all 20166 binary bases at old dimensions two and four,
130320 degree-two type orders, 20880 full Laurent words, and eight
ambient fixtures with repeated types and dirty spectators. A single
four-block control shows why the actual conjugated diagonal algebra
must be used in the quotient. Coordinate old calls and a pattern-one
case are included.

## Limits

The theorem concerns the stated one-bridge alphabet and its relation
budget. Extra types, omitted types and larger budgets are not covered.
It is not a classification of every subextremal projector pool.
The no-edge corollary uses the pinned classification and image bound.
Finite tests corroborate the written all-width and all-length proof.

No native supplier, rounding contract, complete multiplier invoice
or new kappa is supplied. The selected frontier and all five assumptions
remain unchanged. Independent human and formal-kernel review are
unclaimed. Full predecessor package replays, selected cold replay,
Lean and Docker were not run.

## Open next questions

Can a specified second nonorthogonal bridge or a larger relation
budget support a legal saving? State the whole alphabet and paid/target
invoice first. A failure of the one-bridge hypotheses does not supply
a saving or a native interface.
