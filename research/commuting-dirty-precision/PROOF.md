# Commuting interval transport for the target-dependent PR1054 word

This is a conditional local accuracy theorem for the unchanged rounded word.
The all-size argument below uses the pinned written lemmas of PR1085 and
PR1278, not extrapolation from our finite tests. No minimum-precision or
multiplication-exponent claim follows.

## 1. Interface and source binding

Retain Ali Romman's PR1054 at `6bc675be1554b3a3be771147f21f9dc2c6dae50a`:
its constant-coefficient PR985 rounded leaves, length-independent admission,
effective-depth/zero-subtree argument, exact inverse grid word, preparation
and complete operation accounting. Source, target and reserved-depth scratch
are distinct; phases are immutable and do not alias mutable data. Cuts are
complete outer-leaf boundaries, not internal rounded-operation boundaries.

For n factors, the positive ideal word executes U,V,U^-1,V^-1, where
U adds the complete left factor product into the depth's connector and V
adds the complete right product into the target. The negative word is the
literal inverse. The actual PR1054 nested `run` uses exactly the floor/ceil
split, argument wiring, signs and shared deeper scratch of PR628 `compose`.
Their frozen source ASTs are compared with numerical leaves instrumented;
the source itself exhibits the same four recursive calls for every n.
The physical carrier swaps conjugate a logical leaf by a swap and its inverse;
PR1054's already charged two-tape realization and distinct-array requirements
remain inherited. They do not change the logical leaf-boundary word.

Let the ideal factors commute pairwise, with every subset product (including
empty) of norm at most G >= 1. PR1054's actual cyclic factors satisfy this
conditional premise because every factor is a rational function of the same
immutable isometry U=tau Z_M_len^w, where M_len is the cyclic array length;
the single scalar r also commutes. The inherited
complementary-factor argument gives the stated G. Different mutable phases or
unrelated operators do not satisfy this premise automatically.

Put h=ceil(log2 n), C=h+2. Hanson Sun's PR1085 proves every prefix and inverse
prefix has coefficient absolute row sum at most C in the free factor algebra.
Charles Bethin's PR1278 proves every monomial surviving in every two-cut
interval uses each factor index at most once, including intervals crossing two
occurrences of the same child and the reused deeper scratch. Multiplication
of the prefix and inverse-prefix matrices has coefficient row sum at most C^2.
Cancellation cannot increase it. Commutation puts each squarefree monomial
in subset order, so, in the maximum joint-register norm,

    B = C G                 bounds every prefix and inverse prefix,
    L = C^2 G               bounds every interval in either cut order.

Both ingredients are needed. The generic ordered-subset case has only B^2.
PR1244's noncommuting obstruction remains valid; this does not weaken its
hypothesis or claim that unordered products have the ordered-subset bound.

## 2. Nonlinear errors and inverse targets

Let r >= 1 bound the inherited leaf scale, 0 < beta <= 1/2, u=2^-W,
and D >= 0 bound every incoming array. Retain PR1054's all-length admission
`48(g+ceil(log2(W+1))+1) u <= beta^3`, where g=ceil(log2(1/beta)).
In particular W >= 4g+16 suffices. The exact paid leaf count is

    N = 3 q n - 2 q^2,       q=2^floor(log2 n).

PR1054 supplies the target-independent *error bound* (not a target-independent
rounded increment)

    ||delta|| <= a u (||source||+1),   a=68(r+1) beta^-5.

For a negative leaf with input y and output z, exact inversion gives
`y=z+A x+delta(x,z)`. The positive estimate holds for every preimage target z,
so the negative error satisfies the same bound at its unchanged source x.
This step does not treat a rounded leaf as linear or additive in its source.

Let T be the largest actual joint norm at complete leaf boundaries. Insert
the actual nonlinear error of each executed leaf into the ideal linear word.
Variation of constants and the interval bound, applied to these fixed error
vectors after the execution, give

    T <= B D + t(T+1),       t=N L a u.

If t <= 1/2, then T <= Dstar=2 B D+1. The final execution error is at most

    E = 2 N L a u (B D+1).                                  (1)

The execution is finite by the retained stable-closure admission. Thus taking
its maximum T and rearranging this inequality does not assume a prior bound
on rounded intermediate targets. This is the same argument as PR1054, with
its B^2 replaced only at the interval step by L.

## 3. Internal inverse preimages remain paid

Accuracy alone does not control internal leaf values. PR1054 supplies the
forward internal bound `512(r+1)(Dstar+1)/beta^7`, including zero tails.
For an inverse leaf, first bound its positive preimage:

    Dpre <= (2+r/beta) Dstar+1.

Indeed the preimage differs by an ideal factor of norm at most r/beta and an
error at most a u(Dstar+1); t <= 1/2 implies a u <= 1. Reversing the positive
word traverses that preimage's entire forward path. Since
`Dpre+1 <= (r+2)(Dstar+1)/beta`, both directions are covered by

    V = 1024(r+1)(r+2)(B D+1)/beta^8.                        (2)

