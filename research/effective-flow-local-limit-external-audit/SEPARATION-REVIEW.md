# Written constant audit: LOCAL_LIMIT Sections 5–7

Verdict: **PROVED-CONDITIONAL within the reviewed scope; no gap or counterexample found.** The central-frequency, two-logarithm separation, characteristic-function defect, integrated D_n and Gaussian-gradient constants follow under the stated hypotheses. This is separate written AI review, not a blind review, a finite replay, a proof-kernel result or acceptance of the complete local-limit/flow theorem.

## Identity, exposure and scope

Source: alephnan PR6713 head `cd666f05c4e9006025b634687cc493911c8371c8`, `research/effective-direct-flow/LOCAL_LIMIT.md`, Git blob `4779c059964ca4c30e3714fa98674c1b331a5151`, SHA256 `07702eabadefa4e2c435d6ea7e60c781aaa786fa875cab773a5962d8d2a2efe3`. The freshly acquired exact text is `INPUTS/LOCAL_LIMIT.md`; all six source identities, including the repository-root NOTICE rather than a nonexistent package NOTICE, are in SOURCE-PINS.json.

The root authorized this narrowed written audit after public advance claim 19406432. This child had read LOCAL_LIMIT and the source's author-side REVIEW during the preceding S4 scout. That prior exposure is disclosed; no blind-discovery claim is made. Source REVIEW itself discloses its reviewer's earlier separation-discovery contribution. The calculations below are explicit written reconstructions rather than reliance on that review's verdict. I did not read root's developing derivation for this session.

Assume (H): Z is centered, |Z|<=3, 2<=v=E Z squared<=3, E|Z| cubed<=5, and before centering X has atoms at 0, log 2 and log 3 with respective masses at least 1/4, 1/8 and 1/16. Verification of H for the literal tilted source law, the tilt bracket and numerical arithmetic implementation are outside this audit. Put phi(t)=E exp(itZ), delta=1/6, T=2 log n and n>=1296.

For assembly only, assume the source's smoothing inequality (5) with its exact angular-frequency normalization and L1 defect. The external Beurling–Selberg theorem, its normalization, interval/singleton endpoint passage and overall all-flow propagation belong to root's separate review. No claim below independently establishes them.

## 1. Central-frequency constants

