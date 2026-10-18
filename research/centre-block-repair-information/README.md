# Small owner blocks do not compress selected-centre information repair

**Scoped information theorem, exact finite premises; no new kappa or native
supplier.** In the selected PR1094 calls-0/4 observation model, permitting each
repair observation to mix source data from a block of **up to six physical cover
owners** still requires exactly **104 additional scalar linear observations per
owner**. Arbitrary global, even nonlinear, decoding of those observations is
allowed. The earlier owner-local theorem covers blocks of one; this result
tests a changed locality contract rather than repeating that theorem.

The new finite premise is that all **12,432 ordered nonidentity products** of
the actual 112 owner routes are distinct. Together with **6,216 nonparallel
column-pair checks**, this implies that a nonzero vector invisible to both the
old and later query fields must involve at least seven source owners. Seven is
only a lower bound; no seven-owner construction is claimed.

## Exact contract

Use the same rational constant-payload source model as
[`centre-owner-observation-floor`](../centre-owner-observation-floor/README.md).
Let G be the finite regular orthogonal cover group. For each cover owner g,
let x(g) in C^112 vary independently. Compared executions have equal arbitrary
ordinary target/helper dirt. The old observations and desired later field are

```text
Sx(g) = R x(g),
Tx(d) = sum_p H[:,p] x_p(d rho_p),       H = R/4.
```

Here R is the actual eight-by-112 centre matrix, and the 112 rho_p are the
source-bound involutory owner routes, represented by 73-by-73 binary matrices.
The native interpretation of these equations remains conditional on the
predecessors' common-frame, constant-endpoint and source-adapter identities.
This is not a native cold replay. In particular, a regular cover owner is an
element of G, not an ordinary helper-family index.

Partition G into disjoint nonempty blocks B. A repair at B retains scalar
**linear** observations E_B of the initial x(g) for g in B; it may mix all ports
and all owners within B. The rows may be complex and may differ by block.
All old fields Sx and all repair observations are then available to an arbitrary
global decoder. No additional source-dependent state is available. The decoder
must recover **the entire Tx field**, not one output owner or just the eventual
supplier endpoint. Constants independent of x can be subtracted and do not
change the theorem.

**Theorem.** If every block has size at most six, each block needs at least
104|B| repair coordinates. This is attainable as an abstract linear-information
interface, and hence the total additional-coordinate minimum is 104|G|.

## Proof

The exact checks establish three premises:

1. R has rank eight, every column is nonzero, and every pair of distinct columns
   is linearly independent over Q, hence also over C. H=R/4 has the same property.
2. The 112 rho_p are distinct involutions in the group acting regularly on G.
3. The map (p,q) -> rho_p rho_q is injective for p != q: all 112*111 products
   are distinct, with every one of their 73 binary columns compared exactly.

Suppose x is nonzero and Sx=Tx=0, supported on b distinct source owners.
Choose an active source owner g. Since R x(g)=0, premise 1 implies that at least
three port coordinates of x(g) are nonzero. They go to distinct output owners
d=g rho_p because the routes are distinct.

At each such output d, the contribution from g is nonzero. To cancel it in
Tx(d), at least two other source owners must contribute: one other contribution
would be a dependence between two distinct columns of H. There is at most one
port from any particular source owner at d.

A fixed pair of distinct source owners g,h can share at most one output owner.
Indeed, an equality g rho_p=h rho_q implies

```text
h^(-1) g = rho_q rho_p.
```

The right side uniquely identifies the ordered pair (q,p) by premise 3; the
case p=q would force g=h. Thus the at least three outputs reached from g need
at least six **different** other source owners. Consequently b>=7.

Now restrict input variations to a single block B, with |B|<=6. Write S_B for
the old observations of that block, and T_B for its contribution to the entire
later field. The argument proves

```text
ker S_B intersect ker T_B = {0}.
```

Since rank(S_B)=8|B|, its kernel has dimension 104|B|. All other blocks'
source-dependent observations vanish on this restricted input. If E_B had
fewer than 104|B| scalar rows, its restriction to ker S_B would have a nonzero
kernel vector. That vector and zero would give identical old and repair
observations but different Tx. Even a nonlinear decoder cannot distinguish
them. Therefore at least 104|B| rows are necessary.

For attainment, choose eight independent columns of R. Read the other 104
source coordinates separately at each owner, subtract their contribution from
R x(g), and invert the eight-by-eight pivot matrix. This reconstructs every
x(g), so it reconstructs Tx with the granted arbitrary global processing.
The receipt lists the exact pivot and complementary coordinates. This is an
information-level upper bound, not a priced collection or restoration circuit.

More generally, if source and destination column-dependence supports are at
least s and t, and a source-owner pair can share at most M destinations, the
same argument gives M(b-1)>=s(t-1). Only s=t=3 and M=1 are certified here.

