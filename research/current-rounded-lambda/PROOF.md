# Literal one-rounded global LAMBDA with paid Q² routing

Prepared for @CubeJerry with substantial OpenAI assistance.
**Conditional physical interface lemma; no new kappa, full caller, or tariff-cap claim.**

## 1. Actual source and exact scope

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The proposed source is #6936 word at
`03626137d0bd57f09b0bf9597376183ce6fa9683`, with the QUERY-only caller
published at `617903497387a98f7ca929ad0b6928dd32abffec` (3,095 events).
The caller has 14,480 LAMBDA occurrences after expanding its actual A/B
port lists. Each gives an exact sign s in {-1,+1} and a central direction
q from the word's 104 nine-bit ports. `construct_source(site,port,factory)`
checks this actual occurrence and constructs its fixed-q, fixed-s provider.
It is a new provider/header contract, not proof that an old compiler already
emits the required descriptor or dispatches these outer tokens.

The exact primary source `research/p104-main-wire-native/retained/physical-review/verify.py`
at that #6936 head has Git blob
`f41390e0246cd6604a94ef5b418f48a817a4208c`. Its `phase` function uses

    phi(c,omega) = sum_v c_v [v dot omega] mod4.

Its contact and query equations identify Q_q with the one-column multiplier
i^[q dot omega]. Its `central_normalization` explicitly keeps ordinary
Lambda polynomials outside tensor powers. Thus, with f positive columns,

    Q_f = tensor_j Q_q,
    Q_f² = tensor_j X_q,
    Lambda_s(Q_f) = ((1+s*i)I+(1-s*i)Q_f²)/2.

Q_f² is a simultaneous address translation by q in every column, with
**absolute Gaussian phase zero**. The Fourier character is
(-1)^(sum_j [q dot omega_j]), exactly the character of that translation.
This is an all-f identity, not an inference from width-one checks. In
particular Lambda_s(Q_f) is generally not tensor_j Lambda_s(Q_q): two odd
factor characters give Q_total=-1, global Lambda=1, but the product of
factor Lambdas is (s*i)^2=-1. That false implementation is rejected explicitly.

The unchanged #6936 `jclib.py` semantics are retained as
`reference/jclib_6936.py` from the public QUERY-only capsule: its LAMBDA
branch uses `((1+s*i)+(1-s*i)*q²)/2` on the total character. The new source
events keep that sign convention; no replacement definition is inferred.

The new literal monomial recipe is identity9, offset=q, zero linear and
quadratic Z4 coefficients, and phase0. This recipe is derived from #6936;
no membership in the selected #6030 native catalogue is used. The selected
catalogue has 22,803 events/3,453 MOVEs, whereas #6936 has 71,144 events/
6,323 MOVEs. Sharing a generic implementation does not identify those sources.

The retained implementation is `current-coded-gaussian-monomial` at
`7d1ff23714e6f9182c1d0ff9214f65def2f30e04`, joined through the direct serial
provider at `2ec95e06c2a16e73f9da9a8fe41912710135daaf`. All reused bytes
and their original paths/commits/blobs/SHA-256 values are authenticated in
`DEPENDENCIES.json`; no monomial, Count, Tape, ordinary runtime or executor
source is modified. The existing serial result proves its physical route
for all valid descriptors. It is not a premise that an arbitrary formal
involution is a free physical operation.

## 2. Exact new header contract and physical Q² join

At this new outer boundary, a complete field has uniform signed width W>=2,
one common grid Delta=2^-F, canonical coded real/imaginary components and
actual physical blank frontiers. Its caller descriptor has the retained
23-field binary encoding. Let f,K,H,G be positive, 0<=rho<K, u be active_start,
z back_start, a within_bits, and e the caller remainder. Require

    (f-1)G <= H,  2H <= u,  u+9fK <= z,  z+H <= a,
    9f <= d,  row_bits = record_bits*2^a,
    record_bits = 6*r*(W+1),  r positive.

outer and rows are positive. The source mapping identifies central source
axis i, column j with the address position

    u+(i*f+j)*K+rho,   0<=i<9, 0<=j<f,

measured in the retained most-significant address order. All other axes,
packing residues, rows and coefficient positions are spectators. A fibre
used for the precision norm must contain all these 9f translated axes.
For the actual outer carrier the other 144 blocks remain untouched; this
new contract must still be installed by the caller/header exporter.

