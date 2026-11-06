# A fixed negative-coefficient half with no extra clean work cells

Prepared for ToikY with substantial source-aware OpenAI Codex assistance.
Apache-2.0. The positive table, its resource proof and signed-half contract
are credited source components, identified in SOURCE-PINS and CREDITS.

## 1. Contract and exact model

Let W≥2 and let x be any signed W-bit two's-complement integer. A resident
read-only coin u is either zero or one. Write x=2q+p with p∈{0,1}.
The exact negative ABI from zxv6092 is

    S(-x,2,u)=-q-pu = -S(x,2,1-u),
    S(n,2,u)=floor(n/2)+1[u < n mod 2].

Negating S(x,2,u) at the SAME coin generally gives a different fixed-seed
endpoint. The construction below keeps external u unchanged and retains
the original parity p=(-x) mod2=x mod2.

Use Nick Petalas6801's local machine: one mutable work tape with uniform
alphabet {0,1,P0,P1,S0,S1}, one stationary read-only coin tape, and rows
(state,read,coin,next_state,write,move), move∈{-1,0,1}. There is no row
field for writing or moving the coin. Initial work data are

    P0 b0 ... b_(W-2) S(b_(W-1)).

The head begins at parity; the sign is distance W to its right. Exteriors
are arbitrary. The declared end layout has the result, Pp and the same
sign-marker position. Both heads return. Compiled direction is retained;
each directional call ends at its fixed halt state, without a free reset
to its entry state. Repeated-call control is a separate obligation.

There are W value cells, one initially clean parity cell and one stationary
coin cell: W+2 visited cells on two tapes, with no other initially clean
WORK CELL. The six-symbol alphabet is a supplied uniform capability.
We temporarily use the existing P1 glyph inside a value cell and remove
it before any component handoff. This does not add a glyph or cell; it
does use the existing nonbinary alphabet capacity. Immutable location-
typed markers or a two-symbol physical implementation require another
conversion/cost argument. No such binary-native cost is silently free.

## 2. A local modular negator

The following structural rows ignore the coin; expand every row once for
u=0 and once for u=1. Pp means two separate P0/P1 rows. There are sixteen
structural rows and thirty-two coin-expanded rows. N0 is entry and H is
halt. The input parity marker may be either P0 or P1, independent of the
value being negated.

    state read    next write move
    N0    P0      NZ   P0    +1
    N0    P1      NZ   P1    +1
    NZ    0       NZ   0     +1
    NZ    1       NC   P1    +1
    NZ    S0      NB   S0    -1
    NZ    S1      NB   S1    -1
    NC    0       NC   1     +1
    NC    1       NC   0     +1
    NC    S0      NR   S1    -1
    NC    S1      NR   S0    -1
    NR    0       NR   0     -1
    NR    1       NR   1     -1
    NR    P1      NB   1     -1
    NB    0       NB   0     -1
    NB    P0      H    P0     0
    NB    P1      H    P1     0

NZ walks over the low zero prefix. At the first interior one it writes a
temporary P1 tag. NC complements every higher bit, including the marked
sign. NR returns over those higher, now ordinary bits, reaches that tag
before the original parity marker, restores its known value one and
enters NB. NB walks over the unchanged low zero prefix and halts at the
original parity marker. In particular NB has NO row for an interior one.
The invariant, not an uncharged address comparison, identifies its stop.

If the value is zero, NZ reaches S0 and returns in NB without a tag. If
the only one is the marked sign, NZ reaches S1 and likewise returns;
this is the minimum signed value, fixed by modular negation. These cases
explain both sign rows rather than hiding an overflow exception.

On every W-bit word, the low zeros and first one are preserved while
higher bits are complemented. This is negation modulo 2^W. Thus N is an
involution on all canonical W-bit values, returns its parity marker and
coin unchanged, restores ordinary interior bits and never visits outside
the supplied interval. Ordinary integer negation agrees with this map
except at the minimum signed value. We use it for ordinary negation only
after the half, where that value cannot occur.

Entry costs one row. Processing the W value cells through the sign costs
W rows. Returning from the sign to the parity halt costs W rows,
including the stationary final row. This holds for either tagged or
untagged branches. Therefore

    T_N(W,value,p,u)=2W+1.

The work head makes exactly W right and W left unit moves; only its final
halt row is stationary. All W+1 work cells are visited, with no excursion
to an exterior cell. The coin head stays stationary throughout.

## 3. Local reversibility of N

Use the sufficient criterion stated in source6801: for each target state,
all incoming rows have one head direction, and for fixed coin the target
state plus written symbol determines at most one source row. The direction
recovers the previous head location; its written symbol recovers the row.

The incoming directions to NZ and NC are +1, to NR and NB are -1, and to
H are zero. Their written-symbol sets, respectively, are

    NZ: P0,P1,0;   NC: P1,1,0;
    NR: S1,S0,0,1; NB: S0,S1,1,0; H: P0,P1.

Each displayed symbol at a given target/coin comes from one row. N0 has
no internal incoming row. Both criterion clauses therefore hold for
every row, including rows not reached by a particular value. The temporary
marker carries information until restored; no branch/control information
is discarded by declaring it scratch. This is a locally injective partial
machine, not a total operation on arbitrary malformed tapes.

## 4. Complete forward and inverse tables

Retain the exact positive source TABLE with thirty-three rows per direction.
To interpret its coin as v=1-u, replace only each row's read-coin field c
by 1-c. Work writes and moves are unchanged. This is a control-level
reinterpretation of the read-only coin, with no coin write, flip, second
sample or uncharged movement.

