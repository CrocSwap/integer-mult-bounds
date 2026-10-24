# Independent review of separate child precision

Result: PASS for the conditional arithmetic and tape interface. This
review found one scope error in the first proof version. The author fixed
it. No material defect remains in the revised statement.

The reviewed proof is
`temporal-reuse/HETEROGENEOUS-PRECISION-CONTRACT.md`, SHA-256
`4c47389d756d61fea7a672e03494e5219d83bbd7d1b2f7526a62cf411edc6607`.
Its first version had SHA-256
`73713ee5390f879cc7306978a1560a56f39b6738e8fcb04e4fbebfd716fcc2aa`.
The first version stated a `2^O(e)` bound for every finite prefix and
suffix. An explicit `delta^-1` border has a factor `2^Theta(t+e)`.
The revised paragraph applies the bound to the unscaled core and fixed
graphs only. The error-transfer proof and record format must pay for the
border scale separately. This is the required distinction.

## Physical child and helper contract

The source revision is
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`. I read Section 05, the grouped
complex recurrence, the complete compact-field layout, the fixed-tape
schedule in Section 04, and the signed stream arithmetic in Section 02.
The checker binds all five source
files by SHA-256. It also binds the original selected archive and its
template and owner-profile members. These give `m=73`, `W=14336`, and
maximum child rank 48.

Section 05 splits the entire parent row by `u=Wg+w`. One child receives
one complete role stream. Its next recursive row split takes place
inside that stream. Thus the values that become its internal borrowed
helpers are part of its input, even when they are correlated or large.
They must be included in the normalization maximum. The caller's other
roles remain on the LIFO tape and are not available as unscaled helpers.

This distinction is necessary. An approximate identity on `(x,h)` may
return `(x+epsilon*h,h)` and have error at most
`epsilon*max(abs(x),abs(h))`. If only `x=delta` is scaled and an external
`h=1` is borrowed, its principal error is not at most `epsilon*abs(x)`.
The reviewed source layout does not require that invalid call.

The width change occurs during child-input and return copies. Each
scalar or packed address operation sees one common, fixed record width
at its node. The packed operation remains an exact permutation of those
encodings. No coefficient rounding takes place while it holds temporary
XOR combinations. No new owner field or address axis is required for
the numerical normalization. Its copies use a fixed number of work
tapes, as do the retained row scheduler and record arithmetic.

## Numerical proof

For a nonzero complete input with maximum component `M`, choose `b` with
`2^(b-1) <= M < 2^b`. An absolute error at most `2^(-t-1)` after
normalization gives an error at most `2^-t*M` after multiplication by
`2^b`. This holds for negative `b` and for arbitrary helper contents.
The zero branch is valid because the required principal endpoint is
linear and no external helper is touched.

The real block row sum of the raw tensor is at most `2^e`. Thus input
truncation with `t+e+O(1)` fractional bits has an allocated error of
order `2^-t`. A separate output conversion allowance is required.
This is not a claim that the internal approximate word is homogeneous.
Its error guarantee must hold on the actual rounded input.

The parent return grid is also a separate allowance. For the stated
single source restoration, let
`delta^-1 <= 2^(t+D*e+D0)` and bound an unscaled suffix by
`2^(S*e+S0)`. If there are at most `N` conversion errors, a grid with
`2t+(D+S)*e+O(log N+D0+S0)` fractional bits bounds their restored sum
by a fixed share of `2^-t`. The finite constants can make this share
strictly smaller than the remaining budget. A different border with
more powers of `delta^-1` must change the coefficient of `t` in this
grid. Any fixed such coefficient still fits `O(t+e)` bits; it does not
follow from the displayed two-copy grid without a new error bound.

The normalization exponent can be computed by a highest-bit scan on
absolute signed components. A second scan writes the shifted input.
Both scans, the sign conversion, and all required reversals have linear
bit cost. A large negative exponent does not require repeated shifts.
On return, the stream is clipped to the parent's format. It is not
necessary to retain every unscaled low bit. The first input scan must
read the old format in full; its cost belongs to the caller's input-copy
allowance and is not charged only at the smaller child width.

The magnitude bound for the new word must follow from its finite
perturbation estimate. The old exact-child dependency guard cannot be
used for this purpose. The reviewed note makes this restriction explicit.
Likewise, the finite error-transfer schedule must be proved in the norm
used here, with the complete child input and error-output spaces. The
core sensitivity census does not prove that schedule for a changed
controller or its graphs.

## All-size time and simultaneous space

Put `theta=r_max/m < 1`. Choose an integer
`c >= A/(1-theta)` and define `w(e,t)=t+c*e`. For
`e_j=r_j*floor(e/m)` and `t_j=a_j*t+A*e`, where `a_j` is 1 or 2,

    w(e_j,t_j) <= a_j*w(e,t).

This is an all-size inequality; integer remainders only decrease its
left side. Fixed additive precision constants can be included in `A*e`
at internal nodes. The finite number of remainder axes is part of the
node work.

Choose one integer format multiplier `L`, common to all nodes, large
enough for both integer and fractional fields. A real component can use
exactly `L*w(e,t)` bits. This removes any ambiguity from independent
rounding of record lengths. Each child has one `W`th of the coefficient
count. Its physical coefficient volume is therefore at most
`a_j/W` times that of the caller. Fixed headers and work areas change
the common space constant only.

In particular, one active descent contracts the potential volume by at
most `2/W`. The total potential of simultaneously parked ancestors and
the active node is at most

    V_root * sum_(k>=0) (2/W)^k
      = V_root * W/(W-2).

For the selected `W`, this factor is `7168/7167`. The scheduler uses a
fixed number of copies at each active level. Hence total simultaneous
data space is `O(V_root)`, even though a deep child's component width
can exceed the root component width. No ancestor record is widened.
Section 04 also gives a stack schedule for the address subroutine. Its
child volumes contract by `1/W_bit`, its padding factors are fixed,
and its work areas are cleared at each return. The same geometric sum
bounds that temporary data while it is used inside one active numerical
node. Descriptor stacks fit the retained polynomial-record allowance.
This is a space result for the physical scheduler, not a statement that
the maximum precision itself stays at the root value.

Let `v_j` be a node's potential volume divided by the root potential
volume. Then its children satisfy

    sum_child v_child * e_child^sigma
      <= v_j * e_j^sigma * Psi_prec(sigma),

where `Psi_prec(sigma)=(1/W)*sum a_j*(r_j/m)^sigma`. If this moment is
strictly below 1, the grouped source proof applies with these weights.
At a stopping leaf, `e<d^beta`, so `e <= d^(beta*(1-sigma))*e^sigma`.
For compact work the same comparison with exponent `tau` gives
`chi=tau+(1-beta)*max(sigma-tau,0)`. The leaf, compact, reserved-axis,
and descriptor terms must all remain in the final outer bound.

The depth remains `D_c(d)=O(log d)`. Thus the largest component width
is at most a fixed power of `d` times the root width. Since `d` is a
fixed power of the global parameter, record-width descriptors still
have `O(p)` bits. Every nonempty stream still contains its full
length-`r` polynomial suffix. The source lower bound on `r` absorbs
fixed polynomial descriptor work. Increasing the record width does not
remove a compact guard or change an address range. The compact constants
and the common cutoff must be chosen again; the old finite numeric
invoice is not a consequence of this asymptotic argument.

## Exact public output and validation

If the input grid is `2^-g*Z[i]`, the raw endpoint is on
`2^(-g-e)*Z[i]`. A component bound `2^B` and relative accuracy with
`t >= g+e+B+3` put the error strictly below half a grid unit. Nearest
grid rounding then recovers the exact raw output on every principal
row. This includes every row that served as an internal helper. It
does not repair a wrong encoded endpoint or an unproved owned-mode
restoration. Internal approximate children need not use this exact
public rounding rule.

The independent checker imports no producer. It uses the direct tensor
kernel `C[y,x]=alpha^(e-h)*beta^h`, with `h=popcount(x xor y)`, rather
than the producer's butterfly replay. Its exact rational checks include
300 relative cases with a separate internal error, 100 exact public
rounding cases, 36 parent-return cases, five zero cases, and 864
potential cases. It checks a 38-edge maximal-rank descent with precision
doubling on every edge. Five controls reject missing normalization,
external unscaled helpers, a coarse return grid, a root-width cap, and
an insufficient additive potential.

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/heterogeneous-precision-review/check_review.py --workspace /Users/aliromman/Projects/IntegerMultiplicationBounds --out /tmp/heterogeneous-precision-review.json
```

Expected first line:

```text
PASS_INDEPENDENT_PRECISION_INTERFACE_CONTROLS
```

The finite checks support the proof; they do not prove it by enumeration.
No approximate native supplier, changed error census, complete numerical
invoice, or new kappa value was verified. This review is independent of
the failed direct terminal-border construction. It makes no claim about
the cause of that failure.

OpenAI Codex assisted this local research. No PR was prepared. Before
any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
