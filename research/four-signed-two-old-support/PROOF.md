# Two old calls meet length-6 support

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, fix two distinct old projectors
`E, F ∈ {A, B, P, Q}`. The length-6 equation with four added frames, each
used once, is

```
R + S + T + U = 4I - E - F.
```

An added frame may equal an old projector. That permission is the one stated
for the length-5 equation in PR #7083; this note does not widen it.

There is an explicit solution. The six matrices

```
A, B, P, Q, 2A, 2B
```

are nonzero symmetric rational rank-one matrices, they sum to `4I`, and every
target is a subset sum. For every choice of two distinct projectors as
`E, F`, the other four matrices are the added frames and satisfy the equation.
Selected κ stays `781451/250000000`.

This is one solution, not a classification. It is not a word. It does not
say that every solution meets support, and it does not say that no solution
is a word. Three old calls stay untouched. A bounded search that misses
other solutions is not a census and is not used here.

The identity "sum of the paid addresses = 4I" and the necessary condition
"each target is a subset sum of the paid labels" are inherited from
`research/bit-two-signed-frame-floor/PROOF.md`, Section 1. This file does
not reprove them. The new fact is the witness and its subset scan.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

A coefficient vector `(a,b,c)` means `aA + bB + cP`. For a primitive integer
direction `(x,y)` and a nonzero rational scale `s`,

```
s uu^T = s (x(x-y), y(y-x), 2xy).
```

The four projectors and the two doubles are that form:

| label | direction | scale | coefficients |
|---|---|---|---|
| `A` | `(1,0)` | `1` | `(1,0,0)` |
| `B` | `(0,1)` | `1` | `(0,1,0)` |
| `P` | `(1,1)` | `1/2` | `(0,0,1)` |
| `Q` | `(1,-1)` | `1/2` | `(1,1,-1)` |
| `2A` | `(1,0)` | `2` | `(2,0,0)` |
| `2B` | `(0,1)` | `2` | `(0,2,0)` |

Each vector is nonzero and has determinant `ab + c(a+b)/2 = 0`, so each
matrix is rank one. Also `A+B = P+Q = I = (1,1,0)`.

The four targets are

```
A+P = (1,0,1),  A+Q = (2,1,-1),
B+P = (0,1,1),  B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `4I = (4,4,0)`. For
each target `H`, `det(4I-H) = 17/2`, so `4I-H` is not rank one. A singleton
therefore cannot be a target, and a five-label subset cannot be a target,
because its complement would be `4I-H`.

## 2. The six labels sum to 4I

```
A + B + P + Q + 2A + 2B
  = 3A + 3B + (P+Q)
  = 3(A+B) + (A+B)
  = 4(A+B)
  = 4I.
```

The same arithmetic is `3I + I`. No cancellation between the six matrices is
required beyond `P+Q = A+B`.

## 3. Every target is a two-label sum

The four projector pairs are labels in the witness:

```
A+P,  A+Q,  B+P,  B+Q.
```

Each target is that pair, so each target is a subset sum of size 2. The
checker also scans all 63 nonempty subsets and records that, on this
solution, no target has a carrier of any other size. That scan is a check
of one solution. It is not a proof that every support solution is a pair of
projectors.

## 4. Every old pair leaves four added frames

There are six ways to designate `E` and `F`. In each case both are among
the four projectors, so both are labels, and the other four labels are the
added frames. Those four are nonzero and rank one by Section 1. Their sum
is `4I-E-F` because the six labels sum to `4I`.

The three pair-orbits under coordinate exchange and the sign flip are
represented by `{A,B}`, `{P,Q}`, and `{A,P}`:

| old calls | added frames | residual |
|---|---|---|
| `A,B` | `P, Q, 2A, 2B` | `3I` |
| `P,Q` | `A, B, 2A, 2B` | `3I` |
| `A,P` | `B, Q, 2A, 2B` | `4I-A-P` |

The other three pairs are the images of `{A,P}`. The subset scan of
Section 3 uses the same six labels for every row, so support holds for
each designation.

## 5. This witness fails the odd-c count

Reduce the coefficient of `P` modulo 2. All four targets have odd `c`.
Among the six labels, `P` has `c=1` and `Q` has `c=-1`; `A`, `B`, `2A`,
and `2B` have `c` even. Two calls are detected and four targets are
detected.

The inherited call-versus-target inequality in
`research/bit-two-signed-frame-floor/PROOF.md`, Section 1, equation (2),
says that a word needs at least as many detected calls as detected targets.
This note does not reprove that inequality. Under it, the witness is not a
word. Support is necessary and, on this solution, not sufficient. Nothing
here lowers the eight-call minimum or changes the selected record.

## 6. What is not claimed

The length-5 equation `R+S+T+U = 4I-E` is the separate support proof in
PR #7083. This witness uses six labels and does not reopen that proof.
Three old calls, the equation `R+S+T+U = 4I-E-F-G`, are a different
residual. No statement is made about added frames forced to lie outside
`{A,B,P,Q}`: the permission used here is exactly that they may lie inside
that set. One solution with that permission does not classify the solutions
that avoid it.

## Open next questions

Does any other solution of `R+S+T+U = 4I-E-F` meet support and also meet
the odd-c count, with at least four labels of odd `c`? This witness has
only two. A word at length 6 would be shorter than the eight-call minimum.
The first step is one other integral solution with at least four odd-c
labels, then the same subset scan. This package does not list the solutions.

Can four added frames plus three old calls meet support at length 7? The
first step is `R+S+T+U = 4I-E-F-G` for three distinct projectors and one
rational rank-one solution's subset scan. The six-label witness does not
supply a seventh label.
