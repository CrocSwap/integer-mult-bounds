# Three GL2 swaps need five capped-rank invocations

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof; no new kappa.** Three independent coordinate-SWAP targets
have exact minimum **five invocations** when each paid coordinate-CNOT call
may have scalar rank one or two and costs one invocation. The complete
five-call word has rank profile `(2,2,1,2,2)` and total scalar rank nine.
It improves the six-invocation implementation that separately batches two
roles and processes the third role. Every additional dirty role returns
unchanged, with no off-diagonal residue.

More generally, if a rank-one call costs `c1` and a rank-two call costs `c2`,
where `0 <= c1 <= c2 <= 2*c1`, the exact minimum is

```text
c1 + 4*c2.
```

The disjoint batching bill is `3*c1 + 3*c2`. The new saving is therefore
`2*c1-c2`, positive for every strictly subadditive price `c2<2*c1`.
In particular, a power price `c_r=r^theta`, with `0<=theta<=1`, gives
`1+4*2^theta`. Scalar projector rank is not recursive child rank, so this
local result supplies no changed supplier histogram or multiplication bound.

## Model

Let `G=GL_2(F2)`, with

```text
a = [[1,1],[0,1]],  b = [[1,0],[1,1]],  s=aba=bab=[[0,1],[1,0]].
```

For any finite `R>=3`, work coefficientwise in `M_R(F2[G])`. All registers
start arbitrary. The required complete endpoint is
`T=diag([s],[s],[s],1,...,1)`.
A paid invocation is

```text
D_N(g)=I_R+([g]+1)N,  g in {a,b},  1<=rank_F2(N)<=2.
```

The theorem allows arbitrary binary `N`, including nonidempotent matrices.
Restricting the alphabet to idempotents gives the same optimum, since the
attaining word uses only diagonal idempotents. Every factor is invertible:
its square is identity because `([g]+1)^2=0` in characteristic two.
Free scalar `GL_R(F2)` mixing may occur anywhere. There are no other free
address maps, resets, clean allocations or omitted restoration calls.

The changed premise from the rank-one GL2 results is the cap-two invocation
price. David Arias's [PR2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738)
proves the scalar-rank tariff but explicitly leaves sublinear higher-rank
invocation prices outside its conclusion. Ross Richardson's
[PR2415 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18944151)
names rank-two unit prices as a changed question. Their results are used as
cited mathematical premises; their scientific replays are not run here.

## Attaining construction

For a set `S` of role indices, write `E_S=sum_(j in S) E_jj`.
Execute these calls in the listed chronological order, with zero entries
on every role above two:

| Call | Label | Role support | Scalar rank |
| --- | --- | --- | ---: |
| 1 | a | 0,1 | 2 |
| 2 | b | 0,2 | 2 |
| 3 | a | 2 | 1 |
| 4 | b | 1,2 | 2 |
| 5 | a | 0,1 | 2 |

Role zero receives `a,b,a`, role one receives `a,b,a`, and role two receives
`b,a,b`. Both palindromic words equal `s`; the rightmost-first matrix-product
convention therefore gives the same stated endpoint. All factors are
diagonal in role space. Their formal product has no off-diagonal entries,
and every spectator diagonal remains exactly `[e]`. This is an identity in
the full group algebra, with no restriction on register values or addresses.

The two target roles that share a call change between calls. Requiring a
fixed partition into a two-role block and a singleton would miss this word.
No scalar bridge, auxiliary role or uncharged cleanup is needed to attain it.

## Optimality and the exact price

