# Independent audit of PR1624's fixed paired26 minimum 62

[PR1624](https://github.com/CrocSwap/integer-mult-bounds/pull/1624) (an664 /
Andrey Mas, head `712a9b9aa8802d0135a578c0debee7b56c8e492f`) claims a theorem
about PR1020's fixed 26-line puncture with designated normal pair (48, 0).
Among exact eight-term complex decoders, the least separate COPY cost is
**62**, with 256 optimal classes and a sharp branch bound of 67. PR1624 notes
two limits on its own evidence. Its two checkers were written in the same
session. Its 69-cost baseline was replayed from transcribed data, not with
PR1020's program.

This package addresses both limits. **Result: corroborated, with no gap
found.**

- `verify.py` was written from proof.md's prose only. PR1624's `verify.py`,
  `audit.py` and `certificate.json` were not read. It recomputes every finite
  premise the written lower bound uses, with exact integer and Fraction
  arithmetic.
- It runs merged PR1020's own charge code (`decoder_check` in
  `research/root-pair-first-drop-seed48/verify.py`) on PR1020's decoder and
  on PR1624's witness. That code prices them at 69 and 62.
- Sections 3, 7 and 9 of the proof are audited in writing below.

## What `verify.py` checks

| proof.md | Recomputed here | Result |
|---|---|---|
| §2 | 120 root lines; the greedy label basis `[0,1,2,3,6,12,20,30,42]`; `N = ell H^-1 ell^T` on all 14,400 entries; live pairing rank 9; minor `[1,2,3,6,12,20,30,42]` with determinant −256 | as stated |
| §2 | designated pair: label dimensions (8, 7), charge 6, `a·b = 2` | as stated |
| §4–5 | all 511 `Z_lambda`: rank by rational RREF, cross-checked mod 2^61−1. No rank ≤ 6. The 29 rank-7 kernels are 27 root lines, `P ∪ {30}`. Each line's annihilator found by enumeration equals the set from the kernel route. Each line's dimension, support size and functionals match the §5 table row for row. | 482 / 29 / 27, table exact |
| §6 | reduced lines in `b^perp` = {r30}; in `a^perp` = the 13 listed; r0 in neither; `c·r_j` list; `q(c, r_j)` | as stated |
| §8 | `A = 2B^-T` rebuilt from the B choice equals the displayed A. `A^T B = AB^T = 2I`. All 8,836 entries (4,572 with zero right-hand side). Actual supports, label dimensions and charges match the §8 table, with two F2 rank routines. | 62 |
| §9 | `x_j + c` gives the literal partner for all six pairs; the determinant is 1024; exactly 256 independent seven-sets of the 13, equal as a set to the `2^6 + 6·2^5` patterns | 256 |
| §9, new | **every one** of the 256 classes expanded entrywise: dual built, first column exactly `a`, no residual A column on `c`, all 8,836 entries checked, charges summed | 256 × 62 |
| §7, new | own Case II witness (second pair `(c, c)`, six generic pairs), built here, not taken from PR1624 | (6,7,9,…,9) = 67 |
| §10 | isotropic complex shear of the witness over Q(i): designated pair unchanged, `A^T B = 2I`, charges (6,8,9,8,…,8) = 63; the conjugate transpose gives 4−4i at roots (1, 1); the real look-alike has the same 16 separate supports | as stated |
| binding, new | PR1020 code on its decoder: (6,9,…,9) = 69. On PR1624's witness: (6,8,…,8) = 62. PR1020's root indexing, pairing and puncture equal the spec's. This checker on PR1020's decoder: 69. | 69, 62 |

Seven controls must reject: a wrong dual scale; the §10 real look-alike,
whose separate supports are checked equal to the complex example's; dropping
the unit label; restoring line 0, which raises the designated pair above 6; a
wrong annihilator fed through the table comparison; a 61 undercharge claim fed
through the charge comparison; and a dependent seven-set.

