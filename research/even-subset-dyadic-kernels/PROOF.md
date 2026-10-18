# Complementary even-subset fitting kernels

Let n be odd, k even and2<=k<n. Index ports by k-subsets S of[n]. Put
q_S=1+1_S in F2^n. It is the indicator of the complement of S, of odd
weight n-k, so q_S dot q_S=1. For t=|S intersection T|,

    q_S dot q_T = n-2k+t = 1+t (mod2).

Set d=k/2 and P(t)=binomial(t/2,d), interpreting the binomial as a degree-d
polynomial. It has P(k)=1 and P(t)=0 at every even t=0,2,...,k-2.
Consequently K(S,T)=P(|S intersection T|) has unit diagonal and vanishes
on every forbidden distinct binary pairing. The labels are distinct.

## Dyadic coefficients

For every integer t, P(t) is dyadic. For even t it is an integer. For odd t,
write the numerator as a product of d consecutive terms with step2 and divide
by2^d d!. For each odd prime power p^a, the progression is a complete residue
cycle modulo p^a, so at least floor(d/p^a) factors are divisible by p^a.
Summing over a shows that the numerator cancels the whole odd part of d!.
Only a power of2 remains in the reduced denominator. The argument also covers
negative integer t.

Newton interpolation in the binomial basis gives

    P(t) = sum_(j=0)^d c_j binomial(t,j),
    c_j = sum_(i=0)^j (-1)^(j-i) binomial(j,i) P(i).

All c_j are dyadic, and c_0=0. For each j-subset J, use the source feature
1_(J subset S) and target coefficient c_j 1_(J subset T). Summing over J
reconstructs K exactly, since there are binomial(t,j) common j-subsets.
This is an explicit dyadic factorization, not a side computation of I-K.

## Exact support frames

For a nonzero degree-j coefficient, the source feature indexed by J is
supported on S containing J. Each q_S vanishes on J, hence lies in the
coordinate frame U_J={x:x_i=0 for i in J}, of dimension n-j.
Its support spans all U_J. Indeed, on the n-j coordinates outside J the
q_S are all (n-k)-subset indicators. Their weight n-k is odd and lies between
1 and n-j-1. Differences of two such subsets differing in one element give
every pair vector e_a+e_b. These span the even-weight subspace; any one odd
indicator supplies the remaining dimension. This proves the claimed span.
Thus the algebraic separate-encoder support-rank sum is

    C = sum_(j:c_j!=0) (n-j) binomial(n,j).

No compiler or physical copy tree is inferred from that sum. At(n,k)=(25,6),
V=177100, c_1=1/16,c_2=-1/8,c_3=1/8, there are 2625 features and C=58100.

## What the finite checks cover

The exact receipt records every count. The verifier checks all ordered
port pairs and every actual feature-support span for(9,4),(11,6),(11,8).
It checks the complete interpolation at all possible intersections in 15 larger
cases, plus dyadic coefficient controls through k=24. The proof above covers
all admissible odd n and even k; the finite cases are regression evidence.
Three explicit corruptions reject a wrong diagonal normalization, omission
of the complement, and omission of the highest-degree feature.

## Remaining obligation

Construct I-K with legal frames and arbitrary dirty restoration, then price
both orientations, all field lifetimes, ownership, precision and tape. Until
then this is an algebraic decoder family with no new kappa or supplier.
