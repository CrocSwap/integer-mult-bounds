# Complete source-array backing of the first-range Consumer

This is a conditional all-domain source proof for Jose Manuel's unchanged
PR2697 `Consumer.apply`, not a physical allocator or a whole SelectedNode theorem.
It closes the complete-caller storage join requested by PR2825/2845. R9's ADD
result is an inner component, not the new conclusion. Scope starts immediately
before `Consumer.apply` and ends when its returned owned packet is delivered.
Directory setup, frame validation, every generated packet tag, event suspension,
output copying and normal cleanup are included.

## Domain and metric

Use the canonical successful source contract of PR2845: dimension64,
64<=parent_size<128, valid generated finite Program/Fields, positive spectator
counts, admitted prime power M=q^w, canonical separate numerical arenas and
all noncapacity validity/termination premises. The fixture metadata is not
selected catalogue admission. No observers, callbacks, specification lookup or
factory retain extra source objects or mutate borrowed backing. Use exactly the
source factories and real selected coefficient implementation. Python tracing,
external references to transient objects, concurrent mutation, host allocation
failure and arbitrary substituted callbacks are outside the contract.

The metric is the sum of lengths of distinct `Tape.cells` and numerical
`Word.cells` arrays, including LEFT, erased tails and both arena templates.
It is not Python heap/capacity, visited cells, tape movement or a bit-level
physical reserve. Let K0 count every entry array once, including unrelated
suspended residents, all allocated free numerical slots, borrowed Program,
source, old directory and count arrays. Arbitrary entry blank tails belong to
K0; they are never bounded by their current logical contents. Canonical borrowed
counts have no padded interior. Their lengths and identities stay fixed.

Let C be old-prefix multiplicity, H=(M/q)^4096, h the incoming depth, c the code
bit width, r/i the residue/index bit widths, F the complete per-prefix fibre,
N=CH and V=NF. All sizes are positive except h>=0. For the source record codec,

E=c+2+4096(r+1), Q=1+(h+1)E, Qold=1+hE, D=1+N(Q-1).

These count complete serialized fixed-width records, not compressed numerical
values. D is the fresh directory backing, Q a fresh prefix including LEFT.
Let b=max(1,bit_length(V),i,r). Let H_R,H_I be allocated numerical slots and
L_R,L_I their live subsets at entry. Define

G=(max(H_R,L_R+37672)-H_R)(r+2)
 +(max(H_I,L_I+41)-H_I)(i+2), T=200(b+3).

These are uniform upper bounds: independent arena high waters may persist
simultaneously even when live-word peaks occurred at different times. Neither
G nor T is claimed attained. K0 already contains both templates.

For t=max(2i+4,r+3), let J(h)=2((h+1)t+h(r+3))+t+(r+3)+2, the credited
PR2758 conservative four-array continuation bound. With P the entire borrowed
Program backing, put

R=max(J(h),4+J(h+1)+P+84+c+2i).

The second term includes the four parent callback stacks, owned extended
Program and leaf callback. Cleared backing is retained through its last
reference. PR2835's closed-coefficient prefix theorem applies to good, pair
and unit children and to adapter fallback under its canonical semantics.
The literal two-call R9 calibration does not prove those universal premises.

## Complete phase envelope

Set B0=2NF+3+D+2Q+4. A sufficient extra reserve is

G+T+max(
 D+2Qold,
 D+Q+5,
 (2N+1)F+4+D+2Q+max(Q,F)+4,
 B0+F+3+R+1,
 B0+2F+3,
 B0+3F+q^2+3).

The terms are directory production, frame validation, packet copying,
ADD callback, ADD traversal, and non-ADD action respectively. Total backing
is at most K0 plus this expression. This is a constructive upper envelope,
not a sharp maximum and not a claim that different phase peaks coincide.
`ledger.py` implements exactly this expression.

Directory production holds the fresh output and one saved old prefix. During
`saved=old_prefix(...)`, the previous cleared saved object remains referenced
until assignment finishes, so two Qold backings are allowed. Odometer Words
and count helpers are paid by G and T. The final old prefix and odometer cease
to be referenced when produce returns. No one object per high header survives.

Frame validation retains directory and first prefix. Constructing Fields makes
one empty Tape before replacing it with first. Callback construction creates
four empty Stack tapes. It validates the Program but never invokes weight,
so these remain four LEFT cells. `frame.close()` frees its numerical Words but
does not destroy the object: these four arrays persist in the local frame
through the entire packet call. This is the +4 in all packet terms. The
validation peak permits the replaced empty Fields tape as an extra cell.

