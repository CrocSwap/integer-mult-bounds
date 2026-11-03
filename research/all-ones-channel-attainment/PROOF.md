# An attaining cut for every all-ones size

This contribution was produced by Nick Petalas. Apache-2.0.

The result is a scoped written mathematical proof with exact finite
corroboration. Independent human and formal proof-kernel review are unclaimed.

## Contract and cited premises

Use Philippe Van Velzen's PR2177 model and notation in
`research/leaf-destination-transport-bound/PROOF.md` and `PROOF3.md`.
A call on a consecutive factor interval splits into the floor half U,
from its source to its depth scratch, and the ceil half V, from that
scratch to its target. The positive word is U V U' V'; the negative word
is V U V' U'. Primes mean the literal inverse calls. Scratch at equal
depth is shared after completed child calls. All entrance registers are
arbitrary and independent. A leaf is an exact signed shear using one
free noncommuting factor. An error is injected at one completed leaf's
destination, and a channel is the free-algebra coefficient of that error
at a later cut. Its mass is the sum of absolute coefficients.

We use PR2177's complete-call identity F2, exit-column Lemma L1,
y-keeping-chain exit formula Lemma E, positive readout Lemma P, and
inverse Lemma I and Corollary I. We cite PR5938's all-ones upper bound:
at size n=2^g-1, g>=3, at every cut and register in either orientation
there are at most 4g-3 channels of mass H=g-1, and no channel has larger
mass. None of those predecessor claims is re-proved or audited here.

Write [u,v] for f_v f_(v-1) ... f_u, and [u,u-1]=1. Scratch levels are
numbered from one at the root. In the executable, source and target are
registers 0 and 1, so scratch level l is register l+1.

## The new theorem

For every integer g>=3, put H=g-1 and n=2^g-1. In the positive root call,
follow the phase path

    V', V', U, V, ..., V

with exactly H-2 final V steps. Read scratch level three immediately
after that leaf. At this cut there are exactly 4g-3 channels of mass H.
The proof gives 4g-3 distinct injecting leaves explicitly.

Consequently the maximum number of mass-H channels is exactly 4g-3,
and PR2177's distinct-error mass functional satisfies

    E_k(2^g-1) = k(g-1),  1 <= k <= 4g-3.

This is an exact free-algebra channel-mass statement. It does not assert
that one fixed assignment of contraction operators and numerical errors
simultaneously attains every separate polynomial norm bound.

## A family of exits with distinct monomials

Let Y(k,s) be the leaf reached by following the y-keeping U phase at
every level of a size-k call of sign s. This is U' for positive sign
and U for negative sign. PR2177 Lemma E says its exit contains the
destination and floor(log2 k) scratch entries. Each entry is a signed
monomial, and their factor lengths are distinct.

For a call of size 2^h-1 and sign s, define a family A(h,s) of leaves.
For h=1 use its only leaf. For h>=2 take:

1. The family A(h-1,-s) inside the y-keeping U child.
2. Y(2^(h-1),+) inside V.
3. Y(2^(h-1),-) inside V'.

There are (2h-3)+2=2h-1 distinct leaves. Every selected exit has exactly
h nonzero entries, includes the call's destination, and has different
monomials at its different nonzero registers.

Here is an induction proving that last assertion, beyond the cited
single-chain formula. For a selected V or V' leaf, the child is a
power-of-two call, so Lemma E gives h entries and distinct lengths.
The other complete parent phases either read zero error in the parent
source or add to the parent target from zero error in the child's source.
Thus the child exit is unchanged. For a selected y-keeping U leaf, the
inductive exit has h-1 entries and a nonzero child destination entry.
The later V' adds its negative product times that entry to the parent
target. This new entry contains a factor from the parent's upper half;
all child entries contain only lower-half factors. It is nonzero and
different from every child monomial. Other entries stay unchanged by F2.
The extra U' in a negative call reads zero source error. This proves the
induction. All coefficients are +1 or -1 by this argument and L1.

## The readout row

Set b=2^H-1, a=2^H, q=2^(H-1), r=2^(H-2). The root phases U and U'
have size b, while V and V' have size a. Name the first three root
scratch registers z0,z1,z2. Thus z2 is the readout register.

