# Sharp unit-input error for a shared translated Fourier routine

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract and new result

Let G be a finite product of cyclic groups, N=|G|, with its standard
symmetric nondegenerate unit character pairing chi. Both Fourier signs have
the normalization

    (F±u)(x) = (1/N) sum_y chi(x,y)^±1 u(y).

Fix a nonzero element b of order two. Put c(x)=chi(b,x), so c takes the
values +1 and -1 equally often. Let w be any unit-modulus complex function.
As in Nick Petalas's PR #6307, define

    P_b f(x) = f(x+b),
    B_w(u,v) = D_conj(w) P_b F+ [(D_w P_b F-u)(D_w P_b F-v)],
    B(u,v)   = (u*v)/N².

Convolution has no normalization. For a complex bilinear map T write

    ||T||_bil = sup { ||T(u,v)||_2 : ||u||_2=||v||_2=1 }.

The desired map has ||B||_bil=N^(-3/2). The relative unit-input error is

    D(w) = ||B_w-B||_bil / ||B||_bil.

The new result, answering Open next question 2 of #6307, is

    min_(|w|=1) D(w) = sqrt(2 - 8/(3 sqrt(3))).               (1)

The inherited phase choice

    w(x)=1/sqrt(3) - i sqrt(2/3)c(x)                         (2)

attains (1). Every pair of equal normalized characters attains the
unit-input supremum for (2). More generally the following exact formula
computes the unit-input norm for every phase function, without optimizing
over pairs of input vectors:

    m = (1/N) sum_x c(x)w(x),
    D(w)² = max_y {2 - 2 Re[conj(m)c(y)w(y)²]}.              (3)

This statement is about absolute operator error divided by the norm of B.
It does not divide by ||B(u,v)|| at each input pair, which can be zero.

## A bilinear column-norm lemma

Let U,V be any unitary maps on C^N and M any complex matrix with N columns.
For T(u,v)=M[(Uu) pointwise (Vv)],

    ||T||_bil = max_j ||M e_j||_2.                          (4)

Indeed, for unit u,v, Cauchy-Schwarz gives

    sum_j |(Uu)_j(Vv)_j| <= ||Uu||_2 ||Vv||_2 = 1.

The triangle inequality then bounds ||T(u,v)|| by the right side of (4).
If j maximizes it, choose u=U*e_j and v=V*e_j. Both are unit vectors,
their transformed pointwise product is e_j, and equality holds. This
argument works over complex inputs and for rectangular M as well.

The inequalities and the extremizing construction are classical elementary
norm facts. The contribution is their exact application at this normalized,
shared three-pass Fourier boundary and the resulting sharp minimax theorem.

## Apply the lemma with every normalization retained

Write f=F-u and g=F-v. Then sqrt(N)F- is unitary, and the difference is

    (B_w-B)(u,v)=M(f pointwise g),
    M_(x,z) = [conj(w(x))w(z-b)² chi(x+b,z-b)-chi(x,z)]/N.

The maps multiplying u and v each supply another factor 1/sqrt(N).
Equation (4) therefore gives

    ||B_w-B||_bil = (1/N) max_z ||M e_z||_2.                (5)

For the desired map alone M=F+, whose columns all have norm 1/sqrt(N).
This proves ||B||_bil=N^(-3/2), including attainment.

Put y=z-b. The ratio of the implemented and desired coefficients in
column z is

    rho(x,y)=conj(w(x))w(y)² c(x)c(y).

Here chi(x+b,y)/chi(x,y+b)=c(y)/c(x)=c(y)c(x), using that b has order two.
Every desired coefficient has modulus 1/N. Squaring (5) and dividing by
||B||_bil² gives

    D(w)² = max_y (1/N) sum_x |rho(x,y)-1|².

All rho have modulus one. Their average over x is
conj(m)c(y)w(y)². Expanding |rho-1|² proves (3).

For any maximizing y, z=y+b and the explicit unit inputs are

    u(x)=v(x)=chi(x,z)/sqrt(N).

Fourier orthogonality gives F-u=F-v=e_z/sqrt(N). They attain the column
in (5), so the upper bound is an attained supremum, not a relaxation.

## Sharp minimization using the credited predecessor inequality

PR #6307 proves, for every unit phase w in this same contract, that

    E(w)² = 2 - 2 Re[conj(m)n] >= 2 - 8/(3 sqrt(3)),
    n=(1/N)sum_y c(y)w(y)².

Its E is the relative coefficient Frobenius error N||B_w-B||_F.
The predecessor scalar moment inequality and its lower bound are cited
premises here. They are not re-proved or scientifically replayed.
Equation (3) immediately gives

    D(w)² >= (1/N)sum_y {2-2 Re[conj(m)c(y)w(y)²]} = E(w)².

This proves the lower bound in (1) from the cited theorem.

For the inherited choice (2), put h=1/sqrt(3), r=sqrt(2/3). Then

    m=-ir,
    c(y)w(y)²=(h²-r²)c(y)-2ihr,
    Re[conj(m)c(y)w(y)²]=2hr²=4/(3 sqrt(3)).

Thus every column in (3) has squared error 2-8/(3 sqrt(3)). This supplies
the new arbitrary-unit-input upper bound and proves (1). Every equal
character pair attains it, independently of chi(b,b) and N.
The optimal unnormalized absolute error is N^(-3/2) times (1).

## Scope and credit

Nick Petalas #6307 supplies the question, coefficient lower bound, scalar
inequality and phase choice. Hanson Sun / bbMisk #1477 supplies the exact
weighted-layout contract, extending Ross Richardson #940. Character
orthogonality, unitary Fourier normalization, Cauchy-Schwarz and elementary
induced-norm arguments retain their classical credit. Only the unit-input
norm formula, its extremizers and the sharp extension to the stronger input
contract are claimed here.

All finite products of cyclic groups and arbitrary unit complex phase functions are covered by
the written theorem under the stated order-two and shared-routine hypotheses.
The finite verifier uses only products of cyclic factors 2 and 4 of size at
most 16. Its exact arithmetic corroborates the new reduction and attaining
upper bound; it does not prove the universal theorem or audit the predecessor.
Other translation orders, physical phase preparation, rounding, routing,
restoration, compiler closure and the complete supplier bill are unsettled.
No new kappa, supplier admission or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
