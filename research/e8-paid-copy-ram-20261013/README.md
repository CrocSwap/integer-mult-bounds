# A paid-copy E8 RAM construction and its exact-Fourier corollary

This research package gives a self-contained, independently scrutinized
**depth-one positive Gaussian kernel construction**, including arbitrary dirty
helper restoration, paid private response compensation, actual phase/owner
identities, the complete child invoice, and an all-size exact complex RAM
recurrence. Applying the existing OpenAI exact-width compiler and all-length
transfer gives the stated supplied-root cyclic-DFT corollary.

This is an alternative construction and reproduction, with a weaker rate and
more helpers than earlier community suppliers. It changes no selected witness
or multiplication kappa. It does not invent the E8 geometry, phase-frame
framework, Fourier transfer, CRT or chirp reduction. See NOVELTY.md and NOTICE.md
for prior work and the Pro/Codex contribution boundary.

## Statements and model

For

\[
C=\tfrac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},
\quad \alpha=14999/15000,
\]

one fixed deterministic procedure computes \(C^{\otimes k}x\) on every arbitrary
complex array of length \(2^k\), for every \(k\geq0\), in

\[
O(2^k(k+1)^\alpha)
\]

charged exact complex RAM work with linear private workspace. Architecture
depth is fixed at one independently of k. Helpers may contain arbitrary
correlated values. Private tableau/center/decoder storage is paid, initialized
and cleared; recursive workspaces are disjoint from retained caller buffers.

The WHT corollary follows from \(C=aDHD\), where \(a=(1+i)/2\),
\(D=\operatorname{diag}(1,-i)\), and H is unnormalized binary Hadamard. Two
diagonal phase traversals and one scalar normalization cost \(O(2^k)\).
The primary operator used in the cyclic transfer is C itself, not a WHT analogy.

With the additional supplied canonical root and preparation operations below,
one fixed deterministic procedure computes the positive unnormalized cyclic
\(F_N\) on every positive integer length N, for arbitrary complex input, in

\[
O\left(N(\log N)^{14999/15000}(\log\log N)^{45001/15000}\right),
\]

and eventually \(O(N(\log N)^{29999/30000})\). Direct formulas handle the finite
initial range; everywhere-positive logarithms may be used. There is no
N-dependent advice or architecture-depth selection. Constants are enormous and
no useful crossover estimate is proved.

The exact RAM charges complex arithmetic, indexed array access, all copies,
clears, allocation, padding, traversal, scalar preparation and scheduling.
Integer arithmetic/comparison/quotient/remainder operates on a fixed number of
\(O(\log(N+2))\)-bit words per value. Complex coefficients and intermediate
magnitudes are unrestricted exact values; those address-word bounds do not
bound complex precision.

The cyclic procedure is supplied one exact **canonical**
\(\zeta_{D_*}=\exp(2\pi i/D_*)\),

\[
D_*=(2N)L2^{\lceil\log_2(16L)\rceil}<1024N^3,
\quad 2N\leq L<4N,
\]

with L selected by the existing small-prime product/power-of-two construction.
Equivalently, the model has one operation returning that specified root.
Selecting D*, extracting all other roots, preparing scalar DAGs/tables/chirps,
and transforming the fixed chirp kernel are paid. Rational field arithmetic is
not asserted to acquire the master root. An unidentified primitive root of that
order is not the input interface. A root-free Q(i)-constant computation already
fails on \(F_3(0,1,0)\).

Exact complex division is used only in input-independent preparation, with
nonzero-denominator proofs. Variable DFT data undergo linear operations with
prepared scalars. No complex zero test or conjugation of variable data is needed.
Full convolution of two length-N inputs is a separate bilinear corollary using
three transforms at length \(2N-1\), general pointwise products and one canonical
root of order below \(8192N^3\).

## Complete paid provider parameters

The 120 ports are weight-three vectors and complements of pairs in F2^9. Their
real response roots lie in the eight-dimensional sum-zero subspace. Binary
ambient dimension and real response rank are different spaces.

```
h=9, v=120, real response rank=8
live helper roles R=6968; live width W=R+2v=7208
three-block width m=27; paid deficit D=24
global child histogram:
  rank 1:41040, rank 2:240, rank 7:20160,
  rank 8:1440, rank 9:48
private arrays: 7096 (including the reserved center bank)
role-index padding bits a=27^2+ceil(log2 7208)=742
```

The exact moment at \(\kappa=1/15000\) has more than one rank-mass unit of slack:

\[
27\cdot7208-\sum_s sH_s(27/s)^{1/15000}>1.
\]

Every padded owner/role label is an actual input handled by the paid cover or an
ordinary full-window child. The identity owner gives normalized recurrence gap
at least \(1/(27\,2^{742})\); no group-ranking or group-order oracle is supplied.

The complete local word compensates its incoming helper response, loads the
source, executes the core and output, reverses the core, and unloads the source.
Its full live map is \((x,y,H)\mapsto(x,y+x,H)\); the separately derived inverse
adjoint gives \((x-y,y,H)\). The code checks every independent live column,
not just clean helpers or sample vectors. The three-stage owner cover includes
all Gaussian translations, signed exchange and the two final rank-two children.

