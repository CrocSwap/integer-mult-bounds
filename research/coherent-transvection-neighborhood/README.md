# Exact cycle-constrained chart neighborhoods

This contribution, produced by Nick Petalas, proves a scoped binary symplectic
geometry result. It extends David Ganz's single/pair transvection enumeration
in [PR4841](https://github.com/CrocSwap/integer-mult-bounds/pull/4841) to any
nonempty tuple of Lagrangian charts and a linear restriction on the allowed
axes. A graph-cycle kernel supplies one useful such restriction.

The new result is an exact formula, an executable duplicate-free enumerator
and a written all-dimensional proof. The finite certificate corroborates that
proof. It is not a changed physical word, supplier admission, a complete
multiplication theorem or a new kappa. The selected frontier is unchanged.

## The result

Let V be a 2n-dimensional symplectic space over F2, with n>=1 and alternating
form omega. For a in V put T_a(x)=x+omega(x,a)a, including T_0=identity.
Let L_1,...,L_s be any nonempty finite tuple of Lagrangians. Let A be a linear
subspace of allowed axes. Define

```
I = intersection of all L_i
B = A intersect I
m = dim A, b = dim B, r = m-b
t = rank of the pairing A -> B*, a |-> omega(a, .)|B
```

Then 0<=t<=min(b,r). The exact number of distinct **changed** tuples
`(T_a L_1,...,T_a L_s)`, for a in A, is

```
N(A; L_1,...,L_s) = 2^(r+1) - 2^(r-t) - 1.
```

The unchanged tuple is excluded. All axes in B produce that one tuple.
For every a in A outside B, its exact fiber is

```
a + (B intersect a-perp).
```

In particular its size is 2^b if a is orthogonal to B and 2^(b-1) otherwise.
This characterizes every fiber, not only the number of outputs.

Choose any vector-space complement C of B in A. For each nonzero c in C,
retain c. If omega(c,B) is nonzero, choose b_c in B with omega(c,b_c)=1 and
also retain c+b_c. These axes produce every changed tuple exactly once.
`neighborhood` in [verify.py](verify.py) implements this algorithm from bases,
using coefficient kernels rather than enumerating the ambient axis space.

## Proof

We use the one-chart equivalence stated and proved in David Ganz's
[complete-neighbors construction](https://github.com/CrocSwap/integer-mult-bounds/blob/6debdcdac8fe1c87958f8cd42ccb7db73c0a0eef/research/native-clifford-gauge-compiler/decoder/COMPLETE-PAIRED-NEIGHBORS.md),
at the exact predecessor head. For a Lagrangian L, T_a L=L exactly when a is
in L. For two nonfixed axes a,c, their changed charts agree exactly when
`c-a in L intersect a-perp`. This is an inherited lemma. No predecessor
verifier or supplier is imported or replayed here.

**Tuple fibers.** Suppose a is outside I and a,c produce the same tuple.
At least one chart moves. On every moved chart, the inherited equivalence
puts c-a in that chart and in a-perp. On a fixed chart, both axes belong to
the chart, so their difference also belongs to it. Therefore c-a lies in
`I intersect a-perp`. Conversely this condition fixes every originally fixed
chart and gives equal images on every moved chart. Restricting a,c to A
changes I in this difference condition to B. Axes in B fix every chart;
axes outside B move at least one. This proves the full fiber statement.

**Count and representatives.** B is isotropic because it is contained in
L_1. Hence the functional omega(a,.) on B is constant on every coset of B
in A. It defines a rank-t linear map from A/B to B*, so t<=r and t<=b.
Exactly 2^(r-t) cosets annihilate B. Each such coset is one fiber. Every
other coset has two fibers, because its nonzero functional on B has a
codimension-one kernel. Thus the number including the unchanged tuple is

```
2^(r-t) + 2 (2^r - 2^(r-t)) = 2^(r+1) - 2^(r-t).
```

Remove its zero coset. A complement selects one c from each remaining
coset. When there are two fibers, addition of b_c crosses between them.
Different cosets cannot give equal tuples by the fiber statement. This
proves the formula and the duplicate-free construction for all n,s,A.

**Relation to the predecessor.** If A=V and k=dim I, then m=2n, b=t=k by
nondegeneracy, giving `2^(2n-k+1)-2^(2n-2k)-1`. For s=1 or s=2 this is
Ganz's existing result. That specialization is not claimed as new. The
new boundary permits any number of charts and restricted axes, where t
need not equal b and an ambient-space substitution can give the wrong count.

## Exact transport through a graph

Consider a finite connected contact graph. Each oriented internal edge e:u->v
has a specified symplectic map S_e. Choose a rooted spanning tree and let R_v
be its root-to-v transport, with R_root=identity. A coherent transvection
assignment has axes a_v=R_v a. The complete allowed root-axis space is

```
A = intersection over edges e:u->v of ker(R_v - S_e R_u).
```

Tree-edge equations vanish. Equivalently each remaining cycle fixes a under
its root holonomy `R_v^-1 S_e R_u`. The equations retain every edge, including
parallel edges and inconsistent cycles.

Indeed `S T_a S^-1 = T_(S a)` for a symplectic S. Over F2 the axis map
`a |-> T_a` is injective, including zero. For nonzero a, the image of T_a-I
is the line spanned by a, whose only nonzero element is a. Consequently
`T_(a_v) S_e = S_e T_(a_u)` holds exactly when a_v=S_e a_u.
These are precisely the kernel equations above. The tree forces every coherent
assignment to have a_v=R_v a, so the kernel is also necessary.

Apply the theorem to root-coordinate charts `K_v=R_v^-1 L_v` and this A.
Multiplying each output by R_v is invertible, so it preserves equality and
distinctness of chart tuples. The enumerator is therefore complete for the
stated coherent graph moves. Every internal contact rank is preserved, since

```
(T_(a_v) L_v) intersect (S_e T_(a_u) L_u)
    = T_(a_v) (L_v intersect S_e L_u).
```

This is a sufficient restricted class. The theorem does not classify all
assignments that happen to preserve internal ranks. Boundary-edge costs,
absolute phases, ownership, endpoint restoration and all compiler/precision
costs must still be paid in an actual changed word. Their new full invoice is
unknown here. The family decision is to retain this local enumeration lemma
and stop before further physical construction or optimization.

## Two sharp finite distinctions

Write e_1,e_2,e_3,f_1,f_2,f_3 for the standard symplectic basis. Compare

```
U = (span(e1,e2,e3), span(e1,f2,f3), span(f1,e2,f3))
W = (span(e1,e2,e3), span(e1,f2,f3), span(e1,e2+f2,e3+f3)).
```

Every pair in either triple intersects in dimension one. U has common
intersection zero and exactly 63 changed tuples. W has common intersection
span(e1) and exactly 47. Thus even all pairwise distances fail to determine
the coordinated triple neighborhood.

For W, impose the single cycle holonomy T_e1. Its fixed-axis space is
A=e1-perp. Now `(m,b,t)=(5,1,0)` and exactly 15 changed tuples remain.
The unrestricted ambient formula gives 47 and would overcount this search.
The verifier enumerates each stated endpoint set literally.

## Verification and reproduction

Use CPython 3.12 and its standard library. From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/coherent-transvection-neighborhood/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/coherent-transvection-neighborhood/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/coherent-transvection-neighborhood
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/coherent-transvection-neighborhood --check-source-history
```

Expected direct output is
`PASS_COHERENT_TRANSVECTION_NEIGHBORHOOD cases=226260 literal_graph_axes=4096`.
Checks use explicit exceptions and remain active with -O.

For n=1,2 the replay enumerates every linear allowed-axis subspace and every
ordered triple of Lagrangians, including repeated charts. It compares the
actual transformed-subspace sets and exact axis fibers with the representatives
and the formula. The implementation caches identical `(A,B)` enumeration
problems, while testing the literal outputs for every triple/subspace case.
It also checks 256 three-vertex graphs with two independent cycle constraints,
using all 4,096 root-axis tests and literal matrix conjugation equations.
The two n=3 distinctions above are checked separately. Eleven invalid-input
controls and five named mathematical mutations reject. See the generated
[RESULT.json](RESULT.json) for the full enumerated histograms.

`RESULT.json` binds the five package source/metadata files by SHA256. To
regenerate it, pass `--write-receipt /absolute/scratch/path/result.json` to
the same verifier, then compare that generated file. A changed receipt or
source file fails ordinary replay. No network, Git, solver or predecessor
module is needed for direct replay. The citation-only external source in
SOURCES.json is pinned by URL, commit, Git blob and SHA256; it is not a runtime
input or an implicit dependency on an unmerged commit.

The original card's historical positive control was attempted and failed with
`KeyError: 'complex_profile'` in `complex-local-word-ceiling/verify.py` against
the current selected schema. No repair or audit of that old package is claimed.
The source-bound selected-baseline orientation passes. The changed scope and
reason are explicit in TASK.json. No historical/native/Lean/Docker suite or
formal proof-kernel review is part of this contribution.

## Implementation bounds

The theorem is all-dimensional. The public executable accepts 1<=n<=9,
1<=s<=64 charts and at most 128 graph edges. Bases have at most 18 vectors.
Chart intersection contributes at most 576 scalar equations; cycle equations
contribute at most 2,304. Enumeration visits at most 2^18 quotient elements
and retains at most 2^18-1 axes. The exhaustive verifier is separately capped
at ambient dimension four and fixed finite graph/fixture lists. Control flow
has no recursion. Functions stay below 60 lines and checked preconditions and
invariants use exceptions. The registered runs enable warning errors normally
and under -O. No shared runtime or selected source is changed.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates integers
and collections during elimination and enumeration. The scope is this bounded,
one-shot standard-library verifier and enumerator. Enforced dimension/chart/
edge limits bound the live collections; exhaustive endpoint tests exercise
the algorithm rather than a persistent service. A fixed-capacity native port
would be required if steady-operation allocation must be prohibited.
Rule 9 has a bounded test-only dispatch deviation for the eleven explicit
invalid-input callables. Their targets are fixed in `rejection_controls`, and
all must raise ValueError. Production enumeration and transport use direct
calls. No general callback or registration mechanism is provided.

## Open next questions

- Does an actual complete source word have a cycle-coherent multi-chart move
  with a strict full paid-moment gain? Start with a small connected contact
  subgraph and enumerate its kernel-constrained representatives, repricing
  every boundary edge. An exact source graph, phase-aware charts, ownership
  and the complete paid inventory are required.
- Which rank-neutral coordinated moves lie outside edge conjugation? Start
  with one small cycle and compare all endpoint-axis assignments with the
  coherent kernel. A changed boundary contract and complete external-edge
  accounting are required before using those moves in a supplier.

The structured versions of these questions are in TASK.json.

## Credit and scope of originality

This contribution was produced by Nick Petalas. David Ganz / Dugongue,
PR4841 at `6debdcdac8fe1c87958f8cd42ccb7db73c0a0eef`, supplies the inherited
single/pair equivalence and coset representative idea. The new result is the
restricted-axis tuple formula and its complete cycle-coherent graph boundary,
with exact finite corroboration. No priority for classical symplectic geometry
or transvection conjugation is claimed. Cao Yifan / intqwq PR4610, Cinna Davis
PR4690/PR4672 and the retained native-caller contributors supply the contact
optimization setting through that predecessor. Their source credits remain
unchanged. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
