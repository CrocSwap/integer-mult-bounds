# The ternary quaternion negative pair costs exactly six calls

This finite exact certificate establishes the minimum **six** for
`diag([i^-1],[j^-1])` in the full formal algebra `F3[Q8]`, with exactly two
arbitrary dirty roles, positive paid labels `i,j`, all ternary rank-one
idempotent couplings, and arbitrary free `GL2(F3)` scalar mixing. Changing
the scalar field from F2 to F3 supplies no sharing gain for this endpoint.
No new kappa or selected-frontier change is claimed.

This contribution was produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed. New work is Apache-2.0.

## Model and exact conclusion

Write `Q8={1,z,i,zi,j,zj,k,zk}`, where `i^2=j^2=z`, `z^2=1`, `ij=k` and
`ji=zk`. These are eight independent formal basis elements over F3. In
particular `[zi]` is not the coefficient multiple `2[i]`.

A charged factor is

```text
D_N(g) = I_2 + ([g]-[1])N,
g in {i,j}, N in M_2(F3), rank(N)=1, N^2=N.
```

All input values are independent and arbitrary. The complete endpoint is
equality in `M_2(F3[Q8])`, including both zero off-diagonal blocks. No extra
role, free address permutation, erasure, clean allocation or nonlinear scalar
operation is part of this model. Scalar `GL2(F3)` operations alone are free.

The result is an exact finite minimum, not a failed search extrapolated to
other fields, role counts or endpoints. The binary endpoint was already
settled by Aaron Wang's [#2318](https://github.com/CrocSwap/integer-mult-bounds/pull/2318).
The new quantity is the minimum with ternary coefficients and all twelve
ternary projectors. Its value agrees with that cited binary value;
the binary census is not replayed here.

## Why the certificate proves a minimum

**Normalize free scalar mixing.** Augmentation sends every group basis
element to 1, so every charged factor and the target augment to `I_2`.
Moving all free scalar maps to the left conjugates each N by a scalar
invertible matrix and preserves its rank and idempotence. The remaining
scalar product must be `I_2` by augmentation. Thus every legal presentation
has a same-length charged-only presentation in the enumerated alphabet.
This is the predecessor normalization argument over the changed field.

**The alphabet is complete.** The primary checker enumerates all 81 ternary
two-by-two matrices, retaining exactly those with determinant zero, trace
one and `N^2=N`. These are precisely the rank-one idempotents. The separate
checker enumerates all outer products `uv^T` with `v^T u=1` and deduplicates
them. Both obtain twelve projectors, hence 24 charged factors. The primary
checker also verifies conjugation closure under all 48 scalar invertibles.

**Every candidate below six has even length.** Apply the group character
`i -> -1, j -> 1` and then the ordinary two-by-two determinant over F3.
For a rank-one projector,

```text
det(I_2 + (c-1)N) = c.
```

The target character has determinant -1. Consequently the number of i
calls is odd. The character `i -> 1, j -> -1` likewise forces an odd number
of j calls. Both characters send z to 1. Hence the total length is even;
it is enough to exclude lengths zero, two and four. Interleaved free scalar
maps have already been normalized away.

**The complete four-call meet is empty.** Starting at identity, enumerate
all products through two charged calls. Starting at the target, enumerate
all products through two inverse factors. Both breadth-first searches have
new-state layers `(1,24,466)`, total 491 states, from exactly 600 transitions
each. Their intersection is empty. Every word of length at most four splits
into two parts of lengths at most two and would produce an intersection.
Deduplicating equal full matrices loses no continuation because future
left multiplication depends only on the current matrix.

The reverse factors are `D_N(g^-1)` because
`D_N(g^-1)D_N(g)=I_2`. They undo charged calls in the meet;
they do not enlarge the paid operation alphabet.

**Six calls attain the endpoint.** Let `E_1=diag(1,0)` and `E_2=diag(0,1)`.
Three i calls on `E_1`, followed by three j calls on `E_2`, give

```text
D_E2(j)^3 D_E1(i)^3 = diag([i^3],[j^3]) = diag([zi],[zj]).
```

This identity holds in the full formal algebra. It acts correctly on every
dirty input, with no preparation or cleanup omitted. Together with parity
and the exhaustive meet, it gives minimum six.

