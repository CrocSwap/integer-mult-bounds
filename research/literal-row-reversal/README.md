# Complete-record reversal as one literal elementary stream program

**Result type: literal machine implementation and scoped interface lemma.
No new kappa. No global foundational assumption is discharged.**

This package supplies one 524-location, 13-tape program for the actual
elementary binary-descriptor interface on `[P]x[R]x[B]` arrays. It reverses
the R whole B-bit records separately in every prefix, preserves each
record's internal bit order, stages the complete result, and commits it to
the original DATA owner. Every source move, local reset, copy, rewind,
retirement and original-owner write is represented by a local instruction.

For `V=PRB`, `E=ell(P)+ell(R)+ell(B)`, and binary popcount s, the proved
accepting census is exactly

`T=53V+23PR+71P+54R+54B+28E-30(s(P)+s(R)+s(B))-8`.

Hence `T<=256(V+E+1)=O(V)`. The nine private roles add at most
`8V+E+18` cells to actual pre-entry historical backing; blank cells remain
charged. All private bodies and heads are retired on success, so a smaller
subsequent call pays for its current shape without rescanning older tails.

## Why this adds something

The high-level two-stack reversal is already in canonical `02-streams.tex`.
Its algorithm and the elementary O(V) scan theorem are credited prior work.
The missing item addressed here is an actual fixed local-symbol graph at
that encoded boundary, including complete same-owner installation and a
uniform history contract. Descriptor parsing and nested counts are on
tapes; no decoded Python shape, computed address, or trusted map stream
is supplied to the executable program.

The scoped native consequence is exact: for `R=2^f`, reversal is XOR by
the all-ones f-bit word on an **entire contiguous coordinate block**.
Fixed vectors on a fixed number of binary positions compose by a fixed
number of fully paid calls with correct supplied collapsed descriptors.
The retained `flip_digit` map is matched on 21 differential fixtures.
Its old host caller, strided selected-bit packing, general affine routing,
and descriptor production from growing layouts remain caller obligations.

## Entry and exit

Three distinct public descriptor tapes contain canonical positive binary
P,R,B, MSB first and blank-terminated. A fourth public tape holds V bits
and a blank terminator. The nine private owners must have blank guards
and bodies through the proved current visit caps; this is an explicit
precondition, not inferred from a bounded probe. Arbitrary translated
origins and opaque exterior contents are allowed. See [PROOF.md](PROOF.md)
for all caps, source semantics, and exact failure scope.

Successful calls preserve descriptors and all exterior cells, return every
head, clear every private guard/body, and retain the same DATA owner.
Finite descriptor/cardinality violations reject before DATA writes.
Failure cleanup and failure reuse are not promised.

## Reproduce

From this package directory, using Python 3.10 or later:

```sh
python check.py
python -O check.py
```

Both commands emit the exact structured receipt in [RESULT.json](RESULT.json).
No network or third-party Python dependency is needed. The checker
authenticates nine pinned inputs and refuses source drift. It checks all
payloads for every positive shape with `PRB<=8`, plus 64 seeded larger
packets: 3,814 accepting packets and 4,053,639 accepting transitions.
Twelve rejection fixtures preserve DATA, six executable graph mutants are
detected, and explicit alternative maps distinguish reversed bits from
reversed records and cross-prefix leakage. Reuse, retained-history, exact
source-map, and fixed-vector composition receipts are also included.

These finite checks support the graph invariant and universal cost proof;
they are not a substitute for it. Independent checks are documented in
[REVIEW.md](REVIEW.md) when complete. See [VERIFY.json](VERIFY.json) for the
portable reproduction manifest and [VALIDATION.md](VALIDATION.md) for the
executed checks. No unchanged selected-certificate cold replay is claimed.

## Source pins and scope

The tested base is `e54523517d0f03e58352e647c403a5af3e525a57`.
[SOURCES.json](SOURCES.json) gives exact repository, commit, original path,
Git blob, byte length and SHA256 for all copied sources. The only runtime
dependency is the exact finite Builder/Machine reference. The frozen
`literal-layer-phase` source at fork commit
`8b549ca6557ccbb3017b104b27ea35051f990416` provides credited helper patterns;
its phase program is not imported by the new permutation.

[OVERLAP.md](OVERLAP.md) records the bounded novelty gate and limitations of
its search. [NOTICE.md](NOTICE.md) records predecessor and AI-assistance
credit. [TASK.json](TASK.json) is the run checkpoint. This package adds
isolated files only; canonical sources and the selected certificate are
unchanged.

## Open next questions

1. **Literal caller construction of collapsed lengths.** This would turn
   the elementary component into a complete source-side call where encoded
   P,R,B are currently supplied. First select one exact retained caller and
   lower its length construction and call control with its full source and
   head-return bill. A growing layout list cannot be treated as free.
2. **Selected-bit layouts.** Current native suppliers may expose the target
   bits at stride K. Identify and price an existing exact packing interface
   or produce a literal permutation that handles those bits directly. Full
   wider-field reversal is a demonstrably incorrect shortcut.
3. **Additional source permutations.** Literal controlled shifts or the
   fixed-zero modular negation require their own prefix/control/boundary
   program, even though this package implements a useful local reversal.
   Begin with one exact source call and its complete budget, rather than
   assuming the entire ordered-affine lemma has been lowered.
4. **Failure retirement.** The present success contract deliberately permits
   dirty private work on rejection. A caller requiring retry after malformed
   input needs a separately priced cleanup protocol with a finite recovery
   control state and retained history. No such protocol is asserted here.
