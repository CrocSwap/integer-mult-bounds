# Sharp active-row extrema for mixed-width CRT schedules

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written combinatorial proof with exact finite corroboration.
For `d=2^h` axes, `ell>=2` and exactly k widths equal to ell, the remaining
widths being ell-1, the balanced schedule of
[CubeJerry #7152](https://github.com/CrocSwap/integer-mult-bounds/pull/7152)
has sharp active-row extrema

```
A_min = (2ell-3)(d-1) + 2 max(0,k-1),
A_max = (2ell-3)(d-1) + 2 sum_{j=1}^h min(k,2^(h-j)).
```

The prefix placement minimizes the count. Complemented bit reversal of
the first k leaf indices maximizes it at every level simultaneously.
[PROOF.md](PROOF.md) derives the exact count, proves both bounds, and
gives the equality criterion at the minimum. At d=16, ell=3 and k=4,
the extremal active counts are 51 and 67. These are provider invocation
counts, not measured physical execution costs.

The new result isolates the effect of width order in the caller's bill.
It does not assign equal cost to the actual calls. A legal physical axis
permutation and a complete nonuniform numerical/ROM cost comparison remain
necessary before claiming a speed or exponent gain. No new kappa,
supplier admission, selected-frontier change or complete multiplier is claimed.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/crt-active-row-extrema/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/crt-active-row-extrema/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/crt-active-row-extrema
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/crt-active-row-extrema --check-source-history
```

Any CPython 3.12 installation may replace the local interpreter path.
The direct marker is `PASS_CRT_ACTIVE_ROW_EXTREMA`. Each invocation prints
its computed counts and a generated receipt binding all six package files
by SHA256. No result receipt is handwritten or stored in the checkout.

The verifier compares every placement at d=2,4,8,16 against a separate
literal node-row scheduler at ell=2,3,5. A bottom-up occupied-tree engine
checks the counting identity, and the exhaustive minima/maxima check the
bounds. Further constructor cases cover every k through 1,024 axes,
including every level, the closed form and empty/full boundaries.
Explicit exceptions remain active under optimization. The universal
quantifier rests on the written proof; independent human and formal
proof-kernel review are unclaimed.

## Source and scope

Base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
selected #7000 at kappa 0.00363005817. The contextual task picker reported
the older catalogue context; the selected metadata orientation passed.
TASK.json changes `joint-query-controller` to this local scheduling question.
[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541786).

The cited interface is `commands` and `WholeTree.step` in
[the exact #7152 source](https://github.com/CubeJerry/integer-mult-bounds/blob/66adbede4bd4ab603ba3e0a7f6708403905b753c/research/crt-whole-tree-state/tree.py).
Only its published activity rule is a premise. No predecessor executable
or numerical output is imported, and no predecessor verification suite is
replayed. SOURCES.json pins repository provenance; TASK.json records the
external source head and its observed source-file SHA256. This external
citation is not represented as a reachable Git source pin or live replay input.

Credit Jerry Chen / CubeJerry for #7152 and its mixed-width interface;
Ali Romman #5353/#5625, JoyboyBrian #5053/#5219/#5092/#5496/#6100,
ToikY #4195, Cinna Davis #4100, commdata2338 #5519 and their retained
CRT, numerical, row-entry and workspace lineage. Their original credit
lines and artifacts are unchanged. Binary-tree counting and bit reversal
are elementary methods; no general combinatorial-method priority is claimed.

## Open next questions

- Can a physical caller choose a minimizing width placement at a favorable
  complete cost? Start with one legal axis/modulus permutation, charge its
  preparation and inverse, and compare the complete row costs. Physical
  transport and caller compatibility are missing here.
- Which placement minimizes the complete nonuniform numerical/ROM bill?
  Start with the actual node precision and `row_bound` rather than a unit
  price per active row. Legal axis order and the full objective must first
  be specified. TASK.json records these questions and blockers.

## Verification design

The verifier has no recursion, subprocess, network access, imports of
scientific packages, source rewriting or receipt files. Every function is
under 60 physical lines. Input domains are checked explicitly: arithmetic
helpers admit at most 65,536 axes and ell at most 65,536; the literal scheduler
admits at most 1,000 nominal commands. Exhaustive loops use the four fixed
sizes through sixteen axes, constructors use heights one through ten, and
file hashing reads the six named package files. The finite input bounds are
verification limits, not restrictions on the theorem.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and lists
dynamically. The finite verifier retains at most one literal schedule of
1,000 triples, one tree of at most 1,024 leaves in constructor checks, and
one exhaustive Boolean placement of at most sixteen leaves. Files are
read by a process with no writes; their actual lengths bound hash memory.
These bounds and normal/optimized checks are the compensating controls.
A literal fixed-storage implementation would need preallocated arrays;
that physical implementation is outside this combinatorial package.
Warning-strict execution and in-memory AST compilation are the local
diagnostics. No separate static type analyzer or full numerical CRT replay
is claimed. All five selected framework assumptions remain.
