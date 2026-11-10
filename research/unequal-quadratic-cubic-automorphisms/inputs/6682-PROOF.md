# Non-Frobenius rectangular multiplication characters

This contribution was produced by Nick Petalas. Apache-2.0.

The claim is a scoped written proof. Finite execution corroborates it.
Independent human and formal proof-kernel review are unclaimed.

## Statement

Let K = F_q have characteristic p, let d >= 2, and let n >= 2 be an integer
which is not a power of p. Set

```text
A = K[x_1,...,x_d]/(x_1^n,...,x_d^n),
N = n^d,
E = n^(d-1) n(n-1)/2,
S = n^(d-2) n(n-1)/2,
m = q-1.
```

For an integer r >= 0, write H_r = {a^r : a in K*}. Define

```text
D = H_E <(-1)^S>,
g = gcd(m,N),
h = gcd(m,E,m/2)  if q is odd and S is odd,
h = gcd(m,E)      otherwise.
```

Then D is the subgroup of K* of index h. Every K-algebra automorphism of A
has a monomial tangent matrix on the radical modulo its square. Its full
linear determinant image is exactly D.

Let mu in A* tensor A* tensor A be multiplication. Use the ordered ordinary
covariant action of GL(A*) times GL(A*) times GL(A), without permutations or
field automorphisms of the tensor factors. The exact stabilizer determinant
image is

```text
Delta(mu) = {(u,v,w) in (K*)^3 : vw in H_N, uw in H_N, uvw in D}.
```

Equivalently it is defined by the three equations

```text
(vw)^(m/g) = 1,
(uw)^(m/g) = 1,
(uvw)^(m/h) = 1.
```

Its size is m^3/(g^2 h). The GL orbit of mu contains exactly g^2 h orbits
under the product of the three special linear groups. This statement is
invariant under independent changes of basis in the three tensor factors.
It supplies character equations under an orbit promise, not recognition of
that promise, a multiplication chart or a transporter.

## 1. The tangent obstruction

The unique maximal ideal J consists of elements of zero constant term and
is nilpotent. Every automorphism preserves J and induces an invertible map
on J/J^2. Let the linear term of the image of x_i be
ell_i = sum_j a_ij x_j. The degree-n part of the relation sigma(x_i)^n = 0
requires ell_i^n = 0 in A, since all nonlinear terms contribute only degrees
greater than n. The defining ideal is homogeneous.

Write n = p^a b with p not dividing b. The assumption on n means b > 1.
Put k = p^a, so 0 < k < n. In characteristic p,

```text
(1+t)^n = (1+t^(p^a))^b,
binom(n,k) = b mod p != 0.
```

If a row of the tangent matrix has two nonzero entries a_ij and a_il,
the coefficient of x_j^k x_l^(n-k) in ell_i^n is
binom(n,k) a_ij^k a_il^(n-k), which is nonzero. This monomial survives in A
because both exponents are less than n. No other variable can contribute
to this particular monomial. Thus each tangent row has at most one nonzero
entry. Invertibility makes the tangent matrix monomial: exactly one nonzero
entry in each row and column.

Conversely every invertible diagonal scaling and every permutation of the
variables preserves the relations and defines an automorphism. This proves
the exact set of possible tangent maps. The power-of-p hypothesis matters:
when n is a power of p, x_1 -> x_1+x_2 is also allowed.

## 2. The determinant of every nonlinear lift

The finite filtration A, J, J^2, ... is invariant under every automorphism.
In a basis ordered by total degree its matrix is block triangular. Its
diagonal blocks are the maps on the associated graded algebra. That graded
algebra is canonically the same graded quotient A. The graded map is induced
by the tangent substitution, since higher terms vanish in each degree
quotient. Therefore every automorphism has the same determinant as its
monomial tangent substitution. This covers all nonlinear lifts without
classifying or counting them.

Scale one variable by a. Among the n^d basis monomials, each exponent
0,...,n-1 of that variable occurs n^(d-1) times. The determinant is a^E.
Independent scalings thus have image H_E.

Swap two variables. For each of the n^(d-2) choices of the remaining
exponents, exactly binom(n,2) pairs of distinct monomials are exchanged.
The determinant of this basis permutation is (-1)^S. Every variable
permutation is a product of these swaps. Consequently all automorphism
determinants lie in D, and the literal scaling and swap automorphisms attain
every element of D. In the cyclic group K*, adding -1 to H_E adds the
exponent m/2 when that sign is nontrivial. This proves the formula for h.

## 3. Unit determinants and covariant stabilizers

For a in A, multiplication L_a is triangular in increasing degree with
constant diagonal a_0. It is invertible exactly when a_0 != 0, and
det L_a = a_0^N. Hence unit multiplication has exact determinant image H_N,
already attained by constant units.

For completeness, the classical normalization of a unital commutative
algebra autotopism is included. Suppose invertible K-linear F,G,H satisfy

```text
F(x) G(y) = H(xy) for every x,y in A.
```

Set a = F(1), b = G(1). Substituting 1 gives H = L_b F = L_a G, so both
L_a and L_b are invertible. Thus a and b are units. The map
sigma = L_(ab)^(-1) H fixes 1, is invertible, and preserves multiplication
by substitution in the displayed identity. Hence

```text
F = L_a sigma, G = L_b sigma, H = L_(ab) sigma.
```

Conversely these maps form an autotopism for any units a,b and automorphism
sigma. No decomposition or tensor recognition algorithm is being assumed.

The corresponding covariant tensor stabilizer is (F^(-T),G^(-T),H).
Writing x = det L_a, y = det L_b, z = det sigma gives

```text
(u,v,w) = ((xz)^(-1), (yz)^(-1), xyz),
x,y in H_N, z in D.
```

This parametrization is injective, with inverse
x = vw, y = uw, z = (uvw)^(-1). It proves necessity and sufficiency of the
three conditions, the equations and the image size. Constant units and the
scaling/swap automorphisms above give actual attaining maps.

Finally the determinant map from the product GL group onto (K*)^3 is
surjective and has the product SL group as kernel. Its orbits within the
fixed GL orbit are therefore the cosets of Delta(mu), so there are g^2 h.
Conjugating the stabilizer by an independent basis change leaves each
determinant unchanged. This proves the last two assertions.

## Scope and predecessors

The nilpotent-algebra question is posed in Nick Petalas's PR5252. Ali
Romman's PR5316 covers one variable, and PR5459 covers characteristic-power
cutoffs. Armin Pourshafeie's PR5656 and PR5663 extend that latter family to
split and nonsplit products. Their results are credited comparisons, not
theorems reverified here. Recent PR6578 counts the automorphisms of the
Frobenius family; the present result supplies no such count and requires a
different truncation relation. The new step is the non-Frobenius tangent
restriction and its exact scaling/permutation determinant image. The
radical filtration, binomial identity, isotopy normalization and cyclic-group
arguments are classical; no global literature-priority claim is made.

This does not classify unequal non-Frobenius cutoffs, recognize arbitrary
tensors, price coefficient preparation or provide a physical supplier.
Native, compiler, ownership, precision/tape and analytic obligations remain.
There is no new kappa or complete multiplication theorem.
