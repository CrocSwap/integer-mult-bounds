# Independent formal endpoint audit of the balanced caller

## Exact proposition

Let

```
R = Z[Q^±1,D_1^±1,...,D_19^±1].
```

The variables are formal, distinct and commuting. For the exact 353-event
caller in `sources/CONTROLLER.json`, the resulting matrix on all 34
independent input fields is the declared diagonal matrix over `R`. All
1,156 matrix cells are checked as exact integer Laurent polynomials; the
final matrix has 34 nonzero monomials, each with coefficient +1.

The source is PR6348 head
`9894015d6f380206f990ad5fd14bc49bbd26b0d0`, retained at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The caller bytes have SHA256
`6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f`
and Git blob `1f2e375b24aba5fb25580dfea7fab7a2049f3eb8`. The source
generator, four-field checker, proof and notice are retained and authenticated
as predecessor data. Neither new evaluator imports them or the other
evaluator.

This proves the formal endpoint premise deliberately left open by PR6359's
declared-diagonal invoice audit. It does not prove that physical native
operators or caller contacts implement these formal events or satisfy their
commutativity premises.

## Literal event semantics

For a state column `x` in `R^34`, the exact event meanings are:

| Event | Update |
|---|---|
| `ADD(dst,src,c)` | `x_dst <- x_dst + c*x_src`, with integer sign `c` |
| `SCALE(r,c)` | `x_r <- c*x_r` |
| `SWAP(a,b)` | Exchange the two fields |
| `QUERY(dst,src,e)` | `x_dst <- x_dst + Q^e*x_src` |
| `Q_POWER(r,e)` | `x_r <- Q^e*x_r` |
| `IDLE(a,b,J)` | Multiply both fields by `product_(s in J) D_s` |
| `LOCAL(s,src,dst)` | First `x_dst <- x_dst + Q^-1*x_src`, then multiply both fields by `D_s` |

In particular, a negative QUERY exponent is an inverse power of `Q`, not an
ordinary minus sign. The source proof's notation `q` means `Q^-1` here.
The LOCAL update on its ordered source/destination pair is

```
(u,v) -> (D_s*u, D_s*(v+Q^-1*u)).
```

No input is initialized to zero. The 32 fields introduced inside the three
trees are original arbitrary public inputs, as are the two exterior fields.
The source's 21-slot target annotation contains `Q`, a reserved stage-zero
slot, and stages 1 through 19. Both evaluators require the reserved slot to
be zero; the polynomial ring has only the twenty actual variables above.
There is no relation such as `Q^4=1`, and exponents are not reduced modulo
any integer.

The exact event census is 103 SWAPs, 112 ADDs, 67 SCALEs, 19 LOCALs,
16 QUERYs, 16 paired IDLEs and 20 Q_POWERs. Every LOCAL stage 1 through 19
occurs exactly once. These are source-binding checks, separate from the
coefficient calculation used for mutated words.

## The declared diagonal, explicitly

For each role `r`, write its target as
`m_r = Q^epsilon_r * product_(s in J_r) D_s`. The following table specifies
all 34 targets. Each interval denotes all integers between its endpoints.

| Roles | Q exponents, in role order | Common stage set |
|---|---|---|
| 0,1 | +1,−1 | 1..19 |
| 2,3 | −1,+1 | 1..4 |
| 4,5 | +1,−1 | 1..2 |
| 6,7 | −1,+1 | 3..4 |
| 8,9 | +1,−1 | 5..11 |
| 10,11 | −1,+1 | 5..7 |
| 12,13 | −1,+1 | 6..7 |
| 14,15 | +1,−1 | 8..11 |
| 16,17 | −1,+1 | 8..9 |
| 18,19 | +1,−1 | 10..11 |
| 20,21 | −1,+1 | 12..19 |
| 22,23 | +1,−1 | 12..15 |
| 24,25 | −1,+1 | 12..13 |
| 26,27 | +1,−1 | 14..15 |
| 28,29 | −1,+1 | 16..19 |
| 30,31 | +1,−1 | 16..17 |
| 32,33 | −1,+1 | 18..19 |

The primary additionally binds the target annotations to the sixteen
internal-node role pairs, stage sets and orientations, checking each node's
actual QUERY and paired IDLE. This prevents treating a detached diagonal
list as evidence about an unrelated trace.

## Why the exact coefficient certificate proves the proposition

Each event defines an elementary matrix `E_j` over `R`. In chronological
order the state satisfies `x_j=E_j*x_(j-1)`, so the complete matrix is
`M=E_353*...*E_1`. Every entry is a finite Laurent polynomial. Its canonical
representation records each integer exponent vector and its integer
coefficient, combines equal monomials and deletes coefficients equal to
zero. Distinct formal monomials form the defining coefficient basis of `R`.
Equality of these complete dictionaries is therefore polynomial equality,
not agreement at sampled values of the variables.

