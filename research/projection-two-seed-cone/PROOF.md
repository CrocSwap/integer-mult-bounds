# The complete block-two monotone seed cone

This is a scoped proof about an arithmetic recurrence, with a finite exact
certificate for two boundary seeds. It supplies no hook-rank certificate or
physical engine. This contribution was produced by Nick Petalas.

## Statement

Start at block two with real entries

    a_2 = (0,a,b),     a>0, b>=0,     t=b/a.

For integers k>=3 and 0<=r<=k use the unstrengthened projection recurrence
of Jacob Alan Sussman / PR4628 and Maximilian Lutz / PR4643:

    a_k(r) = N_k(r,r) a_(k-1)(r)
           + N_k(r,r-1) a_(k-1)(r-1)
           + N_k(r,r-2) a_(k-1)(r-2),

    N_k(r,r)   = 2^(k-r)-1 + 4^k-2^(k+r),
    N_k(r,r-1) = 2(2^k-2^(k-r)) + (2^r-1)2^(k-1),
    N_k(r,r-2) = (2^r-1)(2^(r-1)-1)2^(k-r).

The last coefficient is zero for r<2. Omit out-of-range entries of the
previous profile. All relevant coefficients are nonnegative, and

    a_k(1) = d_k a_(k-1)(1),
    d_k = (2^(k-1)-1)(2^(k+1)+1)>0.

Define T_m=a_m(m)/a_m(1), including T_2=t. Then:

1. T_m is nondecreasing for every m>=2 if and only if 0<=t<=7/3.
2. It is strictly increasing at every step if and only if 0<=t<7/3.
3. At t=7/3 the first step is a tie and every subsequent step is strict.
4. There is no nonincreasing seed in the stated domain. For t>7/3,
   T_3<T_2 and T_4>T_3, so the sequence is not monotone in either direction.

Equivalently, the nondecreasing cone is 3b<=7a within a>0,b>=0.
This resolves the block-two domain of the monotone-seed question left open
in Nicholas Stone's PR5416. Higher seed blocks remain open here.

## Necessity and the exclusion of descent

Directly applying the displayed recurrence twice gives

    T_3-T_2 = (7-3t)/17,
    T_4-T_3 = (t+13)/187.                              (1)

The second expression is positive for every t>=0. These two identities
prove necessity, rule out nonincreasing sequences, and give both directions
of motion when t>7/3. They do not by themselves prove sufficiency.

## Two modes for the entire continuous seed interval

We use Krzysztof Wojt / PR5193's fixed triangular operator and its uniform
two-step bound. Its matrix bound is a credited premise, not an audit target.
The block-two initial conditions and the classification below are new.

For a sequence f with f(0)=0 put

    (Hf)(r) = h_r f(r)+B_r f(r-1)+C_r f(r-2),
    h_r = 3/2+2^(-r)-2^r,
    B_r = 2^(r-1)+3/2-2^(1-r),
    C_r = 2^(r-1)-3/2+2^(-r).

The raw row operator is d_k I+2^k H. Let e_j(r)=0 for r<j,
e_j(j)=1, and for r>j define

    e_j(r) = (B_r e_j(r-1)+C_r e_j(r-2))/(h_j-h_r), j=1,2.

The denominators are positive since h_r strictly decreases. Thus
H e_j=h_j e_j, with h_1=0 and h_2=-9/4. In particular e_1(2)=4/3.
The seed has the unique expansion e_1+(t-4/3)e_2 on rows zero through two.

Set

    p_(m,j) = product_(k=3)^m
              ((2^(k-j)-1)(2^(k+j)+1))/d_k,
    u_(m,j) = p_(m,j)e_j(m).

Empty products equal one. Induction on m gives the full normalized profile
as the same two-mode sum. At the newly added row r=m the omitted old entry
has coefficient N_m(m,m)=0, so the induction introduces no extra hypothesis.
Consequently, for every real t and every m>=2,

    T_m(t) = u_(m,1)+(t-4/3)u_(m,2).                   (2)

The initial values are

    u_(2,1)=4/3, u_(3,1)=77/51,
    u_(2,2)=1,   u_(3,2)=14/17.

For h=h_j the scalar sequence u_m=u_(m,j) obeys, for m>=4 and x=2^m,

    u_m = alpha(x)u_(m-1)+beta_h(x)u_(m-2),
    alpha(x) = (x-1)(x+4)/((x-2)(2x+1)),
    beta_h(x) = (x-1)/(2x+1)
                * (1+2xh/((x-4)(x+1))).                (3)

