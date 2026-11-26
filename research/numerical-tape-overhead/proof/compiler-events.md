# Finite events in one native interchange

The event inventory connects [coefficient preparation](compiler-labels.md), [geometry](compiler-geometry.md), [factor masks](compiler-factor.md), and [repair](compiler-spectral.md) to the physical tape primitives. It prices unweighted repetitions against the parent volume. The smaller weighted sum used for recursive child time is recorded separately below.

Use `m>=4096`, `t>=1`, `N<=m^5`, `D_g<=m`, `B<=7m`, `D_p<=24 sqrt(m)`, and at most `m^8` nodes in the actual predictor. A physical event here means a grouped role copy/merge, ordinary scalar-stream pass, grade-slice movement, geometry-list generation/application step, or instruction to hand a specified argument to a spatial child. Sequential invocation over a repeated prefix is one grouped request. An *individual scalar coefficient* may be recomputed at every record of a pass. Every call operates on at most the loaded/padded parent volume (less than `2V`), apart from explicitly counted role-local tags and fixed banks. Generating physical range descriptors and moving tape heads within each event have their own transition counts.

### Construction and finite recursion

Construct the short-word controller, the original label tables, the scalar field and shift tables, and the copied formula once for the native node. Their total processing is below `3m^60` transitions using the displayed construction bounds. Retained arrays together occupy less than `M=m^32` short words: label tables use at most `16(N+1)^3`, field tables at most `4m^6`, formula and token workspace less than `256m^8`. Additions, output directories and temporary elimination rows fit within the considerable unused part of the shared bank.

For `h_r=ceil(log2(m)/4)` all three order-three transforms together have at most `3(4^(h_r+1)−1)/3 <16 sqrt(m)` finite tree nodes and at most `3*4^h_r <=12 sqrt(m)` leaves, counting every temporal call. Each internal node has two predictor evaluations of at most `D_p` pencil stages apiece. At most `768m<=m^2` pencils occur in the entire native word. Each leaf executes exactly `m` direct copied swaps and the comparison/pointwise operations in its actual query direction. These are grouped over the leaf's full independent array. Every finite converter repeats its four child phases including the direction-specific pointwise diagonals. Those four are precisely the descendants already counted by this finite tree.

### Actual shared pencil, ignoring child mass for local time

Let `C` be the number of directed rectangles and `r` the selected label rank. Since the pieces are nonempty and pairwise disjoint, `C<=N^2` and `r<=N`. Use the actual [two-pass schedule](foundations/uniform-payload-shared-pencil.md).

| Event in one pencil | Number of sequences before the elementary-list expansion |
|---|---:|
| Source preparation; two destination returns | at most `3NC` in total |
| For each query, source lower map / negative destination lower map / positive destination lower map | at most `3mNC` |
| Fixed-layout conversions for row gather and column scatter, including singletons | at most `2mr(C+1)` |
| Combined sum/coefficient at a rectangle, middle rank coordinates, singleton and retained-original comparison terms | at most `16m(N+1)^2` scalar-slice applications |
| Rank matrix gather-middle product in the prescribed pairing order | at most `m r^2` aligned pairwise multiply-by-bit/add operations, including zeros |

In the scalar count one may instantiate both `A_(j,1)` and `A_(j,2)` separately: at most two slices for each of `(rectangle,query)` and `(rank coordinate,query)`, at most two original-layout comparisons per `(label,query)`, and the constant slice per label. The displayed larger bound allows for both signs and copies from retained input. In fixed-common rank conversion, iterate only the terms of the actual support using directory flags; the upper counts may instead bill all candidate iterations. In either case issue each genuine coordinate change exactly as prescribed. A membership rejection never issues a spatial child.

There are fewer than `16m(N+1)^3` geometry sequences per pencil with slack for empty-incidence tests. Each may compile up to `48D_g` operations. Counting the elementary transformations, the up-to-two child calls each can issue, and their input/output bookkeeping by a further factor 8 keeps their unweighted number over all pencils below `m^22`. Allow a short field-and-sign constant for intermediate operations. All grade increments, listed lower transforms, scalar masks, finite setup, and ordinary scans are outside recursive service.

### Coarse roles, grades and finite repair

