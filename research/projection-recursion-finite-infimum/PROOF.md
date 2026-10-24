# Strict finite-block descent and exact infimum of the projection recurrence

This is a theorem about the exact recurrence with seed
`a_4=(0,27456,48576,68320,86592)`. It does not certify the block-four
hook ranks, establish a physical implementation, or change κ. The recurrence
and seed are due to Jacob Alan Sussman (PR4628); the projection counts and
independent audit are Maximilian Lutz's PR4643. The exact limit used in §6 is
PR5151, head `e6c8e945a47dcc4a6f08974682090fc7f5e221a3`.

## 1. Statement and recurrence

For k>4 and 0≤r≤k set

    a_k(r)=A_k(r)a_(k−1)(r)+B_k(r)a_(k−1)(r−1)+C_k(r)a_(k−1)(r−2),
    A_k(r)=2^(k−r)−1+4^k−2^(k+r),
    B_k(r)=2(2^k−2^(k−r))+(2^r−1)2^(k−1),
    C_k(r)=(2^r−1)(2^(r−1)−1)2^(k−r)  (r≥2),
    C_k(0)=C_k(1)=0.

Terms with out-of-range previous indices vanish. All coefficients are
nonnegative, A_k(k)=0, and A+B+C=4^k−1. Also a_k(0)=0 and

    a_k(1)=q_k a_(k−1)(1),   q_k=(2^(k−1)−1)(2^(k+1)+1)>0.

**Theorem.** T_k=a_k(k)/a_k(1) strictly decreases for every k≥4, and
its infimum is 439277/149175. The infimum is not attained at any finite k.

The new assertion is descent at *every* finite block, not extrapolation from
sampled blocks. Sections 2–5 prove it using a fixed finite rational certificate
and uniform inequalities. Section 6 invokes the predecessor's exact limit.

## 2. Global bound and the two boundary inequalities

Write R_k(r)=a_k(r)/a_k(1). The nonnegative row sums imply

    max_r R_k(r) ≤ (41/13) ∏_(j=5)^k (4^j−1)/q_j
                = (41/13)(33/15)(2^k−1)/(2^(k+1)+1)
                < F,                 F=451/130.

The empty product at k=4 gives the same bound. No monotonicity of the profile
is used here. Put M=2^k and x=2^r. For 2≤r≤4 and k≥5,

    A=M²−1+M(1/x−x),
    B=M(3/2+x/2−2/x),
    C=M(x/2−3/2+1/x),  q=M²−3M/2−1.

Here A−q<0 and q≥M²/2, so

    |R_k(r)−R_(k−1)(r)|
      ≤ F (|A−q|+B+C)/q
      = F M(2x−2/x−3/2)/q ≤4xF/2^k.

Consequently for every m≥K≥4 and fixed r≤4,

    |R_m(r)−R_K(r)| ≤4·2^r F /2^K.                 (1)

The bound follows by summing the finite geometric series and then bounding
it by its infinite sum; no assertion about a limit is needed.

A fixed exact-integer recurrence certificate for 4≤k≤14 verifies

    D3(k):=R_k(3)−(13/10)R_k(2)>1/32,
    D4(k):=R_k(4)−(29/26)R_k(3)>1/16.              (2)

These are 22 rational inequalities. They can equivalently be checked by
positive integer cross products; the replay retains both methods. At K=14,
(1) bounds the subsequent variation of D3 and D4 respectively by

    4F(8+(13/10)4)/2^14 =14883/1331200 <1/64,
    4F(16+(29/26)8)/2^14=36531/1730560 <1/32.

Thus D3(k)>0 and D4(k)>0 for *all* k≥4. This is the only finite certificate
in the proof; the summable bound, not a sample trend, supplies the infinite tail.

## 3. A weighted ordering preserved in the interior

Let h(r)=1−3/2^(r+1) and u_k(r)=a_k(r)/h(r), for r≥2.
We prove u_k(2)≤u_k(3)≤…≤u_k(k). The boundary comparisons are exactly
D3(k)≥0 and D4(k)≥0 since h(3)/h(2)=13/10 and h(4)/h(3)=29/26.
At k=4 these constitute the whole assertion.

