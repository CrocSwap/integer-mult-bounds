# Released two-FULL/one-query problem: source inventory

Source inventory only, 2026-10-23. No t0 solver, search, native replay, compiler,
factory or external post was performed. The monitor authenticated Dillon's
release of original #4930 comment 19141406 and the new handoff at comment
19143357. Its exact local receipt is preserved as `source/RELEASE-MONITOR.json`.
The public theorem is `0e8a13c251a9be1029114cda8b4194f05f3a23ec`,
`research/coded-active-query-bound`; the actual code/normalizer scientific pin
is `4c0a359d88f22f05189d51f48387750b801a45d4`. The publication base is
`20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`. Eight exact source files and their
hashes are listed in `SOURCES.json`.

## Stock and actual operators

There are two main banks of 112 arbitrary independent owner fields each.
Each field has the fixed 17-axis address stock: one shared central axis q,
eight stage-1 axes and eight disjoint stage-3 axes, lifted to f columns, plus
all retained external row/spectator fields. There is no new anchor or extra
address axis. Two fresh source FULLs add two disjoint banks of 408 arbitrary
helper inputs: 816 helper owners, 1040 original main-plus-helper owners total.
An owned query bank is dependent workspace, not productive input credit.

Q is the actual central Gaussian, D1 and D3 the products on their respective
eight axes. They are invertible symmetric actual Gaussian operators; the
different axis factors commute. Q is not order two: its exact square is a
Pauli translation. Put G=D1 D3 Q, a rank-17 Gaussian on the complete stock.

The physical code is not the scalar matrix A. The source gives

    Cs[i,j] = A[i,j] Ki,s^-1 Kj,s,
    Fs = diag(Ds,Ds) L(Cs Q^-1).

The exact local K words, G_rows, Z_mask and compiled monomial wrappers are in
`NORMALIZERS.json`. Embed their nine local coordinates as q plus the selected
stage's eight coordinates, with the other stage as identity. These are stored
matrix ROWS; replacing them by columns changes the operator. The K maps are
real signed orthogonal permutations, commuting with Ds Q but not generally
with Q or Ds separately. Their all-column lift retains the accumulated phase;
owner coefficients are applied once, not tensor-powered with the address map.

## Released sufficient template and all four conditions

All controls are 112-by-112 owner-operator matrices on this same field width.
They are not necessarily single Clifford operators. Seek an invertible t0
such that each of the following has an explicit physically free program AND
an explicit program for its inverse:

| Control | Definition | Mathematical inverse, in exact order |
|---|---|---|
| R1 | t0 | t0^-1 |
| R2 | S0=Q^-1 t0 Q | Q^-1 t0^-1 Q |
| R3 | t=D3 t0 D3^-1 | D3 t0^-1 D3^-1 |
| R4 | K=Q^-1 C3 t C1 Q^-1 | Q C1^-1 t^-1 C3^-1 Q |

The released middle operator is

    J(t0) = [[-t0 C1, t0 Q], [0, -C3 S0]].

Under the source identities, the handoff states

    M = F3 J(t0) F1
      = [[0,t],[-K,0]] diag(G,G).

The cancellation uses the actual source relations [C1,D1 Q]=0 and
[C3,D3 Q]=0, plus [C1,D3]=0 from the disjoint fresh-axis embedding.
For example the upper-left block of J F1 is
t0(-C1 D1+D1 Q C1 Q^-1)=0; the lower-right block of F3 J F1 cancels
by S0=Q^-1 t0 Q. No commutation of t0 with either Gaussian is assumed.

Writing S=[[0,t],[-K,0]], its full main endpoint is

    Xout=t G Yin,       Yout=-K G Xin.

There is no main/helper leakage in the inherited FULL endpoint. The helpers
retain their autonomous source transformations. If the four explicit free
program/inverse requirements hold, the post-map

    S^-1 = [[0,-K^-1],[t^-1,0]]

