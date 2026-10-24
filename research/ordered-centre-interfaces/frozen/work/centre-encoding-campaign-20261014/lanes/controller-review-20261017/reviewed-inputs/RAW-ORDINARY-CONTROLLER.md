# An ordered raw controller with ordinary bridges

This note gives the exact content map for a controller that uses the raw
selected backward and forward words. It includes the original first
forward shear, all ordinary bridges, and the final ordinary X triangle.
It identifies the information that a decoder must obtain. It does not
claim a physical decoder or a complete supplier.

## Local conventions

Let A be the eight selected ports and let U be the other 104 ports. Put
`Q=Q_A` and `q=Q_A^-1`. These operators act on selected coordinates.
For each stage j, let `B_j:U->A` and `D_j:A->U` satisfy `B_j D_j=13I`.
Products keep their displayed order. In particular, this proof does not
move Q through B or D.

At pair i use stages `s_i=2i+1` and `t_i=2i+2`. The backward local is

```text
B_i(a,u;b,v) = (B_s v+q b, u-v-D_s q b+D_s Q a; Q a,v).
```

The corrected forward local is

```text
F_i(h,k;d,v) = (h-q B_t k,k;d,v+k-D_t B_t k).
```

The raw forward local subtracts the additional term `D_t q d` from its
ordinary Y output. Both formulas are exact under the local conventions in
the native-escape source packet. Actual inter-call views are a separate
obligation.

## Event order and endpoint

Write the original pair as `(a_i,x_i;b_i^0,y_i)`. The selected variables
have dimension eight. The ordinary variables have dimension 104. Form
the ordinary suffix `z_i=x_i-z_(i+1)`, with `z_m=0`. Do not change the
selected X fields. The first full forward shear gives

```text
b_0=b_0^0+a_0, v_0=y_0+z_0.
b_i=b_i^0 for i>0.
```

At each pair, run B. Add the next idle ordinary X to active ordinary X.
Subtract active ordinary Y from next idle ordinary Y. Run F. Subtract
the same idle X. Add retired ordinary Y to next idle Y. The two operations
with the next pair are absent at the last pair. At the end, in descending
pair order, add completed ordinary X from pair `i-1` to pair i.

Define

```text
c_i = Q a_i-q b_i,
w_i = z_i-v_i+D_s c_i,
k_i = w_i+z_(i+1),
f_i = B_s v_i+q b_i-q B_t k_i,
e_i = B_t k_i                  for corrected F,
e_i = B_t k_i+a_i              for raw F,
r_i = v_i+k_i-D_t e_i,
v_(i+1) = y_(i+1)-v_i+r_i.
```

The final selected X, selected Y, and ordinary Y fields are respectively
`f_i`, `Q a_i`, and `r_i`. The final ordinary X fields are

```text
K_0 = -y_0+D_s0 c_0,
K_i = -y_i+D_si c_i+D_t(i-1) e_(i-1),  i>0.
```

To prove the formula for `K_i`, use
`z_(i-1)=x_(i-1)-z_i` and `k_(i-1)=w_(i-1)+z_i`. The Y bridge gives
`v_i=y_i+k_(i-1)-D_t(i-1)e_(i-1)`. Thus
`w_i+w_(i-1)=-y_i+D_si c_i+D_t(i-1)e_(i-1)`.
The descending final triangle adds the unmodified `w_(i-1)`, as required.
The first formula follows from `v_0=y_0+z_0`.

These formulas apply to all positive pair counts. The checker tests each
formal operator block for one through six pairs. It checks both F words.
It uses only adjacent Q inverse cancellation and `B_jD_j=13I`.

## What the completed selected query supplies

If a decoder has both `v_i` and `k_i` in a full frame, then

```text
b_i = Q(f_i-B_s v_i)+B_t k_i.
```

