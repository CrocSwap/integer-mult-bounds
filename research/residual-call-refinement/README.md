# Conditional residual and CALL refinement

This package independently audits one all-width implication in Jose Manuel's
PR2809 fixed-role lowering. Under its completed-operation, stock, canonical-input
and parking contracts, the literal residual blocks and successful CALL/RETURN
preserve the source residual's complete packet and chronological continuation.
[PROOF.md](PROOF.md) states the quantified theorem and its hypotheses.
The grammar and construction are predecessor results. This contribution adds
an independent argument and a separately implemented finite oracle.

The source baseline is main `d8e0f83f00191df62174b641e9fff055c357f641`, priority
revision 6. It retains PR2809 `e7d93dd0de0bb81308bc3356f65eddeeb22fd712` with the
documented selected-record loader adaptation. [SOURCES.json](SOURCES.json) pins
132 live input files before source execution. Frozen sources are unchanged.
The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18982149)
takes PR2989's released residual/CALL handoff.

For every admitted width, a half reset leaves exactly `f mod 2` central atoms
as spectators. Child regrouping preserves their ordered coordinates and the
original external gap exactly once. Fresh rows `U` remain a separate child row
factor. CALL copies its capsule before borrowed event words are released, and
RETURN restores the parent with only `current` replaced, at the saved successor
PC. Restored Program views represent the unchanged encoded source program;
Python object identity across calls is outside the relation.

## Finite evidence

[RESULT.json](RESULT.json) records these independently reproducible checks:

- Both retained trace emitters agree with an integer-address grammar oracle on
  100 synthetic plans/widths, 45,896 events and 540 blocks. Dimensions are 2, 3
  and 64, plans have at most eight commands, and widths include both sides of
  the leaf and half-reset thresholds. This is not the complete selected
  32,808-command fallback trace.
- The literal encoded `Layout.child_extents` agrees on 90 complete small
  geometries. All three positions of the external gap and odd/even half-reset
  spectators occur. Every case preserves the complete volume identity.
- Eight actual selected-descriptor CALL/RETURN fixtures check source and full
  directory bytes, root and appended program fields, grants, fresh rows,
  spectator counts, parent restoration and an arbitrary protected return.
  They use a nonzero parent remainder at `n=257`. The good child keeps cutoff
  64. The fallback fixtures lower the dispatch cutoff to 2 to reach both half
  cuts economically. The controlled 23-bit payload is not a complete GL64
  packet or a child implementation. The finite field is `q=3`, outside the
  source's admitted large-prime domain.

Four changes to the literal block emitter must fail: an omitted reset,
duplicated ENTER, lost half flag and two extra cancelling signs. The last
preserves an endpoint but changes intermediate cuts. Lost source/directory
handoffs and a repeated successor PC also fail their contextual relations.
Behavioral tests additionally reject source corruption and a Boolean/integer
receipt substitution. The internal code review identified the missing handoff
byte assertions; this package includes the correction and both loss controls.

The written theorem assumes completed children. Strong width descent can close
that assumption only after the enclosing node correspondence is established.
Completed operations, recursive stock, physical packet execution, full storage,
head movement, H2 costs, interruption recovery and supplier admission remain
outside this result. The selected conditional kappa remains
`0.001672660197076918`. No new exponent or complete multiplication theorem is
claimed. Evidence is author-checked with separate internal proof/code review,
without independent human or formal-kernel verification.

## Reproduction

Python 3.12 and the standard library suffice. From repository root:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/residual-call-refinement
```

`python3.12` can replace the `uv` prefix. The registered commands run the
source-bound verifier and optimized behavioral tests. Verification is read-only
and compares the typed saved receipt; it does not regenerate it. The generic
metadata check separately resolves historical Git provenance.
[ENGINEERING.md](ENGINEERING.md) records bounds and runtime deviations.

## Open next questions

Compose this residual lemma with PR2989's separate whole-word ordering audit,
then bind actual NODE/peel/split and MERGE/return to their complete source
coordinate and ownership contracts. That enclosing-node implication is needed
for recursive closure. Separately, audit one reached weighted leaf or route
with its complete physical cost and stock contract. The existing exponent
comparison alone does not supply these hypotheses. [TASK.json](TASK.json)
records first steps and blockers. This result initiates no construction-family
expansion.

## Credit

Jose Manuel, `jmbarrancoml`, supplied PR2809's fixed-role compiler, descriptors,
parking composition and controlled selected CALL fixture. David Arias supplied
PR2753's logical caller. The retained source credits Jose Manuel's PR2769
numerical codec, ywz65's parking/controller work, commdata2338's substitution
algebra, Aakash Thakkar and Sagar Thakrar's stock work, PR2157's factor words,
and the selected PR589/PR555/source527 lineage. Their complete notices remain
in the unchanged source package. PR2989's separate whole-word audit retains
its scope and credit. Nick Petalas contributes this independent scoped proof,
oracle and checks. Apache-2.0. Process assistance is disclosed in TASK.json.
