# Independent root choice and conditioning audit

## Finding and scope

The proposed root selection proves a uniform bound on all nonzero
prefix products. The constants `B=16h`, `480h^2`, and `1000h^3` are
valid. The continued fraction proof must use a non-strict approximation
bound for a rational number. It must also handle the possible duplicate
initial denominator one. Neither issue defeats the result.

The bound removes the specific large-growth example at the canonical
root. It gives `O(log^3 q)` magnitude and precision guard bits for the
Newton coefficients and their reciprocals. It does not give a short
exact algebraic representation or a fixed-tape compiler. No new cyclic
target cost or multiplication exponent follows from this audit.

## 1. A root exists and can be found

Let `q` be an odd prime, `h=ceil(log2 q)`, and `B=16h`. Call `a` good
when

    B*j*min(aj mod q, q-(aj mod q)) >= q,   1<=j<q.

For a fixed `j`, multiplication by `j` permutes the nonzero residues
because `q` is prime. A bad residue has positive integer distance
`m<q/(Bj)` from zero. There are fewer than `2q/(Bj)` such residues.
This strict inequality also holds when `q/(Bj)` is an integer.
Thus the union of bad choices has size less than

    (2q/B)*H_(q-1),    H_n=sum_(j=1)^n 1/j.

Here `H_(q-1)<=1+ln(q-1)<=2h`. Consequently

    (2q/B)*H_(q-1) <= q/4 < q-1.

At least one good `a` exists in `1,...,q-1`. Testing the candidates
in that order is a deterministic search with `O(q^2)` modular tests
on `O(log q)`-bit integers. It has polynomial bit cost in `q`.
The argument uses primality: for a composite `q`, a nonunit `j` would
not permute all nonzero residues. No composite extension is asserted.

## 2. Continued fraction blocks

Put `alpha=a/q`. Write its regular continued fraction with convergents
`P_k/Q_k`, starting at `P_0/Q_0=0/1` and ending at `a/q`.
Let the final index be `m`. Every nonfinal `Q_k` is less than `q`.
The convergent estimate gives

    |Q_k alpha-P_k| <= 1/Q_(k+1),   k<m.

Equality occurs at the penultimate rational convergent; replacing
`<=` by `<` there is an error. The good-root condition gives

    1/(B Q_k) <= ||Q_k alpha||
                 <= |Q_k alpha-P_k| <= 1/Q_(k+1).

Hence `Q_(k+1)<=B Q_k`. Each partial quotient is also at most `B`.
There can be two initial denominators equal to one when the first
partial quotient is one. All later denominators increase strictly.
The recurrence implies `Q_(k+2)>=2Q_k`, so the number of convergents
is at most `2h+1`.

For a prefix length `0<=j<q`, greedily subtract the largest available
nonfinal denominator. Ignore a repeated denominator one, or retain
its later convergent. Before using `Q_k`, the remainder is less than
the next distinct denominator. The coefficient at this denominator
is therefore at most `B`. The prefix is a concatenation of at most

    B*(2h+1)

rotation blocks, each of length one nonfinal denominator. This is a
decomposition of a sequence into consecutive blocks; it is not a
sorting or random-access claim.

For one block of length `Q=Q_k` starting at an arbitrary rotation,
compare its points with the grid from `P_k/Q_k` at the same start.
Since `gcd(P_k,Q_k)=1`, that grid is uniform. For `1<=s<=Q`,

    distance_circle(s alpha, s P_k/Q_k)
        <= Q*|alpha-P_k/Q_k| <= 1/Q_(k+1) <= 1/Q.

For any half-open circular interval, the uniform grid count differs
from `Q` times its length by at most two. A displaced grid point can
change membership only within distance `1/Q` of an endpoint. Each
of the two endpoint neighborhoods contains at most four grid points,
including endpoint conventions and the small `Q` cases. The block
count discrepancy is therefore at most ten.

Discrepancies add across the consecutive blocks, giving

    D_j <= 10B(2h+1) <= 480h^2.

This holds uniformly for every prefix `j<q` and every circular
interval. A change in the start of a block only rotates its intervals.
The final denominator `q` is not used, because the prefix is shorter
than `q`.

## 3. The capped logarithm bound

Let `f(x)=ln(2 sin(pi x))` on `(0,1)` and let `delta(x)` be distance
to the nearest integer. Define the continuous periodic cap

    f_q(x)=ln(2 sin(pi*max(delta(x),1/q))).

Every point `as/q`, `1<=s<q`, has distance at least `1/q`, so
`f_q(as/q)=f(as/q)`. The total variation of the cap is

    Var(f_q)=2 ln(1/sin(pi/q)) <= 2 ln q.

The bound follows from `sin(pi/q)>=2/q`. Also `integral_0^1 f=0`.
For a direct proof, symmetry gives equal integrals of `ln sin x`
and `ln cos x` on `(0,pi/2)`. Adding them and using the double-angle
identity gives `integral_0^(pi/2) ln sin x=-(pi/2)ln2`.
The endpoint integrals exist because `sin x` is bounded below by a
positive multiple of `x` near zero.

The cap raises `f` only near zero and one. Concavity of sine gives
`sin(pi x)>=q x sin(pi/q)` for `0<x<=1/q`. Thus

    0 <= integral_0^1(f_q-f)
       <= 2*integral_0^(1/q) ln(1/(qx)) dx = 2/q.

This is stronger than the proposed `4/q`. In particular
`0<=integral f_q<=4/q`. Integration by parts against the empirical
counting measure, using the prefix discrepancy above, gives

    |sum_(s=1)^j f_q(as/q)-j*integral f_q|
        <= D_j*Var(f_q) <= 960h^2 ln q.

