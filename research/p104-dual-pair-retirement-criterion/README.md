# Pure dual-pair retirement criterion for equal-target classes (no κ)

**No new κ.** This package states and proves when one independent input of an equal-target class can be
retired at a cut, shows how many can be retired at once, and checks the statement exactly on the literal
words of #6716, #6726 and #6805.

## Result

Let `P` be the prefix matrix at a cut, `X = SP` the endpoint, `G` a class of inputs with `X = tau I` on `G`
(block diagonal), `RF` the registers one ordinary event can combine at the cut, `s` a unit job (a monomial,
`lambda` times a monomial, or a chart), over the dyadic ring `D = Z[1/2]`. The following are equivalent
(`PROOF.md`, Theorem 2.1):

1. basis changes `E` on `G` (at the start, inverted at the end) and `A` on `RF` (at the cut, inverted after it)
   exist such that, after emitting the pivot register and loading a fresh independent input, the word computes
   the old endpoint with the diagonal entry `tau` replaced by the two independent jobs `s` and `tau/s`;
2. `A P E` has the pivot column `s e` and pivot row `s e^T`;
3. a **pure dual pair**: `P c = s u`, `a P = s d`, `a u = 1` with `c, d` on `G` and `u, a` on `RF` (then `d c = 1`);
4. pure columns and pure rows of `s` with `d c = 1`.

The completion is explicit over `Z[1/2]` (Euclid on odd parts, `PROOF.md` section 3): `d c = 1` already splits
`D^G`, and no separate primitive-vector or Hermite condition is needed.

Further statements:

* Ordinary events do not change the pairing, so only cuts after non-ordinary events need to be examined (4.1).
* The number of simultaneous retirements of one job at a cut is the number of **unit** elementary divisors of the
  pairing, not its rank over `Q` (5.1). An explicit rank-one pairing with divisor 3 admits no retirement.
* Cuts inside native calls: helper classes see only the native block (6.1); caller classes reduce to the caller
  cut before the call (6.2); consecutive calls never share a pair (6.3). The statement stops at interleaved calls.

## Hypotheses and scope

The retirements covered are of the conjugation type defined in `PROOF.md` section 1. Hypotheses: equal-target
class with block-diagonal endpoint (H1); the frames of `E` (start and end) and `A` (cut) (H2); a principal
ideal domain of scalars with elementary generation (H3); a unit job (H4). The section on levels works in an explicit
block model. Outside the scope: rewrites that change more than the pivot slot, scalars outside `D`, jobs that a host
grammar does not accept, cuts needing `A` across frames, classes mixing caller roles with helper inputs, and
interleaved calls. Pricing and the framework assumptions of the cited words are not re-derived.

## Exact checks

| Word | Check | Result |
|---|---|---|
| #6716 unretired caller | census of all non-ordinary cuts, classes, jobs | one pair: cut 353, class {4,20,21}, lambda-type job, Gram [1]; retired word replayed on 35 columns |
| #6726 unretired caller | same | pairs at cut 158 (monomial job, class {6,7}) and cuts 383, 392 (class {4,5}); each retired word replayed |
| #6726 final caller (caller of #6805) | same | no cut carries a pair or a rank without a unit (606 events) |
| #6805 native word with the retimed move | cut 12372, frame 243, class of helper 368 | pure columns dim 4, pure rows dim 1, Gram [4,4,4,4] (unit of `Z[1/2]`); retired endpoint on all 771 public inputs |
| controls | pivot outside the class; non-pure row; non-pure column; zero pairing; frame without the retimed role; word without the retiming; rank one without a unit | each rejected with the stated reason |

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-dual-pair-retirement-criterion
```

or directly (about 6 s):

```sh
python3 -B research/p104-dual-pair-retirement-criterion/verify.py
```

Expected markers: `PASS_DUAL_PAIR_RETIREMENT_CRITERION`, and for the launcher `PASS_REGISTERED_RESEARCH_PACKAGE`.
`retained/` holds unmodified copies of the inputs with their pull-request pins in `retained/SOURCE-PINS.json`;
`SOURCES.json` binds the same bytes to their origin commits.

## Relation to earlier work

The helper-basis criterion of Ali Romman (a b = 1 completed by dyadic ADD and SCALE events) is the completion
step used here. #6716 (thu-nmrc), #6726 (zxv) and #6805 (CubeJerry) each exhibit one dual pair at a literal cut
and use it to retire an independent input; the statement above covers those cuts and gives the converse. #6764
(CubeJerry) states the pair conditions as a necessary interface for the binary full-bank model; the
present statement is for general equal-target classes with the converse, the unit-divisor count and the level
propositions. Source: #6702 (DreamingOfClouds) for the native word.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

* Can two native calls be interleaved so that helpers of both are resident in one interior frame, and does a pure
  pair exist across them? (6.3 does not cover it.)
* Is there a literal equal-target class that mixes caller roles and helper inputs?
* Does the unit-divisor count equal the rank over `Q` at every cut of every native helper group of #6805?
