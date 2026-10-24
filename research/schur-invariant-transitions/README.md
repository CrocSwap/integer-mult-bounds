# Split-pivot recurrence and sufficient residual invariants

Prepared by **codyw912**, with substantial **OpenAI Codex (GPT-6 Astra)**
assistance. Apache-2.0. **No new κ and no selected-frontier change.**

This package supplies an intrinsic recurrence, a block-intertwiner certificate
for the seven ordered rank-two residuals, and a sufficient rank-one invariant.
The seven-state numerical table and the total **93,564 / 9,999,360** are credited
to **Mihir Srivastava, PR4689**, not claimed as new numbers. The new contribution
is their derivation through small state transitions without generating GL4 or
GL5, together with a proof that the terminal invariant is sufficient.

**Evidence status:** parent replay on CPython 3.12.13, Linux x86_64, completed
with exit status zero using `python3.12 -B scripts/research_package.py --package
research/schur-invariant-transitions`. Both registered ordinary
`-I -W error -B` and optimized `-I -W error -O -B` commands emitted
`PASS_SCHUR_INVARIANT_TRANSITIONS`; the runner emitted
`PASS_REGISTERED_RESEARCH_PACKAGE`. The replay reproduced 496 initial splits,
172 admitted splits, 784 rank-one pairs, seven exact states, nine rejected
mutations and 93,564/9,999,360 = 2599/277760, including all embedded state and
depth expectations. The expectations remain credited predecessor results;
this is observed regeneration, not a claim to new numerical discoveries.
A separate AI mathematical review found no blocking issue in the recurrence,
stabilizers or invariant-sufficiency proof. Neither that review nor the local
replay constitutes independent human, proof-kernel or hosted approval. The
implementation worker ran no research code, gates, builds or formatters.
Final separate AI static review also reported PASS with no blockers. Parent
reported the shared 331-test suite passing with 11 Windows-specific skips;
this tooling evidence is separate from the mathematical package replay.
No public Discussion claim was posted. Upstream PR creation requires operator
approval; publication status is reported in the handoff.

## Domain and complete-header recurrence

All vector spaces in this package are over F2. Requests remain **ordered**. For
idempotents A,B on V of dimension n, let H(n,k;A,B) count complete ordered bases
M such that both M^-1 A M and M^-1 B M have nonzero leading principal minors of
orders 1 through k. Require 0 <= k <= n; GL0 has order one. Neither commutation
nor an equal-rank hypothesis is needed for the recurrence. An impossible guard
has count zero, in particular when k exceeds either rank.

For a vector a and functional beta satisfying

```
beta(a) = beta(Aa) = beta(Ba) = 1,
W = ker(beta),
A'(x) = Ax + Aa beta(Ax),  B'(x) = Bx + Ba beta(Bx),  x in W,
```

we have the exact, basis-independent recurrence

```
H(n,0;A,B) = |GL_n(F2)| = product_{j=0}^{n-1}(2^n - 2^j),
H(n,k;A,B) = sum_{admitted (a,beta)} H(n-1,k-1;A',B').
```

The minus sign of the ordinary Schur formula equals plus in F2. The maps land
in W because beta(Aa)=beta(Ba)=1. For A, put c=Aa and t=beta(Ax).
Then A(Ax+ct)=Ax+ct since A²=A and Ac=c. Its beta-value is zero, so applying
the same Schur operator again changes nothing: A'²=A'. The argument for B is
identical. In a basis (a,w1,...,w[n-1]) with the w's in W, A has block form
`[[1,R],[C,D]]`, and A' is `D+CR`. Invertible block elimination gives
`rank(A')=rank(A)-1`. This also proves agreement with the intrinsic map.

