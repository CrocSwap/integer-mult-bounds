# A common invariant entrance for the fixed lifting transform

Use Gaussian integers with real coordinates interleaved by binary address.
The pair map, floor convention, stage order and forward period lattice
Gamma_r are those of Tekalign's PR3025/3033 and Nick Petalas's PR3035/3037.
Their retained written theorem is in vendor/period-PROOF.md. This note does
not claim a new proof of that theorem. Let C_j be the ideal positive pair
transform on address bit j, U=C_(r-1)...C_0, and L the literal floor word.
Let E_j be the integral vectors whose paired differences on bit j belong
to 2 Z[i]. The inherited description is

    Gamma = {x : C_(j-1)...C_0 x belongs to E_j for every j}.

Every condition makes the following stage integral. On Gamma, L(x)=Ux,
because both floor divisions at each pair are exact. All statements below
hold for every finite r>=1; displayed indices are finite computations for
r=1..7, not a proved all-rank index formula.

## The maximal common invariant lattice

The C_j commute, since they act on different tensor factors. Direct pair
algebra gives C_j^2=X_j, the address XOR on bit j, and C_j^-1=X_j C_j.
Thus U^2=X_all, the complement of all r address bits. Every address XOR
preserves Gamma: it commutes with the ideal prefixes and only permutes
the pair tests, possibly changing the sign of a difference. In particular

    U^2 Gamma = Gamma.

Define Lambda=Gamma intersect U Gamma. Then

    U Lambda = U Gamma intersect U^2 Gamma = Lambda.

Any U-invariant subgroup K contained in Gamma is contained in U Gamma
as well, hence in Lambda. The same conclusion follows from the weaker
requirement U K subset K for a full-rank finite-index lattice: det_R(U)=1,
so the inclusion has index one. Thus Lambda is the largest U-invariant
sublattice inside the fixed forward period lattice. It minimizes index
among this specified class, rather than among every exact nonlinear
implementation or every possible exactness set.

L^-1 agrees with U^-1 on U Gamma, by bijectivity of the fixed word and
L=U on Gamma. Consequently both completed directions are ideal linear
maps on Lambda and preserve Lambda. Intermediate floor-word states need
not belong to Lambda; only the declared completed-call boundary has this
contract.

## Why the reverse-order intersection computes it

The local even-difference lattice E_j is preserved in both directions by
C_j, because its output pair difference is i times its input difference.
The negative stage C_j^-1=X_j C_j has the same parity-domain tests as the
positive stage; address XORs commute with every other stage and preserve
all those tests.

If x belongs to Gamma and y=Ux, unwinding ideal stages in reverse order
starts at y and encounters exactly the preceding integral even-difference
states. Conversely, reversing this unwind constructs x in Gamma. Replacing
each negative stage by its positive stage merely introduces address XORs,
which do not change membership. Therefore U Gamma is exactly the
prefix-parity lattice for order r-1,...,0. This also agrees with Arham
Tahir's PR3046 inverse-image/permutation result, without importing its
implementation or requiring another HNF.

The primary checker intersects both prefix systems. For one parity test
let J be its odd basis columns. If J is nonempty, choose p in J, subtract
column p from every other column in J and double column p. The resulting
columns form exactly the parity kernel: the change has determinant two,
every new column is even under the test, and both the old lattice kernel
and the new lattice have index two. Applying that same column change to
the original basis and its current ideal image preserves their relation.
Later integer combinations retain earlier tests. Starting from Z^(2^(r+1))
therefore proves that counting nontrivial restrictions gives the exact
base-two lattice index. This is an exact intersection algorithm, not a
sampling inference from passing basis vectors.

At rank seven the forward restrictions are 128,64,48,32,28,22,21 (343
bits). The reverse order adds 15,15,9,9,5,5,0, yielding index 2^401.
The independent checker computes the image of the rational congruence
matrix modulo a power of two and obtains the same index by a different
method. Its quotient factors are

    (Z/2)^116 x (Z/4)^91 x (Z/8)^29 x (Z/16)^4.

The finite result is conditional on the inherited literal word and
prefix-period model. No proof assistant kernel is used.

## Caller closure and a complete local macro

