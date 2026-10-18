# Exact conditional composition and one-coordinate optimality

## Fixed objects

The source is the selected PR1094 forward/backward scalar word. PR1263 lists
237 eligible helpers in sorted order; OS seed 22 selects its entry at
zero-based index 22, helper L248. This lies outside PR1259's seed-37 slice
`[37:53]`. Let `g_h` be PR1263's constant integer exponent for eligible helper
`h`. L248 is in its 218-helper support, with exponents −2 forward and +2
backward. This experiment freezes `g_h` for every `h != 248`.

Enumerate the 71 original ADD events incident with L248 in chronological
order. Let event `j` have original dyadic coefficient `q_j`; put `s_j=+1` when
L248 is its target and `s_j=-1` when it is its source. Let `b_j` be the target
gauge minus source gauge contributed by all the frozen helpers other than
L248. An integer path `x_1,...,x_71` means that L248 carries scale `2^x_j`
immediately before event `j`. Its corrected coefficient is exactly

```text
q'_j = q_j * 2^(b_j + s_j*x_j).
```

Every original event stays in order. Before the first use, between uses, and
after the last use, L248 is moved between the requested exponents with paid
SCALE macros. Its input and output gauges are both zero, so arbitrary initial
L248 dirt is restored. The other 217 helpers retain their paid PR1263 entry and
exit scales. Each inserted SCALE uses the original helper frame at that event;
L248's final restoration uses its FULL frame. The helper has no residual
adapter, COPY or CLEAR use, and the frozen gauges have the same exclusions as
PR1263. Original SCALE operations commute with these positive dyadic gauges.

## Complete local objective

Write a nonzero dyadic coefficient in reduced form as `q = p*2^v`, where `p`
is an odd positive integer and the sign is carried by the ADD opcode. PR696's
copy-init lowerer uses

```text
P(q) = 1 + bit_length(p) + popcount(p) + |v|
       - 1[p=1 and v=0].
```

The complete real-component cost affected by the path is

```text
Σ_j P(q_j * 2^(b_j+s_j*x_j))
  + |x_1| + Σ_(j=2..71) |x_j-x_(j-1)| + |x_71|.
```

The second line is the exact PR696 cost of every inserted L248 SCALE, including
entry and restoration. All nonincident ADDs and the other helpers' boundary
scales are constant across this optimization. The frozen PR1263 L248 gauge has
cost `2|g_248| + Σ_j P(q_j*2^(b_j+s_j*g_248))` in the same local accounting.
The verifier checks that the difference of these two local objectives equals
the difference in literal lowerer counts for the full scalar word.

## Why the integer search is complete

For term `j`, let `v_j` be the exponent of the dyadic `q_j*2^b_j`. The only
integer breakpoint of its variable cost is `-s_j*v_j`: apart from its constant
odd-part cost, `P` is `|v_j+s_j*x|` with the possible one-unit discount at the
same point when the odd part is 1. Define

```text
B = {0} ∪ {-s_j*v_j : 1 ≤ j ≤ 71}
I = [min(B), max(B)] ∩ Z.
```

Clamping any exponent to `I` cannot increase its node cost, because the cost
outside the interval has an outward absolute-value slope and no discount
outside its breakpoint. Clamping is 1-Lipschitz, so it cannot increase any
adjacent transition or either boundary cost. Thus some optimal integer path
lies entirely in `I`. This is the proof of the finite domain; the search does
not rely on a large but unproved cutoff.

The exact dynamic program is

```text
D_0(0)=0
D_j(x)=P(q_j*2^(b_j+s_j*x)) + min_y (D_(j-1)(y)+|x-y|)
answer=min_x (D_71(x)+|x|).
```

For L248 the exact domains are `[-10,2]` forward and `[-2,10]` backward. The
implementation enumerates every `x,y` in `I`, retaining a deterministic
tie-break by SCALE macro count, exponent L1 norm, and lexicographic schedule.
It checks its analytic price formula against literal PR696 lowering at every
visited local coefficient. The two orientations are optimized independently;
the resulting reverse path is checked to be the termwise negation of the
forward path.

## Evidence and boundary

The independent replay checks the full 712-column dirty-state map and the
literal primitive stream on three exact dirty-input fixtures per orientation,
including the coefficient-work register. The complete bill, positive prefix
envelope, denominator depth and predecessor paid profile are included in
`RESULT.json`. Source hashes and Git blob IDs are in `SOURCES.json`.

This proves a finite scalar construction and an exact optimum only in the class
where L248 has an arbitrary integer scale schedule and every other helper is
frozen to PR1263's constant vector. It does not establish native compiler or
hosted-controller admission, a new recursive profile, a new κ, or an optimum
over other changing helpers.