`HeaderView` physically decodes the parent fields and changes exactly two:

    remainder'=0,     selected_axes'=9f.

The latter is computed by nine fixed encoded copies/additions. All other
21 fields are preserved byte-for-byte, including f,K,rho,u,z,a,record_bits,
row_bits,p,d,D and the cutoff. The parent may have e>=9; that is why simply
passing its old remainder to a rank-nine monomial would be invalid. This
private view is supplied only to the monomial consumer, not to an ordinary
or general global header producer.

The exact monomial consumer checks selected_axes=rank*f+remainder,
remainder<rank and selected_axes<=d. These hold. Its front reservation,
active extent and full back coefficient suffix are unchanged under the
new header. In particular `after=z-u-9fK` retains all subsequent carrier
axes, and the suffix folded into coefficient fields retains every complete
row bit. No partial central packet substitutes for the full ambient field.

The unchanged SerialProvider then uses f actual one-column calls, with
its physically encoded f'=1,K'=fK,rho'=jK+rho views. Column j therefore
flips exactly the positions above for which q_i=1. Its binary word consists
of popcount(q) flips. There is no phase, sign change, ordinary runtime call
or rounding in this route. The serial predecessor's most-negative phase
counterexample does not apply: every phase scan is exactly identity, so
every signed W-bit value, including the minimum, remains representable.
Its ordinary constructor and full fixed inventory are still allocated and
charged. No numerical ordinary child or two additional QUERYs are invoked.

## 3. Gaussian numerator and one final rounding

The public field x is preserved while an explicitly owned full-field bank y
is retired, copied from x, and translated by the complete Q_f² provider.
Thus y=Q_f² x in the original ambient order. This is a real copy and real
routing job. It receives no productive helper credit.

For one complex entry write x=a+ib, y=c+id, with integer grid mantissas.
The exact denominator-two numerators are

    N_R = a-s*b+c+s*d,
    N_I = b+s*a+d-s*c.

The desired mantissas are floor((N_R+1)/2), floor((N_I+1)/2). No earlier
rounding, rounded sign conjugation, or rounded subproduct is used.

`gaussian_table.py` emits one fixed table for each sign, with 5,275 rows.
Its ports are (public original, owned translated/staged bank, real numerator
work, imaginary numerator work). It uses only the unchanged lifecycle
branch/write/unit-move/goto/halt/reject ABI. All arithmetic below occurs
through those literal rows; construction-time integers never inspect a
runtime payload.

There are two private numerator banks, each holding one component at width
M=W+2, preceded by marker5 and followed by delimiter2. First scan the real
components, forming R=a+c and I=s(a-c). For bit inputs x,y and carries k_R,k_I,
write the low bits of x+y+k_R and s(x-y)+k_I, and retain their mathematical
floor-halves. After W bits, hold public heads at their real delimiters and
supply their sign bits for two high positions. The signed terminal tests are

    k_R = sx+sy-sR,     k_I = s(sx-sy)-sI.

Rewind the two numerator heads to their protected markers, advance the
public heads to imaginary components, and update in place. Reading old
numerator bits n_R,n_I and new public bits x,y, use

    v_R=n_R+s(y-x)+k_R,  v_I=n_I+x+y+k_I,
    z=v mod2,           k'=floor(v/2).

After W positions and two sign extensions, the exact signed guards are

    k_R=nR+s(sy-sx)-zR,  k_I=nI+sx+sy-zI.

Summing either recurrence times 2^j telescopes: the terminal carry times
2^M is exactly the difference between unsigned and signed expressions.
The displayed tests are therefore necessary and sufficient for the stated
signed sums. Carries are bounded by fixed small intervals independent of W.
No host division, value callback or public-width intermediate test is used.

Let A=2^(W-1). Each final numerator has three +1 coefficients and one -1
coefficient, after choosing s. Since input integers lie in [-A,A-1],

    -4A+1 <= N_R,N_I <= 4A-3.

Adding the upward-rounding offset1 gives [-4A+2,4A-2], strictly inside the
signed width-(W+2) range [-4A,4A-1]. The real-prefix sums also fit that
width. Thus no valid cancellation is lost to an intermediate range guard.
This proof includes W=1 for the arithmetic table, although the retained
physical monomial contract and the assembled provider require W>=2.

