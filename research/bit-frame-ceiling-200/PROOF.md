# A frame-layout ceiling for #200's physical bit word

This note proves an upper bound on the coarse bit saving, and hence on κ, that any choice of operation frames for
the physical bit word of #200 can certify, and applies it to the two ledgers in use on that word: #200's own and the
completed-entrance-bank ledger of #205, #206 and #207. It makes no κ claim and changes no existing file. The method
is DaysSky's #192 (`research/kappa-ceiling`), carried from #168's complex word to this bit word; the facts below
restate #192's with the bit ledger in place of the complex one. `ceiling.py` evaluates every bound with exact
integers and checks its own model against #200's certified ledger child for child.

## Setting

A shared-core bit supplier is described per group vertex by `W` roles, `m = 3h`, and a multiset of children: `n_r`
children of width `r`, `0 < r < m`. Its rank mass telescopes, `Σ_r r·n_r = W·m − D` with `D = 2v − 3ℓ`
(`v` ports, `ℓ` the copied-centre loss). Write `f(r) = r·ln(m/r)` and `C = Σ_r n_r·f(r)`. The repository certifies a
coarse saving `a` when an exact upper bound on the paid moment `Σ n_r·(r/(W·m))·(m/r)^a` plus the positive bad-class
term is below 1 (`bit/prove.py`, `arithmetic/interval_moment.py` in #200). So a certified `a` satisfies

    Σ_r n_r·r·(m/r)^a < W·m.                                                     (∗)

**Fact 1 (moment root, #192 Lemma 1).** If (∗) holds then `a < D/C`, since `(m/r)^a ≥ 1 + a·ln(m/r)`. On #200 the
certified coarse saving lies 0.088% below `D/C` (`ceiling.py`, fact 1).

**Fact 2 (assembly and bootstrap).** #183 (romainhedouin) gives the balanced assembly's acceptance region in closed
form: κ below `G_η(a) = a(1−2η)(1−η)/(1 + a(1−2η))`, increasing in `a` and decreasing in `η`, so `κ < a/(1+a)` for
every `η > 0`. The ordinary-leaf wrapper gives `A_B = (1−θ)·a + θ·a_old < a`. The finite stopped-leaf bootstrap of
#185/#197/#207 produces `a_j = (1−c)·c + c·a_{j−1} < c` at every level from the coarse saving `c`. Hence every κ
built on this word by any of these assemblies satisfies `κ < G(min(bit, complex)) < G(bit coarse) ≤ G(D/C)` with the
bit ledger's `D` and `C`.

**Fact 3 (chains, #192 Lemma 3).** `f` is strictly subadditive on `(0, m)`, so a chain of steps of total width `t`
costs at least `f(t)`; splitting a frame climb into more steps only costs more.

## Fact 4: the frame floor of the fixed word

The certified bit ledger (`scripts/paired_cube_bit_physical.py` of PR168 v4, re-counted by #200's `bit/word.py` and
`bit/terminal.py`) consists of, per vertex:

- three times the steps of every physical slot's frame chain, where a slot starts at 0, at its source line `⟨χ_S⟩`
  or at its gauge `σ`, passes the frame of each of its operations in execution order, its root frame if it is a root,
  and ends at the full space; a recipient continues its donor's slot through the exact step into its gauge;
- three times the source-injection children of width 1 and the copied-centre children (width `dim` of the centre);
- three times the partner-chain (source data) steps, fixed by the partner chronology `kchron`;
- three times the target-chain steps, fixed by the gauges' targets and read order, the side-root frames and the
  partner deliveries;
- one child of width `3·dim σ` per gauged first occupant that is not a recipient (the entrance tails);
- `2v` children of width 2.

`ceiling.py` rebuilds this multiset from the word with #200's own operation frames and checks that it equals
`overridden_profile.child_histogram` of #200's certificate exactly (W 20,668; rank 1,486,160), and that subtracting
the terminal record gives `profile.child_histogram`.

Fix the word: its DAG, operations and execution order, sources and source frames, gauges and read chronology, reuse
pairs, partner chronology, root frames and terminal sinks. The free choice is the frame `F_i` of each operation. An
admissible layout satisfies, as checked by the retained physical checker before the terminal record is applied:
`span(x_i) ⊆ F_i`; both registers of operation `i` are at `F_i` while it runs; every slot's frames nest along its
chain; a donor's last frame lies inside its recipient's gauge; a root is read at its root frame.

**Lemma 4a (joint bounds).** Every admissible layout has `L_i ⊆ F_i ⊆ U_i`, where `L_i = span(x_i) + L_prev(a) +
L_prev(b)` runs forward in execution order from the registers' entrance frames and `U_i = U_next(a) ∩ U_next(b)` runs
backward from root frames, recipients' gauges (for donors) and the full space. *Proof.* Both registers sit at `F_i`,
so `F_i` contains everything below either register's previous frame and lies inside everything above either
register's next frame; the ends of every chain are fixed. ∎ Values only move between registers through operations,
whose shared frame links both chains, so this backward pass already carries every root constraint reachable from
`x_i`. `ceiling.py` checks that #200's layout, and #207's 302-frame layout when given, satisfy every bound.

**Lemma 4b (slot floor).** For each slot, take the minimum of `Σ f(steps)` over nondecreasing dimension sequences with
`d_i ∈ [dim(cumulative L), dim(cumulative U)]` at each event; exact events (gauge of a recipient, root frame) are
fixed; the sequence starts at the entrance dimension and ends at `h`. The sum over slots is at most the slots' cost in
every admissible layout. *Proof.* As in #192: only the coupling between the two registers of an operation and the
subspace structure are dropped. ∎

**Lemma 4c (coupling).** For any integer prices `λ_i`, adding `+λ_i·d` to the destination register's cost and `−λ_i·d`
to the control register's cost at operation `i` keeps the sum of per-slot minima a lower bound, since both registers
share `d = dim F_i` in any admissible layout. ∎ `ceiling.py` runs subgradient rounds on the prices, keeps the best
round and asserts every round's total lies below #200's own layout cost.

**The terminal record.** #200's `bit/terminal.py` (the bit form of #166) deletes each sink register and copies its
rank increments to a pivot target; the certified substitution removes, per sink and stage, exactly the sink's last
step (root frame to full space, width `h − dim root = 3`, present in every layout since the root frame is fixed) and
one target child of width 21 (the pivot's cap read, fixed by the gauges and roots), and keeps every other step
charged. `ceiling.py` checks this against the certificate's `child_delta` (−102 of width 3, −102 of width 21) and the
pre/post target histograms, so the floor of the terminal ledger is the pre-sink floor minus this fixed cost. #207
audits the same −102/−102 substitution on its layout.

**The two ledgers.** `C_own` includes the entrance tails `3·dim σ`; `C_banked` omits them, which is the only ledger
change the completed-entrance-bank construction of #205/#206/#207 makes to the children (their `W` changes do not
enter `D/C`). Both floors share the slot floor and the fixed parts. Hence, for every admissible frame layout of this
word,

    coarse_own < D / C_own,floor      and      coarse_banked < D / C_banked,floor,

and `κ < G(·)` of each.

**Arithmetic.** Every logarithm is a rational lower bound (partial sums of `2·atanh`, nonnegative terms, truncation
below `3^-80`), every `f(r)` is rounded down on the grid `2^-64`, and all sums, the dynamic programme and the prices
are exact integers. The printed ceilings are rounded up on the `10^-7` grid.

## Result

`ceiling.py --check` (1,200 Lagrangian rounds, about 2.5 minutes, stdlib only) on the pinned files of #200 gives:

| Ledger | Floor on C | Coarse saving ceiling | κ ceiling | Certified layout |
|---|---:|---:|---:|---|
| #200's own (entrance tails charged) | 2,804,210 | **6.904e-4** | 6.900e-4 | #200's coarse 6.7777e-4 is 98.2% of the ceiling |
| completed entrance banks (#205/#206/#207) | 2,780,144 | **6.964e-4** | **6.959e-4** | #207's bit coarse 6.8366e-4 (D/C 6.8427e-4) is 98.2% of it |
| without coupling the two registers of an operation | | 7.056e-4 / 7.118e-4 | | |

The deficit is `D = 2v − 3ℓ = 1,936` (`v = 1,760`, `ℓ = 528`, `h = 24`, `m = 72`); the word has 41,288 operations,
18,908 roles, 1,760 reuse pairs and 34 sinks. `--overrides` on #207's `frames/opframe-bases.json` confirms that its
302-frame layout lies inside every joint bound and above the floor.

Consequences.

- Every frame refinement still possible on this word is worth at most +1.8% on the bit side under either ledger.
- The complex supplier used with this word (#202's source-assisted word, coarse 7.00918e-4, itself within 0.01% of
  #192's 7.010e-4 ceiling for its own frames) can never become the binding branch: the bit ceiling 6.964e-4 lies below
  it. So every κ assembled from this bit word and any complex word at or below that ceiling stays below 6.959e-4, no
  matter how the bit frames are chosen. Going further needs a different bit word (circuit, reuse, gauges or sinks),
  a bank construction that removes other children, or a different design (DaysSky's #201 bounds the design at
  2.5592e-3).


## Scope and limits

- The ceiling covers one word: the DAG, operations, sources, gauges, reuse pairs, partner chronology and 34 sinks of
  #200 at `a1175449`. #205, #206 and #207 keep all of these (#207 changes 302 operation frames), so it covers their
  rows. It does not bound constructions that change the word, the pairs, the gauges or the sinks, nor a different
  bank construction that removes other children.
- Fact 2 uses only that every retained assembly accepts κ below `a/(1+a)` of the binding supplier and that the
  bootstrap stays below its coarse saving. It does not re-verify any assembly or bank construction.
- The proofs are elementary and not machine-checked beyond the script's exact arithmetic and self-tests.
