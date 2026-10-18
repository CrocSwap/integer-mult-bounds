# Original P112 cover contracts recover three caller exclusions

Under the exact inherited contracts, this package accounts for three rows
omitted from PR3282's six-contract inventory. Conditional coverage of the
historical TWOSIDE(6,4) cell increases from 62/69 to 65/69. These are
applications of prior theorems, not new geometric exclusions or a current
public unresolved count.

The three rows are `2^2,3,6,7^6`, `2^2,4,5,7^6` and `2,3^2,5,7^6`.
Each has a four-piece quotient basis fitting two six-flats and one common
cut of at most two lines. Original FINITE beta R=7,p=2 bounds the six
required independent directions by four. [PROOF.md](PROOF.md) proves the
quotient and characteristic-zero transfer implications and lists all
inherited assumptions. RESULT.json retains all 69 rows, four new rule
attempts per row, exact indexed counts and literal witnesses.

The four rows uncertified by this expanded fixed inventory are
`2^3,7^7`, `2,3,4^2,7^6`, `2,5,6^8` and `4,5^3,6^6`. The second fits an
unproved four-line rank-seven beta relaxation. A control prevents that
relaxation from being admitted as the available two-line theorem. These
failed cap-role tests do not establish actual-union or coefficient
nonexistence.

Reproduce with Python 3.12 from the repository root:

```sh
python3 -W error -B scripts/research_package.py \
  --package research/p112-b6-t4-original-covers
```

The registered replay runs the historical filter, exact source and receipt
checks, an independently written bitmask application scan and behavioral
controls. Direct Git-free replay runs `verify.py`, `independent.py` and
`test_verify.py` in this directory. Set TMPDIR to a disposable external
directory for the controls. They copy only this small package and reject
source/schema/usage changes, unexpected inputs and a changed live receipt.
Normal and optimized Python execution use explicit checks.

Seven precise predecessor payloads are retained verbatim. SOURCES.json and
a fixed verifier inventory bind their original paths, usage, Git blobs,
SHA256 hashes and exact heads. The primary verifier authenticates every
live payload even when Git is absent. No pending-PR Git object or network
access is needed for the mathematical replay.

This is a scoped conditional composition certificate. The inherited root
code distance, capacities, geometric classifications, FINITE census
conclusions and prior six-contract coverage were not recertified. The
recorded full_b log preserves its earlier failed joins and final corrected
agreement. No heavy replay, Lean, Docker, selected cold replay, human or
proof-kernel approval, full C5, decoder floor, supplier or new kappa is
claimed. Physical costs and consumer/restoration obligations are separate.

## Open next questions

- For `2,3,4^2,7^6`, can actual quotient-basis geometry supply a specialized
  common-four-line result? Start from the exact displayed roles and check
  live successor work. The general rank-seven p=4 contract is unproved
  by the sources used here.
- For the other three rows, reconcile current public handoffs before a
  new census. Failed support-cap sums alone do not rule out useful actual
  overlaps or different contracts. This package supplies no realization.

## Credit and evidence status

DreamingOfClouds/PR3154 supplies the original TWOSIDE and FINITE contracts,
proof map and recorded rerun evidence at
`708f0ad8928c383de8294aea3c126e9461d2066d`. Nick Petalas/PR3161 supplies the
rank-six cover proof at `a1aba8389b87412e6f72ccf4d11f31e0ea232327`.
PR3282 at `9607079de93907d87e6430d6de154f21a66c03e4` supplies the original
69-row inventory and six-contract composition. All earlier exclusions
retain their credit, including its PR3262/3205/3260/3186/3192/3253 and
E8/P112, root-simplex, SMALL2/Pencil and joaqcoo lineage.

Canonical base is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision 6. This closes the omitted-contract audit requested in PR3282;
it is not a construction expansion. Concurrent analytic rank-six A2 and
D6 capacity proofs and mixed-rank cut40 work are separate and unused.
Nick Petalas; substantial automated assistance in analysis and local
checking. Apache-2.0. Internal computational review does not establish
independent human review or selected-frontier admission.
