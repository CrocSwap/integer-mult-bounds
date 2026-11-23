# Packet conservation and historical return across native calls

## Scope and source pins

This audit binds one storage invariant to the actual callers of PR [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042), at `aliromman/integer-mult-bounds@dfd25d553a843a946ca0b94130a5ff8943e98fdd`, under `research/retimed-native-multiplier/`. The comparison base is `CrocSwap/integer-mult-bounds@e54523517d0f03e58352e647c403a5af3e525a57`. `SOURCE-BINDINGS.json` records the exact retrieved bytes. The original bootstrap validates its retained predecessor archive, each member and each text overlay before applying the source patches.

The inspected packet path has no counterexample. Named pages and owner banks intentionally persist across same-stage calls. Five stage-root work files and later-stage ancestors' work files can also persist in separately reserved roles. The usable fence is narrower: **no additional transient work-file scope opened by this stage's line, matcher, shear or raw mutation is suspended at its next same-stage paid edge**. The stronger assertion “no scratch survives a same-rank call” is false for named pages, owner banks and entrance files.

The original [STAGE-STORE.md](sources/pr8042/STAGE-STORE.md), [ACTIVATION.md](sources/pr8042/ACTIVATION.md) and `StageStore.historical` already supply the abstract historical cover. This audit adds source-caller binding, a separate opaque-record oracle, boundary observations and deliberate source failures. It does not reprove the entire all-size constant. PR #8048 at `9b4bb847d7573c8e08827fee22e9bcad8c9bb43c` concerns an older installation; its open inventory question is not transferred to this source. PR #8057 at `4c1ca64c8cad0c3a72aa49f26b084222ec400dcd` inherits the current storage argument.

## Invariant

For every successful legal execution, at every same-stage paid edge and arbitrary native depth:

1. The argument is one complete owner line in direct mode or one complete low packet in covered mode, including the unused prefix, all high representatives, every older coordinate, both coarse blocks, gap and byte suffix.
2. The current packet, unread pending siblings and completed answers partition that owner line. Ancestor pending/answer prefixes preserve their saved markers and bytes throughout the packet's ordered calls.
3. Each named child page begins at its parent's open end. Live parent intervals remain allocated. Parent pages may be read while suspended; only the top page may be written or resized. Normal return erases the child's retained extent before popping its frame. Zero-valued live owners remain allocated owners.
4. The rank-local transient fence stated above holds. Named pages, stage-root files and different-stage ancestors remain charged. A transient may enclose an earlier-stage call, which uses a distinct reserved head set.
5. Descendants return before their caller writes the identified output interval. Saved packet markers and other ancestor bytes are restored; retired suffixes are zero. Historical extent is the maximum over prior active paths, including earlier siblings, rather than a sum of successive sibling allocations.

The numerical consequence still requires the separate bound on simultaneous local owner slots and adapter homes.

## Exact caller equations

Let a weighted argument have `atoms=c=Nf+r`, atom cardinality `alpha`, available fresh cardinality `A`, older cardinality `O`, gap `G` and byte suffix `S`. Its volume is

\[
 W=A O\alpha^{2c}GS.
\]

Write `B=core.owners`, `Q=core.low`, `H=core.high`. Before compilation, `SameOrderBody.weighted` requires `A=U B Q H` and places the two residual factors in `gap=G alpha^r` and `suffix=S alpha^r`. Therefore `OwnerBanks.volume` in `binary_receiver.Receiver.compiled` is exactly

\[
 V=UQHO\alpha^{2Nf}(G\alpha^r)(S\alpha^r)=W/B.
\]

This is **one owner's** volume. It is not a bound on the complete backing bank. A paid job names an existing owner; zero content and a suspended generator do not remove that charge.

Absorb residuals into `G,S`. A covered line has

\[
 V=UQHO\alpha^{2Nf}GS,\qquad \ell=UHO\alpha^{2Nf}GS=V/Q.
\]

`Receiver.serve_line` passes `rows=U`, `types=Q`, `suffix_bytes=H O alpha^(2Nf) G S` to `type_route`. Entrance and inverse exit each traverse all `V` bytes. The pending push has length `V`; each low iteration pops and later appends exactly `ell` bytes.

Let `p0,a0` be saved ancestor markers. After completing `k` packets and popping the next, `0 <= k < Q`,

\[
 p=p_0+(Q-k-1)\ell,\quad a=a_0+k\ell,\quad
 (p-p_0)+(a-a_0)+\ell=V. \tag{1}
\]