The eighth power of beta is retained. Reducing G in error transport does not
license deleting the inverse-preimage factor or substituting the negative
call's incoming target for its positive preimage. A signed component reserve
of `ceil(log2 V)+2` remains sufficient. Block swaps add no magnitude.

## 4. Explicit budgets and a cubic envelope

For generic rational parameters, a sufficient width is

    W = max(w_input, 4g+16,
            p+2+ceil(log2(N L a (B D+1)))).                  (3)

Then (1) is at most 2^(-p-1). Since B D+1 >= 1 and p >= 0, (3) also ensures
t <= 1/4, hence the required feedback bound. No incoming grid is coarsened.
The signed integer width is given after (2).

For the certified prime-power interface r >= 3, retain all PR1054 preparation
parameters, with n=r-1, ell=ceil(log2 r), phi=EulerPhi(r), m>=0, D<=2^m:

    d0 = 1+2ell+r n phi,
    a0 = 2d0+r+2,
    g  = d0+ell+2r+2,          beta=2^-g,
    e  = max(d0+1,a0+1,p+2a0+m+4),
    b_factor = max(n ell,e+r+3).

These inherited analytic/factor-preparation assumptions give G<=2^K where
`K=a0+2r+ell`. Let

    c = ceil(log2(h+2)),
    J = K+c,                  B <= 2^J,
    H = K+2c,                 L <= 2^H,
    A = 5g+ceil(log2(68(r+1))).

The resulting fully explicit sufficient widths are

    W = max(w_input, 4g+16, p+3+ceil(log2 N)+A+m+J+H),
    I = J+m+8g+2ell+16.                                      (4)

Indeed B D+1 <= 2^(J+m+1), and (1) is bounded by
`2^(ceil(log2 N)+H+A-W+J+m+2) <= 2^(-p-1)`.
The integer reserve (2) follows from the same algebra as PR1054 with the
smaller J. Its coefficient error still costs at most 2^(-p-3); preparation
plus execution is less than 2^-p. The supplied root factorizer, stable margin,
Neumann estimate and original kernel approximation are not new results here.

For an all-size coarse envelope use phi<=r, ell,h,c<=r,
`ceil(log2 N)<=1+2h`, and `ceil(log2(68(r+1)))<=ell+8`.
The third term in (4), minus p+m, is at most

    9r^3 - 9r^2 + 47r + 35 <= 15r^3.

The difference is `(r-3)(6r^2+27r+34)+67`, nonnegative for r>=3.
The admission term obeys `4g+16 <= 4r^3-4r^2+20r+28 <= 15r^3`:
its difference is `(r-3)(11r^2+37r+91)+245`. Therefore

    W <= max(p,w_input)+m+15r^3.

The signed integer width only decreases from PR1054's bound, so
`I<=m+15r^3`; the unchanged factor width remains `b_factor<=p+m+7r^3`.
These are convenient sufficient envelopes, not sharp constants. In particular
the leading bound is still cubic, and the lower-order coarse envelope is not
used to choose the explicit widths.

At r=64, p=128, m=20 and w_input=0, (4) gives W=1,162,598 and I=1,291,709,
compared with PR1054's W=1,420,902 and I=1,291,719. Fractional reduction:
258,304 bits. Preparation still uses 516,499 factor bits, 4,000 leaf calls
and six borrowed arrays. This is a comparison to that exact PR1054 contract;
PR1085's similar-looking 1,162,523 number concerns PR905's different leaf
budget and is not superseded or combined numerically here.

## 5. Complete cost and limits

The actual word, source access, carrier swaps, restoration, coefficients and
child calls are unchanged. Write M_len for the data-array length, distinct
from the interval norm bound L above. Retain PR1054's per-leaf bounds
1280 M_len scalar products/divisions and 4096 M_len record moves, and
full-kernel bound `8192(N+1)(h+2) M_len` data-record moves on two tapes.
Let Aword=W+I and Bdesc
include the actual immutable root, margin, multiplier and unit gauge lengths.
With M(s) paying for rounded multiplication and division, the complete bill is

    preparation + O(N M_len M(Aword+Bdesc))
                + O(N(h+2) M_len (Aword+Bdesc)) + O(N M_len).

Long stride/gauge descriptors remain extra input work; preparation retains
its supplied soft-O(r^3(p+m+r^3)) bill. Effective numerical depth cannot
replace structural depth in movement or recursion counts. No additional clean
array, early exit, removed leaf, or free access is used.

Our rounded controls execute small stable rational factor families at their
new generic widths, compare the complete ideal product by a finite geometric
oracle, check both standalone signs, dirty restoration, literal indexed
accesses, signed internal guards, and unchanged paid-operation counts versus
the old finer grid. They are not an execution of the million-bit radix-64
example, an all-size root factorizer, physical compiler, full supplier cold
replay, complete transform, formal proof, or new kappa.