For independent Z', |t(Z-Z')|<=1 when |t|<=delta. The elementary cosine inequality follows, for example, from its fourth-order Taylor bound: `1-cos u >= u squared/2-u to the fourth/24 >= u squared/3` on this domain. Independence and centering give E(Z-Z') squared=2v. Hence

    |phi(t)| squared <= 1-(2/3)v t squared,
    |phi(t)| <= exp(-v t squared/3).

The square-root step uses sqrt(1-u)<=exp(-u/2), with 0<=u<1 here. This is a modulus bound and does not discard an uncontrolled complex phase.

Taylor's integral remainder for exp(itZ), followed by expectation, gives

    |phi(t)-(1-v t squared/2)| <= (5/6)|t| cubed.

For u>=0, `0<=exp(-u)-1+u<=u squared/2`. With u=v t squared/2, the Gaussian error is at most v squared t to the fourth/8. Since v<=3 and |t|<=1/6, this is at most (9/48)|t| cubed. Thus the total coefficient is exactly

    5/6+9/48 = 49/48.

Both |phi(t)| and exp(-v t squared/2) are bounded by exp(-v t squared/3). The algebraic difference-of-powers identity, valid also for complex phi, bounds the nth-power difference by

    n(49/48)|t| cubed exp[-v(n-1)t squared/3]
    <= n(49/48)|t| cubed exp[-nv t squared/6],

because n-1>=n/2. For c>0, the integral over the whole real line of |t| cubed exp(-c t squared) is 1/c squared. Enlarging the integration domain therefore gives

    integral_(-delta)^delta |phi(t)^n-exp(-nv t squared/2)| dt
    <= 36(49/48)/(v squared n)
    <= 147/(16n) < 10/n.

The constants 49/48 and 147/16 require neither a logarithm of phi nor an asymptotic expansion, and are valid throughout the stated finite n-domain.

## 2. Two logarithms: zero cases, ties and the 2pi factor

The distances are even in t, so take t>0. Choose any nearest nonnegative integers p,q to t log 2/(2pi), t log 3/(2pi). At a half-integer tie either choice is permitted: the proof uses only residuals of absolute value equal to the corresponding distance and the usual nearest-integer upper bound. Define

    e2=t log 2-2pi p,   e3=t log 3-2pi q,
    d=max(|e2|,|e3|).

If p=q=0, the nearest-zero choice means these residuals equal the positive phases themselves. Consequently d=t log 3>=delta log 3>1/6>=n^(-1/4), since 1296=6 to the fourth. This handles the branch where the following integer-separation argument would have compared equal powers.

Otherwise 2^q and 3^p are distinct positive integers by unique factorization. This also covers either one-zero case; the positive power differs from 1. Integrating 1/u between the two integers gives

    |q log 2-p log 3| >= 1/max(2^q,3^p).

Nearest-integer bounds give

    max(q log 2,p log 3)
    <= T log 2 log 3/(2pi)+(log 3)/2.

The order of the exponents is important: the powers are 2^q and 3^p. Direct expansion of the phase residuals gives

    2pi(q log 2-p log 3)=e2 log 3-e3 log 2.

Its absolute value is at most d log 6. Combining the three displays yields the exact source prefactor

    d >= [2pi/(sqrt(3) log 6)] exp[-T log 2 log 3/(2pi)].

The given elementary inequalities make the exponent coefficient smaller than 77/620<1/8 and the prefactor larger than 31/20>1. With T=2 log n this proves d>=n^(-1/4). Thus neither ties, one-zero choices nor the all-zero branch cause an exception. No qualitative irrationality constant is substituted for this quantitative bound.

## 3. Pair defect and nth-power attenuation

Centering multiplies the uncentered characteristic function by a unit phase, so its modulus is unchanged. For the finite real law the exact identity is

    1-|phi(t)| squared
    =2 sum_(j<k) p_j p_k [1-cos(t(x_j-x_k))].

Every summand is nonnegative. Retaining the two pairs from atom 0 to log 2 and log 3 and using `1-cos u>=2 dist(u,2pi Z) squared/pi squared` gives

    1-|phi(t)| squared
    >= [4 p0 min(p_log2,p_log3)/pi squared]*(d2 squared+d3 squared)
    >= d squared/(16pi squared).

Indeed 4*(1/4)*(1/16)=1/16. The source does not lose a factor two by confusing the ordered pair expansion with its j<k form. Because d<=pi, the retained defect divided by 16pi squared is at most 1/16; the square-root exponential inequality is applicable. Hence

    |phi(t)| <= exp[-d squared/(32pi squared)]
             <= exp[-1/(320 sqrt(n))],

using pi squared<10 and the separation bound. Raising to the nth power gives exactly exp(-sqrt(n)/320). The bound is for the stated band delta<=|t|<=2 log n. It does not assert an n-independent spectral gap over all real frequencies or a density for the discrete sum.

## 4. Gaussian tail, integrated D_n and B_n assembly

For t>=delta, comparison with t/delta times the same Gaussian integrand gives

    integral_(|t|>delta) exp(-nv t squared/2) dt
    <= 2 exp(-nv delta squared/2)/(nv delta)
    <= 6 exp(-n/36)/n.

Both numerical constants use v>=2 and delta=1/6: nv delta>=n/3 and nv delta squared/2>=n/36. The two-sided outer band's total length is at most 2T=4 log n. Combining the central estimate, outer-band attenuation and entire Gaussian tail gives

    D_n(T) <= 10/n+6 exp(-n/36)/n
                    +4 log n exp(-sqrt(n)/320)
           <= 16/n+4 log n exp(-sqrt(n)/320).

For the conditional smoothing inequality (5), its first term becomes `pi/[sigma sqrt(2pi) log n]`, at most 1/log n because sigma>=sqrt(2) and pi<4. Moreover 2pi>6 implies

    sqrt(n) D_n(T)/(2pi)
    <= 3/sqrt(n)+sqrt(n) log n exp(-sqrt(n)/320) = B_n.

Here 16/6<3 and 4/6<1; the rounding enlarges the bound in the correct direction. Since 2pi/T=pi/log n<4/log n, inequality (5) then yields

    sqrt(n)|Pr(Z_n in I)-Pr(G_n in I)|
    <= 1/log n+(b+4/log n)B_n
     = (1+4B_n)/log n+bB_n = A_n+bB_n.

This checks the assembly of the declared A_n,B_n **conditional on (5)**. It neither re-proves the external approximation nor certifies its endpoint convention; those are separately retained premises. No hidden requirement B_n<1 or asymptotically large n is used in this algebra.

## 5. Gaussian replacement in (2)

For the centered Gaussian density g_n of variance nv,

    sup_y |g_n'(y)| = 1/[nv sqrt(2pi e)].

This follows by maximizing |y| exp(-y squared/(2nv)) at |y|=sqrt(nv). Uniformly in real x and b>=0, integrating the Lipschitz bound from x to x+b gives

    |integral_x^(x+b) g_n(y)dy-b g_n(x)|
    <= b squared/[2nv sqrt(2pi e)].

After multiplication by sqrt(n), v>=2 makes this no larger than b squared/(4sqrt(n)); the omitted sqrt(2pi e) is greater than one. Also sqrt(n) b g_n(x)=b exp(-x squared/(2nv))/c_sigma. Adding this error to (1) proves the source's displayed replacement (2) under the same interval-bound premise. The Gaussian has no endpoint atoms, so this replacement introduces no endpoint-convention discrepancy. At b=0 its extra error and flat-density term are zero; validity for a discrete singleton still depends on the separately reviewed interval/singleton bound, not on Gaussian density alone.

## Remaining obligations and credit

No mathematical error or failed intermediate derivation was encountered in this bounded written reconstruction; no counterexample to the stated assumptions is asserted. All source texts and earlier S4 scouting/exposure records remain preserved. No new or predecessor program, scientific checker, numerical experiment, source import, kernel or huge-onset evaluation was run. Only this written note was authored for the mathematical audit.

Outside: verifying the literal law/tilt and H, external Selberg statement/normalization, atomic endpoint sandwich, the symbolic n>=2^100 and n_LLT onset simplifications, kernel layer-cake transfer, mixed-layer normalization, source/complement/boundary/leaf terms, complete recurrence induction, physical/native/ownership/precision/compiler/outer interfaces and all selected framework assumptions. The note does not improve the onset, exponent, paid profile or frontier and claims no human acceptance.

Credit alephnan for PR6713's effective argument and its disclosed substantial OpenAI Codex assistance; the CubeJerry/PR6329 full-flow exponent contribution and the exact law/flow predecessors; zxv, Ryanson Jonathan/pinterbanget, DLamdata, Nick Petalas, Cinna Davis/1337isnot1337, Jacob Alan Sussman and retained native/precision/analytic lineage. Beurling, Selberg and Vaaler supply the classical approximation, with Laura Shou's paper providing the source's inspected statement. Elementary characteristic-function identities, integer separation and Gaussian calculus are classical. This separate AI-assisted written audit retains all that attribution and is not blind, independent human or proof-kernel review.
