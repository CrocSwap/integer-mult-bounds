# A ceiling on κ for every word on #144's paired-cube design

**Claim.** Keep the design of #144 and change anything else about the local word, including `p`. Then the complex
supplier's saving `a` and the certified κ satisfy

    a < 2.5657 × 10⁻³    and    κ < a/(1+a) < 2.5592 × 10⁻³.

The design is fixed by five things:

- the paired-cube ports;
- the identity `K + H + B = I`;
- the coordinate-star decoder for `B`;
- the `K` step on the source registers;
- the three-stage shared cores.

The parts that may change are the circuit, the root groups, the gauges, the reuse pairs, the terminal sinks, every
frame and `p`.

**What it covers.** The claim is about words that obey rules R1–R8 of §3.4. These describe #144's word format, as
checked by `scripts/paired_cube/verify.py`, by the frame-and-reuse layer of #155–#168 (`paired_cube_physical.py`) and
by the terminal-sink gate of #168. It does **not** cover the source-assisted words of #184, #191, #193 and #194. Those
use the original source registers as controls and exact cancellation, which breaks R1 and R2. §11 says more.

For comparison, the selected construction on main certifies κ = 6.618855 × 10⁻⁴, with complex saving
6.623239 × 10⁻⁴. Its complex word is #181's with #186's frame cuts, reuse pairs and sinks, which are changes of the
kind these rules allow. The ceiling is about 3.87 times that κ.

This note makes no κ claim. It explains:

- how κ is certified (§1);
- two facts about the cost function (§2);
- what is fixed and what is free (§3);
- each lemma, with its proof (§4–§8);
- the charging argument that turns the lemmas into a cost floor (§9);
- how the number is computed, and which steps use a computer (§10);
- scope and limits (§11).

---

## 1. How a construction certifies κ

### 1.1 The ledger

The repository proves `T(n) = O(n·(log n)^{1−κ})` for integer multiplication; larger κ is better. A construction
feeds the assembly a *supplier*. For this note, a supplier is a ledger with three parts:

- a number `m` (here `m = 3h`, defined in §3);
- a role count `W`;
- a multiset of **children**: `n_r` children of width `r`, for integers `0 < r < m`.

The construction's bookkeeping guarantees the rank-mass identity

    Σ_r r·n_r = W·m − D,                                                     (1)

where `D` is the **deficit**, fixed by the design (§3.5).

### 1.2 Lemma 1: `a < D/C`

The repository certifies a saving `a` when an exact rational upper bound shows

    Σ_r n_r · r · (m/r)^a  <  W·m.                                          (2)

Put `f(r) = r·ln(m/r)` and define the **cost** `C = Σ_r n_r·f(r)`.

**Lemma 1.** If (2) holds, then `a < D/C`.

*Proof.* `e^x ≥ 1 + x`, so `(m/r)^a ≥ 1 + a·ln(m/r)` for every child. Multiply by `r·n_r` and sum. Then (2)
gives `W·m > Σ r·n_r + a·C`, and by (1) this equals `W·m − D + a·C`. ∎

So the task is to show that **every** word on the design pays at least some cost `C_lo`. Then `a < D/C_lo`.

### 1.3 From `a` to κ

Both assemblies on main (`scripts/structured_bulk_assembly.py` and the balanced one in
`research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py`) take a transfer saving `a′` and
require three things:

- `a′` is below the complex saving `a`;
- `q = a′(1 − 2η)` with a backoff `η > 0`;
- κ is below the margin `ε_A·q`, where `ε_A ≤ (1 − η)/(1 + q)`.

Hence `κ < q/(1 + q) < a/(1 + a)`.

---

## 2. Two facts about `f`

`f''(r) = −1/r < 0`, so `f` is strictly concave. Since `f(0⁺) = 0`, it is also strictly subadditive:
`f(x) + f(y) > f(x+y)`.

**Lemma 2 (chains).** Suppose a register climbs a total of `t` dimensions in steps `r₁, …, r_k`, each a positive
integer. Its cost `Σ f(rᵢ)` is at least

- `f(t)`;
- `f(1) + f(t−1)` if `k ≥ 2`;
- `2f(1) + f(t−2)` if `k ≥ 3`.

