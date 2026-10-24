# Exact shared Fourier cancellation at arbitrary arity

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped algebraic proof with finite corroboration; no new kappa.** For a
product of k independent inputs, a shared phase-weighted Fourier routine can
have a translated read layout and nontrivial phases. This happens precisely
under the torsion and root-of-unity conditions below. At two inputs the result
reduces to Hanson Sun's [PR1477](https://github.com/CrocSwap/integer-mult-bounds/pull/1477)
phase-free criterion, which builds on Ross Richardson's
[PR940](https://github.com/CrocSwap/integer-mult-bounds/pull/940).

The new repository contribution is the exact higher-arity classification and
its count, including a three-input translated example. The coefficient method,
Fourier duality and the two-input result are predecessor work. No literature
priority for elementary character algebra is claimed. No predecessor verifier
is replayed or incorporated as the deliverable.

## Statement

Let G be a finite product of cyclic groups Z/q_i, each q_i>=2, let N=|G|,
and use the symmetric nondegenerate pairing

    chi(x,y) = exp(2*pi*i*sum_i x_i*y_i/q_i).

Both Fourier signs have normalization 1/N. A read permutation means
`(P_pi f)(x)=f(pi(x))`, and `D_w` multiplies coordinate x by w(x), where
|w(x)|=1. Set

    A = D_w P_pi F^-,       bar(A) = D_conj(w) P_pi F^+.

For any integer k>=2, the identity

    bar(A)[ product_(j=1)^k A(u_j) ] = (u_1 * ... * u_k)/N^k             (1)

holds for every independent tuple u_j in C^G if and only if

    pi(x) = L(x)+b,
    L is a self-adjoint group automorphism,
    (k-1)b = 0 in G,
    w(x) = c*chi(-x,b),        |c|=1,        c^(k-1)=1.                 (2)

Self-adjoint means `chi(Lx,y)=chi(x,Ly)` for the actual product-group
pairing. Unequal cyclic factors do not in general use ordinary matrix transpose.
Convolution in (1) is unnormalized. The product inside the transform is pointwise.
The bar on A means coefficientwise conjugation, not its adjoint or inverse.

For example on Z/2 at k=3, take `pi(x)=x+1` and `w=(1,-1)`.
It satisfies (1) for all three inputs. The same routine fails at k=2.
Thus the two-input phase prohibition does not extend to all arities.
On Z/2 the constant phase i fails at k=3 and succeeds at k=5.

## Proof

Write f_j=F^-u_j. These range independently over all functions on G.
The ordinary normalized convolution identity gives
`F^+(product_j f_j)=(u_1*...*u_k)/N^k`.
For each output x, compare the coefficient of
`product_j f_j(pi(y))`. Since pi is bijective, exactly one coordinate y
contributes to that monomial. Consequently (1) is equivalent to

    conj(w(x))*w(y)^k*chi(pi(x),y) = chi(x,pi(y))  for all x,y.          (3)

Set y=x. Symmetry cancels the character factors and |w(x)|=1 gives
`w(x)^(k-1)=1` for every x. Hence `w(x)^k=w(x)`.
Set b=pi(0) and c=w(0). Taking y=0 in (3) gives
`conj(w(x))*c=chi(x,b)`, so `w(x)=c*chi(-x,b)`.
At x=0 the pointwise root condition gives `c^(k-1)=1`.
For all x it then gives `chi(x,(k-1)b)=1`. Nondegeneracy forces
`(k-1)b=0`.

Substitute these weights into (3) and put `L(x)=pi(x)-b`. All offset
characters cancel. What remains is

    chi(L(x),y) = chi(x,L(y))  for all x,y.                            (4)

For any x,z,y, the right side of (4) is multiplicative in x, so
`chi(L(x+z)-L(x)-L(z),y)=1`. Nondegeneracy forces additivity of L.
Subtracting b preserves bijectivity, so L is an automorphism, and (4)
is exactly self-adjointness. This proves necessity.

Conversely, (2) gives `w(y)^k=w(y)`. Self-adjointness and symmetry imply

    conj(w(x))*w(y)*chi(Lx+b,y)
      = chi(x,b)*chi(-y,b)*chi(Lx,y)*chi(b,y)
      = chi(x,Ly+b).

This is (3), proving sufficiency and (1) for all complex inputs.
The argument is a written all-group proof, not a proof-kernel certificate.

## Exact finite count

Restrict w to the Mth roots of unity, where M is a multiple of the exponent
of G. Write S(G) for the number of self-adjoint automorphisms and G[t] for
the subgroup killed by t. The exact number of shared routines at arity k is

    S(G) * |G[k-1]| * gcd(M,k-1).                                    (5)

Indeed L, b and c in (2) are uniquely recoverable from pi,w. There are S(G)
choices for L, |G[k-1]| choices for b and gcd(M,k-1) choices for c.
All resulting character weights are Mth roots. For a cyclic-factor
presentation, `|G[k-1]|=product_i gcd(q_i,k-1)`.

The declared exhaustive census uses M=lcm(4,q_i) and k=2,3,4,5.
It compares the literal coefficient equation (3) with reconstruction of
(2), including an explicit additivity check, for every permutation and phase
vector. It also checks (5).

| G | M | Candidates per arity | k=2 accepted | k=3 | k=4 | k=5 |
|---|---:|---:|---:|---:|---:|---:|
| Z/2 | 4 | 32 | 1 | 4 | 1 | 8 |
| Z/3 | 12 | 10,368 | 2 | 4 | 18 | 8 |
| Z/4 | 4 | 6,144 | 2 | 8 | 2 | 32 |
| (Z/2)^2 | 4 | 6,144 | 4 | 32 | 4 | 64 |

The two-input column is inherited mathematics and a boundary control.
The higher-arity columns corroborate the new classification. PRIMARY.json
is generated by verify.py and binds its ordered classification stream and
source hashes. It is not a handwritten receipt.

oracle.py imports no primary or predecessor code. It performs the actual
unnormalized negative Fourier passes, pointwise products, conjugate positive
pass and direct cyclic convolution over the exact rings Z[i] and
Z[z]/(z^4-z^2+1), where z is a primitive twelfth root.
Scaling both sides by N^(k+1) makes the expected output N times the integer
convolution. It checks every basis input tuple for every admitted map, plus
one dense integer tuple per map. ORACLE.json is its generated source-bound
receipt. Seven separate semantic controls exhaust their basis domains,
including wrong arity, a forbidden torsion shift, a wrong character sign and
a non-self-adjoint linear map. No rejected-case root cause is inferred from a
mere count. The complete census checks necessity through (3); the separate
transform replay corroborates the admitted cases and named controls.

## Reproduce

From the repository root, with the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/multiinput-shared-fourier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/multiinput-shared-fourier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/multiinput-shared-fourier/oracle.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/multiinput-shared-fourier --check-source-history
```

On another host, substitute its CPython 3.12 path. The registered manifest runs
both verifiers normally and optimized, with warnings as errors. Each default
run reads and compares its full receipt and writes nothing. Explicit
`--write NEW_PATH` generates a fresh receipt and refuses an occupied path.
The two predecessor READMEs are hash-bound live inputs, so a standalone source
export must retain them at their declared repository-relative paths.

## Limits and engineering choices

This is exact algebra for k independent functions and unit-modulus weights.
It supplies no physical Fourier schedule, free phase application, rounded
implementation, tape route, supplier recurrence, complete multiplication theorem
or selected-frontier change. All existing ownership, restoration, native,
compiler, precision and analytic transfer obligations remain separate.
Independent human and formal proof-kernel review are unclaimed.

The fixed census has at most four points, twelve phase choices per coordinate
and four arities. The reference classifier rejects groups above 64 points,
more than three factors, factors outside 2..8 and arities outside 2..64.
These executable limits do not narrow the written theorem.
Loops have finite collection bounds; there is no recursion or dynamic code.
Functions fit within 60 physical lines. Python requires dynamic allocation
and arbitrary-precision integers. This is a Power of Ten rule 3 deviation for
the two finite verifiers: the fixed enumeration domain bounds all live vectors,
ring degrees and integer sizes, and no whole census stream is retained.
The classifier has at most 64 points and its fixed census has at most four.
The oracle uses at most five inputs, four points and ring degree four.
The compensating checks are the exhaustive replay and capacity rejection
controls. Reassess the bounds before expanding the executable domain.
Diagnostics use warnings as errors and optimized replay; no new shared
repository build configuration is changed.

## Open next questions

Can one actual three-input convolution caller absorb the permitted two-torsion
shift and its character weights at lower complete cost? Start with one literal
three-input schedule and the Z/2 translated fixture, then price every read map,
phase, intermediate product, restoration and output conversion. No such physical
schedule or favorable invoice is supplied here, so algebraic permission alone
cannot justify a construction expansion.

Can separately weighted, separately addressed forward routines be classified
for k inputs with a shared final contract? Start by comparing multilinear
coefficients before assuming the forward addresses agree. PR1477 settles the
two-input independent-map case. Physical relevance and a cost advantage remain
unestablished; this follow-on was not pursued after the first verified result.

## Sources and credit

Canonical base is 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
The selected record remains kappa=0.00302015. Source-bound orientation passed;
the full selected supplier was not replayed.

Hanson Sun's PR1477 at f24bb18c20f7bdb3cbc27a1b6a010babf427d6cc supplies
the phase-weighted coefficient method and two-input classification.
Ross Richardson's PR940 at fccac36fa9bcc063c4fda733299a22349ce10e56 supplies
the unweighted adjoint criterion. Their READMEs and inherited source notices
remain unchanged. The retained Fourier manuscript and CrocSwap construction
supply the normalization and application context. SOURCES.json binds the exact
retained predecessor bytes at the canonical base; replay requires no pending
branch or imported predecessor executable.

The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133995)
reserves this higher-arity question. Overlap checks covered live open PRs,
recent handoffs and active Discussions, this account's recent work, targeted
merged searches and main's READMEs. They are bounded novelty checks, not a
literature-priority guarantee. TASK.json records the scope change from the
current audit card to this original interface extension.