## Exact checks and controls

`verify.py` explicitly reuses ywz65's pinned forward scalar interpreter and
route construction. It replays both complete local scalar endpoints on all
704 ordinary symbolic inputs, checks the selected chronological pair and
intervening data separation, derives R and H, and compares their coefficients
to the predecessor receipt. It then checks all column pairs and all ordered
route products and certifies the 104-coordinate information repair.

`independent.py` reconstructs the cut matrices with reverse adjoints of the
literal canonical word, rather than importing that forward interpreter. It
computes the route actions by orthonormal chart swaps and compares the finite
premises. `INDEPENDENT.md` independently reviews the all-block argument.
Both implementations have the same AI-assisted contribution owner; specialist
separation is not independent human or formal-kernel review.

The registered replay also runs three behavioral controls: changed executable
source is rejected before execution, a receipt claiming seven-owner coverage
is rejected, and an occupied output is preserved. The forward interpreter is
compiled from its authenticated source bytes, so a preexisting bytecode cache
cannot replace that source in a direct replay.

Six primary mathematical controls include a rejected parallel column, a
rejected duplicate route, a collapsed-route interface requiring no repair, a
two-owner C2 counterexample when the nonparallel-column premise is removed,
and loss of one dimension after omitting a complementary read. The sixth is
especially relevant: the actual columns satisfy R_44+R_38-R_24=0. Placing these
three values at the three owners d rho_44, d rho_38, d rho_24 cancels T at d,
but does **not** preserve S at those owners. Thus a three-owner kernel of T
alone cannot refute the theorem. These are mathematical controls, not a census
of owner blocks.

## Cost decision and limits

The proposed change was block-local acquisition of a shared centre cache.
Ideal two-call sharing would remove half of the incumbent 64 centre charge and
half of its eight rank-eight children per call before added costs. That
predecessor planning relaxation does not provide a repair implementation.
The present result rejects **information compression** through blocks of size
at most six: the required repair dimension stays exactly 104 per owner.

No scalar-coordinate count here is equated with recursive rank, paid mass,
arrays, bits or tape steps. Acquisition, routing, storage, dirty restoration,
precision, hosting and recursive child costs of a repair remain unknown. An
implementation might change those costs while preserving dimension. No complete
cost rejection of every six-owner circuit, selected-frontier change, or exponent
improvement follows. The family decision is to stop before unpriced synthesis.

The general block statement is a written proof from finite source-bound premises;
it is not a finite enumeration of all subsets of G or a theorem-kernel proof.
Overlapping observation supports, changed query cuts, final-output-only readers,
additional source-dependent state, nonregular actions, nonlinear observations
and blocks of size seven or more are outside the theorem.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/centre-block-repair-information
python3 -I -O -B research/centre-block-repair-information/verify.py
python3 -I -O -B research/centre-block-repair-information/independent.py
```

Local validation passed the complete registered replay on CPython 3.12.12 and
the optimized primary replay on CPython 3.14.6, including the six primary
mathematical controls, three independent premise controls and three behavioral
integrity tests. These checks cover the stated finite premises and artifacts;
they do not turn the written implication into a formal-kernel proof.

Inputs, exact base and source hashes are in `SOURCES.json`. The frozen selected
replay archive is read without extraction; no selected cold replay or hosted CI
pass is implied. The source base is
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6, selected-record
SHA256 `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
Current coordination and scope are in [Discussion3062](https://github.com/CrocSwap/integer-mult-bounds/discussions/3062).

## Open next questions

Can a named block of at least seven owners admit a nonzero vector in both
kernels, and can that change be used by a legally priced repair? First specify
one concrete owner block and solve the combined old/routed equations exactly;
seven is not asserted sufficient. A dimension reduction alone still needs a
source-access, restoration and complete recursive invoice before supplier work
is justified. A changed chronological readout or final-output-only contract is
another question and must specify its exact source-dependent observations.

## Credit and license

Aaron Wang/navinor's PR2391 supplies the native centre-reuse witness and the
additional-observation question. ywz65's `centre-owner-observation-floor`
supplies the sharp owner-local theorem, source matrices and route interface;
its forward interpreter is reused with its notice intact. Credit Sagar Thakrar
(PR2199 and Clifford conventions), Adam Gall (PR1918), commdata2338 (PR2048),
DreamingOfClouds' common-frame lineage, and the selected construction/emitter
lineage of Rohan Arun, Jeremy Kothe, Hao Yan and icekylinx, as recorded by those
sources. The new contribution is the ordered-route-product certificate and
the extension to every block of up to six owners.

Ross Richardson, with substantial OpenAI Codex assistance (GPT-6.1 Sol), including
a separate observation-kernels specialist derivation and implementation.
Apache-2.0. No independent human or formal-kernel review is claimed.