would return the main outputs to diag(G,G) on the 224 original inputs, with
the two banks routed back to their declared owners. Invertibility alone is
not a physical implementation of this post-map.

The mathematical raw inverse transpose is, using transpose rather than
Hermitian adjoint,

    M^-T = S^-T diag(G^-1,G^-1),
    S^-T = [[0,t^-T],[-K^-T,0]].

An actual reversed/transpose tape must preserve the source raw-dual convention,
all phases and owned-buffer lifecycles. For a source backward FULL the retained
normalization is X-only Q^2 conjugation, with D_s^2 output corrections; the
older Y-only convention cannot be substituted. The formulas here do not emit
that tape or automatically provide physical transpose programs for a generic
algebraic unit. Returning inverse-Gaussian jobs to positive jobs likewise
requires the actual Pauli maps, not an order-two assumption.

## One paid query and chart contacts

A direct conditional implementation of J first obtains QY in 112 owned query
fields, then forms -t0 C1 X+t0(QY) and -C3 S0 Y using the required free programs.
All reads of the old Y must finish before Y is overwritten. This explains the
one bank of 112 H1 queries. The query bank is cleared/reset only under the
retained owned-stream rules. A concrete safe COPY/query/use/reset route has
112 query fields; additional scratch for t0 or the free recodings must be
separately allocated and charged. No helper is scratch and no copied stream
earns independent output credit. The handoff does not publish a full emitter.

Each FULL uses its actual stage-local normalizers. The source forward wrappers
at each port i, rightmost acting first, are

    input X: Ei Ki Q^-1,      input Y: Ki,
    output X: Ki^-1,          output Y: Ds Ki^-1 Si^-1,

where Ei,Si are the retained actual entrance-line/exit-hyperplane operators.
The complete products shown by the source are monomial; their factors cannot
be individually dropped or declared free solely from a frame label. The
middle J and final controls act on the normalized physical main fields over
all 17 axes. They must match those exact contact coordinates and preserve the
unused stage block as a spectator where required.

## Promised recursive invoice and the helper complement

The inherited center-free native price and helper outputs per FULL are

    P0 = 2201H1+412H2+510H3+127H4+40H5,
    H  = 28H4+7H7+47H8+326H9.

The released promised complete target/paid census is

    T = 224H17 + 816H9,
    P = 4608H1+838H2+1020H3+254H4+136H5.

Its accounting decomposes exactly as

    P = 2P0 + 112H1 + (94H1+14H2+56H5).

The last bracket is the complement price for the two native helper banks:
94 rank-eight jobs need rank-one complements; 14 rank-seven jobs need rank-two
complements; 56 rank-four jobs need rank-five complements. The remaining 652
are already rank nine. Thus all 816 helper original inputs are credited once,
and no original rank-four/seven/eight reward is also retained after counting
its completed rank-nine job. The price has rank mass 11040 and the target
11152, giving the stated raw surplus 112.

This arithmetic is consistent with the handoff, not an independent native
certificate for its unpublished construction. The actual complement words
must meet the helper's physical entrance/exit charts and retain the other
eight-stage coordinates as spectators, in both orientations. A rank difference
alone does not prove those physical contacts or their monomial adapters. The
source FULL/autonomous-helper premise is inherited; this review performs no
new 816-owner phase campaign. Nor does the positive raw surplus certify a
moment, finite compiler reserve, precision or outer transfer.

Known ordinary source charges remain nonzero: 448 port-wrapper field maps per
FULL, up to 448 further maps per backward normalization, and 6596 dyadic
precompensation ADDs per native FULL in addition to the original native work.
C_s or C_s^-1 has a source program with 224 K maps, 896 scalar ADDs and 16
owned CLEARs, using eight reusable owned mode fields. The inverse coefficient
is -1/52; its odd-denominator precision work is not free. Counts of these
macros in J/output decoders depend on the proposed t0 programs and cannot be
invented here. Query COPY/reset, inverse-query Paulis, routing, all buffers,
heights and full fixed-tape cost remain charged obligations.

