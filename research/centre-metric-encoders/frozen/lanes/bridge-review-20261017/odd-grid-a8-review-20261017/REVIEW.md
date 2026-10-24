# Independent review of the odd grid and complete-minor factors

The A8 scalar factor and common-grid theorem pass this review. The general
complete-minor family also passes. These results remove an arithmetic
restriction of the dyadic emitter. They do not remove the A8 content
kernel, establish a new owner schedule, or prove a complete supplier.

The accepted scope is exact scalar computation on arbitrary inputs at a
legal common-frame cut. One existing owned C0 suffices. The new divisions
are separate fixed odd-division scans. They are not old dyadic SCALEs or
new H1 children. Recursive use requires exact Gaussian-dyadic completed
children on all data and arbitrary helper columns, one root conversion of
all numeric streams, and a separately proved final dyadic endpoint.

## Sources and independent checks

The producer packets are
[A8-ODD-GRID.md](../../independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md)
and
[GENERAL-MINOR-FACTORS.md](../../independent-review-20261017/odd-grid-a8-20261017/GENERAL-MINOR-FACTORS.md).
Their frozen source hashes are in [REVIEW.json](REVIEW.json). The review
checks each frozen file before use. It also checks the actual new-core
interface hash, the retained model source SHA256 and Git blob identities,
and the four pinned PR source Git blobs. It does not claim a new live
GitHub refresh or a rerun of the PR3423 and PR3406 executable suites.

The actual source is the eight-row R matrix in
`new-core-transfer-20261017/INTERFACE.json`, SHA256
`c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746`.
The review derives its Gram matrices from those entries. It does not use
an abstract matrix with only the desired dimensions.

The independent checker imports no producer module. It replays each
literal word as dense integer basis columns on a fixed exact grid. It
checks divisibility before each binary scale and each odd division. This
differs from the producer's Fraction-row replay. It checks every input
column, including arbitrary C0, every stored prefix, the final matrices,
and the complete scalar invoice. The three A8 baseline words and all 69
family factors pass. The 66 nonempty family words each reject a changed
scatter sign.

The checker also verifies signed division and multiplication on 49,140
inputs over the six odd divisors. An independent modular inverse checks
each division output. Twelve recursive fixtures check the active-chain
height invariant and its failure for completed rational children. Those
fixtures support the proof below; they do not substitute for it.

## Actual Gram matrices and the A8 inverse

The first selected minor has ports
`[0,7,20,27,36,46,57,111]`. Let U be its 104-port complement. Every row of
R has 56 signed unit entries. Every row restricted to U has 52. Direct
calculation gives

```text
R_U R_U^T = 52I_8,
K = R^T/4,
H = I_U-R_U^T R_U/4,
H^-1 = I_U-R_U^T R_U/48.
```

If `P=R_U^T R_U`, then `P^2=52P`. The P coefficient in either inverse
product is `-1/4-1/48+52/192=0`. Thus both inverse orders hold on arbitrary
ordinary inputs. H acts by -12 on the eight-dimensional query image and
by one on its complement.

Modulo three, `R_U K_U=13I=I`. The eight K_U columns are independent, and
`H K_U=-12K_U=0`. Thus the old dyadic ring obstruction is real. Extending
the exact arithmetic to division by three removes this obstruction.
It does not change the source native operators.

For row r_i, the inverse computes the complete query `r_i X` in C0,
divides it by 16 and three, then subtracts `r_i^T C0` from ordinary X.
The different row updates have zero cross products. Their product is the
stated inverse. The upper correction after that inverse is fused by
scattering through all entries of R_i instead. Its exact ordered map is

```text
X_U' = X_U-R_U^T R_U X_U/48,
X_A' = X_A-R_A^T R_U X_U/48.
```

The selected scatter does not enter any later query. It therefore leaves
the cancellation and prefix-divisibility proof unchanged. The initial
C0 value has no effect, because C0 is owned and is cleared. No borrowed
data field is cleared or assumed zero.

## All complete-minor unions

The actual 112 columns partition into fourteen disjoint eight-port minors.
The review verifies all fourteen identities `R_Aj R_Aj^T=4I_8` and all
four-unit-per-row support counts. For any union S of k such minors,

```text
R_U K_U = (14-k)I_8,
E = diag(-I_S,I_U),
R E K = (14-2k)I_8,
d = k-13.
```

These individual minor identities prove the assertion for every union;
there is no need to infer it from the first-k examples.

For `k!=13`, direct rank-eight multiplication gives

```text
H_k^-1 = I_U+K_U R_U/d,
A_k = E+K R/d.
```

For `k!=1,13`, the content inverse is

```text
A_k^-1 = E+E K R E/(k-1).
```

For example, the nonidentity coefficient in `A_k A_k^-1` is proportional
to `d+(k-1)+(14-2k)=0`. The same identity proves the reverse order. This
proof retains the order of E, K and R. It does not commute a selected Q
operator through them.