PR2882's complete named-array proof gives the third term, including the
factory RHS, prefix replacement and output-copy peaks. Its source K is
already in K0. At action entry the retained caller part is bounded by
2NF+3+D+2Q, and four validation cells remain. The current local fibre is
borrowed by the action and excluded from action-private counts. The yielded
event and active child event hold numerical Words and finite labels; they
own no separate Tape. The suspended generator's numerical demand is included
in PR2845, including the fallback half-width Word.

For ADD, R9's source decomposition gives at most F+3 payload cells during
either callback, or 2F+3 during traversal. Counts/numerical arrays are counted
once globally through T/G. One replaced empty Fields tape can overlap the
callback start; +1 conservatively covers it. R contains every actual callback
serialized record category, including a child extension's new Program.
The native callback's source dependency closure allocates no private Count.

For atom_swap/sign, inspect every digit pass, not just its output. digit_swap
holds q^2 buckets of total payload F and an output of at most F; if an earlier
returned intermediate is retained it adds F+1. Thus private backing is at most
3F+q^2+2. The extra1 is harmless. digit_complement has q buckets instead;
translate_one has two buckets and one output. The sign wrapper keeps its last
complemented intermediate while translating; q>=2 makes 3F+q^2+3 cover it.
Loop assignment can retain the previous returned Tape, but it is the same
object as current, not another distinct payload. Complete prefixes and both
spectator sides remain in F. All routes and numerical operations keep their
existing time costs; this proof removes no paid operation.

## Count backing, not only nonblank count content

PR2749 proves all intermediate count values <=V, or uses the full i-bit index
width for depth/exponent counts. The same digit argument bounds their maximum
historical encoding length, including a copied marginal high zero: b+3 cells
including LEFT. Shrinking/clearing never increases that maximum. A borrowed
arbitrarily padded count would invalidate this step and is excluded explicitly.

Its source ROOTS inventory totals98 including irrelevant outer/legacy paths.
For backing, closed local variables must not disappear from the inventory.
Charge both the old value of each lexical owner root and a pending replacement
RHS to that root. Returning factories are already separately listed; lists
have the fixed multiplicities recorded there (three extents and three marginal
results). No count-bearing recursive cycle or callback capture is reachable.
Loops overwrite roots rather than append to a retained list, and at most one
replacement is evaluated per root at a time. Thus doubling the conservative98
roots covers closed previous values and constructor transients; rounding196
up to200 proves T. This is a written lifetime strengthening of the credited
content bound, not an inference from the finite test census.

## Exhaustion, ownership and limits

The complete authenticated import cohort allocates source arrays only through
numerical Arena/Word, Count/Natural/Counter, records Tape/Fields/Program/Stack,
directory/packet readers, and stream/bitstream payload factories. The category
partition above covers each. Native plans, Python integer metadata, prepared
code sets and ordinary object fields are outside this explicitly source-array
metric; they must not be advertised as zero heap cost. Program readers and
matrix/form arithmetic allocate numerical Words, not hidden Tape arrays.

On normal return the source's finally paths release numerical live ownership,
restore borrowed heads and erase owned temporaries; the returned packet is the
sole new retained nonnumerical array. Freed arena backing remains in K0+G.
Source byte/head restoration is inherited from the successful semantic
contracts, with finite direct controls. Exception rollback is NOT asserted:
produce, width checks and some constructor allocations precede Consumer's
try/finally. A malformed or failed input needs a separate failure ownership
proof; this theorem neither hides nor repairs that interface.

Actual-width setup runs use finite high radix1 and two old prefixes. They
execute original Consumer.apply through directory and frame validation, then
intercept packet entry. Separate complete small payload runs exercise all
three primitive tags and repeated prefixes; they do not execute the enormous
actual64-dimensional packet. Written source reasoning supplies the general
bound. No new selected supplier, full Node/recursive/outer reserve, physical
bank codec, movement tariff, H2/P3 admission or new kappa follows.

## Open next questions

1. Bind these complete source-array sizes and lifetimes to actual fixed bank
   capacity, markers, placement, movement and return grants.
2. Close setup rejection ownership and constructors before promising rollback.
3. Join this first-range boundary with full Node and suspended recursive/outer
   residents; the present K0 charges them but does not bound their creation.

Credit Jose Manuel PR2697; Ross Richardson PR2825/2831/2835/2845; Nick Petalas
PR2749/2758/2882 and ADD components; ywz65 directory serialization; David Arias
recursive caller and retained physical lineage. New work JoyboyBrian with
substantial OpenAI assistance, Apache-2.0. No human/kernel review is claimed.
