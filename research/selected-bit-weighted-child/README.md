# One selected BIT residual lowered to a contiguous weighted child

The first unhosted rank-42 idle residual in selected PR589 has an executable generic local-ring lowering to **one contiguous 42f-atom weighted child**. The implementation emits unit lower ADD normalizers, a lower cross-bank shear, the child weight descriptor, and inverse adapters. It checks the whole two-bank operator, including inactive coordinates.

A concrete descriptor boundary emerges: two GL64 parent charts with the same low residue modulo 5 require child pivots **1 and 11 modulo 25**. Keeping only the parent's low matrix preserves the rank and call shape but changes the operation. The descriptor needs parent-dependent pivots retained or computed from the full chart; the low matrix alone is insufficient. This is a counterexample to a weakened interface, not a defect found in a selected compiler.

This is a source-bound algebraic compiler component and scoped proof. It supplies no physical routing, bad-class fallback, complete selected compiler, new stock coefficient, or new kappa.

## Selected object and handoff

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The selected assembly binds PR589 at `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46` through receipt blob `e293ddc557742637f9f679f083a1a282d87b1b13`. The selected manifest also binds the frozen nine-stage hosting selection. Exact sources are in [SOURCES.json](SOURCES.json).

The pinned geometry's idle child 6 advances pair 0 from level 2 to level 8 and acts on exterior axes 22 through 63. The hosting allocator orders patterns by decreasing occupied width: 213 copies receive five width-8 helpers and nine receive none. The first full rank-42 remainder is `(child,copy)=(6,213)`, replica 0, side 1, port 102. Those nine copies across 32 replicas account for all 288 rank-42 children. Its projector is

```
P0 = diag(0_22, I_42).
```

There is no local q-perp component, so this projector is independent of the port's root basis. The checker reconstructs the selection from the geometry rule and hosting patterns; it imports no earlier hosting or projector-ledger verifier.

