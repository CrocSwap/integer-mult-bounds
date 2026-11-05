# On-path fixed-width recursive shape production

This proposed physical contract specializes the actual fixed-w stopped
recursion in PR5829 and DELAYED-COVER-BRIDGE section 8. It does not introduce
a changing-width recursion to obtain different H values. Generic arithmetic,
the whole-high address identity, the continuation stack and the codec are
predecessor methods; the intended new edge is their literal on-path recursive
connection with actual frame-owned descriptors.

Compile L >= 2, an odd prime q and N >= 1. For the actual cover,
L=B*|GL_N(F_q)|. Runtime supplies canonical physical binary w,A0,R0 and a
readonly unary remaining-depth d=D-1. Put b=q^(N*N) and H=b^(w-1).
The source specialization is

    A0=T*(L*H)^d, R0=H*R_body, T,R_body >= 1.

H is generated physically once from the supplied w, using a fixed-carry
multiplier by the compile-time constant b. It is then readonly until the
complete invocation returns. Neither H nor any child A/R grant is supplied
as a precomputed list. The supplied w and unary depth are root descriptors;
this task does not yet produce w=ceil(e^(3/1000)) or the stopping depth from e.

At each actual node j, the live descriptors and complete stream have

    A_j=T*(L*H)^(d-j), R_j=H^(j+1)*R_body,
    V_j=L*A_j*R_j=V0/L^j.

Immediately before CALL, the retained literal shape producer computes
A_child=A_j/(L*H), R_child=H*R_j from those live physical headers.
The producer's temporary guides are erased. The grants are copied into
fixed transfer relays and physically retired before suspension. The parent
headers, banks and local scratch are parked by the physical stack. The
child is initialized from the relays, which are erased before reentry.
Thus grandchildren are produced from the suspended child's own descriptors.

The dispatcher has one finite PC, physical CALL/RETURN phase bits and no
host recursion, decoded descriptors, callback interpretation or runtime
tape selection. A completed child output is copied to the separate output
relay before child retirement and pop. After pop it replaces only the
specified owned parent bank. Parent source/header bytes and heads are restored.

The first fixed grammar has two statically named child sites, banks 0 and 1.
At remaining depth zero its literal leaf complements bank 0, then the node
merges all L banks. This tests complete recursive address and ownership
semantics; it is not a Gaussian leaf or the final compiled BIT template.
The table can subsequently be parameterized by a fixed finite list of child
sites without adding runtime tape indices or changing the descriptor proof.

The payload bank count is K=max(16,L+11). Nine additional fixed tapes hold
the physical control stack, phase descriptor, four relays, unary depth,
readonly root width and generated H. Width-generation scratch reuses initially
empty payload scratch; no tape count depends on depth, H or input length.

Local generation/router/stack/return work is bounded by C_template*V_j on
this source domain, with no forced claim of 94V for the whole tree.
Consequently the total bill is the sum over actual node/edge occurrences.
For c fixed recursive sites the recurrence is

    T_d(V) <= c*T_(d-1)(V/L)+C_template*V.

An active chain has local space bounded by a geometric sum of V/L^j,
plus charged root descriptors and persistent tape backing. Sequential sibling
calls reuse the same suffix, so tape count and maximum backing do not grow
with the number of completed calls. Exact constants must be derived from
the emitted table rather than inferred from a small fixture.

The intended actual two-level check is B=2,N=1,q=3,w=2,L=4,H=3,D=3:

    (A,R,V)=(144,3,1728) -> (12,9,432) -> (1,27,108).

All high coordinates and ancestors remain in the R field. Matching volumes
alone is insufficient: the proof and observer must check the complete
address identity a_parent=(a_child*L+l_child)*H+h_child and return its inverse.

Numerical ancestor weights, generation of w/depth from the outer integer
input, final-template route/fallback macros, Gaussian children and precision
remain explicit separate interfaces. This contract does not claim to generate
those missing inputs, close the full production theorem or improve kappa.
