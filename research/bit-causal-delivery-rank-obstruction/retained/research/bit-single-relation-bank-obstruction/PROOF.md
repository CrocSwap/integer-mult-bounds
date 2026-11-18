# One binary helper relation cannot improve this fixed BIT word

The input is the 659-public-field native word retained by
[PR #7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001).
[SOURCES.json](SOURCES.json) pins its compressed bytes and the paired caller.
This result concerns one linear relation over F2 on one group of helpers with
the same entrance and exit charts. It covers both orientations separately.
It gives no new multiplication exponent.

## Contract and price

Let G be one of the nine helper groups. Its entrance is A and its exit is D.
Let H_G be the coordinate space on those helpers. Impose `u*x_G=0` for any
nonzero vector u in H_G. Free invertible changes of helper basis at A and D
can express this promise as the removal of one productive helper. The lost
productive rank is `d=abs(dim(D)-dim(A))`.

Keep the source word, its frames, the paid capture forms and their order fixed.
Grant free storage of every past paid bank at its arrival chart. Also grant
all public entrance fields at their entrance charts. Grant all ordinary
scalar XOR work for free. A paid bank can be omitted only if its value under the
promise is a linear combination of strictly earlier banks and entrance
fields at that same chart. The relation must hold for every remaining
arbitrary public input. This is an optimistic cost model. An exclusion in
this model also applies when these extra resources have positive costs.

The scope does not include a new paid route, a changed capture form, a second
relation, a group with different boundary charts, nonlinear operations or a
composition of forward and transposed changes. Receiver coefficients
are scalars in F2; matrix-valued receiver coefficients are outside scope.

## Exact receiver criterion

At chart C, place all entrance rows first and all paid arrival rows in time
order. Let V_C be their span in the full 659-dimensional entrance space.
The two replays verify that this ordered list is linearly independent at
every chart, in both orientations.

After imposing u, a relation between bank rows can arise only if their sum
is u. Define `L_C = V_C intersect H_G`. Thus a dependency is possible exactly
when u belongs to L_C. Since the original bank list is independent, the
representation of u is unique.

At C=A, the representation uses free entrance fields. The promise lowers
the rank of the free entrances by one and creates no paid saving. At C
other than A, the unique representation must contain a paid bank. Its last
paid token is the only bank that can be recovered from earlier tokens under
the promise. Before that token there is no relation. After removing that
token, all later rows remain independent modulo u. Thus at most one paid
bank can be omitted at each chart. This argument accounts for all causal
linear substitutions, including substitutions through other omitted banks.

The certificate supplies a basis of every nonzero L_C with literal bank
witnesses. A separate checker verifies each witness and proves completeness
from the rank formula

```text
dim(L_C) = number of independent bank rows - rank(rows projected outside G).
```

It checks this formula at every receiver, including charts whose intersection
is zero. It does not assume that clean directions are coordinate vectors.

## Complete finite reduction

At D, the clean space is all of H_G. Every other receiver has clean dimension
at most four in the forward orientation and at most two in the transpose.
Enumerate the union of all nonzero vectors in these small nonterminal spaces.
This gives 664 forward and 125 transposed directions. The union, not a list
of basis vectors, is needed: it includes noncoordinate directions.

For each such direction, the unique witness gives every receiver and the
last paid token at that receiver. In every one of these 789 cases, the sum
of removed paid ranks is strictly less than d.

Every other nonzero u can affect only the terminal chart D. To cover these
unlisted directions, the first checker computes leading positions of the
terminal witness space. The second checker instead grows prefixes of the
bank list and records each increase of the clean prefix dimension. These
are exactly the possible last paid tokens. Every such token has rank at
most d. This covers all `2^410-1` possible nonzero relations in the largest
group without enumerating them.

| Orientation | Helpers in groups | Exceptional directions by group | Maximum nonterminal dimension |
| --- | --- | --- | ---: |
| Forward | 410,2,1,7,6,5,3,2,1 | 661,2,1,0,0,0,0,0,0 | 4 |
| Transpose | 410,2,1,7,6,5,3,2,1 | 100,2,1,6,6,5,3,2,0 | 2 |

The complete per-group counts and terminal rank bounds are in
[RESULT.json](RESULT.json). The full bases, witnesses and exceptional cases
are in [CERTIFICATE.json.gz](CERTIFICATE.json.gz).

## Signed power inequality and complete caller

Write `t=1-kappa`. For `99/100 <= t <= 1`, every positive integer rank r
satisfies `r^t <= r`. The lost ranks are 2, 4, 6 and 8. Exact integer checks
prove `d^99 > (d-1)^100` for each of these ranks. Thus every exceptional case
satisfies

```text
sum(saved_rank^t) <= sum(saved_rank) <= d-1 < d^(99/100) <= d^t.
```

The removed paid moment is smaller than the lost productive moment. The
signed target-minus-paid margin strictly decreases. For every remaining
direction there is at most one removed paid rank r, with `r<=d`. Then
`r^t<=d^t`, so the margin cannot increase. Equal ranks cancel exactly.

The source paired caller has 36 local invocations. Its complete invoice has
107352 paid calls, 19950 productive targets and rank surplus 1506. Both
implementations recount its query, idle and root terms. Fixed caller terms
cancel in the change; the local difference is multiplied by 36. One changed
invocation also cannot give a gain. No whole-call saving is inferred from
a paid count alone. The theorem covers `0<=kappa<=1/100`, which contains the
selected saving and the source BIT saving. No frozen-profile ceiling from a
different caller is used.

## Verification and limits

[census.py](census.py) uses packed binary rows and highest pivots.
[independent.py](independent.py) replays all public endpoints and paid rows
with coordinate sets, checks dimensions with lowest pivots and checks
terminal pivots with prefix ranks. It also verifies all 636 rational frame
bases, orthogonal complements and strict nested paid pairs. Both directions
start with independent public inputs. Reverse CLEAR introduces zero; reverse
INIT discards its owned value; reverse ADD acts on the donor.

[verify.py](verify.py) compares the complete generated certificate and summary.
It rejects an omitted target debit, an omitted receiver, an omitted
noncoordinate direction, a corrupted witness, a future donor and an omitted
terminal pivot. A positive equal-mass split control shows why strict rank
deficit is needed; equal integer mass alone would not prove this exclusion.

The two implementations were written by the same author after reading the
source. This is author checking, not blind review or formal acceptance.
The caller's physical identity, native phases, owned storage implementation,
compiler and tape interfaces, analytic framework and all five framework
assumptions remain inherited. Full predecessor suites, selected cold replay,
Lean and Docker were not run. No physical construction is claimed for the
free retained banks. Since this is an optimistic exclusion, their cost can
only strengthen the result within the stated fixed-word scope.
