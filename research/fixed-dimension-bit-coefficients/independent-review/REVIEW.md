# Independent review of the fixed-dimension coefficient consumer

Prepared for @CubeJerry by a separate OpenAI Codex research agent.
This review concerns the source-arena theorem, not an unconditional multiplication
theorem or a new complete κ.

## Verdict and pins

**Pass within the explicit normal, linear-use source interface.** I found no
remaining semantic, prefix-demand or historical-backing defect in the reviewed
consumer. This is an independent mathematical/source review with finite
corroboration, not a formal proof checker or a production-catalogue certification.

The scientific base is `e54523517d0f03e58352e647c403a5af3e525a57`. The author
freeze reviewed was `e180a8966e273768a20eb71fa98bc097991e9a44` with the
linear-use clarification committed at
`edb41e730cf23e82c6a20d57f21434beb769781b`. The reviewed PROOF.md SHA256 is
`352dfc1c725dfb20319e7cd0075e52a8fd45f21a5aa53547eef91d82fe27d575`.
The code is
`consumer.py`, SHA256
`5ba042c23c2d81f6b0ecb37cfbc954c24b865c05f8007e7666ab638be2856aa8`.
The independent checker authenticates all 15 `usage: input` entries in
`SOURCES.json` by SHA256 and Git blob ID; provenance-only catalogue entries do
not become portable runtime inputs.

I read the full proposed proof and compiler/workspace implementation, the four
retained encoded modules, and the cited capacity-prefix and chronological-field
interfaces. In particular, the numerical source is the N=64 cohort retained by
`delayed-cover-chronological-fields`; it is not silently substituted with a
different numerical implementation.

## Independently derived algebra

The executable review imports none of the author's `check_consumer.py` algebra
or replay. Its nontrivial numeric family uses N=3, rank 2, q=5, width 2 and
root extent 27 with root unit 2. Let

\[
H_G=\begin{pmatrix}1&0&1\\-1&1&1\\0&-1&1\end{pmatrix},
\qquad
H_B=\begin{pmatrix}0&0&1\\1&0&0\\0&1&0\end{pmatrix}.
\]

The first two columns of H_G span the kernel of the sum-of-coordinates map,
while its last column is (1,1,1). Therefore its split projector is
P_G=I−J/3, without running matrix inversion or elimination to obtain the oracle.
Its first two leading minors are 2/3 and 1/3, so the Good pivots are 2/3 and
1/2. Modulo 25 these are 9 and 13. The first Good step has f=9, child 18,
and weights 18 on coordinates 0 through 8 and 1 on coordinates 9 through 17.

For H_B the projector is diag(0,1,1). Its 6-dimensional residual is a
permutation matrix that swaps 1 with 4 and 2 with 3 and fixes 0 and 5.
The retained pivot algorithm therefore returns all diagonal entries 1 and
the same involution. A Pair step with field 4, f=6 and reversal selects
the preceding coordinate 6+(5−j)=11−j and has denominator 1. Its six
weights are consequently exactly

\[
(1,1,1,18,18,18) \pmod {25}.
\]

The current Good shear factor is −P_G[t,0]/P_G[0,0]=1/2=13, for either
nonzero target row. This determines four current coefficients, their sign
inverse and a source-offset multiplication independently of the evaluator.
Two Unit-reset calls independently return 1 while retaining all dead prefixes.

All 14 calls match these closed formulas. They use original labels 65537 and
131069 in 17-bit fields, full nine-entry raw matrices, and nonzero high digits
representing the −1 entries. Runtime `Word.inspect` and new `Tape`
construction are forbidden during the calls. All borrowed numerical bytes and
heads, full Program/Fields bytes and heads, arena-template heads and erased
historical free backing are checked after normal return.

The same four continuation tapes serve the entire sequence, including depth
3 followed by depth 2. The observed separate historical extents are
(45,17,20,10), and pre-existing histories of 283 residue slots and 137 index
slots remain reused. The largest observed extra pending demands are 57
residues and 17 indices. These are corroborating measurements, not the proof
of the universal demand bound.

## Universal source checks

### Specialization and exact semantics

The 17 edits cover the dimension, rank, pair label, raw N²-field and finite
multiplier sites and the two workspace interface sites. The unchanged source
arithmetic does not inspect runtime Word values. Building instances at
N=2,3,64,65,129,130,257,32767,32768,65536 checks that the emitted finite
label width grows beyond 16 bits and that a multiplier of 2N and selector
2N−1 work in their exact fixed ranges. These are finite boundary checks; the
single-occurrence source substitutions give the universal parameter statement.

The Good evaluator serializes its pivot before descending and frees its
matrix. For Pair, the source pushes the denominator request first, then the
numerator request. LIFO execution leaves the denominator on top when PAIR
pops denominator then numerator. This matches δ_a B_π(a)/B_a. Unit returns
one without rebasing or renumbering source slots. Construction still verifies
all chronological labels and the complete prescribed record prefix.

The residual-unit argument is valid over the specified local ring:
conjugation by diag(I,J) gives [[I−P,P],[P,I−P]], which squares to I.
After previous unit pivots are eliminated, an invertible remaining block
must have a unit in its first column, or its determinant would vanish modulo
q. The Good/root-unit premises then inductively make every divided weight
a unit. This is a domain proof, not a conclusion from successful allocation.

