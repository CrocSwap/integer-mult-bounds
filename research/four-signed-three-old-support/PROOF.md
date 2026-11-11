# Three old calls meet length-7 support

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, fix three distinct old projectors
`E, F, G ∈ {A, B, P, Q}`. The length-7 equation with four added frames, each
used once, is

```
R + S + T + U = 4I - E - F - G.
```

An added frame may equal a standard projector. That permission is the one
stated for the length-5 equation in PR #7083 and used again for the length-6
equation in PR #7100. This note does not widen it. Either sign is allowed;
the solution below uses positive scales.

There is an explicit solution. The seven matrices

```
A, B, P, Q, (1/2)A, (3/2)A, 2B
```

are nonzero symmetric rational rank-one matrices, each positive semidefinite,
they sum to `4I`, and every target is a subset sum. For every choice of three
distinct projectors as `E, F, G`, the other four matrices are the added frames
and satisfy the equation. Selected κ stays `363005817/100000000000`.

This is one solution, not a classification. It is excluded as a word by the
inherited odd-`c` count. It does not say that every solution meets support,
and it does not say that no other solution is a word. The length-6 four-odd-`c`
question stays with PR #7100. A bounded search that misses other solutions is
not a census and is not used here.

The identity "sum of the paid addresses = 4I" and the necessary condition
"each target is a subset sum of the paid labels" are inherited from
`research/bit-two-signed-frame-floor/PROOF.md`, Section 1. This file does
not reprove them. The new fact is the witness, its carrier case split, and
the check that every old triple leaves four added frames.

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

A symmetric rank-one matrix has trace equal to its unique nonzero eigenvalue.
Positive trace, determinant zero, and a nonzero vector therefore mean
positive semidefinite rank one.

The four projectors and the three scaled frames are that form:

| label | direction | scale | coefficients | trace |
|---|---|---|---|---|
| `A` | `(1,0)` | `1` | `(1,0,0)` | `1` |
| `B` | `(0,1)` | `1` | `(0,1,0)` | `1` |
| `P` | `(1,1)` | `1/2` | `(0,0,1)` | `1` |
| `Q` | `(1,-1)` | `1/2` | `(1,1,-1)` | `1` |
| `(1/2)A` | `(1,0)` | `1/2` | `(1/2,0,0)` | `1/2` |
| `(3/2)A` | `(1,0)` | `3/2` | `(3/2,0,0)` | `3/2` |
| `2B` | `(0,1)` | `2` | `(0,2,0)` | `2` |

Each vector is nonzero and has determinant `ab + c(a+b)/2 = 0`, and each
trace is positive, so each matrix is positive semidefinite and rank one.
Also `A+B = P+Q = I = (1,1,0)`, and `(1/2)A + (3/2)A = 2A`.

The four targets are

```
A+P = (1,0,1),  A+Q = (2,1,-1),
B+P = (0,1,1),  B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `4I = (4,4,0)`. For
each target `H`, `det(4I-H) = 17/2`, so `4I-H` is not rank one.

## 2. The seven labels sum to 4I

The length-6 witness of PR #7100 is the six matrices `A, B, P, Q, 2A, 2B`.
Their sum is `4I`:

```
A + B + P + Q + 2A + 2B
  = 3A + 3B + (P+Q)
  = 3(A+B) + (A+B)
  = 4I.
