# Central action after an identity-block Schur deletion

**Scoped all-field algebraic proof with finite exact corroboration; no new κ.**
Prepared for ssafwann with substantial OpenAI Codex (gpt-6-astra) assistance,
by one agent. Apache-2.0.

Nick Petalas's [#4801](https://github.com/CrocSwap/integer-mult-bounds/pull/4801)
proves a central-spectrum law for a scalar identity pivot and explicitly asks
for the ordered block replacement. This package answers that question. For a
common identity block of size d and compressed product H, the replacement is
an **intertwiner with two copies of Θ = 2H−H²**, rather than a scalar equation
between matrices of different sizes. When the Schur commutator has rank 2d,
this gives the exact restricted operator, including its nonsemisimple data.

## Theorem and domain

Let F be any field, d >= 1, n > d, and let P,Q in M_n(F) be commuting
idempotents. Both leading d-by-d blocks must be I_d. Write

```text
P = [I R; C D],   Q = [I L; E F0],   H = (PQ)11,
S = D−CR,        T = F0−EL,         K = ST−TS,
Z = (S−T)²,      J = H(I−H),        Θ = 2H−H².
```

No symmetry, invertibility of H, semisimplicity, characteristic restriction,
or maximal-rank hypothesis is imposed initially. Put G=(PQ)21 and define

```text
A = [G−EH, C−E] : F^(2d) -> F^(n−d),
U_H = [I−H  −I; −J  H],   V_H = [I  I; 0  0].
```

Then the ordered identities are

```text
S A = A U_H,     T A = A V_H,
Z A = A diag(Θ,Θ).                                      (1)
```

For every polynomial p in F[t] satisfying p(Θ)=0,

```text
p(Z) K = 0,     Z(Z−I) p(Z) = 0.                        (2)
```

In particular, with m_Θ the minimal polynomial of Θ, the minimal polynomial
of Z divides `t(t−1)m_Θ(t)`. One may instead use the characteristic polynomial
of Θ to get a generally weaker annihilator of degree d+2. Repeated factors
must be retained. Over an algebraic closure the spectrum of Z is contained
in `{0,1} ∪ spectrum(Θ)`; this does not imply diagonalizability.

If additionally **rank K = 2d**, then im K = im A and A is an isomorphism
onto that subspace. Consequently:

- the ordered pair restricted to im K is simultaneously similar to `(U_H,V_H)`;
- `Z|im K` is similar to `Θ ⊕ Θ`;
- its minimal polynomial is exactly m_Θ, and its characteristic polynomial
  is exactly the square of the characteristic polynomial of Θ;
- over a splitting field, each Jordan block of Θ occurs twice in `Z|im K`.

These conclusions concern the indicated invariant subspace, not all n−d
residual coordinates. They do not classify the entire residual pair or count
headers. The dimension minimum is the credited #4671/#4746 result, not a new
claim here. At d=1, (2) recovers #4801's scalar law with Θ=h(2−h).

## Proof, with ordered products retained

Let i:F^d -> F^n and π:F^n -> F^d be the coordinate inclusion and projection.
Thus πi=πPi=πQi=I and πPQi=H. Define the full-space Schur lifts

```text
P̂ = P−PiπP,     Q̂ = Q−QiπQ.
```

In the original block coordinates these are `diag(0,S)` and `diag(0,T)`.
For example P̂i=0 and πP̂=0, and expanding P̂² using P²=P and πPi=I gives
P̂²=P̂. Thus S,T are idempotents. The same facts hold for Q̂.

Define two block columns and a block row:

```text
a = PQi−QiH,     b = (P−Q)i,
Â = [a,b],
B̂ = [π(P−Q); −πPQ+HπQ].
```