Gamma is a Gaussian-integer module: every prefix is complex-linear and
every pair test asks membership in 2 Z[i]. Its image and intersection
are also modules. Thus Lambda is closed under whole-array ADD with any
Gaussian-integer coefficient, global negation and global multiplication
by i. Address XORs preserve it. On arbitrary lattice-valued dirty arrays
x,y the three-step word

    x := L(x);  y := y+x;  x := L^-1(x)

has exact boundary (x,y)->(x,y+Ux). It restores x literally, allocates no
helper, and charges two completed transforms and one complete array ADD.
No source read may observe x during its temporary transform. The initial
values are arbitrary within Lambda, not arbitrary unrestricted integers.
This macro is not a claimed improvement over an existing admitted child.

The closure has decisive limits. Let one denote the constant complex
array of ones. Every ideal/lifted stage fixes it, so one belongs to Lambda.
Let S_j multiply addresses with bit j=1 by i. Earlier forward stages
k<j see equal pairs and fix S_j one. At stage j the paired inputs are
1,i, whose real and imaginary differences are odd. Therefore

    S_j one is not in Gamma, and hence not in Lambda.

This is a linear address-dependent Gaussian phase, not merely a failure
under an unrestricted single-address phase. The local lattice cannot be
assumed compatible with all Gaussian monomial wrappers. This witness does
not prove that no smaller wrapper-invariant lattice exists, nor that every
particular P104 wrapper needs this phase.

Likewise a single-coordinate update by one leaves the lattice: it creates
an odd difference already at that coordinate's first paired stage. Whole
array ADD must not be reinterpreted as a free arbitrary coordinate update.
Division by four maps a lattice-valued source back into Lambda exactly
on the subdomain 4 Lambda. Even an integral quotient can leave Lambda:
4e_a belongs to the rank-one Lambda, but its quarter e_a does not. Every
quarter ADD thus needs an actual divisibility/closure proof or an adapter.
No nonzero integral lattice is closed under indefinitely repeated division
by four, since a nonzero integer coordinate eventually becomes fractional.

## Complete-cost decision

An index of 2^401 describes a restriction on admissible states. It is not
a measurement of physical stored bits, a precision saving, or a free
encoder for arbitrary inputs. A basis encoder B changes a physical U call
to logical B^-1 U B; source-to-literal correspondence or an intertwining
adapter must be proved and paid. The scalar input period grid 16 Z^256
has index 2^1024 at rank seven and lies inside Lambda, but the index
difference 623 is not a demonstrated 623-bit storage reduction.

For any proposed q-call consumer define R_j as the *complete* cost removed
at call j (the old residue extraction/uncomputation, nonlinear correction,
extra ideal pass or recombination actually eliminated by the new word).
Let E,D be initial encoding and final decoding, A_j the needed phase,
dyadic-ADD or other boundary adapters, and Delta_j all added backend,
precision, live-bank, copying, movement and restoration charges relative
to the old completed call. For nonnegative exact costs in one common work
model, the budget for a claimed net gain is

    E + D + sum_j (A_j + Delta_j) < sum_j R_j.

For exact compared costs the inequality is necessary and sufficient for
that fixed finite word. With lower bounds on the added costs and upper
bounds on the removed costs, it is only a necessary screen. With upper
bounds on the added costs and lower bounds on the removed costs, it is
a sufficient screen. Under a uniform per-call net saving S>0 and a
one-time cost C, the corresponding threshold is q*S>C; this does not
supply S, C or a legal consumer. All recursive children, private/borrowed
storage and exact inverse work remain included in those quantities.

Here phase and quarter-ADD closure already fail on explicit inputs, and
no complete codec/intertwining/backend bill has been constructed. Stop at
the local common-interface lemma and these witnesses. There is no new
recursive moment, admitted supplier, selected-frontier change or kappa.

The period-domain restriction matters even at rank one. Pair exactness
requires only that the real and imaginary difference parities agree,
equivalently a-b belongs to (1+i) Z[i]. This index-two lattice is
C-invariant and is larger than Gamma_1 (index four). For example
(a,b)=(1+i,0) and its whole C orbit are exact but outside Gamma_1.
Thus the phase witness above rejects closure of the proposed period
interface, not every exact lifting interface; it is not by itself an
output-error witness. Exploring a larger integral-prefix exactness
domain with a specified consumer is a separate next question.
