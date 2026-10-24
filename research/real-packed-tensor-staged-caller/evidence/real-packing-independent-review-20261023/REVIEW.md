# Independent mathematics review of the PR5095 real-input packing proposal

2026-10-23. **PASS as an exact parent-cut identity and sufficient conditional error lemma.** No counterexample to the frozen note's stated hypotheses was found. This does not validate a changed physical implementation, production Tensor execution, lower total cost or recursive κ improvement.

The reviewed note is `outputs/mathematics-paper-research-20261023/notes/real-packing-5095-fit.md`, SHA256 `3b48e1790472a686ac1d7a50673b90fb2f456b5c72d35a85e5f96dbd54febf62`. The source appendix and manifest are pinned at `87243c00536e42cbc8663b645b80c83a4cf3a8558a9442d37855c6de38b75a69` and `a41239e2bca82f6f8fb63f79eebc11f40bd7cb3671cee30ce94d7ef217315d76`. All nine source snapshots and their byte counts were authenticated before and after this review's scalar calibration. Literal ingress, pointwise, recovery and call order, the Tensor boundary restoration/opposite flags, CRT routing and the source07 Fourier identities were read. No source or frozen A/B output was edited.

## Exact signs, dilation and normalization

Let G be the product of source cyclic groups, |G|=S. Use the source's normalized transforms F−,F+, each with factor1/S. Let R multiply coordinate i by the retained target length t_i modulo s_i. Because gcd(t_i,s_i)=1, R is a permutation. The completed maps are exactly T=RF− and T+=RF+, under the inherited complete-Tensor ideal-map premise. The opposite flag conjugates at both input and output, yielding RF+, with the **same** R. It does not yield R^-1F+ or an unnormalized inverse.

For J negating every source coordinate, RJ=JR. For every complex h,

```
conjugate(J T h)=T(conjugate(h)).
```

Thus, for two separately variable real arrays u,v and h=u+iv,

```
H=T h,
H#=conjugate(J H)=T u−iT v,
A=(H+H#)/2=T u,
B=(H−H#)/(2i)=T v.
```

The product is scalar coordinatewise multiplication on C^S. There is no inner negacyclic polynomial multiplication and no extra divisor r at this parent cut. Source07 gives F+R=R^-1F+, hence RF+R=F+. Since R also preserves coordinatewise multiplication,

```
T+[(T u).*(T v)]
 =RF+R[(F−u).*(F−v)]
 =F+[(F−u).*(F−v)]
 =(u*v)/S².
```

The last S² comes from F−(u*v)=S(F−u).*(F−v) and F+F−=I/S. The existing final multiplier S²2^(2b+4) is therefore correct and unchanged. Tensor's exact 2^gamma restoration is already included in T/T+; it must not be applied again or substituted for an S factor. The original two forward CRT conversions and inverse CRT conversion remain required by this proposal as written.

The two source digit streams remain independent. Their padded arrays have values a_j/2^(b+2), with nonnegative b-bit digits and S−q zero cells; CRT only routes these real values. Hence 0≤u_j,v_j<1/4 and |u_j+iv_j|<sqrt(2)/4<1/2. The packed input satisfies the actual arbitrary-half-disk Tensor entrance. Exact ingress is on the p-grid because p≥b+2. Independence is not replaced by a relation between the two operands; the Hermitian identities arise separately from each operand's reality.

## Independent derivation of the same strict recovery guard

Write h_p=2^-p, epsilon=E2^gamma h_p, C=S²2^(2b+4), with the source's actual E,gamma and production-page premises. The encoded guard is exactly

```
2C(3E2^gamma+2)<2^p,
equivalently C(3epsilon+2h_p)<1/2.
```

Since b≥1 and S≥1, C≥64. Therefore epsilon<1/(6C)≤1/384. The guard's strictness is essential for nearest-integer uniqueness.

The source approximation is uniform on arbitrary computed half-disk inputs, not only on the original quarter-disk arrays. It therefore applies to the one actual packed call. If its returned error e satisfies ||e||∞<epsilon, both real-linear split maps have norm≤1: their errors are averages of e and conjugate(Je). Each split result consequently differs from its own ideal transform by less than epsilon. No rounded Tensor linearity or independence of the two split errors is used.

The ideal split arrays have norm<1/4 because normalized Fourier transforms are contractions. Therefore