## Proof and imported dependency boundary

PROVIDER-PROOF.md is the original Pro-assisted provider text, preserved byte for
byte and bound in SOURCE.json. Sections 3–8 give the response/core/phase/owner
construction; section 10 gives the charged all-size RAM argument. Its broader
tensor-family sections and historical source-audit notes are retained as source
material. The main statements proposed and freshly adversarially reviewed in
this submission instantiate **depth one**. Historical missing-source statements
describe the earlier packet; the three actual Fourier imports needed here are
now included. Historical numerical/source claims are not blanket admitted.

CYCLIC-COROLLARY.md supplies the operator binding and numerical consequence.
The exact-width local compiler, dirty-DAG replay, fixed six-C shear pattern,
linear-work sector packing, CRT and chirp/master-root reduction are imported
from OpenAI/math at `adc7f1241b42e322a6451854ab7e4b4c146bf78a` and included
literally under imports/openai-math/ with their license. No original h=100
network rate, synthesis search or fixed-tape multiplier is imported as a
provider theorem. The contribution is the independently bound E8 instance.

The actual pair sectors carry precisely \(C^{\otimes k}\); their widths sum to
the full array size. This gives the substituted tensor cost at each slot.
Small ordinary FFTs are used only in local polynomial-width preparation, so
the proof is not circular. The scalar polynomial inverse used by the compiler
is triangular Toeplitz, not PR628's neighboring cyclic inverse.

## Reproduction and evidence limits

Python 3.9 or newer, standard library only; no install or network is needed:

```
python3 -B research/e8-paid-copy-ram-20261013/verify.py --check
python3 -B research/e8-paid-copy-ram-20261013/verify.py --write /tmp/e8-ram-results.json
```

The checker is adapted from the fresh independent adversarial referee's own
code, with mathematical constructors/checks unchanged. It imports no Pro
generator or contributor program. It regenerates the E8 roots, core, all live
symbolic columns in both orientations, phase projectors/bases, owner identities,
histogram/moment, ragged pair sectors, canonical root orders/CRT, primitive-root
Newton/Toeplitz identities, dirty DAGs, and complete small chirp computations.
Optimized Python is refused before any output receipt is written.

RESULTS.json is the complete deterministic finite-check receipt, with no elapsed
time determining mathematical equality. SHA256SUMS.json binds all other files.
The ordinary assertions intentionally guard mathematical acceptance, so `-O`
is unsupported and rejected. The proof's all-size induction, compiler depth,
traversal cost and asymptotic bounds are reviewed arguments; finite successes
are not offered as formal proofs or runtime implementations of giant arrays.

REVIEW.md records the fresh independent adversarial acceptance and its exact
artifact hashes. No existing repository generator, workflow, full suite or Lean
build was executed for this new-directory contribution. No full-suite or new
Lean pass is claimed. Existing source mirrors and selected results were kept
unchanged.

## Limits

This package supplies no finite-alphabet multitape implementation, integer-bit
multiplication bound, floating-point stability, practical transform benchmark,
new Lean certification, first E8/dirty-response method, first exact-DFT transfer,
record exponent, strongest-known result, or worldwide priority verdict. Root
encoding/approximation, coefficient growth, precision and global errors,
sequential movement, actual source setup and caller/head/work/return ABI remain
separate obligations. PR631's scoped star-reader puncture theorem is not
contradicted by this different real-response decoder.


## Evidence-integrity repair (local candidate)

The original mathematical proofs, RESULTS.json, SOURCE.json, review, notices
and imported sources remain byte-identical to PR647 head
`956bb581e7f97328e1b53baa5aca3d2490f2f607`. The new integrity.py specifies the
complete sixteen-file package, five required proof files and four included
proof sources independently of candidate lists. SHA256SUMS.json is mandatory
and covers exactly the other fifteen files. Retained evidence/attribution
bytes have fixed original pins; omissions, consistently reduced lists and
rehashed replacement proofs are rejected. Package symlinks and extra files,
including generated caches, are outside this fixed inventory; use -B and
write receipts outside the package.

These checks assume a stable filesystem and a trusted checker/contract.
Authenticate the reviewed revision with an independently obtained Git head or
archive digest before running it. A hash manifest shipped inside the same
package does not authenticate itself or the whole release. The mutable repair
files require that external anchor; a coherently rehashed README edit can
still pass local consistency checks. Passing does not re-prove mathematics.
The retained historical review does not claim acceptance of this new repair.

Run only the new, locally authored integrity tests:

```
python3 -I -B research/e8-paid-copy-ram-20261013/test_integrity.py
```

The tests never import or execute verify.py or provider/contributor programs.
The mathematical verifier delegates its authentication step to this helper;
its mathematical function bodies and deterministic receipt are preserved.
This repair was prepared for Artus's Tintagel campaign with OpenAI Codex
assistance, crediting PR838's coverage finding and PR841's digest-membership
repair alongside the unchanged prior attribution. No theorem, supplied-root
hypothesis or bit-complexity boundary changes.
