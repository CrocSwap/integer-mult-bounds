# Equivalence of the standard-library centre implementation

This implementation and argument were produced by Nick Petalas. Apache-2.0.
The group, its generators, the centre algorithm, mathematical certificate,
threshold and spectrum are MatShep's PR5675. This note proves equivalence of
representations on that fixed finite replay. It asserts no new tensor theorem.

## Integer matrices

Store a matrix U as a tuple of 32 integers. The first sixteen, in row order,
are the real components of 2U; the last sixteen are its imaginary components.
For encoded operands a,b, the real numerator in position i,j is

```text
sum_k (a_real[i,k] b_real[k,j] - a_imag[i,k] b_imag[k,j]).
```

The imaginary numerator uses the corresponding sum of cross products.
Dividing each numerator by two encodes 2UV. The implementation first checks
evenness and the same absolute entry bound as the predecessor. These are
unbounded Python integer operations. There is no floating arithmetic or
machine-integer overflow premise. Transposition with imaginary sign reversal
encodes U*, and (-imag,real) encodes iU. The two local embeddings and CNOT
are the same literal generators in the same order.

The byte key writes every integer modulo 256, exactly the source's signed
int8 representation. Breadth-first discovery visits each frontier in order,
with the generator as the outer loop, as in the source. Induction on discovery
round therefore gives the same ordered matrices and index. The new loop has
an explicit capacity of 46,080 matrices and fails on exhaustion. Every
successful round adds a new matrix, so that capacity also bounds the number
of rounds. The returned list is separately checked for unitarity, Pauli
normalization, scalar lifts and projective count. Its full byte hash must equal
the source certificate.

Conjugation uses the same ordered generators and ordered group list. Union-find
performs the same unions, including the source's direction of each parent
assignment. Sorting classes by their least discovered element gives identical
labels and representatives. The complete little-endian uint32 label hash,
every class size and every representative must match the source certificate.
The root search has a finite bound and fails if exceeded. No class is inferred
from a sample.

## Exact trace aggregation

For every representative r and every enumerated g, the integer dot products
compute tr(U_r* U_g). The numerator must be divisible by four, and the same
squared magnitude bound is checked for every pair. The enumeration retains
all pairs. For each conjugacy class c it stores the multiplicity

```text
h[r,c,t] = number of g in class c with tr(U_r* U_g) = t.
```

For every tested exponent f, distributivity over exact integers gives

```text
sum_(g in c) tr(U_r* U_g)^f = sum_t h[r,c,t] t^f.
```

Thus counting identical traces first preserves every entry of every source
centre matrix. Multiplicities and imaginary parts remain present. This is a
finite regrouping, requiring no convergence or spectral assumption. The code
retains the source's trace-class-function check. A direct repeated-trace
fixture tests multiplicities and complex phase at every f=1..12.

The source's scalar-residue basis is constructed in the same class order.
Its orbits close within four steps because the scalar is i. The implementation
checks closure and keeps exactly the same residue condition and picks. Exact
Gaussian matrix multiplication reconstructs the full product, checks sector
invariance, and compares every reduced matrix and pick with the certificate.

## Retained checks

The square-free annihilating polynomial is evaluated on every coordinate
vector, with unbounded integer arithmetic. Every eigenvalue projector trace,
positive multiplicity, total spectral mass, width rank and unit-diagonal trace
check is retained for all twelve widths. The determinant is the full signed
24-term expansion on every lift. Its three moments and the seven source
rejection controls are retained.

The literal tensor check uses the flattened tensor of matrix entries. This
is the usual matrix Kronecker tensor followed by a fixed coordinate
permutation. The permutation is identical for both operands, so their complex
inner product is unchanged. It materializes all entries through width four,
checks all sixteen ordered pairs at each width and keeps both real and
imaginary components. It does not substitute the trace-power formula for
the literal materialization.

Finally, JSON normalization compares the entire reconstructed source result
with the immutable source RESULT.json. Matching that output alone would be
insufficient; the preceding group, class and complete reduced-matrix checks
are also mandatory. The new output adds source and package SHA256 hashes,
enumerated trace statistics and representation-control counts. It is generated
by execution and contains no handwritten verification receipt.

## Boundary and limits

The argument covers this fixed source and its finite domains. It does not
classify larger groups or admit a source with different generators, file
layout, certificate or dimensions. The script authenticates all four declared
source files before computation. The original verifier is read as an immutable
source input and is never executed or imported. No original credit line is
changed. Certificate and saved output hashes are retained, not regenerated.

MatShep's all-width Schur-product argument and all mathematical claims remain
cited predecessor results. Conformance of this implementation does not add
independent scientific review. No new kappa, native realization, complete
supplier invoice, rounded implementation or selected-assumption discharge
follows. Independent human and formal proof-kernel review are unclaimed.

## Bounds and diagnostics

All loops use fixed dimensions, bounded source collections or the explicit
46,080-element capacity. Group matrices have 32 integer components, the
conjugacy list has 59 classes, centre blocks have at most 21 rows, exponents
are at most twelve and literal tensors have at most 65,536 entries per matrix.
The trace histogram has at most 59*59*81 buckets even without the tighter
Gaussian trace-magnitude constraint. There are four materialized tensors in
one width. Files read for authentication are capped at one MiB each. Functions
stay below sixty physical lines, checks use explicit exceptions under -O,
and the script has no recursion, subprocesses, network, dynamic imports or
mutable external state. It writes only stdout.

Power of Ten rules 3 and 9 require managed-runtime deviations. Python integers,
tuples, counters and iterators allocate and use runtime dispatch. The finite
capacities above bound live collections and explicit call targets. Integer
bit lengths are finite because all exponents and polynomial dimensions are
fixed and authenticated. This is a terminating command with no steady service
loop. Warning-strict normal and optimized execution, syntax inspection,
representation controls and corrupt-input controls supply the available
interpreted-code diagnostics. No unavailable static analyzer is claimed.