The packet schedule performs no pending/answer operation, so (1) holds unchanged at all its 1, 3 or 5 same-stage calls. Its reply moves the active `ell` into the answer suffix. At loop end `p=p0`; `take_answers(a0, completed)` clears precisely the new answers and restores `a=a0`. This proves (1) by induction on `k`. The `p0+a0` ancestor bytes are additional live storage, not absorbed into `V`.

For coarse positions `i,j`, `five_exchange.same_order_line.child` uses `start=i f`, `end=(N+j)f` and passes

\[
\begin{aligned}
 \text{atoms}'&=f,&\text{available}'&=U,\\
 \text{older}'&=HO\alpha^{start},&
 \text{gap}'&=G\alpha^{end-start-f},\\
 \text{suffix}'&=S\alpha^{2Nf-end-f}.
\end{aligned}
\]

Multiplying by the two exposed `alpha^f` blocks gives exactly `ell`: the exponent is `start+2f+(end-start-f)+(2Nf-end-f)=2Nf`. `divmod(row // alpha^start, O)` recovers the genuine high and old ordinals. Coefficients depend on those ordinals while all their payload records remain present. Preparatory and inverse exchanges use this same full shape. More serial exchanges do not create simultaneously owned packet copies beyond their charged homes.

In direct mode `Q=H=1`. For selected axis `i`, the child has `older'=O alpha^(if)`, `gap'=G alpha^((N-1)f)`, `suffix'=S alpha^((N-i-1)f)`, hence full volume `V`. For nonempty frame word `F`, the actual schedule is `direct_route(F)`, one weighted child, `direct_route(F^-1)`. Both basis routes act on the whole line. The coordinate wrapper's two named pages survive; each route's matcher pages return before the next operation.

## Source lifetime fence

`growing_binary.pipe` copies its complete source to a named page, invokes one gate to completion, erases the old page, exchanges page roles, then advances the schedule. The generators construct call descriptors without opening work-file contexts around yields. A covered `lower_tape` closes its three spools before the next weighted child. A direct route's lower, scaler and weighted-pair scopes complete before it returns to the coordinate wrapper.

`weighted_pair` can retain two spools across `core.previous`. The installed `ordinary_carrier.stage_body` binds that callback to `ternary(... maximum=stage-1)`. It cannot reenter this stage's scratch set. The five `root_body` files and two public rectangle files are persistent entrance roles; later-stage ancestors may retain their own work files. The fence is relative to this baseline, not a process-wide zero-open-files claim.

`Banks.clone`, `swap`, `xor` and `OwnerBanks.route` return after their work-file contexts close. `BinarySource.inner`, `StrongBinarySource.raw` and `BinaryWord.native` yield jobs after these mutations complete. At a `QUERY` yield the cloned **owner slot** remains live, but its copy spool has closed. XOR and retirement follow the paid return. Counting open generators is not a payload bound; counting only external owners is also insufficient.

## Arbitrary depth and historical addresses

`Page.__init__` uses `parent.base+parent.size`. Writes and truncations reject a non-top page. In this source path, shrinking uses `erase`, which zeros the former length before logical truncation. Release likewise zeros the current full length before popping. An earlier longer use therefore cannot leave an uncharged dirty suffix. `PacketStack.pop_forward` clears only its top interval; `take_answers(marker)` clears only the suffix at that marker. Equation (1) validates the actual saved-marker caller, not arbitrary arguments to those methods.

Induct on `(stage,c)` lexicographically. A same-stage recursive weighted child has `f=floor(c/N)<c` for `N>=2`; a predecessor call decreases the stage index; cold primitives terminate. A child copies its argument to its own page before descending. Its deeper frames return before final output. The intervening named caller roles leave the identified output page topmost when written. Child pages then clear and pop, and packet markers retain their saved values. The caller can erase the previous ping-pong page, append the reply or reinstall the returned owner. Covered-to-direct dispatch shares `self.arena` with `self.small`, so it creates no untracked second ordinary arena.

For one page role, let `L_j(t)` be its local open extent at depth `j`. Adjacency and reuse give

\[
 H_{role}\le\max_t\sum_{j\text{ active at }t}L_j(t). \tag{2}
\]

The maximum includes longer retired siblings. Different heads can peak at different times; complete historical space sums individual maxima. Delimiters and a one-past-end convention add the fixed per-head allowance. Erasure costs movements and does not erase the historical maximum.

