# Unimodular kernel frames on the selected P112 tetrads

**Exact local reversible-basis witness and a corrected role-scaled budget screen; no supplier or κ improvement is claimed.** Each of the selected provider's 14 source-bound eight-port tetrads has an integer unimodular output-basis change with four rows in the left kernel of its rank-four update matrix. Thus four integer combinations of the eight outputs remain unchanged under that update. A concrete reversible word costs 21 additions, two swaps and one negation per block on one eight-value vector.

The earlier target-specific screen charged this word once per tetrad while using its four invariant combinations across all eight family roles per port. Repeating the explicit word across those eight independent roles costs 192 rank-one-equivalent units per tetrad. Under that direct implementation, at most eight tetrads fit the relaxed coverage mass, and the best feasible target moment is still **1.002886584890 > 1** at `κ=0.003`; nine tetrads already exceed the mass identity. The earlier `κ ≤ 0.0032015701092` joint figure is an **unscaled row-word screen**. The rank-32 coefficient-fusion profile gives a conditional joint ideal ceiling of **0.008697311474**; widening the local-child rank cap to its scalar-model maximum raises the ideal envelope to **0.047807137019**. Neither has a selected consumer or physical suppliers.

The earlier whole-basis table charged the 14 row words once each: 336 rank-one-equivalent units for the forward transform, with an ideal κ ceiling **0.0113664769475** under the hypothetical two-unpaid law; charging the inverse as well gave 672 units and ceiling **0.00967666247328**. Those figures do not repeat the transform over the family roles; they are planning screens, not direct role-wise implementation invoices. Neither profile is a physical supplier. The selected κ remains **0.001672660197076918**.

## Exact construction

For one tetrad, write its two signed four-frames as invertible Hadamard matrices `E0` and `E1`, and stack them as `E`. The update matrix is `K = E E^T`, with rank four. Since `E0 E1^T` has entries `±2`, the left-kernel equation for a coefficient vector `(x0,x1)` is

`x0 = -(E0 E1^T / 4) x1`.

The top block is integral exactly on the even-coordinate-sum sublattice used here. The verifier uses the integer basis

```text
D = [[ 1,  0,  0, 0],
      [ 0,  1,  0, 0],
      [ 0,  0,  1, 0],
      [-1, -1, -1, 2]]
```

and forms the four kernel rows from `N = [-(E0 E1^T)D/4; D]`. Appending the four standard rows at coordinates `(0,5,6,7)` gives `U`. On all 14 blocks the exact checks give `det(U)=-1` and the first four rows of `U K` are zero. The row-reduction witness synthesizes `U` from reversible integer shears, swaps and a sign change. Therefore the transform works on every dirty integer output vector, not only on a clean or zero workspace. It also shows why the earlier unweighted anchor sums were insufficient: those sums coincide, while the full left kernel has rank four.

The transform exposes 56 invariant combinations across the 14 blocks, but this is **not** a proof of 56 unpaid recursive coordinates. The current provider/caller contract does not accept this output basis, and the coefficient binding still does not identify a chronological physical cut or the complete 896-family coverage identity.

## Budget hinge

The source-bound complex ideal profile before this change is `{1:192, 2:56, 32:166}`, priced under the hypothetical two-unpaid-coordinate law. To avoid treating swaps or sign changes as free, the screen charges all 21 additions, two swaps and one negation per block as rank-one units:

| Endpoint contract | Added rank-one units | Profile per call | Moment upper at `a=1/99` | Ideal κ ceiling |
|---|---:|---|---:|---:|
| Consumer accepts the transformed basis | 336 | `{1:528, 2:56, 32:166}` | 0.998529602465 | 0.0113664769475 |
| Transform, then restore the original basis | 672 | `{1:864, 2:56, 32:166}` | 1.000409507302 | 0.00967666247328 |

These use the pinned complex ceiling engine and the same ideal rank-32 budget as the predecessor route. The first case clears `κ=0.01` only if the transformed basis can flow directly into a legal caller without inverse restoration. The second case fails that threshold even before source access, hosting, precision and the other physical obligations are priced. The bit-side endpoint also remains unchanged. No OR-Tools or solver is used.

## Target-specific screen for κ > 0.003

The lower target needs only `a = 3/997` under the retained planning conversion
`κ = a/(1+a)`. I screened partial use of the exact tetrad transforms together
with a separately repriced bit profile. This gives a joint ideal-budget route
just above 0.003 without assigning two unpaid coordinates to every complex or
bit family:

| Side | Changed ideal profile per call | Coverage | Moment upper at `a=3/997` | Ideal κ ceiling |
|---|---|---|---:|---:|
| Complex | 10 transformed tetrads; `{1:432, 2:56, 32:166}`; transform overcharge 240 rank-one units | `u=19/14`, centre charge 112 | 0.999782454490 | 0.003218934400 |
| Bit | `{8:641}`; one local mass unit moved to idle; inherited surcharge included | `u=1`, copy charge 63, idle cap 45 | 0.999642235857 | 0.003201570109 |