We cite the rank-priced extension in
[PR2738, proof section 7](../coxeter-root-tariff/PROOF.md#7-rank-priced-extension-and-scope-boundaries),
using the product-preserving `GL_2(F2)=S3` bridge retained in
[PR2415](../gl2-swap-cut-corollary/README.md).
Its root-cut lower bound is valid for arbitrary binary scalar couplings,
free scalar mixing and arbitrary finite restored dirty workspace. Since
`s` is the length-three longest element of `S3`, **every legal circuit here
satisfies `sum_i rank(N_i)>=9`**. This nine-unit inequality is inherited,
not a new lower-bound theorem claimed by this package.

Each invocation has rank at most two, so four invocations supply at most
eight rank units. At least five invocations are necessary. The table attains
five and nine rank units, proving the exact invocation minimum in both the
arbitrary-coupling and idempotent-only alphabets.

For the price theorem, let `q1,q2` count rank-one and rank-two calls. Then
`q1+2*q2>=9`. If `q2<=4`, the nonnegative price assumptions imply

```text
c1*q1+c2*q2 >= 9*c1-(2*c1-c2)*q2 >= c1+4*c2.
```

If `q2>=5`, the bill is at least `5*c2>=c1+4*c2`. These two cases cover
every finite circuit, including zero prices. The table attains the lower
bound exactly. No rounding of a numerical moment or finite word exclusion
is used in this proof.

The interval `c1<=c2<=2*c1` is part of the statement. For example, with
`c1=1,c2=3`, nine rank-one calls cost nine, below the displayed formula
thirteen. The verifier rejects prices outside the stated interval.

## Evidence and reproduction

Use CPython 3.12 with the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank2-swap-batching
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rank2-swap-batching/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/rank2-swap-batching/verify.py
```

Expected markers are `PASS_RANK2_SWAP_BATCHING minimum=5` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. A different installation can substitute
its own CPython 3.12 path. Default replay writes no files and needs neither
Git nor network. `--emit-receipt` prints a newly computed, source-hash-bound
receipt to standard output. The committed [RESULT.json](RESULT.json) is
generated by that command, never written by hand.

The primary checker multiplies all formal coefficients using binary GL2
matrices. A separate checker builds `S3` from permutations of three points
and applies the gates to every column of its faithful left regular module.
Both check the new complete endpoint. The finite fixtures cover all 168
invertible scalar gauges at three roles, and elementary plus dense gauges
at four through six roles. Gauged calls include actual dirty-role coupling,
with separately applied entrance and exit maps. Each call omission and label
flip must change the formal endpoint; unmatched dirty coupling and an illegal
rank-three invocation must also fail. Exact rational price cases check the
new two-case integer-profile argument. Exact enumerated totals are in the
receipt, not extrapolated to larger spaces.

The universal conclusion is the written construction and price proof using
the cited rank bound. The finite fixtures are corroboration. This is not an
exhaustive search over all legal words and does not replay predecessor
censuses or certify the inherited proof in a formal kernel.

## Open next questions

1. What native interface can implement this exact cap-two scalar-coupling
   invocation at a strictly subadditive complete price? First specify its
   data layout and arbitrary-input entry/exit contract, then charge its
   compilation, scalar work, routing, ownership, precision and cleanup.
   Those physical costs are unknown here; another construction round is
   not justified by the formal five-call count alone.
2. What is the exact three-target tariff when scalar ranks above two are
   allowed at a declared price? First specify one price schedule and compare
   complete attaining words with the inherited nine-unit rank floor.
   The cap-two price argument does not classify that changed alphabet.

## Credit, overlap and limits

David Arias's PR2738 supplies the rank-priced Coxeter theorem. Ross Richardson's
PR1989 supplies the symmetric-group cut theorem, and PR2415 supplies the GL2
bridge and changed-price handoff. Adam Gall's PR1941 and Ross Richardson's
PR1966 retain the cut-method credit. Arham Tahir's
[PR1919](../ut3-rank-bounded-block-calls/README.md) supplies a related cyclic
rank-capped batching precedent for the distinct UT3 central target.
Ali Romman's [PR5031](../mixed-gl2-block-tariff/README.md) prices mixed GL2
blocks at rank one and does not admit unit-priced rank-two invocations.
The underlying register-model lineage includes eumemic, Ali Romman,
Gareth Davidson and David Govea. All retained source notices remain unchanged.

The new contribution is the displayed five-call GL2 support schedule and
its sharp cap-two invocation/concave-price consequence. The rank bound,
GL2 bridge, general cut method and the idea of higher-rank batching are
credited predecessors. No literature-priority claim is made.

The [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19141448)
records the concrete scope. Base is canonical main
`4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision seven.
A submission checkpoint fetched main at
`9269eea18a6a10dddeac6a4f696904c55ef1d365`; guidance, selected record and
the four relevant predecessor paths were unchanged. The scientific base
and immutable pins are retained.
The overlap snapshot covered 330 open PRs and 4193 Discussion records with
complete remote pagination. Sparse local coverage was 128 of 6760 note
paths, supplemented by distinctive main-tree and merged-PR searches and
direct predecessor reads. Arbitrary diffs and unpublished work are outside
that coverage. Open PR2444 concerns rank-one five-SWAP search tooling;
its changed-price boundary is a lead, not a claim to this cap-two result.

Native/compiler admission, physical payload/tape/precision/stock costs,
a complete recursive invoice, selected cold replay, Lean, independent human
review and a complete multiplication theorem are unrun or outside scope.
The selected frontier is unchanged. See [SOURCES.json](SOURCES.json) for
immutable provenance pins and [TASK.json](TASK.json) for the scope change.

### Verifier bounds and diagnostics

The verifier has no recursive calls, solver, subprocess or background service.
Its matrix dimensions are at most six, group tables have six elements,
scalar-gauge enumeration has at most 512 candidates, and price-count checks
use a 13-by-13 grid. Each routine is shorter than sixty physical lines.
Explicit exceptions retain all invariants under optimized Python.

Python dynamically allocates tuples, lists and arbitrary-size integers. This
is a managed-runtime deviation from fixed allocation, confined to the bounded
finite verifier, not a real-time or native-memory guarantee. The dimension
and enumeration caps bound live collections; no unbounded input is accepted.
The compensating checks are the normal and optimized warning-strict registered
commands. Revisit allocation and capacity if these corroboration bounds grow.
No shared repository diagnostic configuration is changed.