For completeness, the e_j equation at r=m first gives
lambda_(m,j)e_j(m)=N_m(m,m-1)e_j(m-1)+N_m(m,m-2)e_j(m-2).
Multiply by p_(m-1,j)/d_m and use
p_(m-1,j)/p_(m-2,j)=lambda_(m-1,j)/d_(m-1).
The two coefficients simplify to (3), by the displayed definitions.
There is no division by a seed value or by a possibly zero top ratio.

## A finite certificate with a uniform infinite tail

For either mode define

    z_(m,j)=2^m(u_(m,j)-u_(m-1,j)),
    v_(m,j)=(u_(m,j),z_(m,j))^T.

Use the maximum vector norm and induced row-sum matrix norm. With

    F_h(x)=x(alpha(x)+beta_h(x)-1),
    A_h(x)=[[1+F_h(x)/x,-2beta_h(x)/x],
            [F_h(x),    -2beta_h(x)]],

equation (3) gives v_(m,j)=A_(h_j)(2^m)v_(m-1,j).
PR5193, PROOF.md Section 3, proves the rational matrix inequality

    ||A_h(2x)A_h(x)-I|| <= 4096/x
               for -15<=h<=0 and x>=64.                 (4)

Both of our h values lie in that interval. In particular,

    ||v_(m+2,j)-v_(m,j)|| <= 2048*2^(-m)||v_(m,j)||

for m>=5. For a fixed parity starting at M put

    S_M = sum_(i>=0)2048*2^(-M-2i)=8192/(3*2^M).

Expanding a finite product of I+E_i, the sum of the norm bounds of all
terms of degree n is at most S_M^n. Therefore, if S_M<1, for every
m>=M with the same parity,

    ||v_(m,j)-v_(M,j)||
       <= S_M/(1-S_M) ||v_(M,j)||.                      (5)

This estimate is uniform in the number of factors. No limiting or numerical
mixing premise is needed.

The standalone exact certificate verifies the following rational inequalities
from the new initial values in (3):

* For t=0, T_m-T_(m-1)>0 at m=3,...,17.
* For t=7/3, the difference is zero at m=3 and positive at m=4,...,17.
* At each M in {16,17}, both ||v_(M,j)||<=2, and for both boundary seeds,

      z_(M,1)+(t-4/3)z_(M,2)>1/2.                      (6)

These are finite rational checks. The generated verifier output contains
their exact endpoint state norms, scaled differences and tail allowances;
the script does not trust a handwritten numerical receipt.

For either boundary seed, 1+|t-4/3|<=7/3. By (5), the difference between
its scaled adjacent difference at m and at M is at most

    (14/3) S_M/(1-S_M)
       = 14/69   at M=16,
       = 14/141  at M=17.

Both are less than 1/4. Equation (6) thus makes every subsequent scaled
adjacent difference greater than 1/4, separately on both parities.
Together with the finite prefix this proves strict increase after the
stated possible initial tie for both boundary seeds.

Finally, for 0<=t<=7/3, the seed and every adjacent difference are convex
combinations of their values at t=0 and t=7/3. This follows from linearity
of the raw recurrence and the seed-independent positive normalization.
Every step after the first is strictly positive at both endpoints. The first
step is (1). This proves sufficiency and the full classification.

## Scope and credit

The new result is the complete continuous block-two cone, with its strict
and equality cases. The argument consumes the general fixed-operator and
uniform transfer inequality of Krzysztof Wojt / PR5193. Nicholas Stone /
PR5416 poses the general classification and supplies separate block-four
parity asymptotics. JoyboyBrian / PR5184 proves descent for the different
fixed block-four hook seed. Nick Petalas / PR5151 supplies a general limit
theorem; none of these predecessor results is recomputed as a deliverable.

The recurrence and engine motivation remain Jacob Alan Sussman / PR4628
and Maximilian Lutz / PR4643, with eumemic / PR288, Swapnil Jain and the
retained certificate-method lineage. Elementary linearity, matrix product
bounds and convexity are classical. No global literature priority is claimed.

This is not a theorem for the optional triangle/max strengthening, higher
seed blocks, arbitrary signed seeds, a=0, or a physical engine. Hook-rank
and representation premises, native operations, dirty restoration, precision,
stock, compiler, complete cost and all five selected framework assumptions
remain outside scope. No new kappa or selected-frontier change is claimed.
Independent human and formal proof-kernel review are unclaimed.