```
||Atilde Btilde−AB||∞
 < epsilon(1/4+epsilon)+epsilon/4
 =epsilon/2+epsilon²
 <2epsilon.
```

Their exact product has norm<(1/4+epsilon)²<.26²<1/2. Componentwise truncation toward zero does not increase modulus and adds complex error<sqrt(2)h_p<2h_p. The returned p-grid product thus lies within the unchanged opposite Tensor entrance.

Insert the exact opposite transform on that actual computed product. Its norm≤1 and the inherited actual opposite-call error<epsilon give total error<3epsilon+2h_p. Scaling by C gives error<1/2 by the **same source guard (G)**. The true recovered real coefficient is an integer, so the existing nearest, inverse CRT and carries apply. The original conservative recovery word width W=(p+2)+4b+4 remains sufficient: the opposite call still returns through its original component boundary, and every final scaling is unchanged.

The lemma is valid only if splitting is exact before the single final product truncation. Separately rounded split banks would require additional terms. It is a new elementary source-bound deduction, not a result proved in the TI report.

## Exact splitting representation must be specified

For returned integer numerators

```
H_j=(a+ib)/2^p, H_Jj=(c+id)/2^p,
```

exact split numerators are `(a+c,b−d)` and `(b+d,c−a)` at grid p+1. If that raw-sum representation is retained, their product has grid2p+2 and must be shifted by **p+2** to return to grid p. Blindly reusing `sandwich.pointwise`'s shift p on those raw sums gives a factor-four error. A scalar control at p=8 with `(a,b)=(c,d)=(32,16)` yields correct p-grid product numerator2; the wrong raw-sum shift produces8.

There is also a useful source-specific alternative. Literal Tensor boundary restoration shifts each returned numerator by gamma≥1, so a,b,c,d are multiples of2^gamma. All split sums/differences are therefore even. One may divide their integer numerators by2 **exactly**, store the split arrays on the original p-grid, then use the ordinary product shift p. This is not a rounding step. The source restoration parity premise must remain bound, and widened sum temporaries must prevent overflow. Either representation realizes the lemma. An implementation must choose one and expose its scales; the frozen proposal does not incorrectly prescribe one of them.

## Evidence and limits

`check_scalar_obligations.py` authenticates the frozen note, appendix, nine source snapshots and cited primary PDFs; checks the exact four-integer split-product identity and factor-four representation control; verifies the conservative rational disk/error inequalities; and checks that reflection commutes with the actual (5,7) / (8,8) coordinate dilation. It also checks strict guard equality rejection. It imports or executes no Tensor, CRT, factory or nested archive. Normal and `-O` JSON are byte-identical. These scalar calibrations do not execute the proposed rounded pipeline.

TEST-SPEC.md defines the smallest next independently discriminating rounded test, conditional on separate ownership/overlap authorization. The present reduced p48 (5,7) catalogue is staged conformance and is rejected by the source's default production recovery admission. Fixed (5,7) does not become production-admitted by increasing p. The p96 supplied-approximation recovery leaf is also distinct from producing approximations through an admitted Tensor. No production multiplication success follows here.

The exact parent call count becomes two complete Tensor invocations instead of three. A total fixed-tape saving still requires packed-bank formation, J-pair routing, widened exact splitting/products, source-produced pages, temporary ownership/cursor restoration and cleanup to be priced. The recursive real/Hermitian closure route remains STOP under the coordinator's existing common-real-scaling finding; this review neither reopens nor extends it. No recursive supplier moment, compiler reserve, selected result or new κ follows from the finite identity.

## Attribution

The standard packing/unmixing identity is credited to the real-FFT literature. The inspected TI SPRA291 primary report is an engineering application report, not a peer-reviewed mathematics theorem; its Appendix A.1 states the relevant linearity and reflection/conjugation formulas. The Johnson–Frigo author-hosted chapter is additional published linearity context. Cooley–Lewis–Welch metadata is not used as evidence of an uninspected equation or priority claim. The derived source guard is local work, not attributed to those publications.

Retain JoyboyBrian's PR5095 caller, Jose Manuel/jmbarrancoml's PR3935 complete Tensor, Tekalign/tekuuu's PR4024 CRT, Mason Hale's recovery predecessor, Harvey–van der Hoeven and the retained native, Gaussian, router and exact-word contributors. Substantial OpenAI Codex assistance; no independent human review or priority claim.
