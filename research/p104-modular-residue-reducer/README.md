# A reversible narrow reducer for P104 coupled residues

PR3035's exact 343-bit residue domain admits a **literal reversible extraction
circuit using only four-bit modular additions**, with a complete local invoice:
**32,417 CNOT + 62,834 Toffoli**, 1,024 clean work bits and two reusable clean
adder bits. An arbitrary 343-bit target receives the canonical residue by XOR;
the input and all work are restored. The 681 quotient bits stay inside the work
bank until uncomputation. They are not erased or treated as free storage.

This answers the narrow-reducer part of [PR3035's handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3035).
It replaces its conservative 1,053-bit integer-intermediate bound with an explicit
bit circuit. It **does not improve the frozen complete lifting invoice**: that
implementation retains the same 448 narrow pair lifts and adds reduction and an
ideal transform. This comparison assumes the same fixed widths, implementations
and nonnegative gate tariffs. There is no runtime, supplier, new kappa, general
circuit lower bound or formal-kernel claim. Stop at this local interface result.

Base main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6;
selected-record SHA256 `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18982123)
is in the existing lifting investigation. Scientific sources are
Nick Petalas/PR3035 `0cc430349a3f3dc200666bc22e997076e0a557ed` and
Tekalign/PR3033 `b12bbaeb5ca2e83f15433fc2dd0ba3b766595281`.
PR3037's maximal-period theorem is a distinct published claim, not a premise of
this reducer or a result reproved here. No larger-lattice search was performed.

## General modular triangular lemma

Let `q=2^g`, `d>=1`, and let H be an integer upper triangular matrix with positive
diagonal `h_j`. Assume `q Z^d` is contained in `Lambda=H Z^d`. Back substitution
on `H z=q e_j` proves `h_j | q`, so `h_j=2^a_j`, `0<=a_j<=g`. Reduced HNF
bounds on off-diagonals are convenient for the finite implementation but are
unnecessary for this mathematical lemma.

Start with `R=t`, `0<=t_i<q`. For `j=d-1,...,0`, let `b_j=floor(R_j/h_j)` and do

```
R_i <- R_i - H[i,j] b_j (mod q), for i<j.
```

Retain **all g bits** of `R_j`. No later pivot touches it. At the end set
`s_j=R_j mod h_j`: the low `a_j` bits are s, and the remaining bits are b.

Summing the shears, for some integer vector k,

```
R_final = t-H b+diag(h)b+q k,
s       = t-H b+q k.
```

Thus `t-s` belongs to Lambda and `0<=s_j<h_j`. This box contains exactly one
representative per coset: if `s-s'=H z`, take the largest j with `z_j != 0`.
Then `s_j-s'_j=h_j z_j`, contradicting `|s_j-s'_j|<h_j`. Therefore this s is
exactly the ordinary descending-division representative, including when that
ordinary computation has negative or large integer intermediates.

Each shear is a controlled modular translation of a target distinct from its
source; it is a permutation on **all** `q^d` register states. Reverse the exact
word to invert it, processing pivots in ascending order and adding instead.
The source quotient is still present when used. This inverse does not require
lattice containment; containment is required for the coset interpretation.
Projection to s alone is generally not reversible. At `d=1,q=2,H=[1]`, both
inputs have residue zero; retaining the quotient bit distinguishes them.

For signed x, use `t=x mod q`. Since `q Z^d` is in Lambda, s also represents
x. Extracting/reading these low bits of a wide input still has a cost.

Containment cannot be replaced by diagonal divisibility. With

```
q=2, H=[[2,1,0],[0,2,1],[0,0,1]], t=(0,0,1),
```

modular reduction gives s=(0,1,0), while ordinary reduction gives (1,1,0).
Solving `H z=t-s` gives `z=(1/2,-1,1)`. The same H at q=4 is admissible;
using the wrong inverse order then fails on that t. The replay checks both
failures, quotient-erasure noninjectivity and the clean-work requirement.

## Literal clean-work oracle and gates

Let `p=sum a_j` and F be the full reversible shear word. Pack the low a_j bits
in increasing coordinate order, low bits first. Given retained input t, a disjoint clean
gd-bit bank R, and an **arbitrary** p-bit target S, execute

```
R ^= t; F(R); S ^= packed_low_H(R); F^-1(R); R ^= t.
```

This sends `(t,0,S)` to `(t,0,S XOR canonical(t))`. It uses `2gd+p` CNOT copies
and F plus its literal inverse. Untouched dirty spectators remain unchanged.
The work bank must start clean. Starting it dirty computes a different function
of `R_initial XOR t`; merely restoring dirty R would not establish this oracle.
No clean bank, output initialization or routing is supplied for free.

For an off-diagonal coefficient c, expand its set bits. A set bit ell gives an
add/subtract of `b_j << ell mod q` on a `w=g-ell`-bit target slice. The source
has `min(g-a_j,w)` bits and is preserved. Lower ell target bits are unchanged.
Every target register stays g bits. The Python arithmetic interpreter may use a
carry/sign bit in an expression; the separate literal bit interpreter uses only
the stated bit registers and restored conjunction ancillas.

To add an l-bit source into a w-bit target, for source bit k=0,...,l-1,
conditionally increment the target by `2^k`. Flip target bits `i=w-1,...,k`
controlled by source bit k and original target bits k,...,i-1. Descending order
preserves those lower-bit carry conditions. Reverse this word for subtraction.
A gate with m>=2 controls expands to `2m-3` Toffolis using `m-2` clean conjunction
bits, followed by their literal uncomputation. One-control X is a CNOT. At w<=4,
two reusable clean bits suffice, restored after every such gate. This is a
classical reversible CNOT/Toffoli circuit, not an admitted project child tariff.

The finite reference supports d<=256, q<=256; its larger widths use up to g-2
clean conjunction bits. The written lemma has no such finite bound. Generic
gate/table growth does not supply a favorable variable-rank recursive bound.

## Exact rank-seven invoice

The byte-identical HNF and checker from PR3035 are in
[HNF7.json](HNF7.json) and [vendor/lattice.py](vendor/lattice.py), authenticated by
[PREDECESSOR.json](PREDECESSOR.json). The replay verifies their bytes/Git blobs,
all prefix-parity basis columns, the complete lattice index and `16 Z^256`
containment. It retains PR3035's sufficient-lattice proof; its index checker is
**inherited code**, not a new independent implementation.

| Quantity per 128-Gaussian block | Exact value |
| --- | ---: |
| d, g, input low bits | 256, 4, 1,024 |
| H nonzeros / off-diagonal coefficients | 4,192 / 3,936 |
| Canonical residue / retained quotient bits | 343 / 681 |
| One-pass modular adds of widths 1,2,3,4 | 236, 1,302, 2,271, 1,340 |
| One-pass modular additions / summed widths | 5,149 / 15,013 |
| One-pass CNOT / Toffoli | 15,013 / 31,417 |
| Complete canonical XOR oracle CNOT / Toffoli | 32,417 / 62,834 |
| Clean work / additional clean adder bits | 1,024 / 2 |
| Sparse public table, direct encoding | 79,488 bits |

In this H every set-bit adder's source has the full target width. The respective
(CNOT,Toffoli) counts for ADD1..ADD4 are (1,0), (2,1), (3,5), (4,14). The oracle
includes 2,391 CNOT copies, both shear directions and every adder's cleanup.
This is a constructive upper invoice, not an optimum.

The direct table stores 3,936 `(i,j,c)` records at 8+8+4 bits and 256 three-bit
diagonal exponents. It can be compiled into a fixed circuit or accessed as public
program data; actual traversal, source addressing, routing and tape/head costs
remain additional. Setup/validation is offline certificate work here; a uniform
supplier must charge its own compiler or table-construction cost. No table-access
or recursive-child tariff is inferred from these bit gate counts.

Including a standalone low-bit input t, target S, work and adder ancillas gives
2,393 live data bits, before program/controller/routing storage. For an existing
wide source x, t can be a read view of its low bits; count the full source's
existing 256W bits and its access instead. Materializing t separately costs
another 1,024 bits. To consume s as numerical data the target must start clean,
which adds that 343-bit clean-bank premise. Other ideal/lift buffers are additional.
At N=512 the four forward blocks can reuse the same work bank sequentially;
four oracle evaluations cost 129,668 CNOT and 251,336 Toffoli. Their 1,372 target
bits and public-table access remain charged. No native N=512 recipe is replayed
or admitted by this four-block arithmetic scaling.

## Complete-path comparison and stopping decision

Write L for the fixed integer lift and U for its ideal linear map. PR3033 uses

```
scalar:  U(x-t) + L(t),             t=x mod 16.
coupled: U(x-t) + U(t-s) + L(s),    s=canonical(t).
```

Equality follows because `t-s` is in the inherited translation lattice. The
wide exact backend is common. Under the **unchanged fixed-width pair loops**,
both narrow lifts pay all 448 pair sites: 3,584 real additions, 1,792 floor
halves and 448 quarter turns, plus their accesses and cleanup. The same
conservative 13-bit signed allocation is valid for both. The coupled reference
adds the reducer, formation of t-s, a narrow ideal transform and recombination.
The direct predecessor ideal loop has 448 pair butterflies, 5,376 real
additions and 256 final exact shifts. For |t-s|<=15 its numerator registers fit
19 signed bits; final values fit 12. A different exact linear backend needs its
own complete price, not an assumed cheap child.

Even optimistically assigning zero cost to additional setup, buffers, access and
cleanup, retaining the same lift and adding this positive reducer/ideal invoice
cannot lower that frozen static bill. This is the decisive stop for **inserting
this reducer before the unchanged scalar lift**. It is not pointwise Python
big-integer or wall-clock dominance: smaller actual values, a different circuit,
range propagation, fusion or a different consumer could change the comparison.
Nor is it a lower bound on all coupled implementations. A new design must name
which operations disappear and pay extraction, its extra linear work, clean
banks, every recursive child, precision, movement and restoration together.

Reversing F cleans this reducer using the same H. It does **not** construct the
inverse-lifting residue split, which needs a basis for `U Gamma`; the predecessor
shows this lattice need not equal Gamma. Full paired lifting/collector restoration,
physical hosting, exact/certified recursive backend, precision/tape and all-size
supplier admission remain inherited or open. The finite reversible extractor
alone establishes none of them and supplies no new kappa.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/p104-modular-residue-reducer
```

The registered replay is standard-library only, reads its exact typed
[RESULT.json](RESULT.json) without rewriting it, and runs eight behavioral groups:
all 170 admissible row-reduced triangular matrices at d=1..3, q=2,4 and all 8,660
corresponding inputs; all 340 elementary-adder source/target pairs at widths1..4;
290 rank-seven low-bit fixtures and 12 signed full-lifting comparisons through
4,096 magnitude bits; source/typed-receipt corruption; wrong inverse order,
quotient loss and missing containment; clean/alias failures; literal rank-seven
CNOT/Toffoli extraction; and an optimized read-only Git-free verifier export.
These are finite computations, not enumeration of the 2^343 residue domain.
Explicit exceptions keep proof-relevant checks enabled under optimization.

A separate internal carry-and-rounding specialist independently rederived the
all-input lemma, recomputed the HNF/gate counts, used Fraction back substitution
for the small census and separately simulated the 340 adders. This is independent
internal mathematical checking with AI assistance, not independent human review.
The source-bound rank-seven comparisons use inherited PR3035 code. No full
selected cold replay, hosted-CI success or formal-kernel proof is claimed.

## Open next questions

1. Can a changed narrow circuit or consumer exploit the 343-bit domain enough to
   pay this extraction and all additional ideal, storage and cleanup costs?
   First identify actual eliminated operations and compare complete invoices.
   The unchanged lift provides no win. No new search or construction expansion
   is proposed by this package.
2. Can a separately certified `U Gamma` basis support an affordable paired inverse
   split? First price both exact reducers and their consumer. Same-H uncomputation
   here does not discharge this obligation. Structured questions are in
   [TASK.json](TASK.json).

Ross Richardson, with substantial OpenAI Codex assistance in the mathematics,
code, tests and writing. Apache-2.0. Credit Nick Petalas/PR3035 for the coupled
lattice, exact HNF, index and source checker; Tekalign/PR3025/3033 for the fixed
lifting word, scalar split and full cost boundary; ywz65/PR2586 for native context;
Arham Tahir/PR2999 for the collision/occurrence lineage and all retained P104
contributors. Generic modular arithmetic, reversible adders and Hermite reduction
are not claimed as new. Frozen sources, selected records, priorities and shared
checkers are untouched.
