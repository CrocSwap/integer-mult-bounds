# A shared hub between two pentagons needs nine query coordinates

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written mathematical proof, with exact finite conformance.
For the graph with cycles `0-1-2-3-4-0` and `0-5-6-7-8-0`, give every vertex
exactly two field coordinates. Over every field, the exact minimum fitting
rank is **nine**. Diagonal blocks are `I_2`; both ordered blocks at every
nonedge are zero; all allowed edge blocks are arbitrary 2-by-2 matrices.
They may be asymmetric, singular and noncommuting.

The independent-set bound gives eight. [PROOF.md](PROOF.md) excludes rank
eight by saturating that bound: terminal subspaces on both arms force the
hub decoder to annihilate the entire query space. Nine disjoint coordinate
pairs attain the bound. Thus this shared-hub mask gives no improvement over
optimal integral edge pairing, even with general directed block coding.
This is the original changed-mask result delivered here, not a claim of a
first result about overlapping cycles in general or of literature priority.

The card `complex-rank-shape-decoder` changes scope from complete supplier
construction to this algebraic decoder side result. It tests one proposed
route around single-cycle pairing obstructions. No source-bound physical
caller, complete signed invoice, new kappa or multiplication theorem follows.
The selected #7000 record and all frozen evidence remain unchanged.

## Exact evidence

The standalone verifier imports no project code and runs no predecessor
executable. It checks:

- 376 complete rank-nine factorizations over F2, F3, F5, F7, F101 and Q,
  including asymmetric and noncommuting edge-block fixtures. Every one of
  their 121,824 ordered entries satisfies the full diagonal/zero contract.
- All 262,144 binary input assignments to the nine-pair encoder and literal
  side-information decoder, giving 4,718,592 coordinate recoveries.
- All 187,200 local normalized branch instances over F2 and F3 used by the
  saturation proof. These enumerate invertible terminal/projection blocks
  and arbitrary intermediate blocks. They are not all fitting matrices.
- Nine query omissions and three illegal diagonal/zero-mask edits reject.
  A positive boundary control attains rank eight after adding only edge
  `0-2`; the original zero-mask validator rejects that code.

The universal exclusion rests on the written proof. These finite checks
corroborate the construction and local algebra, without pretending to
exhaust the unrestricted 18-by-18 fitting-matrix space. The generated JSON
on stdout binds the results to SHA256 of all six package files. No receipt
is hand-written or retained as frozen evidence, and normal execution writes
nothing into the checkout.

## Reproduction

From the repository root, use standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/shared-hub-pentagon-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/shared-hub-pentagon-query/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-hub-pentagon-query
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-hub-pentagon-query --check-source-history
```

Another CPython 3.12 executable may replace that path. Direct verification
prints `PASS_SHARED_HUB_PENTAGON_QUERY` in its JSON result, with minimum
query dimension nine. Both normal and optimized modes use explicit
exceptions. The registered runner executes both, each with a 120-second
limit. Hosted CI status belongs in the contribution PR body.

## Credit and overlap

JoyboyBrian's [#5023](https://github.com/CrocSwap/integer-mult-bounds/pull/5023)
supplies the unequal-payload odd-cycle query interface, with credit to
Tekalign #3362, Sagar Thakrar #2484, ywz65 #2471, Nick Petalas #4909,
Cinna Davis, Adam Gall, ctoth, Philippe Van Velzen and the retained
P112/native lineage. Its single-cycle theorem is credited background.
The proof here does not invoke its numerical results or construction.

Yossi Berliner and Michael Langberg's classical
[*Index coding with outerplanar side information*, Theorem 1.1](https://www.openu.ac.il/home/mikel/papers/outer.pdf)
settles the scalar outerplanar minimum through clique covers. Section 7
leaves vector-linear coding outside that paper's result. The contribution
here concerns two-coordinate blocks and a direct saturation proof.
Classical fitting-matrix rank factorization and coordinate-pair coding
retain their credit. No global first-discovery claim is made.

Nick Petalas's older `clebsch-puncture-query-gap` package studies a different
mask and a specified classical binary matrix. It is related background,
not the source of this question or a construction used in the main step.
No predecessor package is audited or scientifically replayed.

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the catalogue, selected record and odd-cycle
exposition as historical provenance. There are no live external inputs.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595344)
records the same scope. Live open/recent-account PRs, Discussion claims,
local reservations, full-main distinctive README searches and merged-title
searches were checked. The cached scan covers remote pagination but omits
most sparse local notes; the full-main Git searches supplement that omission.
Arbitrary historical diffs and unpublished work remain outside coverage.

## Limitations and implementation constraints

This theorem is a linear dimension contract for this one graph and payload
width. Nonlinear coding, larger payloads and other topologies are unproved.
No physical source reads, query implementation, side-information acquisition,
owned or borrowed state, dirty restoration, frame conversions, coefficient
preparation, hosting, precision, tapes, stock, uniform compiler, complete
recursive invoice or supplier admission is provided. These unknown costs
are not treated as zero. There is no dependent implementation expansion.
No selected cold replay, Lean, Docker or formal proof-kernel build was run.

The verifier has no recursion, subprocesses, network or output-file path.
Every matrix is at most 18-by-18, all finite domains are literal constants,
and all functions are below sixty physical lines. Inputs are streamed,
including the 262,144 assignments; no table of those assignments is retained.
Explicit exceptions enforce contracts under optimization. Warning-strict
normal/optimized execution and syntax inspection supply local diagnostics.
No separate external static analyzer is claimed.

Power of Ten rule 3 has a bounded managed-runtime deviation. Python allocates
integer, Fraction and small collection objects during checking. The largest
matrix has 324 entries, GL2 lists contain at most 48 matrices, and one
branch/input/profile is processed at a time. There is no fixed-storage or
steady-service claim. Build the Lever led to the executable factorization
and repeatable checker; Prove It Works led to every-input literal decoding
and the original-mask rejection of the rank-eight boundary control.

## Open next questions

1. What is the exact minimum on this graph with three coordinates per vertex?
   The same saturation argument excludes the independent-set bound twelve,
   while the cycle-plus-path pairing recipe gives fourteen. Seek a rank-thirteen
   factorization or exclude it. That case is not decided here.
2. Can an actual recursive caller expose this mask and benefit after complete
   physical charges? Pin the producer, consumer and chronological read
   permissions; then price source access, nine queries, side information,
   restoration, frames and delivery. No such caller or native invoice is
   supplied. A dimension optimum alone cannot establish profitability.
