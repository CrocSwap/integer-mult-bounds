# Join the original convolution's field lifetimes to one native window

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Scoped constructive implication; separate review is pending.

## 1. Statement and complete optimistic invoice

The caller is Ali Romman's original #7849 at
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd`: `TensorWord.apply`,
`Multiplier.convolution_grid`, and the two operand references retained by
`Multiplier.multiply` while that convolution executes. The numerical
interface is `direct-native-grid-interface` at #8093 head
`780e96d8c149690df0f06661e2b9f94eb91737fe`. SOURCES.json binds exact bytes.
Neither #7981's changed chronology nor the later integer-recovery portion
of `multiply` is covered here.

Let T be the complete padded tensor record count. Every field includes all
T complex records, spectators and holes. Let B be a common sufficient
signed width for every outer stored component during this interval. Count
one marked complete field by F_B=2T(B+2)+2 cells: two boundary markers per
component and two for the field. Fixed-alphabet alternatives change constants.
For external grid P, valid reference-state radius 2^E at native entrances
and maximum selected pack h_*, set

    W_* = P+E+3h_*+31,          F_* = 2T(W_*+2)+2.

The credited grid interface requests Q_i=P+E+1+h_i, left-shifts input
numerators by h_i and returns raw-H integers by denominator relabeling.
Its conditional private temporary allowance Q_i+2h_i+30 is at most W_*.
Native internal realization and service admission remain premises.

**Theorem.** Seven complete outer field slots suffice for the exact source
convolution interval, with the two original operands held unchanged. At
native calls the first, second and opposite transforms have respectively
three, four and six outer fields live. One complete conversion window
suffices for all calls. Under native return contract N in section 4, if
native private tape t has historical extent at most A_t over these serial
requests, joined historical backing is at most

    7 F_B + F_* + sum_t A_t + M + O(d B_c+B_work+log(T+1)).       (1)

M is a supplied bound on coefficient/control historical backing, including
entry history and the persistent tables and schedules during this interval; B_c
covers scalar coefficient/suffix width; B_work covers separately priced
local arithmetic temporaries. None is hidden in a field slot. Native tape
count is fixed by the supplied template, independently of input length.

If B,B_c,B_work,W_*=O(p), M=o(Tp), d<=T and the native implementation
independently supplies sum_t A_t=O(TW_*), this bound is O(Tp). Precision
alone does not prove the native extent premise. Over H native calls the
complete optimistic work invoice for this interval is

    original diagonal/coefficient work + sum_i native_cost_i
        + O(H T W_*+TB).

The last terms pay conversion, installation, full clearing, construction
of eight outer destination fields and retirement of seven. Original
native transfers, padding, coefficient delivery and cleanup remain fully
charged. This is no multiplier-exponent improvement or new kappa; the five
canonical assumptions and selected certificate are unchanged.

Any already visited native entry extent K_t is included: explicitly,
A_t=max(K_t,max_i A_t(i)), not merely the largest newly live request.
The caller slots use the same common width B throughout this one interval;
an unrelated older pool with wider retained slots needs its own entry term.

## 2. Exact source ownership cuts

Let a0,b0 be distinct original operand owners. `multiply` retains them
through `recovered=self.convolution_grid(a,b)`. The callee's formal a,b
initially alias those owners; they are not extra fields. Rebinding those
formals does not release the caller's references.

`apply` makes a fresh full-field list copy for a forward call or a fresh
conjugating list comprehension for the opposite call. Diagonal and H
stages then write that working field in place. `product_diagonal` retains
an index vector and d+1 scalar suffixes. The literal H body has scalar
components/tuples only. Axis tables, entrance/exit tables, jobs and idle
tables are separate persistent coefficient/control data.

Let f_a,f_b be raw forward outputs, A,B public-grid forward outputs, Z the
pointwise-product field, D the opposite working field, C its conjugated
return and R the final public-grid result. The complete reference census
at each largest reservation/construction/callback cut is:

| Source cut | Distinct complete owners | Count |
| --- | --- | ---: |
| First apply/native calls | a0, b0, f_a | 3 |
| First public-map construction | a0, b0, f_a, A | 4 |
| Second apply/native calls | a0, b0, A, f_b | 4 |
| Second public-map construction | a0, b0, A, f_b, B | 5 |
| Product construction | a0, b0, A, B, Z | 5 |
| Opposite apply/native calls | a0, b0, A, B, Z, D | 6 |
| Opposite conjugating return | a0, b0, A, B, Z, D, C | 7 |
| Final public-map construction | a0, b0, A, B, Z, C, R | 7 |
| Convolution returned | a0, b0, R | 3 |

A destination counts from its first reservation, before full initialization.
Map/comprehension iterators retain their inputs until construction finishes:
f_a cannot retire before A, f_b before B, nor C before R. In the opposite
return D remains live while C is built. Z stays in the convolution frame;
A and B remain local references until that frame returns. Immutable scalar
tuple sharing does not alias mutable physical field cells: the realization
copies represented words into distinct slots.

Exactly eight new complete fields are constructed: f_a,A,f_b,B,Z,D,C,R.
All except R retire by return. Neither root is retired. No later source
read refers to a retired field and no source decision inspects list identity.
An explicit compiler can therefore clear the complete slot at its proved
last reference and reuse it. At most seven reservations coexist, so seven
fixed slots suffice. The fixed seven-way selector is finite control. Six
slots fail at a displayed seven-owner cut for this unchanged out-of-place
chronology; this is not a lower bound for redesigned algorithms.

The induction is independent of the number or numerical content of stages:
all run synchronously on one working field. Actual `axis_packs` supplies
distinct original-axis strides, always on the complete padded array.
Dirty holes are ordinary records in every copy, native call and clearing
scan. No true-volume-only field is substituted for a physical field.

## 3. One conversion window and its paid access

Reserve one separate F_*-cell window on fixed tape. At an H site, borrow the
current working field while all other table owners remain live. Scan all
T records, writing shifted input numerators into uniformly W_*-wide records.
Q_i labels may vary; backing width does not. Strides/format descriptors are
part of charged source control, not free data-dependent routing.

The native service is synchronous. After it installs the complete returned
endpoint in the same held window, scan all records into the current apply
owner. No next source stage reads partial output. Then erase the complete
F_* historical interval and return heads. Include holes, zero records and
all guard cells. The credited grid theorem supplies the numerical endpoint;
there is no second post-return integer shift.

Conversion, commit and erasure each take a complete record scan with a
constant number of forward/return tape passes, O(TW_*) bit work. Markers
permit rewind without an unpriced random-access operation. A fixed maximum
window is blank/unborrowed before every invocation and after every return.
Previous wider requests cannot leave an uncharged dirty tail. Its origin
does not advance with the call count. H multiplies time, not its backing.

## 4. Native return and noncircular admission

**Native return contract N**, in addition to the grid/domain contract:

1. The callback borrows the complete window and exactly its declared dirty
   auxiliary owners. True-coordinate-only access is outside scope.
2. It installs the entire numerical endpoint in the held window before
   return, without substituting an unaccounted fresh result owner.
3. Other borrowed values/heads are restored. Private frames and transfer
   buffers are retired through their full historical intervals. No mutable
   private owner or window alias remains accessible to later continuations.
4. The same fixed private tapes and entry origins are used at each call.
   A separately legal capacity-independent execution supplies the A_t
   envelopes, including all native copies, fields, padding, headers and
   transfers outside the borrowed conversion window.

Every borrowed auxiliary owner's full backing must already be included in
the seven outer slots, the conversion window, M, or the A_t vector. There
are no unnamed, uncharged auxiliary owners; overlaps are identified by
physical owner rather than counted as fresh fields or omitted by aliasing.

The pinned mixed-rank FRAMES describes complete transfers, held-owner
installation, adjacent-frame retirement and sibling reuse of this form.
Its native chart, schedule and admission obligations are retained. The
literal outer source has no accelerated callback; its lifetime census
alone does not prove N.

A reusable returned window differs from an escaping mutable argument.
A retained alias could observe a later call's input or corrupt a newly
reused slot. The diagnostic lease epoch rejects later API access; it does
not prove arbitrary Python/native code has no hidden captures.

For capacity admission, first establish a legal capacity-independent native
trace satisfying N, numerical domain, stock and the A_t bounds. Seven caller
slots, one window and A_t cells per native tape then suffice by the displayed
induction. The wrapper cannot be the first capacity failure. Bounds asserted
only for already successful native calls cannot establish that trace. This
retains the noncircular qualification in the prior numerical-arena proof.

## 5. Historical backing, scope and evidence

Erasure changes content, not visited backing. Each caller slot retains at
most F_B historical cells, the window F_*, and native tape t its own A_t.
Different maxima can occur at different calls. The disjoint regions give
(1). In particular `max(7F_B,6F_B+F_*+sum A_t)` is not a valid replacement
for that sum: a native frame cleared before the seven-owner cut still has
visited backing. The prior per-arena high-water theorem is credited; this
contribution binds that distinction to the actual convolution and the new
requested-grid interface.

Dead exclusive fields are retired by ordinary destructive overwrite, with
complete scan costs. No reversible uncomputation is inferred. Native dirty
restoration remains in N; canonical owned-erasure is not discharged.

The theorem ends when R returns and a0,b0 remain held. Later `physical`,
`original`, `coeffs`, `result_digits`, carry processing and the growing
final integer accumulator are excluded. The latter is not automatically
scalar scratch. Coefficient-construction history, full native admission,
outer recovery and the complete multiplier tape tariff remain separate.

In particular, the returned R is an intentionally surviving owner. Seven
slots cannot simply be reused for a later public convolution while a
caller still holds R or either original operand in those slots. Repeated
public calls require an explicit paid transfer of surviving results to
caller-owned storage and retirement/release of the affected slots, or a
separately bounded outer ownership schedule. Native no-escape alone does
not establish that outer lifecycle. No such repeated-call claim is made.

The bounded checker authenticates the literal caller methods and changes
only complete-field constructors to a fixed-slot logical pool. It compares
with unmodified source arithmetic on actual axis packs/legal strides,
heterogeneous widths and nonzero padded records. Diagnostic coefficient
tables are not a Fourier compiler certificate; the exact sequential native
oracle is not the accelerated supplier. CPython reference lifetimes only
corroborate section 2's universal explicit last-use proof.

**Open next question:** establish N and the A_t vector for one actual
accelerated global invocation at requested Q. Begin at argument transfer,
last held result installation and full private retirement. Native internal
realization, stock legality and physical extents remain the blockers.

Credit Ali Romman for #7849, mixed-rank FRAMES and retained supplier lineage;
Ross Richardson for numerical-arena historical maxima and noncircular replay;
earlier #8093 contributors and compiled-root/common-grid authors for precision.
Independent human and formal-kernel acceptance are not claimed.