PR1624 left the 256 classes unexpanded ("not 256 full entrywise complex
replays"). Here all 256 are expanded. Its branch-67 witness came from its own
certificate; the one here was built separately.

## Written audit of the argument

**§3 normal form.** `D T^T = 2RR^T` has rank 8, and D has eight columns.
`col(DT^T) ⊆ col(D)`, so `col(D) = col(RR^T) = col(R)`, and likewise for T.
R is injective (it has a nonzero 8×8 minor), so `D = RA` and `T = RB` with A
and B unique and invertible. Then `R(AB^T − 2I)R^T = 0`. R is injective and
`R^T` is surjective, so `AB^T = 2I`, hence `B = 2A^{-T}` and `A^T B = 2I`.
Columnwise this says `a_j·b_k = 2δ_jk`. Every step uses only ordinary
transposes and holds over C. The cost model is the same as PR1020's: the
identity entries are `dot(v_i, v_j)/2 = 2 r_i·r_j`, and the per-term charge is
the F2 rank of N on the actual supports. The binding stage executes this.

**§4 reduction.** `lambda` annihilates `W(z)` exactly when every live `i`
with `lambda(ell_i) = 1` satisfies `r_i·z = 0`. So `d(z) ≤ 8` exactly when z
lies in some `ker Z_lambda`. Each `Z_lambda` is rational, so its complex
rank equals its rational rank. With the census (no rank ≤ 6), the set of
nonzero complex z with `d(z) ≤ 8` is the union of the 27 lines. This is
complete over C, not a sample.

**§2 bound (2.1).** N is the Gram matrix of the nondegenerate form beta in
the `ell` coordinates (checked on all 14,400 entries). So
`q(x, y) = rank(beta on W(x) × W(y)) ≥ d(x) + d(y) − 9`. When `d(x) = 9`,
`q(x, y) = d(y)`.

**§7 cases.** A residual `a_k` lies in `b^perp`, so the only reduced line it
can lie on is c. A residual `b_k` lies in `a^perp`, so it is either one of the
13 dimension-8 lines or has dimension 9. r0, the only dimension-7 line, is
excluded. Two cases:

- **Case I** (no `a_k` on c): each residual term costs `d(b_k) ≥ 8`. Total
  ≥ 6 + 56 = 62.
- **Case II** (`a_j` on c, at most one j because A is a basis): for k ≠ j,
  `b_k ⊥ c`, and none of the 13 lines is ⊥ c, so `d(b_k) = 9`. Also
  `d(a_k) = 9`. The j term has `d(a_j) = 8` and `d(b_j) ≥ 8`, so it costs at
  least 7. Total ≥ 6 + 54 + 7 = 67.

The case split is exhaustive. The bound holds for every complex coefficient
choice.

**§9 equality.** Cost 62 forces Case I with every `d(b_k) = 8`, so the seven
residual B columns lie on seven distinct lines among the 13. They must be
independent because B is invertible. Conversely, every independent seven-set
spans `a^perp` (dimension 7). Adjoining b is invertible because `a·b ≠ 0`. A
residual A column on c would force six chosen lines ⊥ c, which is impossible.
So every independent seven-set costs exactly 62. Paired rescaling makes the
classes rational. The count of 256 is verified both structurally and by
direct rank.

No missing implication was found. The theorem's own limits stand. It covers
one puncture and one ordered pair, with the first pair's scaling fixed. It
prices separate COPY charges only. There is no physical decoder, moment or
kappa.

## Independence and limits

- **Separately implemented from PR1624's checkers:** the verifier code, the rank and kernel routines,
  the expansion of all 256 classes, and the branch-67 witness.
- **Taken from PR1624:** the spec. That is the root generation rule, P,
  `J_label`, the minor rows, the designated pair, and the §5/§6/§8 tables and
  matrices, transcribed from proof.md into `verify.py` and compared.
- **Uses predecessor code on purpose:** the binding stage imports PR1020's
  `verify.py` and `explore.py`. These, and PR1020's certificate, are pinned
  live inputs in SOURCES.json.
- Author: one Claude session. A read-only OpenAI Codex review found no
  problem in the written mathematics or the main gates. It flagged two
  controls that were tautological, an unchecked support premise in the §10
  control, and an overbroad independence claim. All four are fixed. This is not human mathematical review, and not a
  proof-assistant proof.
- Not checked: PR1624's own certificate bytes, its 14 controls and its
  separate GPT-6 Pro review. None of these is needed for the theorem as
  written.

## Reproduce

```sh
python3.12 scripts/research_package.py --package research/paired26-independent-audit
python3.12 -B research/paired26-independent-audit/verify.py   # ~30 s, prints PASS_PAIRED26_INDEPENDENT_AUDIT
```

The verifier is stdlib only and works on Python 3.10 or later.

## Open next questions

1. **Does 62 depend on the chosen pair?** Does the minimum, or the 256-class
   structure, hold for the other cost-6 ordered pairs at this puncture, or at
   the other 26-line punctures of the PR1020 orbit? It matters because PR1624
   fixes one pair. First step: the kernel inventory here depends only on the
   live set, so rerun the §6 intersections for each cost-6 pair. Blocker:
   none, but this is outside an audit's scope.
2. **Can a 62/94 COPY ratio be used physically?** This is PR1624's own open
   question. The ratio is still worse than PR968's 56/104, and the result is
   copy-only. Blocker: no physical decoder interface is specified.

## Credit

The theorem, proof, witness and 256 classification are an664's and Andrey
Mas's, with GPT-6 Pro (PR1624). woklerx gave the puncture, the cost-six pair
and the 69 decoder (PR1020). The model comes from themilkman216 (PR968) and
DreamingOfClouds (PR717). The open question PR1624 answered is from Hanson Sun
/ bbMisk (PR1521). This audit was prepared in JosieElliston's donated Claude
Code session 15, with substantial AI assistance. Apache-2.0.
