# Operator-valued paid controls: exact theorem fit

Prepared 2026-10-23 for root's bounded one/two-child construction gate.
This is an applicability note, not a new impossibility theorem, constructed
control or priced physical implementation. The mandatory predecessor is the
[operator-valued coefficient-rank counterexample](operator-valued-gather-rank-boundary.md).

## The existing 112-call theorem already permits operator-valued gathers

The exact source is Dillon's [PR #5126](https://github.com/CrocSwap/integer-mult-bounds/pull/5126),
head `0e8a13c251a9be1029114cda8b4194f05f3a23ec`,
`research/coded-active-query-bound/PROOF.md`, sections 1 through 5 and the
scope section. Its exact source snapshot is
[SOURCES.json](../operator-valued-paid-fit/SOURCES.json).
The proof and extension review were read; their executable checks were not
replayed by this lane.

Let `B_f` be the finite-dimensional twisted algebra of a fixed finite
projective group of monomial one-column maps, with the same map lifted in all
columns. Its coefficients can depend on width. Free input rows and output
columns are arbitrary matrices over `B_f`, so their entries can be different
monomial operators or sums of them. They are not restricted to scalar owner
vectors. The theorem permits chronological linear feedback, independent dirty
inputs, clean scratch, saved responses, fanout and arbitrary paid unary maps.
It requires fresh inputs and equal-width counted fields.

For the actual source code `C=I-14P` and its canonical free retraction
`P=U_mode V_mode`, `V_mode U_mode=I8`, the source proves the following at every
sufficiently large tensor width:

| Required endpoint | Paid unary field calls |
|---|---:|
| `QP` or `PQ`, also with inverse Q | exactly 112 |
| `Q U_mode` or `V_mode Q`, including every free retraction rebase | exactly 112 |
| `J=Q^-1 C Q`, `J-I`, or a free perturbation | at least 112 |

The upper constructions for the first two rows use 112 H1 calls. This does not
assert that every minimum-count implementation uses H1. Homogeneous direct
sums have the corresponding `112m` statement. The source explicitly leaves
`V_mode Q U_mode`, `PQP`, unrelated changed endpoints, wider packed channels,
noncolumnwise maps and correlated already-paid native observations outside.

Thus the coefficient-rank counterexample does not invalidate #5126. The two
arguments use different invariants. The invalid extension extracts one scalar
identity coefficient from an operator-valued outer product. #5126 instead
uses the dimension of a module over the full free algebra.

## The reusable necessary condition and its missing target hypothesis

With `r` paid children and `n` fresh input fields, every acyclic linear circuit
has a normal form

```
y_t = H_t(b_t x + sum_(s<t) e_ts y_s),
T x = F0 x + sum_t l_t y_t,
```

where `b_t`, `e_ts`, `l_t` and `F0` have free-algebra entries. If `r<n`, stack
the `b_t` as a map `B_f^n -> B_f^r`. Finite-dimensional vector-space counting
gives a nonzero column `w` in its kernel. Substitution `x=w z` makes every
paid response vanish by induction, so `(T-F0)w=0`. This proof does not require
the algebra to be a division ring. The dual output cut gives a nonzero free
left relation when there are fewer paid responses than output fields.

#5126 closes this condition for its listed endpoints by actual source coset
separation: no such free right or left relation exists for any free bypass.
It is the source-specific no-relation fact that creates the numerical bound.

The changed four-control problem has an unknown `t0` and an unknown legal
endpoint `E=Q^-1 C3 (D3 t0 D3^-1) C1 Q^-1`. No reduction of every admissible
candidate to one of the endpoints in the table has been supplied here.
Applying the 112 bound to this entire family would therefore be unjustified.
A useful obstruction must first bind the actual endpoint or prove its own
no-free-relation statement. A proposed one/two-child control must instead
exhibit its actual words and all required inverse programs.

## Published Schur identities supply conditional inverses