**Completion and guard proof.** A complete header M determines exactly the
split consisting of its first column a and the first row beta of M^-1.
Conversely, for a fixed split, appending any ordered basis of ker(beta) gives
exactly one header with that first column and inverse first row. Thus its
completion fibre has size |GL[n-1]|, not one and not `2^(n-1)|GL[n-1]|`.
At a unit pivot the determinant of each leading (j+1)-block equals the
corresponding leading j-block determinant of the Schur complement. Partitioning
headers by split and applying this identity proves the recurrence. A basis
change on W bijects its complete headers, so the intrinsic notation is valid.
The recurrence applies at every subsequent, possibly **noncommuting**, residual.

The concrete input is

```
P0 = diag(0,1,0,1,1), Q0 = diag(0,0,1,1,1).
```

Only guard orders 1,2,3 are required. The 31 nonzero first columns have 16
splitting functionals each, giving 496 splits and `496*20160=9999360` complete
headers. After an admitted first split the two residuals have dimension four
and rank two; after the next, dimension three and rank one.

## Rank-two blocks, stabilizers, and certified classification

Matrices use integer **rows**, bit j representing column j. All representatives
have `S=(0,0,4,8)=diag(0_2,I_2)`. In `ker S ⊕ im S`, write
`T=[[E,F],[G,H]]`. An invertible map commuting with S preserves both summands,
so it is exactly `K=diag(U,V)` with U,V in GL2. It stabilizes T exactly when

```
UE=EU, UF=FV, VG=GU, VH=HV.
```

This proves that only 6*6=36 candidates, not GL4, need examination. It also
proves the normalization equivalence criterion: after normalizing S, two T's
are equivalent precisely by this block action.

Here are analytic stabilizer derivations. Let `D=diag(0,1)` and let
`J=e2 e1^t` on F2². In F2 a one-dimensional invertible scalar is one.

* State 1: E=0, H=I, F=G=0. Every U,V works: 36.
* State 2: E=0, H=I, F=0, G=J. The one nontrivial equation is
  `V e2 e1^t = e2 e1^t U`. Equality of nonzero rank-one tensors forces
  `V e2=e2` and `e1^t U=e1^t`; each has two choices: 4.
* State 3: E=H=D and F=G=0. Centralizing D preserves its two distinct
  eigenlines, hence U=V=I: 1.
* State 4: E=H=D, F=0, G=e1 e2^t. The preceding diagonal equations already
  force U=V=I, which satisfies the off-diagonal equation: 1.
* State 5: E=0, H=I, G=0, F=J. Now `U e2=e2` and `e1^t V=e1^t`:
  again 2*2=4.
* State 6: E=0, H=I, F=G=J. Both U and V must fix e2 and its annihilating
  functional e1^t, hence each is `[[1,0],[c,1]]`, c in F2: 4.
* State 7: E=H=D, G=0, F=J. Again U=V=I: 1.

The implementation corroborates these constraints on the 36 GL2² pairs per
representative and prints every stabilizer. It builds only their small **block
orbits**, checking these are pairwise disjoint. For each of the admitted initial
splits, it computes a deterministic basis C of `ker S' ⊕ im S'`, finds a block K
with `C^-1 T' C = K T_i K^-1`, and checks the explicit witness L=CK:

```
S' L = L S,   T' L = L T_i,   rank(L)=4.
```

All 172 splits, their state assignments, and these invertible witnesses are
printed. Unmatched residuals or overlaps fail; no rank-signature heuristic is
used to force membership. This is completeness for the initial split domain,
**not** a classification of every pair of rank-two projectors in dimension four.

## Sufficient rank-one invariant: proof, not a guess

Over F2, each nonzero rank-one idempotent has a unique factorization
`R=u phi`, with u and phi nonzero and phi(u)=1. For an ordered pair
`(R,T)=(u phi,v psi)` on an n-dimensional space use

```
I(R,T) = ([u=v], [phi=psi], phi(v), psi(u)), together with n.
```

These data are necessary under simultaneous conjugation. They are also
**sufficient**. Define `X:F2² -> V` with columns u,v and `Y:V -> F2²` with rows
phi,psi. The first flag determines ker X (zero or span(1,1)). The second flag
determines im Y (F2² or span(1,1)). The two cross-values determine
`YX=[[1,phi(v)],[psi(u),1]]`.

