# Two boundary obligations that remain after the lane inverse identity

Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance. Apache-2.0.
These are scoped interface tests, not a replay of Cao Yifan's native word,
not a universal impossibility result, and not a new bound.

The positive lane identity is supplied by the sibling construction:
for a lower-triangular lane operator A with identical diagonal a and its
actual inverse B, put

`T(A)=a P0+S A R`,  `E(A)=[[A,0],[S(I-B),T(B)]]`,

where S is the nilpotent forward shift, R is its partial reverse and
`S R=I-P0`. T is an algebra homomorphism on this class and
`T(A)S=SA`. Consequently E(A) has the stated actual inverse. The points
below do not challenge that identity. They concern obtaining its exact
shear hypotheses and financing its ideal diagonal boundary.

## 1. An actual inverse does not supply the exact shear hypothesis

Use the polynomial ring Q[η], and define ordinary two-port shears

`U=[[1,-1],[0,1]]`, `L(η)=[[1,0],[η,1]]`,
`F(η)=U L(η)`, `K=[[0,1],[1,0]]`, `B0=[[1,-1],[1,0]]`.

F(η) is an invertible deformation of the ideal upper shear U. Its inverse
is its **actual algebraic inverse**, `L(-η) U^-1`, with determinant one;
no separately generated nominal opposite orientation is used. Direct
multiplication gives

`F(η) K F(η)^-1 K B0 =`

`[[-1-3η+2η², 2η-η²],`
` [ 2+η-2η², -1-η+η²]]`.                                  (1)

At η=0, (1) is exactly `Φ(-1)=[[-1,0],[2,-1]]`. The ideal lower shear
in this special case is `K U^-1 K`, so this test gives actual-inverse
correlation every opportunity to cancel the perturbation.

Now substitute η=S, with L>=2 lanes, and apply the proposed partial
input/output shifts:

`diag(I,S) [F(S) K F(S)^-1 K B0] diag(I,R)`.

Its upper-right block is

`(2S-S²)R = 2(I-P0)-S(I-P0)`.                              (2)

In particular it has diagonal `(0,2,...,2)`. The ordinary ideal repair
`-P0` in the lower-right block cannot alter (2). This gives a grade-zero
wrong-port contribution, so one outer lane scaling cannot make it small.
For L=2, input X=0 and Y supported on lane 1 produces X=2 on lane 1,
where the intended diagonal Gaussian interface produces X=0.

This failure is not intrinsic to every first-order perturbation. Replacing
F by the output-side perturbation `L(η)U` instead gives

`L(η)U K [L(η)U]^-1 K B0 = [[-1,0],[2-2η,-1]]`,

whose upper-right block remains zero. Therefore the actual literal location
and form of the defects matter. Independent input/output scalar matrices,
whole-word invertibility and equality of their grade-zero ideal operators
alone do not establish the exact shear premise needed by E(A).

**Scope.** This is an abstract completed-interface counterexample. It does
not prove that (1) is the endpoint of any paid-child substitution in the
retained round-three native word. The next native test must bind the literal
forward/backward implementations and their errors, including helper mixing,
and prove the required exact shears or a replacement endpoint identity.
Independent commuting fresh D factors multiply the displayed nonzero block;
the presence of such factors alone does not make the counterexample vanish.

## 2. Exact minimal-lane stock has a separate losing invoice

The local lane construction's boundary is one ideal rank-17 inverse job
for each of 112 pairs. It is not a lane-batched realization on arbitrary
inputs. At the minimal lane, the construction supplies exact X jobs and
exact helpers, but each exact Y job has already been supplied by this
boundary provider. Passing that Y through is not an additional net source
of exact jobs.

For the **specific provisioning model** that recursively services every
exact boundary demand and every exact first-lane paid demand using only
these minimal-lane exact outputs, the net target profile is therefore

`T_exact = 2H + 112 H17`,
`H = {4:28,7:7,8:47,9:326}`,

against the same exact first-lane paid profile

`P = {1:4656,2:920,3:1386}`.

The target rank mass is 8,846 and the paid mass is 10,654. This counts the
boundary Y as an exact input/output pass-through and subtracts both sides;
it does not discard an independent target or treat a copied value as one.

For every 0<t<=1, the smallest target rank is 4 and the largest paid rank
is 3. Therefore

`sum T_exact[k] k^t <= 4^(t-1) * 8846`,
`sum P[r] r^t       >= 3^(t-1) * 10654`,

and hence

`target_moment / paid_moment <= (4/3)^(t-1) * 4423/5327 < 1`. (3)

Thus this uniform exact-minimal-lane stock cannot fund its own recursion,
even under optimistic scalar, storage and routing costs. Making the number
of lanes large does not improve the per-unit minimal-lane invoice (3).

**Scope.** This does not rule out a different boundary producer, dynamic
extraction from nonzero lanes, explicitly priced corrective work, or a
changed joint input contract. All those require a new source/target ledger.
Feeding only one nonzero lane to a generic L-lane child program also does
not by itself divide its paid call count by L. Such pruning would require
a literal implementation and cost proof.

## Verification and source binding

`python3 -I -B check.py` and the optimized variant `python3 -I -O -B check.py`
produce the same RESULT.json on CPython 3.14.5. The checker constructs dense
rational matrices for L=2,...,8, obtains each actual inverse by Gaussian
elimination instead of the symbolic inverse formula, checks both inverse
orders and every matrix entry, verifies the transported diagonal leakage,
and includes the benign output-side control. The 70 full independent input
columns represented by those seven matrices are covered by exact equality.
The finite checks corroborate (1)-(2); their written algebra proves all L.
Equation (3) is proved from exact profile masses and rank separation; no
floating root approximation or unsupported numerical optimization is used.

The profiles are inherited from Yiyang's two-full Laurent border, based on
Cao Yifan's round-three native source at
`0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62`, compressed source SHA256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.
The strict split retains the original whole-job monomial boundaries and
splits `4 -> 3+1`, `5 -> 3+2`, `8 -> 3+3+2`. This note does not rerun that
predecessor native or split audit. The positive lane identity and its local
boundary invoice are sibling work, not newly proved by this checker.

Canonical main at the research checkpoint is
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1`; the selected frontier is unchanged.
The inherited finite-precompiler contributors, Dillon's border/recovery
work, native/Clifford sources and all earlier attributions remain credited
in their source packages. No independent human or proof-assistant review
is claimed here.
