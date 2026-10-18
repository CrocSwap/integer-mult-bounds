# Cheaper balanced ternary dirty echoes

**Construction / recursive-interface research; no new multiplication κ.**
At fanout three, androolloyd's
[PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) executes the
first and last child twice and the middle child four times. Its balanced split
puts remainder factors in the first blocks, sometimes making the middle child
longer. Placing extra factors at the **ends** reduces the complete recursive
leaf count: at 15 factors, **208 → 160 calls with the same 5 borrowed arrays**.
All forward, inverse and restoration calls are included. These are operation
counts, not measured runtime improvements.

The contribution is a proof that this placement minimizes **uniform leaf-call
count among recursively balanced ternary splits**, an implementation, and an
independent symbolic audit of the actual pinned PR673 instruction generator.
The audit checks arbitrary nonlinear restoration and the ideal noncommutative
product. It also confirms that changing only PR673's partition hook produces
exactly the new word, for both signs, on the stated finite domain.

PR673 already supplies the general multiway echo and its subquadratic call
bound. This refinement preserves its ternary exponent `α = log₃ 8` and scratch
bound; it improves counts at nonuniform splits. PR673's other fanouts offer
different call/workspace tradeoffs. No optimum over those choices, unbalanced
splits, or unequal leaf costs is asserted. The rounded leaves and inherited
precision assumptions come from Chafik Boukhalfa's
[PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628).

