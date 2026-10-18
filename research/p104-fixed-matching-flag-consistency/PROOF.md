# A relay obstruction for PR3019's fixed endpoint matching

This is a written finite-instance proof, supported by two exact local
implementations. It is not a formal-kernel proof or a new multiplication
exponent. All labels and indices below refer to the frozen ordered inputs and
PR3019's pairing at `44d12bdeb8ade4066645bd968bebd4756b06200a`.

## Contract and favorable relaxation

Let V = F2^9. The correction interface is the shear Y <- Y + C X,
where C = I-G/2; it preserves the target entrance component. Scalar mixing
is linear over Q (or a characteristic-zero extension), with a fixed,
data-independent frame program. Source X_s is immutable; targets Y_t are
unread. Helpers enter
with independent arbitrary dirty values. A helper's frame follows a nested
flag from ZERO to FULL, with one step at each dimension. Scalar operations
between registers require an equal current frame. The original data paths,
208 departure slots and prescribed arrival covers are fixed. No extra
helpers, reads of the original channel's helpers, descending frame transports
or target feedback are allowed.

For helper a assigned to arrival b, write A_a for its dimension-two departure
plane and B_b for its dimension-seven arrival frame. At dimensions three
through six, its actual frame F must obey A_a <= F <= B_b. The endpoint frames
at dimensions one, two, seven and eight are prescribed. Two helpers with
intervals [A,B] and [C,D] can meet at dimension d only if

    A <= D, C <= B, dim(A+C) <= d <= dim(B intersect D).

This condition is sufficient for one isolated common frame, by extending
A+C inside B intersect D. It does not make several such contacts mutually
consistent in one helper's flag.

We grant every source snapshot on its complete frozen data path, arbitrary
interleaving, free scalar mixing, and no restoration or physical charge.
All helpers still move only upward in dimension. Helpers other than 91 may
choose each contact independently at each layer; their actual subspace
coherence is relaxed, not the direction of dimension travel.
Helper 91 alone must have one nested flag. ZERO gives no source read; at
FULL, dimension nine, no target Y40 frame is available, so only dimensions
one through eight can contribute to this correction. These permissions include every
legal program in the stated contract, so failure in this relaxation rejects
that exact matching under the contract.

## Exact small contact boundary

The independently reconstructed incidence table is complete, not a sample.
Self contacts are omitted.

| Helper | Possible other helper contacts, by dimension |
| --- | --- |
| 17 | 16 at 1; 83 at 8 |
| 83 | 82 at 1; 91 at 4, 5, 6; 17 at 8 |
| 91 | 90 at 1; 83 at 4, 5, 6; 139 at 4, 5; 183 at 8 |

Each of these three helpers can read only its own source at dimension one:
X8, X41 and X45, respectively. At dimension one each of their paired
helpers 16,82,90 has the same unique source line and no different source can
enter that component. Y40 has no direct equal-frame source read,
and only helpers 17 and 83 can write it, at dimension eight. In particular,
the late contact 183--91 at dimension eight cannot feed the earlier contacts
91--83 at dimensions at most six. The programs may wait in real time, but a
helper cannot return to a smaller frame dimension.

New source information from outside {X8,X41,X45} could therefore enter the
correction increment at Y40
only by the ordered relay

    helper 139 -> helper 91 -> helper 83.

At the first contact, helper 91's frame contains A139. At any later contact
with helper 83, its frame lies inside B80, because helper 83 is assigned to
arrival slot 80. Nestedness would imply A139 <= B80. The exact separating
vector is

    113 in A139,    113 not in B80.

Consequently that ordered relay is impossible. An attempted contact with 83
before acquisition from 139 does not carry the new source information. Equal
dimension contacts would need the same frame and give the same contradiction.
Repeated contacts, copying and linear cancellations cannot create an outside
source coefficient without a first such legal information path.

Thus the added correction increment at Y40 has X support contained in
{8,41,45} for every legal nested choice
of helper 91, independently of all choices of the other helpers. Their dirty
inputs do not initially contain an X coefficient and cannot supply X1 on
arbitrary independent inputs.

## Correction contradiction and coverage

Retain the predecessor contract that the original channel contributes G/2
to the target; this package does not replay that channel identity. The
correction increment must contribute C = I - G/2, determined by the ordered
E8 roots in the frozen fixture. The total target value can contain source
coefficients that the new correction increment cannot acquire; unread Y
prevents using that existing response as a correction source. The exact
row C[40,:] has 48 nonzero entries, including all three indices 8,41,45. Its
45 other required coefficients cannot be delivered by this matching. In
particular,

    required C[40,1] = 1/2,    realizable added correction coefficient = 0.

This rejects every full flag assignment for this matching, not merely the
published intermediate bases. It does not reject another endpoint pairing,
changed cover planes, additional lifetimes, original-helper reads, descending
transport, target feedback or a different correction architecture. It does
not prove a new minimum number of lifetimes.

The primary finite checker supplies an independent form of corroboration.
Since B8/A91 has dimension five, its complete flags number

    (2^5-1)(2^4-1)(2^3-1)(2^2-1)(2^1-1) = 9,765.

The checker enumerates all of them exactly. Keeping the other 207 helpers
relaxed, 477 choices miss 45 required pairs and 9,288 miss 46; none pass.
Removing the single-helper consistency requirement restores the predecessor's
4,992 reachable required dependencies. This is a finite exhaustive computation.
The contact-boundary argument above explains why no unenumerated program
within the stated model can evade the obstruction. Neither is a complete
supplier admission, an all-parameter multiplication theorem or a formal proof.

## Recursive-cost consequence

The tested mechanism uses 208 unit-step flags, hence 1,872 rank-one helper
transports. Under PR2920's inherited favorable transport/ideal-idle screen,
the original channel plus these flags has profile H1=2946, H2=58, H3=86,
H4=104, H5=48, H6=24, H7=8, H8=8, ideal H51=824/17, m=73 and W=832/9.
Its reported selected-saving moment is about 0.99889624. This package does
not recertify that screen. Native ADDs, chronology, owners, routing,
restoration, precision, tape and consumer costs remain additional and unknown.

The obstruction says this exact proposed matching cannot realize that
favorable budget by choosing intermediate flags within the stated contract.
It supplies no positive recursive-cost improvement or new kappa. The correct
next step is to change a named boundary or pairing before paying for scalar
or native synthesis, not to treat the relaxed support certificate as an
executable correction.

## Attribution

Nick Petalas supplied PR3019's matching and the PR3013/2996/2981/2920 endpoint
and optimistic-contact lineage. Arham Tahir's PR2997 supplies the complementary
fixed-full-flag audit. Retain Sudarsh Chaturvedi/PR2924, Sagar Thakrar, Hiroki
Kumazaki/PR2889/2353, ywz65/PR2614, Arham Tahir/PR2675/2682, Philippe Van
Velzen, Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940/2090,
Jeremy Diviney/PR2113, Josie Elliston/PR1071 and Ali Romman/PR1125, with their
retained geometry/native/compiler sources. New analysis: Ross Richardson with
substantial OpenAI Codex assistance and two internal mathematical specialist
implementations. Apache-2.0; no independent human review is claimed.