The table rewinds the owned copy's head over its two components using the
real numerator as a width guide: skip its two high positions, move left
once per remaining bit, then repeat for the other component. The original
public head stays at its imaginary delimiter. Both complete input components
have already been read, so overwriting this owned pair cannot affect later
original or translated input pairs.

For each numerator, add1 with a bit carry, discard the first result bit,
and emit W result bits into its original owned-copy component positions.
The one remaining high bit must equal the emitted sign; the final addition
carry must equal old_sign-new_sign. This is exactly the iff signed-width
criterion for floor((N+1)/2), including negative odd N. No assertion that
upward rounding commutes with negation is made: R_up(-1/2)=0 while
-R_up(1/2)=-1.

A completed pair leaves both numerator heads at their delimiters. Rewind,
clear their current logical digits/delimiters to encoded logical blanks,
and return to marker5 for reuse. Physical retirement later erases all encoded
blanks and any old longer backing. Equal real/imaginary widths and matching
public/owned shapes are checked while scanning; their canonical initial
format remains a theorem premise, not universal corrupt-input validation.

## 4. Complete staging, failures and ownership

The STAGE table writes only the owned copy and the two numerator banks.
It never writes the public field. Earlier completed pairs may have changed
the owned copy when a later pair rejects. Those changes are allowed only
because this is explicitly owned disposable storage.

On successful STAGE completion, the unchanged executor restores heads and
unchanged `Controller.primitive` retires its two work banks. A separate
literal COMMIT table copies the complete staged owned field to the public
field. All signed checks have already passed, so under the canonical format
premises COMMIT cannot fail its extent check. This separation uses the actual
executor's paid origin return; no free rewind guide for the full field is
assumed. The two numerator banks are reused and charged again by COMMIT's
primitive wrapper, even though its table does not need them.

`LambdaProvider.run` explicitly retires every owned work role before use,
copies the original field, prepares the private header, executes the real
serial translation, executes STAGE and then COMMIT. Its finally boundary
releases the view, physically retires all private roles including a failed
partial copy, and returns public and context heads to their local origins.
Thus a final signed-range rejection leaves the complete public value intact
and returns clean owned bodies and restored public/context heads. This
property is proved for valid numerical geometry and named arithmetic
rejection. No arbitrary malformed/interrupted native execution or process
termination rollback is claimed.

All physical tapes are distinct and behind protected local LEFT markers.
The initial public/context heads are at their origins. Old private bodies
must be contiguous binary prefixes and their heads within their local bodies
or frontiers. Hidden dirt after a physical blank is excluded. The fixed
inventory is allocated before runtime; pointer identity checks do not prove
physical segment disjointness. No arbitrary borrowed workspace is erased.

## 5. Actual-input error and all-column precision contract

For an admitted input, each real and imaginary output differs from the
exact Lambda_s(Q_f) of that actual input by at most Delta/2. Therefore on
any containing complete X-fibre,

    ||output-Lambda_s(Q_f) input||_X <= 2^((X-1)/2) Delta = eta_X.

The count is 2^X complex entries, or 2^(X+1) real components. This is the
single rounding contract demanded by the published precision package
`56bc9383594a3efc303148e00bb746851abd1ed5` Sections2/5. It is uniform in
positive column multiplicity and in all spectator fibres. Since the pure
translation is a unitary involution, the ideal global Lambda has eigenvalues
1 and s*i and norm1. That algebraic fact is prior; the new contribution is
its source-specific physical producer and one-rounded arithmetic join.

A simple sufficient closed admission domain is
||input||_X <= (2^(W-1)-1)Delta, with X containing every translated axis.
Unitary Lambda then has each output component within the same symmetric
bound, so rounding fits width W. More general inputs succeed iff every
rounded component fits. The source precision proof's common-width/radius
substitution may also be used once its actual caller/header and inherited
operator premises are installed. This package does not silently identify
its W,f,selected_axes with a complete caller export or prove all upstream
rounded states satisfy that external guard.

## 6. Full positive cost, source count and historical backing

Let V be the complete coded public physical length, E the parent descriptor
length, P the fixed total number of owned private roles, and A_old the sum
of their initially dirty contiguous physical body lengths. All constructor,
source access, fixed-table generation and allocation costs are F_template.
They are positive and separate from variable-input traversal.

