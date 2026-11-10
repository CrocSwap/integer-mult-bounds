# External audit of the effective interval local-limit argument

Source: alephnan PR6713 head `cd666f05c4e9006025b634687cc493911c8371c8`, LOCAL_LIMIT.md sections3-7 and bounds(1)(2). Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0. The local-limit theorem and effective flow construction remain predecessor work. This is an external source-aware AI audit, not a new exponent, human acceptance or proof-kernel certificate.

## Proposition and evidence boundary

**No gap found in the reviewed analytic implications, conditional on H and the classical interval approximation stated below.** Both separately authored exact-rational first runs certify all six H predicates for the literal nine-atom law across the entire declared alpha interval. Their complete method-specific enclosures are retained and are not claimed identical; each is checked by its own full regeneration. No n-fold convolution is enumerated. The tilt's existence, uniqueness and reported alpha bracket are inherited; none is inferred from a numeric replay.

Let X have a finite real law with atoms at exactly0,ln2,ln3 of masses at least1/4,1/8,1/16. Put Z=X-E[X], and suppose

    2<=v=E[Z^2]<=3, E|Z|^3<=5, |Z|<=3 almost surely.

For n>=1296 integer let S_n be the sum of n independent copies of Z, and let G_n have mean0 and variance nv. Define

    B_n=3/sqrt(n)+sqrt(n)*ln(n)*exp(-sqrt(n)/320),
    A_n=(1+4B_n)/ln(n), c_sigma=sqrt(v)*sqrt(2pi).

For every real x, b>=0 and every interval I with endpoints x,x+b, including any endpoint convention,

    sqrt(n)*|P(S_n in I)-P(G_n in I)| <= A_n+b B_n.       (R1)

Consequently

    |sqrt(n)*P(S_n in I)-b*exp(-x^2/(2nv))/c_sigma|
      <= A_n+b B_n+b^2/(4sqrt(n)).                       (R2)

At b=0 the possibilities are the empty interval and singleton{x}. These are included, not suppressed by an assumption that S_n has a density. The bound is uniform in x. Source sections8-9, the symbolic huge onset, kernel transfer and complete flow propagation are outside this review.

## Classical approximation and Fourier normalization

