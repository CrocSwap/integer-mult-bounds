# Finite nine-stage precision obligation

We audit the unchanged PR589 tuned 111-port, 439-helper word, under the
scalar convention consumed by the PR463/510 global template. Forward
ADD has coefficient +1. The inverse reverses the local event order and
negates ADD coefficients, while interchanging fresh COPY and literal
ERASE. Absolute coefficient propagation replaces every ADD coefficient
by +1 in either orientation. MOVE has no scalar effect in this model.
This is a statement about this finite unbanked scalar stream, not its
physical projector realization or complete rounding-error analysis.

There are eight banks of 111 data inputs, and nine disjoint groups of
439 arbitrary helper inputs: 4,839 independent inputs in total. A single
private copied-center slot starts and ends at zero. Normalize the
absolute value of every ordinary input by a common upper bound M. The
positive replay starts every ordinary input at one and the private slot
at zero. Every scalar prefix is then bounded by M times the corresponding
positive replay value, by induction on ADD, COPY and ERASE. No correlation
or helper cancellation is used. Its maximum is the exact maximum of
this *positive majorant program*, not a claim that all signed coefficients
can attain that majorant simultaneously.

## Source and schedule binding

The word is expanded independently from its D, A, retained-total scatter,
B and C fields. The result is compared event for event with the pinned
source exporter after deleting MOVE records. All 24,305 local ADDs and
9 COPY/ERASE pairs must match. Reverse events are checked for private-slot
freshness, immutable original centers and exact erase bindings in the
three-variable model below. The isolated source exporter runs without
optimization even when this verifier is run with `-O`.

The local-stage pair sequence is `(0,0,0,1,1,2,2,3,3)`, with odd-numbered
stages reversed. The two scalar shears associated with each bridge act
on distinct destination banks. The independent schedule is compared
with the actual `recipe(4)` function extracted from pinned `global_k.py`.
The adapter's edit inventory is inspected to ensure it does not replace
the recipe or prefix expression. The pinned prefix expression itself is
evaluated, rather than inferring its value only from a receipt.

In total the schedule contains 9(24,305+18)+18(111)=220,905 scalar
ADD/COPY/ERASE events, followed by a norm-preserving exchange. Boolean
replay verifies all 4,839 independent input columns return to identity,
including all 3,951 independent helper columns. The copied slot closes
to zero. Omitting each of the eighteen bridge shears separately breaks
that identity. Boolean restoration is additional interface evidence;
it does not replace the integer positive-prefix computation.

## Three-coefficient local model

For each orientation, initialize each source-bank row as (1,0,0), each
target-bank row as (0,1,0), every helper row as (0,0,1), and the private
slot as (0,0,0). Apply the same positive operations to these triples.
All coefficients are nonnegative integers. At every prefix, a row
`(a,b,c)` is therefore the exact value of the positive local program
when the two banks are uniformly X,Y and all fresh helpers uniformly H:

`a X + b Y + c H`.

For arbitrary nonuniform inputs bounded by X,Y,H in these respective
groups, the same expression is an upper bound by monotonicity. Preserve
every distinct row triple that occurs at a prefix; the local peak bound
is the maximum of those linear expressions. Preserve every endpoint
triple in each data bank; its next bound is the maximum of its endpoint
expressions. A reversed stage swaps the roles of the two physical data
banks, exactly as the source schedule does.

Initialize the eight bank bounds at one. Each local stage uses its
current pair of bank bounds and H=1 because its helper group is disjoint
from all previous stages. Update only the two active bank bounds and
accumulate the running maximum of all stage-prefix bounds, including
helper rows. A bridge `d += +/-s` updates its bound by `B_d += B_s`.
An exchange swaps bank bounds. Each update preserves a valid bound on
every data register; completed helpers are untouched and their peaks
are retained in the running maximum. This proves the envelope for the
complete schedule, with no enumeration of possible input magnitudes.

The checker also propagates every physical scalar register separately,
using separate integer state from the triple model. At every local event
its value is checked against the corresponding evaluated triple, the
stage envelope and the source coarse bound. During a bridge the
destination values increase monotonically; their checked endpoint
bounds therefore cover all intermediate port updates as well. The
exchange cannot increase any value. This is complete prefix coverage
for the finite scalar stream defined above.

## Exact bounds and limits

Local unit-input maxima are F=49,347 forward and B=1,113,070 reverse.
The original uniform product treats each of the eighteen bridge shears
as at most doubling the current global bound and every local stage as
multiplying it by F or B. Therefore it gives

`C = 2^18 F^5 B^4 = 117742596540718658156527847560864213734191286190080000`.

This safe coarse bound has bit length 177. The new bank envelope is

`E = 4758582824306830850667441862686468262449`, of bit length 132.

The complete positive program reaches

`P = 157414168625211913030896415270398859713`, of bit length 127.

Thus `2^126 <= P < 2^127`, `P <= E < C`, and the positive maximum is
attained at zero-based stage 8, local scalar-event index 24,257, global
helper register 4,469. These are exact integer results. P is sharp for
the specified positive program; no optimality of E among other summary
methods is asserted. The source's 192-bit production charge is unchanged.
In particular, `P < 2^127` is **not** by itself a 128-bit production
admission: physical owner hosting, cover routing, residual isometries,
MOVE interpretation, outer error propagation and complete compiler
interfaces are outside this experiment. The global template and
selected supplier retain their existing obligations and charges.

## Adversarial controls

Twenty-three controls reject using the Boolean identity endpoint as a
unit precision bound, using the largest local bound for the full
schedule, dropping all arbitrary helper inputs, omitting each bridge
shear, deleting a consumed source pin, and changing the word digest.
The first three are counterexamples to specified shortcuts, not bugs in
the source, which already uses a conservative composition product.
All mathematical arithmetic here is exact integer arithmetic.
