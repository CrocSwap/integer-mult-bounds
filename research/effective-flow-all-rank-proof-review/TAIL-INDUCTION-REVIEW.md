# External written review of PROOF sections6–8

Verdict: **PROVED-CONDITIONAL for the reviewed propagation/induction steps.**
No missing implication or counterexample was found in sections6–8, provided
the exact complete-flow identities, rank ranges, positive finite constants,
early-layer estimate and uniform local-limit bound stated by the source hold.
This is an external audit of a theorem the source already claims, not a new
exponent, onset, rank census, finite-margin calculation or supplier admission.

Source: alephnan PR6713 head
`cd666f05c4e9006025b634687cc493911c8371c8`, exact retained
`session-10/INPUTS/PROOF.md` (16,628 bytes; SHA256
`e7dbe4e1705a307e9eb32f6f06b340fb2c49948cc749110d6be2c6fb3da94ea9`).
The review used that text and hand
integer/rational algebra only. No scientific program was read, imported,
compiled, executed or newly written. Earlier source/LOCAL_LIMIT review exposure
is disclosed; this is separate AI written reasoning, not a blind human review.

## Premises and exact quantity being bounded

The argument assumes the complete default-height mirror decomposition and
conservation identity from the pinned flow predecessors, including **every**
unmatched boundary/terminal exit and its multiplicity. It assumes the actual
recurrence has finite nonnegative histograms, C_N>0, N/121<z<=N and
1<=e<=48N/121<N. These are not independently re-established here.

Also assumed are 0<q<247/250, 0<J<2000, c_sigma<4, sigma^2>2,
tau>3/400, B_leaf<4*10^6, D_full>40000, Q=52,092,027,504,
|M|<=5Q and sup|f|<=Q. The exact finite q/J/margin/rank calculations remain
source premises, not a new census. Uniform LLT(3) with epsilon=10^-8 and the
source section5 early-layer discrepancy<1563 are inputs to this note; their
own proof audits are separate.

Write w_h=(1-q)q^h and F_h=c_sigma*sqrt(G)*E f(u_h). Section3's exact
decomposition, after dropping only nonnegative root capacity, gives

    D_N/F_G >= sum_(h=0)^(G-1) w_h F_h
                 - B_leaf*c_sigma*sqrt(G)*E g(u_leaf).

Here g(u)=exp(-tau*u) for u>=0. The full limiting expression is
D_full=M-B_leaf/tau. Positivity of A,J,c_sigma,G gives F_G>0. No division
by an approximately estimated source count is used.

## Middle layers and the missing infinite weight of M

Let n=n_LLT and G>=2n+2. For3000<h<=floor(G/2),
ell=G-1-h>=G/2-1>=n. Moreover sqrt(G/ell)<=2. Conditional on the
target-word sum, any mixed window becomes an interval of length at most5 in
the paid centered sum. LLT(3) therefore bounds its scaled mass by
2(5+epsilon)<12, without requiring a bound on that interval's location.
The weighted left-end kernel bounds sum to at mostQ, so |F_h|<=12Q.
Overlapping windows need no cancellation or disjointness assumption.

The comparison with M must include an **infinite** geometric tail, even though
there are only G mixed layers. The exact useful decomposition is

    sum_(h=0)^(G-1) w_h F_h - M
      = sum_(h=0)^3000 w_h(F_h-M)
        + sum_middle w_h F_h + sum_late w_h F_h
        - M*sum_(h=3001)^infinity w_h.

Thus early errors total<1563 because their weights sum to at most1. Middle
absolute values cost at most12Q*q^3001, and the final missing-M term at most
5Q*q^3001. This explains17Q, including the late/infinite missing M exactly
once. It is not a silent assumption that the finite weights sum to1.

From log(q)<-3/250, q^3001<exp(-36). The hand exponential bound below gives
exp(36)>10^15. Also

    17Q=885,564,467,568 <10^12,

so this middle-plus-missing-M charge is strictly below1/1000.

## Late layers, including zero paid letters

For h>floor(G/2), ell may be0. No LLT is used: directly |F_h|<=4Q*sqrt(G),
since the random variable's law is a probability measure and |f|<=Q. The sum
of late weights is at most q^(floor(G/2)+1)<=q^(G/2). Hence

    late <=4Q*sqrt(G)*q^(G/2)
         <=4Q*G*exp(-3G/500)
         <=8Q/((3/500)^2*G).

The last step is the elementary exp(x)>=x^2/2 for x>0. At G>=10^18 its
numerator/denominator comparison is

    8Q/((3/500)^2*G)
      = (2,000,000Q)/(9G)
      <=104,184,055,008,000,000 /9,000,000,000,000,000,000 <1.

This covers the final h=G-1 layer with no paid letters and makes no Gaussian
or central-limit assertion for a deterministic/short paid sum. The lower
bound G>=10^18 itself follows from G_0=2*2^(10^12)+2; already
2^60=(2^10)^6>10^18. No enormous integer is materialized.

## Whole leaf half-line and atomic endpoints

For leaves ell=G>=n_LLT and u=delta-Z_G. Reflecting a subinterval of
[0,5000) gives a Z_G interval of length<=5000 whose left endpoint has absolute
value<5002, uniformly for every0<=delta<a<2. Since sigma^2>2, LLT(3) and
1-exp(-x)<=x give interval discrepancy from Lebesgue measure at most

    epsilon+5000*5002^2/(4G)
      =10^-8+31,275,005,000/G <5*10^-8.

