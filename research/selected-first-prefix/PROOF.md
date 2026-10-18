# The first selected prefix on complete families

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I give a scoped written proof and
finite executable evidence; I have not formalized the argument.

## 1. Quantified interface

Fix the selected R480/T16 archive, global call 0, and the row decomposition
in PR2287, `research/selected-complex-layer-closure/PROOF.md`, section 3.
Write W=14336 and Gamma=|O(73,2)|. At the node under consideration, require
R_rows=W Gamma U with U>=1. Interpret the existing row ordinal as

    row = (F Gamma + g) U + u,
    0<=F<W, 0<=g<Gamma, 0<=u<U.

Use the source's lexicographic row-order enumeration of cover matrices.
Put all remaining
compact, body and spectator coordinates inside each complete row. If a row
contains b>=1 Gaussian values, a whole family contains N=Gamma U b values.
The scalar interpreter receives encoded positive N and component width
h>=2, with one common binary exponent for these integer component words.
Its least-significant-bit-first words use two's-complement signed values.
The bank contains W consecutive complete families in this row order.

PR2287 specifies the mixed-radix row decomposition. I implement its natural
lexicographic ordinal here; the selected finite archive does not itself
serialize an all-size numerical tape. The contract applies after the
inherited row padding and before this call's cover-local entrance work.
It includes the entire unused row range and compact rectangle. A caller
with an independent outer prefix must deliver the corresponding family
streams or pay for its separate traversal; this implementation accepts the
single row-major bank described above.

Let v=2hN be a whole-family bit length and B=Wv the live bank length.
For admitted inputs, the executor returns the same bank except

    F119 <- (-F119 + F169)/2.

It performs SCALE(-1/2) first and ADD(+1/2) second. It preserves the input
bank and encoded headers until the caller requests commit. The caller can
then replace its owned bank and close the protected return before a
recursive boundary. The complete invocation and commit cost O(B+v), with
O(B+v+h+log B) additional transient storage in a fixed physical inventory.

Admitted means that each real/imaginary component passes the inherited
scratch-policy microstates. SCALE executes NEG then exact HALF; ADD copies
the source to zero scratch, halves scratch, adds it to the current target
and clears scratch. Require representable signed intermediate values and
exact halves. A representable endpoint alone does not imply admission.
This proof does not derive the complete caller's precision reserve.

## 2. The actual common chart

`selected_binding.py` authenticates the selected archive and four member
byte hashes, then checks the embedded provider, forward-stream hash and
literal rows. Call 0 has stage=replica=pair=time=0, forward orientation,
provider gauge44, and 704 distinct live owner families. Its first rows are

    raw0: phase zero_frame_precondition
    raw1: SCALE L119 by -1/2, frame0
    raw2: ADD L119 += L169/2, frame0.

Raw0 is a section marker. The owner entries are [119,[1,0,7]] and
[169,[1,0,57]], respectively. They select Y data ports 7 and 57, whose
labels are 21 and 56. The canonical word gives native start frame zero
for both roles, and its frame-zero basis is empty.

Use the data route rho(q,stage), rather than the helper or idle chart.
The authenticated pure definition returns I73 when stage=0. For both
ports, the stored stage-zero translations are zero. The retained phase
functions also give

    desired(q,-1,'Y') = stage_frame(q,0,'0') = [].

These empty operator products give the exact identity, including global
phase. The retained source interprets its Fourier multipliers as exact
Z4 polynomials and fixes the uniform vector; equal Pauli supports alone
would not suffice. PR1969 already supplied the data-phase/transport
analysis. I use that analysis to discharge this particular prefix premise.

For clarity, write a whole-family entrance chart as

    (C_i v)(d) = E_i(d) P_d^-1 v(d sigma_i^-1).

At native target label g_t, set d=g_t sigma_t. Then

    (C_t^-1 C_s v)(g_t)
      = P_d E_t(d)^-1 E_s(d) P_d^-1
        v(g_t sigma_t sigma_s^-1).

The two selected roles have sigma_t=sigma_s=I and E_t=E_s=I.
Their whole-family charts therefore agree, with common action P_d^-1
at label d. Each P_d permutes address coordinates and acts identically on
the two full packets, including their tensor-lifted columns and spectators.
The two scalar operations commute with that common linear permutation.
Thus their untransported pointwise execution refines the selected entrance
semantics. Native frame0 alone would not establish this conclusion.

James Chang's PR2370 states this common-chart premise in
`Current1094Row2AddReference.lean`. I supply its selected source instance
and physical row interpretation here. I neither modify nor compile that
Lean proposal.

The negative control matters: the idle bases B21 and B56 both pass their
orthogonal Gram checks, but B21 B56^-1 sends e0 to the mask47, rather than
mask1. Substituting those bases changes the family alignment. The checker
rejects this substitution, a nonzero entrance translation, an off-stage
call, a changed frame and changed/duplicate owners.

## 3. Moving the prefix before the cover loop

For each cover label d, let A_d be the complete entrance chart and Z_d
the exit chart on that invocation's 704 owner packets. Write P for raw1
and raw2 together, and S_d for the remaining local word. Define

    H_d = A_d^-1 P A_d,
    R_d = Z_d S_d A_d,
    L_d = Z_d S_d P A_d = R_d H_d.

This factorization does not require entrance and exit charts to agree.
The tail R_d retains its entry and exit routines and starts its local
arithmetic at raw3.

