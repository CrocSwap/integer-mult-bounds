# Addressed matcher and ROW schedule

This closes one scheduling obligation under named P1/P2 primitives, not their
fixed-tape implementation or P3. The fixed source is original helper462, from
frame0 to rank-four frame506. With source rows B and A, S8=[B^T|A^T], and
P8=B^T(BB^T)^-1B=S8 diag(I4,0) S8^-1. For f>0 put N=8f and S=S8 tensor I_f.
This explicit tensor family is not the enormous complete #4814 uniform word.

Rational elimination emits factors E1,...,Et with S8=E1...Et. Each is a swap,
a unit scaling or an elementary add; the actual source has 5/5/14. Each right
factor acts on columns, so E[i,j]=a updates column j from column i. Lift each
factor separately to each lane, on each of the N high-matrix rows. Inverse
routing reverses this chronological list and inverts every factor.

Both executable entry points require odd prime q by exact trial division.
The finite matrix solver therefore works over the local ring Z/q^w, not a
general composite-modulus ring; an invertible residual column always has a
unit pivot. Global compiler prime thresholds and witness avoidance are still
separate inherited hypotheses. The verifier independently multiplies both
actual emitted factor lists over the rationals and checks the source projector.

For G=G0+qG1 and local ring modulo M=q^w, let L=S mod M and R=q^(w-1).
After the complete high linear factor word, G1'=G1 L mod R. The generator
retains an explicitly owned copy of the old low row while applying it. Then
C=(G0 L-(G0 L mod q))/q mod R is added, one addressed cell at a time, and the
low type changes to G0 L mod q. Thus the rebuilt row is G S mod M. S is a unit
matrix at admitted q, so this is a permutation of the entire GL cover and
carries arbitrary array values without productive copying. Inverse routing
restores the complete original row. The finite low-type permutation and the
carry-control preparation remain charged P2 implementations, not address oracles.

Each high swap acts on two explicitly addressed complete radix-q chunks of
width e=w-1. If 2k>=e, it calls the named older completed supplier directly.
Otherwise its high prefix H_hi of k digits is borrowed as ROW, with D_hi and
all other exposed fields retained as spectators. Pad only this ROW range to
ceil(q^k/reserve)*reserve. The body emits the literal five-step source wrapper
D-=H; F; D+=H; F; D=H-D. Given P1's restored raw endpoint F=(CD,CH), its result
is exactly (D,H) on the body. ROW is checked returned before unpadding and
before the older width-k high-part interchange. Consequently the entire two
chunks swap and every unrelated current field is unchanged. The borrow is
from the CURRENT argument, with no new external ROW or zero original owner.

The outer exposed ROW and arbitrary complete spectators are disjoint from
the high-matrix fields. Induction on steps preserves their bytes and physical
owner identifiers. No two original owners may occupy the same physical slot;
no owned low cache is a productive source owner. Every allocation is paired
with complete initialization, clearing and release. Successive inner borrows
reuse the restored range and never multiply a reserve per sequential call.

At the native cut the cover row is h=gS. The inherited completed canonical
rank-4f contract has projector h Q h^-1=g P g^-1; it leaves the whole ROW and
spectators fixed. Undoing the route restores g, while the head/tail result is
the requested source projector with its complete tail reversal. The generator
therefore schedules this one complete source invocation correctly under the
named primitive contracts, at every f and every admitted odd prime/width.
Finite independent execution corroborates the induction; it is not a proof of
P1's native/tape primitives, P2's movement bounds, P3 or API admission.

The ledger records each completed primitive, exact addressed counts, argument
widths, low-cache allocation, ROW padding range and exact arithmetic workspace.
In particular it never maps unresolved physical cost to zero. Low-cache size
is N^2 ceil(log2 q) bits, independent of w for fixed N,q. A route accumulator
bounded by N(M-1)^2 needs bit_length(N(M-1)^2)+1 bits; fixed rational inverses
must be prepared at the current modulus and their work remains charged.
These are exact integer precision requirements, not a bound on the native
arithmetic provider's precision. P3 needs those provider, tape and recurrence
constants separately; no scalar stock constant is derived here.
