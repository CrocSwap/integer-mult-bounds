# A uniform root choice for the Newton Fourier factors

## Completed component

Let `q` be an odd prime and let `zeta=exp(2 pi i/q)`. There is an
explicit search, with polynomial cost in `q`, for a unit `a` modulo
`q` such that every partial product

    H_j = product_(s=1)^j (1-zeta^(a s)),    0<=j<q,

satisfies

    2^(-1000 h^3) <= |H_j| <= 2^(1000 h^3),
    h=ceil(log2(q)).

Use `u=zeta^a` in the imported exact-width Newton compiler. This does
not change its Toeplitz identities. The output is the ordinary Fourier
output with a unit permutation of its row indices. The unit can also
be included in the output CRT formula. The search and the permutation
are explicit. No random choice or unproved prime property is used.

This repairs the exponential coefficient bound of the canonical-root
Newton factorization used in our first candidate. It does not supply
the missing fast fixed-tape sector packing or a new multiplication
exponent. Those operations must have their own full paid proof.

## Integer search and termination

Set `B=16h`. Test `a=1,...,q-1` in order. Accept precisely when

    B*j*min(a*j mod q, q-(a*j mod q)) >= q

for every `1<=j<q`. This uses exact integers of `O(log q)` bits.
For a fixed `j`, multiplication by `j` permutes the nonzero residues
because `q` is prime. Fewer than `2q/(Bj)` possible `a` fail this
test. The number that fail at some `j` is therefore less than

    (2q/B) sum_(j=1)^(q-1) 1/j.

The harmonic sum is at most `1+ln q<=2h`. Hence the number is less
than or equal to `q/4<q-1`. At least one `a` passes. The complete
search has `O(q^2)` integer tests, so its bit cost is polynomial in
`q`. In the small-prime working length, `q` is polynomial in the
logarithm of the global length. This setup is additive polynomial
work; it is not a full-array table.

The admissible set is unchanged by `a -> q-a`. The first accepted
`a` is below `q/2`, so the initial convergent denominators `1` and
`floor(q/a)` are distinct.

For the chosen rational rotation `alpha=a/q`, the test gives

    distance(j alpha, Z) >= 1/(Bj),    1<=j<q.

## A prefix discrepancy bound

Let `p_n/q_n` be the continued-fraction convergents of `alpha` before
the final denominator `q`. The elementary convergent inequality gives

    |alpha-p_n/q_n| <= 1/(q_n*q_(n+1)).

Thus `distance(q_n alpha,Z)<=1/q_(n+1)`. Combining this with the
search condition gives `q_(n+1)<=B q_n`. The partial quotients are
therefore at most `B`. Successive denominators obey
`q_(n+2)>=2 q_n`, so there are at most `2h+1` convergents.

For any `j<q`, greedily use the largest convergent denominator no
greater than the remaining prefix length. Each denominator occurs
at most `B` times, since the remainder is below the next denominator.
This partitions the first `j` rotation points into at most
`B(2h+1)` consecutive blocks.

A block of `q_n` consecutive rotation points differs, on the circle,
by at most `1/q_(n+1)<=1/q_n` from a shifted equally spaced grid of
`q_n` points. For any interval, each of its two boundary neighborhoods
contains at most four grid points. The grid's interval count differs
from its expected count by at most two. The count error of the block
is therefore at most ten. Adding the blocks gives the uniform bound

    sup_I |count_(s<=j){s alpha mod 1 in I}-j*length(I)|
        <=10 B(2h+1) <=480 h^2.

All terms are explicit. This argument uses the usual convergent
identity, which follows by substituting the remaining continued
fraction tail into the two preceding numerator and denominator
recurrences. The final exact convergent has zero error; it is not
needed for a prefix shorter than `q`.

## Bounds for the sine product

Put `f(x)=ln(2 sin(pi x))` on `(0,1)`. Cap it at its value at `1/q`
within distance `1/q` of each endpoint, and call the result `f_q`.
Every nonzero residue `s a mod q` has distance at least `1/q`, so
the cap does not change the sampled values.

The integral of `f` on `(0,1)` is zero. One direct proof uses
`sin(2x)=2 sin(x) cos(x)` and the equal integrals of `ln sin(x)` and
`ln cos(x)` on `(0,pi/2)`. The cap raises that integral by less than
`4/q`: use `sin(pi/q)<=pi/q` and `sin(pi x)>=2x` for
`0<=x<=1/q`. Each endpoint contributes less than `2/q`.

The total variation of `f_q` is at most `2 ln q`, because
`sin(pi/q)>=2/q`. Integration by parts against the prefix count
function therefore gives

    |sum_(s=1)^j f_q(s alpha)-j*integral(f_q)|
        <=2 ln(q)*480 h^2.

