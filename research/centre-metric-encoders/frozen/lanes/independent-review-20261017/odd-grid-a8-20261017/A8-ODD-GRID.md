# Exact division by three for the actual A8 borrowed block

The one-minor borrowed block is invertible in the retained machine model.
Its inverse needs exact division by three. The current dyadic scalar
emitter does not have this operation, but the retained fixed-tape model
already permits fixed odd divisors on a common exact grid. Thus the
modulo-three obstruction applies to that emitter's coefficient ring. It
is not an obstruction to the required computation.

This note gives a scalar word for the actual A8 block, its fused upper
correction, and a complete representation rule for recursive use. The
fused word uses one existing private array, 7,008 old real scalar
primitives, and 16 real division-by-three scans. It adds no native child
at a legal common-frame cut. It has odd denominator height one at every
prefix. These are new finite statements about this block. The common
odd-grid method is retained prior work.

The result does not supply the complete controller, its owners, or its
phase proof. In particular, the fused original-X response still has an
eight-dimensional kernel. The retained selected Y values are necessary
for the complete two-bank map. No new complete kappa value is claimed.

## Source binding

The actual interface is `../../new-core-transfer-20261017/INTERFACE.json`,
SHA256 `c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746`.
The checker verifies this pin before it reads R. The clean core, its full
native phase review, and the raw selected boundary convention are reviewed
in the parent directory's `NEW-CORE-LOGICAL-REVIEW.md`,
`NEW-CORE-NATIVE-REVIEW.md`, and `NEW-RAW-REVIEW.md`.

The source model was fetched again at commit
`6f100d4bb5083f8c35d96fd95a539811c62f245c`. The following files have the
same Git blob identities as the prior rational-decoder source packet:

