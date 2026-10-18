# Two S4 double-transposition targets need eight paid calls

**Scoped exact negative result; no new κ.** With three dirty scalar roles,
free `GL3(F2)` mixing and the paid alphabet of adjacent transpositions, two
copies of the S4 double transposition `(13)(24)` require exactly eight calls.
The natural displacement-rank floor is only four, so this test asks whether
register mixing can use that gap. A sign-determinant parity argument and a
complete formal radius-three meet-in-the-middle exclude every possible
improvement to six calls.

## Exact model and optimistic cost

Let `R = F2[S4]`. There are three scalar roles over `F2`, all with arbitrary
dirty input. A call chooses one adjacent transposition
`s in {(12),(23),(34)}` and one of the 28 rank-one idempotents
`N = u v^T in M3(F2)` with `v^T u = 1`, and applies

```text
D(s,N) = I3 + ([s] + [e]) N.
```

Every call costs one. Arbitrary interleaved scalar `GL3(F2)` maps are free.
The endpoint is the full formal group-algebra matrix
`diag([(13)(24)],[(13)(24)],[e])`; therefore the third arbitrary dirty role
is restored identically. The complete alphabet has 3×28=84 paid factors.

The direct Coxeter word for `(13)(24)` has length four, so the two-target
upper bill is eight. In the natural permutation representation on `F2^4`,
each adjacent transposition has displacement rank one, while `(13)(24)` has
rank two. Rank subadditivity therefore gives a four-call lower floor. The
strict improvement objective is six calls or fewer, a two-call / 25% saving.
This screen grants free register mixing and the third role without any
separate hosting, allocation or restoration charge, and charges every paid
address call. It is an optimistic local model, not a physical bit supplier.

The accepted selected record is
`κ = 836330098538459/500000000000000000`, with selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Its review is `docs/research/community-batch1099-review.md`; the source
manifest is `research/community-frontier1094-audit/SELECTED-SOURCE.json`; the
assembly certificate is
`research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`); the
reproduction command is `make frontier1094-verify`. The binding-only baseline
reports the complex primitive as binding. This result has no supplier
occurrence, recursive moment or selected-κ implication.

## Exact lower bound and matching construction

The selected word `s2 s1 s3 s2` (where `s1=(12)`, `s2=(23)`, `s3=(34)`)
equals `(13)(24)`. Applying it with coordinate idempotent `E11`, then with
`E22`, gives the exact eight-call formal endpoint. All eight single-call
omissions and an endpoint changed on the dirty third role fail exact replay.

For the lower bound, augmentation `ε([g])=1` sends every paid factor to the
identity. Move any free scalar map through a paid factor by conjugating `N`;
the conjugate remains a rank-one idempotent. The product of all free maps is
then the identity by augmentation, so it suffices to enumerate words in the
84-factor alphabet.

The sign homomorphism `S4 -> C2` sends every paid adjacent transposition to
the nontrivial element `x`, with `x^2=1`, and sends the even target
`(13)(24)` to the identity. Over the commutative ring `F2[C2]`, the matrix
determinant lemma gives
`det(I + (x+1) u v^T) = 1 + (x+1) v^T u = x`.
Every scalar `GL3(F2)` map has determinant one. Hence a `k`-call word reaching
the target must satisfy `x^k=1`, so `k` is even. A strict improvement over
eight must consequently use at most six calls.

Every paid factor is an involution because `( [s]+[e] )^2=0` in
characteristic two. Any word of length at most six splits into two words of
length at most three. Reversing the second part from the target would put an
intermediate matrix in both radius-three balls. The exact search enumerates
all such formal matrices, storing each 3×3 matrix as nine 24-bit
`F2[S4]` coefficient masks. Each ball has layer counts
`[1,84,4697,232692]`, for 237,474 states; their intersection is empty.
The hashes of the sorted packed states are recorded in
[CERTIFICATE.json](CERTIFICATE.json). The two upper/lower arguments establish
that the exact minimum in this model is eight.

This is an exact theorem about one finite paid alphabet and one endpoint,
not a test over selected address columns. The natural representation supplies
only the weaker rank floor; the final exclusion uses the complete formal
group-algebra balls. The proof does not rely on faithfulness of the natural
group-algebra representation.

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/s4-double-transposition-seedb270/verify.py
python3.12 scripts/research_package.py --package research/s4-double-transposition-seedb270 --check-only
python3.12 scripts/research_package.py --package research/s4-double-transposition-seedb270
```

Expected verifier output begins:

```text
PASS_S4_DOUBLE_TRANSPOSITION EXACT_8 direct=8 rank_floor=4 parity=even factors=84
balls=237474,237474 intersections=0 layers=[1, 84, 4697, 232692]
```

On Python 3.12.3 the full exact replay took about 3.1 seconds and used 93 MiB
peak resident memory as measured by `/usr/bin/time -v`. The certificate stores
deterministic complete-ball hashes, not an unbounded or sampled search.

## Scope and overlap

The main nonabelian register predecessors are PR #1720 (head
`edb4a289a5f32c8209140144e384dcd3fa8cbfd1`), which treats two 4-cycle targets
in S4 with the same adjacent-transposition alphabet, and the completed UT3
central-commutator results in PR #1443 and its later third-role follow-up,
PR #1478 (head `b30fdba48f3db70e3589ba740b0782b56ec0ba2e`). The present
endpoint changes the target cycle type to `(2,2)`, where transposition length
four exceeds natural displacement rank two; the question is whether scalar
mixing bridges that specific gap. PR #1333's exact binary-affine register
formula and PR #1573's UT3 all-register rank result also use displacement-rank
arguments, but their address groups, paid alphabets and targets differ. This
package does not claim a new general rank method and imports no predecessor
code. PR #1705's GL2 coordinate-SWAP targets and PR #1711's AGL2 affine targets
are also distinct.

The pre-submission PR scan used REST at 2026-10-14 08:12 UTC and covered 415 open PRs;
the only S4 adjacent-transposition match was PR #1720's 4-cycle endpoint, and
no double-transposition claim appeared. The overlap helper could not refresh
its own PR cache because the installed `gh api` rejects `--slurp`, so the REST
census was run directly. A fresh complete Discussion fetch at 08:12 UTC covered
366 records and showed no S4 `(2,2)` target claim. The completed finding was
posted to [coordination Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18919260).
The full local claim is in [CLAIM.md](CLAIM.md), including the exact seed,
catalogue revision, base, selected-record hash, scope, competitors and expiry.
The focused result is submitted as [PR #1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734).

This local model is not physically mapped to the selected bit supplier. The
selected baseline remains complex-primitive-bound; physical address
realization, hosting, precision, restoration cost in a native circuit and
recursive-moment impact remain unestablished. No selected source, certificate
or frontier value is changed.

## Open next questions

The exact local endpoint is closed, so no adjacent target tuple is claimed.
The remaining question is whether any selected bit supplier exposes these
adjacent transpositions at a fully charged unit cost while retaining the dirty
role contract. The first step would be an explicit supplier-interface map and
invoice; the current complex-primitive binding and absence of an identified
supplier occurrence block a selected-bound conclusion.

## Research record and credit

This is a fixed nonabelian register-model negative result, not a new supplier,
conditional bound or multiplication theorem. Sources are pinned in
[SOURCES.json](SOURCES.json); the complete state and controls are in
[CERTIFICATE.json](CERTIFICATE.json), and the written argument is
[PROOF.md](PROOF.md). Prepared by Cinna Davis with substantial OpenAI Codex
assistance in scoping, algebraic proof, exact implementation, verification and
writing. No subagents or independent human review are claimed. Apache-2.0.