| Per-node source of unweighted events | Numerical majorant |
|---|---:|
| An actual coefficient slice over all shifts/duplicate roles | Split at most `32B<=m^2` roles; at most `2m^8` tokens per role; each has one masked streaming copy, at most `m^8` grade increments, and one streaming sum. Each increment can take at most `m` role copies. Budget `16(32B)(2m^8+1)(m^9+3)` events per slice including extraction, deposit and clearing. |
| Outside/padded role assembly and complete converters | In a four-phase repair, one direction's regroup sends `(p=16r+q,label,family,check)` to `(r,label,child_role)` with `child_role=(2q+family)B+check` in `[32B]`. Thus each direction has at most `32BN` source/destination role pairs across common prefix/range; each of the four phases has both directions. At most `512BN` grouped moves including copies and clears. |
| Checks, transpose lifts and spectral table | At most `64(32B+1)^2` aligned role-pair passes per internal finite node. Tag one current role at a time, append at most `m` trits by distinct comparison passes, and strip the tags before each converter call. This is at most `256(32B+1)^2(m+1)` events per such node. |
| Ordinary order-three diagonals and direct-leaf comparison | A constant number of completed diagonals per finite node, every diagonal at most `m` physical comparisons/ordinary passes. Even using one pass per shift/duplicate, `1024(B+1)(m+1)` events suffice per node. |

These loop bounds give **at most `m^38` unweighted events per native finite body**. For example, a pencil has at most `16m(N+1)^2<=m^12` slices and there are `<=m^2` pencils. The slice count in the first row takes less than `m^21` events even using `32B<=m²`. Their product is below `m^35`. The other rows, the geometric events, the `mr²` additions and setup loops together fit the remaining slack. Setup itself is paid separately. Coarse loops read and compare directory entries, pack/recover a group if requested, and use at most a fixed number of ordinary branches per loop index. The slack absorbs at least 128 empty-loop or control charges per listed event. Local iterator counts never loop through all values of `w` at zero payload volume: the only visits to that module occur while streaming actual independent data.

For coefficient/control work alone we can charge each event `m^48` transitions **at every underlying scalar position**, even a geometry list needed only once. Together with setup this gives **`m^88 V`** transitions for finite small-word generation, lookup, field algebra and coefficient evaluation. Per-scalar grade odometer advances fit the same bill. The caller must add the physical cost of its own passes, including large run-length/shape parameter generation, tag movement, payload restoration, and all spatial call handoffs. These are excluded from this component coefficient bound and cannot be recovered from its polynomial exponent alone.

### Weighted recursive invoice

Each genuine endpoint/rank conversion groups the internal rows at a single label or rank intermediate of the current finite volume `U`. Its child argument is `U/N`. There are at most `3N lambda` reserve-only source/destination preparations and at most `2mr(1+lambda)` fixed-layout conversions with singletons. The elementary lists cost at most `96D_g` recursive exchanges apiece, and the `<=5D_g` post-preparation lower shears use none. Thus the per-pencil child mass divided by `U` is at most

    96 D_g [3 lambda + 2(mr/N)(1+lambda)]
    <= 288 D_g (1+lambda)(1+mr/N).

The existing `2^22` coefficient remains sufficient. Finite repair descendants have volume one sixteenth of their actual finite parent. In each order-three transform this sums to `1+1/4+…`; the direct leaves have total fraction `4^(−h_r)` and each has `m` full-leaf child exchanges. The final three transforms therefore cost `(8 D_p R_pen+3m 4^(−h_r))U` in recursive spatial volume. Spatial padding is undone before all `2a` full-parent reserve calls. Their multiplicity remains `2aV`, independently of these smaller label groups. This weighted recurrence and its validity on arbitrary independent input remain exactly the ones used by AQ.

**Review scope.** The independent recount checked the rank-support invariant and inverse orientation, the short-word domain inequalities, and the lower-shear stages against B2. It found an omitted `t>=1` standalone guard and ambiguous shear-inverse wording, both corrected. The [finite checks](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/compiler-check.py) cover actual label matrices, arbitrary selected minors, higher-radix rectangle codes, full coordinate-list equality and finite-field table entries. The physical controller and full time inequalities remain written results.
