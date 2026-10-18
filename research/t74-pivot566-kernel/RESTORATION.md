# Restoration argument for the pivot-566 kernel

This note is the written argument behind `kernel_check.py`, which checks every step below exactly (standard library,
about 4 seconds; receipt `evidence/KERNEL-CHECK.json`). Everything holds identically on both PR1297 words (gauge44 and
extra, which have the same gates).

## Program and edit

The program semantics are those of the unchanged independent `audit_local.py` (#645). A call runs

  precondition → compensation → A → cut → B → early-cleanup tail → remaining cleanup.

The compensation is derived from the word: it cancels the helper columns of the port rows (registers 112–223) of the
A → cut → B map. The whole program must equal the call map: ports += data, every other register restored, in both
orientations.

The kernel changes only reads of the cold pivot q = 566. It makes nine changes (`inputs/EDITS.json`; B indices are the
original word's):

- it deletes `494 -= q` (B755);
- it inserts `150 += q`, `209 -= q`, `590 -= q` and `672 -= 2q` before B0, `590 += q` before B47, `672 += 2q` before B224
  and `98 -= q` before B520;
- it inserts `98 += q` at early-cleanup position 86.

Precondition, A, cut, remaining cleanup and interfaces are byte-identical.

## Lemma

Suppose no inserted gate writes q, and every inserted read of q (new program) and every deleted read (old program)
happens while q holds its initial value x_q. Then, after any gate, new state − old state = x_q · D, where

  D = Σ_i c_i S_i e_{t_i}.

Here term i adds c_i·q to register t_i, and S_i is the product of the common gates after term i. The deleted gate
`494 -= q` enters as the term `494 += q`, the effect of its removal.

Proof: by induction over the gates. A common gate is linear, so it maps the difference to its image. An inserted gate
adds c_i·x_q·e_{t_i} to the new state only. A deleted gate's absence removes its c·x_q·e_t from the old state's side.
So only q's column can change, and D is the whole difference.

The hypothesis holds. q is written only at B866 (`566 += 98`) and restored at early-cleanup position 85
(`566 -= 98`). Every new read lies before B866 or after position 85, and the deleted read B755 lies before B866.
`kernel_check.py` confirms it directly: q's row equals e_q, from the program start, at all eight inserted reads in the
new program and at B755 in the old one.

## Ledger

Each term's contribution S_i e_{t_i} at the end of the tail (coefficients of x_q; all other registers 0):

| Term | 98 | 145 | 146 | 149 | 150 | 161 | 163 | 164 | 166 | 209 | 210 | 482 | 494 | 590 | 672 | 679 | 697 | 702 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deleted `494 -= q` (B755) |  |  |  |  |  | +1 | +1 | −1 | −1 | +1 | −1 | +1 | +1/2 |  |  |  | +1 | +1/2 |
| `98 -= q` before B520 | −1 | −1 | +1 | −1 | +1 | −1 | −1 | +1 | +1 |  |  | −1 | −1/2 |  |  |  | −1 | −1/2 |
| `98 += q` at early-cleanup position 86 | +1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `150 += q` before B0 |  |  |  | +1 | −1 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `590 -= q` before B0 |  |  |  |  |  |  |  |  |  |  |  |  |  | −1 |  |  |  |  |
| `590 += q` before B47 |  | +1 | −1 |  |  |  |  |  |  |  |  |  |  | +1 |  |  |  |  |
| `209 -= q` before B0 |  |  |  |  |  |  |  |  |  | −1 | −1 |  |  |  |  |  |  |  |
| `672 -= 2q` before B0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | −2 | +1 |  |  |
| `672 += 2q` before B224 |  |  |  |  |  |  |  |  |  |  | +2 |  |  |  | +2 | −1 |  |  |
| **sum** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

How the terms cancel:

- **The helper window on 98 re-delivers into the deleted read's cone.** It reaches exactly the registers that the
  deleted `494 -= q` reached (161, 163, 164, 166, 482, 494, 697, 702), with opposite signs.
  - 98 is written at B852 (`98 += 397`) and read at B866, B1177 (`150 += 98`) and early-cleanup position 85.
  - With 98 carrying −x_q from B520, q carries −x_q from its write B866 on. q's later reads (B907 `146 += q`,
    B1050 `494 += q`) carry that difference on.
- **The 590 donor window and `150 += q`** cancel the window's extra reach into 145/146 and 149/150.
- **`209 -= q` and the 672 donor window** take over the deleted read's share of 209 and 210.
- **At the end of B** the difference is exactly D = −e_98 − e_566: 98's window is still open, and q carries its copy.
  - Position 85 (`566 -= 98`) cancels q's difference, because 98's difference is the same.
  - q is then x_q again, so the new gate `98 += q` at position 86 closes the window.

## Compensation and the whole program

- The compensation is unchanged. At the end of B, D touches only 98 and 566, so no port row of the A → cut → B map
  changes, and the derived compensation cannot change. Both derivations are also computed and compared gate by gate:
  7,208 gates, identical.
- The B + tail map is unchanged: all register rows, from the program start, compare equal (0 differ).
- So the whole program map is unchanged.

Independently of this argument, the unchanged `audit_local.py` checks each shipped word on its own. The whole program
must equal the call map in both orientations, and every frame chain, entrance, end frame and cone must be legal. Both
words pass (`verify.py`).

## Frames and price

Recounted from the frames, with audit_local's climb rules, the paid profile per call changes by H1 +1, H2 −2, H3 +1 on
both words:

- gauge44: {1: 2346, 2: 504, 3: 414, 4: 130, 5: 82, 8: 8} → {1: 2347, 2: 502, 3: 415, 4: 130, 5: 82, 8: 8};
- extra: {1: 2338, 2: 512, 3: 418, 4: 126, 5: 82, 8: 8} → {1: 2339, 2: 510, 3: 419, 4: 126, 5: 82, 8: 8}.

Only two register chains change, and each keeps its rank mass:

- **494** goes from [1, 2, 1, 1, 2, 1, 1] to [3, 1, 1, 2, 1, 1]. Without the early read at B755, its first two
  climbs merge into one.
- **150** goes from [2, 3, 2, 1] to [1, 1, 3, 2, 1]. The new read `150 += q` at B0 splits its first climb.

At PR1319's endpoint the surrogate weights give c_1 − 2c_2 + c_3 = 2,116,453 − 2·4,227,981 + 6,337,654 = −1,855 units
per call, the recorded delta (`evidence/PRICING.json`).

The frames come from the PR1186 exact solver. Their legality does not depend on it, because `audit_local.py` and the
native chain check them.

## Controls

Each mutated edit is checked by the same scalar steps, and each fails:

| Mutation | What breaks |
|---|---|
| `98 += q` dropped | D ≠ 0 at the end of the tail (1 register) |
| `98 += q` at position 85, before q's own restoration | the lemma (q is not x_q there), and D ≠ 0 (2 registers) |
| donor 672 opened with +2q | D ≠ 0 (2 registers) |
| deleted read B755 kept | D ≠ 0 (10 registers), ports touched at the end of B, compensation changes |

## Scope

This is an exact finite argument about the two local words. The construction's inherited all-size compiler,
common-label/mutable-source, hosting, precision/tape, analytic and bit assumptions are unchanged and not addressed here.