For completeness, this is the ordinary bounded-variation estimate:
subtract the uniform measure of mass `j`, integrate its cumulative
count error against the differential of `f_q`, and bound that
differential by its total variation. The endpoint term is zero.

The integral term is nonnegative and below four for `j<q`. Divide by
`ln 2` and use `ln(q)<=h ln 2`. The absolute base-two logarithm of
`H_j` is at most

    4/ln(2)+960 h^3 < 6+960 h^3 <=1000 h^3.

This proves both bounds for every prefix product, including `H_0=1`.

## Exact Newton identity and the cheap change of root

The imported local compiler has

    F_q(u)=N D_N^-1 N^T,
    N_(i,k)=(-1)^k u^(k(k-1)/2) H_i/H_(i-k)  for i>=k,
    N_(i,k)=0  for i<k.

Its Toeplitz coefficient is `h_j=1/H_j`. The reciprocal coefficient
also has the closed form

    g_j=(-1)^j u^(j(j-1)/2)/H_j,    0<=j<q.

The finite q-binomial product proves it. Expand
`product_(s=0)^(j-1)(1+u^s z)` by induction and set `z=-1`.
The first factor vanishes for `j>=1`, giving
`sum_(k=0)^j g_k h_(j-k)=0`. The term at `j=0` is one.
Thus `h` and `g` have the same coefficient magnitude bound.
Use this closed form for `g` when preparing numerical coefficients.
The generic reciprocal recurrence alone does not supply an error bound
for its intermediate values.

Every entry of `N` is at most `2^(2000 h^3)`. Its diagonal and its
inverse have comparable magnitude bounds. Indeed, with
`K=2^(1000 h^3)`, the imported identities give
`P^-1=D_N^-1 N^T` and `N^-1=P^-1 F_q^-1`. The inverse Fourier
matrix has infinity norm one, so `||N^-1||_infinity<=q K^3`.
These are magnitude and guard-bit bounds, not bounds on the degree
of an exact algebraic representation. The rectangular
cross update in the Toeplitz compiler uses sums of at most `q`
products of `h` and `g`, so these coefficients also require only
`O(h^3)` magnitude bits. Fixed-vector Fourier preparation adds
polynomial factors in `q`. The six-kernel shear replacement uses
`t_1=1+|mu|^2` and `t_2=mu-t_1`; both have modulus at least `3/4`.
It therefore does not introduce an exponentially small new divisor.

The root change has the exact identity

    F_q(zeta^a)_(i,j)=F_q(zeta)_(a i mod q,j).

To return the standard output at index `k`, read the new output at
`a^-1 k mod q`. This is a unit index map. When CRT is already used,
the unit multiplies its existing local output unit. It does not need
another Fourier transform or a larger root order.

## Precision and remaining bill

The imported local word has `O(log^4 q)` layers. A conservative bound
on its prefix operator norms is `2^O(log^7 q)`: each layer has only
disjoint shears, monomials, or kernels; its coefficients have
`O(log^3 q)` magnitude bits. Tensoring such words across `ell` prime
axes gives a guard of `O(ell log^7(q_max))` bits. This is an upper
bound for the literal word. It is not a claim of optimal conditioning.

For the imported working length, `ell=Theta(p/log p)` and
`log(q_max)=O(log p)`. This guard is `O(p log^6 p)`. A complete
finite-precision implementation must pay that increased coefficient
width, all scalar preparation errors, and all layer errors. The
increase is a fixed power of `log p`, so it can be absorbed in any
strict `p^delta` asymptotic slack after the actual error and tape proof
is supplied. It is not an `O(p)`-width supplier under the original
fixed-format contract without that separate adapter.

The exact root selection and coefficient identities are completed
here. The fast fixed-tape packing of the primorial sectors, the full
scalar error program, arbitrary temporary state, and returns are not
completed here. The exact complex-arithmetic paper does not supply
those bit-machine contracts. No new kappa follows from this component.

## Verification and sources

`verify_newton_hybrid.py` checks both primitive powers one and two at
`q=3,5,7,11` in an exact cyclotomic algebra. It checks 408 matrix
entries, the reciprocal Toeplitz coefficients, the output unit map,
and omitted-diagonal controls. It also executes the integer root
search and checks its continued-fraction bounds at seven larger
primes, with exact sampled discrepancy checks. The written argument
above proves the uniform coefficient bound; sampled discrepancies
are not its proof.

The original Newton factorization and exact-width compiler are in
OpenAI math at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`,
`build/sections/local.tex`. The batched transfer is eumemic's note at
`6f87d1a`, as indexed by PR225. Their source files, Git blobs, author
credits, and licenses are retained. This note supplies a primitive
root choice and its elementary conditioning proof. It claims no
literature novelty.

Prepared with OpenAI Codex assistance. Apache-2.0.