Decreasing continuous exp(-tau*u) has left value1. The source's Stieltjes
initial-interval argument therefore gives the same bound for its integral on
[0,5000), including a possible atom at0 and excluding a possible atom at5000.
The LLT explicitly allows all endpoint conventions, so reflection neither
loses nor duplicates either endpoint.

The intervals [5000+j,5001+j), j>=0, partition the **whole** remaining
half-line, with every atom at a partition point assigned once. Their scaled
probabilities are at most1+epsilon<2 by the location-uniform LLT(3). Positive
summands justify summing all intervals by monotone convergence, giving

    scaled leaf tail <=2*exp(-5000*tau)/(1-exp(-tau)).

This is a complete geometric-series bound, not a finite window/cutoff. It
also remains valid when some intervals are outside the finite support.
Tau>3/400 and exp(-37.5)<10^-16 imply

    1-exp(-tau)>=tau/(1+tau)>3/403,
    scaled tail <(806/3)*10^-16 <3*10^-14.

Separately, the Lebesgue tail is exp(-5000*tau)/tau
<(400/3)*10^-16<2*10^-14. Both tails must be charged when comparing with
the whole limiting integral1/tau; the source does so. Multiplying by
B_leaf<4*10^6 gives total leaf error

    <4*10^6*(5*10^-8+5*10^-14)=1/5+2*10^-7.

The terminal paid letter r was already completely summed in P(s). The base
cap is u>=0; replacing it by u>=log(r) would be an unallowed second terminal
cap. Sections6–8 make no such replacement. The half-line bound therefore
does not silently discard high terminal ranks or unmatched exits.

## Small hand certificate for the two exponential estimates

No large-power program is needed. Positive Taylor terms give

    exp(3)>sum_(j=0)^8 3^j/j!
          =89641/4480=20+41/4480>20,
    exp(3/2)>1+3/2=5/2.

Thus exp(36)=exp(3)^12>20^12=4,096*10^12>10^15, and

    exp(37.5)=exp(3)^12*exp(3/2)
             >20^12*(5/2)=10,240*10^12>10^16.

This independently supplies exactly the two estimates used above. It avoids
expanding the source's larger(8/3)^36 and(163/60)^37 comparisons; those large
integer comparisons were not independently recomputed here.

## Total error, every offset and strong induction

The mixed error is<1563+1/1000+1, and the leaf error<1/5+2*10^-7.
Their sum is<1564.2010002<1600. Consequently

    D_N/F_G >D_full-1600>40000-1600=38400>0.

Since F_G,C_N are positive, H_N(s)=1-D_N/C_N<1. All uses of the leaf and
early/middle estimates are uniform in the actual floor offset delta; the late
estimate is location-free. For every integer N>=N_0=121*5^G_0,
N/121>=5^G_0, so floor(log_5(N/121))>=G_0. This is every such integer,
not only the subsequence N=121*5^G. Offset0/cap equality is included by the
endpoint-uniform LLT and inherited complete decomposition.

For the initial-range step, use the exact inherited conservation identity
sum c_z*z-sum d_e*e=608U_N(1)>0. Applying the recurrence to the linear test
function yields exactly

    [sum c_z*(N-z)+sum d_e*e]/C_N
      =N-608U_N(1)/C_N <N.

All coefficients are nonnegative. Each N-z is an integer in[0,N), and each
exit e is in[1,N). The prescribed base values therefore prove L(n)<=n for
all n by ordinary strong induction. This deduction uses the complete identity
and full exit histogram, not independently rechecked P(1),T(1) or U moments.

As0<s<1, for1<=n<N_0,
n=n^s*n^(1-s)<=N_0^(1-s)*n^s. For n>=N_0, apply the same claimed majorant
to every positive smaller child; L(0)=0 handles a possible z=N source. The
exact recurrence gives

    L(n)<=N_0^(1-s)*n^s*H_n(s)<=N_0^(1-s)*n^s.

The finite initial-range inequality is proved symbolically by L(n)<=n, so no
uncomputed exhaustive initial-range census is needed. N_0 is a sufficient
symbolic onset and constant, not the first successful rank or practical cost.

## Scope and credit

This note closes no selected framework assumption and changes no exponent,
frontier, paid profile or physical admission. Rebinding the exact finite flow,
numeric margin/q/J and all source identities is outside this review; the
uniform LLT and early-layer proofs are explicit separate premises. Full
historical recurrence correctness and any transfer to a real recursive caller
remain distinct from the reviewed propagation once those premises hold.

Credit alephnan6713 for the source theorem; zxv4436/4483, Ryanson Jonathan /
pinterbanget4459 and mirror-flow lineage, DLamdata6118, Nick Petalas6125/6128,
CubeJerry's exponent predecessor, Cinna Davis/1337isnot1337, Jacob Alan Sussman
and retained native/precision/analytic contributors. Classical geometric tails,
Stieltjes integration, exponential estimates and strong induction remain
classical. This external written audit uses substantial OpenAI Codex assistance
and separate AI reasoning, without human or proof-kernel certification.