Their top d rows / first d columns vanish respectively: πÂ=0 and B̂i=0.
The following expansion gives the identity-pivot specialization of Petalas's
ordered Schur factorization (#4597), also used in #4671/#4746:

```text
[P̂,Q̂] = PQiπ(P−Q) − (P−Q)iπPQ + PiHπQ − QiHπP = ÂB̂.
```

Indeed expand `(P−PiπP)(Q−QiπQ)` and its reversed product, cancel PQ=QP,
and use πPQi=πQPi=H. Removing the zero first blocks gives `K=AB`, where
`B=[R−L; −(PQ)12+HL]`. This derivation does not commute any rectangular factors.

Now compute the four actions directly:

```text
P̂a = PQi(I−H) − Pi(H−H²) = a(I−H)−bJ,
P̂b = PiH−PQi              = −a+bH,
Q̂a = a,
Q̂b = a.                                                   (3)
```

For example πPa=H−H² and πQa=0; πPb=I−H and πQb=H−I.
These four identities prove the first two equations of (1). Their difference
has the right-acting block matrix

```text
U_H−V_H = [−H  −2I; −J  H].
```

Here J=H−H² is a polynomial in H, so HJ=JH. Squaring this particular matrix,
with its order retained, gives

```text
(U_H−V_H)² = [H²+2J  0; 0  H²+2J] = diag(Θ,Θ).
```

This proves the last equation of (1). The commutation used in this step is
between two polynomials in H; it is not an assumption on arbitrary original
matrix blocks. Repeated application and linear combination give
`p(Z)A = A diag(p(Θ),p(Θ))`. Multiplying by B proves the first equation of (2).

For any two idempotents S,T, with no commutation assumption on them,

```text
Z = S+T−ST−TS,
ZS = SZ = S−STS,       ZT = TZ = T−TST,
K² = Z²−Z.                                                (4)
```

Each line follows by expansion and S²=S,T²=T. These central identities are
credited to the existing projector/Schur lineage, especially Ryanson
Jonathan #4609 and Petalas #4801. Multiplying `p(Z)K=0` by K and using (4)
proves the second equation of (2), since all polynomial factors in Z commute.

Finally K=AB implies im K ⊆ im A and rank K <= rank A <= 2d. Under the stated
sharpness hypothesis every inequality is equality. A then identifies F^(2d)
with im K, and (1) gives both restricted similarities. The minimal polynomial,
characteristic polynomial and Jordan statements follow from this actual
isomorphism, not merely from an annihilating polynomial. This completes the
all-field proof, including singular and nonsemisimple H.

## Attained repeated roots and an indispensable endpoint factor

Take the nilpotent three-by-three Jordan block

```text
H = [0 1 0; 0 0 1; 0 0 0].
```

The credited sector construction below produces full commuting pairs with
n=13, d=3 and rank K=6, over both F2 and F3.

| Field | Θ | Minimal polynomial on im K | Ranks of K, ZK, Z²K, Z³K | Minimal polynomial on the whole residual |
|---|---|---|---|---|
| F2 | H² | t² | 6,2,0,0 | t² |
| F3 | 2H−H² | t³ | 6,4,2,0 | t⁴ |

Thus replacing m_Θ by its square-free part is false even on im K. In the
ternary example, m_Θ(Z) is nonzero on the full residual, of rank one; an
additional factor t is needed there. The second identity in (2) permits it.
This is a concrete block-pivot example, beyond #4801's scalar repeated root.
The displayed whole-space values are finite exact fixture claims, verified
by the first linear dependence of complete matrix powers.

For an example without scalar eigenvalues over F2, use
`H=[0 1; 1 1]`. Then Θ=H² and m_Θ=t²+t+1. The constructed n=8 pair has
rank K=4 and whole-space minimal polynomial `t(t²+t+1)`. Consequently a
scalar-eigenvalue check alone cannot verify this theorem. The same displayed
H over F5 supplies an odd-characteristic sign control and a repeated-root
shift; it is a separate field calculation.

### Explicit fixture construction

This is a padded version of Petalas #4746's all-field construction, following
ssafwann #4671's binary construction. It is included to make every example
independently reproducible, not as a new dimension result. Let W=I−H. In the
00 sector choose `X00=−W, Y00=I`, of dimension d. For each active sector
10,01,11 with target F respectively W,W,H, choose columns N complementing
im F and set `X=[F,N], Y=[I;0]`. Then X is onto, Y is injective and XY=F.

Concatenate X's to π0 and stack Y's to i0. Their products sum to
`−W+W+W+H=I`, so π0i0=I. On the four sectors let
`P0=diag(0,I,0,I), Q0=diag(0,0,I,I)`. Take `M=[i0, basis(ker π0)]` and form
`P=M^-1 P0 M, Q=M^-1 Q0 M`. The pivots are identities and `(PQ)11=H`.
The six active ranks give sharpness by #4746; the new checker independently
checks the resulting full-matrix commutator rank in every case. Dimension is
`4d+nullity(H)+2 nullity(I−H)`, at most 6d. No optimality is claimed for the
padded 00 sector. Greedy standard-coordinate complements make the executable
construction deterministic.

## Verification

Python 3.12 standard library, no network, Git or predecessor-code dependency
in the scientific verifier. All checks use explicit exceptions under `-O`.

```sh
python3.12 -B scripts/research_package.py --package research/schur-block-central-law
python3.12 -B scripts/check_research_commit.py --package research/schur-block-central-law --check-source-history
python3.12 -I -W error -B research/schur-block-central-law/verify.py
python3.12 -I -W error -O -B research/schur-block-central-law/verify.py
```

On macOS arm64 / CPython 3.12.11, the registered normal and optimized
replays pass in 6.32 seconds combined (local duration, not a speed comparison).
The registered replay runs both direct modes and emits
`PASS_SCHUR_BLOCK_CENTRAL_LAW`. The verifier writes no files.

- All **1,244** H in seven complete domains: d=1,2,3 over F2 and d=1,2 over
  each of F3,F5. For each it constructs P,Q, verifies their premises and H,
  forms literal Schur complements, checks K=AB, both ordered actions, the
  central intertwiner, both polynomial laws and exact restricted minimal
  polynomial. Complete-matrix powers acting on K check the latter without
  using the proposed intertwiner as an oracle.
- Every **1,472** ordered commuting identity-pivot binary projector pair at
  `(n,d)=(3,1),(4,2)`: respectively 253 and 1,219 pairs. These credited small
  domains test the new laws beyond the sharp fixture construction. No pair
  in these domains is sharp; rank-zero and rank-one commutators occur.
- Four displayed fixtures additionally check every rank sequence
  `rank((Z−λI)^j K)=2 rank((Θ−λI)^j)` for every λ in their field and
  j=0,...,d+1, and compute their whole-space minimal polynomials.
- Nine rejection controls distinguish repeated roots, the full-space
  endpoint factor, H from Θ, the odd-field sign, sharpness, pivot validity,
  idempotency, input commutation and the census capacity limit.

Universal claims rest on the written argument. The finite domains are prime
fields only; no characteristic-zero, extension-field or arbitrary-dimensional
census is claimed. Source-history/committed-byte checking and export transport
integrity are separate from mathematical validity. No independent human or
formal proof-kernel acceptance, Lean, Docker, full-history replay or selected
scientific cold replay is claimed. Hosted CI is reported separately in the PR.

## Scope, overlap and attribution

Base: canonical main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision
7, selected conditional κ=0.00302015. The scoped handoff is claimed in
[Discussion #4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653),
with a [#1166 pointer](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147366).
The `formal-interface-lemma` card is explicitly **changed** to a written
algebraic side result. It supplies a necessary residual constraint and, under
sharpness, one exact restricted representation. It does not audit the selected
supplier's uniform implementation. The source-binding orientation command
stopped at the sparse-omitted `certificates/checkpoints/frontier4359.json`;
no selected baseline pass is claimed.

Initial overlap covers all 7,091 tracked in-scope notes on this base, 319 open
PR bodies and 4,505 Discussion records, with complete pagination and no coverage
warnings. The final refresh covers 322 open PRs (14:19 UTC), 4,520 Discussion
records (14:21 UTC), and all 7,091 tracked notes, without coverage warnings.
Canonical main is unchanged. TASK.json records these snapshots.
Targeted all-state PR searches supplement this, but arbitrary diffs, nested
notes, an exhaustive closed-PR body inventory and unpublished work remain
outside coverage. No absence-of-matches claim establishes novelty.

Exact base-main README bytes are provenance-pinned in SOURCES.json; their
historical claims retain their stated review status. None is a runtime input.
The immediate #4801/#4746 predecessors were merged when checked; archive acceptance
does not imply independent scientific approval.

- **Nick Petalas #4801**, head `98bc071317b17fd8bb4f21044328914c7561d3cb`,
  supplies the scalar law and explicit block question. **#4597**, head
  `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`, supplies the ordered factorization;
  #4278/#4259/#4228 retain the scalar Schur/header lineage.
- **Nick Petalas #4746**, head `5f014560d6225cae17598ac479fb29d2947d8e6b`,
  supplies the signed all-field sectors and fixture construction, extending
  **ssafwann #4671**, head `8d2e3bc76aa7d43e5c629daaf1e72d4dd5a81ed9`;
  #4657/#4678 retain the identity-pivot and counting lineage.
- **Ryanson Jonathan #4609**, with disclosed Claude Code assistance, supplies
  central-operator/idempotent context; #4617 and **lee-phys #4634** retain
  their binary dimension/sharpness contributions.
- **Mihir Srivastava #4689**, **codyw912 #4735**, **MatShep #4762**,
  **Nick Petalas #4915**, and **JoyboyBrian #5072** supply the distinct residual
  census, recurrence, descriptor, orbit weights and scalar incidence work.
  Those quantities are not repeated here. **Krzysztof Wojt #5128** supplies
  arbitrary-pivot dimension minima, a different obligation.
- **Cinna Davis #4100** and the retained source527, commdata2338 and Jose
  Manuel normalizer lineage supply the BIT/header context.

Substantial predecessor AI-assistance disclosures and Apache-2.0 credit are
retained in their unchanged sources. No shared code, frozen evidence, existing
package, priority or selected-frontier file is modified.

## Open next questions

The block-central identity is closed at this scope. A next useful question is
whether, for one specified singular H, the extension of the restricted pair
on im K to the whole residual can be classified and weighted. Start with the
ternary H=J3 example above: its central nilpotency grows from three to four.
The missing data are how the complementary residual directions attach to
im K, and their split/header multiplicities. The present theorem is not a
complete state invariant or transition law; another dimension scan is not
needed to answer it. No follow-up claim is held.

Nonidentity block pivots and subsequent noncommuting deletions require new
hypotheses and a new derivation. Physical production separately needs a named
header cover and priced selection/emission, reads, ownership, dirty restoration,
precision, storage, stock, dispatch and the complete consumer bill. Those costs
remain unknown, not zero. This session stops at the one-deletion theorem.