For A_k, first apply E, query `R_i E`, and scatter through `R_i^T`. For
its inverse, first apply E, query R_i, and scatter through `E R_i^T`.
For distinct row indices, `R_i E R_j^T=0`. Therefore earlier row updates
do not change a later complete query. This proves the two content words
as well as the ordinary words. The literal all-column checks agree with
these formulas.

At k=0, the ordinary inverse and A_0 are the J inverse. Its odd divisor
is thirteen. At k=14, the ordinary space is empty. Its three ordinary
factor words are identities that do not use or clear C0. The content
maps are `A_14=-J` and `A_14^-1=-J^-1`. These endpoints are consistent
with both the formulas and the literal words.

The two singular cases have different causes. At k=13, the complement
is one complete square minor. Hence `R_U^T R_U=4I_8`, so H_13 is zero
on all eight ordinary fields. No coefficient extension inverts it.
At k=1, `R E K=12I_8` and

```text
A_1 E K=0,
E A_1=I-E K R/12.
```

The second matrix is a projector with trace 104. The checker separately
multiplies its dense integer numerator by itself and checks the trace.
Thus A_1 has rank 104 and nullity exactly eight over Q. Its kernel is
the image of E K. The explicit selected input Q is invertible and cannot
remove these kernel channels. A controller that needs A_1 inverse remains
invalid. A controller may use the retained selected Y information, but
must prove and price that use.

## Prefix denominators and one C0

Write a factor's scalar denominator as `2^t o`, with o odd. Each row
query is completed before it is scaled or divided. A complete later query
equals that row's query on the module input, because all preceding row
updates cancel. It therefore has no new odd denominator. A partial query
can have denominator o from an earlier scatter, but it is not divided
while partial. The division adds one factor o to the complete query.
Scattering that value cannot add a second factor. This proves that every
prefix has an odd denominator dividing o relative to the module input,
including inputs that already have an odd denominator from a parent.

The A8 inverse has t=4 and o=3. Its eight divisions together add at most
one ternary level, not eight. Across the full family, `t<=5` and
`o` belongs to `{1,3,5,7,9,11,13}`. The divisor nine means two ternary
levels. The binary argument is the same: a complete query cancels the
prior factor before another scale occurs.

The family words use one initial CLEAR and one after each of the eight
rows, for nine CLEARs. The first CLEAR discards only the arbitrary owned
C0 input. Between rows C0 is zero and stays in the common frame. At exit
it is zero and can return to its private empty-frame convention. No
nonzero value is relabelled. The A8 baseline retains sixteen CLEARs;
the separate family packet removes the seven adjacent duplicate CLEARs.

For any union of minors, each data-prefix row has 1-norm at most
`1+8*56/4=113`. A partial query has at most 56 terms, so its row 1-norm
is at most 6328. Unit-ADD arithmetic temporaries are at most 12656 times
the input magnitude, below `2^14` times that magnitude. The smaller
exact first-k norms in the receipt also pass the independent replay.
This is a factor guard, not a completed supplier precision constant.

## Exact record scans

For an odd o, division reads a bit b from least to most significant,
writes `a=(b-c) mod 2`, and sets `c'=(c+oa-b)/2`. The carry starts at
zero and remains in `0,...,o-1`. Summing the bit recurrence gives

```text
o Q_unsigned = N_unsigned+2^w c_final.
```

For sign bits s_N and s_Q, exact signed division is equivalent to
`c_final=o s_Q-s_N`. On a valid input the quotient fits in the signed
width. The scan overwrites its input and needs only finite carry and sign
control. A nonmultiple must fail; numerator one is a decisive control.

Multiplication uses `a=(ob+c) mod 2` and `c'=floor((ob+c)/2)`. Its signed
test is `c_final=o s_N-s_output`. The allocated guard prevents overflow.
Both scans preserve the record layout. The stated bound of `4(w_g+1)`
arithmetic-head steps per scan covers traversal, positioning and return.
Descriptor and record-counter work is additional linear work. The old
scalar price is not assigned to these scans.

## Recursive common grid and cost

The retained
[stopped-product source](../../interface-proof/rational-decoder/sources/notes/stopped-product-complex.tex)
explicitly implements this method with odd divisor 21. It includes root
dyadic inputs, arbitrary dirty auxiliaries, exact Gaussian-dyadic completed
children, active-chain denominator accumulation, and outer unscaling.
The new packet applies that existing method to the factors above.

Fix a finite parent word with at most M odd factors. Let L be an odd
multiple of each factor's o. A completed child must have an exact
Gaussian-dyadic matrix on every data and arbitrary helper column. It then
preserves any existing odd denominator of its input. Only unfinished
calls can add odd factors. A live chain of at most D+1 nodes adds at most
`K=M(D+1)` factors L.

