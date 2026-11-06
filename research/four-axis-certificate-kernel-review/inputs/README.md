# Sharp four-axis reversible Gaussian grid rounding

This contribution was produced by Nick Petalas. Apache-2.0.

A new sixteen-point integer-grid map has an explicit inverse, fixes zero and
preserves the exact complex sum. Its uniform Euclidean error is `sqrt(8) h`
for both the forward and adjoint ideal four-axis native Gaussian operators.
A half-grid witness proves that no integer-output rule can do better on this
block. Claim type: scoped written proof with a finite construction certificate.

This answers the four-axis part of Ali Romman's
[PR6536 open question](https://github.com/CrocSwap/integer-mult-bounds/blob/83fee59d692b0764d716e8356a7d991e4d503868/research/three-axis-coset-rounding/README.md).
The new step is a sum-preserving matching on 64 real Walsh quotient classes,
reused for the real and imaginary parts. Keys and both correction directions
pack into 3,072 bytes. The table is constructed deterministically and certified
on every replay.

For independent sixteen-point blocks in an N-entry tensor, the new group has
error at most `h sqrt(N/2)`. At four axes this halves the triangle-inequality
certificate of separately rounded groups of sizes three and one. This is an
error-bound improvement; the dense reference kernel has no claimed physical
cost advantage. No new kappa or selected-frontier change is supplied.

## Proof and evidence

[PROOF.md](PROOF.md) proves the all-input inverse, exact sum and sharp error
from the finite certificate. [construction.py](construction.py) builds the
matching; [kernel.py](kernel.py) executes the actual integer map.
[verify.py](verify.py) checks its predicates independently and emits a generated
receipt bound to every package file and the packed table hash.

The replay checks 64 correction rows in both directions, all 4,096 real-class
pairs, another 68 signed/large-word/sharp fixtures and ten rejection controls.
Every one of the 4,164 fixtures runs both directions against a direct native
matrix oracle, including literal inversion and sum preservation. Maximum squared
error times sixteen is 128, exactly the sharp bound. Missing/altered offsets,
invalid component formats and the implementation's input-size limit are checked.

From the repository root, CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/four-axis-reversible-grid/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/four-axis-reversible-grid/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-axis-reversible-grid
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-axis-reversible-grid --check-source-history
```

The absolute interpreter path is the publication environment; another CPython
3.12 executable works. Commands write only stdout. The package needs neither
pending Git objects nor network access. The code caps inputs at 4,096 bits per
component; the written algebraic proof covers all integers. Use 4,090-bit input
components to leave round-trip headroom within that executable cap.

## Credit and boundaries

Credit Ali Romman for PR6536's larger-block question and three-axis construction,
PR6534's two-axis construction and PR5821's Gaussian Smith execution. Credit
David Ganz / Dugongue for PR5815's Gaussian Smith construction.
Credit Brian / JoyboyBrian's PR5485 for the retained native rounded-call and
port context, PR4743's channel lineage, and the retained Gaussian native work
of David Ganz / Dugongue. Walsh transforms, finite quotient enumeration and
bipartite matching are classical. No predecessor result is replayed or audited.
The new result is the four-axis correction matching and its application.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. Scope changes the uniform-transfer card from an actual-caller
assumption audit to a constructive local precision result. It discharges none
of the five selected assumptions. Independent human and formal proof-kernel
review are unclaimed. Phase covariance, exact fourth power, pointwise nearest
output, full-call optimality, Boolean/tape lowering, supplier admission and a
complete rounded multiplier remain unproved. [ENGINEERING.md](ENGINEERING.md)
records implementation bounds and managed-runtime deviations.

## Open next questions

1. Install the four-axis map in one literal native caller. First bind its
   input/output charts, adjoint schedule, arbitrary dirty banks and full error
   budget. Current local optimality does not prove caller admission.
2. Give a complete physical bill for the factored lookup. First lower the two
   real transforms, residue classification and shared table to a reversible
   Boolean/tape program with restored workspace. Table bytes do not price access.
3. Determine whether the same optimal error permits an exact fourth-power or
   phase-covariance contract. First add those identities as finite quotient
   constraints. The present matching certifies its explicit inverse only.