Here is the full extension argument, including the potentially missing datum.
Consider two systems X,Y and X',Y' with these three data equal and ambient
dimensions equal. Let L=im X, K=ker Y, and similarly L',K'. Equality of ker X
makes `f0(Xz)=X'z` a well-defined isomorphism L->L'. Equality of YX gives
`Y'f0=Y|L`, so f0 sends L∩K isomorphically onto L'∩K'. Equality of im Y and
ambient dimensions gives dim K=dim K'. Extend this restriction to any
isomorphism fK:K->K'. The maps f0,fK agree on the intersection and therefore
combine to an isomorphism f1:L+K -> L'+K'. It satisfies `Y'f1=Y`.
Finally choose a basis of a complement of Y(L) in the **common** im Y, and
choose a lift in each ambient space for every vector of that basis. Those lifts
complement L+K and L'+K', respectively: the induced maps from these quotients
to im Y/Y(L) are isomorphisms. Mapping corresponding lifts extends f1 to an
invertible f on V with `fX=X'` and `Y'f=Y`. Consequently
`f(u phi)=(u' phi')f` and `f(v psi)=(v' psi')f`.

Thus no extra datum is missing: the intersection information is already fixed
by ker X, im Y and YX. This is an all-dimension binary proof, not a consequence
of the finite terminal census. Dimension must be retained. For example, when
both flags are zero and both cross-values are one, rank(YX)=1; in dimension two
X and Y would both be invertible, an impossibility. Dimension three admits it.
When either equality flag is one both cross-values must be one. Hence in
**dimension three** there are exactly seven possibilities, all realized below.

## Terminal counts from consistent linear constraints

For rank-one requests an admitted split requires
`phi(a)=psi(a)=1` and `beta(a)=beta(u)=beta(v)=1`. For fixed a the last three
constraints are consistent iff every relation among a,u,v has even coefficient
sum. Equivalently the coefficient and augmented matrices have equal ranks.
Thus the exact number of terminal splits is

```
g(R,T) = sum_{a: phi(a)=psi(a)=1}
         [consistent a,u,v -> 1] * 2^(n-rank(a,u,v)),
H(3,1;R,T) = 6*g(R,T).
```

The zero vector never satisfies the first conditions. In particular a=u+v
with u,v distinct gives the odd relation a+u+v=0 and contributes **zero**.
Dropping consistency is not a valid use of the rank formula.

The following representatives give the terminal class table. Vector and
functional integers have the same least-significant-bit coordinate convention.
The last four rows list the distinct cross-pairings in order.

| Invariant | (u,phi,v,psi) | g | Derivation in dimension three |
|---|---|---:|---|
| 1111 | (1,1,1,1) | 10 | a=u contributes 4; three other a contribute 2 each |
| 1011 | (1,1,1,3) | 6 | a=u contributes 4; the other allowed a contributes 2 |
| 0111 | (1,1,3,1) | 6 | a=u,v contribute 2 each; two other a contribute 1 |
| 0000 | (1,1,2,2) | 1 | a=3 is inconsistent; a=7 contributes 1 |
| 0001 | (1,1,2,3) | 3 | a=1 contributes 2; a=5 contributes 1 |
| 0010 | (1,3,2,2) | 3 | a=2 contributes 2; a=6 contributes 1 |
| 0011 | (1,3,2,7) | 4 | a=1,2 each contribute 2 |

The verifier constructs this table and uses invariant lookup in the recurrence.
As an independent finite corroboration, all 28²=784 ordered rank-one pairs are
checked against literal `(a,beta)` split constraints, with no basis enumeration.
Every next-pivot transition is counted with multiplicity; deterministic stdout
contains all seven terminal-type entries, including zeros, for each state.
The ordered-pair populations in the displayed class order are respectively
28,84,84,168,168,168,84, also embedded as exact targets. The seven H(4,2)
values are additionally compared against direct recursive split evaluation
with the GL-order zero-guard base case; memoization is in-memory only.


## Expected state and guard-depth tables