At the root, choose one grid `2^-P/L^K` and multiply all padded numeric
numerators by `L^K`. This includes arbitrary borrowed values and all
numeric work streams. It does not scale addresses or descriptors. Any
nonzero numeric literal must use this representation. No local division
or recursive entry changes the format. The binary guard P must cover the
new complete event list.

Every intermediate is then on the chosen grid. In particular, immediately
before each /o scan, the encoded numerator is divisible by o, because its
exact quotient is also on that grid. This is a consequence of the root
dyadic-input invariant. It is false for arbitrary integer numerators on
the finest grid. It is also false if completed children retain an odd
denominator and one counts only live depth. The independent fixtures check
both failure modes.

At the final outer return, the proved Gaussian-dyadic endpoint implies
that each numeric numerator is divisible by `L^K`. Exact unscaling gives
the required original encoding, including every borrowed role's declared
endpoint. This conclusion needs the actual final semantic proof. A local
factor or denominator calculation does not supply it.

For A8, use L=3. Both root conversions cost at most
`8 N K(w_g+1)` arithmetic-head steps, plus linear descriptor work, and
add at most 2K numerator bits. For the full family, a uniform choice is

```text
L=45045=3^2*5*7*11*13 < 2^16.
```

It uses six prime scans for each multiplication or division by L. Both
root conversions cost at most `48 N K(w_g+1)`, plus descriptor work,
and add at most 16K bits. Here N counts all real numeric records, not
only active data. A factor with odd division adds sixteen real scans,
or at most `64 n(w_g+1)` arithmetic-head steps for n complex entries
per field, plus the retained linear stream work.

If every child has at most `48e/73` axes, two recursive edges reduce the
axis count by more than half. Thus `D<=2 ceil(log2(d+1))` is safe.
Fixed M gives logarithmic extra width and `O(V log d)` root work. An
exact completed u-axis child adds at most u binary denominator bits and
row-norm factor `2^u`. A finite complete parent can therefore use the
stated linear guard recurrence once its own constants a and b are
calculated. This establishes a way to obtain the guard. It does not
establish those constants for an unspecified new controller.

The common scalar scale commutes with exact linear native operators.
The conclusion does not apply to a rounded native operation without a
separate exactness proof. The read PR3423/PR3406 sources impose Newton
module and source-divisibility conditions in their own setting. PR3423
also explicitly obtains the coefficient map `E^-1 A E` and exhibits
its difference from A. Those results neither ban odd grids here nor
prepare arbitrary dirty payloads for free. Their executable suites were
not rerun for this review.

## Complete component invoices

The independent literal recount gives the retained A8 baseline:

| Factor | Old real primitives | Real /3 scans | CLEARs |
| --- | ---: | ---: | ---: |
| H | 6,720 | 0 | 16 |
| H inverse | 6,752 | 16 | 16 |
| Fused inverse and upper correction | 7,008 | 16 | 16 |

All use zero new native children at the legal common-frame cuts. Their
maximum stored row 1-norms are 121, 52 and 52. The nine-CLEAR family words
subtract fourteen old primitives from each A8 row. The corresponding
S40 costs are 4,658, 4,706 and 5,986, with no odd scan. Its content map
and inverse cost 7,346 and 7,330.

For the whole family, let `t=v2(4|k-13|)` and
`u=v2(4|k-1|)`. The nonempty word prices are

```text
H_k:          7218-512k,
H_k inverse:  7186-512k+16t,
Fused:        7186-256k+16t,
A_k:          7186+16k+16t,
A_k inverse:  7186+16k+16u.
```

Each nontrivial odd divisor adds sixteen real scans. The independent
recount verifies every one of these formulas and every local assembly
sum in the producer table. Those assembly sums consume the prior
164,514-scalar core, its rank mass 5073, the stated physical exchange
prices, and the fourteen-scalar C1-through-C7 cleanup. They do not count
as a literal native transfer or a controller replay in this review.

## Reproduction and conclusion

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/odd-grid-a8-review-20261017/check_review.py
```

Expected status:

```text
PASS_INDEPENDENT_ODD_GRID_AND_MINOR_FACTORS
```

The independent checker ran successfully. Both producer checkers also ran
with separate output paths in this review directory. Their two receipts
and two literal-word files match the frozen source bytes exactly, as
recorded in [PRODUCER-REPLAY.json](PRODUCER-REPLAY.json).

No material defect remains in
the stated scalar and representation claims. The native local-word
transfer is reviewed in a separate lane. Complete phases and owners,
recursive hosting, the final dyadic endpoint, the complete binary guard,
and the supplier moment remain necessary for a complete construction.
No new kappa value follows from this packet alone.

This review used substantial OpenAI Codex assistance. No PR, commit, push,
or publication was made. Before a future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