*Proof.* Merging two steps lowers the cost (subadditivity). So it is enough to treat exactly 1, 2 or 3 steps. The
cost is a concave function of the steps on the simplex `{rᵢ ≥ 1, Σ rᵢ = t}`. A concave function is smallest at a
vertex, and the vertices are the permutations of `(1, t−1)` and of `(1, 1, t−2)`. ∎

Three derived quantities appear below:

| symbol | definition | meaning |
|---|---|---|
| `δ` | `f(1) + f(h−2) − f(h−1)` | extra cost of one intermediate stop in a climb of `h − 1` |
| `ε` | `f(1) + f(h−3) − f(h−2)` | extra cost of one more intermediate stop |
| `g₃` | `min(3f(1), f(3)) = f(3)` | cheapest way to be at a line in all three stages (§3.3) |

By Lemma 2, a climb of `h − 1` with one intermediate stop costs at least `f(h−1) + δ`, and with two it costs at least
`f(h−1) + δ + ε`.

---

## 3. The fixed design

### 3.1 Addresses, ports and cubes

Work in `F₂^h` with `h = 2p`. Group the coordinates into `p` pairs `{2i, 2i+1}`, and call the two coordinates of a
pair *partners*. A **port** `S` picks one coordinate from each of three different pairs, so there are
`v = 8·C(p,3)` ports. Its address `q_S ∈ F₂^h` is the indicator vector of `S`. Two facts follow:

- `q_S·q_T ≡ |S∩T| (mod 2)`;
- `q_S·q_S = 1`.

The **cube** of a port is the set of 8 ports on the same three pairs. Every port is both a **source** (input `x_S`,
held in the source register `X_S`) and a **target** (output register `y_T`).

### 3.2 The identity, and what the auxiliary word must deliver

The local word must add `x` into `y`. #144 splits the identity as `I = K + H + B`, where
`B_{T,S} = (|T∩S| − 1)/2`:

- `B` is delivered by the `h` **coordinate stars** (copied centres). Star `i` is the sum of `x_S` over the ports
  containing coordinate `i`.
- `K` acts inside each cube. It is implemented on the source registers themselves (§3.4, R7).
- `H = −B` on pairs of ports in **different** cubes, and 0 inside a cube. It is the only part delivered by the
  **auxiliary word**.

For `T` and `S` in different cubes, `H_{T,S} = −(|T∩S| − 1)/2`. That is `½` if `|T∩S| = 0`, `0` if it is 1, and
`−½` if it is 2. Define

    row(T) = { S in another cube : |S∩T| ∈ {0, 2} },     col(S) = { T : S ∈ row(T) }.

The relation is symmetric, so `row(T) = col(T)` as sets of ports. The auxiliary word must carry each `x_S` to every
`y_T` with `T ∈ col(S)`. Since `|S∩T|` is even exactly when `q_S·q_T = 0`, every `S ∈ row(T)` has `q_S ∈ q_T^⊥`.

`scripts/paired_cube/verify.py` checks this identity entry by entry (`Signed H mismatch`).

### 3.3 Frames: what a register pays

A **register** below always means a physical register. Every register has, at every moment of a stage, a **frame**:
a subspace of `F₂^h`. Within a stage, a register's frames form an ascending chain, each containing the previous
one. Each strict step from dimension `d` to `d′` is one child of width `d′ − d`. A register is *at* `F` when `F` is
its current frame, and its **stops** are the frames of its chain.

An auxiliary register's chain ends at the full space `F₂^h`. It starts in one of two ways:

- at `0`, and then every step is paid in each of the three stages;
- at a **gauge** `σ`: the chain starts at `σ`, and one merged child of width `3·dim σ` is paid once for all three
  stages.

So an auxiliary register that is ever at a line (a frame of dimension 1) has paid at least `g₃` to be there: three
steps of width 1 (`3f(1)`), or one merged gauge child (`f(3)`).

### 3.4 The word: what may vary

Within the design, the local word is the reversible "transparent" sequence

    z ← z + Vx      (inject each source x_S into its own source role)
    z ← Mz          (operations among auxiliary registers)
    y ← y + Jz      (reads: deliver root values into targets)

