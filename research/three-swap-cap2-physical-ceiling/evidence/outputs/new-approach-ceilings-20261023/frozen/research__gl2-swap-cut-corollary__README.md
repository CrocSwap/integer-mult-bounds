# Coordinate-SWAP cost with any restored dirty workspace

**A source-bound corollary of PR1989, not a new general lower-bound theorem.**
In the formal `F2[GL_2(F2)]` model used by the coordinate-SWAP line, the exact
cost of `t` SWAP targets is **3t paid calls**, for every finite number `R>=t`
of arbitrary-input roles. This includes noncommuting scalar projectors and
any number of restored dirty spectator roles.

Consequently the thirteen-call five-SWAP candidate in
[Aaron Wang's PR2317](https://github.com/CrocSwap/integer-mult-bounds/pull/2317)
is excluded without a commuting-projector restriction: its minimum is 15.
Four SWAPs cost 12 even with extra dirty roles. These implications resolve the
same-model open questions 1 and 2 in the frozen
[four-SWAP note](../four-swap-full-occupancy/README.md).
Those historical files remain unchanged.

The contribution is the explicit model identification, an independent audit,
and a retrievable answer to the live handoff. The all-parameter cut theorem
and method are credited to
[PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989), whose
[proof](../symmetric-adjacent-cut-bound/PROOF.md) is retained byte-identically.
This is not a new supplier, a physical cost improvement, or a kappa claim.

## Exact model and isomorphism

Let

```
a = [1 1]     b = [1 0]     s = aba = bab = [0 1]
    [0 1]         [1 1]                    [1 0]
```

in `G=GL_2(F2)`. Products act on columns, so `gh` means `g` after `h`.
A paid factor is `D_N(g)=I_R+([g]+1)N`, where `g` is exactly `a` or `b`,
`N=uv^T` is binary, and `v^Tu=1`. Each paid factor costs one, including
all preparation and restoration. Scalar `GL_R(F2)` operations are free
and may be interleaved. There are no other free address operations, clean
allocations, resets, copies or erasures. The required complete formal map is

```
T = diag([s], ..., [s], 1, ..., 1),   with t copies of [s].
```

Every role begins arbitrarily; all spectators are individually restored and
all off-diagonal couplings vanish. Equality is coefficientwise in the full
formal group algebra, not equality of the natural two-dimensional matrices.

Order the three nonzero column vectors as
`v1=(0,1)^T`, `v2=(1,1)^T`, `v3=(1,0)^T`. Define `phi(g)` by
`g v_i = v_(phi(g)(i))`. This action is a homomorphism with the same product
convention. It is injective because fixing these vectors fixes a basis;
`|GL_2(F2)|=6=|S3|`, so it is a group isomorphism.

| GL2 element | Image in S3 | One-line image | Inversions |
|---|---|---|---:|
| e | e | 123 | 0 |
| a | (12) | 213 | 1 |
| b | (23) | 132 | 1 |
| ab | (123) | 231 | 2 |
| ba | (132) | 312 | 2 |
| s=aba | (13) | 321 | 3 |

Extending linearly maps the six formal basis elements bijectively and
preserves every product. It therefore gives an algebra isomorphism
`F2[G] -> F2[S3]`, and an entrywise isomorphism of register matrices.
It preserves the scalar projector `N`, every free scalar map, all role
counts and all dirty endpoint requirements. The paid labels become exactly
the two adjacent transpositions. Thus every hypothesis of PR1989 is met;
its inversion-sum theorem gives minimum `t*3`.

## Direct proof of the specialized lower bound

For clarity, this restates the relevant PR1989 argument with its notation
specialized, rather than relying on an unexplained invocation.
Use the six ordered pairs `(i,j)` of distinct labels in `{1,2,3}`.
Each permutation acts simultaneously on the two entries. Partition the
address basis into `H={i<j}` and `K={i>j}`, on **every** one of the R roles.
For the resulting operator M write `q(M)=rank_F2 M[K,H]`.

For arbitrary operators U,V, block multiplication gives

```
(UV)[K,H] = U[K,H] V[H,H] + U[K,K] V[K,H],
q(UV) <= q(U) + q(V).
```

No commutativity or invertibility is used in this inequality. A free
scalar map is `S tensor I_6`, so its crossing block is zero, even when
it mixes active roles with spectators. For a paid factor, the crossing
block is `N tensor P_g[K,H]`. Either adjacent label reverses exactly
one increasing ordered pair, so this block has rank `rank N=1`.
SWAP maps to reversal, which reverses all three increasing pairs with
independent images. The target crossing block is therefore the direct
sum of t rank-three blocks and R-t zero blocks, of rank `3t`.
Subadditivity proves that any legal word has at least `3t` paid factors.
All intermediate roles and their dirty values were included; no bound
on R except finiteness was used.

For attainment, on each target role j execute `a,b,a` with coordinate
projector `E_jj`. The formal product has `[aba]=[s]` in that diagonal
entry and identity elsewhere. Concatenating the t words gives T in
exactly `3t` calls. It uses no extra roles or free operations, and leaves
no restoration debt. This also handles t=0, with the empty word.

The universal conclusion rests on this written argument and the explicit
isomorphism. It is not an extrapolation from finite fixtures or a
formal-kernel proof.

## What this closes and what it does not

The mapping answers the exact formal-model questions in the four-SWAP
note and PR2317. PR2317's commuting-family computation remains credited
as predecessor evidence; the additional noncommuting search it proposes is
unnecessary in this same alphabet. This note does not rerun or supersede
its finite enumeration as independent evidence.

The natural two-dimensional GL2 representation alone is not faithful
on the group algebra: the nonzero formal sum of all six group elements
has zero natural-matrix image over F2. The checker rejects an endpoint
corrupted by this sum. The six-dimensional ordered-pair action for S3
is regular and faithful; full formal coefficients are nevertheless used
for the primary endpoint checks.

Charging a direct SWAP label as one call changes the alphabet: that
one factor crosses three directions. Charging a rank-two projector as
one call changes the tariff: it can cross two. Clean workspace with only
a restricted-input endpoint, partial/unrestored spectators, other address
maps or nonlinear operations also change the theorem's premises.
The argument supplies no native rational-address compiler, source access,
hosting, precision/tape, recursive child moment or outer multiplication
assembly. It does not settle the different abelian rational-frame model
or the GL3 CNOT alphabet. No selected cold replay is asserted.

## Reproduction and finite evidence

From the repository root:

```
python3.12 -B scripts/research_package.py --package research/gl2-swap-cut-corollary
```

`verify.py` uses packed full group-algebra coefficients and binary row
elimination, importing no predecessor implementation. It checks all 36
group products and 4,096 algebra products, all 1,302 paid factors for
R=1..5, and all 3,136 ordered pairs of three-role factors (including
noncommuting cases). It verifies both orientations of the direct word
for t=0..8 and R=t,t+1,t+2: 27 complete formal endpoints, plus all 324
single-call omissions. It checks wrong labels, dirty spectator coupling,
the natural-representation alias, free scalar mixing, and changed-price
boundary controls. These are complete finite domains, not searches over
all legal words.

`independent.py` and [REVIEW.md](REVIEW.md) give the separately implemented
regular-action audit, its exact domain and the mathematical model review.
`test_verify.py` exercises actual guard removal and semantic corruptions;
it also checks equivalent group-basis order and read-only Git-free replay.
Each detector must reject for the intended reason. The registered commands
run with `-O` to ensure their checks do not rely on Python assertions.

## Sources, attribution and freshness

Pinned base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
[SOURCES.json](SOURCES.json) authenticates both retained proof/model inputs.
PR1989 head: `8b9f3ec8b1e5745c42fec68d75da5fbc82ea91ec`; its proof is identical
to the pinned main copy (SHA256
`008be68867a8e85f4e18455d206e03f20aebfc28e9f08efba576180e7e1edc50`).
PR2317 head: `139779c86ba8215910117ddb383e4df007b23dcf`; its README SHA256 is
`edba3d71ad274311f3a8c2293d390a7adba38deca344662c0364cbdd192521d3`.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18944151)
answers its linked handoff in the existing investigation thread.

