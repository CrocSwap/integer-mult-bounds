# PR4610 comment resolution and next construction contract

TL;DR: PR4610 has one substantive comment, by Matarener, and no formal reviews
or inline review threads at this checkpoint. It reports bounded no-gain
evidence, rather than a correctness defect requiring a code patch. The new
construction work explicitly changes the fixed-warp premises of that search.
No higher kappa or independently verified search ceiling is claimed here.

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

## Comment addressed

Source: https://github.com/CrocSwap/integer-mult-bounds/pull/4610#issuecomment-6342665165
by Matarener, last updated 2026-10-22T14:02:04Z.

The reported experiments distinguish two frozen inputs:

| Input | Reported scope | Result |
| --- | --- | --- |
| 4b4c75bc0fd64d3eee54029e8d2fab834251fca6 (.00302152) | Eight MILP variants and three plateau chains, plus commuting windows through K=8 | No improvement in those models |
| 1eb8da6cfb35512c0cc2533413e5ca42f48e13c6 (.00302176 native word) | Commuting windows through K=8; MILP/plateau not rerun | No improvement in those windows |

Both hold warp entrance/exit frames and maps fixed and vary the stated
commuting-scalar/contact family. The report does not establish global
optimality for the current word, arbitrary reorderings, changed warp maps,
paid phase changes, altered helpers or new recursive interfaces. Solver
optimality in the reported finite models is not an exact all-size ceiling.
These are the contributor's reported results; their unpublished scripts and
solver certificates have not been independently replayed by this package.

Resolution: credit and retain this bounded negative evidence, avoid rerunning
the same fixed-warp family, and make the changed premise of each new search
explicit. The latest .0030217758 compiler refinement uses the same 1eb8 native
word; it does not contradict the comment or claim a new scalar reorder gain.

`REVIEW.json` records the source ID, body hash, timestamps and scope distinction.
`REVIEWS.json` and `REVIEW-THREADS.json` preserve the empty API results. GitHub
thread-state resolution is not applicable because this is a conversation
comment, not an inline review thread. No contributor's comment is hidden,
edited or deleted.

## Open next questions and acceptance plan

1. **Paid phase interfaces.** First seed a phase carrier on an actual helper,
   transport it consistently through the shared native G maps, and compute
   the exact added paid ranks versus independent helper reward. PR4665's
   fixed-rank/fixed-boundary phase obstruction remains credited; changing a
   phase label without paying the changed edge does not escape it.
2. **Coupled recursion.** First compose the actual restored round5 involutive
   lift with a phase adapter and derive an arbitrary-input endpoint identity.
   Every owned stream, phase normalizer, recursive call and restoration is
   charged. An unfunded block matrix is not a supplier.
3. **Grouped phase types.** Distinguish one global S(P) from a tensor product
   of f phases. First derive the exact split/merge contract and cost of the
   smaller Gaussian pivot job. A fixed global correction cannot be credited
   with eliminating an entire tensor-width rank without proof.

Any candidate above .0030217758 must have a changed actual native/recursive
construction, a complete strict moment and compiler/outer transfer, exact
arbitrary-helper replay, independent checks and scoped Lean proofs. Another
compiler-reserve change does not meet this assignment. The full native phase
semantics and complete physical/analytic compiler theorem remain separate
formalization obligations; the current Lean certificates retain their stated
scope.

The user's initial reference to #4160 was explicitly corrected to #4610.
Partial unrelated R437 work was stopped and preserved as unfinished local
research. It is not an additional admission premise or published contribution
of this comment resolution.
