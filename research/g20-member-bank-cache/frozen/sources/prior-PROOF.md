# A free choice of carrier does not expose another G20 split

## Contract and new claim

Fix Ali Romman's PR5708 word, `WORD.json.gz`, at
`829d01fc031f7323ffcfa423fdfd1f24dcbe3190`. Its scalar normalized
coordinates, native frame induction and existing helper endpoints are cited
premises. This proof does not establish those source results again.

A helper group G consists of all retained public helper roles with the same
entrance subspace U and exit subspace V. Fix an event cut and one entire bank
S of fields having the same physical frame F, where V is strictly contained
in F and F is strictly contained in U. Include every field in S, including
main fields and existing owned fields. No member of G need occur in S.
Binary changes of basis at the input, cut and output may use every eligible
coordinate. A split must preserve independence and restore every output
outside G. Adding paid frame changes, changing the scalar word, mixing
boundary groups with different endpoint frames and using address-dependent
coefficients are outside this contract.

The new finite claim is that all 1,981 distinct eligible contexts with
`S intersect G` empty have zero boundary pairing. There are 46 such contexts
with two nonzero kernel spaces; 45 even have nonzero internal pairing.
Thus the failure is not merely the absence of a scalar pivot or the absence
of available kernel vectors. No free choice of an existing physical carrier
repairs the boundary pairing on this word.

The executable also obtains zero boundary pairing in all 7,870 contexts,
including the helper-pivot domain reported in PR5708. Those old cases are
context for the expansion, not a separate contribution or supplier audit.

## The necessary boundary pairing

Use column states. Let A be the complete normalized prefix map from all
entrance fields to the cut, and let B be the suffix map from that cut to all
exit fields. The maps include the scalar effects of owned erasures. Queries
change physical frames and leave normalized coefficients unchanged under
the cited native contract.

For a row a supported on S, eligibility means c = a A has no coordinates
outside G. For a column b supported on S, eligibility means d = B b has no
coordinates outside G. The full spaces of such a and b are kernels of the
restrictions of A and B to the complementary boundary coordinates.

An independent one-coordinate split requires

    a b = 1 and c d = 1.

The internal equation permits extraction and substitution in a cut basis.
The boundary equation is necessary even if the cut carrier and the boundary
helper pivot are different physical roles. To see this, write h for the
original helper inputs and z for the new independent successor input.
Extracting c h and substituting z along b changes the final helper vector to

    h + d (z - c h).

This uses the cited identity normalized endpoint on the helper group. The
new combined output is

    (c h, (I - d c) h + d z).

If c d = 0, the nonzero input pair (h,z) = (d,1) maps to zero. If d = 0,
then the successor input is itself lost. Either case contradicts independent
output jobs. Invertible boundary bases cannot repair this rank loss.
The equation c d = 1 follows for an independent split over F2.
For several simultaneously split coordinates the same argument requires an
invertible boundary pairing matrix; a zero matrix excludes every positive
number of channels.

The zero-pairing conclusion is unchanged by extending scalars to any field
of characteristic two. The kernel spaces extend by scalar extension, and
the zero bilinear matrix remains zero. Over an extension field the required
one-channel pairing is nonzero and can be normalized to one; it is still
excluded here.

## What the executable enumerates

There are 685 fields, 14,794 events and 14,795 event cuts, including both
boundaries. Exact rational reduced row spaces identify 645 physical frame
classes. The retained helper endpoint groups have sizes 413, 1 and 1.
For each group, the checker lists every source frame strictly between its
two endpoints. It does not impose a bank-size or kernel-support cutoff.

The backward sweep computes the suffix columns. For `ADD d,s`, it applies
`B[:,s] ^= B[:,d]`. For an erasure of d it stores B's old d column, then
sets that column to zero. In the forward sweep it removes one event from the
suffix: ADD is its own inverse, and an erasure restores the stored column.
Prefix rows advance by `A[d,:] ^= A[s,:]` or by setting an erased row to
zero. Frame transitions update the bank partition. At the final boundary
the suffix must be the identity and every frame must equal its declared exit.

An ADD changes only its one common-frame bank. An erasure, initialization or
query changes only the old and new banks of its destination. Every initial
bank and every changed bank is checked. Other banks retain their exact prefix
rows, suffix columns and membership. Exact keys consisting of group, frame,
slots, prefix rows and suffix columns remove repeated contexts. They do not
merge distinct linear-algebra problems.

For each context the checker computes bases L and R of the two eligible
kernel spaces. It verifies their defining equations and independence.
Opposite-pivot rank elimination separately checks completeness through
`dim kernel = |S| - rank(restriction)`. It then forms every entry

    C_ij = (L_i A) (B R_j).

Every C is zero. This certifies the entire eligible spaces by bilinearity,
rather than a bounded-support search for a and b. The result excludes a
necessary equation; there is no delivery cost to optimistically set to zero.

The output records every count and a deterministic digest of the context
summaries. The source hashes are checked before parsing. The generated
execution receipt separately binds the exact package bytes.

## Controls and scope

The checker compares the complete dependency space against literal exhaustive
enumeration for all 512 triples of three-bit rows. A two-role borrowed-carrier
example has a real channel in a bank containing no helper role and must be
accepted. Orthogonal-image, unit-channel and foreign-coordinate controls
separate the boundary and eligibility conditions. All checks use explicit
exceptions and remain enabled under optimized Python.

This is a finite exact certificate plus a scoped algebraic obstruction.
It supplies neither a global BIT lower bound nor a complete multiplication
theorem. It adds no native word, target, paid saving or kappa. Source native,
compiler, precision, ownership, tape, outer-assembly and the five framework
assumptions remain outside this proof. Independent human and formal
proof-kernel review are unclaimed.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman for the
PR5679 independent-split construction and its different-physical-role open
question, PR5708's exact final word and helper-pivot census, and PR5609's
prefix/suffix cut method on the older word. The source construction retains
Dugongue, ai-nanachi and the compact436, native, controller, helper, ordinary
and stock lineage cited in those packages. Gaussian elimination, rank-nullity
and bilinear base change are classical. No predecessor executable is imported
and no predecessor credit line is changed. New material is Apache-2.0.
