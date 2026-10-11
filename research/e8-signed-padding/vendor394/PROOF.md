# Why the fused program computes #390's operator, and what is re-opened

Notation: x (120 sources), h (783 helpers), y (120 targets). The main word is the gcert/1 word (A, scatter, B), here #390's prefix18 word with its two sink uncomputes and our nine new helper → helper gates.

**1. The bracket (#390, re-implemented and regression-checked).** The main acts on scalar values as x' = x, h' = N·x + A·h, y' = y + M·x + B·h. Here A is the product of the literal helper → helper shears. The bracket has three parts:
- **Before the main**, at the common old frame: y −= (B·A⁻¹)·h, then h ← A⁻¹·h, where A⁻¹ is the reversed, negated helper → helper subword.
- **The main** now yields (x, N·x + h, y + M·x).
- **After the final climbs**, at FULL: for every non-sink helper, h_r −= N_r·x.

`emit.prewhite` computes these lists. On #390's word it reproduces #390's `prewhite.json` exactly, in the same order. On ours, `emit.validate` replays all 1,023 live columns exactly in both orientations. The backward orientation is the same chronological sequence with each t += a·s replaced by s −= a·t. The replay confirms (x, h, y) → (x, h, y + x) forward and (x, h, y) → (x − y, h, y) backward, private work zero, and every main scalar at a common exact frame label.

**2. Our gates keep everything but the sink rows.** Each new gate is helper → helper at a frame where all three registers already sit, so no climb is added and the paid histogram is unchanged. Each is inserted after the sink's last influence on any y or retained total. The adjoint of the main from all y outputs, including the scatter, is identically zero on the sink from that point on. The x and y rows of the full rational operator and the retained totals are therefore unchanged, as `clean.py` checks against #378. `gx.check1` (E0–E7, exact scalar E5) and the gxcore mirror (sixths units) accept the word. The sinks' clean rows N_r are exactly zero.

**3. A zero-row sink needs no cleanup.** With N_r = 0, the bracket leaves h_r equal to its input value up to its frame walk. The emitted program has no event on the sink after its final climb except its rank-0 new → old adapter, which acts on the local factor. `validate` enforces this, and a control that adds a FULL repair on a fused sink is rejected.

**4. Fusing the padding.** The sink's final climb from frame f to FULL is compiled as M₁·C_[d]·M₂ (d = 2 for all three sinks, and these are existing audited edges 731→1, 744→1, 759→1). On the bank stream we apply instead (climb) ⊗ C₇₂ = (M₁⊗I)·(C_[d]⊗C₇₂)·(M₂⊗I). This is one C child of rank d + 1 on a coordinate set (d local coordinates plus window coordinate 72) between the same monomials, so the paid profile changes by rank 2 + rank 1 → rank 3.

Since no event touches the stream afterwards in this invocation, the fused invocation equals the unfused invocation followed by C₇₂ on that stream. The arbitrary-dirt property of #377 says each invocation acts on a helper stream as C_block ⊗ I_exterior, and its y output is independent of the helper value. So C₇₂ commutes with every other invocation on that bank stream, and with all data-family operations, which use disjoint families. Hence the result equals #377/#390's schedule, where the padding is a separate sweep before the X_δ(g) cover correction.

The routes of #390's ordinary banks are coordinate permutations that fix coordinate 72 (`clean.py` rebuilds them from #390's rule). The fused C on invocation coordinate 72 is therefore P_g·C₇₂·P_g⁻¹ at the bank class g = d·A⁻¹, exactly #377's padding. Each fused occurrence (3 helpers × 32 replicas per stage) lies in a distinct ordinary bank, so every such bank class receives C₇₂ exactly once. The 8 heterogeneous banks of #390 keep their rank-8 endpoints and have no padding.

**5. Price.** The profile is 288 × (validated paid local events) + 2vT idle children at 16, 8, 32, 8, 48, 8, 48, 32, 16 + 9·(3131 − 8 − 96) paddings. Its values are m = 73, live 58,899, rank mass 4,289,643, deficit 9,984, max child 48 and halving degree 2 (73² > 2·48²). The same pipeline on #390's own emitted program returns #390's b exactly. Both PR #315 engines admit b = 40055507598519/4·10¹⁶ and exclude the next grid point. The outer assembly with our #382 c gives κ = 125048239231783/1.25·10¹⁷ (complex-bound, 47 strict constraints). The same call with #390's b returns #390's κ.

## Re-opened arguments

- **#352's emitter/validator chronology** (old_response, cleanup after adF of every non-y gate) is not used. It is replaced by #390's bracket (§1), which #390 already introduced. Our extra rule is §3.
- **#377's padding as an end-of-schedule paid rank-1 cover sweep**, for 96 banks per stage. It is replaced by §4. That argument relies on the arbitrary-dirt invocation property (#377/#352, retained) and on the general compiler admitting a C child whose coordinate set mixes local coordinates with an exterior window coordinate. The latter is the same kind of child the compiler emits, up to a coordinate permutation, but #377's window-lift lemma is stated for transitions that cancel the exterior factor. For stage 8, where E₈ already contains coordinate 72, the canonical label T_U ⊗ C_{E_s} is not the right bookkeeping. The argument above is at the operator level and does not use labels.

## Re-proved by our checks

- the word's labels, nesting and exact scalar replay (`gx.check1`, gxcore);
- x/y operator rows and retained totals;
- sink zero rows;
- #390's bracket (regression) and ours in both orientations on all 1,023 columns, with lifetimes and common labels;
- the fused-sink rule;
- bank distinctness and coordinate-72 fixing;
- the profile from events, b, c and κ.

## Not re-run (inherited obligations)

- #390's rank-8 endpoint phase adapters (sinks 355/403), its Clifford audit of new edges, and its finite invoice. Our changes add 9 scalar gates per invocation and change the bracket sizes slightly (pre-helper 1,550 → 1,556, post-repair 7,800 → 7,776). No new local edge is used.
- #377/#352's retained interfaces: window lift, arbitrary-dirt banks, X_δ(g), injective routes, halving, rows, precision.
- #382's bit-side admissions.