followed by the inverse cleanup at the full frame. The rules for any word:

- **R1. Operations.** An operation `a ← a ± b` between auxiliary registers runs with both registers at one common
  frame `F`. `F` contains `q_S` for every source `S` in the **conservative support** of the value moved. The
  conservative support is every source with a path to that value in the circuit; signed cancellation does not
  remove a source.
- **R2. Injection.** `x_S` enters the auxiliary word once: by the injection into its source role, at a frame
  containing `q_S`.
- **R3. Root groups.** A root group `G` is a set of targets. Its value is read from an auxiliary register into every
  `y_T` with `T ∈ G`, with that register at the read's frame. The frame contains the value's conservative support and
  lies inside the group's **cap**

      cap(G) = ( span{ q_T : T ∈ G } )^⊥.

  In the certified words the read frame is the cap itself.
- **R4. Old values.** A role's register holds arbitrary old content when the role begins. That content is cancelled by
  a read from the register at the frame it has at that moment: `0` for an ungauged role, the gauge otherwise. The
  read goes into every target that the role's content reaches.
- **R5. Reuse pairs.** A recipient role may take over a donor's register after the donor's last operation. The
  register's chain is the donor's chain followed by the recipient's.
- **R6. Terminal sinks** (#166, #168). A sink role with group `G` and pivot `p ∈ G` is deleted. Each write into it
  becomes a write into `y_p` at the original frame `F_i ⊆ cap(G)`, with the control register and `y_p` at `F_i`.
  For every other target `t ∈ G`, `y_t −= y_p` runs at frame 0 before the first write and `y_t += y_p` runs at
  `cap(G)` after the last. Groups of different sinks are disjoint.
- **R7. Data registers.**
  - `y_T` climbs from `0` to its top, `q_T^⊥`. Every read or write into `y_T` happens with `y_T` at that event's
    frame.
  - `X_S` is used by the auxiliary word only for the injection. Its itinerary is fixed by the `K` step: it starts at
    `span(q_S)`, moves to a 3-dimensional frame, then to a hyperplane, then to the full space. Its steps are
    `2, h−4, 1` in every word (`K_source_itinerary_verified` in `verify.py`).
- **R8. Stages.** All three stages run the same local word.

A **delivery** into `y_T` is an event that adds auxiliary-word content to `y_T`: a root read (R3), an old-value read
(R4), a sink write into a pivot, or the final `y_t += y_p` of a sink (R6). By R7 its frame is a stop of `y_T`, so it
lies in `q_T^⊥`. By R1 and R3 it contains `q_S` for every source it carries.

Free: `M`, the groups, the gauges, the pairs, the sinks, every frame and `p`. Fixed: the ports, the identity, the
stars and the `K` step.

### 3.5 The fixed part of the ledger and the deficit

Every word pays the following, per port and over three stages:

| part | children | cost |
|---|---|---|
| source registers (R7) | three each of widths `1`, `2`, `h−4` | exactly `3(f(1) + f(2) + f(h−4))` |
| target registers | a climb of `h − 1` per stage | at least `3f(h−1)` |
| endpoints | two of width `2` | exactly `2f(2)` |
| star copies | `3h` of width `h − 2` per vertex | exactly `3h·f(h−2)/v` |

The stars cost `ℓ = h(h−2)` in rank, and the deficit is

    D = 2v − 3ℓ = (8/3)·p(p−1)(p − 6.5).

`D ≤ 0` for `p ≤ 6`, so no positive saving is possible there. From here on `p ≥ 7`.

---

## 4. Paths only climb

A **path** of `x_S` follows the value from its injection to a delivery. Each hop is one of:

- an operation, where both registers are at the same frame;
- a read or a sink write, where the auxiliary register and the target register are at the same frame;
- the final `y_t += y_p` of a sink, where both target registers are at `cap(G)`.

Between hops the value stays in one register, whose frames ascend. A recipient continues its donor's register, so a
reuse pair is not a hop. Hence **the frames along a path never decrease.**

Two consequences are used below.

- **Supports lie in frames.** A register's conservative support always lies in its current frame. Content arrives by
  an injection or an operation at a frame containing it (R1, R2), and the frame only grows afterwards.
- **Deliveries are orthogonal.** If a path of `x_S` ends with a delivery into `y_T` at frame `F`, then every earlier
  frame `E` on the path satisfies `E ⊆ F ⊆ q_T^⊥`, so `q_T ⊥ E`.

For every `T ∈ col(S)` there is a path of `x_S` to `y_T`, because `H_{T,S} ≠ 0`.

---

## 5. Three counting facts

**Count.** `|col(S)| = 12(p−3) + 12·C(p−3, 2) + 8·C(p−3, 3)`.

*Proof.* Write `S = {s₀, s₁, s₂}`, let `s̄ᵢ` be the partner of `sᵢ`, and call the other `p − 3` pairs *free*. Sort
`T ∈ col(S)` by how many of `S`'s pairs it uses:

- none: any port on free pairs, `8·C(p−3,3)` of them;
- one: its coordinate there must be `s̄ᵢ`, giving `3 · 4·C(p−3,2)`;
- two: its coordinates there must be `{sᵢ, sⱼ}` or `{s̄ᵢ, s̄ⱼ}`, giving `3 · 2 · 2(p−3)`;
- three: the same cube, excluded. ∎

**Lemma S.** For `p ≥ 7`, the vectors `{q_T : T ∈ col(S)}` span exactly `q_S^⊥`, of dimension `h − 1`.

*Proof.* Every such `q_T` lies in `q_S^⊥`. For the converse, there are `p − 3 ≥ 4` free pairs.

1. Ports on free pairs are in `col(S)`. Two of them that differ in one coordinate sum to `e_u + e_{u′}`, where `u` and
   `u′` are partners or lie in different free pairs (this needs a fourth free pair). Such vectors give every
   even-weight vector on the free coordinates, and a single port adds an odd one. So every `e_x` with `x` free is in
   the span.
2. `{s̄ᵢ, y, z}` with `y`, `z` free is in `col(S)`. By step 1, every `e_{s̄ᵢ}` is in the span.
3. `{sᵢ, sⱼ, z}` with `z` free is in `col(S)`. So `e_{sᵢ} + e_{sⱼ}` is in the span.

These vectors span a space of dimension `2(p−3) + 3 + 2 = h − 1`. ∎

**Lemma M.** Let `p ≥ 7` and `w ∉ {0, q_S}`. Then at least `μ = 4(p−3)` targets `T ∈ col(S)` have `w·q_T = 1`.

*Proof.* Let `N(w)` count those targets. There are three cases.

- **(a) `w` differs on the two coordinates of some free pair `k`.** Swapping the coordinate that `T` uses in pair `k`
  is an involution on the targets of `col(S)` that use `k`, and it flips `w·q_T`. There are `4(p−2)(p−4) + 12` such
  targets, so `N ≥ 2(p−2)(p−4) + 6`.
- **(b) `w` is constant on every free pair, equal to 1 on a free pair `k` and 0 on a free pair `k′`.** Moving `T`'s
  coordinate from `k` to the same position in `k′` maps the targets that use `k` but not `k′` one-to-one onto those
  that use `k′` but not `k`, and flips the parity. So `N ≥ 4(p² − 8p + 18)`.
- **(c) `w` equals one value `c` on every free coordinate.** By the count above,

      N = 8·C(p−3,3)·c + 4·C(p−3,2)·#{i : w_{s̄ᵢ} = 1} + 2(p−3)·#{pairs P : w(P) + c odd},

  where `P` runs over the six pairs `{sᵢ, sⱼ}` and `{s̄ᵢ, s̄ⱼ}`.
  - If `c = 1`, then `N ≥ 8·C(p−3,3)`.
  - If `c = 0` and some `w_{s̄ᵢ} = 1`, then `N ≥ 2(p−3)(p−4)`.
  - Otherwise `w` lives on `{s₀, s₁, s₂}` with weight 1 or 2. Exactly two pairs `{sᵢ, sⱼ}` then have odd weight, so
    `N = 4(p−3)`.

Every bound is at least `4(p−3)` for `p ≥ 7`. ∎

*Consequence.* Let `Φ ∋ q_S` be a subspace of dimension at least 2, and pick `w ∈ Φ` outside `span(q_S)`. Then at
least `μ` targets of `col(S)` are not orthogonal to `Φ`. Also `|col(S)| ≥ 2μ`.

---

## 6. Every source enters at its own line

**Lemma E.** Let `p ≥ 7`.

1. The register of the source role of `S` is at exactly `span(q_S)` when `x_S` is injected.
2. For all but at most `n_g = ⌊v/|col|⌋` sources, that register is at frame 0 when the source role begins. It then
   steps to the line, which costs `3f(1)` over the three stages.

*Proof.*

1. Let `F` be the frame of the injection, so `q_S ∈ F`. Every path of `x_S` starts there. By §4, `q_T ⊥ F` for every
   `T ∈ col(S)`. Lemma S gives `F ⊆ (q_S^⊥)^⊥ = span(q_S)`.
2. Before the injection the register's frames lie in the line, so each is `0` or the line. Suppose the register is
   already at the line when the source role begins. By R4 the role's old content is read at the line into every
   target it reaches. The role's content reaches every `T ∈ col(S)`, since `x_S` does. So every such `y_T` has
   `span(q_S)` as a stop. A chain has at most one stop of dimension 1, so the sets `col(S)` of these sources are
   pairwise disjoint. There are at most `v/|col|` of them. ∎

In the certified words no source role is gauged (`selected_sources_untouched` in `verify.py`), so the exceptional set
is empty there.

---

## 7. Every target has registers at its own hyperplane

Call an auxiliary register a **T-register** if it is at `q_T^⊥` at some moment. Its next frame is the full space, so
a register is a T-register for at most one target.

**Lemma T.** Let `p ≥ 7` and let `T` be a target.

1. `T` has a T-register.
2. If `y_T` has no stop strictly between `0` and `q_T^⊥`, then `T` has two different T-registers.

*Proof.*

1. For every `S ∈ row(T)`, some delivery into `y_T` carries `x_S`. Its frame contains `q_S` and is a stop of `y_T`.
   Stops are nested, so the largest of these frames, `F*`, contains `q_S` for every `S ∈ row(T)`. Those vectors span
   `q_T^⊥` (Lemma S, with `row(T) = col(T)`), and `F* ⊆ q_T^⊥`. So `F* = q_T^⊥`.

   The delivery at `F*` is not the final `y_t += y_p` of a sink. That step runs at `cap(G)` for a group with at least
   two targets, of dimension at most `h − 2`. So it is a root read, an old-value read or a sink write, and in each of
   those an auxiliary register is at `F*`.
2. Every delivery that carries a source is at a nonzero stop of `y_T`, hence at `q_T^⊥`, and as in part 1 it comes
   from an auxiliary register at `q_T^⊥`. If two registers deliver, we are done. Otherwise one register `R` makes
   every delivery, so at its last delivery its conservative support contains `row(T)`.

   Look at the last arrival of content into `R` before that delivery, at frame `F`. All earlier arrivals were at
   frames inside `F`, so `R`'s support lies in `F` (§4). Hence `q_T^⊥ = span(row(T)) ⊆ F ⊆ q_T^⊥`. An injection
   happens at a line (Lemma E), so this arrival is an operation `R ← R ± b`. The register `b` is auxiliary, differs
   from `R`, and is at `q_T^⊥`. ∎

---

## 8. Every source fans out through its units

### 8.1 Units

Fix a source `S`. A **unit** of `S` is an auxiliary register that is at `span(q_S)` at some moment. The source role's
register is a unit (Lemma E). A chain has one stop of dimension 1 at most, so units of different sources are
different registers. A unit's **exit** `Φ` is its next frame after the line. Units come in three kinds:

| kind | exit dimension | targets `T ∈ col(S)` with `q_T ⊥ Φ` |
|---|---|---|
| **big** | `2 … h−2` | misses at least `μ` of them (Lemma M) |
| **small** | `h − 1` | at most one (`Φ^⊥` is a line) |
| **idle** | `h` | none |

### 8.2 Targets served at the line

Let `L(S)` be the set of targets `T ∈ col(S)` of one of two kinds:

- **line targets:** some delivery into `y_T` happens at the frame `span(q_S)`;
- **pivot targets:** `T` is a non-pivot target of a sink group `G` whose pivot register has the stop `span(q_S)`, and
  `span(q_S) ⊆ cap(G)`.

Two facts:

- **Each `T ∈ L(S)` has an intermediate stop.** A line target has the stop `span(q_S)`. A pivot target has the stop
  `cap(G)`, where the sink's final `y_t += y_p` runs. That frame contains `q_S` and has dimension at most `h − 2`.
- **A target is in `L(S)` for at most two sources, and then it has two intermediate stops.** It is a line target for
  at most one source, because `y_T` has one stop of dimension 1 at most. It is a pivot target for at most one
  source, because it is in at most one sink group and the pivot has one stop of dimension 1 at most. If it is a line
  target for `S′` and a pivot target for `S ≠ S′`, the stops `span(q_{S′})` and `cap(G) ∋ q_S` are different.

### 8.3 Lemma D

**Lemma D.** Let `p ≥ 7`, and let `S` have `b` big units and `s` small units. Then one of the following holds:

- `b ≥ 2`;
- `b = 1` and `|L(S)| + s ≥ μ`;
- `b = 0` and `|L(S)| + s ≥ |col(S)|`.

*Proof.* Take `T ∈ col(S)` outside `L(S)`, and a path of `x_S` to `y_T`. It starts at `span(q_S)` (Lemma E). Let `r`
be the last register on the path that holds the value at the frame `span(q_S)`.

- `r` is not `y_T`, since `T` is not a line target.
- `r` is not a pivot `y_p`. From `y_p` the value can only continue by the sink's final `y_t += y_p` at `cap(G)`. Frames
  ascend, so `span(q_S) ⊆ cap(G)`, and `T` would be a pivot target.
- `r` is no other target register, because only a pivot passes a value on.

So `r` is an auxiliary register, that is, a unit `u`. A hop at the line would land in another register at the line,
so the value stays in `u` until `u` moves to its exit `Φ_u`. Every later frame on the path contains `Φ_u`, so
`q_T ⊥ Φ_u` (§4).

Hence every target of `col(S)` outside `L(S)` is orthogonal to the exit of some big or small unit. One big unit
misses at least `μ` targets, and each small unit covers at most one. ∎

---

## 9. The cost floor

### 9.1 What registers cost (three stages)

Put

    U₂ = g₃ + 3f(1) + 3f(h−2),     I₀ = g₃ + 3f(h−1).

By §3.3 and Lemma 2:

| register | stops after its entrance | cost at least |
|---|---|---|
| idle unit | line, full | `I₀` |
| small unit | line, hyperplane, full | `U₂` |
| big unit | line, exit, full | `U₂` |
| big unit that is a T-register | line, exit, `q_T^⊥`, full | `U₂ + 3ε` |
| T-register that is not a unit | `q_T^⊥`, full | `3f(1)` |

A small unit whose exit is `q_T^⊥` is a T-register at no extra cost. An idle unit is never a T-register.

For the source role's register, `g₃` can be replaced by `3f(1)` unless `S` is one of the `n_g` exceptions of
Lemma E. That adds `3f(1) − f(3)` to each of its floors.

A target register costs at least `3f(h−1)`. It costs `3δ` more with one intermediate stop, and `3δ + 3ε` more with
two (Lemma 2).

### 9.2 Charging

Put `ρ = U₂/μ`. Make two kinds of transfer:

- every T-register pays `3ε` to its target;
- every target `T ∈ L(S)` pays `ρ` to `S`.

Transfers cancel in the total. So the cost of all target registers and auxiliary registers equals the sum of three
kinds of balance: one per target, one per source, and one per auxiliary register that is no unit.

**Targets.** The balance of `T` is its extra cost above `3f(h−1)`, plus what it receives, minus what it pays. It is at
least

    τ = min( 6ε,  3δ + 3ε − ρ ).

- No intermediate stop: `T` is in no `L(S)` (§8.2) and has two T-registers (Lemma T). Balance `≥ 6ε`.
- An intermediate stop, and `T` in at most one `L(S)`: extra cost `≥ 3δ`, one T-register, at most one payment.
  Balance `≥ 3δ + 3ε − ρ`.
- `T` in two sets `L(S)`: two intermediate stops (§8.2), so extra cost `≥ 3δ + 3ε`. Balance
  `≥ 3δ + 6ε − 2ρ ≥ 3δ + 3ε − ρ`, because `ρ ≤ 3ε`.

**Registers that are no unit.** A T-register costs `≥ 3f(1)` and pays `3ε ≤ 3f(1)`. Balance `≥ 0`.

**Sources.** The balance of `S` is the cost of its units, minus their payments, plus `ρ·|L(S)|`. After payments a big
unit keeps at least `U₂`, a small unit at least `U₂ − 3ε ≥ ρ`, and an idle unit at least 0. By Lemma D:

- `b ≥ 2`: balance `≥ 2U₂`;
- `b = 1`: balance `≥ U₂ + ρ·(s + |L(S)|) ≥ U₂ + ρμ = 2U₂`;
- `b = 0`: balance `≥ ρ·(s + |L(S)|) ≥ ρ·|col| ≥ 2ρμ = 2U₂`.

In each case the source role's register is one of the units, and its floor is higher by `3f(1) − f(3)` unless `S` is
an exception. So the balance is at least `2U₂ + 3f(1) − f(3)` for all but `n_g` sources.

The argument uses four side conditions: `ε ≤ f(1)`, `ρ ≤ 3ε`, `U₂ − 3ε ≥ ρ` and `|col| ≥ 2μ`. The last is §5. The
script asserts the others exactly at every `p` it evaluates.

### 9.3 Theorem

**Theorem.** For every `p` with `7 ≤ p ≤ 99`, every word on the design satisfies `C ≥ C(p)`, where

    C(p) = v·[ 3(f(1) + f(2) + f(h−4)) + 3f(h−1) + 2f(2) + 2U₂ + τ ]
           + (v − n_g)·(3f(1) − f(3)) + 3h·f(h−2).

*Proof.* Add the fixed part of §3.5 to the balances of §9.2. ∎

In words: besides the data registers, every source needs two registers that leave its line and stop again before the
full space, and every target needs two registers at its hyperplane or a stop of its own.

---

## 10. The numbers

`ceiling.py` computes `D/C(p)` for `7 ≤ p ≤ 99` in exact rational arithmetic.

- `ln x` reduces to `x ∈ [1, 2)` by halving, then uses `ln x = 2·atanh((x−1)/(x+1))` and `ln 2 = 2·atanh(1/3)`.
- Partial sums of `atanh` are lower bounds, since every term is positive. Adding the geometric tail
  `z^{2K+1} / ((2K+1)(1 − z²))` gives upper bounds.
- A lower bound is used wherever `f` enters `C(p)` positively and an upper bound wherever it is subtracted.

So every printed bound is a true upper bound on `a`.

| p | 7 | 9 | 11 | 12 | **13** | 14 | 16 | 20 | 30 | 60 | 99 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `a <` | 7.11e-4 | 2.0837e-3 | 2.4856e-3 | 2.5487e-3 | **2.5657e-3** | 2.5540e-3 | 2.4832e-3 | 2.2753e-3 | 1.7935e-3 | 1.0549e-3 | 6.829e-4 |

**Tail, `p ≥ 100`.** By Lemma E every source role's register climbs from its line to the full space, which costs at
least `3f(h−1)`. The source and target registers cost at least `3f(h−1)` each (Lemma 2). For `r < h` we have
`m/r > 3`, so `f(r) > r·ln 3`. Hence `C > 9v(h−1)·ln 3`, and with `D < 2v`,

    a < 2 / ((18p − 9)·ln 3) ≤ 1.0165 × 10⁻³    for p ≥ 100.

The maximum is at `p = 13`:

    a < 2.5657 × 10⁻³   and   κ < a/(1+a) < 2.5592 × 10⁻³   for every word on the design, at every p.

The cost per port at `p = 13` (`h = 26`, `m = 78`, `v = 2288`, `D = 2704`):

| term | cost per port |
|---|---:|
| source registers `3(f(1) + f(2) + f(h−4))` | 118.59 |
| target registers and endpoints `3f(h−1) + 2f(2)` | 99.99 |
| two units per source `2U₂` | 215.42 |
| target balance `τ` | 22.37 |
| source roles enter from 0 | 3.29 |
| star copies | 0.96 |
| **total** | **460.63** |

Each ingredient lowers the ceiling:

| floor | ceiling on `a` |
|---|---:|
| data registers and star copies only | 6.3627e-3 |
| + one unit per source (Lemma E) | 4.2121e-3 |
| + a second non-idle unit per source (Lemma D) | 2.9420e-3 |
| + registers at each target's hyperplane (Lemma T) | 2.7868e-3 |
| + source roles enter from frame 0 (Lemma E) | 2.7653e-3 |
| + the `K` itinerary of the source registers (R7) | 2.5657e-3 |

If the `K` step were also free, the source registers would only be known to cost `3f(h−1)`, and the ceiling would be
the fifth row.

---

## 11. Scope and limits

**Assumed.** Rules R1–R8 of §3.4, as properties of #144's word format:

- each source is injected once, into one source role;
- `H` is produced only through auxiliary root groups and sinks, with conservative supports inside frames;
- every role's old content is cancelled by a read at the frame where the role begins;
- sink groups are disjoint;
- the source registers follow the `K` itinerary, and the three stages run the same word.

**Not covered.**

- **Source-assisted words** (#184, #191, #193, #194). They use the original source registers as controls at later
  frames and reuse registers after exact cancellation. That breaks R2 and the conservative supports of R1, so
  Lemmas E, T and D do not apply. Their best complex saving so far is 7.009184 × 10⁻⁴ (#193).
- **A different decoder, port family or stage structure.** Those change §3.
- **The bit supplier.** The bound is on the complex saving. κ is also below the bit saving, which this note does not
  bound.

**Proved by hand, for all `p ≥ 7`:** Lemmas 1, 2, S, M, E, T, D, the count of `col(S)`, the charging of §9 given its
side conditions, and the tail.

**Computer, exact arithmetic (`ceiling.py`):**

- `D/C(p)` for `7 ≤ p ≤ 99`, and the maximum over `p`;
- the side conditions of §9.2 at each of those `p`;
- the tail value at `p = 100`.

**Computer, sanity only (not used by the proof):**

- `ceiling.py --brute` enumerates `col(S)`, checks Lemma S, and checks Lemma M: over every `w` at `p = 7, 8`, and over
  one `w` from each symmetry orbit for `7 ≤ p ≤ 16`.
- `model_check.py` rebuilds the abstraction of §3–§8 for a real certified word and checks every lemma's conclusion
  on it. On #144's word (`p = 12`, on main) and on #168's word (`p = 11`, with frame layer, 2,310 reuse pairs and 47
  sinks) it finds:
  - the abstraction lists exactly the certified children;
  - every source role enters from frame 0 at its own line;
  - every source has three units, all big, and every target of `col(S)` is reached through a unit exit;
  - every target has three T-registers (#144) or two (#168);
  - every unit, source and target pays at least its floor.

  It was not run on main's selected word (#186), which is stored in its own archive format.

**Not tight.** On those two words the floor `C(p)` is 19% and 26% of the certified cost. The theorem charges two
registers per source; the certified words use about eight auxiliary registers per port. The extra registers carry
each `x_S` above its line to its roughly `8p³/6` targets, and they are shared between sources. Charging them needs a
lower bound on frame-constrained, cancellation-free circuits for `H`, which this note does not have.

**Not reviewed.** Nothing here is machine-checked beyond the scripts' exact arithmetic and self-tests, and no one
else has reviewed the proofs.

## Reproduce

    python3 research/design-ceiling/ceiling.py --check     # the ceiling, exact; under a second
    python3 research/design-ceiling/ceiling.py --brute     # counting lemmas at small p; a few seconds
    python3 research/design-ceiling/model_check.py         # the lemmas on #144's word; about 15 seconds
