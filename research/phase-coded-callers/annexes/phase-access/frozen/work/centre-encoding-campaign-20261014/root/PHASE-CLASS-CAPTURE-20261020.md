# Centre codes supported on phase classes

A physical diagonal centre action is sufficient, but it is not necessary.
A centre action can mix fields within a class whose phase ratios are
admitted monomial maps. This permits a smaller phase-query interface.
It does not remove the cost of the common frame.

The exact scalar experiment below uses the actual rank-sixteen response.
It reduces the active part of a conjugated capture code from 112 fields
to 56 fields in the stated common frame. A dyadic variant has been
emitted in the independent-review lane; its distinct review is in
progress. The scalar experiment here uses division by three and remains
a separate baseline.

## General reduction

Let the invertible field phases be the diagonal operator Q. Partition
the fields into classes. For each class g choose one global anchor phase
Z_g. Assume that the following maps are admitted monomial maps in the
current frame:

```text
A_i = Q_i Z_g^-1,     for i in g.
```

Let Z repeat Z_g on every field of class g. Thus Q=A Z. Every map in
A and Z is a spatial operator on one field. No scalar matrix is moved
through A in the argument below.

Suppose a scalar code has the factorization

```text
C = T^-1 S T,
```

where T has nonzero entries only within classes. Suppose S changes and
reads only a specified set J of fields, and is identity on its
complement. Since T commutes with Z, direct multiplication gives

```text
Q C Q^-1
  = A T^-1 [Z_J S_J Z_J^-1 direct-sum I] T A^-1.       (1)
```

This is an implementation on arbitrary fields. In chronological order:

1. Apply the monomial maps A^-1.
2. Apply T.
3. Apply Z_J^-1 on the active fields.
4. Apply S_J.
5. Apply Z_J on the active fields.
6. Apply T^-1.
7. Apply A.

There is no new field or zero-input premise. The passive fields retain
all of their data. The inverse uses S_J^-1 and the same two alignment
passes. If every anchor phase has a rank-one native implementation,
the word uses at most 2|J| such children. T, S, and every alignment
map retain their full scalar and packed-map costs.

The same statement applies to a centre response K that preserves each
class. In this case ZK=KZ, so

```text
Q K Q^-1 = A K A^-1.                                (2)
```

This is native-free inside the specified frame. It still has scalar
and map costs. If K is not a unit over the scalar coefficient ring,
an in-place K or K^-1 needs its additional arithmetic services.
An additive use Y += KX is a different operation.

These identities use arbitrary spatial operators. They therefore hold
at every tensor width. A finite phase test is not their proof.

For a transported inverse code Q C^-1 Q, use (1) with C^-1 and retain
the right factor Q^2. When Q^2 is a declared translation, that factor
can be included in the first alignment pass as A^-1 Q^2. For a negative
conjugation, the new alignments Q_i^-1 Z_g must also be admitted
monomial maps. The actual directional phases commute, so those
alignments are A_i^-1. The general positive theorem alone does not
give this additional premise. These are ordered identities; the
positive and negative words are not interchangeable.

## Actual scalar baseline

The response is E=H^-1 E_mode H. H is the actual signed pair code on
48 of the 112 ports. E_mode consists of eight signed blocks
I-dd^T of size six and eight such blocks of size eight.

Use R=span(30,45,75,384). The actual labels have fourteen q+R classes,
each of size eight. H preserves those classes. Each size-six block
meets three classes in two ports each. Each size-eight block meets four
classes in two ports each. These claims are exact source checks.

In each block choose one of its class pairs. Let e equal d on that
pair and zero elsewhere. Put

```text
u = 2e-d,
v = 2d/k-e/2,
S = I+u v^T,                    k in {6,8}.
```

Since d^T d=k and e^T d=e^T e=2,

```text
S d = 2e,
e^T S = (4/k)d^T,
det S = 2(4-k)/k.
```

Both allowed determinants are nonzero. It follows that

```text
S (I-dd^T) S^-1 = I-(k/2)ee^T.                     (3)
```

The right side is supported in the selected phase class. It need not
be diagonal in the original port coordinates.

For every signed pair (a,b), take the sum and difference coordinates

```text
s = d_a x_a+d_b x_b,
t = d_a x_a-d_b x_b.
```

This is a dyadic unit code. Let P be their direct sum. In these
coordinates S is identity on every difference. On the m=k/2 sums it is

```text
S_m = I+(2f-1)(2*1/m-f)^T,
```

where f selects the chosen pair sum. Thus T=P H preserves each global
phase class and

```text
C = H^-1 S H = T^-1 S_reduced T
```

has only 8*3+8*4=56 active coordinates in the T representation.
Equation (3) also shows that C E C^-1 preserves every phase class.

The literal scalar implementation and inverse each cost 4204 old real
scalar units. Forward capture uses sixteen real division-by-three
scans. Inverse capture uses sixteen real multiplication-by-three scans.
Each has prefix row one-norm at most twelve on all arbitrary inputs.
The reduction T costs 1582 old units. The reduced code costs 1040 old
units plus its odd scans. These are scalar-chart costs.

The checker verifies all 640 input columns, both inverse orders,
all 528 untouched roles, the actual response conjugation, the pair
partition, and the exact reduction to 56 active fields. It does not
import the producer's matrix or replay functions. Its source pins
include the frozen actual response and pair geometry.

## Physical scope

The common rank-four frame for R makes within-class phase ratios
monomial and each anchor phase rank one. Subject to that frame's
admission, (1) gives the conditional 112-child bound. The two alignment
passes have at most 224 monomial field maps. This bound is not a
complete supplier invoice.

The current changed supplier exit uses the different rank-one frame
W45. The bridge lane checked all 56 proposed pair ratios in that
frame. Every one has rank two. Therefore the 112-child common-frame
bound cannot be combined with the current one-W45-exit budget.
Preparing the rank-four frame, removing it, or changing the native
endpoint requires a separate construction.

The full supplier also has routed stage responses and cross-bank
couplings. Neither (1) nor (3) proves their code matching, current
source access, helper completion, final raw output, or recursive cost.
The next construction test is a changed native endpoint that retains
its existing pair code and explicitly prices the additional pair
frames.

## Reproduction and status

Run each command with one process:

```text
python3 -I -B work/centre-encoding-campaign-20261014/root/check_phase_class_capture_20261020.py --out NEW_OUTPUT_DIRECTORY
python3 -I -O -B work/centre-encoding-campaign-20261014/root/check_phase_class_capture_20261020.py --out ANOTHER_NEW_OUTPUT_DIRECTORY
```

Both must print `PASS_ACTUAL_PHASE_CLASS_CAPTURE`. The two JSON output
files must agree byte for byte. The retained final runs are
phase-class-capture-final-normal and phase-class-capture-final-optimized.
The earlier run is a retained rational-matrix experiment before
division-by-three was expanded into its literal service.

This note builds on the actual low-displacement response, the physical
pair geometry, the bridge rank-one capture, and the independent-review
lane's phase-class analysis. AI assistance was used. No PR or
publication is authorized. Before any PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