This is an exact selected-source recovery formula with one positive Q
operation. It is not yet a paid decoder. The completed ordinary fields
give each `w_i` by inversion of the final triangle, but they do not give
`k_i=w_i+z_(i+1)` without the original ordinary suffix. They also do not
give the incoming ordinary baseline `v_i`. A decoder must establish these
sources or eliminate them by another identity.

## A dyadic obstruction for a restricted decoder

Consider a causal controller in which each backward input receives its
own original Y with identity coefficient. Earlier pairs may contribute
to this input. Suppose that the extra X source at the forward call has no
dependence on the current or future original Y. Suppose also that the
final X operations are dyadic units and that productive selected Y depends
only on original X.

For fixed original X, the diagonal block from original Y to the completed
local X before F is

```text
R_s = [[q,B_s],[-D_s q,-I]].
```

Its Schur complement after the selected block q is `-I+D_s B_s`.
Since `B_sD_s=13I`, its determinant has a factor `12^8`, apart from units
and a sign. The selected X update in F is a unit upper shear. The global
X-on-Y matrix is block triangular before its final unit operations.
Its determinant therefore has 3-adic valuation `8m`, when each selected
Q is a unit at 3.

It follows that no dyadic linear decoder can recover all original Y from
completed X and the productive selected Y fields alone. Fix original X
and set it to zero. The selected Y fields then add no Y information. A
left inverse over the dyadic ring would force the square X-on-Y matrix
to have a unit determinant, which it does not have.

This determinant argument does not imply that `8m` independent queries
are missing modulo 3. Off-diagonal blocks can change the rank loss. It
also does not exclude a decoder that reads ordinary retired Y, a different
selected set, a noncausal bridge, or a changed local map. For a scalar
postlower parameter lambda, the same argument holds: the local Y block
has lower row `[-lambda D_s q,-I+(1-lambda)D_sB_s]`, and its Schur
complement is still `-I+D_sB_s`.

For the specific matched ordinary bridges in this note, there is a
stronger statement. Restrict to original X equal to zero. Undo the final
X triangle to obtain `w_i`. Undo the selected X shear to obtain
`h_i=f_i+q B_ti w_i`. Then

```text
v_0=y_0,
v_i=y_i+L_(i-1) w_(i-1),       L_(i-1)=I-D_t(i-1) B_t(i-1).
```

For each i greater than zero, use the old w values to replace

```text
w_i by w_i+L_(i-1)w_(i-1),
h_i by h_i-B_si L_(i-1)w_(i-1).
```

These replacements are a unit lower block triangular map. They put the
X-on-Y map into the block diagonal form with diagonal blocks `R_si`.
The formal checker verifies these identities for both F variants.

Over a field of characteristic 3, `B_sD_s=I`. Thus `D_sB_s` is a
projection of rank equal to the selected dimension. The Schur complement
`D_sB_s-I` has kernel equal to the image of D_s. Each `R_s` has nullity
eight, for selected dimension eight. The complete matched controller has
nullity `8m`. For array-valued ports, multiply this dimension by the common
scalar dimension of one array. The statement applies after reduction to
any field of characteristic 3 in which the displayed operator relations
remain valid and Q is a unit.

Consequently, a linear decoder for this controller needs independent
information from ordinary retired Y on this `8m`-dimensional kernel.
This is an information requirement. It is not a lower bound of `8m`
native children: one physical operation may carry more than one scalar
dimension, and a changed circuit may use a different representation.

## Verification and scope

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/check_raw_controller.py
```

Expected output:

```text
PASS_RAW_ORDINARY_CONTROLLER
```

The receipt pins this note and the local source notes. The checker tests
the local inverses, the full event order, the active ordinary cuts, and
the endpoint formula in a formal ordered operator algebra. It includes
controls for a missing selected-X query and an incorrect final tail order.
It does not replay the local physical words, price inter-call native
views, or prove a complete decoder. Independent review remains required.

The local physical selected exchanges are due to the native-escape and
coordinating lanes. The determinant observation is from the native-escape
lane. This note supplies its causal-controller scope and the distinction
between determinant valuation and rank loss. This work used AI assistance.
