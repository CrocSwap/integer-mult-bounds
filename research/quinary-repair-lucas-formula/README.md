# A closed Lucas formula for the resonant repair rank

For every field F of characteristic five and every positive h divisible by
four, the proper-subset disjointness matrix A_h has

```text
rank_F(I-A_h) = (4*2^h - 2*L_h - 5)/5,
L_0=2, L_1=1, L_(n+2)=L_(n+1)+L_n.
```

Claim type: scoped written arithmetic proof with exact finite corroboration,
depending on Brian / JoyboyBrian's [PR5221](https://github.com/CrocSwap/integer-mult-bounds/pull/5221)
rank theorem. The new contribution evaluates its five-state integer recurrence
in closed form. It proves `total_blocks=(2^h+2*L_h)/5` for every even h.
The inherited rank and additive rank-one correction count are unchanged.
See [PROOF.md](PROOF.md) for the complete argument and premise boundary.

The Fibonacci multiplicities and modular Jordan theory are classical. David
Benson's [Section 5.1, page 83](https://homepages.abdn.ac.uk/d.j.benson/pages/papers/b/benson/banach-book.pdf)
describes the same tensor/Fibonacci pattern. The claimed contribution is its
explicit Lucas specialization to the repository's resonant repair endpoint;
no literature-priority claim is made for the classical ingredients.

## Evidence and reproduction

The direct verifier applies the quoted replacements as integer bookkeeping;
it does not import or replay a predecessor scientific verifier. Iterative fast
doubling and a separate binomial sum agree on all 513 Lucas values through
index 512. The literal recurrence agrees with 512 parity/multiplicity formulas,
257 even block-count formulas and 128 resonant rank substitutions. Fifteen
invalid inputs and five named formula mutations are rejected. A generated
stdout receipt binds every package file and the exact recurrence transcript.
No receipt is handwritten or committed.

From the worktree root, with the local interpreter or any CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/quinary-repair-lucas-formula/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/quinary-repair-lucas-formula/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/quinary-repair-lucas-formula
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/quinary-repair-lucas-formula --check-source-history
```

Expected direct marker: `PASS_QUINARY_REPAIR_LUCAS_FORMULA`. The registered
commands run both warning-strict normal and optimized modes, each with a
120-second limit. Direct verification needs only these six files and the
standard library. Repository metadata validation additionally needs reachable
Git provenance from [SOURCES.json](SOURCES.json).

## Limits and implementation bounds

The all-dimensional conclusion follows from the written arithmetic proof and
the cited rank premise. Bounded replay is corroboration. This contribution
does not audit PR5221's Jordan rules, deletion argument or matrix ranks.
Nonresonant dimensions, physical realization, native calls, routing, dirty
restoration, precision, stock, compiler and outer admission remain outside
scope. All five selected assumptions remain. No new kappa, selected-frontier
change or complete multiplication theorem is claimed. No predecessor scientific
suite, selected cold replay, Lean or Docker run is required or claimed.

The verifier has no recursion or subprocesses. Its outer domain is 0..512,
fast doubling uses at most ten bit steps and each binomial sum at most 256
terms. The bookkeeping has five integer counts; its extra terminal update
has total dimension 2^513. Each formula mutation checks at most 128 indices.
Explicit checks remain active under optimization. Power of Ten's fixed-memory
rule has a bounded CPython allocation deviation: arithmetic, six source reads
and JSON serialization allocate managed objects during this terminating run.
All functions are below 60 physical lines. Warning-strict execution and
in-memory syntax checks are the available diagnostics; no separate static
analyzer or formal proof kernel is claimed.

## Open next questions

Can a nonadditive physical repair avoid this additive rank obstruction?
First specify its arbitrary-input identity and full preparation, routing and
dirty-restoration invoice. The missing physical caller blocks any supplier
conclusion. No continuation is reserved.

## Credit and coordination

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

Credit Brian / JoyboyBrian PR5221 for the recurrence and rank theorem; Ali
Romman PR4962, Nick Petalas PR5173, mikey1201 PR172 and icekylinx PR144 for
the retained tensor, endpoint and compiler lineage; and David Benson for the
classical modular-representation context. Predecessor files and credits are
unchanged. Exact base-file Git and SHA256 pins are provenance, not live inputs.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370178).
Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities revision 8,
selected PR6030. This changes the coframe card to a historical arithmetic
side result, as recorded in [TASK.json](TASK.json). PR6469 studies the speed
of a bounded rank evaluator. No evaluator, matrix corpus or implementation
question from that work is extended here. Live handoffs, open PR bodies,
merged formula/object searches and main READMEs were checked. Arbitrary
historical diffs and unpublished work remain coverage limits.