### Positive owners and changing windows

The Gaussian analogue uses **historical slot count**, not current live count. `spool.Arena.field` uses free slots first. Allocation/retirement induction gives `high=max_so_far(live)` within an arena, including temporary zero and replacement fields. A child starts at `start+high*extent`, and parent allocations are suspended. A later child may use a different `ambient_bits` and slot width, but its base is the then-current parent historical end, not the previous child's far end. Field retirement clears before freeing. Normal child return truncates to its saved start. Thus (2) becomes a maximum of sums of local `high*extent` on active arena paths.

In `retimed_supplier.Positive._run`, the incoming snapshot closes before `recipe.open().run`; a paid leaf receives an existing field of volume `W/B`; outgoing scratch opens after that run returns. Public rows, simultaneous private fields, borrowed slots and temporary zeroes stay charged. Both half-column subjobs name the existing owner and run serially. Selecting another axis window does not create an uncharged row. This proves allocation/return shape, conditional on the independent bound for how many owners can be live.

The stronger “start at `live*extent`” rule is false. Allocate two two-byte parent slots and retire the **first**, leaving the second live. Then `live=1, high=2`. Starting a child at byte 2 overwrites the retained slot; the source correctly starts at byte 4. A free-list hole does not make the live slots a prefix.

### Conditional geometric charging

Suppose each local home on one role is bounded by `K` times the native argument, and production compiled owner counts satisfy `B >= B_* > 1`. The caller equations give `W_child <= W_parent/B_*` within a stage, with another factor `Q` for a covered packet. Its entire active chain contributes at most

\[
 K W_0\sum_{j\ge0}B_*^{-j}=K W_0\frac{B_*}{B_*-1}
\]

to that role's historical cover, independently of sibling count, itinerary or window position. Positive row descent has the same implication. Earlier-stage padding and entrance rectangles retain separate bounds and roles. Small-rank fixtures have `B=1`: they corroborate return correctness, not production geometric contraction. This corollary cannot replace proving `K` or the live-owner census.

## Executable evidence and failures

`audit_packets.py` wraps observation boundaries around actual physical operations. The independent oracle computes the nonidentity rational 2-by-2 frame and complete address permutation on unique four-byte records. Canonical low/high enumeration is reused from the source; its completeness is not independently proved here.

| Fixture | Records | Same-stage calls | Earlier-stage calls | Ordered packet calls |
|---|---:|---:|---:|---|
| Direct nonidentity, modulus 9 | 52,488 | 1 | 10 | One child and both basis routes |
| Covered dirty spectators, modulus 3 | 10,368 | 40 | 80 | 8 with 1, 4 with 3, 4 with 5 |
| Covered all true highs, modulus 9 | 2,834,352 | 40 | 80 | Same 16 lows, all 27 highs per low |

Every observed boundary has no newly opened local transient scope, full packet volume, equation (1), restored ancestor bytes and saved markers. Entrance/exit traverse exactly `V`; external guards, final cursors and every output record agree with the separate oracle. All retired child high-water tails are zero. Each fixture has only one genuine weighted-child depth: `N=2`, the called child has `atoms=f=1`, and that child stops. The 40 calls are ordered siblings, not deeper recursion. The arbitrary-depth result above follows from the source caller equations and suffix-return induction, not extrapolation from this one-depth replay. `exact-trace.json` records retained named page stacks and observed weighted depth explicitly. Instrumented movement counters are diagnostics, not a timing receipt: observations can add source-meter movements.

Five controls mutate actual function bodies in memory while leaving source bytes intact. Omitting the inverse basis route fails the full-record oracle; replacing true highs by one fails (1); using answer marker zero fails marker return; omitting page erasure fails the historical dirty-tail check; retaining a real dirty transient around the packet fails the same-stage fence. The separate positive allocator control rejects the live-count base rule.

These finite checks do not execute astronomical production ranks or prove the complete coefficient/index storage bound. The remaining independent target is the simultaneous owner/local-adapter census at production yields, including Gaussian replacements and source controls, then its substitution into the existing historical theorem. This is a proof obligation, not evidence that the all-size statement is false. No physical premise, analytic estimate, threshold or cost constant is changed.

Credit: Ali Romman's source and storage binding, Clear1nsight's inventory question, and the retained predecessor authors. Prepared for @CubeJerry with OpenAI assistance. This new written argument is not advertised as kernel-checked or human-approved.
