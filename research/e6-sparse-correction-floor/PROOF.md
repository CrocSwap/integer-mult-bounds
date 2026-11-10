# A support obstruction for the fixed E6 correction

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written invoice proof with exact finite corroboration.

## Contract and cited premises

Use Cinna Davis / 1337isnot1337's PR2240 factorization, fixed dense pairing
B0 and seven-term pricing contract. Write X for its full-column-rank
36-by-6 coordinate matrix and H for its symmetric basis Gram matrix.
The original six columns have the cited pairing ranks

```text
(r_1,r_2,r_3,r_4,r_5,r_6) = (6,7,6,6,6,6).
```

These ranks are trusted mathematical premises from PR2240, not independently
recounted or re-certified here. Each nonzero term with pairing rank r has
fully charged cost max(5,r). The source certificate, exact source head and
retained bytes are pinned in SOURCES.json. Its model and Theorem C lineage
credit PR1590 and the retained root-unit contributors.

For nonzero rational a in Q^6 and nonzero rational lambda the correction is

```text
p_i = X e_i,       q_i = X(H e_i-lambda a_i a),   1<=i<=6,
p_7 = X a,         q_7 = lambda X a.
```

Cancellation gives sum_i p_i q_i^T = X H X^T. The factorization and this
identity are credited to PR2240. A genuine seven-term member has every q_i
nonzero. X has full column rank, so the p_i, p_7 and q_7 are nonzero.

## The new bound

Let s be the number of nonzero coordinates of a, and let epsilon be one if
a_2 is nonzero and zero otherwise. For every positive real q, the complete
seven-term charged moment satisfies

```text
sum_(i=1)^7 max(5,r_i(new))^q
 >= (s+1) 5^q + (5-s+epsilon) 6^q + (1-epsilon) 7^q.        (1)
```

In particular its unit-price charged cost C satisfies

```text
C >= 42-s-epsilon.                                       (2)
```

To prove (1), if a_i=0 then q_i=X H e_i and the entire original term,
including its support and pairing rank, is unchanged. Exactly 5-s+epsilon
of those fixed terms have rank six and 1-epsilon has rank seven. The s
changed terms and the extra term each pay at least five. Positive powers
preserve these inequalities. Summing proves (1); setting q=1 proves (2).
This argument does not enumerate or bound the rational coefficients.

The bound is sharp for the relaxation that records only the unchanged ranks
and the five-unit floor of the other terms. Assigning five to every changed
and extra term attains its right side. This is an abstract invoice witness,
not a decoder, a simultaneous rank-attainment theorem or a physical program.

## Consequences for the rational two-coordinate family

Every direction supported on at most two coordinates has C>=39. If its
support excludes coordinate two then a two-coordinate direction has C>=40.
For the claimed plane a=e_1+t e_2, t rational, the floor is 39 when t!=0
and 41 when t=0. No minimum decoder cost or attainment of either floor is
asserted.

The seven-term condition is automatic for these directions. The source
basis matrix is

```text
H = [2 0 1 1 1 1
     0 2 1 1 1 0
     1 1 2 1 1 1
     1 1 1 2 1 1
     1 1 1 1 2 1
     1 0 1 1 1 2].
```

Every H e_i has at least four nonzero coordinates. If q_i=0 then full column
rank of X gives H e_i=lambda a_i a. If a_i=0 this contradicts H e_i!=0;
otherwise its right side has at most two nonzero coordinates. This is also
a contradiction. Thus the whole rational two-coordinate family, including
all nonzero lambda, is covered without excluding untested degeneracies.

Equation (2) also gives necessary support conditions for any genuine member
to match or improve the original six-term cost 37. Cost at most 37 requires
s+epsilon>=5, hence at least four nonzero coordinates; if exactly four,
coordinate two must be included. Cost at most 36 requires at least five,
again including coordinate two when there are exactly five. These are
necessary conditions, not constructions or sufficient conditions.

The elementary fixed-term argument is the new step. PR2240 supplies the
factorization, the six ranks, finite-alphabet screen and tariff. PR2247
changes the base by elementary shears and is outside this fixed-base result.
DreamingOfClouds's PR2277 supplies the broader root-code floor 36. It already
excludes cost 35 for all such root-code decoders. The new support gate is
stronger for this sparse fixed-base family and does not replace that theorem.

## Finite evidence and limits

The verifier enumerates all 63 nonempty coordinate supports. For each support
it exhausts charged ranks in {5,6,7} on its changed and extra terms, keeping
the other ranks fixed. There are exactly 3(4^6-1)=12,285 abstract invoices.
Every invoice dominates the sorted lower profile coordinatewise, and each
of the 63 abstract minima attains (2). The bound for arbitrary larger ranks
follows from the written monotonicity argument, not this finite alphabet.

The new parameter fixtures cover all 15 coordinate pairs, four rational
ratios outside the earlier ternary pair alphabet and four nonzero rational
lambda values. These 240 fixtures check coefficient cancellation, unchanged
terms and absence of zero factors. They do not recompute E6 pairing ranks or
replay PR2240's published census. Five invalid supports are rejected, and
explicit ordinary/exceptional/full-support boundaries guard the debit.

This is a fully charged Theorem C invoice obstruction, not a raw-rank floor
or complete physical supplier bill. Exact minimum cost on the rational plane,
compatibility of the abstract minimum ranks, dense directions, changed bases,
native realization, ownership/restoration, routing, precision/tape, stock,
compiler and outer costs remain open. All five selected framework assumptions
retain their status. No new kappa, selected-frontier change, supplier admission,
complete multiplication theorem, independent human or formal proof-kernel
acceptance is claimed.
