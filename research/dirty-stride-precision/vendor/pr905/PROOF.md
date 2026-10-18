# Cubic precision for balanced cyclic inverses with arbitrary dirty arrays

This is a local arithmetic result, not a new multiplication
exponent or a common-label/Clifford implementation.

## 1. A free-algebra prefix lemma

Let A_0,...,A_(n-1) be composable linear operators. Use exactly PR628's
balanced binary commutator word with distinct source, target and one dirty
connector at each recursion depth. At this point the A_j need not commute.
At complete leaf boundaries regard each instruction as the ideal shear
`target += sign A_j source`. Source rows and target columns of every
primitive prefix matrix are the corresponding identity row and column.
The same holds for its inverse. Other coordinates outside the current
subproblem are untouched. This follows directly because no leaf writes the
subproblem's source or reads its target.

Every matrix entry of every prefix and inverse prefix is a noncommutative
polynomial in the A_j whose monomials have strictly decreasing indices.
In particular no factor occurrence is repeated. The sum of absolute integer
coefficients in any block row is at most

    C_n = 2 * 3^h,    h = ceil(log2 n).

Proof by induction on the balanced tree: the leaf assertion is immediate,
with coefficient row sum at most two. At an internal node let B be the full
left product and A the full right product. All indices of A exceed every
index of B. Write U for `z += B x`, V for `y += A z`. A prefix has the form
`R C`, where C consists of zero to three completed children and R is a
prefix inside the next child. Complete children restore all deeper scratch.
Their exact outer-coordinate states, with unchanged x, are:

| Word | completed children k | z after C | y after C | active child |
|---|---:|---|---|---|
| positive U,V,U^-1,V^-1 | 0 | z | y | left |
| positive | 1 | z+Bx | y | right |
| positive | 2 | z+Bx | y+Az+ABx | left |
| positive | 3 | z | y+Az+ABx | right |
| negative V,U,V^-1,U^-1 | 0 | z | y | right |
| negative | 1 | z | y+Az | left |
| negative | 2 | z+Bx | y+Az | right |
| negative | 3 | z+Bx | y-ABx | left |

Each C and C^-1 has coefficient block-row sum at most three. The last
boundary is the completed product shear and has row sum at most two.

For an active left child, R's target column z is the identity column and
its source row x is the identity row. In R C, any Bx term already in z is
therefore added without another left factor; the y row is untouched by R.
In C^-1 R^-1, a nontrivial product can only prepend A to an expression from
the left child. For an active right child, R's target column y and source
row z are identities. In R C a nontrivial product can only append B to an
expression from the right child; in C^-1 R^-1 all A terms multiply the
identity source row. Inspection of the eight displayed cases includes the
AB terms, signs, and both inverse formulas. Thus all new products are
ordered concatenations of disjoint index sets. Addition and cancellation
cannot create another monomial. Coefficient row sums are submultiplicative,
so both R C and C^-1 R^-1 have row sum at most three times the child bound.
The balanced depth is h, proving the assertion for all n.

Consequently, if EVERY ordered subset product of the A_j has operator
norm at most G>=1 (including the empty product), then every ideal prefix
P and its inverse have norm at most B=C_n G in the maximum joint-array
norm. Every interval propagator P_j P_i^-1 has norm at most B^2. This last
step need not have squarefree monomials; the two prefix bounds suffice.

## 2. Common cyclic factors give a small subset bound

Now let U be a unit-weighted permutation, hence an isometry in every integer
power, and let `product_j(z-rho_j) = r Q(z)` for n=r-1. All inverse factors
use this same U, direction, and immutable phases. PR628 puts scale r on
exactly one factor; all other factors have scale one.

Suppose `||Q||_1<=M`, `||Q(U)^-1||<=H`. For any subset J, commutativity gives

    product_(j in J)(U-rho_j I)^-1
      = product_(j notin J)(U-rho_j I) Q(U)^-1 / r.

The elementary Mahler-measure inequality
`product_j max(1,|rho_j|) <= ||r Q||_1 <= r M` implies that the complementary
polynomial has coefficient norm at most `2^n r M`. Thus every unscaled
subset inverse has norm at most `2^n M H`; a subset of the actual scaled
factors has norm at most

    G = max(1, r 2^n M H).

This is PR862's complementary-factor argument, now applied to the free
prefix lemma, rather than to an in-place scan. There is no low-zero-bit
requirement. The factor r is paid even for subsets containing the scaled
leaf. The assertion is false in general for different noncommuting shifts;
the free-algebra lemma alone does not supply a small G.

## 3. Rounded execution and exact dirty restoration

