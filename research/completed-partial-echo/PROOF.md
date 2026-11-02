# The exact completed-observation injection tariff

This contribution was produced by Nick Petalas. It is a scoped written
algebraic proof. Exact finite checks corroborate the implementation; they
are not a proof-kernel verification or a multiplication theorem.

## Boundary and alphabet

Work over any field of characteristic zero. Let X and W be vectors in the
same nonzero finite-dimensional space, and let D be a vector in another
nonzero finite-dimensional space. All three incoming vectors are arbitrary
and independent. X is an immutable source, W is borrowed dirty workspace,
and D is an additive receiver. There is no other data storage.

Fix s independently arbitrary linear maps L_i from the source space to the
receiver space. A word must work uniformly for every tuple of these maps.
Its available instructions, including their positive complete prices, are

| Instruction | Action | Price |
| --- | --- | --- |
| H_i | D += L_i W | c_i^+ |
| H_i inverse | D -= L_i W | c_i^- |
| J_+ | W += X | a |
| J_- | W -= X | b |

Every instruction leaves the other fields unchanged. H_i and its inverse
are fixed indivisible source-preserving blocks, including any internal
workspace restoration and normalization. No direct L_i X evaluation,
scalar rescaling, output feedback, query retention, map-dependent word,
additional borrowed field or free copying is permitted. Repetition and
arbitrary interleaving of all labels are allowed. In particular, a lower
bound may not assume that only H_i occurs between checkpoints i-1 and i.

There are ordered, read-only output checkpoints O_1,...,O_s. At O_j the
required receiver is exactly

    D_initial + (L_1 + ... + L_j) X.

The observer sees only D. W need not have its incoming value at a checkpoint.
At return, X and W must both equal their incoming values, and D must still
equal its final observed value. Observation execution has a separate cost,
common to every compared word and excluded from this instruction tariff.

## Theorem

The exact minimum complete instruction price is

    sum_i (c_i^+ + c_i^-) + ceil(s/2) (a+b).                 (1)

In particular, exactly 2 ceil(s/2) source injections suffice. Every word
needs at least one forward and one inverse use of each label and at least
ceil(s/2) uses of each injection direction. These bounds hold simultaneously
and are simultaneously attained, for arbitrary positive prices.

The unit-price minimum is 2s + 2 ceil(s/2). Separately executing s ordinary
restored echoes costs 4s. For s=2 the minimum falls from eight to six, with
both complete partial outputs observed. This comparison does not remove
any child calls. If a complete array injection costs N scalar additions,
the saving is 2 floor(s/2) N additions, before any changed routing costs.

## Lower bound

At every time the workspace has the form W_initial + eX, where e is an
integer. It starts with e=0. Only J_+ and J_- change it, by +1 and -1.

For each label i let A_i and B_i be the integer coefficients in the
receiver expression

    D = D_initial + sum_i (A_i L_i W_initial + B_i L_i X).

Initially all coefficients are zero. An H_i instruction with sign
epsilon in {+1,-1} changes A_i by epsilon and B_i by epsilon e.
Injections change none of these coefficients.

Uniformity in the independently arbitrary maps, together with independent
arbitrary X and W_initial, makes coefficient comparison legitimate.
For example, set all maps except L_i to zero and then set either input
vector to zero. A nonzero scalar multiple of every possible L_i cannot
vanish in characteristic zero. Thus at checkpoint j necessarily

    A_i = 0 for every i;       B_i = 1 if i <= j, else 0.   (2)

Include time zero as checkpoint zero. In the interval from checkpoint
i-1 to checkpoint i, A_i changes by zero while B_i changes by one.
Consequently the net number of forward minus inverse H_i instructions
in that interval is zero, and some H_i instruction must occur. There
must be at least one of each sign. Summing these label-specific bounds
gives the first term of (1), even if other labels occur in those intervals.

Every one of the s checkpoint intervals contains an injection. Otherwise
e would be constant on that interval, and the changes for every label
would satisfy Delta B_i = e Delta A_i. Equation (2) would give the
contradiction 1=0 for its newly observed label.

Let u,v be the total numbers of J_+,J_- instructions, including any
instructions after the final observation. Exact return of arbitrary W
requires u=v. Therefore 2u=u+v>=s, so u=v>=ceil(s/2).
All prices are positive. Adding these simultaneous bounds proves (1).

## Attainment and the first improvement

Start with e=0. For odd i execute the chronological triple

    H_i inverse; J_+; H_i; observe O_i.

Its receiver change is -L_i W_initial + L_i(W_initial+X)=L_i X,
and it changes e from zero to one. For even i execute

    H_i; J_-; H_i inverse; observe O_i.

Its receiver change is L_i(W_initial+X)-L_i W_initial=L_i X,
and it changes e from one to zero. These statements preserve arbitrary
incoming D and every prior completed output. If s is odd, finish with J_-.
If s is even no final instruction is needed. The final correction changes
only W, so the last observed output is preserved at return.

The word uses each H_i once in each direction, ceil(s/2) J_+ instructions,
and ceil(s/2) J_- instructions. It attains every bound above.

For the smallest strict improvement, s=2, the complete word is

    H_1 inverse; J_+; H_1; O_1; H_2; J_-; H_2 inverse; O_2.

At O_1 the workspace is W_initial+X; at O_2 and return it is W_initial.
Both receiver observations contain the external-source update, without
any contribution from W_initial. No hidden receiver observation is used.

## Relation to the cyclic question and its limit

PR4860 asks for completed partial external-source echoes, beyond its
canonical partial-batch record. The present result answers the normalized
block subproblem: supply a complete canonical batch H_i, price that block
and its actual inverse, and then apply the schedule above. Ross Richardson's
PR1287 supplies the cyclic-equivariant batching and ordinary dirty echo;
PR4860 supplies the canonical normalization tariff. Their costs are included
in c_i^+,c_i^- and are not re-established here.

The observer must allow the borrowed workspace to retain the shift X at odd
checkpoints. If W is also required to be restored at every observation,
the same proof applied within each interval forces at least one injection
of each sign there. Separate echoes then attain the exact price

    sum_i (c_i^+ + c_i^-) + s(a+b).

This explains the source of the saving and its boundary. It is not a claim
that canonical cyclic frames may be ignored inside a child, or that a caller
permits shifted workspace at its observations. No actual selected supplier
or observer is bound. The five framework assumptions, physical movement,
native access, ownership, precision, compiler and outer funding remain open.