## Reproduction and source boundary

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -B research/ternary-dirty-composition/verify.py
```

Expected final line: `PASS_TERNARY_DIRTY_COMPOSITION`. The checker authenticates
the vendored inputs, recomputes every certificate field, and compares the
complete result with [EXPECTED.json](EXPECTED.json). All new checks use explicit
exceptions and stay active under `python3 -I -O -B`. For a new output file, use
`--write /absolute/new/certificate.json`; an existing file is rejected.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR628 dependency: `0768f97d06c623b8211e651543c66135796b62bf`.
PR673 dependency: `0e35f56cab3cae1eb0a99447135569d687c5695a`.
The retained files are byte-exact in [vendor/pr628](vendor/pr628) and
[vendor/pr673](vendor/pr673), with SHA-256 and original paths in
[SOURCES.json](SOURCES.json). PR663 at
`e0e546fd01b396478c68b6b6c5a16d87515983ba` is credited for the independent
binary audit and sharp count; it is not an executable dependency. No pending PR
must be merged to replay this package. The assignment, candidate selection,
overlap checks, and time limit are recorded in [CLAIM.json](CLAIM.json).

At this base, the selected conditional value is
`51110230636731/31250000000000000 = 0.001635527380375392`, from #626/#543.
Its certificate is `research/community-k492-audit/pr626/replay/ASSEMBLY.json`,
SHA-256 `6127732e2fcdd470dab349c1c51d03cd9f0787ad0309b1b4a7c811a908028f4e`.
The associated `docs/research/community-k492-review.md` retains the all-size,
compiler, hosting, normalized-residual, precision, tape, and analytic assumptions.
This package changes none of those suppliers or the selected pointer.

## Interface and eight-call identity

Arrays are elements of an abelian group. A child call adds a deterministic
function of its source and the **initial deeper scratch** to its target,
preserves its source, restores every deeper scratch array, and has an increment
independent of its target. Its negative call is the exact inverse instruction
word. Read-only factors, phases, and coefficients stay fixed between calls.
All active source, target, and scratch arrays are distinct; no ancestor array
is reused as deeper scratch. Overlapping views and hidden mutable dependencies
are outside this contract.

Let `A`, `B`, `C` be the three consecutive factor-block functions and `u,v` two
borrowed arrays. PR673's chronological eight-call sequence at fanout three is

```text
u += A(x)
v += B(u)
y += C(v)
v -= B(u)
u -= A(x)
v += B(u)
y -= C(v)
v -= B(u)
```

Every call restores the same deeper scratch `t`. For initial `u₀,v₀`, write

```text
a = A(x;t).
```

The first target update sees `v₀+B(u₀+a;t)`. Calls four and five restore
`v₀,u₀`; the second target update sees `v₀+B(u₀;t)`. The final call restores
`v₀` again. The target increment is

```text
C(v₀+B(u₀+a;t);t) - C(v₀+B(u₀;t);t).
```

It does not depend on the initial target. This proves the recursive interface
by induction, even for nonlinear functions. The exact inverse reverses the
eight calls and reverses their signs, recursively. Negating signs without
reversing order is not valid in general.

For ideal linear children, the two arguments differ by `BAx`, and the increment
is `CBAx`. Induction thus
gives `Fₙ₋₁ ... F₁ F₀ x` in the original factor-list order. Commutation is not
assumed. The ideal increment is independent of all dirt. The rounded increment
can depend on dirt: `A(x)=x, B(u)=u², C(v)=v, x=1` gives increments `1` and `3`
for `u₀=0` and `u₀=1`, although both scratch arrays are exactly restored.

## Optimal placement within balanced ternary recursion

There is no search or factor reordering. Seed 58 selects arity
`2 + (58 mod 3) = 3`. At `n>=3`, write `n=3q+r`, `0<=r<3`, and split the
original list into consecutive lengths

```text
a = q + [r>=1],  b = q,  c = q + [r=2].
```

The longer blocks go to the ends, which execute twice; the middle executes
four times. For a singleton there is one leaf and no scratch. For two factors,
the ordinary four-call binary commutator uses one scratch array. Exactly:

```text
N(1)=1, N(2)=4;  N(n)=2N(a)+4N(b)+2N(c)  (n>=3)
S(1)=0, S(2)=1;  S(n)=2+max(S(a),S(b),S(c))  (n>=3).
```

**Optimality in this class.** A balanced split has sizes `q` or `q+1`. The
displayed placement gives

```text
N(3q)   = 8N(q)
N(3q+1) = 6N(q) + 2N(q+1)
N(3q+2) = 4N(q) + 4N(q+1).
```

These values are strictly increasing. Indeed `N(2)-N(1)=3` and
`N(3)-N(2)=4`; for every `q>=1`, the next three successive differences are
`2Δ, 2Δ, 4Δ`, with `Δ=N(q+1)-N(q)>0` by strong induction. For any larger
child placed in the middle while a smaller one is at an end, exchanging their
sizes saves `2(N(q+1)-N(q))>0`. Optimizing each child recursively and applying
this exchange proves the minimum over all recursively balanced ternary size
placements. Blocks stay contiguous and factors keep their original order;
only the cut positions change. This argument uses uniform leaf-call costs.

**Workspace.** No child, inverse, source restoration, or identity factor is
omitted. Children
reuse the same deeper pool **sequentially**, so peak storage takes a maximum,
not a sum. Every balanced placement has the same multiset of child sizes, so
the scratch recurrence is unchanged from PR673 at fanout three. For `n=3^d`,
`N(n)=8^d` and `S(n)=2d`. In general let
`h=ceil(log₃ n)`. Every child has length at most `ceil(n/3) <= 3^(h-1)`;
induction gives `N(n)<=8^h < 8 n^α` and `S(n)<=2h`, with the singleton handled
separately. Hence the all-`n` bounds are `O(n^α)` calls and `O(log n)` arrays.
The strict comparison `α<2` follows from `8<9`, not a numerical logarithm.

For completeness, if `3^d <= n < 3^(d+1)`, the exact scratch count is `2d`
when `n=3^d`, `2d+1` when `3^d<n<=2·3^d`, and `2d+2` otherwise. Follow the
largest child `ceil(n/3)` repeatedly: after `d` ternary levels the remaining
size is one, two, or three respectively. A size-two node costs one further
array; a size-three node costs two. Finite checks separately compare this
formula against both the resource calculator and emitted array addresses.

| Factors | PR673 ternary leaves | Refined leaves | Arrays, both words |
|---:|---:|---:|---:|
| 3 | 8 | 8 | 2 |
| 5 | 26 | 20 | 3 |
| 8 | 56 | 48 | 4 |
| 14 | 184 | 136 | 5 |
| 15 | 208 | 160 | 5 |
| 31 | 656 | 632 | 7 |
| 58 | 2,240 | 2,208 | 8 |
| 63 | 2,560 | 2,560 | 8 |
| 127 | 11,872 | 8,800 | 9 |
| 255 | 35,072 | 34,688 | 11 |

As a secondary comparison, PR628's binary word at `n=15` uses 232 calls and
4 arrays; at `n=63`, it uses 4,000 calls and 6 arrays. Ternary recursion thus
still trades more arrays for fewer calls against that baseline. The binary
counts use PR663's `3qn-2q²`, `q=2^floor(log₂ n)`, checked against PR628's
actual dispatcher through 64 factors. The seed-selected `n=58` diagnostic is a
generic product, not a claim of a prime-power kernel at radix 59. `n=63` is the
factor count for radix 64, but its table entry is accounting, not an executed
radix-64 coefficient or kernel certificate.

## Rounded execution, preparation, and complete paid scope

Inherit PR628's leaf hypotheses for both signs: each ideal factor has norm at
most `K=r/beta`, and a completed rounded leaf has error at most
`a u (B+1)`, where `a=13(r+1)/beta³`, `u=2^-w`, and `B` bounds its source.
Require `a u<=1` and `u<=beta²/2`. The leaf restores its temporarily modified
source by inverse causal lifts. The new dispatcher invokes that unchanged
leaf; it does not insert a transform, copy, or unpriced restoration between
children.

Let `M_j` be the maximum array norm after `j` completed leaves and let initial
norms be at most `D`. With `G=2+K`,

```text
M_(j+1) <= (1+K) M_j + a u (M_j+1)
M_j + 1 <= G^j (D+1).
```

Comparing to the ideal word on the same initial arrays, its error satisfies
`E_(j+1) <= (1+K)E_j + a u G^j(D+1)`. Consequently the final error is at most

```text
N(n) a (D+1) u G^(N(n)-1).
```

Thus it suffices to choose

```text
w >= p+1+ceil(log₂(N(n) a (D+1))) + (N(n)-1)ceil(log₂ G),
```

in addition to the two leaf precision conditions. Execution then consumes at
most half the `2^-p` error budget. PR628's independent factor/phase preparation
must still supply the other half, scaled by the original source magnitude:
use its preparation target `p+1+ceil(log₂(max(1,||x||)))`. Dirt enters the
execution bound but not the ideal operator perturbation. This is conditional
on the inherited leaf and preparation estimates, not a new audit of them.

All cost components remain visible:

| Resource | Charge / condition |
|---|---|
| Completed leaves | Exactly `N(n)`, including every inverse leaf |
| Mutable array space | Source, target, and `S(n)` arbitrary length-`L` arrays; `O(L(S(n)+2)w)` bits, with transient integer magnitude included in word size |
| Leaf traversal | Three computational passes (`3L` loop visits) per leaf, plus its coefficient-stability and grid-validation scans; `O(L)` arithmetic work per call |
| Source and phase access | Every causal update, closure-product update, target update, and undo is paid. The leaf uses `(5L-2)` phase reads for an outer factor and `(6L-2)` for an inner factor. Multiply by each factor's actual occurrence count. The test fixture separately checks its `L` unit phases; a concrete public phase-taking wrapper must admit immutable, nonaliasing phases and charge that scan |
| Helpers / restoration | Two outer borrowed arrays at each ternary level; deeper pools reused only after exact restoration. No zero-initialized length-`L` helper is required |
| Control | Streamed word, `O(log n)` live control frames / `O(log² n)` indexing bits, plus `O(n)` read-only factor descriptors; no expanded instruction list in `compose` |
| Arithmetic | PR628's charged clean scalar arithmetic and counters; no reversible-bit implementation supplied |
| Coefficient and phase preparation | The same certified approximations, enclosures, original-input scaling, and charged oracle/table access as PR628 |
| Normalization / frame changes | The radix scalar is included in one leaf's multiplier and its error bound. No additional frame conversion appears in this array-level construction; conversion to a physical supplier remains an obligation |
| Routing | Neighboring cyclic layout in either direction. PR628's arbitrary-stride two-sort cost remains additional; no free route or owner allocation is assumed |

Under PR628's `log₂(beta^-1)=O(r³)`, `n=r-1`, these bounds give
`w=O(p+log(D+1)+r^(3+α))` and `O(r^α)` leaf passes. Interior causal/closure
magnitudes add only `O(log(beta^-1)+log r)` bits per leaf beyond the completed
array bound. With the **same conditional fast-arithmetic and preparation
interfaces**, the resulting work bound is

```text
soft-O((L r^α + r³) (p + log(D+1) + r^(3+α)))
```

plus charged phase-oracle and routing costs. The exact-rational prototype is
not an implementation or benchmark of that fast bit bound. A fixed number of
dirty data arrays, common-label realization, fixed-tape scheduling, complete
transform composition, analytic transfer, and integer multiplication are still
outside the result. No currently binding supplier/assembly constraint changes,
so none of these local savings imply a new complex exponent or κ.

## Evidence and stopping rule

The refined schedule is tested with free nonlinear function terms and
independent noncommutative linear expressions for every `n=1,...,64`, plus
`81,128,243`. The pinned PR673 generator is independently checked with both
engines for `n=1,...,64` and `81,127,128,243,255`. On that same 69-case domain,
replacing only its partition function in memory emits exactly the refined
forward and inverse words, with the same scratch count. Vendored source bytes
remain unchanged. This audits PR673's fanout-three word and resource functions;
its other fanouts, phase-alias repair, and κ appendix are outside this audit.

The checker also minimizes over all 23,328 balanced size placements arising
for `n=3,...,10000`, using independent dynamic programming. It agrees with the
refined recurrence in all 10,000 sizes, finds strict savings over the original
ternary placement at 9,919 sizes, and checks the closed scratch formula.
The written induction supplies the all-`n` proof; this finite replay is not a
formal proof of the full multiplication theorem.

Rounded tests use the unchanged PR628 leaf with mixed inside/outside factors,
both cycle directions, nonzero targets, arbitrary dirty arrays, a spectator,
independent dense inverse solves, and exact whole-word inversion. Additional
cases use PR628's authenticated factor certificates at radices 4, 9, and 16
and independently expand the complete kernel polynomial. They certify the
execution error against the represented factors; the separately inherited
coefficient perturbation remains part of the full kernel accuracy contract.

Controls remove or flip each of the 64 leaves of the `n=9` word, reverse factor
order, alias the two ternary scratch roles, misuse inverse ordering, violate
the public array interface, and demonstrate nonlinear dependence on dirt.
There are 141 rejecting controls, plus the concrete nonlinear dirt example.
The complete finite domains, case digests, and results are in EXPECTED.json.
The integer budget domain is all prime-power `r` in `[3,256]`, targets
`{1,128,1048576}`, and initial-magnitude bit bounds `{0,20,1024}`. There is no
search exhaustion or general impossibility claim. Work stops after this fixed
refinement, its stated coverage, and independent review; other arities,
unbalanced splits, unequal leaf costs, and supplier integration are not
investigated here.

## Credit and license

Prepared by **Dillon Amburgey**, with substantial **OpenAI Codex** assistance.
[NOTICE.md](NOTICE.md) preserves predecessor and related-work attribution.
All new files use Apache-2.0; the original PR628 notice and PR673 source credit
are retained verbatim. The echo construction and its exponent are credited to
PR673. This contribution is the balanced ternary placement minimum, its
scratch-preserving savings, and independent symbolic and rounded evidence.
