# Physical first narrow inverse-window transaction

Prepared for @CubeJerry with substantial OpenAI assistance. **No new κ.**
Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. Result and exact boundary

Fix one microbox/coarse context, union round r and active axis f. Let Q be an
ordinary section of the caller's same rational Gaussian Reference, partitioned
into interiors I and retained indices J. Write

\[
Q=\begin{pmatrix}A&B_0\\C_0&D\end{pmatrix},\qquad F=D-C_0A^{-1}B_0.
\]

E contains J and every interior endpoint coupled to J, verified by exact zero
support. The input has already passed the preceding dense interior stage.
The ideal first sparse window is

\[
T_E(v)_{E\setminus J}=v_{E\setminus J},\qquad
T_E(v)_J=F^{-1}(v_J-C_0v_I).                 \tag{1}
\]

Only supported entries of v_I are needed. This is the first narrow inverse
window of #4100's five-factor arrangement. The intervening interior map acts
on a disjoint bank and can follow the boundary solve. The second shear,
broad forward F application and complete multiplication remain outside scope.

`UnionInverseWindow.run` implements the specified rounded version of (1),
using unchanged #5059 completed-product rounding and the retained exact
seven-product kernel. It returns the original record order, every header bit,
and exact E-minus-J scalar words. Borrowed bodies/origins are restored; owned
scratch is erased; `consume()` erases the protected output. Tapes and roles
are fixed independently of all encoded dimensions.

The theorem starts at prepared step-4 complete E-lines, headers, E/J tables
and same-context pages. Actual #4583 flag/ordinal emission and the whole union
router remain open physical interfaces. The finite harness executes retained
#4327 scheduling around this literal transaction; §7 identifies its host
boundary and source substitutions. No host scheduler operation is claimed as
a literal tape operation.

## 2. Serialized interface

The unchanged #4583 header contains marker01, g h-bit coordinates, g flags,
g h-bit ordinals, t-bit count and t-bit tag, all big-endian. Thus
H=2+2gh+g+2t. Each header is followed by real/imaginary w-bit **little-endian
two's-complement** integers on the 2^-P grid. This scalar format has no
negative-zero pattern. Unchanged signed readers/writers provide linear scans,
sign recovery and headroom checks; malformed nonbinary/truncated input fails.

Physical Count metadata are g,h,t,f,r,a=|E|,n=|J|,b,w,P, with a>=n>=1,
dyadic b>=2, 0<=f,r<g and P<w. The E table contains a sorted h-bit coordinates;
the mask contains a bits and n ones. Eight factor ports hold shear and F
pages. Payload/table/page ports must be pairwise distinct and outside every
active or inactive owned descendant. Metadata may alias each other, but not
these ports or owned roles. All origins are checked through paid moves.

The reader checks marker/tag/count, active flag and count of earlier flags,
active coordinates against the E table, consecutive active ordinals0..a-1,
strict E ordering and zero inactive ordinals. Masking only the active coordinate
and ordinal, it compares every other header bit against the line's first
record. It checks complete table extents and J cardinality by scans. Therefore
accepted lines have common spectators and complete ordered E values.

Other-axis membership/rank truth, line distinctness and common coarse context
are preparation premises. Equal local headers cannot identify different coarse
pages. The source producer binds one Reference/origin/partition; this is not
online authentication of arbitrary coefficient pages. No long-key sort is free.

## 3. Original coupling through the existing solver

Let N contain C0 only in J rows and E-minus-J columns. For any entrywise-masked
pieces N_s,N_t, the product is zero: an intermediate index would have to lie
in both disjoint sets. Split by b-blocks into N_L,N_D,N_U. Verified bandwidth
implies adjacent block support. Hence

\[
(I+N_L)(I+N_D+N_U)=I+N,\qquad(I+N)^{-1}=I-N.
\]

Lower diagonal inverse pages are identities; upper ones are I-N_D. The
unchanged physical `prepare_pages` accepts block-bidiagonal factors; scalar
triangularity inside a diagonal block is unnecessary. `FastBoundaryPages`
therefore serves both the shear and F solve. Protected outputs are copied or
merged then consumed, and the parent scope is suspended around each child.

Rounding preserves E-minus-J exactly: coupling rows are zero and diagonal
rows identity on already-grid inputs. No rounded J value feeds a later
coupling, since all coupling columns are in E-minus-J. Up to three effective
roundings affect a J component. This staged function can differ from a single
completed-shear rounding; an executed off-block control distinguishes them.
[NUMERICS.md](NUMERICS.md) funds page error, all four passes and the exact
Reference target. Incoming post-dense error remains the caller's induction.

