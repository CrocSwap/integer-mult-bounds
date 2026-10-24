# One complete physical periodic Gaussian update

## Exact successful-domain claim

Fix the unchanged Reference(384,1,2,4,18,320), description SHA256
`4001280a290db7fe1afbbbed80704821796da86c3de8f86516b8debaf099591c`.
The selected target address of source j is j for0<=j<192 and j+1 for192<=j<384.
Target192 is a hole. PR5159's exact source preparation yields3072 nonnegative
33-bit integer coefficients c(i,h), h=-4,-3,-2,-1,1,2,3,4, in the same order
as `Plan.rows`. The corresponding input is selected[(i+h) mod384]. These are
original periodic entries, including wraps; no local143-row approximation is used.

Put s=2^33, d=4151/65536 and R=(1+2/s)/d. For arbitrary integer complex vectors
u,y on this grid with component l1 bounds |u_i|_1<=s and |y_i|_1<=Rs, the service
returns all385 rows of

    z_i = u_i - trunc_toward_zero(sum_j c_ij y_j / s),

component by component. The hole output is exactly u_192. Input vectors and
row-major coefficients are borrowed, unchanged and returned at head1. The output
is owned, retained until explicit `consume()`. All six private tapes return erased
at head1, with their full allocated backing retained. The same owner is reusable
after consumption. Rejection has no rollback guarantee; successful-domain
ownership is the claim. No claim about untrusted corruption of an exclusively
transferred owner's internals is needed.

There are ten distinct fixed tape backings: three borrowed, six private and one
output. Every port uses the same meter; alias and canonical-head checks precede
cell reads. Blank-owner validation is itself physically scanned. A pending output
cannot be bypassed by moving its head to the end. `consume()` physically clears
and rewinds it, not merely a flag change. Fresh fixed-capacity blank backing is the
initial resource premise; constructor markers and every blank cell are installed
through measured local writes and moves. No tape is resized or allocated during
an update. The fixture serializer and checker may inspect arrays; measured
execution uses only current-cell reads/writes and unit moves.

## Arithmetic proof and range

All numerical work words are80-bit two's-complement, little endian. Coefficients
are33 unsigned bits. Since d>1/16 and 1+2/s<2, R<32; more sharply the displayed
rational gives R<16. Thus every input/iterate component has magnitude<2^37.
Each coefficient is<2^33, so every partial sum of at most eight products has
magnitude<2^73. The exact output magnitude is at most s+8*2^37<2^41. All these
quantities lie strictly inside the signed80-bit range. The bounds include
intermediate partial sums and do not assume cancellation or only final norms.

`muladd` is ordinary binary shift-add modulo2^80. For coefficient bit k=1 it
adds the low80-k bits of y to accumulator positions k..79 with one-bit carry.
Discarding the final carry implements reduction modulo2^80. The loop invariant
after coefficient bit k is a=a_initial+(c mod2^(k+1))*y modulo2^80. The range
above identifies its final residue with the unique signed exact integer sum.
The arithmetic uses only bit/carry states and fixed bounded control; it never
decodes a payload into a host integer.

`rounded` copies bits33..79 down, sign extends, and tests whether any of the
33 discarded bits was nonzero. Arithmetic right shift equals floor(a/s).
For negative a with a nonzero discarded part it adds1, exactly giving truncation
toward zero. `subtract_emit` is the binary full-adder for u+NOT(r)+1 modulo2^80.
Its signed interpretation is u-r by the same range bound. Coefficient products
and all partial sums are exact; there is precisely one truncation per output
component after all eight offsets, including for the zero hole accumulator.
The actual early-per-offset truncation control differs on178 fixture rows.

## Ordered delivery, including layout and wrap

The incoming coefficient tape is row-major source order, with eight records per
source row and33 bits per record. `setup` makes eight complete physical passes.
Pass h skips the other seven records by unit moves and copies that pass's record
to the next segment of a separate table tape. Each pass returns the borrowed
coefficient head to its original marker. This is a paid layout change: no host
transpose, dynamic array gather or free offset jump is used.

For one offset h the current-input head physically advances from its marker to
the fixed selected address h mod384. It then reads one whole complex word for
each of384 source rows. After source191 it physically skips the hole's two words;
after source383 it physically rewinds to its marker. Thus induction gives exactly
selected[(i+h) mod384] at source row i, including the two ends of the period.
After the pass it physically returns to head1. The coefficient segment and
accumulator bank are traversed in source-row order; the accumulator skips the
hole at i=192. Two80-bit temporary words hold one input component and one current
accumulator. The updated accumulator is written back by80 backward moves followed
by80 local copied bits. The second component uses the same coefficient record.
Every temporary is erased and rewound before reuse.

Induction on h gives the complete unrounded sum in every selected accumulator;
the hole remains zero. A final385-row scan applies rounding and subtraction and
emits output in original target order. Input u, table, accumulators and output
are returned/cleared as stated. These proofs concern arbitrary admitted payloads,
not only the retained deterministic fixture. The finite fixture corroborates all
770 components, all identities, head returns and retained erasure; the proof is
what supplies the quantified claim.

## Primitive instruction, setup and storage invoice

The declared physical model has local read, write and unit-move instructions,
and fixed finite-control operations. Each costs one. A bit full-adder/truth-table
operation costs one control step. A counted loop costs one entry, two per
iteration (test/advance) and one exit. Conditional tests and bounded geometry
transitions are charged explicitly with `tick`. Tape rewinds include every
read, move and continuation test. Successful-domain `need` predicates are
checking assertions of the proved instruction preconditions, not payload
computations or branching shortcuts. Host object-identity/capacity tests specify
the ownership ABI and are separate fixed arity metadata checks.

