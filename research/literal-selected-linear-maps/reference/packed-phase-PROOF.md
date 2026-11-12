# A literal quadratic phase for a current selected native recipe

**Scoped enabling lemma; no new kappa.** Prepared for Jerry Chen / @CubeJerry
with substantial OpenAI assistance. Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.

## 1. Exact claim, source and novelty

Fix the nine-coordinate right monomial in the lowering of the actual retained
#7000 native `MOVE` at zero-based program index **24472**:
`["MOVE",415,3,99,false]`. Its before/after frames are 3 and 99 and its
proper-width central child has rank 1. The source is
`research/shared-wire-split-composition/data/final.json.gz`, compressed SHA256
`2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883`,
with canonical uncompressed JSON SHA256
`91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097`.
This is a current selected source event, not the historical event8814 fixture.

`RECIPE.json` retains the whole exact lowering, including both monomial
recipes. The right factor has constant phase 1, linear coefficients
`(3,3,3,3,0,3,3,2,0)`, and symmetric quadratic row masks
`(111,111,111,111,0,111,111,0,0)`. Diagonal entries are already included in
the linear coefficients; only strictly upper matrix entries contribute
quadratic terms. With `J={0,1,2,3,5,6}`, its input-coordinate phase is

\[
q(x)=1+3\sum_{i\in J}x_i+2x_7+
      2\sum_{i<j,\ i,j\in J}x_ix_j\pmod4.                 \tag{1}
\]

The retained `clifford_exact.monomial` constructs `diag; permutation;
translation; global phase`. Hence (1) is evaluated **before** the affine
address map. The global unit phase commutes with that map. Its matrix rows
and offset 1 remain in `RECIPE.json`; this package does not implement them.
The source normalization/exterior scalar coefficients are not replaced by
this Gaussian unit phase.

`bind_selected.py` authenticates exact source bytes, locates the actual
event, recomputes its lowering, and checks the complete factored kernel with
the retained independently written signed-Pauli/Gaussian interpreter. It
also checks all 512 right-monomial basis inputs against the separate formula
`q(x)=1-(sum_J x_i mod2)+2*x_7`. This follows from
`3h+2*binom(h,2)=h^2+2h`, which is 0 for even h and 3 for odd h modulo4.
These are source-binding checks, not a new review of the full catalogue.

