# Exact full-mask rank for separated-port excess payloads

The complete fixed PR2484 112-port mask has minimum fitting rank

    49d + sum_(p in T) e_p

when every port has width d>=1 and only the 44 ports T of the retained
separated 22-plane set Q receive arbitrary excess widths e_p>=0.
The theorem holds over every field, with arbitrary rectangular ordered free
blocks, and the bound is attained on the full mask. This is a scoped proof
with finite corroboration. No new kappa or supplier admission is claimed.

This answers a restricted family of Tekalign's [PR3362](https://github.com/CrocSwap/integer-mult-bounds/pull/3362)
Open next question 1, which asks for full unequal-width 112-port attainment.
The credited uniform 49d theorem and Q/C5 lower bound are dependencies.
The new result is the full-mask lift for all 44 independently increased
separated widths. The first example has d=1, width two at port 0, all other
widths one, and exact minimum rank 50 in a 113-by-113 matrix.

[PROOF.md](PROOF.md) gives the lower bound and explicit support-wise encoder
and decoder. It also separates the result from the general unequal-width
problem. [SOURCES.json](SOURCES.json) pins the predecessor proofs, partition,
matching and label archive at canonical base
`624de9dc66858af0945e5f8a0942488d62280d43`. No predecessor executable is imported
or run. The card's scope is explicitly changed to this algebraic side result;
this does not supply a new paid profile or satisfy the physical mechanism gate.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/full-mask-separated-excess
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/full-mask-separated-excess/verify.py
```

Expected direct output:

```text
PASS_FULL_MASK_SEPARATED_EXCESS matrices=50 field_ranks=150 controls=10
```

The registered hook runs normal and optimized isolated checks. The direct
verifier works without Git when the declared input files retain their paths.
`--emit` prints a newly generated receipt; acceptance compares the complete
canonical JSON to [RESULT.json](RESULT.json). The receipt binds package and
proof file hashes and the source manifest. It is generated, not hand-written.

The 50 full-mask matrices are all new nonuniform payloads: one single-unit
increase at each of the 44 Q ports, then three larger patterns both with and
without independent invertible port charts. Each is checked against every
forced identity and ordered zero block and ranked by literal elimination over
F2, F3 and F101. The patterns include d=2 and simultaneously unequal excesses.
A 201-bit base-width recipe is checked without expanding its matrix. These
finite instances corroborate the universal written proof; they do not enumerate
all fitting matrices or prove the universal lower bound by search.

Ten controls cover invalid base widths, malformed/negative/Boolean excesses,
a one-direction forbidden leak, a changed diagonal identity, an omitted
extra-coordinate charge, and refusal to expand beyond 512 coordinates.
The archive and source files are authenticated before use. All acceptance
checks remain enabled under optimized Python.

## Limits and implementation checks

This is an exact linear query-capacity theorem. It does not price native
copies, access, frames, dirty restoration, precision, hosting or a complete
consumer. No complete multiplication theorem, selected-frontier change,
independent human review or formal proof-kernel acceptance is claimed.

The verifier uses managed Python allocation, a documented Power of Ten
memory-rule deviation. Expanded matrices are capped at 512 coordinates;
there are 50 fixed fixtures and three fixed finite fields. Compressed input
integers have at most 4096 bits, and compressed arrays have fixed sizes
112 and 49. Pinned files are capped at 16 MiB and the extracted JSON member
is capped at 16 MiB. Tar/JSON/Python runtime allocation is not statically
controlled. Functions stay below 60 lines and there is no recursion. The
small callback set in rejection controls is a documented indirect-call
exception, restricted to the ten immediate controls. The source hash bounds
the exact runtime input. `-W error` is part of both registered commands; no
additional project Python linter configuration was found. The finite expansion
cap is exercised by a rejection control. A future larger replay must revise
these bounds before expansion. No asynchronous or persistent work is started.

## Open next questions

- Can excess widths on the ten C5 ports, or on the other 58 ports, also
  attain Tekalign's principal lower bound on the full mask? First increase
  one such width, compare the support capacity with that bound, and give
  a full fitting factorization or a stronger obstruction. The present
  theorem leaves those changes open.
- Can one of these unequal query layers improve a fully paid native
  implementation? First choose source/target charts and price every read,
  copy, frame change and restoration. Those costs remain unknown here.

## Credit

This contribution is produced by Nick Petalas. Credit Sagar Thakrar/PR2484
for the scalar partition and Q/C5 witness; ywz65/PR2541 and PR2471 for the
all-field uniform block theorem and earlier mask work; Tekalign/PR3362
for the unequal principal theorem and full-mask question; Cinna Davis/PR1825,
Adam Gall/PR1889, ctoth, Philippe Van Velzen and the retained E8/P112 lineage.
No predecessor credit is changed. Elementary support embeddings and linear
rank inequalities are classical methods; no literature-priority claim is made.
New material is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
