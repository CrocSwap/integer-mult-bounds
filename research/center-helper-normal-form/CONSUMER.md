# An exact two-call controller for a homogeneous three-step query chain

**Conditional controller identity; no physical native realization or higher K.**
This is an exact consumer for a specified three-field offer. The normalized
PR4694 scalar chains alone do not prove that offer's physical hypothesis.

Let Q be a symmetric invertible operator with Q^4=I and let P=Q^2 be an
available monomial involution. A tensor Gaussian C^tensor(f) has these
properties under the retained phase convention. On three arbitrary independent
fields assume an oracle

    U = [[I,Q,0],[0,I,Q],[0,0,I]].

Its actual raw inverse transpose is

    U^-T = [[I,0,0],[-Q,I,0],[P,-Q,I]].

The bottom-left term is required. Define free matrices with only ordinary
scalar and Pauli entries:

    D = diag(P,I,P),             E = I - P E_31,
    L = [[I,0,0],[0,-P,0],[I,0,P]],
    R = [[0,I,I],[I,0,0],[0,0,P]].

Then the exact identity is

    L U E D U^-T D R = diag(Q,Q,I).

The chronological program is R, D, the raw-dual call, D, E, the forward
call, L. Every boundary is invertible and uses only scalar ADDs, signs,
field exchanges and P. For example an ADD with coefficient P can conjugate
its source by P, perform the ordinary ADD, then restore the source by P;
no Gaussian query or zero-only input is hidden in the notation.

To prove the identity, use

    E D U^-T D = I - Q^-1 (E_21+E_32).

Indeed the D conjugation changes -Q on the two adjacent lower edges to
-Q^-1 and leaves the P long-root term. E removes that term exactly. Multiplying
by U gives

    [[0,Q,0],[-Q^-1,0,Q],[0,-Q^-1,I]].

Direct multiplication by R and L gives diag(Q,Q,I), using P^2=I and
P Q^-1=Q. These are block-operator identities at every width, not numerical
specializations or tensor powers of a sum. Symmetry Q^T=Q is needed to identify
the raw dual as written.

consumer.py verifies every coefficient in the exact cyclic group ring
Z[q]/(q^4-1), checks the actual raw inverse transpose, and includes separate
dense rational specializations. It rejects a wrong long-root sign, an omitted
correction, an omitted raw-dual quadratic term, missing Pauli conjugation,
and dropping the order-four hypothesis.

## Conditional transverse and price ledger

Suppose the actual forward provider also multiplies all three fields by the
same fresh rank-b Gaussian D_s, commuting with Q and these boundaries. Suppose
the actual raw-dual provider has the corresponding identical inverse Gaussian
on all three fields, converted to a positive one by its true Pauli normalizer.
Two disjoint transverse stages then give targets

    two rank-(2b+1) jobs and one rank-2b job.

The third field has its central query restored; it still receives the
transverse Gaussian. If each full invocation has autonomous helper profile H
and complete paid profile P_local, the complete moment for this gadget is

    2 H_t + 2 (2b+1)^t + (2b)^t - 2 P_local,t,   t=1-C.

Writing the local rank deficit relative to three rank-b main jobs as
E=P_local,1-H_1-3b, its rank surplus at C=0 is 2-2E. This is a conditional
bookkeeping formula, not an invoice assigned to PR4694 or a new exponent.

## The actual missing interface

The real retained-center word has different charts on its helper, center
and Y directions. Its source helper has rank nine, its retained center moves
from an eight-dimensional chart to the empty chart, and the terminal Y
combination spans different eight-dimensional charts. A scalar Jordan chain
therefore does not supply U(Q) with a common commuting transverse multiplier.

The next concrete test is a costed embedding of one of the eight recorded
chains into this homogeneous offer, with every chart conversion and the
remaining R_X data terms retained. Only after that succeeds may the formula
above be used with actual paid and target profiles. The package does not
claim a free full Jordan basis, independent center credit, a profitable native
consumer or a higher K.

Prepared for Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.
Credit the PR4694 coupled interface, Cinna Davis's controller lineage, Cao Yifan,
zxv, Jacob Alan Sussman and retained native/phase/precision authors. No priority
claim is made for elementary block elimination identities.