The algebraic tensor phase and amortized multicounter update are prior work
of Ali Romman in [#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375),
retained in `reference/sequential-phase-PROOF.md`. In particular that work
already includes a constant phase once per active column. The contribution
here is a **fixed local transition graph** for this actual selected recipe,
including binary header acquisition, implicit complete address enumeration,
all Gaussian fields and repetitions, exact original-owner commit, restored
heads/private windows, and complete time and historical-extent bounds.

The predecessor `physical-gaussian-monomial/PROOF.md` explicitly supplies
structured tape control without a complete table. The selected tape-lift
work supplies record lists. `current-serial-monomial-leaf` makes its
descriptor iterator literal but leaves its numerical service structured.
The streaming tariff leaves encoded-control lowering open. We do not claim
their phase identities, physical monomial theorem, or tariff as new.

## 2. Supplied local ABI and theorem

The following packed interface is supplied, rather than inferred from the
native word. Supply five positive integers `f,r,P,S,w` in canonical Elias
Gamma form on HEADER, in that order. Gamma(z) is `ell` zero bits followed by
the `ell+1` ordinary binary digits of z, where `ell=floor(log2 z)`. Let E be
the total length of these five codes. No source/native descriptor conversion
is hidden in the theorem.

At DATA's origin supply the complete array indexed lexicographically by

\[
[P]\times[2^f]^m\times[S],\qquad m=9.                 \tag{2}
\]

The last coordinate of `[2^f]^m` varies fastest. Each record contains r
Gaussian coefficients; each coefficient contains first w real bits and then
w imaginary bits, both MSB first in signed two's-complement notation. All
coefficients share an arbitrary fixed caller grid, which this operation
does not change. Write

\[
Q=2^{mf},\quad N=PQS r,\quad V=2Nw.
\]

DATA contains exactly V binary cells and then a blank. It may have opaque
data beyond that boundary. HEADER may have opaque data after the five codes.
Both heads start at their respective origins. On each of the 21 private
tapes, supply a blank work window starting one cell before its head's
arbitrary origin and long enough for the extents below. All cells outside
the declared work/input windows are opaque and must be preserved. Tape
origins may differ and may be negative. Earlier allocated backing is not
assumed to shrink on erasure.

For coordinate integers `a=(a_0,...,a_(m-1))`, define column j by
`x_(j,i)=(a_i >> j)&1`. The desired mode is

\[
\Phi(a)=\sum_{j=0}^{f-1}q(x_j)\pmod4.                \tag{3}
\]

**Theorem.** The fixed graph emitted by `compile_phase()` has 8,211
locations, 23 tapes, alphabet `{blank,0,1,|}`, and only local `read`,
one-cell `write`, unit `move`, fixed `goto`, and `halt` operations. It is
independent of all five runtime integers and all payload data. On every
legal complete packet, it accepts if and only if every requested rotated
Gaussian component fits in the original w-bit signed range. On acceptance
it replaces each coefficient z at address `(p,a,s)` by `i^Phi(a) z` at the
same address and owner, preserves HEADER and all opaque cells, returns every
head to its exact entry origin, and erases all private bodies and guards.

On a named signed range failure it rejects before **any DATA write**, so
the complete public payload and HEADER remain unchanged. Private work and
head positions need not be restored on rejection. There is no rejected-call
reuse, interruption recovery, or general malformed-input guarantee.

The emitted graph can also be constructed for a fixed `1<=m<=9` recipe.
Those smaller specializations are finite verification fixtures. No runtime
recipe loader, input-sized graph, decoder oracle or extra address lookup is
an operation of the selected graph. Python only constructs the fixed graph
and simulates its local instructions. Observer integers such as the simulator
step count do not affect any transition of the graph. The finite verifier
step budget is external to the specified program.

## 3. Header and initial state

The retained C2 `gamma` helper represents each integer as a unary run on a
fixed private tape. It counts leading zeroes on LENGTH, starts the target
with one, and for each following binary bit b replaces unary v by `2v+b`.
DOUBLE is erased after each such replacement. The code consumes exactly the
number of tail bits recorded on LENGTH, without a decoded host value. HTRACE
records one unary cell for each HEADER move and returns HEADER exactly to
its origin; it is erased by that return.

After the five decodes, COLUMNS, COEFF, OUTER, SPECTATOR and WIDTH contain
`1^f,1^r,1^P,1^S,1^w`. All heads are at their body origins. Each private
window has a unique local `|` at origin minus one. No boundary search can
cross that guard.

The initialization loop scans COLUMNS once. For each of its f ones it writes
a zero on each of the m coordinate counters and advances those heads.
The only numerical phase state is one of four control labels; each iteration
adds the fixed constant q0=1 modulo4. On leaving the loop it therefore holds
`f*q0 mod4`. It rewinds COLUMNS and all counters, giving the first address
`a=(0,...,0)` and the correct mode. In particular replacing this initialization
by a single q0, or by zero, would be wrong at general positive f.

## 4. Synchronized counters and phase invariant

Each counter holds its coordinate integer in exactly f cells, LSB first.
At every `record` entry all m counter heads are at their origins. The
integer values of the counters are the current address a; the four-state
control is exactly (3). Neither P nor S nor the coefficient ordinal enters
the phase. For each record, the program retains that control state while
traversing S spectator copies and their r coefficients. COEFF is rewound
after each r fields; SPECTATOR is rewound after each S records. Every
header-supplied repetition is implemented by scanning these unary bodies.

The next address is obtained by incrementing counter m-1. During a carry in
counter i, **at each carry-bit read all m counter heads are aligned at the
same column j**. The intervening fixed sequence of unit moves finishes
before the next counter read. If the
old bit is x, a flip changes (3) by

\[
(1-2x)\alpha_i+2\sum_{k\ne i}Q_{\min(i,k),\max(i,k)}x_{j,k}\pmod4. \tag{4}
\]

For the quadratic contribution the sign `1-2x` can be omitted because
`-2=2 mod4`. The graph reads the fixed list of neighboring counters at
their current cells, accumulates the sum in four-state control, flips the
bit in counter i, and moves **all** m heads right by one. If x was zero,
the carry ends, all heads rewind to their own guards, and the next record
starts with the updated phase. If x was one, the carry continues.

On the blank after f cells, the graph checks that all aligned heads see
blank and rewinds them. Counter i has wrapped to zero and the control still
equals (3), because every flip was paid by (4). It then carries into counter
i-1. On overflow of counter 0 all m counters are zero. OUTER advances once;
another outer row starts with the phase **f*q0**, not necessarily zero.
The final row instead goes to the end-of-DATA check. No phase reset oracle
is required: the invariant itself supplies the right wrapped value.

Induction on individual flips proves the invariant. The standard binary
odometer argument proves that the program visits every address in (2)
exactly once in the prescribed order for each outer row. The proof covers
arbitrary joint coefficient arrays; it assumes neither pure tensors nor
uncorrelated columns. The tensor law merely specifies the diagonal action
(3) on the basis coordinates of a complete array.

## 5. Gaussian arithmetic, commit and exact failure domain

The WIDTH run makes each component read consume exactly w bits, including
leading zeroes and ones. REAL and IMAG are reused for one coefficient.
Every DATA move writes one DTRACE cell; none writes DATA. The retained
literal negation helper traverses a complete component from its LSB end,
complements each bit and adds one with a one-bit carry. The ordinary carry
invariant proves the modular result `-z mod 2^w`.

At the sign cell the helper remembers both the original and resulting sign.
Both are 1 exactly for the unique unrepresentable negation
`z=-2^(w-1)`. It rejects that case. This argument also holds for w=1;
no absolute-value operation on the original width is used. Copying or
swapping a most-negative component is allowed when it is not negated.
Thus the exact acceptance guards are:

| Mode | Rotation | Components forbidden to equal `-2^(w-1)` |
|---|---|---|
| 0 | `(x,y)` | none |
| 1 | `(-y,x)` | y |
| 2 | `(-x,-y)` | x and y |
| 3 | `(y,-x)` | x |

Both components are transformed and staged in OUTPUT in the correct order.
Their scratch bodies are erased before the next coefficient. A failure
after earlier coefficients therefore can leave a partial private output,
but the original complete DATA has not changed. All four operations are
exact integer Gaussian unit multiplication on the unchanged caller grid.
There is no rounding, truncation or intermediate scalar normalization.

After all `P Q S r` coefficients the program requires DATA's next cell to
be blank. DTRACE then returns DATA to its entry origin while erasing its
own body. OUTPUT rewinds. Commit copies all V staged bits onto the **same
DATA owner**, erasing each OUTPUT bit and rebuilding DTRACE. Its second
return erases that trace and restores DATA. The program rewinds the now
blank OUTPUT, clears every unary parameter and counter body, erases each
local guard, and restores every private head to entry. No public marker is
installed. All scans are bounded by bodies and private guards, so opaque
cells outside the declared windows are never read or changed.

## 6. Full literal time bound

Each table instruction has unit cost. Put

\[
B=E+(m+1)f+r+P+S+w+(m+1)^2 P Q+V+1.
\]

For every accepted legal packet the explicit conservative bound is

\[
T\le65536 B.                                             \tag{5}
\]

The same bound holds up to rejection for a legal complete packet with a
signed range failure. This is an intentionally loose uniform bound, not a
claimed optimized streaming tariff. Its components are as follows.

* Unary Gamma acquisition and return cost at most
  `256(E+f+r+P+S+w+1)`: prefix updates `v->2v+b` cost at most `47v+35`
  helper instructions plus the constant Gamma wrapper; the sum of earlier
  binary prefix values of z is less than z. The five prefix/tail traces and
  complete rewinds are included. This helper is copied from the frozen C2
  program with only fixed tape identifiers changed.
* Initialization and eventual counter/parameter cleanup cost
  `O((m+1)f+r+P+S+w+1)` with an absolute constant below256. All zero bits,
  guards, unused fixed ports, rewinds and erasures are included.
* A complete mf-bit odometer cycle, including the final wrap, flips exactly
  `F=2Q-2` bits. This remains true when its mf cells are split into m length-f
  fields. Every flip uses at most m-1 neighbor reads, one write, m head
  moves, and a bounded number of local reads/jumps. Returning the m heads
  after a carry segment crosses exactly the cells just traversed; its work
  is `O(m*segment_length+m)`. Each nonempty segment contains a flip, so all
  rewinds, field-end tests, carries to preceding fields, and outer-row
  advances fit `128(m+1)^2 P Q`. There is no f factor per address.
* Each Gaussian pair uses at most `256w` instructions including two loads,
  both possible negations, staging and component rewinds. The unary r/S
  loops and their rewinds add O(N), bounded by another `32V` because
  `r,S,w>=1`. They do not rerun phase arithmetic per coefficient.
* Complete output/data return and commit cost `24V+13` with the retained
  helper convention; end checking, parameter cleanup and fixed guards are
  already covered. No retained history is rescanned.

The sum is below (5), with substantial slack. These are instruction counts,
not timings extrapolated from finite fixtures. Because m=9 is fixed and
`r,S,w>=1`, `P Q<=N<=V/2`. Also `f,r,P,S,w<=V` and
`E=O(f+r+P+S+w)`. Thus (5) gives **O(V)** on this supplied local ABI for
every positive f. This absorption requires no long-record or RAM premise.
The unreduced expression (5) exposes all header/repetition/counter terms.

## 7. Historical storage and repeated invocation

Let K0 include all previously backed cells and initial input/header storage,
including opaque regions and current entry heads. Retiring or erasing cells
does not subtract from K0. A sufficient additional backing bound is

\[
K_{\rm final}\le K_0+2V+4E+(m+4)f+4(r+P+S)+8w+256.       \tag{6}
\]

OUTPUT and DTRACE each reach V cells plus an end/guard boundary. HTRACE and
LENGTH are bounded by E. DOUBLE never exceeds the largest decoded value.
The five unary parameters have their declared lengths. REAL/IMAG reach w
cells; the m counters each reach f cells. Fixed guards and end probes fit
the constant in (6). The work regions can therefore be chosen in advance
from those lengths, although the graph itself only discovers their ends
by local scans. It creates no input-dependent number of tapes or objects.

On a successful longer-then-shorter reuse, the active bodies are blank and
heads restored; prior backing remains part of K0. The next execution touches
only the next active lengths, so (5) does not depend on old high-water marks.
This conclusion follows from local guard-delimited scans; it is not a claim
that the sparse Python cell dictionary models deallocation. No analogous
reuse result is claimed after a rejecting call.

## 8. Composition limits and open next questions

The exact source recipe binding does not prove that the native compiler
produces the five-Gamma descriptor or the packed geometry (2) at a physical
invocation. In particular a field layout with inactive gaps or interleaved
spectators needs its own paid bridge or a more general literal mask program.
Affirming those interfaces from a finite source index would be a hidden
assumption. They remain supplied here.

The affine map, its routing/Compact work, source access, caller scalar
arithmetic, recursive rank-one C call, lifecycle composition and descriptor
production remain outside this component. The local table and fresh output
buffer do not establish global stock, tape, precision or recursive supplier
admission. All five selected foundational assumptions remain in the full
theorem, and the selected complete kappa is unchanged.

**Open next questions:** (1) Produce this exact packed descriptor from one
actual native invocation, or lower the existing arbitrary-active-mask update
while pricing the required physical layout; (2) join the corresponding
affine route and rank-one child with complete entry/return/lifecycle costs;
(3) establish the caller's common grid and signed headroom at that joined
occurrence. Each requires its own source-bound evidence, rather than a new
claim about this standalone diagonal pass.

Credit #5375 for incremental quadratic phases and tensor constants; the
retained #7000 source/compiler and earlier Gaussian/Clifford contributors
for the recipe; C2 `literal-layer-phase` for Gamma, signed staging and
return helpers; B1 `literal-layer-egress` for the original-owner staging
method; and #7349 for the retained literal machine. Independent AI review,
when recorded, is not human or proof-kernel verification.