## 4. Streaming invariant and physical layout

The outer loop reads the source end marker, without decoding or repeatedly
counting the whole substream. A batch collects b/2 complete complex lines,
carrying across prefix changes within the fixed context. Real and imaginary
columns alternate. Raw headers/current values are archived for that batch;
two component buffers are reused. Each E column is padded to b ceil(a/b)
rows; only the final incomplete batch gets inactive columns.

Column-to-row conversion uses #4376's lockstep schedule with encoded controls.
At span s, split consecutive whole N*s-word column groups onto two tapes,
then merge s words from each for every row. Doubling s takes log2 b stages.
The inverse splits per-row groups and joins whole children in reverse order.
Four fixed roles suffice, and clearing scans current live content. The old
classical transpose with b complete square scans is not used.

After the shear, copy and consume its full E return. One mask scan selects
J rows, keeping b columns together, then pads to b ceil(n/b) rows. The F
return merges with the saved E-minus-J rows. One inverse transpose exposes
component columns; interleave them with each archived header. Verify and
remove all row and column padding. The batch archive is then erased before
the next batch. Each actual line is emitted exactly once in its original
order, and its full header is copied without modification.

Every variable loop in this transaction uses an encoded Count or a nearby end
marker. Named role and descriptor tuples have fixed size. Python action,
line and batch counters are observations, unused by scheduling. Constructor
sealing and the inherited no-decoding tripwire are tested, but the all-size
claim follows from the source-level role/control invariants, not finite tests.

## 5. Complete online bill

Let m be the number of complete complex lines and define

\[
 K_E=\lceil a/b\rceil,\quad K_J=\lceil n/b\rceil,
 Z=\lceil2m/b\rceil,\quad
 Q_b=[2(2K_E-1)+2(2K_J-1)]Z.                 \tag{2}
\]

The exact matrix-call count is Q_b and exact scalar-child count
Q_b 7^log2(b), including both passes in each shear/solve. This retains every
small-R and partial-row ceiling. There is no call for an empty substream.

Put ell=1+h+t+ceil(log2(a+b+w+g+P+2)). Let T_7(b,w) be the retained kernel
bound, including its scalar multiplier and internal U/V width guards. The
complete new online time is

\[
 Q_b T_7(b,w)+
 O\left([ma(H+w)+ZK_Eb^2(w+ell)+1]ell^3\right).           \tag{3}
\]

Here T_7=O(b^log2(7)[M(w+log b)+(w+log b)L_7^3]), with
L_7=1+log2 b+ceil(log2(w+2)), as proved in the retained predecessor.
The extra ell covers genuinely encoded descriptor work, not free word-RAM
arithmetic. Header copying/comparison scans H bits; active big-endian fields
cost O(h²+t²), flag/index comparisons O(g log(g+1)), and all fit the stated
header allowance. Signed payload reads/writes are inherited linear scans.
Count products/divisions for padded extents and transpose lengths operate on
short descriptors; each stage's whole and chunk sizes are computed once.
The total stream length never appears in a per-bit arithmetic operation.

Per batch, transpose and inverse move K_E b²w bits O(log b) times. Mask
extraction/return, all archive reads, input/output copies, page validation,
rewinds, child consumption and live erasure are included. The #5059 outer
invoice uses local column count b and log(a+b) or log(n+b), not log(m).
Canonical prepared page banks are scanned in the already-priced child calls.
Source construction, exact rational serialization and physical `prepare_pages`
are separately included by [NUMERICS.md](NUMERICS.md), equation(13).

For the following production specialization, additionally assume the retained
carve's density |E_f|/L=O(W/B_int), a block b=Theta(W), and |E_f|=Omega(b)
on each nonempty active axis, so its row ceiling costs only a constant factor.
These conditions are not consequences of an arbitrary
admitted partition: taking I empty can make E the whole axis. The finite
fixture does not establish that density. In #4100's corresponding regime
h,t,log a,log b,log w=O(log p), w=O(p), H=o(p), and
M(O(p))=O(p polylog p). Combining this density and (2) with the inherited incidence identity
sum_(r,f)|E_f|m_(r,f)=sum_f |E_f| L^(g-1) gives the existing dense boundary
shape O(V d W^(log2(7)-1)/B_int polylog p), plus a polynomial per-microbox
ceiling/setup remainder. In particular the extra one in ceil(2m/b) costs
O((|E_f|/b) T_7(b,w)) per substream, with the corresponding priced movement
terms; there are at most g squared substreams per microbox. This
remainder is retained until an actual outer amortization funds it.
Here V is payload-bit volume; B_int is the carved
interior cap, distinct from b. This uses the current dense balance, not the
historical structured-exponent point audited by #5275. #4376/#4645 already
prove generic row-field/ledger absorption; neither is claimed anew here.

