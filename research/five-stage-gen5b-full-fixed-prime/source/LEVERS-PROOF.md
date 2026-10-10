# Early helper restoration and terminal sinks on the gen5 kernel word

Two transcript stages are added after the kernel stage of #290 (#285's gen5 word, #287's descent and target stages,
the 450 collective kernel entries), in this order: `restore_transform.py`, then `sink_transform.py`. Both screen the
actual input word freshly and must reproduce their frozen selection (`restore-selection.json`, `sink-selection.json`,
each bound to the SHA256 of its input word and scalar projection).

## 1. Early restoration (PR #280 mechanism, PR #283 endpoint-aware banking)

Cut: the first `cleanup_gate` ADD (record 601,737 of the kernel word). At the cut every target row is final (checked
on all 1,760 F2 target rows). A helper a qualifies when its formal row is untouched at the cut, its only remaining
scalar incidence is a += c·b, b is not written between the cut and that incidence, and no COPY/ERASE follows the cut.
On gen5 exactly 794 helpers pass; 440 of them (entrance rank 20, current frames of a and b rank 22) have an exact
rational join E of rank 23 that is nondegenerate for 9I−J; the other 354 (entrance 21, frames 23/23) join to the full
frame and are not changed. All 440 helpers and 440 donors are distinct and the two sets are disjoint; all c = −1.
These are exactly the counts and shapes of #280's gen4 screen. Kernel members are plain helpers (entrance 0), the
target squares act on targets, so neither stage overlaps.

Integer argument. The moved shear a += c·b commutes with every crossed gate u += d·w because u ≠ a, w ≠ a (a has no
other incidence) and u ≠ b (b unwritten on the interval) — checked on every crossed gate of the actual word. So
executing the 440 shears at the cut (disjoint registers, mutually commuting) preserves the signed scalar map for all
inputs, including arbitrary dirty helpers. a then ends at E, not FULL.

Endpoint and banks. With A = σ (the entrance) ⊂ E, both nondegenerate, P_σ P_E = P_E P_σ = P_σ, so D = P_E − P_σ is an
idempotent of rank dim E − dim σ = 3, with image E ∩ σ^⊥; the reflected reverse change (I−P_σ)−(I−P_E) is the same D.
The five-stage completion of such a helper is P_σ + (I − P_E) (rank 5·21 instead of 5·20) and its stage-private
residual is D in each of the five windows. `global_lowering` emits these completions (the endpoint frame rides in slot
3 of the COMPLETE record) and keeps the global deficit 4,400; `geometry527` checks one actual (σ, E) pair exactly
(idempotence, commutation, traces, disjoint windows) and rejects the old formula I − P_σ; `bank_check` builds every
chart from the G-orthogonal basis (E ∩ σ^⊥ | σ | E^⊥) — 440 new exact charts — and `bank_template` re-tiles: the 440
residuals of width 3 join the (3⁴⁰) banks (531 → 1,191 per stage) and leave the (4³⁰) banks (−880 per stage), all
assignments enumerated. Local paid delta {1: +1,320, 2: −880} (two rank-2 climbs become three rank-1 climbs per helper);
endpoint rank saving 440.

Checks: fresh screen = frozen selection; integer commutation on every crossed gate; F2 replay of all 19,406 columns
forward and inverse; omitting the moved restorations is rejected; every MOVE rebuilt from operand frames, both reflected
ledgers, all used frames nondegenerate; the completion histogram (completion rank σ + 24 − dim endpoint) is pinned and
used by the global, bank, math and finite stages.

## 2. Terminal sinks (PR #283 mechanism)

Entry: the last copied-centre ERASE (record 505,285). A zero-to-full helper r qualifies when its only uses are one
initial dirty read y_t += −r at ZERO for each t of a target set S before the entry, forward writes r += x after it,
one terminal delivery y_t += r at a common root frame for each t ∈ S after the last forward write, and cleanup writes
r −= x after the last delivery (never copied). 16 helpers on gen5 have this shape (as on gen4); in 8 of them a target of
S is read by #287's target squares, which breaks the commutation argument (and the pivot's frame chain), so they are
excluded. The 8 kept (S of size 4, two forward writes, two cleanups, root frame rank 21) have disjoint S, no target of
S is ever a scalar or COPY source anywhere in the word, and the pivot p (smallest such target) is not otherwise written
on the interval.

Integer argument. Originally each y_t receives −d_r + (d_r + X) = X, X the sum of the forward writes. In the new word
the writes go to y_p (so y_p receives X), y_t −= y_p is executed right after the entry and y_t += y_p right after the
last forward write, so each y_t (t ≠ p) also receives exactly X; nothing reads a target of S and nothing else writes p
in between, and r was read only by the deleted reads. r is deleted (registers compacted, n 19,406 → 19,398, R 15,886 →
15,878; the removed roles are recorded in the context so the bank census still checks the role set).

Checks: fresh screen = frozen selection; the coefficient pattern (−1 reads, +1 deliveries, +1 writes, −1 cleanups) and
the source/writer conditions on the actual word; F2 replay of all 19,398 remaining columns forward and inverse; three
omission controls (redirected writes, setup, restore) rejected; MOVEs rebuilt, both reflected ledgers; each removed
helper frees exactly its 24-rank path (local delta {3: −8, 21: −8}); the global lowering, banks ((24⁵) family shrinks by
96 per stage), scalar projection, math and finite stages run at R = 15,878 with the deficit 4,400 rechecked.

## Ledger and result

Both stages are priced from the fresh composed word, not added: local delta {1: +1,320, 2: −880, 3: −8, 21: −8};
φ-ledger (φ(r) = r·ln(120/r), deficit fixed) gains −886.6 and −381.4. Literal stock 1,244,515 → 1,243,415 → 1,242,935;
banks per stage 164,423 → 164,203 → 164,107. κ: #290 7.44714499357628·10⁻⁴ → 7.45272862652714·10⁻⁴ (restorations,
+0.0750%) → 745513573133379/10¹⁸ = 7.45513573133379·10⁻⁴ (sinks, +0.0323%; +0.1073% in all); bit coarse
7.46069778575685·10⁻⁴, below the complex supplier's 7.54736418878859·10⁻⁴ (#233 word in the five-stage layout), so the
bit side binds. Each value equals the ledger model's prediction made before the stage was built.

## Lever not shipped: transported dirty entrances (PR #280)

On gen5 the transport cut must follow #287's ZERO-frame target-prefix setups (record 505,945), which read targets as
sources; 1,910 of the 1,975 untouched plain helpers have a target in a square and fail the commutation condition. Of
the rest only 8 (four reads, first frame 19, entrance 19) have a negative φ balance (helper gain φ(19) against four
target climbs split at E), total −68.8 (≈ +0.006% κ); after the sinks only 4 remain (−34.4, ≈ +0.003%), the others'
targets now carry sink setups. Not implemented.