For the new Gaussian stages, let S=sum(W_i+1) over all real components.
Counting every physical tape action and every executed flat row, a safe
bound is 4096(S+1), plus entry/final old-body, context-head and fixed-role
charges. One ordinary position performs at most four coded reads, two writes,
four moves and finite carry-state jumps; its reversals and two high positions
are included. Coded reads cost at most10 physical actions, writes9, moves4,
plus their executed rows. Pair rewinds, encoded-blank clearing, executor
origin returns, the separate full-field COMMIT and successful retirement
are all linear in S. Two-component work reaches at most 3(W+4) physical
bits in each numerator role. A previous larger width remains allocated.

An entry retirement from displacement p<=A costs 2p+3 for origin, 3A+1 to
erase, and 2A+3 to return: at most7A+7. The outer copy, final owned-bank
retirement, context returns and private view contribute O(V+E+P)+7A_old.
The new header construction/release has O_9(E+1) encoded-symbol work, because
rank9 is fixed. It makes no runtime integer conversion.

Retain the serial monomial's complete bill. Write g=popcount(q),
C=outer*rows, R1=2Wr*2^(a-z), M1=C*2^z, Vraw=M1*R1, and
A1=2+z+ceil(log2(R1+1)). Its contribution is

    O_9(f*((g+1)*(Vraw+M1*A1^6)+V+(E+1)^4+P)).

Therefore the whole Lambda invocation costs

    F_template
    + O_9(f*((g+1)*(Vraw+M1*A1^6)+V+(E+1)^4+P))
    + 4096(S+1) + O_9(V+E+P) + 7A_old.

There is no subtraction of inherited ordinary work and no conversion of
this bill to the old 1000-unit LAMBDA allowance. Only with the separately
stated padding absorptions R1>=A1^6 and (E+1)^4+P=O(V) does the variable
term simplify to O_9(fV), plus old history. If those premises fail, the larger
bill stays. All f iterations reuse one provider; no history reset or new
per-column allocation is hidden.

The one extra full-field bank has current backing V. Each of the two
numerator roles retains max(old_capacity,3(W_max+4)). The header roles
retain maxima O(E+1), and every unchanged serial/monomial role retains its
own full historical maximum from the predecessor space theorem. Add public,
context, ancestor and fixed-controller backing. Erasure does not shrink
these maxima. The unused ordinary object and its tapes remain counted.

At the caller-source level, there are 14,480 such service occurrences.
Each gains one explicit owned-copy lifetime and its positive bill; the two
primitive work roles and provider inventory must be included in active
stock. There are zero new recursive paid jobs and zero productive helper
credits. Whole-caller sequential reuse, unfinished-context stock and the
sum of all source/setup/runtime bills still require compiler integration.
No full raw cap, accepted exponent or unconditional theorem follows here.

## 7. Evidence and limitations

The source census pins every occurrence/sign/port/q. Physical descriptor
checks cover all23 fields with old remainders0,8,152 and several positive f,
including cases where passing the old remainder would violate rank9.
The Gaussian arithmetic has an independent direct integer oracle over all
four arbitrary signed inputs at widths1,2, plus wider signed endpoints.
It runs through unchanged primitive tables, including explicit rejection
cleanup, source protection and a positive tape/control bill.

Complete reduced-rank composition executes the actual monomial provider,
private header, Gaussian staging and commit for both signs, late overflow
and reuse after failure. An ordinary-runtime entry trap rejects any accidental
child invocation. The source-specific nine-axis recipe/header join is proved,
but the minimum4096-record nine-axis numerical run is not claimed executed:
the16-record reduced run took0.91s and more than5 million physical actions;
a simple record-scaling screen already exceeds230s before the larger recipe's
extra flips, beyond the120s attempt cap. This is a feasibility screen, not
a formal wall-time lower bound or a runtime measurement of the source case.
No nine-axis host vector evaluation is relabelled physical execution.

Credit the source authors DreamingOfClouds/#6936/#6937, the retained phase
and monomial work (#3087/#4172), CubeJerry's serial/provider/lifecycle and
scalar work, and the published source precision package. Horner/carry,
Gaussian identities, permutation tensoring and nearest-up rounding are
classical. Full source/header exporter installation, admitted caller precision,
all remaining native services, recursive owned history, common physical
tariff and analytic recovery remain open. All five framework assumptions
remain globally conditional. Separate AI review is not human or kernel
acceptance; the finite tests do not substitute for this all-size argument.