The unscaled joint screen is limited by the bit row, so its optimistic ideal
ceiling is **κ ≤ 0.003201570109**. This treats the eight-value row word as
one rank-one-equivalent invoice while using its invariants across eight family
roles. For comparison, allowing a fractional `5129/8` local
rank-8 count gives the slightly lower cap `0.003201073477`. The boundary
control is sharp for the proposed complex
count: nine transformed tetrads give a moment lower bound above one
(`1.000232875069`), while ten give an upper bound below one. Each transformed
block exposes four invariant combinations among eight ports; with eight live
family roles per port, ten blocks correspond to the hypothetical average
`u = 1 + 4·10/112 = 19/14`. The unscaled model charges the 21 adds, two swaps
and one negation once per block; it does not charge their repetition over the
eight roles.

### Direct role-repetition audit

The target coverage gain is `u = 1 + k/28` after `k` tetrads because each
block contributes four invariant combinations for each of eight family roles.
The synthesized 24-operation word acts on one eight-value vector, so the
straightforward role-by-role implementation adds `24·8 = 192` rank-one-
equivalent units per tetrad. Keeping the same rank-32 children and repricing
the replacement coverage identity gives:

| Repeated tetrads | Added rank-one-equivalent units | Local mass | Coverage allowance | Moment upper at `a=3/997` |
|---:|---:|---:|---:|---:|
| 8 | 1,536 | 7,152 | `65264/9` | 1.002886584890 |
| 9 | 1,728 | 7,344 | 7,248 | infeasible: local mass exceeds allowance by 96 |

The verifier checks every count from zero through fourteen. All mass-feasible
counts (zero through eight) fail the target moment; nine through fourteen
violate the replacement mass identity. This closes only the direct repeated-
word realization. It does not rule out integrating the basis change into a
changed consumer. The next section checks that coefficient-map fusion exactly.

### Fuse the basis change into the decoder coefficients

There is a cheaper algebraic route than running the reversible word. The
existing four decoder terms on a tetrad are the columns of E, giving
K = E E-transpose. If the consumer accepts the U output basis, compose U into
their output coefficient vectors:

    K_new = U K = (U E) E-transpose.

The first four rows of U E are zero. Replaying all 14 blocks against the
selected port-pairing matrix shows that the original 56 terms each have copy
rank 2, while all 56 composed terms have copy rank 1. Thus the same exact
coefficient identity changes the decoder profile from {2:56} (mass 112) to
{1:56} (mass 56), without adding the runtime row-word invoice. This is a
source-bound coefficient-map result; a selected chronological consumer has
not yet been shown to accept the changed basis.

For k transformed tetrads, the repriced profile is
{1:192+4k, 2:56-4k, 32:166}, the centre charge is 112-4k, and the
hypothetical unpaid average is u=1+k/28. Exact interval pricing at
a=3/997 gives:

| Tetrads | Profile per call | Centre charge | u | Moment upper | Complex ideal κ ceiling |
|---:|---|---:|---:|---:|---:|
| 4 | {1:208, 2:40, 32:166} | 96 | 8/7 | 1.000106721134 | fails |
| 5 | {1:212, 2:36, 32:166} | 92 | 33/28 | 0.999061736347 | 0.004097178442 |
| 9 | {1:228, 2:20, 32:166} | 76 | 37/28 | 0.994881797197 | 0.008985332615 |

Five blocks are the first count that clears the target. For a stronger joint
screen, retain the bit supplier's nine rank-7 copies and replace its remaining
5,066 local rank-mass units by 158 rank-32 children plus ten idle units. With
one unpaid coordinate, copy charge 63 and the inherited surcharge retained,
that integer bit profile has ideal κ ceiling **0.008697311474**. Nine fused
complex blocks raise the complex ideal cap above it; eight reach only
0.007763240725. Thus the two-side ideal ceiling is **κ ≤ 0.008697311474**,
limited by the bit profile. The complex rank-32 children, bit rank-32
repacking, changed consumer and complete outer invoices remain
unimplemented, so the selected κ is unchanged.

### Relaxed maximum-rank envelope

To test how much the rank-32 choice itself limits the target, the verifier also
allows each ideal local child to have any integer rank below its parent
dimension: at most 72 on the complex side (`m=73`) and 63 on the bit side
(`m=64`). The existing idle/remainder cap remains 51 and 45, respectively.
At positive `a`, a unit of paid mass has lower moment cost at larger child
rank. Greedily filling the largest allowed local rank and then comparing the
remainder with the idle cap therefore minimizes the moment among profiles
with the same mass and these rank ceilings.