Suppose the assertion holds at k−1. For r≥5, the weighted row of the
recurrence has coefficients

    K_r(r)=A_k(r),
    K_r(r−1)=B_k(r)h(r−1)/h(r),
    K_r(r−2)=C_k(r)h(r−2)/h(r).

Its action on u_(k−1) is u_k(r). Compare it with K_(r−1); both supports
lie in indices≥2. At r=k extend u_(k−1)(k)=u_(k−1)(k−1); the extension
has zero coefficient because A_k(k)=0.

The total row mass, with M=2^k,x=2^r, is

    S(x)=M²−1−3M−(3M/2)/(x(x−3/2)).               (3)

It increases with x≥4. The upper-tail difference at index r−1 is

    K_r(r)+K_r(r−1)−K_(r−1)(r−1)
      = (3M/4)(x²−10x+10)/(x(x−3/2)) ≥0,         (4)

since x≥32 and x²−10x+10>0 there. At index r the difference is
A_k(r)≥0. At index r−2 it equals

    S(x)−S(x/2)+K_(r−1)(r−3)≥0;

at index r−3 (or any smaller index) it is S(x)−S(x/2)≥0.
Thus every upper tail of K_r dominates that of K_(r−1). The elementary
summation-by-parts identity for a nonnegative nondecreasing sequence v,

    Σ_s (K_r(s)−K_(r−1)(s))v(s)
      = v(2)Σ_s(K_r(s)−K_(r−1)(s))
        + Σ_(t≥3)(v(t)−v(t−1))Σ_(s≥t)(K_r(s)−K_(r−1)(s)),

is nonnegative. Apply it to v=u_(k−1). Therefore u_k(r)≥u_k(r−1)
for every r≥5. The two already proved boundary inequalities complete the
induction. No order involving u_k(1) is assumed; that order need not hold.

Equations (3) and (4) follow by inserting the displayed A,B,C and
h(r)=(x−3/2)/x. They are rational identities, not fitted inequalities.

## 4. The top profile inequality

In particular, for every k≥4 and M=2^k,

    a_k(k−1)/a_k(k) ≤ h(k−1)/h(k)=(2M−6)/(2M−3). (5)

The denominator is positive: the seed is positive at r≥1 and the recurrence
preserves this at all those indices (the top has B>0). This also justifies
all ratios used below.

## 5. Strict descent for every block

The top row at block k+1 and the one-step normalization give

    T_(k+1)=(2M−1)[(M+2)a_k(k)+(M−1)a_k(k−1)]
            /[(M−1)(4M+1)a_k(1)].

Subtracting T_k shows that strict decrease is equivalent to

    a_k(k−1)/a_k(k) < (2M²−6M+1)/(2M²−3M+1).

The right side exceeds the upper bound in (5) by exactly

    3/[(2M−3)(2M²−3M+1)]>0.

Hence T_(k+1)<T_k for every k≥4, including the first step. For source
calibration, T4=41/13, T5=834241/278850 and T6=1188222/399685.

## 6. Infimum and scope

PR5151's exact projection-recursion limit theorem, applied to this same
block-four seed, gives lim_(k→∞) T_k=439277/149175. Together with strict
descent this proves the stated infimum and its nonattainment at finite k.
We retain the pinned predecessor proof as a read-only source; its limit is
not inferred from finite output here.

The result is unconditional for the stated numerical recurrence. Interpreting
its values as engine lower bounds still requires the predecessor's hook-rank
and representation premises. In particular the input 48576 and 68320 ranks
are not certified by this package. There is no universal assertion for other
seeds, no enlarged gate model, and no improvement of the selected κ.

## Open next questions

Certify the two block-four hook ranks with independently replayable minors.
A separate question is to characterize which seeds obey strict finite descent;
ordinary monotonicity or concavity of the seed alone is not a sufficient
substitute for the weighted boundary inequalities proved here.