The entry overlap helper covered 614 open PRs including drafts and 1,139
Discussion records, with complete pagination and no warnings, at
2026-10-15 07:57–08:00 UTC. Focused follow-up at 08:01:57 UTC included local
READMEs, TASK records and the PR ledger. Closed PRs are represented through
local notes/ledger only; arbitrary diffs and nested sources are not searched.
No-match output is not a novelty claim: this is explicitly a corollary of
known work. TASK.json records the changed scope from the bit-mechanisms draw.

Credit: Ross Richardson/PR1989 for the general theorem; Adam Gall/PR1941 and
Ross Richardson/PR1966 for its cut-method predecessors; Cinna Davis for the
finite symmetric-group work credited there. Aaron Wang/PR2317 supplied the
commuting five-SWAP screen and the concrete live handoff. The coordinate-SWAP
model and earlier bounds retain Gareth Davidson/PR1333,
commdata2338/PR1414/1491, Cinna Davis/PR1541, Ross Richardson/PR1722 and the
four-SWAP note, and Aaron Wang/PR1705/1755 lineage. See the pinned source
notes for their own earlier attribution. Prepared by Ross Richardson with
substantial OpenAI Codex assistance, including a separate mathematical
verification specialist. No independent human review is claimed. Apache-2.0.

## Open next questions

No further uniform-price formal SWAP search in this exact alphabet is
justified by these handoffs. A useful follow-up must identify a changed
operation, price or endpoint contract, derive its crossing charge, and
fully price any physical implementation before claiming supplier relevance.
The first decisive check is whether the proposed call can cross more than
one direction for its declared charge. Native realization and complete
recursive accounting remain the blockers to transferring such an escape
into the multiplication construction.
