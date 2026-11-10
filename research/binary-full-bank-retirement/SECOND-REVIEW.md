# Worker C independent review: full-bank binary retirement

Prepared for Jerry Chen / [@CubeJerry](https://github.com/CubeJerry), with substantial OpenAI assistance. Apache-2.0. This is a separate-agent mathematical and executable review within the same AI-assisted session; it is not independent human or formal-kernel verification.

**Conclusion:** the full-bank ordinary obstruction, forward-plus-restoration thin-query debt, mixed L/SL extension and strict price loss are valid under the stated common-S algebra, ordinary F-valued source/target controls, fixed active history and newly supplied rank-one thin-query alphabet. The one-channel and two-channel escape endpoints also check. No new κ or all-size framework discharge follows.

Reviewed files in `research/binary-full-bank-retirement/`:

| File | SHA256 |
| --- | --- |
| PROOF.md | `e3113f38f71ffff7cd5b8cc6666cdee7bb0ae8b7e1f775e815c1e1e9f2876d35` |
| verify.py | `0236916d4b76f8205300d0d35ee0b270c1c3ed0eb794da634c25bfd72da4ca1e` |
| rank_controls.py | `f1d6a92f1c49f1b4e1d6ffc7dfde358f06bb3ff3a1b954a97c2a3d3f3aeb881c` |

These hashes identify the proof before the lead's scope-wording clarification. The boundaries below must remain in the final version.

## Endpoint forcing and arbitrary-K obstruction

For old target LR, coefficient comparison at the full binary endpoint forces the eligible ordinary input column into X and the eligible ordinary output pullback into Y. Their dual pairing is zero. For old target SLR, both lie in the A,B auxiliary bank. Thus ordinary mixing across the four banks does not create additional eligible scalar-target channels.

For prefix L, comparison in the active Y and X rows successively forces U_B=0 and U_A=0. For prefix SL, the constant part of the active X row forces U_B=0. The general cut-row formula has X coefficient W1, A coefficient SL p−S W1 and B coefficient L p−SL q. The X identity sets W1=0; the B identity, with ordinary p,q,D_B, sets p=D_A=0. Hence D U=0. The deduction does not constrain K to a projector, an invertible map or an S-independent matrix. Granting arbitrary K strengthens this necessary-condition obstruction; it does not assert that every K admits the required full endpoint.

## Mixed-prefix rank lemma

I independently checked the mixed L/SL blocks. After ordering r0 pure-L channels and r1 SL channels, the relevant odd blocks are

```
M0 = [D_A0, -D_B0],      N0 = [U_A0; -U_B0],
M1 = [0, D_A1],          N1 = [U_B1; 0].
```

The complete dual pairing gives M0 N0=I_r0. Direct multiplication gives M1 N1=0. The SL diagonal block of D U=I gives

`r1 <= rank(D_A1)+rank(U_B1) = rank(M1)+rank(N1)`.

For M=[M0;M1] and N=[N0,N1], choose a row-space complement of M1 inside the row space of M, and a column-space complement of N1 inside the column space of N. Then

`M0=A M1+M0'`, with `rank(M0')<=rank(M)-rank(M1)`,

and

`N0=N1 B+N0'`, with `rank(N0')<=rank(N)-rank(N1)`.

Using M1 N1=0,

`I_r0=A M1 N0'+M0' N0`.

Subadditivity of rank implies

`r0+rank(M1)+rank(N1) <= rank(M)+rank(N)`.

Combining these gives

`r0+r1 <= rank(M)+rank(N) <= rank(G1)+rank(H1) <= k_forward+k_restore`.

The last inequality follows because invertible ordinary multiplication preserves odd-part rank, while a rank-one thin S-query changes the odd part by a rank-one matrix. This uses the free basis 1,S, not merely S=±1 substitution, and remains valid in characteristic two. It correctly charges both the basis and its inverse. The two-channel escape disproves an unjustified stronger forward-only debt.

## Sharpness endpoints and price

I manually recomputed the two-channel cut basis with K=L I. Its four fields are exactly

`(SL A, SL B, L(X+S Y), L Y)`.

Swap the first two with genuinely fresh E,F, apply the inverse basis, apply the remaining right-body operations and binary tail, then swap the final auxiliary outputs with E,F. The result is

`(LR(X+S Y), LR Y, SL A, SL B, R E, R F)`.

The one-channel version with K=diag(L,LR) gives old-A target SL, old-B target SLR and new-E target R. Both versions use one forward query and one restoration query; the two-channel version attains total-query lower bound r=2.

For positive a,b and 0<t<1, strict concavity makes H(x+1)−H(x) strictly decreasing and strictly less than H(1)=1 when x>0. Thus both fragment orientations satisfy `0<g(a,b)<1` and `0<g(b,a)<1`. Summing r gains gives less than r, while the new thin queries cost at least r. Unchanged native/helper work cancels, and granting ordinary routing and restoration free makes the comparison more optimistic. This is a valid strict loss for the stipulated added-thin-query model. Changed productive-helper contracts and packed oracles remain outside that price proof.

## Executed checks

The following read-only commands passed under Python 3.12.14:

```sh
python3 -I -B research/binary-full-bank-retirement/verify.py
python3 -I -B research/binary-full-bank-retirement/rank_controls.py
```

The endpoint verifier reported certificate SHA256 `80cd36fffbb23cb186d6d1a36764e32805787a20a2c7edf53c2bd5aff41c6134`. It reconstructs the unchanged endpoint, both changed arbitrary-input endpoints and the two-channel cut prefix, and rejects the specified restoration, fresh-routing and final-association mutants. The rank controls checked 17,391 scalar-block fixtures over F2 and rejected both missing-premise controls. These finite tests support the implementation; they do not substitute for the universal complement-space argument.

## Scope wording required in the final package

The physical factor 104 should be described as a **portwise instantiation of the common-S model**. The displayed theorem does not prove the same bound for arbitrary cross-port coupling among distinct physical central operators S_q.

Ordinary matrices are explicitly F-valued and independent of S,L,R. If physical λ/translation controls are intended to be included, their reduction to this ordinary-control model needs to be stated. A formal central-character decomposition may cover scalar/λ controls that preserve the relevant Q² sectors, but arbitrary physical permutations mixing those sectors are not automatically included. Retaining the narrower explicit ordinary-control scope is sufficient.

The fixed completed-left active history, ordinary old source/target bases, common old scalar target and added rank-one thin-query alphabet are substantive hypotheses. Existing query reuse, a changed history or suffix, different body monomials, alternative target contracts, packed operators and changed productive helper boundaries remain outside the argument. The five selected framework assumptions retain their status.
