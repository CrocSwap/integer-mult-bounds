# Numerical and ownership boundary for one actual child

## Source-bound entrance and receiver

The pinned selected WORD has 770 public fields and 29 owned fields. Its event9896
is MOVE236 from frame 3=[] to7=[21], with public rather than private ownership.
Before this event every opcode is ADD, INIT or SCALE. Both public fields 236
and 720 initially use frame 3. The complete destination-write scan finds only
8203: ADD236<-236−2*720, and no earlier write to720. INIT targets are owned and
cannot alias these public fields. Therefore the exact entrance is
u=initial236−2*initial720. It is coarse-h aligned; no earlier MOVE-return error
or fractional scalar touches either entrance. Earlier reads of236 do not write it.

PR6499 initially quantizes each512-complex-coordinate public field to coarse h.
Its Euclidean quantization defect is at most 16h, so if ideal initial fields have
norm at most B, the stored entrance obeys ||u||<=3B+48h<4B for p=t+14>=14 and
h=B2^-p. Fine records encode this same value as32 times the coarse integer.
The numerical child requires and checks the exact division by32.

The source MOVE convention is Γ_to Γ_from†, from canonical caller `local.py`
(native recipe construction). Frame3 is empty, so this event's operator is
Γ_[21]. Frozen `canonical_frame(9,[21])` gives chronological K†, C(bit0,+), K.
Its ideal operator is K C K†, including the full absolute phase.

## Actual frame and rounded map

The source monomial has G rows(3,4,9,16,1,32,64,128,256), inverse rows
(16,17,2,20,8,32,64,128,256), quadratic rows(16,0,16,0,5,0,0,0,0) and zero
linear phase. Equivalently K|x>=(-1)^[x0(x1+x3)]|Gx>. The source compiler's512
ideal columns are checked against

    Γ_[21]|z> = (1+i)|z>/2 + (1-i)(-1)^[z0+z2]|z xor21>/2.

This is an ideal operator identity only. For the actual rounded oracle, orient
original-coordinate pairs with left bit4=0 and right=left xor21, and apply the
phase(-1)^[left0+left2] on the right component before and after the pair kernel.
This orientation follows G^-1 row0=16. Its left endpoint has absolute
K†-chart phase zero, not merely the asserted relative phase. It cannot be replaced by arbitrary pair
exchange merely because the ideal linear operator is symmetric: the nonlinear
rounded kernel need not commute with exchange.

The implementation evaluates the literal predecessor6509 kernel, once, on all
256 disjoint pairs in the K† chart. Its all-grid theorem gives coarse outputs,
combined pair squared error0 or h², and an exact same-grid inverse. The two
monomial wrappers are exact and preserve Euclidean norm. Thus the completed
error relative to ideal Γ_[21]u has square at most256h². Its field norm is at
most 16h=B2^-(t+10), precisely the6499completed error allowance at n=9. No final
coarse rounding is added. The predecessor pair theorem, phase covariance and
inverse retain their original authors' credit.

For sharpness set initial720=0 and choose initial236=K v, where v has x=1h,y=0
on each of the256 bit-zero pairs. Its norm is16h<=B, so it is a valid public
input after initial quantization. Every pair has a mixed-parity sum and squared
rounding error h², giving total256h². This is deterministic actual rounding,
not a freely chosen independent-error pattern.

## Fixed records, work and cleanup

Every partially processed pair layer differs from the corresponding unitary
partial layer by at most 16h. Its norm stays below5B. Monomial phases and
permutations preserve norm. Thus coarse component magnitudes stay below
5*2^p, and raw pair numerators have magnitude at most20*2^p+1<2^(p+5).
The existing p+21 signed temporary width is conservative. Returned fine
records have magnitude below160*2^p<2^(p+8), so the caller's p+16 signed format
is ample. Exact /32 and *32 conversions introduce no rounding.

The reference norm-admission guard first checks p+16 signed input format.
After exact /32, each component has at most p+11 signed bits. Its square fits
2p+21 unsigned bits; summing1024 squares fits2p+31 unsigned bits. These wider
guard temporaries and the cap square are charged explicitly. Guarded bit work
is O(512*(p+21)^2); the core native path is O(512*(p+21)). Forward admission
uses3*2^p+48; inverse validation admits an additional16h to contain the forward
image. Both remain below the5B intermediate bound used above.

A fixed permutation cycle is evaluated with one Gaussian temporary initially
zero: swap it with the first location, then each successor, then the first
again. A cycle of length L uses L+1 swaps and returns the temporary to zero.
Fixed points require only their phase. Correct phase placement and inverse
cycle orientation are checked against the complete fixed route and ideal
columns. Routes are read-only program data; preparation, storage, decoding,
reads/writes and temporary/control work are included in the invoice.

This certifies the in-place destination update and the cycle temporary's return.
It does not turn ordinary pair arithmetic into a clean reversible bit circuit.
The source pair workspace's initialization/clear requests remain explicitly
charged under its indexed model; physical pair-local/control cleanup is open.
No Python-GC argument or uncharged old destination bank is used.

This is one width-one numerical child, with a direct finite indexed bill. There
is no accelerated recursion claim, full physical tape implementation, complete
caller/stock/compiler/outer admission or new kappa. All five framework assumptions
remain. Finite executions corroborate the source-bound written argument; they
are not a formal proof kernel or independent human acceptance.