- [The fixed-tape model](https://github.com/CrocSwap/integer-mult-bounds/blob/6f100d4bb5083f8c35d96fd95a539811c62f245c/upstream/build/sections/02-streams.tex).
- [The exact recursive contract and guard](https://github.com/CrocSwap/integer-mult-bounds/blob/6f100d4bb5083f8c35d96fd95a539811c62f245c/upstream/build/sections/05-layers.tex).
- [The retained common odd grid](https://github.com/CrocSwap/integer-mult-bounds/blob/6f100d4bb5083f8c35d96fd95a539811c62f245c/notes/stopped-product-complex.tex), in "One exact odd-denominator grid".

The retained grid proof uses division by 21. It scales all root dyadic
inputs and dirty auxiliaries once. It proves the depth bound from the
Gaussian-dyadic endpoint of each completed child. Its exactness argument
also applies to division by three.

The local campaign predecessor is
`../../interface-proof/rational-decoder/RATIONAL-DECODER.md`. That note
gives the exact signed scan, a one-accumulator J inverse, and the root-grid
cost. Its independent review is
`../../temporal-reuse/RATIONAL-DECODER-REVIEW.md`. The A8 factor below uses
the same arithmetic method on the actual ordinary block. It does not
claim to introduce fixed odd division or common grids.

## The actual block and its inverse

Let

    A = [0,7,20,27,36,46,57,111],   U = {0,...,111} minus A.

The pinned interface gives an 8 by 112 signed matrix R. Each row has 56
nonzero entries. Write R_U for its 104 ordinary columns, and put

    K = R^T/4,   H = I_U - K_U R_U.

The checker derives, from the pinned entries,

    R_U R_U^T = 52 I_8,   R_U K_U = 13 I_8.

Each row of R_U has 52 entries, each equal to +1 or -1. Hence

    H^-1 = I_U - K_U R_U/12 = I_U - R_U^T R_U/48.       (1)

For P=R_U^T R_U, the identity P^2=52P proves both inverse orders. In fact
the coefficient of P in (I-P/4)(I-P/48) is
`-1/4 -1/48 +52/(4*48)=0`. The same calculation proves the other order.
The eigenvalue on the eight-dimensional query image is -12 for H and
-1/12 for its inverse. The eigenvalue on ker(R_U) is one.

The failure of H to be a dyadic unit is exact: modulo three, the eight
columns of K_U are independent kernel channels. Equation (1) removes
this obstruction over Z[1/2,1/3]. It does not change the native source
operators or treat an odd division as an admitted old SCALE.

## One private accumulator

Use the already owned private C0 array. For each row r_i of R_U, perform
the following steps in order:

    C0 = 0
    C0 += r_i[p] * X_p       for each nonzero ordinary entry p
    C0 *= 1/16
    C0 /= 3                 exact signed numerator division
    X_p -= r_i[p] * C0      for each nonzero ordinary entry p
    C0 = 0

All eight rows use the same array. Distinct rows are orthogonal, so the
rank-one updates have zero cross product. Their product is exactly (1).
All other fields are unchanged. C0 ends at zero and has no dependence on
its arbitrary initial value. This is an owned-array construction. It
does not permit the erasure of an arbitrary borrowed helper.

To apply H, use the same query and scatter with `C0 *= 1/4`, and omit the
division by three. Its row updates also have zero cross product.

Suppose that k complete inverse rows have already run. The complete next
query r_i X equals r_i times the module input, since each earlier term
contains r_i r_j^T=0. A partial query can have one new factor of three in
its denominator. The complete query has none. Division occurs only after
the complete query. The new scatter therefore adds at most one factor.
This proves the odd-height-one bound at every prefix, including partial
queries and partial scatters. It holds relative to any existing input
height, including rational inputs from an unfinished parent.

The same argument bounds the additional binary denominator height by four
for the inverse and by two for H. Partial queries do not receive another
scale until the complete orthogonal cancellation has occurred.

## Fuse the completed-X upper correction

The raw selected backward boundary needs, after H^-1 on ordinary X,

    X_A += K_A R_U X_U.

All these X fields are at the same completed full frame. Since
`R_U H^-1 = -R_U/12`, the combined map on the initial completed X is

    X_U' = X_U - R_U^T R_U X_U/48,
    X_A' = X_A - R_A^T R_U X_U/48.                     (2)

Thus the inverse loop can scatter through all 56 entries of the full row
R_i, instead of only its 52 ordinary entries. Each query still reads only
ordinary X. Its orthogonality and denominator proof are unchanged.
Selected writes do not enter later queries.

This order matters. The upper correction uses the final ordinary X, and
(2) is the ordered product of that upper map with H^-1. The checker
verifies this product on all 112 data columns. It does not move a line
operator Q through R, K, or H.

For the raw backward formula, write the original input as x=(a,u),
y=(b,v), and put q=Q^-1 on selected fields. The retained physical input
convention has selected X=Q a. The raw backward core, before its old
postlower correction, gives

    X_U = u - J_US Q a - H v,
    X_A = q b - J_AA Q a - J_AU v,
    Y_A = Q a,   Y_U = v.

Apply (2). The borrowed-y response of completed X becomes `diag(q,-I)`.
In particular, arbitrary ordinary borrowed v is restored with coefficient
-I; it need not be zero, divisible by three, or a previously computed
centre. The common-grid conversion below supplies the integer divisibility
for every such input.

Let E=diag(-I_A,I_U). Apart from the explicit input Q, the fused response
of X to original x is

    A_X = E - K R/12.

The actual matrix has `R E K=12I_8`. Therefore `A_X E K=0`, and
`E A_X=I-E K R/12` is a rank-104 projector. The nullity is exactly eight.
Division by three does not remove this content kernel. The full two-bank
map still has the selected original content in Y_A. A controller that
requires A_X^-1 cannot use this A8 word. A controller that uses the
retained selected Y must prove that use explicitly.

## Literal invoice and finite guard

The old scalar price is used without modification. A complex unit ADD
costs eight real primitives; a positive complex `1/4` SCALE costs four;
`1/16` costs eight; CLEAR costs two. A complex odd division is two separate
real scans. It is not assigned an old primitive price.

| Factor | Unit ADDs | SCALEs | CLEARs | Old real primitives | Real /3 scans |
| --- | ---: | ---: | ---: | ---: | ---: |
| H | 832 | 8 | 16 | 6720 | 0 |
| H^-1 | 832 | 8 | 16 | 6752 | 16 |
| H^-1 with upper correction | 864 | 8 | 16 | 7008 | 16 |

All three rows use no new native child. The H input word is legal on the
ordinary Y fields at frame I. The inverse and fused words are legal on
completed X at FULL. C0 must be cleared and assigned the same frame before
its query; all operations in one factor then use that frame. No nonzero
private value is relabelled. The scalar packet contains no native frame
transition. A complete transferred word must check these lifetime facts.

An exact Fraction-row calculation covers all 113 input columns:
112 data fields and arbitrary C0. It obtains the following maximum row
1-norms over every stored scalar prefix:

| Factor | Maximum row 1-norm | New binary height | New odd height |
| --- | ---: | ---: | ---: |
| H | 121 | 2 | 0 |
| H^-1 | 52 | 4 | 1 |
| Fused inverse | 52 | 4 | 1 |

The row norms bound stored magnitudes relative to the maximum input field
magnitude. Primitive unit ADD temporaries are bounded by twice the larger
operand bound. The SCALEs and exact division decrease magnitude. Thus
256 times the input bound suffices for H scalar arithmetic, and 128 times
the input bound suffices for either inverse. The signed division carry is
at most two. These are finite factor bounds. They do not assert that the
old complete supplier's precision constant is unchanged.

When added to the independently reviewed 164514-scalar core, the two
selected exchanges for F cost 416 and the one selected exchange for B
costs 208. Clearing the seven other owned fields costs 14. Thus the
predicted complete local bills are

    balanced F: 171664 old real primitives,
    fused B:    171744 old real primitives plus 16 real /3 scans.

Both retain native mass 5073. These sums are predictions for the literal
transfer. This packet does not claim to have replayed those complete new
words. Their emitter, helpers, phase bindings, and frame checks remain a
separate verification step.

## Exact signed division and root preparation

Use one signed w-bit two's-complement numerator. Starting at its least
significant bit, read b, write a, and update the finite carry c by

    a = (b-c) mod 2,   c' = (c+3a-b)/2,   c starts at 0.

The six possible input-bit/carry transitions preserve `0 <= c < 3`.
Summation gives `3 Q_unsigned = N_unsigned + 2^w c_final`. With input
and output sign bits s_N,s_Q, the signed quotient is exact precisely when

    c_final = 3 s_Q - s_N.

This condition rejects nonmultiples. On a valid division the quotient
cannot overflow. The numerator is overwritten in place. Carry and sign
flags need only finite control. There is no second numerical array.
At most `4(w+1)` arithmetic-head steps cover a move to the low end, the
computation traversal, delimiters, and return. Retained descriptor and
record-counter work is an additional O(w+1) per record. The coefficient
four is not claimed for that separate layer.

Multiplication by three writes `(3b+c) mod 2` and updates
`c'=floor((3b+c)/2)`. Its signed final test is
`c_final=3s_N-s_output`. The preallocated guard prevents overflow. The
same arithmetic-head scan bound applies. Both algorithms preserve the
common record format. The checker exhausts all signed inputs at widths
one through twelve, as a check of the general invariant, and rejects the
unscaled numerator one.

## Recursive common-grid theorem

Assume a fixed finite parent word has M inverse-factor occurrences. Assume
all other local operations are Gaussian dyadic. Replace each completed
recursive child by its exact linear endpoint on every data and arbitrary
helper column. Assume each such endpoint is Gaussian dyadic. Let D bound
the number of recursive edges in any live call chain. Put

    K_3 = M(D+1),   S = 3^K_3,   common grid = 2^-P/S.   (3)

P is a binary guard for the new complete word. At the outer boundary,
multiply the padded integer numerator of every physical numeric stream by
S. This includes arbitrary borrowed data, helpers, and numeric work
streams. Private zeros remain zero. Address fields, tags, and descriptors
are not numeric payloads and are not scaled. Any numeric literal must be
written in the same representation. The factors here write only zero.

No denominator tag is added. No stream changes format at a local
division, recursive entry, or return. A common scalar S commutes with
every exact linear native operator, so the encoded computation represents
the same operator. This statement does not apply to an unproved rounded
version of that operator.

Each finite parent prefix adds at most M to the odd denominator height.
The height-one factor proof allows this count per inverse occurrence,
instead of eight counts for its eight divisions. Gaussian-dyadic
operations cannot add odd height. A completed Gaussian-dyadic child also
cannot add odd height, even when its input already has an odd denominator.
Only unfinished calls add height. Their chain has at most D+1 nodes. Thus
all intermediates lie on (3), and every /3 scan receives an integer
numerator divisible by three.

This proof starts with arbitrary dyadic root values scaled by S. It does
not start with arbitrary integer numerators on the finest grid. The latter
claim would be false, as numerator one shows. It also does not permit a
completed recursive child to retain an uncancelled rational normalization.
Repeated completed children with endpoint x/3 can increase odd height
beyond any bound that counts only active depth. Such a construction needs
a different global denominator bound.

At the completed outer return, require the exact intended
Gaussian-dyadic endpoint on all physical roles. Every numerator is then
divisible by S. Divide all physical numeric streams by three K_3 times.
This restores the original encoding of arbitrary borrowed values under
their stipulated endpoint operation. There is no new approximation error
and no new tolerance premise. The inherited final truncation occurs only
after this exact unscaling.

If N counts all real numeric records and w_g is the guarded common width,
both outer conversions together cost at most

    8 N K_3 (w_g+1)

arithmetic-head steps. Descriptor and counter work adds
`O(N K_3 (w_g+1))`. The additional numerator width is at most `2K_3` bits,
since `3^K_3 < 2^(2K_3)` for positive K_3. One local inverse factor on n
complex entries per field adds at most `64 n (w_g+1)` arithmetic-head
steps for its sixteen real scans, plus the retained linear stream work.
Its old scalar invoice is separate and remains in the table above.

For the retained 73-axis recurrence with largest child at most 48e/73,
`2*48^2 < 73^2` gives `D <= 2 ceil(log2(d+1))`. Fixed M therefore adds
O(log d) bits and O(V log d) outer work. The local scans add O(V) finite
node work. The same positive complex-power slack absorbs the outer log
factor. This statement preserves a strict exponent once its complete
supplier moment is proved; it does not supply that missing moment.

A full guard can be constructed as in the retained proof. Give each local
scalar primitive a finite magnitude and denominator-height charge, and
use the exact bound above for each factor. Completed u-axis children add
at most u binary denominator bits and a factor `2^u` in row norm. A
finite parent with total child rank s and largest child ratio rho<1 has
a prefix bound of the form

    A(e) <= A(rho e) + a e + b,

where a and b are explicit constants from its complete event list. For
e>=1, `(a+b)e/(1-rho)` is a linear inductive majorant, with a fixed base
allowance. The additional `2K_3` numerator bits in (3) are logarithmic.
Thus O(p) records suffice in the retained parameter family. The complete
controller must calculate its own a,b and binary P. A cancellation-based
bound for a different old whole word cannot be copied without that check.

Replacing /3 by a dyadic approximation alone is not this extension. The
checker replaces it by 85/256 and proves that composition with H does not
restore arbitrary inputs exactly. This rejects that direct substitution.
It does not exclude a separately proved reversible rounded construction.

## What the recent Newton-code results do and do not require

[PR3423](https://github.com/CrocSwap/integer-mult-bounds/pull/3423) and
[PR3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406) were
refreshed and their pinned proof files were read. Exact heads, paths, and
Git blob identities are in `sources/GITHUB-PINS.json`. Their executable
suites were not rerun for this audit.

Their actual P104 code is `B_9=E Z[i]^512`, where
`E=[[1,0],[1,1+i]]^tensor9`. The proved source Clifford alphabet preserves
this module. The signed-floor pair is exact on its stated domain. The
real initial Y banks must also satisfy the appropriate fourfold
divisibility before quarter reads. These are source-domain obligations,
not free preparation of arbitrary dirty payloads.

The [PR3423 consumer proof](https://github.com/CrocSwap/integer-mult-bounds/blob/15d28c4de37dc47ea07cd7173c8b318fca7a4d75/research/p104-newton-interfaces/CONSUMER.md)
states the resulting coefficient map as `E^-1 A E`, and checks a case
where it differs from A. A caller must bind that changed interface. The
common scalar grid in (3) has `S^-1 A S=A` for every exact linear A. It
therefore avoids that non-scalar interface change, but pays root scaling,
extra width, exact scans, and all unchanged native operations. Neither
Newton theorem imposes a ban on odd rational intermediates in the retained
exact machine model. Their fixed P104 bill also does not replace the bill
for the changed PR3133 core used here.

## Reproduction and remaining work

Run one process from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/odd-grid-a8-20261017/check_a8_odd_grid.py --out /tmp/A8-ODD-GRID-REPLAY.json
```

Expected status: `PASS_A8_EXACT_ODD_GRID_NORMALIZATION`.
The checker writes the boundary words next to its chosen receipt. Compare
both files to the frozen packet. It verifies all formal input columns,
both H inverse orders, the fused order, every prefix denominator bound,
all local bills, the exact X-content kernel, and signed record arithmetic.
Controls reject an omitted division, an approximate inverse, and a root
numerator outside the stated representation contract.

The next required check is the literal transfer onto both new native
providers, with all helper and private columns, legal frames, and native
phase pins. A complete supplier must then use the retained selected
content, bind the controller, host all private state, prove every owner
endpoint, and calculate the complete moment and precision. These tasks
are not certified by this local packet. An independent reviewer must also
review this new factor and its grid argument; the producing lane's older
independent reviews do not review its own new construction.

The actual raw selected mechanism and minor block identities come from
the native-escape and new-core-transfer lanes. The scalar scan and grid
method come from the credited retained sources and prior rational-decoder
work. OpenAI Codex assisted the derivation, implementation, and source
audit. No human review, maintainer selection, PR, push, or publication
commit is claimed.
