# Stronger completion and exact changed-field count

The governing [source proof](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/unit-query-review-20261015/GENERAL-COMPLETION.md)
has SHA-256
`df76e7ff4b532bfab58a9aea5ce7d29493305a76013ef6cd20fb38b7ad2dde01`.
Its [accepted review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/upstream-followthrough-20261015/general-completion-review/REVIEW.md)
checks each argument. The statements below retain its scope and notation
qualification. They do not add a native implementation claim.

## Completion and converse

Let A be a commutative ring with `1 != 0`. Work on n complete fields of
N coordinates, with `N>=1`. The query has d complete fields, where
`1<=d<=n`. Select d input fields S, and let U be their complement. For
maps R and K of compatible sizes, suppose `R_S=R i_S` has a two-sided
inverse. Put

```text
L = R_S pi_S,       G = i_S R_S^-1,
B = R-L,           D = i_U pi_U K,
J = I-KR,
T = (I-DL)(I+GB),
T^-1 = (I-GB)(I+DL).
```

The support identities `LG=I`, `LD=0`, and `BG=0` make both factors
invertible shears. Expansion gives `T=I+GB-DR`, `pi_U T=pi_U J`, and
`LT=R`. Thus T is a unit, retains every unselected row, and stores the
full query in S. No condition on the selected part of K or on RK is
needed. These two output equations determine T uniquely.

If R is onto, the existence of any such unit T with an arbitrary linear
readout `Q pi_S T=R` is equivalent to `R_S` being a unit. Surjectivity
forces the square Q to be a unit. A block row operation then makes
`[R; pi_U J]` triangular with diagonal blocks `R_S,I`. Both the onto
premise and the full-query requirement are necessary, as the two frozen
converse controls show.

If the selected part of K equals `R_S^-1`, the repair T-J is a split
projection. The general repair need not be a projection. This extra
projection property must not be transferred to arbitrary K.

## Exact count and actual specialization

Now also assume `RK=gI`, with scalar g. A unit d-field minor remains
available. Among all linear unit repairs of J, the minimum number c of
changed complete output fields is

```text
c_min = 0  if 1-g is a unit,
c_min = d  otherwise.
```

This minimization permits repairs that do not store the full query.
For unit `1-g`, the displayed source inverse makes J itself a unit. For
nonunit `1-g`, a residue field in which g becomes one gives J nullity
dN. The difference between a unit repair and J must be injective on that
kernel, so its rank is at least dN. A change in c whole fields has rank
at most cN. The completion above attains the resulting bound c>=d.

For the pinned actual matrix, `A=Z[i,1/2]`, `n=112`, `d=8`,
`K=R^T/4`, and `RK=14I`. The selected ports are
`[0,7,20,27,36,46,57,111]`; their minor has Gram matrix `4I`.
Both maps to F13, with i sent to 5 or 8, are valid. The residue nullity
is 8N and the exact minimum is eight changed fields. Realification gives
the same count for dyadic real-linear unit maps, including conjugation,
by using both Gaussian sectors and 2N coordinates per complex field.

The lower bound also covers a nonlinear map only when it has a
surjective reduction on the full residue module and retains the same
unchanged outputs. Here U_c denotes the n-c unchanged fields. The
inequality is `rank(pi_Uc Jbar) <= (n-d)N < (n-c)N` when c<d.
It gives no conclusion for a rounding code without that residue map.

The module must include every cover and payload coordinate. Restricted
inputs in `ker(R)` already have `J=I`. Allowing division by 13 also
removes this actual ring obstruction. Unit endpoint views must be units
over the stated ring; fieldwise output views preserve the changed-field
support. Unequal physical frames still require valid native access.

The source local word pays eight native line children, but the rank
argument does not prove that child count necessary. Native access,
recursive hosting, workspace, finite precision, and complete supplier
admission remain outside this annex. No selected frontier or kappa claim
changes.
