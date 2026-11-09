# Chain-root caller on the G20 word

## 1. Statement
Let B be the binary reduction of the integral chain-nested root caller `chainroot.build([1]*9,[1]*9)`. Let W be the merged #5708 local word. Under the premises retained in section 6, B run with W at each LOCAL has the invoice of section 4 and admits ordinary BIT saving 0.00380058610508.

## 2. Orientation
W runs its main wires from frames (X,Y)=(8,7) to (1,0), with scalar endpoint X=x, Y=x+y. `check.py` proves over Q, on every port, with P_f the orthogonal projector of frame f:

    P(entry X)=I,  P(exit Y)=0,  P(exit X)+P(entry Y)=I,  P(exit X)P(entry Y)=0.

Write T_f for the paired-address reflection of frame f, so T_f²=1 and T's of nested frames commute. Telescoping along each wire gives the physical endpoint, replayed at both moduli:

    X' = T(exit X)T(entry X) x,   Y' = T(entry Y) y + T(entry X) x.

Put q=T(exit X) and D=T(entry Y). The port identities give T(entry X)=qD, so

    X' = D x,   Y' = D (y + q x).

This is the LOCAL form, with q central and q²=1.

So B runs on W directly, in the free variables q and D, with no reversal. The target job at role r is the reflection on its line and stage blocks, of rank q+7|S|.

**Reversal is unnecessary.** W's records go from frames (8,7) to (1,0), the opposite of the (1,0) to (8,7) orientation, but the form above is the same in both. #5708's own controller changed every local call to this orientation and left its main polynomial check unchanged, which is the merged precedent. As a cross-check, `check.py` also replays the time-reversed word B^r, both with LOCAL and IDLE_ONE read as literal inverses and after renaming D to D^-1. It has the same bill, and B followed by B^r is the identity. No involution is used on repeated body variables: a doubled idle rejects.

## 3. Reduction
Only ADD, SWAP, LOCAL, QUERY and IDLE_ONE occur in B. No SCALE or normalizer survives, so the binary caller has no address-dependent scalar. The integral caller's true inverse is replayed over Z[q,D^±1]/(q²−1), which gives the integral identity before reduction, so reduction modulo 2 never divides by 2. The integrality argument is the one for the forward caller: x_i−w_i=f_i and x+w=h_m give determinant ±1 bases, with ±1 pivots checked on every event.

## 4. Invoice
Targets are 18 local copies of 413 rank-8 and 2 rank-4 helpers, plus 111 fields of rank q+7|S| per role. Paid jobs are 18 local histograms {1:1281, 2:1338, 3:58, 4:57, 5:102, 6:10}, 111 rank-1 jobs per thin query, and 111 jobs of rank 7|S| per one-field idle:

    T = {1:111, 4:36, 8:7656, 15:222, 22:222, 29:222, 36:222, 43:222, 50:222, 57:222, 64:222, 127:111}
    P = {1:23391, 2:24084, 3:1044, 4:1026, 5:1836, 6:180, 7:222, 14:222, 21:222, 28:222, 35:222, 42:222, 49:222, 56:222}

Both histograms are recounted from the emitted stream. T−P mass is 753, and every rank-mass tail is non-negative, so the signed moment is strictly decreasing on the whole interval from the backend to 0.0039, and its zero is unique.

**The empty-field credit.** The 111 rank-1 targets are the empty field E, which carries only q and enters through the three thin queries. Like every target below the floor it is completed on its owner with the cost charged. The gain rests on this credit: without those targets the surplus is 642 and the raw crossing is in (0.0032366, 0.0032367), below #5708's 0.0035077 [`check.py`]. #5708 credits its helper fields the same way, so this is the model's convention, not a change to it. An outer use must feed E as an independent productive input. This is a review question.

## 5. Finite admission, fresh for this caller
**Tails.** Use the completion-tail form of #4416 and #4433 with paid splitting at c^v and same-owner completion at b^v, on the mixed compiler rules retained in #5708. At C=0.00380058610513, c=13, b=14, u=1/5, v=2048, two engines prove

    alpha=P_t/T_t < 1-2^-48,  gamma=P_(t+u)/(c^u T_t) < 31/32,  delta=9690 b/(c^C T_t) < 19/20,