Inside the root V', write its children as U1,V1,U1',V1', in their
positive-call names. Since V' is negative, their order is
V1,U1,V1',U1'. Both children have size q. Inside V1', its U child U2
is positive, has size r and maps z1 to z2. Our cut is U2's Lemma P cut.
Let e=b+q+r-1. The row taking the entrance of root V' to z2 at that cut is

    z0  -> [b,e]
    z1  -> [b+q,e]
    z2  -> 1
    scratch level 3+l -> [e-r/2^l+1,e],  1 <= l <= H-2.

Every other entry is zero. In particular the row ignores the root target
and is nonzero on every scratch level 1,...,H+1. Every coefficient uses
only upper-half letters f_b,...,f_(n-1).

To obtain the row, the completed first V1 phase changes only the root
target. The completed U1 phase adds [b,b+q-1] z0 to z1. In V1', the
first V child again changes only the root target. Lemma P applied to
U2 supplies its source product, identity target entry and successive
suffix products. Composing with U1 gives the displayed z0 entry.
This also covers H=2, when U2 is a leaf and the final list is empty.

## The 4g-6 lower-half channels

Select A(H,+) in root U and A(H,-) in root U'. There are 2H-1 leaves
in each group. Every selected exit has H nonzero signed monomials on
root scratch levels 1,...,H+1. Between either exit and root V', completed
phases can affect only the root target, because the error in the root
source is zero. The displayed readout ignores that target.

Each of the H exit entries is multiplied by a nonzero monomial using
only upper-half letters. Its right part consists only of lower-half
letters and differs from every other exit right part. Unique word
factorization at the disjoint alphabets makes the H resulting words
different. No cancellation is possible. Each selected channel has mass H.
Together the groups supply 2(2H-1)=4g-6 channels.

## Three upper-half channels at the same cut

We specify three more leaves:

- Y(q,+) in U1 of root V.
- Y(q,-) in U1' of root V.
- Y(q,+) in U1 of root V'.

The third leaf has an exit on z1 and the deeper scratch levels, with
H distinct monomials by Lemma E. The later readout inside V1' is
Lemma P's row for U2. It is nonzero on all those H positions and uses
only factors in V1, whereas the exit entries use only factors in U1.
The same disjoint-alphabet argument gives mass H.

For the first leaf, mirror the final cut backward through the inverse
pair V,V'. Let L be the leaf count of a size-r call and p be the number
of leaves through U2's Lemma P cut. A size-q call has 4L leaves, and a
size-a call has 16L leaves. Our cut in root V' follows 9L+p leaves.
The mirrored cut in root V follows 7L-p leaves: it lies in V1's third
phase U2', after L-p leaves of that inverse phase.

The completed U2 followed by L-p leaves of U2' equals the first p
leaves of U2, by literal inversion. The intervening complete V2 phase
changes only the root target and is ignored by row z2. Thus at the
mirrored cut, the readout on the exit of the first leaf is again
Lemma P's U2 row. Its H terms do not cancel, just as for the third leaf.
Corollary I transfers the same channel to our final cut, so its mass is H.

The second leaf is the inverse partner of the third leaf. Indeed,
reversing the y-keeping path in U1 gives the y-keeping path in U1'.
Corollary I identifies their channels at the final cut. The intervening
root U' acts trivially on these columns because it reads the zero root
source error. Hence the second channel also has mass H.

These three leaves lie outside the two lower-half groups and are
pairwise distinct. This proves at least (4g-6)+3=4g-3 channels.
The cited PR5938 upper bound makes the count exact. Choosing any k of
these distinct channels proves the stated E_k equality by its definition.

## Explicit cut position

Let T(k) be the number of leaves in a balanced call. F2's four phases
give T(1)=1 and T(k)=2T(floor(k/2))+2T(ceil(k/2)). Thus

    T(2^j)=4^j,
    T(2^g-1)=4^g-3*2^(g-1).

The Lemma P cut of a size-r power-of-two call follows (T(r)+2)/3 leaves.
Counting the phases before our cut gives

    t_g = 2T(b)+T(a)+2T(q)+T(r)+(T(r)+2)/3
        = (43*4^(g-2)+2)/3 - 3*2^(g-1).

Here t_g counts completed leaves, starting at one. The construction
specifies a cut without inspecting any data or running a search.

## Limits

The theorem concerns the balanced floor-half word and independent error
symbols at distinct completed-leaf destinations. It leaves lower channel
mass levels, E_infinity, a production rounding rule, internal leaf errors,
physical storage/access, native realization and all five selected framework
assumptions unresolved. It supplies no precision invoice or new kappa.
Finite execution corroborates this proof; it does not replace induction.