With all 14 tetrads fused, the complex profile becomes
`{1:248, 72:73, 56:1}`: the 166 rank-32 children (mass 5,312) are replaced by
73 rank-72 children and one rank-56 child. It retains centre charge 56 and
`u=3/2`; its exact ideal κ ceiling is **0.047807137019**. The bit side keeps
its nine rank-7 copies and uses 80 rank-63 children for 5,040 of the remaining
5,066 local mass units; 26 units join the rank-45 idle pool. Including the
inherited surcharge, its ideal κ ceiling is **0.052325479402**. The joint
envelope is therefore limited by the complex side at **κ ≤ 0.047807137019**.

Under this expanded local-rank relaxation, three fused tetrads are the first
to pass `κ=0.003`: two fail the target moment, while three give a joint ideal
ceiling of **0.005390681416**. The full 14-tetrad envelope is about 28.6 times
the selected κ, but this remains a pricing envelope, not a found supplier or a
new selected result. The near-full-rank children, family-level unpaid map,
chronological consumer, and complete physical invoices are unresolved. The
greedy rank argument applies only to this fixed-mass scalar pricing
relaxation; it does not show these profiles can be constructed.

### Earlier rank-8 control and implementation headroom

The earlier bit rank-8 control does not depend on a fractional number of
local rank-8 calls.
Using **641 rank-8 children** accounts for 5,128 of the 5,129 local rank-mass
units; the last unit is put into the rank-45 idle remainder. This removes
fractional local-child counts only; the reorganization into rank-8 children is
still hypothetical.

At `a=3/997`, the unscaled one-copy and rank-8 control profiles have little
room for additional rank-one-equivalent cost. Their exact boundary is 132 extra
rank-one units per complex call (moment `0.999998848969`); 133 fails
(`1.000000488321`). On the
bit side, 195 extra units pass (`0.999998362601`) and 196 fail
(`1.000000188892`), including the inherited surcharge. These are cost
allowances for a future implementation, not estimates of its cost. Any source,
frame, restoration, ownership or precision work must fit inside the allowance
or the target is lost.

The one-copy result is a target-budget screen only. The `u=19/14` identity is
not derived for the full complex provider: invariant linear combinations are
not automatically unadvanced recursive coordinates, and no selected caller
is shown to accept the hybrid basis. The direct repeated-word implementation
misses the target before source access, hosting, precision or consumer costs.
The complex rank-32 and maximum-rank children are also only ideal profiles.
On the bit side, even the integer counts have no physical block implementation
or new owner map. No supplier, outer assembly, or selected κ improvement
follows. The selected record remains **0.001672660197076918**.

## Open next questions

1. Can the source-bound U coefficient map be carried through a real selected consumer cut? First bind one transformed tetrad to its chronological producer output and consumer coefficients, then replay the dirty-input identity. Blocker: the selected contract still names the original basis; the coefficient fusion is static and has no chronological provider/caller trace.
2. Do the 32 invariant coordinates in one tetrad block correspond to unpaid recursive coordinates across the eight roles and all 896 complex families? First derive the complete source, owner and endpoint map for one transformed block. Blocker: the current witness binds coefficient ports but not a recursive family path.
3. Can the complex rank-72/rank-56 and bit rank-63 profiles be realized within the remaining physical invoices? First build and replay one dirty-input child block on each side; count source access, frames, hosting, restoration and precision. Blocker: the near-full-rank profiles are ideal repackings without physical local words or complete outer bills.

## Reproduce

From the repository root:

```sh
python3 -I -B research/p112-tetrad-dual-anchor-screen/verify.py
python3 scripts/research_package.py --package research/p112-tetrad-dual-anchor-screen --check-only
python3.12 scripts/research_package.py --package research/p112-tetrad-dual-anchor-screen
```

The verifier pins the selected replay, source-bound port map, P112 frame proof, exact complex ceiling engine, and the bit supplier's word, invoice and pricing engine. It reconstructs all 14 blocks, checks the old signed-anchor controls, derives every `U`, verifies determinant and kernel equations, synthesizes and reverses each dirty-output word, composes the output coefficient map and checks its exact U K matrix and all 56 rank-one copy costs, then recomputes the direct and fused target-0.003 boundaries, integer rank-8/rank-32 controls, maximum-local-rank envelope, overhead controls and zero-through-fourteen direct role-repetition table with exact interval arithmetic.

## Credit

This screen builds on the P112 root/frame geometry in [p112-tetrad-local-decoder](../p112-tetrad-local-decoder/README.md), the selected port bijection and ideal rank-32 budget in [selected-p112-tetrad-rank32-route](../selected-p112-tetrad-rank32-route/README.md), and the bit profile and pricing engine in [bit-revision3-levers-seed03](../bit-revision3-levers-seed03/README.md). Those predecessors retain their original attribution and broader claims. Prepared by Codex with user direction and substantial OpenAI assistance. Apache-2.0.
