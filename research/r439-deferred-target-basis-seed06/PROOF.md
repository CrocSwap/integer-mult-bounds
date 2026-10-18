# Deferred target basis (H5-tw): proofs

This note proves four statements and records one refinement:

1. the replacement lemma H5-tw, with its converse;
2. that deferring the target-basis undo turns every lineage word into a word meeting H5-tw, with a
   unique scatter listing;
3. the cut-by-cut bridge, with an argued physical reading that needs no premise beyond those the base
   words already use;
4. maximality of the deferral under fixed ordered frame paths, among prefix splits of the literal undo
   order;
5. the order-ideal refinement: splitting the undo at a commutation-closed down-set. On every word the
   search finds a split three scatter ADDs below full deferral, and the split is fully checked on
   four words. It is found by search and is not claimed optimal.

`verify.py` checks every finite fact used here, on every committed lineage word (as of base
c6765481).

## Notation

A word has `n = 2v + r` registers: sources `x` (v of them), targets `y` (v) and helpers `h` (r).
Write `z = (x, h)`. Here `v = 111`, `r = 439` and `n = 661`. The word runs D, then A, then the
scatter, then B, then C. The scatter is realised literally: COPY one retained helper into a clean
temporary at the zero frame, ADD that temporary into the listed targets, then ERASE it. Each ADD
`d ^= s` is an elementary transvection over F2.

As in PR1868, a finite product of transvections acts on `M^n` for any F2-module M through its F2
coefficient matrix. "Boundary" means the complete coefficient matrix on all 661 columns, with
arbitrary ("dirty") helper inputs.

The kept clauses come from the inherited interleaved lemma. eumemic's PR543 states it (restated in
`research/e8-bit-r420/README.md`), and eumemic's PR555 adaptation `xcheck_p.py` checks it:

- **H1**: no gate whose destination is a z register reads a target.
- **H3**: A writes only z registers. The scatter reads only retained helpers and writes only targets.
  Each B gate either writes a z register from z registers, or writes a target (from any sources).
- **C clause**: every C gate has a z destination, reads only z registers and runs at the full frame.
- **D-shape** (the structural part of H2, as in PR1194 and PR1868): every D gate is at the zero frame
  and reads and writes only targets and helpers. D contains no COPY, ERASE or climb.

By H1 no helper gate in D reads a target, so D's operator has the form

    (x, y, h) -> (x, R y + N h, T h)

for a v-by-v matrix R, a v-by-r matrix N and an r-by-r matrix T. By H1 and H3 the raw word
`W0' = (A, scatter, B)` has the block form

    z' = U' z,      y' = V y + J x + K' h.

The inherited H2 target clause is `R = I`: D adds to the targets without changing their basis. This
is also PR1194's "complete restoration of every target basis at D's boundary". The inherited H5 is
`V = I`.

## 1. The replacement lemma H5-tw

**Contract H5-tw.** Keep H1, H3, the C clause and the D-shape. Replace the pair (H2 target clause
`R = I`, H5 `V = I`) and the K check by:

    (i)   V R = I,
    (ii)  J = I,
    (iii) V N = K' T,
    (iv)  C U' (I_x ⊕ T) = I on z.

**Lemma.** Under the kept clauses, the complete word maps `(x, y, h) -> (x, y + x, h)` on every
F2-module if and only if (i)–(iv) hold.