Let Omega_d consist of the 704 original owner packets for cover label d.
I retain the selected route certificate that each sigma_i belongs to
O(73,2); this package does not independently replay the full helper-chart
census. Each local role i has its own family owner F_i and route
d -> d sigma_i^-1. If Omega_d and Omega_e intersect, the family labels
first force the same role i because the 704 owners are distinct. Right
multiplication by sigma_i^-1 is bijective, so equality of cover labels
forces d=e. Hence these packet supports are disjoint for distinct d.
The inherited private-work contract requires fresh local input and
completed cleanup; shared physical work tapes may then be reused between
invocations without carrying state across their mathematical actions.

For d!=e, H_d commutes with R_e. Move each H_d across the other labels'
tails, keeping the order within its own packet:

    L_dGamma ... L_d1
      = (R_dGamma ... R_d1) (H_dGamma ... H_d1).

Using section 2, I identify the right-hand prefix product with the single
whole-family update in section 1. The executor therefore needs no cover
enumeration or P_d application for this prefix. The subsequent tail
still needs its original gathered owner packets and adapters. This
factorization supplies an alternative call prefix, not a complete-call
speedup or a changed supplier invoice.

The selected execution schedule begins with this call's local cover
sweep, including its normalization wrappers, and completes it before the
next local invocation. The source compiler checks that first schedule
entry. I move the prefix within this one sweep, without reordering any
other selected invocation.

Each component encounters the same two scalar microstate sequences before
its own tail. On admitted inputs, moving disjoint packets preserves their
divisibility and signed-headroom conditions. Outside that domain, a new
schedule may encounter a different failing component first; I make no
failure-order equivalence claim for the whole selected call.

## 4. Physical execution and complete charges

The constructor authenticates source data and fixes W, the two owners and
the two recipes before receiving payload. It preallocates 64 parent scratch
tapes, the parent's protected output, PR3098's 128 scalar scratch tapes
and its protected output. This gives 194 owned tapes, independent of h,N.
The inherited pool specializes allocation sites, and the tests seal Tape
and Arena constructors during invocation. Runtime selectors use encoded
Counts and sequential bit reads; Python integer decoding appears only in
source compilation and test oracles.

The parent computes the encoded extent v=2hN, scans the complete B-bit
bank and copies families119/169 into separate v-bit leases. It validates
and traverses the other bits without interpreting their coefficients.
It rewinds the borrowed bank, runs the first scalar with borrowed headers
under a suspended parent scope, copies and clears the scalar return, then
runs the second scalar on the updated target and original source. It
again consumes the scalar return. The second bank scan substitutes the
updated family119 and copies every other family in order. The parent
clears its leases, erases owned markers and returns the protected bank at
its local origin.

The separate commit operation consumes the caller's old owned bank,
copies the complete protected result into it, rewinds the bank and clears
the result and its marker. A caller may also consume the protected return
through its own charged ownership protocol. Reuse requires consumption.
For a named CoefficientDomainError, the parent clears partial owned work
and returns no bank; it preserves the complete borrowed input and headers.
The recovery claim covers these arithmetic errors, not interrupted or
malformed-tape execution.

A fixed number of full-bank scans, rewinds, copies and erasures costs O(B).
Each family's countdown has amortized O(v+log v)=O(v) traffic. The initial
binary product uses O(log h (log h+log N)) operations, which O(hN) absorbs
for h>=2,N>=1. PR3098 supplies O((I+1)v) for each scalar recipe, including
word loads, arithmetic, zero-scratch initialization, restoration checks
and disposal. With fixed recipe lengths I1=2 and I2=4, the total is

    O(B + (I1+I2+2)v) = O(B+v).

The borrowed bank and replacement coexist before commit. The parent also
holds a fixed number of whole-family streams; the scalar engine uses
O(h+log N) local work and one v-bit return. Thus additional transient
storage is O(B+v+h+log B). For retained physical backing, charge each fixed
role's historical maximum extent, including previous larger invocations;
erasure does not shrink a tape's historical backing.

I do not insert that temporary bank into PR2287's old V+720v envelope.
Commit and close the prefix work before any recursive tail cut. Then the
tail begins with the same number of original families and the same U,
compact fields and child widths. A caller that carries the temporary bank
across such a cut must add a parked-B charge.

## 5. Evidence and limits

The exact cover size is

    Gamma = 2^1296 product_(i=1)^36 (2^(2i)-1),
    2^2627 < Gamma < 2^2628.

I retain PR2287's group count and row-stock proof. `selected_extent`
multiplies encoded U and b by that compiled constant. The extent check
constructs the 2632-bit encoding of 15 Gamma and allocates no cover
payload. The all-N execution argument above instantiates this extent.

The physical tests instead run complete W=14336 banks at generic finite
N=1 and N=3, with 17/18-bit components. They compare all bank bits with an
integer oracle, including arbitrary signed values in unselected families.
Those banks are tests of the generic physical primitive; neither has the
full selected Gamma extent. Further checks exercise later-field NEG
overflow and inexact HALF, reuse after failure, protected-output rejection,
and caller-owned commit with live encoded headers. A small disjoint-route
model checks prefix factorization and fails under a nonbijective route or
unequal operand charts. It is not an O(73,2) payload replay.

Reviewers still need to assess the written all-size proof and inherited
physical framework. I have not run the complete cover tail, selected cold
replay, Lean or a multiplication theorem. I leave the selected frontier
and its conditional status unchanged.