At complete leaf boundaries the unchanged PR628 leaf has local error at
most `a u (||source||+1)`, where `a=13(r+1) beta^-3`, `u=2^-w`, and the
closure condition is `u<=beta^2/2`. All initial arrays, including borrowed
ones and target, have norm at most D. Leaves are deterministic target-
independent signed increments and restore their sources exactly. Immutable
phase and factor data must be disjoint from every mutable array.

Let N be the actual paid leaf count, including all inverses and restoration:
`N=3 q n-2 q^2`, q=2^floor(log2 n), hence N<=2n^2. Let M_actual be the
largest computed joint norm at leaf boundaries. Variation of constants
inserts the actual, possibly nonlinear, errors into the ideal shear word.
With B=C_n G and t=N B^2 a u it gives

    M_actual <= B D + t(M_actual+1).

If t<=1/2 then M_actual<=2 B D+1 and the complete execution error is at most

    2 N B^2 a u (B D+1).

This is the perturbation argument in PR877, with a different, smaller
prefix bound. It does not assume rounded children are linear or independent
of dirt. Their exact inverse identities still restore source and borrowed
arrays, and the negative whole word exactly cancels the positive whole
word on the same grid. Intermediate state inside a leaf retains PR628's
separate causal/closure bounds.

## 4. Explicit cubic budgets

For prime power r>=3, put n=r-1, ell=ceil(log2 r), h=ceil(log2 n),
phi=EulerPhi(r), and suppose D<=2^m, m>=0. Reuse the PR621/PR862 bounds

    d0 = 1+2ell+r n phi,
    a0 = 2d0+r+2,
    g = d0+ell+2r+2,
    beta = 2^-g.

The original kernel has inverse norm <=2^a0. Prepare the same dyadic-root
polynomial Q using coefficient error epsilon=2^-e, where

    e = max(d0+1, a0+1, p+2a0+m+4),
    b = max(n ell, e+r+3).

The common-isometry Neumann argument gives ||Q(U)^-1||<=2^(a0+1),
||Q||_1<=2^r and original-versus-prepared inverse error on the source at
most 2^(-p-3), in particular <=2^(-p-1). The inherited radial derivative
bound gives the leaf margin beta. As in PR862, these are supplied
approximate-factorization/coefficient-verification algorithms, not a claim
that the rational fixture executable implements their asymptotic runtime.

Then the scaled subset bound is <=2^(a0+2r+ell). Put

    J = a0+2r+ell+1+2h,
    Aerr = 3g+ceil(log2(13(r+1))),
    w = max(w_input, Aerr, 2g+1,
            p+3+ceil(log2 N)+Aerr+m+3J).

Here 2^J>=B because 3^h<=2^(2h). The execution error is at most 2^(-p-1),
and closure and feedback smallness both hold. Combined preparation and
execution error is <=2^-p. No incoming grid is silently coarsened.

Since phi<=r, ell,h<=r, and ceil(log2 N)<=1+2h, the precision overhead is
at most `9r^3-9r^2+48r+33 <=16r^3` for r>=3: the difference is
`(r-3)(7r^2+30r+42)+93`, which is positive. Thus

    w <= max(w_input,p) + m + 16r^3.

Also b=O(p+m+r^3). Integer magnitude bits are O(m+r^3): the leaf-boundary
bound is 2BD+1 and the inherited internal leaf adds O(g+ell) bits. The
complete word size is therefore `max(w_input,p)+O(m+r^3)`.

The neighboring-layout execution and preparation bill is

    soft-O((L r^2+r^3)(max(w_input,p)+m+r^3)).

All N leaf calls, their three passes and validation/source access, inverse
work, scalar arithmetic, descriptors and routing remain paid. Borrowed
storage is ceil(log2 n) arbitrary dirty length-L arrays; no clean length-L
array and no reserved zero bits have been added. Phase-oracle or long exact
phase-description access is an additional charge. Arbitrary-stride routing
and the inherited arithmetic/preparation hypotheses remain as in PR628.

## Scope and credit

This proves a sufficient local precision bound for the existing balanced
classical arithmetic dispatcher. It does not prove minimum precision,
practical speed, bit-reversible arithmetic, a common-label or Clifford word,
physical owner layout, a full transform recurrence, a multiplication
reduction, or any change to kappa. A finite symbolic trace supports but does
not replace the all-size induction above. The general statement depends on
the inherited leaf and preparation lemmas.

Credit Chafik Boukhalfa / chafreaky for PR628 and PR862, Gareth Davidson /
bitplane for PR877's restored-child prefix and nonlinear perturbation audit,
0xkilgore for PR663's exact leaf count and restoration audit, and the
original PR621 kernel lineage. This draft was prepared by Chafik Boukhalfa
with substantial OpenAI Codex assistance. No independent human review,
formal verification of the full theorem, or literature priority is claimed.
