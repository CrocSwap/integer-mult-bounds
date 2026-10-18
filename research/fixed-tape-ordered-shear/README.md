# Fixed-tape ordered shear at every extent

**Scoped construction: a literal all-size routing kernel with a complete linear
physical bill. No new multiplication exponent or complete recursive caller.**

For every positive binary-encoded `P,Q,G,S`, and every Boolean payload of volume
`V=P Q² G S`, the supplied controller moves

```
(p,x,g,y,z) -> (p,x,g,(y+x) mod Q,z).
```

A second controller implements the inverse. Each uses exactly **14 tapes,
7 alphabet symbols and 531 finite microinstructions**, independent of all four
runtime extents. Every instruction is a local symbol branch/write, a unit head
move, a fixed jump, halt or rejection. The complete cost is **at most 442V
transitions and 41V visited tape cells**, including binary descriptor conversion,
payload movement, head returns and erasure of every scratch cell and marker.
Both bounds include the constant setup and are attained at `P=Q=G=S=1`.
The source and binary descriptors are preserved; the output is separately owned.

[PROOF.md](PROOF.md) proves the loop invariant and exact transition/span
identities for arbitrary extents and arbitrary payloads. [TABLE.json](TABLE.json)
is the complete finite program bank, not a trace specialized to test sizes.
The all-size result is a handwritten algorithmic proof with executable evidence;
it is not a proof-assistant certificate.

## Why this addresses the routing bottleneck

The current-main [`add_high`](../selected-bit-stream-routes/qadic_streams.py)
already describes the relevant ordered split/merge permutation, but its payload
meter omits host arithmetic, scratch erasure and some head returns. This package
physically realizes its `c=±1`, zero-carry, forward-field specialization for every
extent, including unbounded prefix, gap and suffix dimensions. It replaces that
specialization's host-controlled loops with finite control and pays every step.
The independent checker authenticates that predecessor before executing it,
compares endpoints, and confirms that the ordinary-swap oracle is not reached.

The useful advance is a composable physical kernel with an explicit interface
and uniform bill. It does **not** discharge the entire selected route: rational
scaling, nonzero or data-dependent carries, reversed-field interchange, recursive
role allocation, leaf/bootstrap substitution and H2 acceleration remain open.
It changes neither the selected result nor κ. The scientific base is current
main at session start, `8e22a9d9f621c72ab5b299061c2be4c7f638fd3c`.

## Implementation and evidence

| File | Review purpose |
|---|---|
| [machine.py](machine.py) | Finite local instruction language and sparse physical interpreter |
| [counters.py](counters.py) | Binary-to-unary conversion with amortized linear cost |
| [shear.py](shear.py) | Extent-independent assembly, split/merge and complete cleanup |
| [verify.py](verify.py), [RESULT.json](RESULT.json) | Exact table regeneration, static input immutability and 98 sparse physical cases |
| [independent_check.py](independent_check.py), [INDEPENDENT-RESULT.json](INDEPENDENT-RESULT.json) | Separate dense interpreter, coordinate oracle, source binding and physical mutation controls |
| [test_counters.py](test_counters.py), [test_independent.py](test_independent.py) | Binary shrink boundaries, malformed interfaces and authentication failures |

The independent replay covers 164 directional cases, 15 inverse round trips,
30 cases with independently translated tape origins and 34 authenticated
predecessor comparisons. It exhausts every four-bit payload at `Q=2`, uses
one-hot bases in several spectator layouts, and checks every final cell/head,
source preservation and both exact resource formulas. Its six mutation controls
catch payload corruption, omitted scratch erasure, omitted source rewind,
reversed orientation, nonlocal head motion and altered predecessor bytes.
These finite tests corroborate the implementation; the universal claim comes
from the proof, not extrapolation from the fixtures.

## Reproduce

Python **3.12**, standard library only. From the repository root:

```sh
python3.12 scripts/research_package.py --package research/fixed-tape-ordered-shear --check-only
python3.12 scripts/research_package.py --package research/fixed-tape-ordered-shear
```

Every registered command is read-only and checks the saved receipts. Explicit
regeneration, only when intentionally changing the implementation, is sequential:

```sh
python3.12 -I -B research/fixed-tape-ordered-shear/verify.py --write
python3.12 -I -B research/fixed-tape-ordered-shear/independent_check.py --write
```

[SOURCES.json](SOURCES.json) pins the source commit, Git blobs and SHA256 hashes.
The live predecessor input is checked from its actual bytes before execution,
including under `-O`. Its imports do not use cached bytecode. Other source rows
are historical provenance. [VALIDATION.md](VALIDATION.md) records environment,
commands, export checks and limits. [TASK.json](TASK.json) records the assigned
question, scope refinement, overlap coverage and stopping rule.

## Overlap and predecessor boundary

The start-here, handoff and mechanism discussion threads, all open PRs and the
paginated active Discussion records were checked before substantial research.
The local task metadata records coverage and freshness. No public coordination
post was made because the user-supplied instructions require separate authority.

- [PR #2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753)
  supplies the logical all-size caller. Its fixed physical bank and complete
  dispatch are still open; this package supplies one physical route kernel.
- [PR #2760](https://github.com/CrocSwap/integer-mult-bounds/pull/2760)
  maps the logical caller/storage obligations; this construction addresses a
  primitive inside that boundary, not the whole map.
- [PR #2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635)
  supplies literal matched-packet parking; the newly published
  [PR #2769](https://github.com/CrocSwap/integer-mult-bounds/pull/2769)
  connects numerical slots to that parking machine. The active
  [physical-caller lowering claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18958887)
  covers Frame/BankParking integration and suspended roles. This package
  implements payload permutation; it does not duplicate that codec or allocator.
- [PR #2636](https://github.com/CrocSwap/integer-mult-bounds/pull/2636)
  supplies a fixed-tape padding scan; it does not implement this cyclic shear.
- [PR #2235](https://github.com/CrocSwap/integer-mult-bounds/pull/2235)
  supplies broader multitape formalization infrastructure. This package neither
  imports it nor claims Lean verification.
- [PR #2592](https://github.com/CrocSwap/integer-mult-bounds/pull/2592)
  prices signed SWAP words in an abstract tariff; it does not compile this
  ordered physical stream operation.

[PR #2411](https://github.com/CrocSwap/integer-mult-bounds/pull/2411) links a
separate external Lean multiplication proof. This package does not audit that
proof or claim a first fixed-machine multiplication result; its boundary is
the selected stream specialization above.

The underlying ordered-affine split/merge method is already in the upstream
stream lemma and selected stream package. The novelty here is the complete,
size-independent finite controller, its all-size physical cost proof and
independently interpreted export. This is not a new algebraic method.

## Open next questions

1. Extend the physical compiler to one named carry or rational-scaling kernel.
   That is needed to cover the remaining `add_high`/`scale_high` cases. Start
   with a fixed carry and preserve the same ownership/cleanup contract; each
   extension needs its own finite-control and uniform-volume proof.
2. Follow the active physical-caller lowering claim and bind this kernel to its
   named route role once the role/alias contract is available. That connection
   is needed for whole-caller compilation; it should build on the ongoing work.
   A route kernel and parked payloads alone do not resolve the H2 recurrence.

The structured forms, including blockers, are in [TASK.json](TASK.json).

## Credit

Prepared for David Arias with substantial OpenAI Codex assistance, including
independent implementation and checking agents. The upstream ordered-affine
stream lemma and Jose Manuel's selected stream reduction supply the method and
interface; their attribution and frozen files are retained. New work is
Apache-2.0. No frozen archive, selected frontier or predecessor was changed.
