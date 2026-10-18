# An inverse for the complete twenty-site phase map

## The fixed word and the parameters

Fix the retained T740 owner replica `0`, port `0`, its eight data streams,
the hosted axes and their actual placements, the translations, and the complete
ordered data-event word. The authenticated projection is the same one used in
[PR3272](https://github.com/CrocSwap/integer-mult-bounds/pull/3272), with the
canonical `idle-star-paired-axis-census` sources pinned in `SOURCES.json`.
Here **every** idle child `j=0,...,19` receives an independent multiplier `z_j`
at its residual phase event, including the twelve children whose current
residual basis is empty. Each such event occurs once in the fixed word.

For a Fourier character `x` in `F_2^73`, a basis `A` contributes

`f_A(x) = i^(sum_{a in A} parity(a & x))`.

Replacing the residual basis at child `j` by `A'_j` gives the multiplier
`z_j(x)=f_{A'_j}(x)/f_{A_j}(x)`, provided the hosted prefix and translation are
fixed. These physical multipliers are fourth roots of unity. The algebraic
theorem is stronger: for each character it permits **arbitrary nonzero complex
values** of all twenty `z_j`. The multipliers may depend on the character.

Multiply the resulting eight-stream matrix by `i^(-popcount(x))` to remove
the common baseline phase, and call the normalized matrix `M(z;x)`. Put

`g(x) = i^(-parity(11 & x))`.

The integer `11` represents the three coordinate bits `0,1,3` in the source
recipe. In particular `g(x)` is always nonzero. The retained normalized matrix
has 72 signed monomial terms, and each entry has one common ambient factor,
either `1` or `g`. Both implementations derive these terms from the complete
fixed word; `RESULT.json` retains all entries, not only those used below.

**Theorem.** For every `x`, the map `z -> M(z;x)` is injective on
`(C\{0})^20`. It has the rational inverse below on its image. Consequently
`M(z;x)=I` if and only if every `z_j=1`.

## Exact character algebra and source replay

For a binary vector `a`, its parity has the following exact lift modulo four:

`parity(a & x) = sum_i a_i*x_i - 2*sum_{i<j} a_i*a_j*x_i*x_j (mod 4)`.

This follows by expanding `(1-product_i(1-2*a_i*x_i))/2`; all terms of degree
at least three are divisible by four. Therefore the lift is exact on every
Boolean character. Linear coefficients are in `Z/4`, and quadratic
coefficients are even. The primary checker stores them in three bitsets;
the independent checker uses a separate representation. They retain exact
integer coefficients of each formal `z` monomial and each lifted phase.

The replay begins with the identity matrix, applies the hosted phases at
their source schedule positions, and executes every owner-zero local shear,
idle phase, bridge, terminal translation and terminal row operation in order.
A site's `z_j` is inserted at its idle phase, after including its unchanged
residual axes and translation. Finally the common baseline factor is removed.
There is no inference from sampled characters: combining terms with identical
lifted phase polynomials is an exact identity on all `2^73` characters.

The primary authenticates the declared source closure before executing the
canonical projection helpers, including the full fill projection check. Its
phase algebra, matrix replay and inverse check are local to this package.
The independent checker reconstructs the required projection directly from
the authenticated JSON inputs, without importing that executable or the
primary checker. The resulting 72-term matrices agree exactly.

## Twenty entries and the inverse

The following source-derived entries suffice. Indices are zero-based; an
entry shown divided by `g` has the common nonzero ambient factor removed.

| Entry | Polynomial |
| --- | --- |
| `M00` | `z13` |
| `M11` | `z12` |
| `M02` | `z0*z13 - z0*z1*z15` |
| `M22` | `z0*z1*z15` |
| `M12/g` | `z0*z12*(z1-1)` |
| `M30/g` | `z14*(1-z3)` |
| `M31` | `z12-z3*z14` |
| `M33` | `z2*z3*z14` |
| `M04` | `-z4*z15+z4*z5*z17` |
| `M44` | `z4*z5*z17` |
| `M34/g` | `z4*z14*(z5-1)` |
| `M51` | `z3*(z7*z16-z14)` |
| `M52/g` | `z0*(z14*(1-z1)+z16*(z1-z7))` |
| `M55` | `z6*z7*z16` |
| `M06` | `z8*z17-z8*z9*z19` |
| `M66` | `z8*z9*z19` |
| `M56/g` | `z8*z16*(z9-1)` |
| `M71` | `z3*z7*(z16-z11*z18)` |
| `M74/g` | `z4*(z16*(1-z5)+z18*(z5-z11))` |
| `M77` | `z10*z11*z18` |

Recover the variables in this order, using already recovered quantities on
each right-hand side:

```text
z13 = M00
z12 = M11
z0  = (M02 + M22)/z13
z1  = 1 + M12/(g*z0*z12)
z15 = M22/(z0*z1)

u   = z12 - M31                       [= z3*z14]
z14 = M30/g + u
z3  = u/z14
z2  = M33/u

z4  = (M44 - M04)/z15
z5  = 1 + M34/(g*z4*z14)
z17 = M44/(z4*z5)

p   = M51/z3 + z14                    [= z7*z16]
z16 = (M52/(g*z0) - z14*(1-z1) + p)/z1
z7  = p/z16
z6  = M55/p

z8  = (M06 + M66)/z17
z9  = 1 + M56/(g*z8*z16)
z19 = M66/(z8*z9)

p   = z16 - M71/(z3*z7)               [= z11*z18]
z18 = (M74/(g*z4) - z16*(1-z5) + p)/z5
z11 = p/z18
z10 = M77/p
```

Substitute the twenty displayed entries: each recovered expression equals
its named variable. Every denominator reduces to a nonzero monomial in the
original variables and `g`. In particular the temporary denominators `u`
and `p` are the monomials indicated in brackets. Thus none can vanish on the
stated domain. The primary verifies these identities in the Laurent polynomial
ring `Q[z0^+-1,...,z19^+-1,g^+-1]`, allowing division only after the denominator
has reduced to a single nonzero monomial. The independent checker separately
checks the inverse identities.

This proves injectivity: identical matrices at the same character yield
identical recovered coordinates. Substituting all `z_j=1` in the *complete*
source-derived matrix gives `I`, as checked coefficient by coefficient.
Injectivity therefore also proves the identity-fiber assertion. The inverse
is claimed on the image; an arbitrary eight-by-eight matrix need not belong
to that image or make these divisions valid. A fixed-word identity is also
impossible with any `z_j=0`: the eight diagonal monomials collectively contain
all twenty variables, whereas the identity has eight unit diagonal entries.

## Rank consequence and its hypotheses

Suppose each replacement residual list is a linearly independent binary
basis. For a uniformly random character `x`, the parities of a rank-`r`
independent list are independent uniform bits. Hence

`E_x f_A(x) = ((1+i)/2)^r`, and `|E_x f_A(x)|^2 = 2^(-r)`.

All-character operator equality, with the fixed word and fixed hosted and
translation phases, first gives `z_j(x)=1` at every character for each site
separately. Its old and new residual phase functions are equal; their averages
have equal squared magnitude, so their residual ranks are equal. The source
nonzero residual ranks are

`r4=r6=r14=r15=1`, and `r8=r10=r12=r13=48`.

Every other residual rank is zero. In particular an empty site cannot receive
a nonempty independent residual basis while another site's phase compensates
for it in this fixed word. For legal combined hosted-plus-residual independent
bases, the hosted ranks are fixed as well, so the full child ranks are unchanged.

Independence is essential to this rank statement: repeating one axis four
times has trivial phase without being an independent rank-four basis. Equal
phase functions also need not mean equal bases. For example, the six standard
axes and the six complement-of-one vectors in `F_2^6` are distinct orthonormal
bases with equal lifted phase sum. The conclusion is separate phase-function
and rank preservation, not basis uniqueness.

## Scope and attribution

This is an exact finite symbolic certificate and a scoped algebraic proof,
not a formal-kernel proof or a complete multiplication theorem. It concerns
the one retained owner-zero/port-zero word. It does not classify changed
hosting, translations, event order, stream charts or other owner/port words,
and does not provide a native layout, supplier or new scalar-operation bound.
The arbitrary reciprocal-chart single-receiver question in PR3254/PR3275
changes a different interface and is not being ruled out here.

The selected geometry and schedule, retained census authors and upstream
sources are credited in `README.md` and `SOURCES.json`. PR3263 identified the
failure of rank-only acceptance for a donor candidate. PR3272 supplied the
five-site exact phase algebra and rank-average method; this proof uses that
method and derives the entire simultaneous twenty-parameter map and its
inverse. Its result applies to all twenty sites, including potential receivers
with currently empty residual bases, rather than treating each receiver as
a separate single-site experiment.

## Open next questions

Determine whether a specified change of hosting, translations or stream charts
creates a nontrivial phase equivalence while retaining all source operator
and native-cost obligations. An operator result for another owner/port must
be bound to that word; the present certificate supplies no universal claim
over the remaining groups. Equal-rank, equal-phase basis changes are also
still possible and need their own geometry and cost analysis.
