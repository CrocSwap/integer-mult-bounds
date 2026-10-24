# Separate child precision on the retained row layout

Status: proof candidate for independent review. This note proves an
arithmetic and tape interface, subject to the finite circuit premises
below. It does not prove that the current changed controller has the
required endpoint. It gives no new supplier or kappa claim.

The key distinction is between the requested accuracy and the number of
bits in the input encoding. A child can receive a fine input encoding
and still use a smaller accuracy parameter. It must normalize its own
complete principal stream before it discards low bits. An absolute error
bound on an unrelated, larger stream does not suffice.

## Actual source and native-child scope

Use repository revision
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`. The relevant source files are
`upstream/build/sections/05-layers.tex` and
`notes/batched-complex-rows.tex`. The former source states the following
facts in the paragraphs headed `Where the rows come from`.

* A parent row has index `u=Wg+w`. The complete row goes to role `w`.
* A native child receives one complete parent role stream. All of that
  stream's remaining address ranges and compact fields remain complete.
* Its own role rows, including rows used as arbitrary helpers, come from
  that same stream.
* Before the call, the other parent role streams are parked on a LIFO
  tape. The child does not read them. On return, its stream is copied
  back and the parked streams are restored.

The batched source combines the `r` consecutive native slots into one
child on `r*f` axes. It retains the complete row split and the factor
`1/W` in logical volume. It does not combine different parent role
streams into a child. This is the distinction needed for relative error:
scaling one child's complete principal stream also scales all rows that
the recursive supplier will use as its arbitrary internal helpers.

For the selected profile, `m=73`, `W=14336`, and the largest child rank
is 48. Its integer row depth is `D_c(d)`. The precision change below
does not add an address axis or increase this depth. It changes the
coefficient record width during a child call.

The independent census in `SPARSE-PRECISION-CENSUS.json` concerns the
pinned full-mode cores. It checks all 3,486 native climbs in each
orientation by exact forward input rows and exact reverse source
responses. In F there are 553 source-sensitive children: 508 have input
supported only on the scaled source, and 45 also have an unscaled input
component. The latter profile is 40 rank-one and 5 rank-two children.
In B, all 526 source-sensitive children are source-clean. All counts
concern that core. A changed inverse-adjoint word needs a new census.

## Finite circuit premise

Suppose a candidate native supplier on `e` active axes has a finite
border word. Each native call is a raw `C` tensor, with its proved
monomial wrappers. The number of scalar gates, native events and role
fields is fixed. The word has no input-dependent branch except the
numerical normalization described below.

Suppose its ideal limiting endpoint is the required raw `C^e` on every
principal row. All temporary owned fields must have the required final
state. This premise includes the actual controller, mode owners, terminal
adapter and complete native frames. A local T shear alone does not meet
it.

For a requested relative error `2^-t`, suppose the finite word's proved
error transfer assigns each child a multiplier `a_j` in `{1,2}`. Its
relative error request is at most

    2^(-a_j*t-A*e),

where `A` is a fixed integer. The same finite proof must bound the border
error and each scalar rounding error. The source-normalized lemma in
the coordinator's `SPARSE-PRECISION-TRANSFER.txt` is one possible way to
obtain such a schedule. This note does not replace its full input and
output error-space hypotheses.

One may use the maximum absolute real or imaginary coefficient as the
norm. A raw `C` on `r*f` axes has real block row sum at most `2^(r*f)`.
Monomial wrappers preserve this norm, up to their stated fixed scalars.
Thus the exact prefixes and suffixes of the unscaled core, with its
fixed graphs and wrappers, have bounds at most `2^(A0*e+A1)` for fixed
integers `A0,A1`. The explicit accuracy-dependent border scales are
excluded from this bound. Their `O(t+e)` exponents are handled by the
error-transfer premise and the parent format below. The logarithms of
the fixed-core bounds fit the additive `A*e` accuracy allowance. No
dimension-dependent square root of the number of records is needed.

For the source-normalized word, choose `delta` on the same accuracy
scale as the ordinary child error, after these finite prefix constants
are paid. A dirty-sensitive child then gets two copies of `t`; the
others get one. The finite proof must also include the full output
space of each child and all fixed external graphs.

## Relative error from a bounded-input implementation

The input to one child is a finite array of signed Gaussian dyadic
coefficients. It can have any correlations between its productive and
helper rows. Let `M` be the largest absolute real or imaginary component.
If `M=0`, return the zero principal stream. No external helper is read.

Otherwise scan the whole stream and find an integer `b` such that

    2^(b-1) <= M < 2^b.

The scan needs the highest nonzero bit of each absolute component. It
does not need a sum of squares or multiplication of two record values.
Divide the complete stream by `2^b`. The new maximum is in `[1/2,1)`.
Run the bounded-input approximation and then multiply its output by
`2^b`. If the normalized absolute error is at most `2^(-t-1)`, the
returned error is at most `2^-t*M`.

Input conversion must also be charged. Round the normalized input to
`t+e+3` fractional bits before the native approximation. The exact raw
map has real block row sum at most `2^e`, so this changes its intended
output by less than `2^(-t-3)`. Reserve the remaining error budget for
the recursive calculation and final conversion. An extra fixed number
of bits makes the sum strictly less than `2^-t*M` after unscaling.

This is valid even when the complete input stream is very small. For
example, a clean stream of size `delta` is first scaled to unit size.
It is not rounded to a grid intended for an unrelated unscaled helper.
Every internal helper row receives the same normalization. This step
would not justify borrowing an external unscaled parent stream.

The exponent `b` is a stream descriptor. Finding it, changing the signed
coefficient format, shifting the coefficient bits, and copying the
result take time linear in the input and output bit lengths. The shift
is one streaming operation; it is not `abs(b)` repeated arithmetic
passes. The original layer source already charges such shifts by one
scan in time and by their bit count in the denominator guard.

## A bounded parent record format

Within a node, use one common coefficient format with `O(t+e)` integer
and fractional bits. The finite constant must cover the exact scalar
word and the chosen border exponent. A source scale can require about
`t` extra fractional bits. A dirty-sensitive child can require about
`2t` output accuracy. Both requirements fit a fixed multiple of `t+e`.

On each child return, round to the parent's declared fine grid before
the next parent gate. The resulting error is an additional additive
error at that native output. Use a grid of at least `2t+A2*e+A3`
fractional bits, with fixed constants large enough for the finite word.
Even after one source restoration by `delta^-1`, the sum of these
conversion errors fits the node error budget. The same rule can be used
after a source scale or a scalar operation when the exact result would
need more fractional bits. These errors need not be relative to a tiny
child input; they have their own absolute budget relative to the
normalized node input.

This avoids an invalid format requirement. A tiny child can have a very
negative normalization exponent. There is no need to retain all of its
unscaled low bits in the parent. The parent return-grid bound controls
their removal. Without this separate bound, a relative-error statement
alone would not establish a common finite parent format.

Every internal value has magnitude at most `2^O(e)` on normalized node
input, except an explicit border scale, whose extra exponent is `O(t)`.
Thus the integer side also fits `O(t+e)` bits. This claim uses the proved
finite perturbation bound on actual child inputs. It does not assume
that an approximate child leaves an exact coarse dyadic grid at return.
The old semantic linear guard only applies to exact completed children
and is not used as such here.

## Child formats and the precision potential

The caller keeps its parked streams in the caller's format. During the
existing child-input copy, write the child stream in the child's format.
During the existing return copy, unscale and round it to the caller's
format. No step needs to widen an ancestor's parked records.

Write the requested child accuracy as

    t_j = a_j*t + A*e,       e_j = r_j*floor(e/m).

Absorb fixed ceilings into `A*e`, since an internal node has `e>=1`.
Choose a fixed integer `c` with

    c >= A/(1-r_max/m),      w(e,t)=t+c*e.

Then, for every `a_j>=1`,

    w(e_j,t_j)
      <= a_j*t + A*e + c*(r_j/m)*e
      <= a_j*(t+c*e) = a_j*w(e,t).

This inequality controls all recursive paths, including paths with
several precision doublings. It is stronger than bounding the maximum
precision by a common width at the root. At the root,
`w(d,t)=t+O(d)`. In the retained outer family, `d=o(p)` and `t=O(p)`,
so its width remains `O(p)`.

A child has one `W`th of the parent's coefficient count. Therefore its
precision-weighted logical bit volume is at most `a_j/W` of the parent's
potential volume. The conditional complex moment is

    Psi_prec(sigma) = (1/W) sum_j a_j*(r_j/m)^sigma.

The node normalization, format conversion, parking and return scans
cost its current potential volume times a fixed constant. The same
weighted-tree proof as in `batched-complex-rows.tex` then applies if
`Psi_prec(sigma)<1`. The stopping leaf work and the compact-operation
exponent remain explicit terms of that proof.

The address rectangle does not change when a coefficient record gets
longer. The row count and full active/compact ranges are unchanged.
The largest precision on a path is at most a fixed power of `d` times
the root precision, since the depth is `O(log d)` and `a_j<=2`.
Consequently all record-width descriptors still have polynomial size
in the original global parameter. The retained polynomial record length
dominates this descriptor work. The compact field constants must be
chosen to cover these larger fixed polynomial bounds; their old finite
numerical coefficient is not asserted unchanged.

## Exact public raw output on a known input grid

Suppose the public input is on `2^-g*Z[i]` and its component magnitude is
at most `2^B`. A raw `C^e` output is on `2^(-g-e)*Z[i]`. Run the relative
approximation with

    t >= g+e+B+3.

Its component error is less than half one output-grid unit. Round each
real and imaginary component to that known grid. This returns the exact
raw output. It also returns the exact required value of every principal
row used internally as a helper. The assertion uses the raw limiting
endpoint premise; it cannot round an unspecified encoded endpoint into
the required transform.

Internal recursive calls need not perform this exact public rounding.
They use the requested relative tolerance and return to the caller's
declared grid. This is why their accuracy is not forced to equal the
number of fractional bits in a fine caller input.

## Remaining construction obligations

The actual completed limiting controller, arbitrary mode restoration,
all owner windows, the terminal T adapter and the changed native profile
remain prerequisites. A local census cannot prove them. The final
inverse-adjoint restored-mode construction may have a different census
from the full-mode source-normalized word checked here.

The finite constants for source and native maps, scalar work, compact
fields, precision conversion and the eventual outer cutoff still need
a complete invoice. The argument above states how precision enters the
recursive moment. It does not identify a new accepted value of that
moment or a complete kappa witness.

The coordinator supplied the finite perturbation lemma. The circuit
lane independently found the late borrowed-input sensitivity witness.
This lane supplied the independent complete census and the row/record
argument. OpenAI Codex assisted this local research. Publication is on
hold. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