`verify.py` reconstructs each output functional backwards. Starting with
`lambda=e_r^T`, it substitutes each event in reverse chronological order,
using `lambda_before=lambda_after*E_j`. For a LOCAL event, the two new
functional weights are

```
lambda_src' = D_s*lambda_src + Q^-1*D_s*lambda_dst,
lambda_dst' = D_s*lambda_dst,
```

using the old weights on both right-hand sides. This is an algebraic
transpose pullback on coefficient vectors. It is neither a Hermitian
adjoint nor inversion of the caller: it performs no conjugation and does
not reverse the signs of literal powers.

Induction over the reversed instructions proves that the resulting row is
exactly `e_r^T M`. The primary computes all 34 rows and checks
`M_(r,c)=0` for `r!=c` and `M_(r,r)=m_r` for every role.

`oracle.py` uses a separately implemented representation: twenty-component
integer exponent tuples. It propagates each independent input basis column
forward through all 353 events. Its LOCAL implementation preserves the old
source column, scales both fields and adds the appropriately shifted source
to the destination. Forward induction gives exactly `M*e_c`; all 34 columns
agree with the same advertised diagonal. The reverse engine instead uses a
central exponent and a sorted stage-label multiset. Neither engine uses a
finite-order quotient, a numerical evaluation, the author replay or the
other engine.

Both exact matrix encodings give SHA256
`8263cc6b643ee815427d7d8a08e1080e920b9de070bac26a49383424f9d20fd2`.
The hash summarizes the coefficient certificate; each evaluator first checks
the complete matrix itself. The full result applies to every vector of
`R^34`, so all 34 original inputs remain arbitrary and have no off-diagonal
leakage.

As a separate consistency check, multiplying event determinants gives

```
det(M) = product_(s=1,...,5) D_s^6
         * product_(s=6,...,19) D_s^8.
```

Its coefficient is +1 and its Q exponent is zero, matching the product of
the 34 declared diagonal entries. This is a unit in `R`; no input dimension
is discarded by the formal caller.

## Specialization and its exact limits

Let the formal variables be replaced by pairwise commuting units of a
unital ring, or by pairwise commuting invertible linear operators on a
common module. The universal property of the Laurent ring gives a unital
ring homomorphism to their commutative image. Applying that homomorphism
entrywise preserves the proved matrix equality. The coefficient ring may
have zero divisors; no division by a nonunit or field-only argument is used.
Units supply the meaning of negative powers.

This specialization need not be injective or faithful: actual operators
can have additional relations. No converse from a specialized identity to
the formal identity is claimed. Noncommuting substitutions are outside the
proposition. In particular, this audit does not establish physical stage
commutativity, the LOCAL ABI, orientation wrappers, absolute phases, or
native tensor-power realization.

## Controls, prior coverage and credit

Seven primary changed words and eight independent-oracle changed words are
structurally parsed and then actually evaluated. They are not rejected
merely for changed source hashes, event counts or repeated stage labels.
The mutations remove an IDLE, Q_POWER or QUERY; flip a query exponent or ADD
sign; replace an IDLE stage; or alias a LOCAL stage. Each gives an explicit
input/output, exponent tuple and unequal integer coefficient.

The oracle's eighth control flips a legal Q_POWER from −2 to +2. Its power
changes by four and the formal replay rejects it. That difference can vanish
after imposing `Q^4=1`; the certificate therefore labels this as a formal
counterexample, not a physical failure under such a specialization.

Ali Romman, with substantial OpenAI Codex assistance, supplied the
four-field extension, its separate module checker, the tree proof and this
literal caller in PR6348. The new contribution is an independent exact-source
endpoint audit, not discovery of the four-field identity or a new general
Laurent or lifting theorem. Retain Cinna Davis's thin-query/path interface,
the PR6167/PR6144 and native lineage, and the complete `sources/NOTICE`.

Clear1nsight's PR5550 and flyingviper's PR5717 audit earlier 32-bank,
eighteen-call interfaces. Selected PR6030 has a different eighteen-call
caller. Matarener's PR5442 binds a lifting/group-algebra argument to the
older PR5413 caller, and PR4457 isolates a physical commutativity premise.
Those results retain their credit; they are not source-bound checks of this
new 353-event trace. This package's reverse-functional, forward-column and
mathematical reviews were separately assigned for ToikY with substantial
OpenAI Codex assistance. Same-session agent review is part of the author
process, not independent human or formal-kernel acceptance.

Remaining obligations include physical operator binding and commutativity,
all native maps/widths and phases, caller contacts, owned-query lifetimes
and erasure, complete paid/ordinary funding, precision/tape, compiler and
outer admission. The finite invoice and native-matrix audits in PR6359 and
PR6360 remain their own bounded results. The five assumptions
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery` remain. No new admitted kappa, multiplication theorem
or selected-frontier change follows.