### Demand before capacity

I audited allocator requests directly, including a replacement before its
old Word is freed. Division has three current output/scan words and a fourth
requested replacement. In inverse, the four Euclidean residents plus the
two division results and a four-word modular multiply give peak ten.
Increasing the fixed multiplier label changes its number of iterations but
not its two-result-at-a-time allocation invariant.

The raw header holds high, partial output and low palette; preparation of
fixed constants may additionally hold high and raw matrices. Its largest
palette phase is 3N²+12. During the subsequent multiply there are high,
raw, basis and partial header, bounded by 4N² plus scalar scratch. During
inverse, high/header plus the augmented matrix total 4N²; the identity-list
entries alias the right half. Thus 4N²+12 is valid for prepare. Good uses
projector, elimination copy and at most N pivots. Pair uses projector and
one 4N² residual. No parent matrix survives a VALUE expansion boundary.

Allowing 64 more scalar residents, every phase is bounded by
max(4N²+12,2N²+N+12,5N²+12)+64. For N≥2 this is 5N²+76,
below 16N²+128 by 11N²+52. The source has six retained indices;
coefficient/step/seek/division/address phases remain below the stated extra
128-index allowance, including their requested next word. No loop accumulates
one numerical matrix or Word frame per descriptor depth.

This derivation is valid on a prefix stopping at the first capacity guard:
it uses planned shapes and local live/request effects and does not assume a
successful run. With no free slot, every current allocated slot is live, so
the pending bound contradicts a first inventory failure under the stated
entry capacity. A distinct noncapacity rejection remains possible.

### Full retained backing and cost

A VALUE record occupies 2I+4 symbols and a scalar record R+3. The pending
stack has at most 2h+1 records; the value stack at most h+1; each reverse
role has at most one record. Counting a left marker and first blank for
each role gives the stronger simple bound (3h+4)T+8, where
T=max(2I+4,R+3). This bounds the sum of the four historical maxima and
implies the author's (4h+12)T+16. Reentry takes maxima per physical role;
clearing a role does not shrink its allocated backing.

Direct delimiter counts give Program extent
2I+R+7+h(Q+5b_N+2I+10), and Fields extent
(h+1)(Q+N²(R+1)+2)+2. Both are below the published invoices. All N²
words and complete earlier fields remain charged even after Unit. Numerical
storage includes each permanent template, all entry-allocated slots and all
erased historical slots; it is explicitly a source-array bound rather than
a finite-tape physical-bank theorem.

The evaluator has at most a binary depth-h VALUE tree. Charging a complete
prefix scan at each node, all encoded arithmetic, preparation and erasure
fits the loose displayed cubic bill. The bound h≤log(n₀)/log(N/(N−1))
follows directly from each admitted child equation. The claimed exponential
absorption uses the separately required root map n₀≤e and
w=ceil(e^(1/250)); e≤w^250 converts this fixed-N overhead to a polynomial
in w. The selected catalogue, root map and invocation count are not supplied
by the package, so this remains a conditional local implication.

## Boundary controls and lease scope

Three actual constructor cases use N=65 with Pair field 128, N=130 with
Good rank 129, and N=257 with Unit rank 256. Their complete fields contain
4225,16900,66049 digits respectively. The test deliberately stops before
dense numerical preparation at these dimensions.

Twelve numerical/domain controls reject: ten multipliers just outside 2N,
the old <=128 multiplier guard reinserted into the actual N=130 Good
constructor, and a changed original field label in a dead Unit prefix.
The last control confirms that Unit does not bypass chronological label
validation. It does not claim all malformed dead numeric fields are validated;
the theorem separately requires canonical complete input fields.

Two interface limitations were clarified during review. The supported entry
is `Workspace.open`; the unchanged legacy `controller.selected_offset` does
not pass the newly required borrowed stack roles and is not an installed
entry. Also, `Workspace.active` is an exclusive-use flag, not a generation
token. An isolated control confirms concurrent open is rejected, but a stale
handle's abort is not generation-guarded and can retire a live successor.
Only the current live callback may evaluate/close/abort; a closed or aborted
handle is permanently retired. The normal theorem requires this linear-use
contract and makes no broader exception-safety or hostile-host claim.

## Reproduction

After this directory is copied to `independent-review/` inside the package:

```sh
python3 -I -B research/fixed-dimension-bit-coefficients/independent-review/independent.py
python3 -I -O -B research/fixed-dimension-bit-coefficients/independent-review/independent.py
```

Both must print:

```text
PASS_INDEPENDENT_COEFFICIENT_REVIEW 10 14 3 816 12
```

Use `--package-root PATH` while the review directory is outside the package.
The script is read-only unless `--write-result PATH` is supplied. The 816
checks compare independently counted record extents and phase inequalities
over a declared finite domain; the symbolic arguments above provide their
universal scope. No heavy author suite was rerun by this reviewer.

The original predecessor credit and licensing remain with the author package.
All five global assumptions, the actual selected producer/descriptor interface,
changing-width physical banks, host metadata lowering, full caller costs and
the complete accepted multiplication bound remain outside this review's result.
