# Physical half-source addition on one fixed grid

Fix a positive width n and an orientation epsilon in {+1,-1}. On two distinct
tapes, a word has left marker # at origin-1, n bits in least-significant-first
order, right marker # at origin+n, and head at origin. Both origins are arbitrary
integers. Exterior cells are arbitrary, including more markers and bits. The
alphabet is {blank,#,0,1}. A transition reads only the two scanned symbols,
writes at most one symbol per tape, and moves each head by at most one cell.
The compiled controller has 14 nonterminal states and 224 table entries for both
orientations together. Neither width, absolute position, an unbounded integer,
nor a seek instruction is available to it.

Let the two words decode as signed two's-complement integers x and y in
[-2^(n-1),2^(n-1)-1]. If x is odd, the controller rejects in one transition,
without a write or head movement. If x is even, it halts after exactly 2n+3
transitions. It preserves the entire source tape, both markers and all exterior
cells, changes only the n target bits, and restores both heads to their origins.
The target represents y+epsilon*x/2 modulo 2^n. If that mathematical result lies
in the signed interval, its signed decoding is exactly y+epsilon*x/2.

The range premise is not checked by this controller. In particular, an overflowing
sum wraps and halts successfully. The supplied signed-result contract must retain
the premise; the modular contract does not need it. Odd-source rejection is a real
runtime branch, not an unpaid global input checker. Equal widths, markers, tape
separation and well-formed bits are caller premises. Malformed inputs may reject
after partial writes; transactional malformed-input recovery is not claimed.

## Shifted source and addition invariant

Write x's bits as b_0,...,b_(n-1). The start transition checks b_0=0 and moves
only the source head right. An arithmetic right shift of an even signed integer
has bits a_j=b_(j+1) for j<n-1 and a_(n-1)=b_(n-1). This includes n=1: the only
even one-bit signed input is zero, and the initialized previous bit is zero.
In integer terms, the shifted word represents x/2; no rounding occurs.

For positive orientation set d_j=a_j and c_0=0. For negative orientation set
d_j=1-a_j and c_0=1. The latter is the n-bit complement-plus-one representation
of -x/2 modulo 2^n. At the beginning of the jth target update, source head is
origin_x+j+1, target head is origin_y+j, and the finite carry is c_j in {0,1}.
For j<n-1 the scanned source bit supplies a_j. At the last update the source
reads its right marker and the stored previous source bit supplies the sign
extension. The original target bit y_j is read before it is overwritten.

Each update writes z_j=(d_j+y_j+c_j) mod 2 and retains
c_(j+1)=floor((d_j+y_j+c_j)/2). Thus

    sum(k<j) z_k*2^k + 2^j*c_j
      = sum(k<j) (d_k+y_k)*2^k + c_0.

Induction starts at j=0 and the full-adder identity proves the next step. At j=n
discarding the final carry gives the claimed modular sum. Every target bit is
written exactly once in increasing order, and no source transition writes.
The integer interpretation follows from uniqueness of signed decoding in the
declared interval. This proves all widths, rather than extrapolating test cases.

## Return trace, exact cost and reusable dirty state

There is one start transition, n-1 ordinary add transitions, and one final
sign-extension update. Both heads are then at their right markers. One end
transition moves both left. Exactly n rewind transitions pass over the bits;
the next transition reads the left markers and moves both right into `done`.
Therefore the first terminal state occurs at

    1 + (n-1) + 1 + 1 + n + 1 = 2n+3.

All earlier well-formed states are nonterminal. Both heads stay within the closed
marked intervals. Only target positions 0,...,n-1 relative to its origin receive
writes. Exterior storage is neither read nor modified; translation changes no
transition. No work tape or initialized carry cell is used: the one-bit carry,
last source bit and orientation reside in finite control.

Run the opposite orientation with the same source and the returned target. The
modular updates cancel exactly, restoring every original target bit and both
heads in another 2n+3 transitions. If each call is being interpreted as a signed
exact-grid operation, require the intermediate target also to fit. The original
target may be arbitrary dirty data in the signed range; it is not initialized
to zero. The two calls cost 4n+6, and source access remains paid in each call.
This is endpoint invertibility on the stated interface, not a claim that the
underlying transition relation is a reversible Turing machine.
Finite control terminates in its prescribed `done` state; it is not restored to
`start`. A surrounding dispatcher may connect that known return state to its
next operation, charging any additional dispatch transition separately.

## Connection to the selected component reference

PR2370's exact retained `componentCode` is read(source), halve, addMemory(target),
write(target). Its theorem gives target+source/2 and preserves distinct sources.
For any common fixed fractional grid 2^-p, represent source and target as
x*2^-p and y*2^-p. Under the integer premises above, the physical endpoint
decodes as (y+epsilon*x/2)*2^-p, exactly that component equation (epsilon=+1).
Applying the controller to real and imaginary components requires two paid calls,
2*(2n+3), plus acquisition and routing; it is not a free Gaussian operation.

This is a refinement of the memory component equation only. PR2370 deliberately
retains a visible dirty accumulator holding the result, whereas this controller
has no such tape. No equality of those full machine states is claimed. A caller
must provide its own permitted scratch/accumulator contract and common source/
target charts. Frame annotation zero alone is not chart equality. The physical
marked two-tape layout has not been connected to the reference family allocator.

The package does not provide selected word initialization, physical family
addressing, common precision, all-prefix divisibility/headroom, or a global
supplier/recurrence. Marker creation, data acquisition and routing are outside
the measured prepared-word boundary. Generic ripple addition and sign extension
are standard; the contribution is this literal charged in-place boundary and
its source-matched contract, not a new addition algorithm or multiplication bound.