The forward table contains the source forward rows, with states prefixed
PF_, followed by one copy of N prefixed NF_. Redirect the source H target
to NF_N0 and the negator H target to HF. Start at PF_F0 and halt at HF.
The inverse contains N prefixed NI_, whose H target is PI_I0, followed
by source inverse rows prefixed PI_, with their H target HI. Start at
NI_N0 and halt at HI. These are namespace renamings; the inverse and
forward halt labels retain their compiled direction.

Each directional table consequently has 33+32=65 rows, 130 overall,
independent of W. TABLE.json is the literal program. The source program
data are credited components; they are not new rows of this contribution.
No width-dependent unary program or addressed seek is invoked.

For the forward value, the positive component gives

    z=S(x,2,1-u)=q+pu,
    -2^(W-2) ≤ z ≤ 2^(W-2).

For W≥2 this range excludes the minimum signed W-bit value. N therefore
computes the ordinary negative y=-z=-q-pu, exactly the required ABI.
It preserves Pp, the resident coin and both head positions. Its tag has
been released before HF. Canonical entry/exit layouts and arbitrary
exterior contents are preserved, as required.

For inverse input (y,Pp,u), first apply N modulo 2^W, then the source
positive inverse under coin v=1-u. If y is not the minimum signed value,
the negator gives -y and that inverse reconstructs

    q=-y-pu,    x=-2y+p(1-2u).

Source6801's exact inverse-image theorem accepts precisely when this x
fits W signed bits and restores x and P0. For the remaining y=-2^(W-1),
N fixes y modulo 2^W. With pu=0 its top two bits are 10; with pu=1 the
source decrement wraps them to 01. The source sign-extension test rejects
in either case. The desired integer reconstruction also lies outside the
signed range, since it is at least 2^W-1. Thus the minimum-value modular
corner creates no false inverse input. This proves the complete image
criterion, both endpoint compositions and restoration on their declared
domains. Rejected nonimage inputs have no rollback promise.

## 5. Phase joins retain local injectivity and charge every step

In the pinned source data F0 and I0 have no internal incoming rows. Its
halting rows all move zero. Source forward halt rows have unique written
Pp/coin pairs; N's halt rows do too. After renaming, the new NF_N0 and
PI_I0 targets therefore each have only zero-direction incoming rows with
unique written Pp/coin pairs. Other state namespaces are disjoint.
The coin-case bijection preserves the source criterion for each coin.
Section3 establishes it for each new negator copy. Consequently each
complete compiled directional table satisfies both criterion clauses.

A join changes the target state of an ALREADY COUNTED row. It adds no
transition and supplies no erased data-dependent control bit or reset.
Forward and inverse remain compiled retained choices with fixed HF/HI
return states. Collapsing that distinction is outside this contract.
These local/endpoint arguments do not install a repeated-call compiler.

## 6. Exact transition invoice

The credited positive table costs 2W+1 when p(1-v)=0. Otherwise it costs
2W+2k+3, where k is the first zero position of q=floor(x/2), capped at
W-1 (use W-1 when all W bits are one). Its inverse on the corresponding
image costs exactly the same number. Here v=1-u, so its condition is pu.
Adding the exact 2W+1 negator cost, without a phase-join surcharge, gives

    T_-(W,x,u)=4W+2               if pu=0,
    T_-(W,x,u)=4W+2k+4 ≤ 6W+2    if pu=1.

Both directions have this invoice on a valid forward/inverse pair.
For x=-1,u=1, p=1,q=-1,k=W-1, so each direction attains 6W+2 for every
W≥2. The negative result there is y=0, with retained p=1 and coin u=1.
This is the exact worst case of these tables, not an optimal leading
constant among all possible programs. Source6801 owns the 4W+1 positive
bound; only the new negator/composition invoice is claimed here.

## 7. Evidence and source-execution boundaries

The all-width statements above have a written proof. The new verifier
replays literal candidate rows against independent integer arithmetic,
checks directional microstep criteria, exact costs, inverse boundary,
tag cleanup, head/coin/control/exterior preservation and meaningful faults.
Executed domains/counts and final immutable byte bindings are reported by
generated receipts and the README after actual observations.

The positive source TABLE is PROGRAM DATA. Executing the new negative
word executes those source-derived positive transitions as a credited
component. Reports must say so, even though the original positive checker
is not imported or rerun. The older6092 unary program is not a replay
target. Neither the negative arithmetic itself nor the positive table's
reported prior finite counts are rediscovered or recounted as new results.
New finite evidence is for the composed negative contract and local N.

## 8. Remaining physical obligations and credit

The logical uniform six-glyph work tape, markers, one retained parity bit
and resident read-only coin are supplied premises. Binary encoding and
marker production, conversion from6092's layout, coin acquisition and
delivery/freshness, allocation, actual reached widths, native MOVE,
repeated-call control, precision/restoration/storage and the complete
supplier invoice remain unprovided. No actual selected caller is repriced.
The original joint-query-controller acceptance gate remains unmet; its
card scope is explicitly changed and its outcome partial. No broad family
search, optimal-machine theorem, supplier, κ/frontier change or merge is
claimed. All five selected assumptions remain. Source-aware AI challenge
and finite execution are separate from human or proof-kernel acceptance.

Credit zxv6092/6066 for the exact two-sign ABI/restoration and charged
baseline; Nick Petalas6801 for the positive fixed table, layout/resource
proof and released negative branch; JoyboyBrian6095, AAAmirinu6244,
Nick6026, Ali Romman5599 and the retained stochastic/native lineage.
Two's-complement identities, first-one negation, local partial-machine
injectivity and composition are classical. Substantial OpenAI Codex
proposal, implementation, source-aware challenge, overlap and metadata
roles share the provisional/source-data exposure; no blind or independent
human/end-to-end verification claim is made.