The T rows, b,z,o,f, header weights and full guards below are Mihir's PR4689
results. Here m counts the next admitted splits, G sums their terminal g-values,
and `H(4,2)=6G`. These m,G and depth targets are the predecessor's depth data
and arithmetic consequences of its table, reproduced by the parent replay.

| State | T rows | b | z | m | G | o=20160/z | f=6G/z | Header weight | Full guards |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | (0,0,4,8) | 1 | 36 | 60 | 600 | 560 | 100 | 20160 | 3600 |
| 2 | (0,0,4,9) | 3 | 4 | 44 | 312 | 5040 | 468 | 60480 | 5616 |
| 3 | (0,2,0,8) | 126 | 1 | 30 | 61 | 20160 | 366 | 2540160 | 46116 |
| 4 | (0,2,2,8) | 18 | 1 | 34 | 136 | 20160 | 816 | 362880 | 14688 |
| 5 | (0,4,4,8) | 3 | 4 | 44 | 312 | 5040 | 468 | 60480 | 5616 |
| 6 | (0,4,4,9) | 3 | 4 | 36 | 180 | 5040 | 270 | 60480 | 3240 |
| 7 | (0,6,0,8) | 18 | 1 | 34 | 136 | 20160 | 816 | 362880 | 14688 |

After the initial admitted guard, let depth d=0,1,2 be the number of further
common guards passed. A next split has |GL3|=168 unrestricted completions,
whereas a successful two-step continuation has |GL2|=6 completions. Conjugation
by GL4 has uniform fibre z onto its orbit (orbit-stabilizer theorem). Therefore

```
d0=(20160-168m)/z, d1=(168m-6G)/z, d2=6G/z,
headers per orbit element = b*z,
full guards in initial state = b*6G.
```

| State | d0 | d1 | d2 |
|---|---:|---:|---:|
| 1 | 280 | 180 | 100 |
| 2 | 3192 | 1380 | 468 |
| 3 | 15120 | 4674 | 366 |
| 4 | 14448 | 4896 | 816 |
| 5 | 3192 | 1380 | 468 |
| 6 | 3528 | 1242 | 270 |
| 7 | 14448 | 4896 | 816 |

Summing gives 172 first-admitted splits and 3,467,520 first-guard headers, but
only 93,564 full-guard headers. The full fraction is 2599/277760. State 6 retains
the credited one-block sharp-header count 60,480 and full continuation 3,240.
No uniform weighting of states or orbit elements across distinct initial
fibres is assumed.

## Reproduction, controls, and boundaries

Python 3.12 standard library, five files, no third-party imports, external reads,
pending-head objects, network calls, subprocesses, persistent caches or write mode in the
scientific verifier. Direct exported-package execution needs no Git:

```sh
python3.12 -I -W error -B research/schur-invariant-transitions/verify.py
python3.12 -I -W error -O -B research/schur-invariant-transitions/verify.py
```

Each command prints deterministic JSON followed by
`PASS_SCHUR_INVARIANT_TRANSITIONS` only after every explicit check succeeds.
The package runner also checks historical source metadata:

```sh
python3.12 -B scripts/research_package.py --package research/schur-invariant-transitions
```

VERIFY.json proposes a 60-second cap per run, not a measured runtime. The
scientific domain is 496 initial splits, seven 120-split next domains, 36 block
changes per representative, and 784 terminal pairs, plus direct recursive
split evaluation of the seven H(4,2) representatives. There is no GL4/GL5
generator, no 4x4 raw-matrix census, no native compiler, Lean or selected cold
replay. All failure checks use exceptions rather than disabled-by-`-O` asserts.
Permanent mutation controls reject missing GL2/GL4 completion factors,
commutator-only and product/sum/commutator-rank identification, transposition,
unordered terminal requests, ignored odd relations, omitted Schur correction,
and replacing full guards by first-guard counts. States 1 and 3 have equal
commutator rank but different continuations; states 2 and 5 share the listed
ranks yet are distinct ordered orbits. Transposition exchanges 2/5 and 4/7.