The claim is in [discussion #2114](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114). Relevant predecessor heads are:

| Work | Exact head | Relationship |
|---|---|---|
| [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084) | `8001a23b003bec5dff5e61edec907b652c475932` | Conditional selected BIT stock; compiler remains open |
| [PR2097](https://github.com/CrocSwap/integer-mult-bounds/pull/2097) | `1d3ee0926656d5260c6cb1c0b81964ffe9fe1377` | Fresh-field counting under dependency hypotheses |
| [PR2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120) | `378593574261e0b0915e7e8a83147aa640274fc8` | Sharper stock bound; asks for selected field dependency |
| [PR2140](https://github.com/CrocSwap/integer-mult-bounds/pull/2140) | `7ec858702da04d02748a5c05d439f602741a869a` | Fixed port q-adic row route; leaves residual/child descriptors open |

The generic normal-form theorem and contiguous index rule already occur in [three-stage-cover-bit.tex](../five-stage-source527-banks/proof/three-stage-cover-bit.tex), sections “One weighted child on a generic residue class” and “Atom contract and common endpoint”. They retain their authorship. This contribution adds the selected rank-42 binding, executable ordered lowering, independent direct-operator checks, and high-field descriptor counterexample.

## Exact normal form

Let q be an odd prime, w>=1, and R=Z/q^w Z. Let g be any element of GL64(R), and set P=g P0 g^-1. Let C reverse the 64 coarse coordinates. Restrict to the **generic class** where successive northeast pivots of P C are units. No pivot permutation or pivot scaling is granted. The executable rejects nonunit pivots, including nonzero multiples of q; it does not implement fallback.

Unnormalized lower row and column additions give unit lower L,R0 with

```
L (P C) R0 = E D F^t,
E=(e_0,...,e_41), F=(e_63,...,e_22), D=diag(p_0,...,p_41).
```

Lower row additions clear below pivot (k,63-k); lower column additions clear to its left. They preserve earlier pivot rows and columns. Every pivot is a unit. The remaining block vanishes because the unit 42-by-42 minor and split rank 42 give a factorization through that minor. This argument takes place over the local ring. The implementation also checks the complete remaining block and full split factorization.

For arbitrary diagonal unit weights A define the retained weighted residual

```
G_A = diag(A,I) [[I-P, P C], [C P, I-C P C]] diag(A^-1,I).
```

With Q=diag(L,R0^-1), write

```
Q G_I Q^-1 - I = [E; B] [A0, D F^t].
```

The pivot minor supplies a left inverse of [E;B] and a right inverse of the second factor. Involutivity implies `A0 E + D F^t B = -2I`. The retained formula

```
K = -(B+F D^-1)E^t + F D^-1 A0 (I-EE^t),
S = [[I,0],[K,I]]
```

gives, by ordered multiplication,

```
S Q G_I Q^-1 S^-1 = [[I-EE^t, E D F^t],
                     [F D^-1 E^t, I-FF^t]].
```

For weights, replace L by `L_A=A L A^-1`, K by `K_A=K A^-1`, and each pivot by `d_k=A[k]*p_k`; R0 is unchanged. These follow by diagonal conjugation, without commuting a general matrix past A. The emitted program executes:

1. H <- L_A H and Dtail <- R0^-1 Dtail, using the recorded ADDs.
2. Dtail <- Dtail + K_A H.
3. One weighted reversed interchange on the first 42 head and last 42 tail coordinates, fixing the other 44 coordinates.
4. The inverse cross shear and inverse intrabank adapters.

The complete program is G_A on arbitrary dirty inputs. Inactive coordinates are fixed at the middle boundary; the outer adapters retain their required action in original coordinates and cannot be omitted.

## Atom order, descriptor and spectators

For n=64f, head atom if+j is in column j; its paired tail column is f-1-j. Apply adapters columnwise with `A_j=diag(A[if+j])`. Execute the middle as one call on the contiguous head prefix and tail suffix, each of length 42f, with

```
A_child[kf+j] = A[kf+j] * p_k,  0<=k<42, 0<=j<f.
```

Head position kf+j pairs with global tail position `64f-1-(kf+j)`. This is the full 42f reversal, since `C_42 tensor C_f=C_(42f)`. Column-major weights and omission of the within-column tail reversal both fail the differential checks. There is no gather, interleaving, extra child or pivot-normalization pass.

Parent weights may depend on older ancestors and atom index, but not on head/data values or fresh fields. Compilation reads the complete current parent chart and those weights. At the child boundary that parent chart is an ancestor. The child descriptor takes frozen parent values and its atom index, with no child-current or unused-stock argument. Emitted ADDs target head/tail atoms only. Extending this program by the identity on the parent row, older ancestors and unused stock preserves each complete spectator for every initial value. No zero spectator assumption is used.

This is an algebraic read/write property of this program. It does not certify physical stream execution of prefix-controlled ADDs, complete padded invocation cylinders, or a completed ordinary leaf's internal borrowing. Parent weight evaluation and those global source interfaces remain inherited.

If the normalizers have nL,nR ADDs and K has nK nonzero entries, the complete adapters contain `2f*(nL+nR+nK)` coordinate ADD updates, plus one rank-42f child. Each coefficient multiplication belongs to its ring ADD and is not declared free physical work. Here nL,nR<=1785 and nK<=4096, giving the loose bound 15332f. [RESULT.json](RESULT.json) records exact counts. Converting them to the retained ordinary-operation toll remains open; no moment or stock coefficient changes.

## High-field counterexample

Permute the selected active axes first, then modify only coordinates 0 and 42. Modulo 25 compare the determinant-one blocks

```
g_low  = [[1,1],[ 0, 1]],   P_low  = [[ 1,24],[ 0, 0]],
g_high = [[1,1],[10,11]],   P_high = [[11,24],[10,15]].
```

The displayed projectors are the conjugates of diag(1,0). Both charts have the same reduction modulo 5. Embed the block in the selected rank-42 projector, leaving 41 other active and 21 inactive coordinates unchanged. Both are generic: first pivot 1 or 11, all later pivots 1. For unit parent weights the first child multiplier must therefore be 1 or 11. Substitution of low-only pivots in the otherwise correct high-chart adapters fails complete equality.

The source already permits full-parent dependence; this example makes its necessity explicit for the selected maximal child. Conversely, choosing a factor 1 or 2 from a fresh child bit changes the child action on a tail basis input even without writing the row coordinate. Row preservation alone cannot establish descriptor independence; such an adaptive rule is excluded here.

## Reproduce and limits

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -B research/selected-bit-weighted-child/verify.py
python3 -I -O -B research/selected-bit-weighted-child/test_child.py
python3 scripts/research_package.py --package research/selected-bit-weighted-child
```

Expected verifier output:

```
PASS_SELECTED_BIT_WEIGHTED_CHILD rank=42 cases=10 basis=768 controls=10 no_new_kappa
```

The registered command also prints PASS_REGISTERED_RESEARCH_PACKAGE. Add `--check-only` for metadata/source pins alone.

Nine fixtures use q=5,7,2^89-1 and w=1,2,3. A Lucas-Lehmer check certifies the last prime, which exceeds 2^80; this does not certify eligibility for every other selected denominator or minor. These nine use one guaranteed generic low-class construction; a tenth fixture at q=101,w=2 uses a different dense low class selected from a fixed list of at most 32 charts. Every fixture checks all 128 columns of the weighted operator. At q=5,w=2 the ADD interpreter is compared with a separate direct D_P formula on all 768 basis columns for f=1,2,3 and dirty vectors. Other fixtures check dirty vectors at each f. The small-ring suite additionally enumerates all 3888 GL2(Z/9) charts and their 108 distinct rank-one projectors: all 63 generic projectors pass all basis tests for f=1,2,3, and all 45 nongeneric projectors reject. These finite checks support the implementation; the ordered proof supplies the all-f/all-width statement.

Sources are authenticated by SHA256 and Git blob before use. A freshly computed receipt must equal the complete committed JSON. `--write-result PATH` creates exclusively. No selected record, source, or frozen predecessor is rewritten, and no predecessor executable is imported.

The executable bounds per-bank dimension by 64, compiler width by 8, and interpreter f by 3. It uses Python dynamic allocation and integer arithmetic. Proof quantifiers exceed these finite bounds. No full cold replay, formal-kernel proof, independent human review, native precision/tape proof, or hosted CI success is claimed. Transferring the selected physical recipe to the all-size GL64 cover remains conditional.

## Open next questions

1. Can the emitted prefix-controlled ADDs receive a complete ordinary-call and tape bill? Begin with one nonconstant K_A coefficient, preserving the full parent high field and unused quotient. The physical ordered-affine implementation and internally borrowing ordinary leaf remain blockers.
2. Can the retained unit-pivot fallback be emitted for a nongeneric selected residual with the same descriptor dependency? A [complementary fallback claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114#discussioncomment-18934129) by Ross Richardson became active during this work. Coordinate with it and compare the two interfaces on the same selected projector, checking the full 128D operator and charged child list. No completed artifact from that claim is used here. Treating residue-zero entries as zero modulo q^w is invalid.

Structured questions are in [TASK.json](TASK.json).

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance. New material is Apache-2.0. The weighted-child algebra, fresh-field contract and contiguous index rule belong to the retained three-stage-cover framework, including eumemic's source527 packaging and its credited lineage. Zhihao Chen supplied the nine-stage geometry; DreamingOfClouds supplied PR545/PR589's selected BIT pipeline on eumemic's base, with the retained hosting/compiler lineage. Adam Gall supplied PR2084/PR2097, Nick Petalas PR2120/PR2140, Josie Elliston PR1956/PR1965, and ToikY PR1990. Rohan Arun's PR1094 and Jeremy Kothe's preceding assembly bind the selected source. This account's PR1307 and PR1421 provide earlier hosting and ledger audits; their results and executables are not reintroduced as new evidence.