Gelfand, Gelfand, Retakh and Wilson, *Quasideterminants*, Advances in Mathematics
193 (2005), DOI [10.1016/j.aim.2004.03.018](https://doi.org/10.1016/j.aim.2004.03.018),
give the ordered Schur expression over a unital ring in Proposition 1.2.6,
p.10 of the [inspected author preprint](https://arxiv.org/pdf/math/0208146).
The actual inverses in the expression must exist. This is useful for
constructing an inverse identity in the concrete operator algebra, rather
than transferring a generic rank lower bound.

For an operator-valued gather row `V`, scatter column `U` and one paid child
`H`, take `S=I+U H V`. When the middle inverse exists, ordered elimination gives

`S^-1 = I - U (I + H VU)^-1 H V`.

In particular the actual operator identity `VU=0` implies
`S^-1=I-U H V`. The inverse uses the same `H` with the opposite scatter sign.
No commutation assumption and no `H^-1` call are required. If `VU` is nonzero,
writing the one-field middle inverse does not implement or price it. Its
source access, precision, temporary ownership and all recursive calls remain
obligations.

For two chronological children, the normal form already preserves their
ordered interaction:

`T = F0 + l1 H1 b1 + l2 H2 b2 + l2 H2 e21 H1 b1`.

It cannot be replaced by the sum of two independent rank-one updates unless
the cross term is actually absent. Likewise, a product of two invertible
nilpotent-update shears has its inverse in reverse order; each use and every
control conjugate still needs its own physical cost binding.

Porat and Vinnikov, *Realizations of non-commutative rational functions around
a matrix centre, I*, JLMS 104 (2021), DOI
[10.1112/jlms.12459](https://doi.org/10.1112/jlms.12459), supply realization
synthesis over a unital algebra in Theorem 2.4, p.10 of the
[inspected preprint](https://arxiv.org/pdf/1905.11304). Its ordered product and
inverse constructions are (2.7) and (2.8), pp.12–13. These preserve algebraic
identities when the stated domain and invertibility conditions hold.
Their algebraic state dimension is not a theorem about native H1 call count.

## Why generic noncommutative rank is insufficient

The actual free algebra has relations and can have zero divisors. For a
nontrivial involutive Pauli translation `X`, `(I-X)(I+X)=0` although both
factors are nonzero. A universal free-field calculation does not retain this
specialized algebra unchanged. Generic inversion height, generic minimal
realization size or generic inner rank can therefore neither exclude nor
construct the required physical control without an exact specialization
argument. The source module cut avoids that problem by using ordinary
finite-dimensional linear algebra and an explicitly verified coset property.

No new paper was needed for these implications. No search over controls,
group enumeration, solver, native/history experiment or external write was
performed. The next useful input is the construction owner's actual candidate
and invoice, or an exact endpoint reduction missing from the present source.

## Construction-owner follow-up: a narrower translation module cut

The construction owner subsequently proposed a more specific family: every
internal free coefficient is in the Pauli-X translation algebra `B`, while
paid X-Gaussian children and translations generate a fixed finite projective
group algebra `A`. The target `T=t0` is invertible, commutes with Q and D3,
and its fourth endpoint is required to be monomial-Clifford free. This excludes
intervening free K/C programs outside B, arbitrary monomial gathers,
noncommuting children and a paid fourth endpoint.

The proposed source step is `projection_B(T)=0`. The author is deriving it
by isolating every translation coefficient in the actual fourth endpoint.
Matching such a term with a different owner pair would force the relative
source linear part to be identity; after the owner pair is fixed, the
translation itself must match. A translation does not change the symplectic
nonmonomial witness furnished by the source's zero diagonal. The full written
source-isolation and module argument have now been read in the construction
owner's report, with no blocking mathematical error found under its retained
source facts. Normalizer data, macro counts and native execution were not
independently replayed by this lane.

Conditional on that step, the resulting module argument is valid. At one
sufficiently large faithful width, a circuit with fewer than 112 paid children
has a nonzero `w in B^112` annihilating all direct paid-input rows. The circuit
then gives `T w=F0 w in B^112`. But right multiplication by B preserves the
nontrivial right cosets, so `projection_B(T)=0` puts `T w` in their direct sum.
The intersection is zero. Literal invertibility of T forces w to be zero,
a contradiction. This uses no scalar coefficient-rank bound and no
division-ring or semisimplicity hypothesis.

The conceptual check requires a fixed projectively finite A and free endpoint
alphabet, the same column lift at every width, exact cocycle phases and owner
coefficients applied once. It requires fresh equal-width input fields and all
bypass/gather/scatter/feedback coefficients in B. It covers the translation
operator-valued counterexample under those premises. It does not exclude the
full arbitrary-monomial family originally assigned to the construction owner.

The reviewed construction-owner report is `outputs/operator-valued-paid-control-gate-20261023/REPORT.md`, SHA256 `19932a49cda97acb2e3f4933f95d4bed5598e441d7593132bd07d15a63c23731`. Its explicit `U_i=X_(q_i)`, `V_i=c_i X_(q_i)^-1`, `H=Q` shear has `VU=0`; its direct fourth-endpoint implementation produces an additional `228 H1` invoice, which is an upper construction cost, not a lower bound for all paid endpoints. The report retains the incomplete ordinary bill and unexecuted caller. One minor clarity suggestion was to state explicitly that the commuting X-Gaussian generators have finite projective order, proving the fixed algebra is finite.