The external premise is the Beurling-Selberg interval majorant/minorant with angular Fourier support[-T,T] and spatial L1 error2pi/T. I checked this normalization against Laura Shou, Theorem4.1, printed page12 of [arXiv2110.15301v3](https://arxiv.org/pdf/2110.15301v3). Its transform uses a forward factor1/(2pi), as visible again in equation4.8; multiplying that transform by2pi changes neither support nor the spatial defect. Set its parameter D=T. This imports a classical approximation statement, not the paper's unrelated graph theorem or a proof of the approximation.

Use here

    hat F(t)=integral F(u)exp(-itu)du,
    F(u)=(1/(2pi))*integral hat F(t)exp(itu)dt.

For a length-b interval write F_-<=1_I<=F_+, with defect d=2pi/T. The minorant may take negative values. Nevertheless triangle inequality gives, for BOTH signs,

    ||F_+||_1,||F_-||_1 <= b+d,
    |hat F(t)|<=b+d.

Nonnegativity of F_- is never assumed. Finite L1 norm and compactly supported bounded transform make the inversion integral integrable. One may use the continuous inverse-transform representative; if an approximation statement is only specified almost everywhere or uses half-weight boundary values, the enlargement/contraction argument below supplies the required pointwise sandwich away from those boundaries. Continuity and the constant values of an indicator on the open interior/exterior preserve the inequalities there.

Put phi(t)=E exp(itZ) and

    D_n(T)=integral_[-T,T] |phi(t)^n-exp(-nv t^2/2)|dt.

Inversion and Fubini against either probability measure are justified by the integrable bounded-support transform, even when S_n is atomic. They give

    |E F_+(S_n)-E F_+(G_n)| <= (b+d) D_n(T)/(2pi),
    |E F_-(S_n)-E F_-(G_n)| <= (b+d) D_n(T)/(2pi).

The Gaussian density is at most1/(sqrt(v)*sqrt(2pi n)). Its expectation of either approximation differs from its interval probability by at most that density bound times d. The upper and lower sandwiches each use ONE such defect, not the sum of two defects. Hence

    sqrt(n)*|P(S_n in I)-P(G_n in I)|
      <= 2pi/[T sqrt(v)*sqrt(2pi)]
         +(b+2pi/T)*sqrt(n)*D_n(T)/(2pi).                (S)

This independently checks the source's normalization and the signed-minorant use.

## Endpoints, including atoms and b=0

For b>0 choose0<2epsilon<b. An outer interval[x-epsilon,x+b+epsilon] and an inner interval[x+epsilon,x+b-epsilon] sandwich every endpoint convention of I. The outer majorant is at least1 at every point of I, which lies strictly inside the outer interval. The inner minorant is at most0 outside I and at most1 inside. This remains valid when the external indicator uses half weights at its own endpoints; those endpoints are separated from the original boundary. The continuous band-limited representatives also suffice by the preceding interior/exterior argument.

Apply the same Fourier/Gaussian estimates to these lengths b+2epsilon and b-2epsilon. The Gaussian probabilities of their differences from I tend to0, and all analytic bound terms depend continuously on their lengths. Squeezing and then epsilon down to0 yields(S) for each original endpoint convention, with no atom-size premise. It is not necessary that the probabilities of outer-minus-inner walk intervals tend to0, so a boundary atom is not accidentally discarded.

For b=0, an empty interval has zero mass for both measures. For{x}, shrink[x-epsilon,x+epsilon]. Continuity from above of probability measures gives its walk mass; Gaussian mass and the b-dependent terms tend to0. Thus(R1) holds with A_n, and(R2) does also. This establishes the singleton case used by a future layer-cake caller, without auditing that caller here.

## Central-frequency calculation

Take delta=1/6. For independent Z' one has |t(Z-Z')|<=1 whenever |t|<=delta. Since1-cos u>=u^2/3 for |u|<=1,

    |phi(t)|^2=E cos(t(Z-Z'))<=1-(2/3)v t^2,
    |phi(t)|<=exp(-v t^2/3).

Centering is essential in the next Taylor step. The third-moment bound gives |phi(t)-(1-vt^2/2)|<=(5/6)|t|^3. The positive exponential remainder at u=vt^2/2 gives |exp(-vt^2/2)-(1-vt^2/2)|<=v^2t^4/8. Using v<=3, |t|<=1/6, the sum is at most

    (5/6+3/16)|t|^3=(49/48)|t|^3.

Telescoping nth powers, both bases have modulus at most exp(-vt^2/3). For n>=2, n-1>=n/2, so

    |phi(t)^n-exp(-nv t^2/2)|
      <= n*(49/48)*|t|^3*exp(-nv t^2/6).

The full-real-line integral of |t|^3 exp(-c t^2) is1/c^2. Replacing the central integral by that larger positive integral gives

    integral_[-delta,delta] difference
      <= 36*(49/48)/(v^2 n)<=147/(16n)<10/n.             (C)

No phase cancellation or nonnegative characteristic-function assumption was used.

## Separated frequencies and the two logarithms

Let d_j(t)=dist(t ln j,2pi Z), j=2,3, and d=max(d_2,d_3). Set T=2ln n. It is enough to consider delta<=t<=T by symmetry. Choose nonnegative nearest integers p,q to t ln2/(2pi),t ln3/(2pi). Either choice in a rounding tie satisfies the same error bound.

If p=q=0, d=t ln3>=1/6>=n^(-1/4) because n>=6^4 and ln3>1. Otherwise unique factorization gives2^q!=3^p, including the cases with one zero exponent. Integrating1/u between these distinct positive integers gives

    |q ln2-p ln3|>=1/max(2^q,3^p).

Nearest-integer errors e_2=t ln2-2pi p, e_3=t ln3-2pi q obey

    2pi*(q ln2-p ln3)=e_2 ln3-e_3 ln2,
    max(q ln2,p ln3)<=T ln2 ln3/(2pi)+(ln3)/2.

Thus

    d(t)>=[2pi/(sqrt(3)*ln6)]*exp[-T ln2 ln3/(2pi)].      (L)

The two prime bases and exponents must not be interchanged in the integer-separation argument. Elementary bounds ln2<7/10,1<ln3<11/10,pi>31/10 imply

    ln2 ln3/(2pi)<77/620<1/8.

Also sqrt3<2 and ln6<2 imply the prefactor in(L)>1. Substituting T=2ln n proves d>=n^(-1/4). This uses only distinct integers; it does not invoke an ineffective irrationality measure or assume a frequency gap near t=0.

The uncentered atom differences determine the modulus. For the finite law,

    1-|phi(t)|^2=2 sum_(i<j) p_i p_j[1-cos(t(x_i-x_j))]
      >=4 p_0 min(p_ln2,p_ln3)*(d_2^2+d_3^2)/pi^2
      >=d(t)^2/(16pi^2).

All omitted pair terms are nonnegative. With pi^2<10 and sqrt(1-u)<=exp(-u/2),

    |phi(t)|^n<=exp[-n*d(t)^2/(32pi^2)]
                <=exp(-sqrt(n)/320).                    (F)

The asserted gap is for the nth power on this finite band; it is not a uniform constant gap for phi over unbounded t.

## Integration, constants and Gaussian replacement

For the Gaussian outside delta,

    integral_(|t|>delta) exp(-nv t^2/2)dt
      <=2 exp(-nv delta^2/2)/(nv delta)
      <=6 exp(-n/36)/n.

The separated-band length is at most2T=4ln n. Combining(C),(F) and this tail,

    D_n(T)<=16/n+4ln(n)exp(-sqrt(n)/320).

In(S), the smoothing term is at most1/ln n: it is pi/[ln(n)*sqrt(v)*sqrt(2pi)] and v>=2,pi<4. Further2pi>6 and2pi/T=pi/ln n<4/ln n. Therefore

    sqrt(n)D_n(T)/(2pi)<=3/sqrt(n)
                            +sqrt(n)ln(n)exp(-sqrt(n)/320)=B_n,

and(S) is at most1/ln n+(b+4/ln n)B_n=A_n+bB_n, proving(R1).

For the Gaussian density g_n, differentiating and maximizing gives

    sup_y |g_n'(y)|=1/[nv sqrt(2pi e)].

Consequently |integral_x^(x+b)g_n(y)dy-b*g_n(x)| is at most b^2/[2nv sqrt(2pi e)]. Multiply by sqrt(n), use v>=2 and sqrt(2pi e)>1, and get b^2/(4sqrt(n)). The Gaussian has no endpoint atoms. Combining with(R1) proves(R2) for all endpoint conventions and b>=0.

## Written scope controls

1. Negative minorants cannot be treated as probability densities. Their L1 norm is controlled by triangle inequality, not by assuming integral equals norm. Dropping that absolute-value step is not justified by a pointwise lower sandwich.
2. The zero-nearest-integer branch is indispensable. No d(t)>=n^(-1/4) statement can hold down to t=0, where d=0.
3. Removing an incommensurate atom can leave the other coarse hypotheses intact yet destroy attenuation. Put probabilities1/4,1/8,5/8 at0,ln2,5ln2. Then mean=(13/4)ln2, variance=(83/16)(ln2)^2, third centered absolute moment=(3419/256)(ln2)^3, and centered support<3. The elementary2/3<ln2<7/10 gives2<v<3 and third moment<5. At t=2pi/ln2 all uncentered phases coincide, so |phi|=1; this frequency lies in the stated band for n>=1296. It is a control after deleting the log3-atom premise, not a counterexample to the submitted lemma. These are hand calculations, not executed convolution tests.
4. A singleton cannot be replaced by a zero-length Lebesgue interval without the shrinking-probability argument; the walk can have atoms even though the Gaussian does not.

## Remaining obligations and attribution

The numerical H certificate concerns the nine-atom law across the inherited alpha bracket and centering at its actual mean. It does not certify the predecessor's tilt root bracket or mean-equals-ln5 equation. The classical Beurling-Selberg statement is a cited premise; only its applicability/normalization is checked here, not a new proof of it. The giant onset in section8, kernels in9, all-layer/leaf/complement/boundary flow propagation, physical/native suppliers, complete invoices, compiler/precision/stock/tape/outer and all five framework assumptions remain outside.

The effective local-limit and complete flow contribution remain alephnan's PR6713 work, with substantial OpenAI Codex assistance. CubeJerry PR6329 supplies the earlier exponent/flow step; zxv4436/4483, Ryanson Jonathan/pinterbanget4459/4467, DLamdata6118, Nick Petalas6125/6128, Cinna Davis, Jacob Alan Sussman and retained native/precision/analytic contributors retain their credit. Beurling, Selberg, Vaaler and Laura Shou retain the classical/normalization references. The separate AI audits/calculators add external source-bound scrutiny, not human, formal or selected-frontier acceptance.