*Proof.* D sends `(x, y, h)` to `(x, R y + N h, T h)`. Applying `W0'` gives

    z' = U' (x, T h) = U' (I ⊕ T) z,
    y' = V (R y + N h) + J x + K' T h = V R y + J x + (V N + K' T) h.

C reads and writes only z registers, so it leaves y unchanged and sends z' to `C U' (I ⊕ T) z`.
The final state is therefore

    (z, y)  ->  (C U' (I ⊕ T) z,  V R y + J x + (V N + K' T) h).

If (i)–(iv) hold, this is `(z, y + x)`, since `V N + K'T = 0` over F2. Every coefficient lies in F2,
so the identity holds on every M.

Conversely, suppose the boundary `(x, y, h) -> (x, y + x, h)` holds. Evaluate on the F2 unit columns:

- the target rows on the target columns give `V R = I`;
- the target rows on the source columns give `J = I`;
- the target rows on the helper columns give `V N + K'T = 0`;
- the z rows give `C U' (I ⊕ T) = I`. ∎

**Remarks.**

- **Invertibility.** `V R = I` forces R and V to be invertible, with `V = R^-1`.
- **The inherited case.** With `R = I`, (i) is H5, so the inherited contract is the case `R = V = I`.
  - (iii) with `V = T = I` is PR1194's `N = K`.
  - (iii) with `V = I` and general T is PR1868's K-tw.
- **The cleanup (iv).**
  - Under the literal H4 (C is the reversed list of z-gates of A and B), `C = U'^-1`, so (iv) holds if
    and only if `T = I`.
  - PR1868's H4-tw is (iv) itself.
  - So the converse proves (iv) from the boundary; it is not assumed through the C clause, which only
    fixes C's shape.
- **The listing is unique.** The scatter listing is determined by the rest of the word. Suppose a word
  keeps D, A, B and C and changes only the listing, from L to L'.
  - The retained totals are nine distinct registers of an invertible state, so their columns c are
    linearly independent.
  - The final targets change by `V_B (L' + L) c`, where `V_B` is the invertible target block of
    everything between the scatter and the end.
  - So L is the only listing that meets the boundary.

## 2. The deferral meets H5-tw

**Shape of the lineage words.** Every committed PR915-lineage word has a D section of the form

    helper-star preparations, P_E, reads, U_E, helper restorations.

- `P_E` is the target-basis preparation: 306 target-from-target gates (307 on PR1040 and PR1449).
  Its product is E.
- The reads are 111 gates, target-from-helpers.
- `U_E` is the undo: exactly `P_E` reversed, gate by gate, so its product is `E^-1`.

All of these gates are at the zero frame. There are small layout variations:

- the helper parts are empty on PR915's word;
- on PR1047 and PR1449 one helper gate sits on each side of the reads;
- on PR1449 the preparation is not contiguous.

The argument only uses three facts:

- the target gates before the first read are exactly `P_E`;
- the target gates after the last read are exactly `U_E`;
- no target-from-target gate sits among the reads.

`verify.py` checks all three on every word.

**The base word W.** W satisfies the inherited target clauses `R = I` and `V = I`. Let the reads add
`M h~` to the targets, where `h~ = T_s h` is the helper state at the reads and `T_s` is the
helper-star preparation. Then W's D target operator is

    y -> E^-1 (E y + M T_s h) = y + N h,      N = E^-1 M T_s.

W also satisfies (iii) and (iv):

- the 17 words with `T = I` satisfy PR1194's `N = K`, with literal H4;
- PR1868's two absorbed words satisfy its K-tw and H4-tw.

**The deferred word W'.** W' makes three changes:

- it deletes `U_E` from D;
- it replaces the scatter listing S (rows over the nine retained totals) by `E S`;
- it runs the same `U_E` gates, at the zero frame, as the first gates of B.

**The deferred word's blocks.**

- *D.* D' is D without `U_E`. Its target operator is `y -> E y + M T_s h = E (y + N h)`, so
  `R' = E`, `N' = E N` and `T' = T`.
- *Up to the undo.* A does not touch targets (H1, H3). The scatter adds `E S c`, where c holds the
  nine COPY values (functions of z only). The undo then maps the targets by `E^-1`. So after the undo
  the targets hold `E^-1 y + S c`, exactly what W's targets hold after its own scatter on input
  `E^-1 y`. B is unchanged.
- *The raw word.* Hence `W0''(y) = W0(E^-1 y)`, which gives `V'' = V E^-1 = E^-1`, `J'' = J = I`,
  `K'' = K'` and `U'' = U'`.

Therefore:

    V'' R'  = E^-1 E = I,
    V'' N'  = E^-1 E N = N = K' T,
    J''     = I,

and C, U' and T are unchanged, so (iv) is inherited. W' meets H5-tw with `R = E` and `V = E^-1`.
It fails H5 (`V ≠ I`) and the H2 target clause (`R ≠ I`). By the uniqueness remark, `E S` is the
only listing for this placement.

`verify.py` computes R, N, T, V, J and K' directly from the words, not from this derivation. It
checks:

- `R = E` and `V = E^-1`, the latter as the matrix of the literal undo gates;
- (i)–(iv), and the D-shape;
- that the base word is the `R = V = I` case;
- that T is unchanged.

The controls exhibit the converse: each failing control violates at least one equation, and its
dirty endpoint fails.

| control | failed equations | dirty endpoint |
|---|---|---|
| old listing S | J, K | wrong on all 111 targets |
| dropped undo gate | V R, K | wrong on 6 targets |
| undo in preparation order | V R, J, K | wrong on 111 targets |
| one wrong E S row | J, K | wrong on 6 targets |
| swapped non-commuting undo pair | V R, K | wrong on 24 targets |

Here "K" abbreviates `V N = K'T`. Every control fails the dirty endpoint.

## 3. The bridge, cut by cut

Align W and W' as follows:

- the common D gates;
- W's undo, which W' skips;
- the common helper restorations and A;
- the nine COPY blocks (W adds column j of S, W' adds column j of E S);
- W''s deferred undo, which W skips;
- the common B and C.

**Invariant.** At every cut in this alignment:

1. every non-target register has the same value and the same frame in W and W';
2. every target is at the zero frame in both words;
3. W''s target vector equals `M_c` times W's target vector.

Here `M_c` is I before W's undo. During W's undo it is the running product, and it equals E from the
end of W's undo through the last COPY block. During W''s undo it is again a running product, and it
returns to I.

*Proof.* Induction over the cuts:

- *Common z gates.* By H1 they read no target, so they see identical operands in both words.
- *Undo gates.* These are the only target-from-target gates in the window. A W-only gate G updates
  `M <- M G`, and a W'-only gate updates `M <- G M`. Both run at the zero frame on registers that
  are at the zero frame.
- *COPY blocks.* A block copies the same retained total (a z register, equal in both words) and adds
  `S_j c_j` in W and `E S_j c_j = M (S_j c_j)` in W'.
- *Frames.* Targets never move before B: A and the scatter do not climb them, and the exporter places
  every scatter ADD at the zero frame.

After W''s undo, `M = I`, so the complete states agree in value and frame. The remaining
instructions (B and C) are identical.

**What `verify.py` replays.** It replays both words in lockstep with frames. The deferred side is the
deferred word itself: its D and A must equal the replayed steps, and its B must start with the replayed
undo. It checks the invariant at every cut. A listing other than `M S` breaks the invariant at the
first COPY block it affects; the old-S control is rejected exactly there.

For example, there are 3,585 cuts on PR1062, of which 2,931 have twisted targets, and 3,136 on PR1188,
with 2,482 twisted. The verifier also checks that no z gate reads a target in the window and that
`M = E` when the scatter starts.

**Physical reading (argued, not proved).** The physical realization of W is inherited:

- For the 17 words with `T = I`, `verify.py` re-checks two facts. W's D has the same complete
  operator as PR589's D. The PR1194-style proof-only splice, W's A/scatter/B/C with PR589's
  target-only D, passes every inherited owner flag.
- For PR1868's two absorbed words, PR1868's own per-cut bridge applies.

We argue that W' needs no new physical premise. W' differs from W, at every cut, only on targets. They
differ by a linear map of the targets, and the twisted targets are:

- held at the zero frame;
- read by no z gate.

The gates that realize this map in W' are of kinds the inherited interface already admits after A:

- **Undo gates.** The deferred undo consists of B target writes from target sources, which the
  inherited H3 permits ("writes a target", any sources). They run under the inherited common-label
  realization at the zero frame, where every operand already sits.
- **Scatter ADDs.** W's own scatter ADDs are zero-frame target writes made after A's climbs and the
  COPYs, which is the same situation as the deferred undo and the `E S` listing.

Nothing at a nonzero frame differs, and no register climbs carrying a different value.

This differs from PR1194's substitution, which was restricted to frame-zero D prefixes. Here the
twisted window extends through A and the scatter, though the targets stay at frame zero and unread
throughout.

**Contrast with PR1868.** There, three helpers climbed out of the zero frame while holding
`centre + leaf`. That needed the common-frame / climb-additivity premise, applied newly to helpers.
Here no twisted register ever climbs.

## 4. Maximality under fixed frame paths

In this section **B means W's B**, which is W''s B after the deferred undo. `verify.py` computes these
facts on W's B, and establishes them on all 19 words:

- **(F1) Target-frame disjointness.** For each target, take the set of nonzero frames on its ordered
  frame path. These sets are pairwise disjoint: none of the 6,105 target pairs share a nonzero frame.
- **(F2) Every first B touch climbs.** Every target's first B touch runs at a nonzero frame. The very
  first B gate, B[0], is such a climb.
- **(F3) Target-column confinement.** No B target write reads a target, and none runs at the zero
  frame. B's own target block (B alone, from the identity) is I.
- **(F4) The undo covers every target.** All 111 targets are undo operands.

**Proposition 1 (the undo cannot run later).** Keep the gates and the ordered per-register frame
paths. Then every target-from-target gate runs at the zero frame, before the first B climb of either
of its operands.

*Proof.* A gate at frame f needs both operands at f at that moment. With fixed paths, f lies on both
operands' paths, and by F1 the only common frame is the zero frame. Frames never descend, and by F2
each target leaves the zero frame at its first B touch. ∎

Consequences:

- The undo block cannot follow B[0]. Its target, register 111, is an undo operand (F4).
- Each undo gate can pass only B gates that touch neither of its operands. Such a move is a
  commutation, and changes no value, frame or count.

The control that moves the undo after B[0] is rejected by the frame replay (register 111 would
descend from frame 127 to 0). Ignoring frames, its endpoint is also wrong, on 28 targets.

**Proposition 2 (no B-side absorption).** No undo gate can be absorbed into B.

*Proof.* In the single-edge sense of PR1868, absorption would delete an undo gate `t ^= s` and
compensate in a later gate writing t. In B, such gates are B target writes at nonzero frames f (F3).
Compensating there needs s at f, so f would have to lie on s's path, which F1 excludes. ∎

The census covers every pair (undo gate, B gate writing its destination): 585 pairs per word (587 on
PR1040, 586 on PR1449). None of them is frame-legal.

More generally, B's target block is I (F3), so B supplies no target-from-target mixing. All of
`E^-1` must therefore be realized by zero-frame target gates that run before the first climbs. The
deferred undo is one such placement. The remaining freedom is:

- the choice of circuit for `E^-1` (an open question);
- reorderings that leave its product unchanged. On PR1062 and PR1188, 270 of the 305 adjacent
  transpositions commute, and those keep the boundary. The other 35 change the operator, and the
  checked one breaks the endpoint;
- **where to split the undo between D and B** (below).

**Prefix-split census.** Suppose the first k undo gates, in the literal undo order, stay in D and the
rest are deferred. The scatter then costs `nnz(E_k S)`, where `E_k` is the basis after those k gates.
Among these prefix splits of the literal undo order only, full deferral (k = 0) attains the minimum
over all split points (307, or 308 where E has 307 gates) on every word:

- **Ties.** The first five undo gates leave `E S` itself unchanged, and the first six keep
  `nnz(E_k S) = 97`, so k ≤ 6 tie. On PR1449 the counts are six and seven, so k ≤ 7 tie. On PR1040 the
  minimum is unique.
- **Per-column choice.** Restricted to the two bases I and E for each COPY column, it would not help.
  The old column weights are `[63, 55, 55, 55, 63, 63, 55, 55, 63]`. The E-basis weights are
  `[17, 17, 8, 4, 8, 11, 13, 6, 13]`, or `[17, 16, 8, 4, 8, 10, 13, 6, 13]` on PR1040, so E is
  better on every column. Such a choice would also need the undo inside the scatter, which the word
  format cannot express.

**Scope.** These statements assume fixed ordered frame paths. If paths may change, `verify.py` counts,
for each of the 213 B target writes at frame f, the other targets that could be co-located at f
under three criteria:

| criterion | writes with a partner | max partners |
|---|---:|---:|
| loose upper bound: the target's final frame contains f | 102 | 58 |
| also: its frame at that moment lies inside f | 102 | 55 |
| also: f fits monotonically between its own earlier and later fixed touches | 94 | 7 |

Any such visit inserts a climb into that target's path, which changes the paid profile. That class is
outside this census.

## 5. The order-ideal refinement

Full deferral is not optimal once commuting reorders of the undo are allowed (pre-PR proof review).

**Construction.** Let I be an **order ideal** of the undo's dependency poset: a set of undo gates
closed under "every earlier undo gate it does not commute with". Then:

- the undo sequence is commutation-equivalent to (the gates of I, in order) followed by (the rest, in
  order);
- with `G_I` the product of the gates in I, the rest compose to `E^-1 G_I^-1`.

The ideal-split word keeps the gates of I at the end of D, at the zero frame, lists the scatter as
`G_I E S`, and runs the rest first in B.

**It meets the same lemma.** Its D target operator is `G_I E (y + N h)`, so:

- `R = G_I E`;
- `V = E^-1 G_I^-1`, hence `V R = I`;
- `V N' = N = K'T`;
- J, K', U', T and C are unchanged.

The bridge is the same with `M = G_I E` during A and the scatter.

**Search, pinned in EXPECTED.json.** `verify.py` enumerates every order ideal of size at most 4, and
then runs a greedy strict descent from the empty ideal:

| | 306-gate words | PR1040 |
|---|---|---|
| minimal gates | 61 | 62 |
| ideals of size 0–4 | 1, 61, 1,854, 37,461, 566,500 | 1, 62, 1,915, 39,313, 603,838 |
| best ideal | {31, 51, 52} | {32, 52, 53} |
| scatter nnz | 97 → 94 | 95 → 92 |

PR1449 gives 1, 62, 1,915, 39,315, 603,961 ideals, and its best ideal is {32, 52, 53} with nnz 94.
The greedy descent reaches the same ideal on every word, and no ideal of size 4 improves on size 3.

**Fully checked words.** On PR1062, PR1188, PR1040 and PR1868's absorbed PR1188 word, `verify.py`
builds the best split found and applies the deferred word's checks:

- boundary both ways;
- identical frame paths and MOVE records;
- paid profile from frames and from the exporter;
- guards;
- owner checker, with exactly `H5_V_identity` newly false;
- H5-tw identities with `R = G_I E` and `V` the matrix of the remaining gates;
- the per-cut bridge.

| word | base | full deferral | ideal split |
|---|---:|---:|---:|
| PR1062 | 11,500 | 11,070 | **11,067** |
| PR1188 | 10,492 | 10,062 | **10,059** |
| PR1040 | 11,780 | 11,348 | **11,345** |
| PR1868 absorbed PR1188 | 10,489 | 10,059 | **10,056** |

They match the counts an independent pre-PR reviewer found. F, B and the guard bits equal the full-deferral values.

This is a refinement **found by search, not an optimum.** The only pinned search evidence is the exhaustive
search over ideals of size at most 4 and the greedy descent above; whether larger ideals go lower is open.
Full deferral stays the headline construction because its contract is the cleanest (`R = E`, `V = E^-1`).

## 6. Accounting

The scatter falls from 527 to 97 ADDs. The undo's 306 ADDs (307 on PR1040 and PR1449) move from D to
B; none is deleted. So the complete local count falls by 430. On PR1040 it falls by 432: its E differs
(PR1040's extra target step), and its E S listing has 95 ones.

| quantity | change |
|---|---|
| F | unchanged on every word |
| B | falls on every word |
| guard bits | never rise |
| frames, climbs, COPY ranks | unchanged |
| exporter MOVE records (2,911) | identical |
| paid profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129 | unchanged |

On PR941's floor-calibration word the nine-stage guard moves from 193 to 192 bits. That word is the
only base word that misses the guard, and the guard check must reject it (a pinned control). Its
deferred word meets the guard.

## 7. The selected-word heuristic (PR589)

PR589 has no target-basis block: its D is the 111 reads, so the deferral itself is vacuous there. A
scatter basis G still fits H5-tw, with `R = G` and `V = G^-1`.

**Construction.** Run Prim's algorithm over the 111 scatter rows plus a zero root:

- edge cost is `2 + Hamming distance` (one gate in G and one in `G^-1`, plus the changed row);
- root cost is the row weight.

The tree has 79 edges and 32 roots. G is the 79 transvections `a ^= parent(a)`, children before
parents, placed after the D reads at the zero frame. `G^-1` is G reversed, as the first gates of B.
The listing is `G S`, with 254 ones.

**Cost and checks.** The scatter-related cost falls from 527 to `158 + 254 = 412`, and the word from
24,305 to 24,190 ADDs. `verify.py` applies the same checks:

- boundary;
- frames and MOVE records;
- exporter paid profile and rank mass;
- guards (93/177 bits, unchanged; the reverse bound B rises from 1,113,070 to 1,117,988);
- H5-tw identities;
- the bridge to PR589 itself.

**Owner flags.** PR589 passes every owner flag. The heuristic word makes three newly false:

- `H2_D_frame0_targets_from_helpers` and `K_equals_D`: the same syntactic departure every lineage word
  already has, caused by target-from-target gates in D.
- `H5_V_identity`.

This is a heuristic (an MST over one fixed cost model), not an optimum.

## 8. What is not proved here

- **Native and hosted replay.** Native 5/9/11-stage C++ replay was not run on the deferred words.
  Hosted emission and invoice were not run either; for the deferred PR1122 word, PR1806's PR1122
  nine-stage hosted invoice is the obvious route. The undo now appears in B's exporter phase (4)
  rather than D's (1), and any phase-specific expectation of those tools is unchecked.
- **Inherited obligations.** The all-size compiler, the common-label/mutable-source realization,
  rounding/tape and the analytic obligations remain inherited.
- **Adoption.** Whether H5-tw is accepted as the interface is a maintainer decision. The lemma and
  the argued bridge are offered as the case for it.
