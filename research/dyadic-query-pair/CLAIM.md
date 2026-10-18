# Seed 54: fuse two completed native BIT shears

Claim recorded 2026-10-13 at 06:20 UTC (01:20 America/Chicago).
OS randomness (`secrets.randbelow(100)`) returned **54**: recursive interfaces.
Exact fresh `origin/main` base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
Primary checkout observed at PR756 head `4fad623a1e4ca06959f4326e221c2f8d9125c269`;
it and PR805's branch/worktree are reserved for their existing workers.
This work uses the isolated managed `seed54-boundary-interface` worktree.

## Selection and hypothesis

Three narrow candidates were considered: a shared-output dirty echo, a new
Gaussian boundary batch interface, and fusion of two completed native BIT
address shears. PR714/730/744/758/784/788 already cover many echo/checkpoint
classes; PR481 already prices the Gaussian batching mechanism. The third
candidate has a different object and permission contract and is selected.

PR521 supplies a one-child native unipotent query `h`. PR677 completes the
DATA shear `S_h: x ^= (h+I)y` with two queries on the target and no private
row. Investigate the completed pair `S_(h^a) S_(h^-a)` for `a=2^j`, using
the explicit six-affine/one-child lowering of `h^k` at dyadic `k`. Hypothesis:
`h^-a; XOR_y; h^(2a); XOR_y; h^-a` replaces four children by three and four
XOR scans by two, restoring every input except the prescribed target.

Method: derive the literal lowering over the rationals and every odd residue
ring; prove the endpoint over F2-valued full arrays; check full small ADDRESS
domains by a separate coordinate/permutation implementation; prove a
three-query lower bound in an explicitly scoped query/XOR model. Seed 54
selects the large fixed coefficient fixture `a=2^54`. Coverage includes
`j=0..54`, both signs, full-order/shorter/fixed orbits and dyadic modular
specializations. No randomized search or stronger-bound search is planned.

Price the optimistic complete typed recurrence before implementation:
three ordinary ADDRESS children, each on full BIT volume `V/3` and width
`N/3`, eighteen ordered affine scans, two aligned XOR scans, coefficient
preparation, primitive work, source access, routing and all head returns.
Compare against the completed four-child pair, including its twenty-four
affine scans and four XORs. No clean/disposable/borrowed full private row.
Primitive and child workspace remain paid. Growing `j` is not free.

Expected deliverable: scoped recursive-interface construction and written
query bound, standalone exact checker/certificate, full cost/storage limits,
source pins, negative controls and one focused PR; **no new kappa**.
Expected finish: by 07:15 UTC (02:15 America/Chicago). Reserve at least the
final quarter for verification, overlap refresh and handoff.

## Coordination and concrete non-overlap

No pinned issue exists (GitHub GraphQL `pinnedIssues` returned empty).
Immediately before this claim, live metadata covered 627 open PRs through
#814. No centered native query-pair fusion was found. The review ledger
marks PR521 and PR481 unreviewed; citation does not imply maintainer approval.
The selected record is PR741, conditional kappa `0.001661202643272239`;
its review, actual SW4 construction and source manifest were inspected.

PR756 is a performance change to a historical balanced-Fano enumeration.
This package touches no such checker, searches or performance receipts.
PR805 changes real rational cyclic leaves and restoration of one dirty
array plus a scalar. This package instead concerns exact odd-ring ADDRESS
permutations acting on F2 VALUE arrays, with queries on the genuine DATA
target and no full private row; it imports none of PR805's leaf construction,
restoration interface, code or verification. Both live PR descriptions and
relevant diffs were read. Neither existing PR will be changed.

Prepared for **Wentao Li** (GitHub `VictorLiwentao`) with substantial OpenAI
Codex assistance. Predecessor names and notices will be retained. Apache-2.0.

## Completed result (single final claim update)

Submitted [PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840).
The mathematical package commit is
`9623aa12bc4c3c3828f6a804c94c42f90e511041`; the exact base remains
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. This result update changes
only the claim record. The final PR head is reported in the chat handoff.

The hypothesis succeeds as a scoped construction: three ordinary ADDRESS
children, eighteen affine events and two XORs replace four children,
twenty-four affine events and four XORs for the specified completed pair.
All dirty source/spectator inputs are preserved and no full private row is
added. The proof establishes the sharp three-query minimum in the stated
power-query/XOR model; it does not assert a minimum over all tape programs.
Fixed-j coefficient costs and all typed primitive/child charges remain paid.
**No new kappa or physical runtime improvement is claimed.**

Reproduce: `python3 -I -O -B research/dyadic-query-pair/verify.py`.
Expected: `PASS_DYADIC_QUERY_PAIR`. Completed coverage: 112 signed lowerings,
1,792 rational columns, 16,128 modular columns, 91,320 two-query products,
154,160 full-domain dirty basis columns per program, 7,552 orbit columns,
25 mathematical/admission controls and six package faults. Final evidence
agrees on CPython 3.9.6, 3.12.14 and 3.13.2, including isolated optimized
and relocated offline runs. Exact fetched Git inputs, selected-record and
staged whitespace checks pass. One untouched-base `make verify` passes its
seven initial historical groups, then stops on missing SymPy at gen4
(exit 2); no full-suite or selected-supplier cold replay is claimed.

Final overlap refresh covered 636 open PRs through #839. The two consumed
PR heads remain unchanged. Later PR800/822/829/836/838 have different
Clifford, storage or evidence-admission objects; no code is consumed.
Upstream advanced to `f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting
PR799 at conditional kappa `0.001661634653669567`; its actual X4 construction
and review were read and recorded as context. No frontier record is edited.

Concrete non-overlap is unchanged: PR756's Fano checker/performance package
and PR805's rational cyclic leaf/dirty-array-plus-scalar restoration are
excluded. Neither existing PR, branch or worktree was changed. The result
uses exact odd-ring ADDRESS maps and F2 VALUE arrays on the genuine DATA
target, with no full private row. Complete supplier/physical/compiler and
analytic transfer remain open, as detailed in PROOF.md and VALIDATION.md.
