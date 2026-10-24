# Independent growing-carrier decoder audit

The frozen word is correct as a finite canonical-frame decoder. It
uses three persistent carriers, eight targets, twelve scalar reads,
and no copies. Its rank mass is 55. It is not a complete source
factory, controller, supplier, or integer multiplication witness.

The input word hash is
15d7b2143c360357a1f372926b1ff77378b48099118fa8b506d752daf7f33da5.
The source is the p518 paired-five experiment. The frame definitions
come from the pinned exact Clifford source with SHA-256
2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962.
The checker does not import the builder or call lower_child.

## Exact scope and output

The ADDRESS space has six binary coordinates. The carrier ports are
e0, e2, and e4, encoded as 1, 4, and 16. Target t has port

    q(t) = sum_i e_(2i + bit_i(t)),       0 <= t < 8.

The three carrier labels start at their port lines. Each target starts
at frame zero. All full labels have the canonical tag T. For a frame F,
its operator is the saved canonical_frame(6,F), denoted T_F.

Each ADD has both operands at exactly the same full tag and frame.
Each child starts at its stated source label and implements
T_new T_old^-1. Thus the complete word has the common-frame invariant
h_r = T_label(r) x_r. Its scalar replay is

    X_i(final) = X_i(initial)
    Y_t(final) = Y_t(initial) + sum_i bit_i(t) X_i(initial).

This holds for arbitrary values in all eleven input streams. It does
not assume zero carriers or zero targets. The physical output is

    h_i(final) = T_FULL T_(ei)^-1 h_i(initial)
    h_(3+t)(final) = T_(q(t)-perp)
        (h_(3+t)(initial) + sum_i bit_i(t) T_(ei)^-1 h_i(initial)).

The phrase "carrier values stay unchanged" refers to the scalar
coordinates X_i. Their physical frames change during the word.

## Independent finite checks

The checker rebuilds the scalar rows and full label run from the
literal events. It checks every pending target before each carrier
growth, every target hyperplane condition, and all final labels.

It parses the serialized affine Gaussian monomials in each recipe.
Their binary matrices are invertible, their quadratic matrices are
symmetric, their phase fields are valid, and their diagonal parity
conditions hold. The executed order is right, rank-r Fourier child,
then left. Thus the recipe matrix is L F_r R.

An integer Gaussian interpreter is separate from the producer's
interpreter. It compares each of the 23 recipes on all 64 basis
columns, including global phase: 1472 exact column checks. It then
replays the complete physical word on all 11 * 64 = 704 basis columns
and checks the displayed output formula. Its literal inverse restores
every one of those columns. A phase-plus-one mutant is rejected.

These recipes and events are complex-linear. Equality on these basis
columns therefore gives equality on every complex input vector. The
canonical frame definitions are shared with the producer; the builder,
lowering procedure, and numerical state interpreter are not.

## Cost and monotonicity

There are 39 literal events: 12 ADDs and 27 paid child calls. There are
23 distinct child recipes. Those two child counts must not be confused.
The paid profile is

    rank 1: 15
    rank 2:  2
    rank 3:  5
    rank 4:  4
    rank 5:  1.

Its mass is 15 + 4 + 15 + 16 + 5 = 55. Every frame move is a strict
nested ascent. There is no nonmonotone transport charge in this word.
The cost telescopes correctly for each register. Each carrier goes
from rank one to rank six and pays five. Each target goes from rank
zero to rank five and pays five. This also gives 3 * 5 + 8 * 5 = 55.

This count starts with the stated three carrier lines already present.
It does not pay for producing those scalar carriers, reaching their
initial labels, scalar and monomial primitives, routing, precision,
storage, owner charts, or exceptional work. A complete construction
must pay those costs.

## Why the fixed-cap terminal argument does not apply

Carrier 0 reads target 3, whose port is 26, at frame span{1}. It later
grows to span{1,16} before its remaining reads. But 16 dot 26 is one,
so that later frame is not contained in target 3's endpoint hyperplane.
The earlier target is no longer pending. No future compatibility rule
is violated.

Therefore a single final read cap cannot describe all reads of this
carrier. The fixed-cap terminal proof charges one terminal by the
capacity of one fixed cap. It cannot use that charge when one role
reads at several growing caps.

The three-selector analogue of the old per-read charge is 2^d/8 at a
read cap of normal rank d. The actual summed carrier charges here are
3/2, 2, and 2. They are greater than the old one-unit budget for a
fixed terminal. This is a direct illustration of the changed premise,
not a new lower bound for all decoders.

The word also uses caps smaller than the maximal common cap of its
served group. A four-target selector halfspace has maximal common cap
dimension three in this six-coordinate cube, while its initial reads
use a rank-one cap. Thus the later weaker argument about growing
maximal caps and cross-cube exclusion does not automatically cover
this word. No claim about all 141 channels follows from this example.

## Endpoint adapters needed for a complete word

For the three unit carrier ports, T_(ei) equals C_ei exactly. For all
eight target ports, however,

    T_(q-perp) != F C_q^-1.

The signed tableaux differ, and the exact basis-column values also
differ. The raw canonical-frame word must not be called the legacy
data endpoint formula. The correction

    E_q = (F C_q^-1) T_(q-perp)^-1

has B-rank zero for each of the eight targets. It is a monomial
operator. An exit can therefore preserve the child-rank mass, but
its actual monomial operations must be emitted and charged.

Use a distinct full post label with operator F C_q^-1. Emit the exit
as a relabel from the canonical q-perp label to that post label.
Check its complete serialized monomial, including phase. No later ADD
may use that target under its old canonical tag. These exits are not
in the frozen 39-event word.

## Conditions for both parities and all H channels

1. Produce the actual scalar channel rows. Check every main input
   column, including arbitrary dirty helper columns. If a helper is
   zero on entry, state and pay for that condition. The local decoder
   accepts prepared carrier values; it does not produce them.
2. Give every carrier its actual starting frame and operator. A
   schedule over abstract selector normals is not by itself an
   ADDRESS embedding. Check even-weight normals and both parities in
   the actual frame geometry and canonical operator family.
3. Use the actual target frames at the decoder cut. They need not be
   zero in the full word. Every ADD must have a common full label.
4. Before each carrier growth, check compatibility with every still
   pending target in the full schedule. Include targets in other
   cubes. Removing served targets permits growth; it does not permit
   incompatible future reads.
5. State each required signed channel coefficient. Check that each
   delivery occurs exactly once with that coefficient. Both parity
   halves must give the required complete scalar matrix.
6. Compile every actual transition, including its global phase, and
   count every emitted call and primitive. Use endpoint telescoping
   only on nested monotone paths. Charge general frame transport by
   its actual recipe.
7. Emit the data and helper endpoint adapters with explicit tags.
   Check the complete endpoint, restoration or retained helper block,
   and all cross blocks. Do not infer a permitted helper clear from
   the local decoder.
8. Build the full controller and owner schedule. Count persistent
   carriers, changing invocation lifetimes, residual widths,
   spectators, bank calls, and initialization. Only the resulting
   paid full profile can be compared with the live frontier.

The three-carrier mechanism survives independent exact replay. The
extension obligations above remain separate from this finite result.
