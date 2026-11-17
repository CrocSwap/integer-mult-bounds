# Exact transport cost for a fixed-line permutation

For a permutation moving `s` public registers on distinct fixed lines, the
minimum number of owned MOVEs is **`2s`**. Every MOVE can have rank one in an
attaining schedule. Thus the minimum owned tariff is also `2s` whenever a
rank-one MOVE costs one and every positive-rank MOVE costs at least one,
including `r^(1-C)` for `0 <= C <= 1`.

This is a **scoped written proof with exact finite corroboration**. It permits
arbitrarily many shared owned carriers, feedback, interleaved reads and writes,
intermediate subspaces and owned erasure. The public registers stay on their
distinct lines throughout the exchange, and scalar gates only join registers
on equal frames. [PROOF.md](PROOF.md) states the complete contract and proof.
The universal result rests on that proof, not on a finite census.

## Connection to the Whitehead question

DreamingOfClouds's [PR #6939](https://github.com/CrocSwap/integer-mult-bounds/pull/6939)
asks whether shared owned runs can carry the beta crossings of its window
native more cheaply. Its existing matching exchange moves all 104 public X
registers while they remain on distinct lines. The theorem gives an exact
**208-MOVE floor for that exchange**, even with arbitrary carrier sharing and
interleaving. Its rank-one exchange attains the floor. We cite that construction
and the port count; we do not replay or claim credit for them.

This closes sharing as a way to improve that fixed-line preprocessing contract.
It does not exclude changing public frames during the exchange, mixing the
exchange with the later Y bounce, Gamma coupling, or a different native.
No kappa improvement, supplier admission, full physical native replay or
complete multiplication theorem is claimed. The tariff counts owned MOVEs
only. Scalar operations, allocation, storage and physical delivery remain
separate costs.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/fixed-line-crossing-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B research/fixed-line-crossing-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-line-crossing-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-line-crossing-floor --check-source-history
```

The marker is `PASS_FIXED_LINE_CROSSING_FLOOR`. The checker enumerates every
permutation through six registers over Q and three prime fields, checks a
104-register exchange, enumerates all nested MOVE edges in the binary subspace
lattices through dimension four, and exercises rejected circuits and a changed
public-frame control. Its stdout receipt binds the package bytes by SHA256.
It writes no generated files. Exact counts appear in the generated output.
An export can run the direct verifier without Git or predecessor executables.
The changed-frame control permits public ascent and descent; it is a boundary
test, not a proposed legal native.

[SOURCES.json](SOURCES.json) pins the predecessor text, catalogue and selected
record as historical provenance. There are no external runtime inputs or
dependencies. The selected metadata orientation passed; the selected cold
replay, predecessor scientific suites, Lean and Docker were not run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can a public-frame change or an exchange interleaved with the Y bounce
  reduce the complete Whitehead bill? This escapes a specific hypothesis of
  the floor. Start with one literal shared-carrier schedule and record its
  complete endpoint, frame changes and both public and owned charges. A legal
  schedule with restored outputs and a favorable complete bill is missing.
- What is the smallest peak owned storage among schedules attaining `2s`
  MOVEs? The construction here uses one carrier per moved source. Start with
  a single permutation cycle and permit interleaving; a matching storage
  lower bound is not supplied here.

## Credit

The new fixed-line theorem, general attaining schedule and checker were
produced by Nick Petalas. DreamingOfClouds supplies the Whitehead window
construction, matching exchange and shared-landing question in #6939.
Retain its credit to Ali Romman #5599, CubeJerry #6912/#6914/#6916,
unpaidmoon #6930, icekylinx #104 and their native/caller predecessors.
New work is Apache-2.0; predecessor files remain unchanged.

## Checker bounds

The finite checker caps inputs at 104 ports and 832 events, with at most 211
symbolic rows of 107 integer coefficients. It enumerates at most 720
permutations at a given size and four payload fields. The lattice check uses
at most 67 subspaces with 16 elements each. Every loop has an explicit finite
corpus or enforced input bound; no recursion, subprocess or network call is
used. Each function is under 60 lines. Explicit checks remain enabled under
optimized Python.

Python's managed runtime allocates rows, sets and integers during replay,
which is a deviation from fixed allocation under Power of Ten rule 3. The
stated finite capacities bound live collections; fixture coefficients have
absolute value at most 104. This is a bounded offline verifier, not a real-time
implementation. Revisit allocation and coefficient bounds before expanding
its input domain. Warnings are errors in both registered commands.