The recurrence is proved generally for binary idempotents; the seven-state
certificate is only for the displayed sector profile (1,1,1,2). No larger-field
invariant classification is claimed. The binary event is not admission into
the retained odd-q executable normalizer. Physical header selection/emission,
reads, restoration, storage, stock, dispatch and the complete consumer bill
remain unpriced, not zero. No formal proof-kernel or independent human theorem
acceptance is claimed.

## Provenance, overlap, and credit

Canonical base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7,
selected κ=60403/20000000=0.00302015 from #4470. TASK.json explicitly changes the
`formal-interface-lemma` card to this algebraic side result; it neither discharges
the selected all-size interface obligations nor repeats stale endpoint arithmetic.
SOURCES.json pins only historical canonical-main provenance; VERIFY.json has no
external live inputs. Pending works below are immutable **citations**, not Git
ancestry or executable dependencies. Embedded numeric expectations are openly
transcribed fixtures, not runtime-authenticated remote files.

* **Mihir Srivastava**, substantial OpenAI Codex assistance, [PR4689](https://github.com/CrocSwap/integer-mult-bounds/pull/4689),
  head `3a72fbad148294aa9ca7f900a48dbb10e64232be`:
  [seven-state table and proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3a72fbad148294aa9ca7f900a48dbb10e64232be/research/schur-residual-orbits/README.md),
  [depth receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/3a72fbad148294aa9ca7f900a48dbb10e64232be/research/schur-residual-orbits/RESULT.json).
  All seven numerical states and the total retain this attribution.
* **ssafwann**, substantial OpenAI Codex assistance, [PR4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678),
  head `af9cf805c501e4e9e947c98c0b97b2281b6b6e97`: one-block counts, equal
  completion fibres, profile and [released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653#discussioncomment-19126925).
  [PR4671](https://github.com/CrocSwap/integer-mult-bounds/pull/4671), head
  `8d2e3bc76aa7d43e5c629daaf1e72d4dd5a81ed9`, supplies the sector criterion.
* **Nick Petalas**, [PR4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597),
  head `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`: block Schur bound and orbit
  question; retained [scalar Schur proof](../schur-commutator-criterion/README.md)
  supplies residual idempotency/rank and the earlier header lineage.
* **Ryanson Jonathan**, substantial Claude Code (Claude Opus 5.5) assistance:
  [full-guard convention and separate-family census](../full-guard-header-census/README.md).
  Retain **lee-phys**'s binary sharpness/dimension contributions, **Cinna Davis**'s
  PR4100 BIT request context and its normalizer lineage (source527, commdata2338,
  Jose Manuel). No predecessor code is imported or copied into this verifier.

At the final parent checkpoint, canonical origin/main remained
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. The refreshed overlap snapshot
covered 469 open PRs at 2026-10-22T16:48:00.710568+00:00 and 3,624 discussion
records at 2026-10-22T16:48:34.859558+00:00, with complete pagination. All 5,860
tracked local records were covered; the local snapshot had 5,864 records,
including four from this contribution work. Direct predecessor heads #4689,
#4678, #4671 and #4597 remained unchanged from the cited pins. Coverage does
not include arbitrary remote diffs, closed remote PR bodies or unpublished work;
no novelty or reservation over those domains is asserted. No public Discussion
claim was posted. Upstream PR creation requires operator approval; publication
status is reported in the handoff.

## Open next questions

1. **Can a sufficient higher-rank state invariant replace block-orbit matching?**
   This is relevant to scalable recursion beyond one binary profile. First derive
   the representation data of two image/kernel decompositions and test proposed
   invariants against the explicit witnesses here. Block intertwiners certify
   this finite domain but are not a general classification; that is the blocker.
2. **Can the state recurrence support an admitted, paid header cover?** The finite
   full-guard probability alone supplies no executable cost bound. First state
   the actual caller's field and header-selection contract and price emission,
   physical reads and restoration. Odd-q admission and the complete consumer bill
   remain separate blockers. No expansion or follow-up claim is held here.
