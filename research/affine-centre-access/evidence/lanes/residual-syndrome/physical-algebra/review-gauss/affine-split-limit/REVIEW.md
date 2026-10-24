# Independent review of the affine splitting limit

Result: accept `SPLIT-LIMIT.md`, SHA256
`6e79f870420b99c59c10c0e91160e3dbf548d8e821bb2dc94b4f39cfb2713f8b`,
within its literal Haar-tree class. No material correction is needed.

## Affine branches and exact record count

Express each branch's spectral set in the original address coordinates.
The tests on a path can be pulled back through all preceding affine
charts on that path. Each is an affine functional, even when a different
branch uses a different chart. A nonconstant test cuts the current
affine set in half and lowers its dimension by one. Thus a leaf at
depth `d` has dimension `m-d` and has `2^(m-d)` coefficient records per
unchanged external index. No common bit order or basis is needed.

In the stated code, a split processes all records of its current
branch and retains both halves. Each original spectral address belongs
to exactly one descendant at every later split on its path. Count
these address-and-split pairs first by split and then by terminal leaf.
This gives

    T=sum_(internal v)|A_v|=sum_(leaves l)|A_l|d_l.

The leaf sum must include rejected and parked detail branches. They
hold independent coordinates of arbitrary input data. The invertible
Haar code permits them to remain parked; it does not permit their
earlier processing or their stored values to be omitted.

A block made from literal splits has the same identity relative to
its input node. Its terminal parts can have different relative depths.
Replacing those depths by one block step is a different cost model.
For example, three active-only splits of a 16-record branch have
terminal sizes 8,4,2,2 and depths 1,2,3,3. Their work is 28 records.
A full three-level tree processes 48 records. Neither example is a
single 16-record scan under this grammar.

The proof does not turn that charge into a lower bound for a direct
block algorithm, a fused algorithm outside the literal split format,
or a recursive native child. Such an implementation must receive its
own analysis. The source note states this restriction.

## Accepted rank and fixed-width work

The accepted leaves are disjoint affine subsets of the target set.
If each such subset has dimension at most `m-k`, each accepted leaf
has depth at least `k`. Dropping the nonnegative rejected-leaf terms
therefore gives

    T>=k sum_(accepted l)|A_l|=k|S|.

The statement also applies to any fixed partition realized by such a
tree. It does not give a cheap realization of an arbitrary partition.

For fixed-format records, each literal split reads or writes a full
record of charged width `w`. Its bit work is at least a fixed positive
multiple of `w` per processed record. The result is
`Omega(k delta V)`, where `V=Nw`. If `w` is only a common lower bound,
`V` here means the corresponding lower-bound volume. This is not an
adaptive-format or general bit-complexity lower bound. Row, compact,
spectator, and polynomial fields are unchanged external indices in
the stated class; they multiply both volumes by the same factor.

Address maps, reverse codes, and the target update can add work. They
cannot subtract from this forward split charge. A change that mixes
protected external indices, uses non-affine branches, or allows
overlapping outputs to cancel is outside the stated argument.

## Application and source binding

The inherited affine bound gives
`k=n ceil(lambda/2)-(lambda mod 2)` for the sufficient all-odd sector,
with fixed `n>=2`. The independently reviewed density theorem gives a
positive limit `2^-((n-1)(n+2)/2)`. Hence `k` grows linearly in `lambda`
while the density stays bounded below by a positive constant. This
proves `Omega(lambda V)` for this projector implementation class.
It also excludes an all-size `O(V(n lambda)^tau)` charge for fixed
`tau<1` in that class.

The density result is an inherited dependency, not a new density
proof. I read its exact spectrum formula in the pinned `QUOTIENT.md`
and its independent receipt. The formula's nonnegative rank terms
decrease to the limit. The new checker verifies the stored width-152
and preceding-width fractions by integer cross multiplication. The
limit exponent at `n=73` is exactly -2700. This constant is small;
the asymptotic obstruction is not a strong finite-budget estimate.

For a fixed residue, the sharp dimension bound gives
`k_d=n(lambda-kappa_lambda(d))`, so the same count gives
`T>=k_d|S_(n,d)|`. Empty small-width residues contribute zero. This
step does not assume all accepted leaves have the same size.

## Independent checks and scope

The checker does not import or run the producer. It builds three small
trees whose linear tests genuinely differ by branch. Each test is
extended to a full invertible binary chart. It checks all node ranks,
both retained halves, every grouped-subtree identity, and every
original address's visit count. It also verifies all terminal labels
by direct odd-phase calculation. The three trees process 860 records.
Omitting rejected detail terms fails the exact count in each case.

These checks supplement the general double-counting proof. They do not
replay a new native word or prove a lower bound for all linear circuits.
The result does not exclude computing the actual centre query without
a complete sector projector. It does not exclude productive native
children billed by their own recurrences, non-affine leaf methods,
or interference between overlapping encodings.

No producer or earlier review file was changed. No PR, commit, or push
was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
