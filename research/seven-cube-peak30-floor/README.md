# Affine seven-cube peak-30 decoding costs at least 200

Every finite affine binary factorization of the cubic seven-cube decoder
with each term's copied rank at most 30 has total copied rank at least **200**.
This raises the lower endpoint of Hanson Sun's
[PR1564](https://github.com/CrocSwap/integer-mult-bounds/pull/1564) tradeoff
from 140 to 200. Its cited cost-240 upper construction leaves the interval
**[200,240]**. Attainment of 200 and the exact optimum are unclaimed.

This is a scoped written mathematical proof with exact finite corroboration.
The new [factor-span argument](PROOF.md) uses the complete coefficient
identity. Each factor has at most two linear variables under the predecessor's
low-rank classification. Both factor matrices therefore have rank at least
five. Their rank-two product needs at least eight terms. At least four terms
cost 30 by diagonal coverage, so the total is at least 20*8+10*4=200.

The predecessor's classification and upper witness are cited premises, not
audit deliverables. No predecessor scientific code, census or witness is
executed. [SOURCES.json](SOURCES.json) pins its README and certificate as
historical provenance at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

This is an algebraic side result for the changed
`complex-rank-shape-decoder` card. The inherited additive stage budget already
fails; this result does not make that family a promising supplier. No native
word, complete paid/productive invoice, new kappa or selected-frontier change
is supplied. The selected record at the base remains PR6030. The exact scope
and source question are in [TASK.json](TASK.json).

## Reproduce

From the worktree root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/seven-cube-peak30-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/seven-cube-peak30-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/seven-cube-peak30-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/seven-cube-peak30-floor --check-source-history
```

Another CPython 3.12 path can replace the local one. The direct checker is
read-only and Git-free. It prints a generated JSON receipt binding all six
package source hashes, then `PASS_SEVEN_CUBE_PEAK30_FLOOR total_floor=200`.
Normal and optimized commands are registered separately in [VERIFY.json](VERIFY.json).

The new corroboration checks 5,546 generated subspaces through seven variables,
including all 541 containing the parity vector. An independent complete
XOR-state BFS checks five small coefficient problems, including pure constants,
with 132,112 states in total. Their minima are 2,4,2,6,4 for
(n,d)=(1,1),(2,1),(2,2),(3,1),(3,2), respectively. Direct point evaluations check 17,472 product entries.
There are 4,752 independent affine-pair diagonal cases, 112 complementary-pair
cases, three complete positive words, ten rejected contracts and boundary
fixtures for the support cap and independent constant. These are new small
lemma checks, not a replay of the seven-cube rank census.

The universal quantifiers rest on the written proof. No independent human or
formal proof-kernel review, Lean, Docker or selected cold replay is claimed.
Physical routing, source access, arbitrary dirty restoration, hosting,
precision, stock, tapes, compiler and outer admission remain separate obligations.

## Verification implementation

The checker has no recursion, subprocesses, imports from predecessor packages
or network calls. Dimensions are capped at seven, subspace traversals at
5,000 spaces, words at sixteen terms, and each small BFS at 65,536 states.
Every function fits within 60 physical lines. Explicit exceptions keep all
scientific checks active under optimized Python. The two interpreter modes
use warning-strict diagnostics. AST inspection finds a maximum function length
of 29 physical lines and no assertion-dependent checks. Ruff is unavailable
in the reproduction environment.

The managed-runtime allocation deviation is bounded as follows.

```text
Rule: 3, fixed allocation before steady operation.
Location: verify.py, all finite checks and source hashing.
Reason: CPython allocates integers, collections and iterator temporaries.
Scope: this standalone checker only.
Compensating control: at most 5,000 subspaces with 128 vectors each;
  at most 65,536 states per BFS; six source files capped at 256 KiB each.
Verification: explicit capacities, warning-strict normal/optimized replay,
  and inspection of every loop and allocation path.
Follow-up: use fixed-capacity lower-level storage if hard allocation
  guarantees become a requirement.
```

No repository-wide analysis or compiler-warning configuration change is claimed.

## Open next questions

1. What is the exact peak-30 total optimum in [200,240]? First test the
   full coefficient equations for the relaxed eight-term, four-rank30 count.
   The obstruction is simultaneous attainment of the span and coverage bounds.
2. Can a complete two-stage retention interface change the inherited additive
   charge? Start with the predecessor's four-term decoder and price retained
   state, delivery and restoration. That legal physical interface is missing;
   a smaller tradeoff interval alone cannot remove the supplier obstruction.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0. Hanson Sun / bbMisk
supplies PR1564's seven-cube model, exact low-rank classification, prior bounds
and upper constructions. Credit Joel Pulikkan / GamingPuzzled for the star
identity, Ross Richardson for the cube/budget approach, martinxxx9 for the
affine factor-span reduction, and icekylinx/eumemic, DreamingOfClouds, Jacob
Sussman and Zhihao Chen for the retained decoder/frame lineage. The new step
is the sparse-support dimension bound and its cost-200 consequence. Classical
rank inequalities and affine counting retain their usual attribution.