## Reproduce and evidence

Use CPython 3.12 and the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-q8-negative-pair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-q8-negative-pair/regular.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-q8-negative-pair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-q8-negative-pair --check-source-history
```

Any CPython 3.12 installation can replace the displayed interpreter path.
`VERIFY.json` registers ordinary and optimized runs of both checkers. Each
command is read-only. The expected scientific markers are
`PASS_TERNARY_Q8_NEGATIVE_PAIR` and `PASS_TERNARY_Q8_REGULAR_ACTION`.

`verify.py` stores all 32 formal coefficients directly. `regular.py` imports
no producer code. It independently constructs the group using Hamilton
quaternions, the projectors using outer products, and all factors as dense
16-by-16 matrices in the faithful regular action over F3. The complete two
forward/reverse sets agree after recovering formal coefficients from the
identity-input columns. The regular action is faithful as an algebra action;
a smaller faithful group representation would not suffice for this check.
These are two arithmetic implementations in one contribution, not independent
human review.

Both checkers verify the six-call witness, reject each of its six single-call
omissions and find a planted four-call target with the same meet routine.
The primary checker additionally checks all 512 associativity triples, gate
inverses and determinant characters, rejects invalid projectors and labels,
and distinguishes dirty off-diagonal leakage and group sign from scalar minus.

The generated `RESULT.json` records full-set digests, counts, the witness and
SHA256 hashes of the other six package files. Default replay recomputes it
and rejects a mismatch, including Boolean aliases for integers and duplicate
JSON keys. Explicit `verify.py --emit` prints a fresh generated receipt for
comparison; it writes no files. Source manifests are historical provenance,
not executable dependencies. No predecessor verifier is imported or replayed.

The fixed-domain Python programs use managed allocation, a Power of Ten rule
3 deviation. Each formal state has 32 coefficients and each regular state
has 256 entries. Each search retains at most 601 states and at most 576
next-layer candidates; all loops have fixed bounds or iterate bounded package
data. Functions are under 60 physical lines, control flow is nonrecursive,
and failures use explicit exceptions that remain active under `-O`.
The compensating control is the fixed field, role count and search radius;
expanding any of them requires new capacity limits and a separate task.
Warnings-as-errors replay is the registered Python diagnostic check.

## Scope, overlap and credit

Base `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
The `bit-new-register-model` card is changed to a coefficient-field side
question. Its historical binary baseline is not the first working example
for this field; the six-call ternary coordinate word is the first fixture.
`TASK.json` records the changed premise and the stop at this first result.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144877).
Live PRs, active Discussions and recent handoffs, this account's recent
contributions, distinctive all-main README searches and merged-PR searches
were checked. The cached helper covered 331 open PRs and 4,359 Discussion
records, with incomplete sparse local-note coverage. Arbitrary diffs and
unpublished work remain outside coverage; no-match searches prove no novelty.

Credit Aaron Wang's #1822/#2318 for the Q8 pair model, binary precedents,
full-boundary convention and exact-search direction; eumemic #288 for the
scalar-idempotent register model; woklerx #1443 for the formal group-algebra
and normalization predecessor; Ali Romman #468, Gareth Davidson #1333 and
the retained register-model lineage. The twelve-projector enumeration and
ternary endpoint certificate here are new. No historical priority is claimed
for determinant characters or meet-in-the-middle enumeration.

Physical ternary address realization, scalar-map charges, source access,
restoration, frame/hosting, precision, tape, stock, recursive supplier
admission and the complete multiplication theorem remain outside scope.
Lean, Docker, predecessor scientific replays and the selected cold replay
are unrun. None of these unknown costs is treated as zero in a physical bill.

## Open next questions

1. Does the same six-call minimum hold with an arbitrary number of restored
   dirty ternary roles? Start with a role-uniform invariant or a three-role
   exact word. The two-role meet supplies no extra-role lower bound.
2. Can a written argument exclude four calls over every odd field? The
   determinant parity proof survives, but the projector inventory changes.
   Start with the forced label counts `(1,3)` and `(3,1)` and retain all eight
   formal group coefficients. No general-field exclusion is claimed here.