## 6. Fresh and retained backing

The protected full return occupies ma(H+2w) additional bits. Streaming
arithmetic does not make this output storage free. Apart from borrowed source,
metadata and page banks, a fresh call uses

\[
 O(ma(H+2w)+ab(H+2w)+K_Eb^2w+ell^2)+S_{fast}(a,b,w).      \tag{4}
\]

The second term is active batch/header storage; it is not the whole-space
bound. Two line buffers, transpose roles and selected/preserved matrices fit
the remaining terms. For repeated calls, retain the maximum visited extent
of **each** fixed role over its complete history, including erased buffers
and all inactive arithmetic descendants. Borrowed history is still caller
storage. Erasure preserves that accounting; it does not release past cells.
Named buffers and pools are emptied on both success and failure; a pending
flag protects the output even if the caller moves its head beyond live data.

## 7. Rounded scheduling and source harness

Rounded axis maps need not commute. For each flag class C_F, replacing an
active coordinate by another E_f coordinate preserves every flag. No complete
E_f-line therefore reads outside C_F. At round r every record of this class
undergoes the same r-th member of F. Thus C_F executes its active axes in
increasing order, as the full-grid ascending-axis rounded reference does.
Other axes act identically and other classes cannot affect its inputs.
This proves the identity for deterministic rounded line maps and current
values, without a linearity or commutation assumption.

`schedule_hook.py` makes three checked fixture substitutions in #4327's
retained verifier: replace random source/linear-reference setup by the actual
Reference/grid fixture; replace the uniquely marked step-5 block by the
literal whole-substream callback; expose final records in its return dictionary.
Step4, step6 inverse/radix and step7 split/LIFO bodies execute unchanged. The
callback serializes exact model-produced current records with the unchanged
#4583 codec, invokes the physical owner, verifies every returned header, and
supplies updated records to the original continuation. This is a host-model
integration fixture, not a whole physical union implementation.

The primary source is Reference(61,3,2,1,3,32), ordinary window[16,20), with
explicitly validated dyadic interior(1,2). E comprises all four coordinates
and J=(0,3). This is an admitted partition, not the conservative CORE-PROOF
carve output: its global W>=4 would make this tiny window all-boundary.
The finite fixture supplies admissible current values at the post-dense
boundary; it does not execute the preceding dense interior inverse or prove
its error induction.
The exact factors are physically serialized and unchanged `prepare_pages`
produces both banks. Host rounded pages are observers, not a substitute for
that preparation. The independent oracle derives F from the original Q
inverse's JJ block, checks both-sided original equations, and computes page
words and complete integer dots separately. Full-grid checking uses neither
the author's transport nor its local map. Cheap physical controls exercise
off-block coupling, partial batches, padding and failure after a completed
batch. Finite checks corroborate the universal proofs above.

## 8. Dependencies and remaining limits

#4100 supplies the five factors/schedule; #4327 its record-level audit; #4583
the header ABI. #4376/#4645 already prove generic short-field/ledger claims.
Open #6626 optimizes header width and supplies no physical caller. These are
inherited results. #4186 supplies the residual framework and #5059 its exact
two-pass page function. Retained kernel/caller files are byte-identical to
CubeJerry's published commit `f821cba68f44048e70e78afb75603ed4dde99f11`.
This package adds current-Reference page binding, original coupling composition,
serialized many-column transport/return and the complete substage invoice.

The inherited tape alphabet has binary data and fixed markers. Measured
actions are reads/writes/moves; a constant-factor binary simulation and finite
control establish the asymptotic TM bill. They are not counts of all Python
VM instructions or exact binary-machine transitions. No finite-size speedup
is claimed. Prepared headers/context, incoming dense-stage error, broad forward
stages and outer assembly remain premises or unfinished interfaces. The selected
frontier and all five global assumptions remain unchanged. **No new κ.**
