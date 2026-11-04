# Adversarial written review of the smoothing argument

Verdict: **no material gap found in the reviewed argument, conditional on H and the cited classical interval approximation.** Fourier normalization, the signed-minorant estimate, inversion against an atomic law, endpoint passage and singleton treatment are valid as written. The overall constant assembly and the weakened-hypothesis lattice control also check out. This does not certify H, the tilt, the huge onset, kernel transfer, full-flow propagation or a physical supplier.

Reviewed: the coordinator's session-05 FOURIER-REVIEW.md draft, whose numerical-H status was PENDING when read; the pinned source LOCAL_LIMIT.md; and the primary-paper text identified below. ROOTNUMERIC code, numeric first results and source checkers were not read or executed. The earlier SEPARATION-REVIEW.md was completed before reading this coordinator derivation. This review is source-aware, not blind: prior exposure to the author's REVIEW.md and its disclosed discovery participation remains explicit. Agreement of AI reviewers is not human or proof-kernel acceptance.

## 1. Primary statement and normalization

I independently consulted the parsed mathematical text of Laura Shou, [arXiv:2110.15301v3](https://arxiv.org/pdf/2110.15301v3), Theorem 4.1 on printed page 12 and equation (4.8) on printed page 13. The theorem states the real-line interval sandwich, Fourier support within [-D,D], and each spatial absolute defect 2pi/D. Equation (4.8), consistently with the periodization identities nearby, uses the forward factor 1/(2pi). These facts support setting D=T. No screenshot or visual inspection is claimed, and the theorem's proof is not re-proved here.

Let the paper's normalized transform be ghat_paper. The convention in the audit is `Fhat(t)=integral F(u)exp(-itu)du`, so `Fhat=2pi*ghat_paper` and its inverse has factor 1/(2pi). Multiplication of a transform by this nonzero constant does not change its support. The functions themselves and the spatial L1 defects are unchanged. Thus no extra 2pi belongs in the bandwidth or the spatial defect. The unrelated graph/Weyl conclusions of Shou's paper are not imported.

## 2. Signed minorants and legitimate inversion

For either approximation F and interval indicator chi, the external premise gives `||F-chi||_1=d`, where d=2pi/T. Therefore

    ||F||_1 <= ||chi||_1+||F-chi||_1 = b+d.

This applies to F_minus even when it has negative values. Identifying its integral with its absolute integral would be invalid; the coordinator does not do that. In particular the argument remains valid when b<d and the signed minorant integral is negative.

It follows that |Fhat(t)|<=b+d. Since Fhat vanishes outside [-T,T], it is integrable, with integral of its absolute value at most 2T(b+d). Its inverse-transform representative is continuous and bounded. Inversion holds almost everywhere in Lebesgue measure, and the continuous representative may be chosen for the approximation. This choice must be made before integration against an atomic law; equality merely Lebesgue-almost-everywhere would not alone justify substituting values at atoms.

The coordinator's continuity/enlargement argument supplies this pointwise justification. On an open interior or exterior region where chi is constant, a continuous representative agreeing almost everywhere with a function satisfying the sandwich also satisfies the same inequality everywhere there. A violation would persist on an open set of positive Lebesgue measure. Original interval endpoints are placed strictly inside the outer interval and strictly outside the inner interval, so no undetermined boundary representative is needed.

For any probability law mu, Fubini is now justified by

    integral integral |Fhat(t)exp(itu)| dt dmu(u)
    = integral |Fhat(t)|dt < infinity.

Consequently E_mu F is finite and obtained by integrating Fhat times the law's characteristic function, with the inverse factor 1/(2pi). No density of the walk is required. IID summation gives characteristic function phi(t)^n; the centered Gaussian gives exp(-nv t squared/2). Therefore the expectation difference is bounded by `(b+d)D_n(T)/(2pi)`, with the sign of the Fourier exponential consistent in both expectations.

## 3. One Gaussian defect in each direction

The Gaussian density is bounded by `gmax=1/[sqrt(v)*sqrt(2pi n)]`. For either sign, its expectation of F differs from its interval probability by at most d*gmax, directly from the spatial absolute defect.

For the upper probability error, use F_plus; for the lower error, use F_minus. Each direction has one expectation-comparison error and one Gaussian defect. The two directional inequalities are maximized, not added. Thus taking an absolute value does **not** cost a second defect. Multiplying by sqrt(n) gives precisely

    sqrt(n)|P(S_n in I)-P(G_n in I)|
    <= 2pi/[T sqrt(v)*sqrt(2pi)]
       +(b+2pi/T)*sqrt(n)*D_n(T)/(2pi).

This is the coordinator's (S) and the source's inequality (5).

## 4. Endpoint sandwich without discarding atoms

For b>0 choose 0<2epsilon<b and let I_out=[x-epsilon,x+b+epsilon] and I_in=[x+epsilon,x+b-epsilon]. Use the continuous majorant for I_out and minorant for I_in. They bound the actual indicator of I for every choice of its endpoint inclusions. This also avoids a possible half-weight convention at the approximation's own endpoints.

The argument can be written without assuming any continuity of the walk distribution at x or x+b. The upper error is at most

    (b+2epsilon+d)D_n(T)/(2pi)+d*gmax
      +P(G_n in I_out)-P(G_n in I),

and the lower error is at most

    (b-2epsilon+d)D_n(T)/(2pi)+d*gmax
      +P(G_n in I)-P(G_n in I_in).

Only Gaussian probabilities appear in the two small boundary remainders. They tend to zero, and the other terms depend continuously on epsilon. Passing epsilon down to zero proves (S) for the original I. In particular the proof never needs `P(S_n in I_out minus I_in)` to tend to zero; that claim could fail at boundary atoms.

For b=0, empty intervals are immediate. For the singleton, apply the positive-length result to closed [x-epsilon,x+epsilon] and decrease epsilon to zero. Probability continuity from above gives the singleton's walk mass, while Gaussian mass and the length-dependent bound vanish. The resulting bound is sqrt(n)P(S_n=x)<=A_n. This is a genuine measure-theoretic singleton argument, not replacement of an atomic singleton by a zero Lebesgue integral.

## 5. Assembly and lattice-control spot checks

My prior written Sections 5–7 audit remains separate. Spot checking the coordinator's assembly gives the same constants: from `D_n(T)<=16/n+4log(n)exp(-sqrt(n)/320)`, division by 2pi>6 and multiplication by sqrt(n) is at most B_n. The smoothing term is at most 1/log n using v>=2 and pi<4, while 2pi/T<4/log n. Hence (S) is at most `1/log n+(b+4/log n)B_n=A_n+bB_n`. The Gaussian derivative remainder b squared/(4sqrt(n)) is consistent with the earlier independent derivation. No onset simplification is used to obtain these bounds.

The written lattice control is correct after deleting, and only after deleting, the log-3 atom premise. For K on {0,1,5} with probabilities {1/4,1/8,5/8}, its mean is 13/4, variance 83/16 and third centered absolute moment 3419/256. Scaling by log 2 gives the displayed source control. The elementary bounds 2/3<log 2<7/10 yield

    83/36 < v < 4067/1600,
    E|Z| cubed < 1172717/256000 < 5,
    |Z| <= (13/4)log 2 < 91/40 < 3.

Thus the other coarse hypotheses and first two atom masses really remain valid. At t0=2pi/log 2 every uncentered phase is one, so centering leaves modulus one. Also 1/6<t0<12, whereas for n>=1296, `2log n>=8log 6>40/3>12`. Thus the resonant frequency lies in the claimed band and destroys attenuation under that weakened premise. It is not a counterexample to the original lemma and not an executed test.

## Scope and disposition

No correction is requested for the reviewed smoothing implication. In particular no missing factor 2pi, doubled Gaussian defect, illegal use of a signed minorant as a density, Fubini dependence on a walk density, or lost endpoint atom was found. Conditionality remains important: the classical approximation and H are premises of this written argument. The pending numerical-H work must not be called passed until its actual checks and evidence are complete; this review supplies no such execution evidence.

The source's symbolic huge onset, Section 9 kernel transfer and every mixed-layer/source/complement/boundary/leaf propagation step remain outside, as do physical suppliers, invoices, native/owned/precision/compiler/outer work and all selected assumptions. No kappa or frontier update, stronger onset, human acceptance or formal proof is claimed.

Credit remains with alephnan PR6713 and the retained CubeJerry/PR6329, zxv, Ryanson Jonathan/pinterbanget, DLamdata, Nick Petalas, Cinna Davis, Jacob Alan Sussman and native/precision/analytic lineage. Beurling, Selberg and Vaaler retain classical approximation credit; Shou provides the inspected primary statement. This separate source-aware written AI review adds scrutiny, not authorship of the local-limit theorem. Only SMOOTHING-ADVERSARIAL-REVIEW.md was intentionally written for this task; no scientific program, import, source checker or proof kernel ran.
