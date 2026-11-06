# Positive signed halves in linear tape time without clean work cells

For every signed W-bit input, W>=2, and resident read-only coin u, the
fixed table in this package computes

```
(x, parity=0, u) -> (floor(x/2)+(x mod 2)(1-u), parity=x mod 2, u)
```

and explicitly reverses it. Each direction takes at most **4W+1 local tape
transitions**, including head return. The bound is attained by x=-1,u=0.
Only the W value cells, one retained parity cell and one stationary coin
cell are visited. There are **no additional clean working cells** and no
width-dependent program tape. The table has 33 rows per direction.

Claim type: scoped constructive proof with exact finite corroboration.
The result is a local physical arithmetic component, with no new kappa,
complete supplier or selected framework assumption discharged.

## What this adds

[zxv's PR6092](https://github.com/CrocSwap/integer-mult-bounds/pull/6092)
posed the optimized-layout/faster-program question. Its positive-half
implementation has W clean working cells and an O(W^2) unary-walk program
envelope. Those statements and its arithmetic contract are cited inputs;
its executable is not imported or replayed here.

This implementation changes the boundary to a marked parity cell and marked
sign cell, followed by literal local scans and ripple increment/decrement.
One tape holds the value/parity cells; a second supplies the stationary
read-only coin. These markers and the resident coin are input premises.
The 66-row `TABLE.json` works at every width without an addressed operation
or width counter. [PROOF.md](PROOF.md) gives the invariants, signed range,
exact inverse image, transition formula and a 2W movement lower bound.
Each directional table also satisfies the finite local injectivity criterion
for a partial reversible Turing machine. Direction remains a compiled choice.

This is a different local layout from the prior unary interpreter and from
AAAmirinu's [reached-coin wrapper, PR6244](https://github.com/CrocSwap/integer-mult-bounds/pull/6244).
Layout conversion and coin delivery must be charged before using the gain
in a caller. The negative-coefficient half is not implemented.

## Evidence and reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/linear-positive-half-tape/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/linear-positive-half-tape/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/linear-positive-half-tape
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/linear-positive-half-tape --check-source-history
```

Elsewhere substitute a CPython 3.12 executable. There are no dependencies
or external runtime inputs. The direct verifier writes only stdout, including
a newly generated receipt bound to package-file hashes, then prints
`PASS_LINEAR_POSITIVE_HALF_TAPE`. Checks use explicit exceptions and remain
active with optimization.

The finite replay covers:

- 16,376 exhaustive signed-input/coin cases at widths 2 through 12, executing
  786,356 forward/inverse transitions.
- 328 larger or translated cases, including signed extremes through width
  4,096 and exterior spectators, executing 500,012 transitions.
- Every inverse boundary point through width eight: 1,016 valid points
  accepted and 1,016 nonimage points rejected.
- Every table row's local injectivity and incoming-direction condition,
  exact per-input times, and eight named rejecting controls.

The all-width theorem has a written proof. These counts describe executed
finite domains; they do not replace that proof with a proof-kernel result.
The executable caps widths at 4,096 for a bounded replay, while the fixed
table and written proof cover every W>=2.

## Limitations

Marker preparation, layout conversion, random generation/delivery, negative
coefficient signs, repeated-call compilation, actual caller precision,
other arithmetic macros, native MOVE and the complete supplier bill remain
unproved here. There is no numerical overflow within the stated local input
range, but no reached caller width is certified. Restoring a coin tape does
not make it fresh for later adaptive calls. No selected cold replay, Lean,
Docker, complete rounded multiplier or selected-frontier update was run.
All five selected framework assumptions remain.

## Open next questions

- Construct a negative-coefficient table with the same scratch and linear-time
  boundary. Start with a completely charged local two's-complement negation
  stage. No such table or composition proof is supplied here.
- Bind one reached positive-half caller to this layout and price marker setup,
  coin delivery, conversion and cleanup. Start at a pinned physical cut;
  a compatible complete placement and guard contract are missing.

The same questions and blockers are recorded in [TASK.json](TASK.json).

## Credit and provenance

This contribution was produced by Nick Petalas. Credit zxv's PR6092 for the
contract and faster-layout question, PR6066 for logical restoration,
JoyboyBrian's PR6095 for the related marker interpreter, AAAmirinu's PR6244
for reached-coin delivery, Nick Petalas's PR6026, Ali Romman's PR5599 and
the retained stochastic/native lineage. Binary shifts, ripple arithmetic
and the local reversibility criterion are classical; the new result is
this explicit fixed table and its all-width boundary/resource proof.
[SOURCES.json](SOURCES.json) pins the exact predecessor statement and proof
as provenance at the canonical base. No predecessor credit line is changed.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441282).