Geometry and word sizes here are fixed. Control indices are bounded finite
states, never arbitrary numerical inputs or offsets decoded from data. `skip`
performs every intervening unit move. Python is the implementation of this
finite-control local-tape model; a literal standalone compiled instruction tape
or all-width encoded controller is not asserted. Its source representation is
charged separately, as are its bounded control states. Runtime counters in the
meter and read-only checker observations are measurement instrumentation and
never execution operands.

RESULT records constructor, one complete update, zero-data reuse, and actual
output-consumption primitive vectors separately. Their sum counts all performed
physical work, including the eight-pass layout, entry blank scans, initialization,
all coefficient/input delivery, arithmetic, final output and cleanup. A zero-data
update follows every coefficient bit branch identically to any admitted data.
The only data-dependent instruction path is the negative discarded-bit correction
in `rounded`. Each taken correction adds exactly

    (reads,writes,moves,control) = (161,80,162,324).

Derivation:80 increment positions contribute80 reads/writes/moves,80 full-adder
steps and162 loop steps plus one carry initialization. The return scan contributes
81 reads,82 moves and81 control steps. Consequently for every admitted data vector

    update = zero_update + q*(161,80,162,324),  0<=q<=770.

The verifier checks this equality using the actual number of negative nonintegral
component sums, and records the universal upper vector using q=770. This is an
exact structural invoice, not extrapolation from a sample. Output consumption is
also a fixed complete scan. Installation and byte representation of the coefficient
supplier remain a separate premise below; they are not hidden inside these vectors.

Private payload capacities are101376 (offset-major table),61600 (accumulator),
33 (coefficient), and80 each (input, accumulator, rounded word), plus two markers
per tape:163261 cells. Owned output retains61602 cells. Borrowed row-major
coefficients retain101378 cells; each input retains61602. Total retained backing
is449445 cells over ten fixed tapes, all from the declared five-symbol alphabet,
so3 bits/cell gives1348335 backing bits. This includes empty/erased backing,
coexistence during setup, the output and both input vectors. No live-bit count
replaces allocated backing. Extra caller blank tails are outside this exact
fixed-capacity interface and would require their own charge.

The fixed-control source bytes and bounded controller state allocation are
reported separately in RESULT. Every loop induction variable is at most101376,
so17 bits suffice; the verifier counts at most96 local names across all source functions. At most
eight simultaneously active counted-loop generators add24 copies of their three
local values, so128 slots of32 bits safely cover this nonrecursive control. Add
32 constant slots of32 bits and a32-bit program location. Fixed references to
ten roles take four bits each. This is a conservative abstract finite-control
representation, not a measurement of Python heap size or a binary compilation.
The initial coefficient materialization, interval caches and host serializer are
not physical tape operations in this package: they form an explicitly borrowed,
authenticated input premise. Original setup is nevertheless actually replayed by
the default verifier and its full packet compared byte-for-byte to the retained
coefficient packet. Its numerical/caching bill remains that of PR5159.

## Numerical composition and limits

PR5159 proves, for this same quantized table and single rounding after each row,
that y0=u and275 updates have the prescribed state bound and combined coefficient,
data-rounding and tail allowance below2^-20/2; its analytic-reference perturbation
is separately funded. Exact physical-update equivalence allows that same induction
without a new error term. This is a symbolic275-update composition, NOT an executed
275-update physical trajectory.

A concrete composition uses two identical owners with alternating output banks.
The next owner borrows the prior output; once its update returns, the prior output
is consumed before that owner is reused. u and coefficients remain borrowed
throughout. Both owners' constructor/private/output capacities coexist and are
charged; every invocation includes its paid layout/setup again. The conservative
physical work is two constructor vectors plus275 universal update vectors plus
275 consumption vectors (the last consumption occurs after the final consumer).
Both owners' complete backing, rather than one scratch peak, must be used for
that composition. The first input y0=u needs a distinct physical copy because the interface
rejects aliasing. With n=61600 bits, constructing its framed tape costs
(n+1,n+2,2n+3,3n+3); copying u and rewinding both ports costs
(3n+2,n,4n+4,4n+4), in the same primitive-vector order. Clear this copy after
the first update for one further output-consumption vector. Therefore a complete
symbolic preparation/update/cleanup allowance is

    2*constructor + copy_constructor + copy_and_return
      +275*universal_update_upper +276*output_consume.

The eventual final output consumer is external and must return its head to1
before consumption, just like every owner output. Its actual arithmetic/work
is not included in this update-service bill. Two owners plus borrowed u and
coefficients and the initial copy retain674308 cells, or2022924 backing bits;
the erased initial copy remains resident. This explicitly pays the initial
copy and every service cleanup rather than treating an alias as free. The
executed claim remains the single complete update and zero-data owner reuse.

## Open next questions

1. Physically generate/serialize the authenticated coefficient stream, including
   original interval precision, cache coexistence, installation and restoration.
2. Supply the initial copy and enclosing final consumer, then optionally execute
   the full275-update alternating-bank lifecycle with its complete invoice.
3. Replace fixed80-bit/385-row control by an encoded variable-width geometry only
   after deriving its full arithmetic/control/backing bill.

No all-size throughput, sparse-halo speedup, literal binary program compiler,
full Core/Tensor/multiplier admission, new kappa or selected-frontier change follows.
Credit PR5159's original numerical service by JoyboyBrian, Jose Manuel's immutable
Reference and numerical source, Vlado Vojdanovski, Jeremy Kothe, Cinna Davis,
Mason Hale, Chafik Boukhalfa and the retained predecessor lineage. Prepared by
JoyboyBrian with substantial OpenAI Codex assistance; new work Apache-2.0.
