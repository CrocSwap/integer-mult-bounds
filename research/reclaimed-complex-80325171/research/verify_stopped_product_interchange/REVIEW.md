# Independent review of PR104's stopped product-ring bit interface

Date: 2026-10-08 UTC. Exact reviewed head:
`854ba7dca98651eab2050402384e1a7784534f0a` of
[PR104](https://github.com/CrocSwap/integer-mult-bounds/pull/104).
The source repository is `icekylinx/integer-mult-bounds`.

## Verdict

**The new bit-interface argument agrees with the retained assumptions. No
mathematical gap was identified in the changed opposite-bank factorization,
atom implementation, stopped recurrence, ordinary endpoint conversion, or
associated row-stock interface.** The supported ordinary bit saving is

    a_b = 803380799 / 10^13 = 0.0000803380799.

This is a new proved conditional interface, not merely the earlier increasing
one-run compiler with a better histogram, and not a strengthened assumption that
arbitrary address reversal is free. The old increasing-run/shared-basis no-go
therefore does not refute it. The outer wrapper has a fixed factor of two; it
must remain outside the whole coarse recursion, as the actual source specifies.

This review does not establish the separate rational-center complex interface,
full scalar-producer realization, analytic transfer, or final claimed global
saving `194869/2500000000`. Those require their own checks. No upstream program,
large producer, Lean/Covering run, or full scientific replay was executed.
The independently diagnosed stale Makefile provenance pin is not used as a
mathematical objection.

## Exact sources and scope

The central inspector materialized exact-head files under
`research/pr_watch_2316/PR104/` and verified the eleven certificate-bound hashes.
This review read the actual argument, not just the certificate's numbers:

- `notes/stopped-product-factorization.tex`, lines 1–81: ring, global convention,
  simultaneous basis, and whole-involution factorization; lines 83–112: list.
- `notes/stopped-product-interface.tex`, lines 1–29: adapters/remainders;
  31–53: uniform two-parameter recurrence; 55–95: ordinary wrapper and rows.
- `notes/stopped-product-assembly.tex`, lines 1–27: simultaneous row stock.
- `upstream/build/sections/02-streams.tex`, lines 124–196: the actual retained
  ordered-affine streaming lemma, including proof of uniformity in atom width.
- `notes/batched-algorithms.tex` and `notes/projector-batching.tex`: retained
  componentwise/spectator uses of that lemma.
- Exact selected bit input and stopped-product network certificates.

The cached PR36 files `copied-centers-bit.tex`, `copied-centers-lemma.tex`,
`partial-swap-construction.tex`, and `batched-bit-rows.tex` were read to check
what is inherited: both copied-center orientations, ordinary leaf saving,
complete spectators, finite role volumes, row borrowing, and fixed tapes.
The hash manifest accompanying this review records all exact104 files used.

## 1. Simultaneous generic basis is sufficient

For every fixed rational idempotent P of rank r and every k <= r, the leading
k-square determinant of U P U^-1 is a rational function on GL_m. It is not the
zero function: choose a basis carrying P to diag(I_r,0). There are only finitely
many projectors in the selected fixed finite network. Clearing denominators,
taking their finite product, and using irreducibility of GL_m proves a common
nonempty rational open set. Rational enumeration terminates. This does not
require the projectors to commute, share eigenvectors, or be triangular in the
same basis.

For P in the chosen basis, M=P C_m has every northeast i-by-j corner of rank
min(i,j,r): reverse the columns and use the nonsingular leading square of size
min(i,j,r), while rank(P)=r supplies the upper bound. Consequently rightmost-pivot
elimination using only lower row and lower column operations yields

    L M R = E F^t,
    E=(e_1,...,e_r), F=(e_m,...,e_(m-r+1)).

Both L and R, as well as their inverses, are lower triangular in their respective
physical bank orders. The pivots form an anti-diagonal contiguous run. This is
exactly the departure from the previous increasing-run obstruction.

Choosing this basis changes the finite address labels of every frame together.
It is not an uncharged tape transformation. Original full interchange is
invariant under applying the same U to both banks; the subsequent common
opposite-bank conjugation changes its endpoint to F_n. Common-frame scalar
identities and nested projector identities are preserved.

## 2. The whole involution is normalized, not only its cross corner

For one atom per formal coordinate, set

    D'_P = [(I-P), P C; C P, C(I-P)C],
    Q = diag(L,R^-1), g = Q D'_P Q^-1.

The rank of g-I is r (the address characteristic is odd), and its upper-right
block is E F^t of rank r. Hence the stated factorization

    g-I = [E;B] [A,F^t]

exists. Idempotence of the involution gives AE+F^t B=-2I_r. For the actual

    K = -(B+F)E^t + F A(I-EE^t),

one obtains directly

    KE=-B-F,       F^tK=A+E^t.

For S=[I,0;K,I], multiplying the whole blocks gives

    S g S^-1 = [I-EE^t, EF^t; FE^t, I-FF^t].

This fixes every unselected coordinate and exchanges the first r coordinates
of the first physical bank with the last r of the second in opposite order.
The diagonal complements and lower-left block have not been discarded.

For f atoms per formal coordinate, use Q_f with I_f and S_f with K tensor C_f.
The same calculation lifts with E tensor I_f, F tensor C_f, A tensor I_f, and
B tensor C_f. On the two selected physical intervals,

    C_r tensor C_f = C_(r f).

The middle map is therefore exactly one F_(r f) child, not r separate children,
not an ordinary child requiring a hidden reversal, and not a gathered block.
Both intervals are contiguous. All other coordinates are complete spectators.

The construction always names the earlier physical interval the head. If the
originally named banks occur in the other order, rename the two chunks first;
F_n itself is symmetric under this naming swap. Every frame within that
invocation uses the same diag(I,C_n) convention. This does not require freely
exchanging physical banks or alternating the convention within a network.
Forward and reverse/complementary frame changes use the same involution; their
adapter inverses remain lower triangular. The copied-center source confirms
that these are the two invocation orientations actually required.

## 3. Ring specialization and uniform atom cost

The important domain distinction is

    one atom = Z/q^w Z,
    f atoms = (Z/q^w Z)^f.

One atom is not an F_q vector of w independently translated digits. Nor is the
whole f-atom field treated as one cyclic Z/q^(wf) field. Intra-atom carries are
allowed; inter-atom carries are absent. Reversing the f atoms commutes with
componentwise multiplication by fixed rational coefficients.

After fixing the finite rational tables, choose q to avoid all required
nonzero numerators, denominators, and pivots. Thus every required diagonal
scalar is a unit modulo q^w for every w. One proves matrix identities over Q
and specializes them; no unsupported field-rank argument is made over the
zero-divisor ring Z/q^w Z. The oddness of q also preserves the involution's
characteristic-zero normalization.

The inherited lemma in `02-streams.tex:124–196` is exactly strong enough:
for a fixed finite rational coefficient table and a fixed number of O(w)-digit
controls earlier than a target of range q^w, a target shift or unit scaling
costs O(V), with arbitrary intervening spectators and suffix records. Its proof
splits a cyclic target fiber, computes offsets in w^O(1) tape operations, and
charges that preparation to q^w complete target positions. Fixed integer
scalings use a fixed number of streams; rational units use their inverses and
possibly a paid negation. All counters and local cleanup are included. The
implicit constant is independent of w; no unit-cost arithmetic is assumed.

Each new atom update meets these hypotheses:

- Intrabank lower factors use at most m fixed controls at the same atom offset.
  Descending target-field order keeps all earlier controls unchanged.
- In a cross shear, D_(i,t) is controlled by H_(j,f-1-t). Even though atom index
  order is reversed, every head atom physically precedes every tail atom.
- Each pass describes only the selected target and fixed controls; other
  intervals collapse into complete spectator fields. There are O(f) separate
  passes per fixed matrix, not one uncharged f-atom operation.

Since m is fixed, the full adapter bill is O(V n)=O(V e/w). This explicitly paid
factor is central to the argument. Had the proof used F_q^w digitwise updates
while claiming the cyclic lemma for free, or treated all f atoms as one update,
there would be a different obligation. The actual source does neither.

Descriptors can be computed in polynomial time in the lengths, per pass. As in
the retained scheduler, complete root digit ranges remain as spectators and
no parked ancestor is scanned. Polynomial descriptor work is absorbed into
O(V) for each pass. O(n) passes use a fixed tape set, reused sequentially.

## 4. Child closure, peeling and ordinary leaves

For n=m f+delta with delta<m, the first delta head atoms and last delta tail
atoms are paired in reverse order. Their old ordinary width-w interchanges
produce precisely those pairs of F_n. The remaining two intervals are
contiguous and carry F_(m f). At n<m, at most m ordinary atom-pair calls finish
F_n directly. These calls preserve every inactive digit and complete spectator.

The old ordinary interface acts on a numerical q^w atom range after padding
both chunk ranges to binary powers, with volume inflation below four and
binary width O(w). It need not use the new fixed q internally. This padding is
removed after each completed old call. It is a fixed cost within the remainder
or leaf toll, not an accumulating padding factor on the coarse recursion.

The complete finite list independently reconstructed from the selected h=23
input has width set 1,...,22,484,506, all below m=529. Its weighted rank is
75972299557 and its volume denominator is W=143617474. Copied-center rank-22
transforms and rank-one endpoint corrections are included. I did not reconstruct
the full scalar producer from scratch.

## 5. The stopped recurrence and ordinary wrapper

For fixed w throughout a coarse invocation, the source recurrence is

    T(n,w) <= sum_r (n_r/W) T(r floor(n/m),w)
              + C n + C w^(1-a_old),

with the latter term also bounding the n<m base range. Let tau=1-a_*.
The independent rational enclosure agrees with the certificate:

    a_* = 4019/50000000,
    1-mu_tau = 5833629405069796335513229037 /
               13595148940731587639987765177686687744 > 0,
    1-mu_1 = 33/1865162 > 0.

Strong induction yields A n + B n^tau w^(1-a_old), with A and B independent
of both n and w. The mu_1 gap pays the linear adapters; the mu_tau gap pays
the old remainder toll. Floors only decrease child arguments. No recurrence
constant is being hidden in the child multiplicities.

With product-ring arithmetic and C^2=I, the actual chronological sequence

    D <- D-H; F_n; D <- D+H; F_n; D <- H-D

maps (H,D) to (D,H). A direct symbolic calculation gives intermediate states
(H,D-H), (C(D-H),CH), (C(D-H),CD), (D,D-H), (D,H).
Thus both F_n calls are complete top-level calls, each reusing restored rows;
they are not inserted around every recursive child. The three lower updates
cost O(V n).

Taking theta=1/1000, w=ceil(e^theta), n=floor(e/w), and using the old ordinary
method on the fewer than w residual digits gives

    O(V [ e^(1-theta)
          + e^((1-theta)(1-a_*)+theta(1-a_old)) ]).

The remainder has a smaller exponent. The derived saving equals

    (1-theta)a_* + theta a_old = 803380799/10^13.

Since theta exceeds that saving, the paid adapter term is lower order. The
bounded exceptional widths use the old method. Numerical binary-to-radix-q
padding is performed once around the completed ordinary endpoint; its volume
factor is below q^2. Intermediate reversed endpoints are not used to remove
padding or justify ordinary high-digit borrowing.

## 6. Restored rows and width stock

The external reserve is a product of simultaneously needed stocks. The least
halving degrees independently checked are 16 for 529/506 (coarse), 9 for
575/529 (ordinary leaf), and 17 for 576/552 (complex). Every W has bitlength28.
The combined coefficient is

    16*28 + 9*28 + 17*28 = 1176,
    4000 - (51/25)*1176 = 40024/25 > 0.

Every coarse or complex split leaves its factors of the ordinary stock available
at the leaf/remainder. Sequential copies and both outer F_n calls reuse restored
rows. They do not introduce extra independent coordinates. A conservative
global e bounds every depth, so the p^4000 reserve is sufficient under the
retained comparison e<=Cp and its eventual threshold.

For a standalone ordinary interface without supplied rows, borrow O(log e)
high digits as in the inherited ordinary construction, including enough product
stock for the coarse and old families. The outer completed operation is ordinary
interchange, so the high-digit construction applies; it is not asserted for a
bare reversed child. The reserve grows polynomially in e and hence requires
only O(log e) borrowed digits. One final padding and O(V log e) moves are
absorbed by the claimed exponent.

## 7. Independent bounded controls and limitations

`check.py` is original standard-library code and imports no upstream module.
It constructs a dimension-four family containing the two actual overlapping
triple exterior projectors for H=I-J/9, plus ranks1,2,3 coordinate projectors.
The exterior pair has trace([E_S,E_T]^2)=-3/8, so it is also a direct control
against accidental reliance on simultaneous triangularizability. A single
small rational basis satisfies all leading-minor conditions on the first
bounded attempt.

The check verifies lower L/R and inverse adapters, the rank factorization,
K identities, all blocks of the full involution, and contiguous reversed child
maps for atom counts1 and2. Full matrix identities are also reduced modulo
101^w for w=1,2,4. It tests the ordinary wrapper in three cyclic atoms, rebuilds
the rank histogram, independently encloses the exact coarse moment, and checks
all stop/row arithmetic. `CHECKS.json` and `check.log` record the passing run.
Runtime was below one second under the documented 60 CPU-second / 256 MiB caps.

These finite controls support the written proof but do not replace the general
proof or demonstrate the full dimension529 rational basis by explicit table.
The constructive generic-basis argument supplies existence for that finite
family. The retained analytic, exact-recovery, and machine-model assumptions
remain conditional as disclosed by the source. No extra new bit-side assumption
was needed in this review.
