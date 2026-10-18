# Exact C5 phase schedule for a dirty five-child echo

## Contract

Use an output pentad `D` in Z^5 and three workspace pentads `W` in Z^15, all
arbitrary and dirty. Let `Q` be the same five-cycle on `D` and `P` the direct
sum of that five-cycle on the three workspace pentads. Each child has map

```text
C_i(D,W) = (D + R_i W, P W),       R_i P = Q R_i.
```

The concrete five-child instance uses pentad selectors `(0,1,2,0,1)`. Each
child adds the selected pentad to `D`, then applies `P` to all of `W`. Its
complete word costs 5 data ADDs plus 36 frame ADDs, for 41 ADDs. The inverse
costs the same. No child has clean input state.

## Explicit five-cycle and prices

For a pair of registers define the signed swaps

```text
T+(a,b): a += b; b -= a; a += b       (a,b) -> (b,-a)
T-(a,b): b += a; a -= b; b += a       (a,b) -> (-b,a)
```

Then

```text
T-(a,b); T+(a,c); T-(a,d); T+(a,e)
```

maps `(a,b,c,d,e)` to `(e,a,b,c,d)`. The four signed swaps use 12 signed
ADD instructions, with no NEG. Direct integer-matrix multiplication in the
checker confirms the exact permutation, including the signs.

Implement phase `r` in Z/5 by the shorter of the forward cycle and its inverse
repeated as needed. This gives the explicit price vectors:

| Phase r | Output B(r) | Workspace A(r) = 3 B(r) |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 12 | 36 |
| 2 | 24 | 72 |
| 3 | 24 | 72 |
| 4 | 12 | 36 |

These are exact prices for the declared macro alphabet of whole-register
powers, not a proof of unrestricted ADD-circuit minimality.

## Shortest aligned schedule

Immediately before a child, let `t` be the common workspace/output phase. The
child advances the workspace phase to `t+1` and leaves the output phase at
`t`. To reach the next aligned phase `s`, apply `P^(s-t-1)` to `W` and
`Q^(s-t)` to `D`, with exponents reduced modulo five.

If a schedule must work for every independent intertwining reader `R_i`, each
child must be entered aligned: an unaligned child changes its contribution by
a nonidentity power of `Q`, as witnessed by a selector reader. The entrance
and gap prices therefore give the exact finite-state recurrence

```text
F_0(t)     = A(t) + B(t)
F_(j+1)(s) = min_t [F_j(t) + A(s-t-1) + B(s-t)]
g(k)       = F_k(0)
```

with phases reduced modulo five. Initial and terminal frame changes are
included. Every legal word in this macro alphabet supplies a path, and every
path is emitted by its stated powers, so the recurrence is exact for the
uniform-reader contract.

For `k=5`, the minimum is 60 ADDs, with aligned phases

```text
0, 1, 2, 3, 4, 0
```

An independent enumeration checks all 5^5 = 3,125 candidate phase paths. The
eager control restores `P^-1` after each child, including the terminal gap,
and costs `5*A(4)=180` phase ADDs. Both schedules implement the same map
`(D,W) -> (D + sum_i R_i W, W)`.

For `k=10`, the exact recurrence gives 120 phase ADDs and path
`0,1,2,3,4,0,1,2,3,4,0`. This joins two consecutive copies of the five-child
reader list. Its phase cost equals the sum of two optimized `k=5` paths; the
cross-call saving below comes from removing one outer copy/restore wrapper.

## Complete dirty echo and invoices

From the body `H(D,W)=(D+sum_i R_i W,W)`, form the exact echo on an additional
arbitrary source `X`:

```text
W += X
H(D,W)
W -= X
H^-1(D,W)
```

Its full map is `(D,X,W) -> (D+sum_i R_i X,X,W)`. The inverse body is the
literal reverse signed word. The source copy and restoration cost 30 ADDs for
all 15 coordinates. The complete invoices include every child, every inverse,
all frame powers, and the outer copy and restoration:

| Construction | Complete ADDs | Reads | Prefix row-L1 peak |
|---|---:|---:|---:|
| One optimized five-child echo | 560 | 1,120 | 22 |
| One eager five-child echo | 800 | 1,600 | 11 |
| Two optimized five-child echoes | 1,120 | 2,240 | 32 |
| One optimized ten-child echo | 1,090 | 2,180 | 42 |

Thus the C5 schedule saves 240 ADDs against eager restoration for one
five-child echo. Combining two optimized calls saves a further 30 ADDs by
removing one 30-ADD source copy/restore wrapper; the joint ten-child map is
checked against the composition of the two separate maps on all 35 basis
columns.

The optimized words have larger prefix row-L1 peaks than their eager/separate
controls. This is an exact coefficient-envelope warning, not a precision
admission: the package does not identify a supplier, set a fixed-precision or
tape contract, or transfer these savings to the selected recursive profile.

## Scope

The construction is exact for the stated integer-linear C5 reader contract and
the declared whole-register power alphabet. It does not prove the C5 cycle
word globally shortest, identify a selected supplier, certify precision or
tape costs, or change the selected frontier or kappa.