```

Those six matrices already sum to `4I`. The only matrix that can be adjoined
while keeping the sum equal to `4I` is `0`, which is not rank one. The
length-7 witness is therefore a replacement, not an extension: substitute

```
2A = (1/2)A + (3/2)A
```

by two positive-semidefinite rank-one matrices. The seven labels sum to the
same `4I`. The two new matrices are distinct from `A` and from each other,
and `2B` is distinct from `B`, so the seven matrices are distinct.

## 3. Each target has exactly one carrier

Write a subset of the seven labels by which of `P` and `Q` it contains,
together with a subset of the axis frames

```
{A, (1/2)A, (3/2)A, B, 2B}.
```

Every axis frame has `c = 0`. The coordinate `c` of `P` is `1` and the
coordinate `c` of `Q` is `-1`, so a subset sum has

```
c = ε_P - ε_Q ∈ {-1, 0, 1}.
```

`A+P` and `B+P` have `c = 1`. `A+Q` and `B+Q` have `c = -1`. A subset with
`c = 0` is not a target, so every carrier contains exactly one of `P` and `Q`.

The `a`-coordinate of a subset of `{A, (1/2)A, (3/2)A}` is a sum of a subset
of `{1, 1/2, 3/2}`. The eight sums are

| subset | `a` |
|---|---|
| empty | `0` |
| `{(1/2)A}` | `1/2` |
| `{A}` | `1` |
| `{(3/2)A}` | `3/2` |
| `{A, (1/2)A}` | `3/2` |
| `{(1/2)A, (3/2)A}` | `2` |
| `{A, (3/2)A}` | `5/2` |
| all three | `3` |

Only the empty subset gives `a = 0`, and only `{A}` gives `a = 1`.

The `b`-coordinate of a subset of `{B, 2B}` is a sum of a subset of `{1, 2}`:
`0`, `1`, `2`, or `3`. Only the empty subset gives `b = 0`, and only `{B}`
gives `b = 1`.

If the subset contains `P` and not `Q`, its sum is `P + (α, β, 0) = (α, β, 1)`.

- `A+P = (1,0,1)` forces `α = 1` and `β = 0`, hence exactly `{A, P}`.
- `B+P = (0,1,1)` forces `α = 0` and `β = 1`, hence exactly `{B, P}`.

If the subset contains `Q` and not `P`, its sum is `Q + (α, β, 0) = (1+α, 1+β, -1)`.

- `A+Q = (2,1,-1)` forces `α = 1` and `β = 0`, hence exactly `{A, Q}`.
- `B+Q = (1,2,-1)` forces `α = 0` and `β = 1`, hence exactly `{B, Q}`.

These four pairs are labels in the witness, so each target is a subset sum.
On this solution each target has that one carrier and no other. The eight-row
table and the four sums `{0,1,2,3}` are the whole case split: they list every
subset of a three-element set and of a two-element set. The verifier also
sums all `2^7 - 1 = 127` nonempty subsets of the seven labels and records the
same four carriers. That scan is exhaustive for this one finite set. It is a
check of one solution. It is not a census of the solutions of the equation.

## 4. Every old triple leaves four added frames

There are four ways to designate `E`, `F`, and `G`. In each case all three
are among the four projectors, so all three are labels. The omitted projector
`H` together with `(1/2)A`, `(3/2)A`, and `2B` are the added frames. Those
four are positive semidefinite and rank one by Section 1, and they are
distinct. Their sum is

```
H + (1/2)A + (3/2)A + 2B = H + 2A + 2B = 2I + H.
```

The three old calls sum to `(A+B+P+Q) - H = 2I - H`, so the determinant
residual is

```
4I - (2I - H) = 2I + H.
```

The added frames meet the residual. The four rows are

| old calls | added frames | residual |
|---|---|---|
| `A, B, P` | `Q, (1/2)A, (3/2)A, 2B` | `2I+Q = (3,3,-1)` |
| `A, B, Q` | `P, (1/2)A, (3/2)A, 2B` | `2I+P = (2,2,1)` |
| `A, P, Q` | `B, (1/2)A, (3/2)A, 2B` | `2I+B = (2,3,0)` |
| `B, P, Q` | `A, (1/2)A, (3/2)A, 2B` | `2I+A = (3,2,0)` |

Every row uses the same seven labels, so the carrier statement of Section 3
applies to each designation. One added frame is the omitted projector. The
other three are proper positive scales of `A` or `B`, hence distinct from
every standard projector.

## 5. This witness fails the odd-c count

Every label in the witness has an integer `c`-coordinate: the two half-integer
frames lie on the `A` axis, so their `c`-coordinate is `0`. Reduction of `c`
modulo 2 is therefore a character of the additive group generated by these
seven matrices. `P` has `c = 1` and `Q` has `c = -1`. The other five labels
have `c` even. Two calls are detected.

All four targets have odd `c`, so four targets are detected. The inherited
call-versus-target inequality in
`research/bit-two-signed-frame-floor/PROOF.md`, Section 1, equation (2),
says that a word needs at least as many detected calls as detected targets.
This note does not reprove that inequality. Under it, the witness is excluded
as a word. Support holds on this solution and is not sufficient for a word.
Nothing here lowers the eight-call minimum or changes the selected record.

## 6. What is not claimed

The length-5 equation `R+S+T+U = 4I-E` is the separate support proof in
PR #7083. The length-6 equation `R+S+T+U = 4I-E-F` is the separate witness
in PR #7100. This witness uses seven labels. Replacing `2A` by two summands
is how it leaves that six-label set; it does not reopen either result.

The odd-`c` question for the length-6 equation is open question 1 of PR #7100
and is a different equation. No statement is made here about a length-7
solution with four or more odd-`c` labels. No statement is made about added
frames on a direction other than `(1,0)`, `(0,1)`, `(1,1)`, or `(1,-1)`.
One solution on the old axes does not classify the solutions that leave
those axes.

## Open next questions

Does any other solution of `R+S+T+U = 4I-E-F-G` meet support and also meet
the odd-`c` count, with at least four labels of odd `c`? This witness has
only two, and both of those are `P` and `Q`. A word at length 7 would be
shorter than the eight-call minimum. The first step is one other solution
whose labels have integer `c` and at least four odd values, then the same
carrier scan. This package does not list the solutions. The same question
for `R+S+T+U = 4I-E-F` remains the length-6 question of PR #7100.
