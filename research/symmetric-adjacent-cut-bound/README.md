# Adjacent permutations cannot share paid calls across dirty registers

For every symmetric group `S_n`, every target tuple, and any finite number
of restored dirty registers, the exact paid-call cost in the formal model
below is `sum_j inv(w_j)`. Extra dirty roles and free scalar mixing cannot
improve the direct bill. This is a written all-parameter obstruction, with
finite corroboration; it gives no physical BIT supplier, recursive moment,
or new kappa. The selected construction and its frozen inputs are unchanged.

## Exact model and proof

Work in the full formal group algebra `F2[S_n]`, for `n>=2`. A paid unit is
`I_R + ([s_i]+1)N`, where `s_i=(i,i+1)` and N is any binary rank-one
idempotent. Arbitrary scalar `GL_R(F2)` mixing is free. Every entrance value
is arbitrary. The complete endpoint is
`diag([w_1],...,[w_W],1,...,1)`, with `R>=W`; every spectator and every
off-diagonal coupling must be restored. All preparation and restoration
calls count. No other free address maps, resets, erasures or clean cells
are supplied by the model.

The [proof](PROOF.md) lets permutations act on ordered distinct pairs and
separates increasing pairs from decreasing pairs. Crossing-block rank is
subadditive under multiplication. Each paid call has crossing rank one;
free scalar maps have rank zero there; the endpoint rank is the sum of
inversion counts. Coordinate-projector adjacent sorting words attain that
bill in the full formal algebra, without extra roles.

The lower-bound representation is not an endpoint oracle: the nonzero
formal sum of all 24 S4 permutations has zero ordered-pair image. Both
checkers reject a dirty-output perturbation using this kernel. Attaining
endpoints are proved and checked in the full formal algebra separately.

## Contribution and predecessor credit

Cinna Davis's computations already establish these fixed S4 cases:

| Earlier object | Direct and now uniform minimum | Predecessor |
| --- | ---: | --- |
| Two copies of `(1234)` | 6 | [PR1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720) |
| Two copies of `(13)(24)` | 8 | [PR1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734) |
| Two noncommuting adjacent 3-cycles | 4 | [PR1749](https://github.com/CrocSwap/integer-mult-bounds/pull/1749) |
| `(13)(24)` together with `(12)(34)` | 6 | [PR1801](https://github.com/CrocSwap/integer-mult-bounds/pull/1801) |

This proof covers all n, heterogeneous target tuples and all finite dirty
role counts at once. Further finite sharing searches in this same model
are unnecessary. We do not claim to rerun the predecessor searches.

The theorem also gives 10 for the single S5 reversal posed in
[this earlier claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18919621),
and six for the S4 cycle/inverse pair posed in
[this claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18924180).
These are credited problem statements, not assertions about unpublished outcomes.

The cut-rank method follows Adam Gall's
[PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941) and Ross
Richardson's [PR1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966).
The added ingredient is the ordered-pair action for the adjacent symmetric
group alphabet. The abelian rational-frame model and its attribution remain
in the pinned [three-register predecessor](../bit-three-register-lower-bound/README.md).
Exact heads, scope, source pins and overlap limits are in [PROOF.md](PROOF.md),
[TASK.json](TASK.json), [SOURCES.json](SOURCES.json), and [OVERLAP.json](OVERLAP.json).
The [independent review](REVIEW.md) identifies the exact mathematical source hashes.
No claim of literature priority is made.

## Exact finite evidence

The universal conclusion comes from the proof. The two implementations use
different state encodings and construct attaining words differently.

| Covered finite domain | Evidence |
| --- | --- |
| All 5,912 permutations in S2 through S7 | Sorting words and explicit cut matrices; independent complete Cayley BFS on 34,406 directed edges |
| All 1,550 paid factors for n=2..5, R=1..4 | Complete rank-one inventories, crossing ranks and involutions |
| All 1,885 words of lengths 0..3 for n=3, R=2 | Full formal expansion and cut inequality, including every diagonal endpoint |
| All 576 ordered S4 pairs with a third dirty role | Full formal endpoints and inverses; all 3,456 single-call omissions reject |
| All 168 scalar GL3 changes on a mixed-target circuit | Dirty mixing and exact restoration; all 4,704 projector conjugations |
| Three fixtures at n=8,12,20, R=5 | Three active targets and two spectators; formal words and inverses |

The [independent checker](independent.py) imports no producer code or receipt.
Besides BFS, it checks 350 complete paid matrices, all 175 scalar GL matrices
through three roles, 35 distinct rank-one projector conjugates, 744 formal
S4 endpoints, and all prefixes of 168 scalar-gauged words. The producer's
[fixed receipt](EXPECTED.json) records counts, histograms, canonical word
hashes and eleven boundary controls.

Six tests additionally remove actual acceptance predicates to check control
sensitivity, corrupt scientific receipt fields, reject duplicate/missing
evidence and source drift, and check byte-identical explicit generation plus
unchanged isolated optimized replay in a read-only copy. The controls cover
changed alphabets, rank undercharging, nilpotent projectors, singular/free
address maps, dirty leaks, missing restoration, scalar residues, reversed
noncommuting words and representation kernels.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/symmetric-adjacent-cut-bound
```

The registered commands run the producer, independent checker and six tests.
For direct replay:

```sh
python3.12 -I -B research/symmetric-adjacent-cut-bound/verify.py
python3.12 -I -B research/symmetric-adjacent-cut-bound/independent.py
python3.12 -I -B research/symmetric-adjacent-cut-bound/test_verify.py
```

Expected producer marker: `PASS_SYMMETRIC_ADJACENT_CUT_BOUND` with
`permutations=5912 s4_pairs=576` and `no_new_kappa`. Default replay consumes
EXPECTED.json; `--write` is a separate, explicit generation operation.
The registered runner also checks historical Git provenance. None of these
commands is a selected-supplier cold replay.

## Open next questions

Does cross-register sharing remain impossible when adjacent labels have
different positive prices? The unit-price proof does not establish an exact
weighted tariff. A bounded first step is S4 with prices `(1,2,1)`: compute
direct weighted distances by exact Dijkstra search and test combinations of
permutation-action cut inequalities on all 576 ordered target pairs. The
blocker is a matching weighted lower bound, or a complete formal sharing
counterexample. PR1966 already handles the two-generator odd-dihedral case;
another unchanged S3 census is unwarranted.

Physical supplier adoption separately needs a source/target interface,
native address and scalar-operation costs, frame/hosting, precision/tape
accounting, and a complete recursive profile. Those obligations remain open.
The proof's rank-d corollary charges each rank-d call by d; it does not price
invocations at one or establish a nonlinear recursive moment.

Prepared by Ross Richardson with substantial OpenAI Codex assistance.
The math-bit-suppliers specialist derived the proof; a separate
math-exact-circuit-verification specialist independently checked it and wrote
the second engine. This is AI-assisted review, not independent human or Lean
verification. New work is Apache-2.0.
