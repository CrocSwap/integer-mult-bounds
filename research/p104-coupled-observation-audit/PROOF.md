# Exact audit of the two coupled observations in edit 26

## Result and source boundary

This package checks the local two-receiver claim in PR7756 at scientific
commit `9e051455757d1cc86b822e52e42e1e1c98ead417`. The retained constructor
rebuilds the source graph through edit 25. Its observer supplies the graph
immediately before edit 26. This construction is a dependency, not a newly
verified theorem here. No retained function or global is changed.

There are 1,262 public scalar inputs. Write `x_j` for input `j`, and `b_k`
for bank `k` in this graph. The two source equations are

```text
s0 = x1149 - x1152/2,
s1 = (x1152 - x1151)/2.
```

The result is exact over the rationals. Chart 144 can observe precisely the
line spanned by `s0` in the plane spanned by `s0,s1`. Chart 177 can observe
precisely the line spanned by `s1`. Both observations have the required
response to both paid impulses. Subtracting them restores terminals 130
and 166 when both source equations are zero.

This verifies one claimed scalar implication. It gives no new kappa and
no complete acceptance of PR7756, its earlier edits, its caller or its price.
All five framework assumptions and the selected frontier remain unchanged.

## Complete local banks and explicit observations

The checker enumerates every public input and paid arrival at each chart.
There are six local banks at each chart and no local public entrance.
Their order below is also the column order in the rank certificates.

| Chart | Complete ordered bank list | Observation |
| --- | --- | --- |
| 144 | 101940, 101941, 101949, 101984, 101985, 101996 | `(b101949-b101940)/2 = s0` |
| 177 | 101937, 101938, 101943, 101981, 101982, 101987 | `2*(b101943-b101937) = s1` |

The equalities refer to the unperturbed graph. The new checker propagates
sparse integer numerator vectors forward from the public inputs. Each
vector has one exact positive denominator. It computes all 15,144 public
coefficients of the twelve banks, including zero coefficients. It also
computes both pulse columns at every bank and every terminal on the two
receiver charts. The complete required graph has 904 nodes. Its donor
charts and a separate topological order are checked.

## Certificates that exclude a second source direction

At either chart, let `B` be the matrix whose six columns are the public
coefficient vectors of its banks. Form the 1,262-by-8 matrix

```text
M = [ B0 B1 B2 B3 B4 B5 -s0 -s1 ].
```

A vector in the kernel of `M` gives a local observation and its coefficients
in the source plane. The two complete kernels are

```text
chart 144: span{ (-1/2, 0, 1/2, 0, 0, 0, 1, 0) },
chart 177: span{ (-2,   0, 2,   0, 0, 0, 0, 1) }.
```

Every one of the 1,262 row equations is checked for these vectors. To
certify that each kernel has dimension one, the certificate supplies a
nonzero 7-by-7 minor. All indices below are zero-based column positions
or literal public-input labels.

- Chart 144 uses public rows `2,786,1149,3,4,18,1151` and columns
  `0,1,2,3,4,5,7`.
- Chart 177 uses public rows `2,818,1151,3,4,54,1149` and columns
  `0,1,2,3,4,5,6`.

Both determinants are exactly `1/512`. The complete matrices are in
`RESULT.json`. Fraction-free determinant evaluation checks the selected
minors separately from rational row reduction. A nonzero minor proves
rank at least seven. The explicit nonzero kernel vector proves rank at
most seven. Thus the two kernel descriptions are complete. In particular,
the six banks at either chart are linearly independent.

The source equations are independent. If only `s0=0` is imposed, a linear
observation that vanishes on all allowed public inputs must belong to
`span(s0)`. Its intersection with chart 177's bank space is zero. That chart
therefore has no nonzero correction of the required type. The same argument
with the charts exchanged applies if only `s1=0` is imposed. This conclusion
concerns these two equations and these banks. It does not exclude a
construction with different constraints, banks, transfers or nonlinear state.
Other lanes in edit 26 are outside this audit.

## Both incoming disturbances

The symbols `u,v` denote the two parallel-basis impulses from the journal.
They are not isolated injections at only the named pivot registers:

```text
u: add u at 101324 and u/2 at 101902; both routes are 117 -> 834.
v: add v at  99605 and v/2 at 100008; both routes are 117 -> 837.
```

Forward propagation of these two additional formal columns gives

```text
observation at 144: s0 - (u+v)/2,
observation at 177: s1 + (-u+v)/2.
```

The errors at terminals 130 and 166 are respectively `-(u+v)/2` and
`(-u+v)/2`. The other two terminals on these charts have zero response to
both impulses. When `s0=s1=0`, subtracting the local observation removes
the entire error at each affected terminal. This holds for arbitrary
rational `u,v` and all constrained old inputs by linearity.

The response matrix is `((-1/2,-1/2),(-1/2,1/2))`, with determinant `-1/2`.
After imposing the source constraints, the two observations recover
`u = -z144-z177` and `v = -z144+z177`. The nonzero determinant does not
provide a physical cross-chart readout; each actual terminal uses only
its own local observation.

## Separate evidence and rejection controls

The new forward propagation and fraction-free rank certificates do not
call the source's entrance expansion, pulse routine or row-space routine.
After the separate calculation, the unchanged source local checker runs
as a cross-check and matches its retained receipt. That check uses reverse
entrance expansion. Both paths share the pinned pre-edit graph constructor.
This is separate implementation evidence, not independent human review.

Four controls flip one coefficient in one parallel impulse. Each produces
a nonzero error after the two prescribed repairs. The resulting residual
vectors at terminals 130 and 166 are retained in `RESULT.json`. Two further
controls flip the nonzero observation coefficient on the third bank; each
breaks the all-input source identity.

A terminal-only control would miss some pulse errors: changing a companion
arrival can leave the terminal response unchanged while changing its local
observation. The controls therefore test the complete repaired expression.
They do not require an irrelevant terminal response to change.

All 31 retained files have Git-blob and SHA-256 pins. The selected base
manifest supplies provenance only; it asserts no unmerged ancestry. Normal
and optimized registered replay check the same certificate.

The complete 32-edit witness, whole native operator, physical catalogue,
mixed caller, interval price gate, selected cold replay, Lean and Docker
were not run. No compiler assumption is discharged. Broader construction
and caller review remain open.