For `H_j=product_(s=1)^j (1-zeta_q^(as))`, `0<=j<q`, it follows
that

    |ln |H_j|| <= 4+960h^2 ln q,
    |log2 |H_j|| <= 6+960h^3 <= 1000h^3.

The case `j=0` is `H_0=1`. The index restriction is required:
`H_q=0`, so no inverse bound holds at that endpoint.

## 4. Newton and reciprocal coefficient bounds

Set `u=zeta_q^a` and `C_q=2^(1000h^3)`. The preceding result gives

    C_q^(-1) <= |H_j| <= C_q,   0<=j<q.

The inspected local Newton identity is

    F_q(u)=N D_N^(-1) N^T,
    N_(i,k)=(-1)^k u^(k(k-1)/2) H_i/H_(i-k),   k<=i,
    N=diag(H_i) T diag((-1)^k u^(k(k-1)/2)),
    T_(i,k)=h_(i-k),   h_j=1/H_j.

All required products stop at `q-1`. The diagonal `D_N` has entries
`(-1)^k u^(k(k-1)/2) H_k`, and is invertible. Its diagonal and its
inverse have magnitudes at most `C_q`. The entries of `N` have
magnitudes at most `C_q^2`.

The reciprocal-series coefficients through degree `q-1` are exactly

    g_j=(-1)^j u^(j(j-1)/2)/H_j.

To check them, multiply the coefficient at degree `n` in `h*g` by
`H_n`. For `1<=n<q`, the finite q-binomial identity gives

    sum_(k=0)^n (-1)^k u^(k(k-1)/2) H_n/(H_k H_(n-k))
        =product_(s=0)^(n-1)(1-u^s)=0.

At `n=0` the coefficient is one. Every denominator is nonzero in
the stated range. Thus `T^(-1)` has coefficients `g_j`, also bounded
by `C_q`. This closed form should be used for numerical preparation;
the generic reciprocal recurrence does not automatically inherit a
small numerical error budget when evaluated without a new analysis.

The standard DFT is recovered by an output permutation:

    (F_q(u)x)_i=(F_q(zeta_q)x)_(ai mod q).

To produce standard output index `k`, read the local output at
`a^(-1)k mod q`. This is a unit permutation in the complex norm.
Its fixed-tape movement remains a separate paid operation.

## 5. What the local compiler bound supports

The local Toeplitz compiler forms cross entries from sums of at most
`q` products `h_j g_k`. Their magnitudes are at most `q C_q^2`.
Its rank-three displacement vectors are made from these entries,
products `h_j g_k`, and unit vectors. Their magnitudes are bounded
by a fixed polynomial in `q` times `C_q^2`. The fixed-vector Fourier
transforms add a factor at most `q`. Thus the resulting scalar DAG
coefficients have logarithmic magnitudes `O(h^3)`.

The conversion of a shear coefficient `mu` to nonzero shears uses
`t_1=1+|mu|^2` and `t_2=mu-t_1`. Here

    |t_1|>=1,
    |t_2|>=1+|mu|^2-|mu|>=3/4.

Their inverses are bounded, and their upper magnitudes still have
logarithm `O(h^3)`. Thus this conversion introduces no small new
denominator. The Newton diagonals and their inverses already satisfy
the same logarithmic bound. These checks cover the displayed local
compiler coefficients; they are not a numerical implementation of it.

For `ell=O(p/log p)` axes with `q_max<=p^c`, a synchronized word has
`O(log^4 p)` slots. A tensor monomial slot has coefficient magnitude
logarithm `O(ell log^3 p)`. The tensor `C` slots add `O(ell)` norm
growth per slot. Multiplying the conservative bounds over all slots
gives an intermediate data magnitude guard

    Gamma=O(ell log^7 p)=O(p log^6 p).

This is a polylogarithmic increase relative to width `p`. It can be
absorbed in a slack polynomial factor `p^delta`, for any fixed
positive `delta`, when the remaining bit and tape bounds are proved.
The estimate is conditional on the stated axis count and polynomial
prime sizes. It is not a proof of the full target running time.

Magnitude bounds do not imply that the exact algebraic coefficients
have `O(h^3)` representation bits. Numerical root preparation,
coefficient evaluation and error tolerances must be specified. The
closed reciprocal formula gives a direct route that avoids the generic
unstudied recurrence. Fixed-tape sector movement, selectors, output
permutations, stock, and returns remain missing from this component.

## 6. Finite independent checks

`independent/verify_root_choice_independent.py` constructs the bad union
by pulling small residues back through the inverse of each `j`.
It then checks the selected root directly. This method is independent
of scanning candidate roots until one passes. It checks exact rational
convergent errors, denominator ratios, every greedy prefix, and exact
circular interval discrepancy for each convergent block. Mirrored
roots exercise the duplicate initial denominator case.

The run passed 24 root cases on 12 odd primes from 3 through 2053,
8,256 prefix decompositions, and 56 block checks. It used less than
21 MiB RSS and 0.014 seconds. Its receipt is
`independent/root-choice-independent-receipt.json`.
The finite run checks conventions and edge cases. The arguments above
establish the uniform bounds; no numerical DFT target was tested.

The Newton and compiler formulas were inspected in the retained
`sources/openai-local.tex`; tensor synchronization was inspected in
`sources/openai-synchronization.tex`. Original source notices remain
unchanged. The proof above uses elementary continued fraction,
discrepancy, and integral arguments and claims no literature novelty.

Prepared with OpenAI Codex assistance. Apache-2.0.