## Actual free dictionary versus a theorem's enlarged algebra

The public active-query theorem deliberately grants arbitrary finite linear
owner programs over a fixed finite projective group H of one-column monomial
maps, possibly non-Clifford, to strengthen its LOWER BOUND. Each map is lifted
as the same h in all f columns. It permits width-dependent scalar coefficients
within that mathematical model and proves its obstruction at sufficiently
large f. It does not present an executable tariff for every such H map, every
element of its span, or every invertible matrix over that span.

The construction handoff expressly asks for EXPLICIT free implementations.
Its actual known source dictionary is narrower and operational:

* elementary scalar owner ADDs/mixing, signs and owner routing, with fixed
  coefficients computed and rounded under the caller's precision rules;
* owned COPY/reset/clear with original independent fields preserved;
* the exact K_i,s and inverses, their supplied phase-correct P/D/X words,
  ordinary phases/Paulis and any explicitly compiled fixed coordinate map;
* C1,C3 and their inverses through the concrete eight-mode scalar programs;
* Q^2 and Ds^2 Pauli maps with their actual finite passes.

This dictionary is closed under concatenating actual finite programs. A unit
must have a returned inverse program; mathematical nonsingularity supplies
neither its finite word nor its cost. There is no admitted closure rule saying
that conjugation by Q or D3 preserves this dictionary. In particular a word
with an even Gaussian count can still be nonmonomial/nonfree. Generic finite-H
or full Clifford-span hypotheses from a different theorem must not be silently
installed here. Arbitrary width-dependent coefficients also need a uniform
descriptor, bit-height and runtime prescription, not a unit-cost oracle.

There is also a general exact monomial-Clifford constructor in the retained
symbolic source, not just a table of K_i: `normalizers.py` lines 123–127 calls
`ce.monomial(op)`, checks exact tableau and phase, and emits only P/D/X/phase
letters. A specified rank-zero Clifford candidate can therefore be represented
by a literal fixed-axis word and its inverse. It still needs its 17-axis
embedding, all-column phase lift and finite indexed-movement/precision bill
under the retained monomial implementation. This is distinct from granting
every arbitrary non-Clifford permutation in the theorem's enlarged H. No new
letter was synthesized or tested in this review.

### Smallest concrete units subclass for the design lead

A useful source-grounded first class is t0=B tensor I_address, where B is a
fixed scalar owner matrix accompanied by a finite elementary program and its
inverse. A particularly strict finite generator alphabet is owner ADD with
coefficients +1 or -1, owner swaps and signs. Any fixed word in these generators
has an explicit inverse by reversing and inverting its gates, uses no Gaussian
call or new axis, and has a finite ordinary cost. B is then unimodular. Other
fixed rational B can be admitted only with their explicit scaling/division and
precision programs. This is a candidate subclass, not a claim of a solution.

For such scalar B, the first three conditions reduce to B and B^-1 because
they commute with Q and D3. The remaining test is the actual ordered operator
Q^-1 C3 B C1 Q^-1 and its inverse. The source normalizers fix its phase-correct
17-axis terms. Astra owns the creative intersection derivation; no linear
system, determinant test, t0 candidate enumeration or operator solver is run
by this inventory review. Proving a cancellation in a one-column matrix alone
would not justify every width: an all-column word identity and its physical
finite program are still required.

Credit Dillon for the released template and active local theorem, Dugongue for
#4929, the #4933 normalizers/coded ABI authors, Cinna Davis, Cao Yifan, zxv,
Jacob Sussman and all retained native/helper/compiler predecessors. Prepared
with substantial OpenAI Codex assistance; Apache-2.0. The joint #5124 mechanism,
finite-packing work and the other agents' operator-intersection design remain
separate ownership scopes.
