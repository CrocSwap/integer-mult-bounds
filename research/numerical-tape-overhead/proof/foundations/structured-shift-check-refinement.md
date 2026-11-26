# Shift-only checks and a small scalar field

Status: **optional finite refinement, independently accepted by Route A
and the session lead**. See [review-structured-shift-check.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/routes/A/review-structured-shift-check.md) and
its linked exact checker for the independent gate and finite test scope.
This is not used by the accepted whole-input theorem and does not assert
a better overhead rate. It identifies structure relevant to a future
physical executor for the exponentially wide tensor module.

## 1. Tensor the check map with the independent module index

Suppose a predictor is the direct sum of B equally sized shift blocks,
each having w independent rows, and its completed value at a frequency is

    P = diag(p_1,...,p_B) tensor I_w.

Assume at most s shifts lie in a known containing exceptional set J.
Choose an s-by-B check matrix H0 whose columns in every such J admit a
left inverse. A Vandermonde matrix on B distinct field elements suffices.
Then use

    H = H0 tensor I_w.                                  (SC1)

The exceptional row set is J times the entire module index. Its relevant
check matrix is `(H0)_J tensor I_w`; both the left inverse and the
transpose right inverse tensor with I_w. Thus the Hermite or F4 two-P
repair proof applies unchanged. It needs B check nodes, not B*w nodes.
The spectral table is also the same shift-space table tensored with I_w.

This uses structure of the actual exceptional sets; it does not claim
that H corrects every arbitrary set of s*w row coordinates. Every module
row remains an independent input. Dense shift-check work costs O(B)
arithmetic operations per independent input row in the row model.

## 2. Pairwise-independent ternary shifts

Let r be the least integer with `(3^r-1)/2>=m` and put B=3^r. Select m
nonproportional nonzero vectors a_j in F3^r, including a basis. This can
be done by enumerating vectors whose first nonzero coordinate is one.
For t in F3^r use

    beta_j(t)=a_j dot t modulo three.

Then `2m+1<=B<6m+3`. The seed-to-shift map is injective because the
selected vectors include a basis. For every fixed query exponent tuple k,
the shifted digits b_j=(k_j+beta_j(t)) modulo three are individually
uniform and pairwise independent. Therefore their ordinary count c has

    E[c]=m,     Var(c)=2m/3.                            (SC2)

Let b=5ceil(sqrt m). Chebyshev gives a fraction at most
`2m/(3b^2)<=2/75<1/32` outside `[m-b,m+b]`, uniformly for every k.
The family and every seed/indicator coefficient are explicitly generated
in polynomial m time. No random seed is chosen by the algorithm.

To use the all-power-two degree architecture of
[power-two-degree-predictor.md](power-two-degree-predictor.md), take T to be the least power of two
at least 2b+1, set D=T-1 and u=m-floor(D/2). The count window `[u,u+D]`
contains `[m-b,m+b]`, and D=O(sqrt m). For m>=4096 it has D<=m;
the bounded smaller range may use the existing constructor.

Use exactly the carry-bit formula and the factored Lucas expression

    omega^(u-sum beta_j)
      product_(i<log2 T) (1+(omega-1)^(2^i) B_i).

Every addition has a power-of-two degree budget, so the cyclic predictor
is defined over F4 without auxiliary roots. Its common width w is a
power of two and can still be exponential in polynomial m.

## 3. Exact repair fractions and a logarithmic-degree field

For B>=219, `floor(B/32)>=(2/75)B`. Put s0=floor(B/32), duplicate the
module by 32, and let v=32w and R=Bv. The tensor check
`H0 tensor I_v` has s0*v rows and corrects every actual exceptional shift
set. Its row count is at most S=R/32, an integer. Append S-s0*v zero
check rows to obtain exactly S checks. The added coordinates are internal
workspace, are charged, and are transformed as part of the full phase;
they are not counted as additional independent parent inputs.

Each phase therefore has exactly 2S=R/16 rows, preserving the four-child
mass 1/4 of the accepted O3 contraction. The same structured left/right
inverses recover every possible exceptional error. Zero padding here is
an explicit enlargement inside the paid check budget, not a replication
of an odd-width input module to an incompatible width.

Choose e=ceil(log_4 B) and explicitly construct a degree-e irreducible
polynomial over F4. Bounded enumeration and polynomial division, as in A's
finite-field refinement, take polynomial B work. The resulting field has
at least B elements, so it supplies all distinct check nodes and unit
differences. Its degree over F4 is O(log m), rather than depending on the
exponential module width. All shift-space inverse and table operations
at one spectral tuple have polynomial m dimensions and ordinary
field-coordinate cost. Enumerating the complete 3^m tuple table remains
an exponential setup option; no polynomial bound on that entire expanded
list is asserted.

## 4. What this does and does not pay for

The predictor still occupies w independent module rows per shift. The
current accepted general compiler expands those matrices and therefore
retains its singly exponential finite-data envelope. The refinement alone
does not alter the complete overhead theorem or its numerical constants.
Its larger count window also changes the absolute stage coefficient; the
old Q3 number cannot be reused silently for this optional variant.

The concrete future interface is a physical execution of these tensor
pencils and shift-only checks using their succinct description, charging
module-index permutations, aligned row scans, all address changes, setup,
and parked arrays. Matrix sparsity or the small coefficient field does
not prove such an implementation. This is the remaining step before any
growing-arity consequence could be assessed.

Credits: standard pairwise-independent linear shifts; source check repair;
A's characteristic-two carry and power-of-two refinement; B's tensor-check
observation; Jerry Chen (@CubeJerry); AI-assisted finite analysis.