with gamma<0.8965 and delta<0.9329, and 1/(1+v 2^-48)+4·2^(-v/32)<1. Separation is 13^64<14^63, and the shifted exit comparison 2·13^(64v)<=127^(63v) holds. The guards `c^64<b^63` and ambient<256 are #5708's, not part of #4433's statement, which asks 1<c<b<m. 13^k<14^(k-1) holds for every exponent k>=36, so the check does not depend on the exact exponent 64 as long as the true one is at least 36. The guards also hold uniformly on the approach interval [0.003507719059749, 0.0039].

**Compiler.** H0=809840675154182145 and H1=615573843471206695464073598626, with the strict integer inequalities at h=1/64.

**Axes.** The largest target is 127, but all 18 stages keep separate seven-axis blocks beside an eight-axis native interface, so the conservative working geometry has 134 axes. This form's guard is 134<256, and every dimension charge below uses 134. As a cross-check, the separate ambient-cap reading at power 768, cutoff 15, floor 16, gap 1e-10 passes at 134 axes for tested 0.00380058: log power 608, grid 29217, H=292170000000000, routes 408544560000 plus visible 182425128, below 10^12, owned bank 3048480, below 10^7. That reading is not used for the admitted value. Its visible bound keeps the inherited allowance of 10^7 per call, which is not recomputed for this native, so it is a cross-check only.

**Fees.** The base primitive count is 1059400502463 < 2^64: 373,764 scalar and header passes, 2,077,582,824 parking passes, 134,046 routes (all 18 calls' port routes, a pair per target and a pair per paid job), 434,997 records, dimension work for 53,337 queries, 10,944 matcher terms. The stream's cancellation-free majorant has 492 bits, inside the 1024-bit envelope. Each compiled instance receives its own 48 owned banks.

**Delayed cover.** The list is rebuilt for this caller. It consists of the 636 frames the word uses, the frame 506 and 508 matchers, 333 thin line jobs, 1776 idle-block jobs and 2220 main targets. Thin, idle and main projectors are port lines plus disjoint coordinate stage blocks, so they add no denominator. Over all frames and matchers, the denominators and determinants have only the prime 2. The odd prime q>max(2^60 N^5, 2^(2H)) is chosen after the compiled word, its matchers and their rank witnesses are fixed, with cover loss 1e-14 paid by 2^60·1e-14>256. No role-specific weight is created: the binary caller has no scalars, and only finished rank-one leaves are normalized against ancestor data.

**Levels.** With rho=1/100, L=0.00380058610511 and a_j=(1-rho)L+rho b_(j-1) on the strict 1e-15 grid, starting from #5708's completed backend:

    0.003507719059749 -> 0.003797657434656 -> 0.003800556818405 -> 0.003800585812242 -> 0.003800586102181 -> 0.003800586105080

Each step satisfies b_(j-1)<b_j<a_j<L<rho<1-a_j. Backend calls lower the finite level and coarse calls lower the atom count.

## 6. Scope and dependencies
Retained premises: all-column native operators, ROW and spectators, owned erasure, mixed-target compilation, ordinary normalizers and completed backends, precision, fixed tape and analytic recovery. They are the premises of #5708 and are not discharged. The completed backend is #5708's conditional one, whose interface is arbitrary widths and complete chunks with spectators kept and ROW stock restored. The per-source fees above are redone, but this package does not independently prove that interface.

Inputs from merged #5708 only: word, frames, matcher, invoice control, backend value. The caller is new. No native word, caller, admission or interval engine from #6726 or #6834 is an input; a price control on a second native histogram uses only literal numbers.

Not examined: route legality and stage-block placement remain inherited premises, as in #5708. The ambient-cap lemma is not used for the admitted value.

Outer use requires a Gaussian supplier and bill, and a productive input for E, and is not asserted here.
