# Independent phase-exact check of the selected frontier1094 word's Clifford recipes

**Independent verification: no new κ, and no existing check is changed.**

- Track: 75–84 (independent verification), assignment seed 76, drawn with the OS CSPRNG via Python `secrets`.
- Card: `independent-moment`, with the scope **refined** in [TASK.json](TASK.json). The scope is one selected assembly premise, checked by a genuinely independent exact implementation.
- Base: `0b1cccf8`. The selected record frontier1094 is unchanged.

## The claim checked

Lemma G's `RecipesExact` premise (`research/e8-lemma-g-lean/LemmaG/Stream.lean:110-112`) says that every relabel `A → B` of the stream executes `T_B ∘ T_A⁻¹`, where `T_F` is the canonical frame operator of frame `F`. Every climb that the selected complex profile prices as a rank-r child relies on it: the stored recipe `L ∘ (C_[r] ⊗ I) ∘ R` must implement `T_new ∘ T_old⁻¹` exactly.

For the selected word, this package checks every stored record on all 512 columns of ℂ^(2^9), global phase included:

- **2,896 child recipes.** Each satisfies `L ∘ F_r ∘ R ∘ T_old = T_new`. This is the same as `L F_r R = T_new T_old⁻¹`, because `T_old` is invertible.
- **224 endpoint adapters.** Each satisfies its defining identity, which is Lemma G's H6:
  - source: `M ∘ C_q = T_start`;
  - target: `M ∘ F_9 ∘ C_q⁻¹ = T_final`.

**Result: all 2,896 children and all 224 adapters are exact** (`PASS_FRONTIER1094_RECIPES_EXACT`).

### What was checked before, and what is new

- **The producer's own check is complete, but not independent.** `phases_full.py`/`lower_child` (icekylinx) asserts two things for each recipe: equality of the signed Z4 Pauli tableau, and of column 0. Together these pin the Clifford operator exactly, global phase included. But that check ran in the producer's own code, on in-memory operators, at generation time.
- **The Lemma G package's checkers ran on other words.** `e8-lemma-g-lean` (DreamingOfClouds) ran producer-independent, all-512-column checks of these premises on four other words: #484's `lg_instances` I-tr for H2, and `code/check_adapters.py` for #433's data-adapter identities (H6). It did not run them on the selected gauge44 word.
- **Seed80** (`research/complex-frame-distance-seed80`, woklerx) checks the ranks of the same 1,004 frames and 2,896 edges, and makes no phase claim.
- **Our #1262** rebuilt the selected rank ledger independently, without phases.

**What is new.** For the **selected** word, the stored, byte-bound `CLIFFORD-RECIPES.json` is now re-decoded and checked against `T_B T_A⁻¹` and H6. The check uses a kernel written from scratch and calibrated against the Lean literals and published digests. It is a second, independent implementation of a check the producer already passed, not the closing of a known gap.

## Binding ([verify.py](verify.py) `load`, checks B1–B12)

- **The archive.** The selected record and the frontier1094 certificate `ASSEMBLY.json` (1122cb3a…) bind the capsule `selected-replay.tar.gz` (f1da8061…), which batch1099's integration record pins.
- **Exact bytes only.** The checker parses exactly the bytes it hashed. Members are resolved by full path under `candidate/strict/`, never by basename.
- **The certificate chain.** The certificate gives the template (9c4c5142…) and the owner audit (30bafff0…). The owner audit's `source_artifacts` give the raw digests of the gauge44 provider's four files:

  | File | Raw sha256 |
  |---|---|
  | `CANONICAL-WORD.json.gz` | 16bc0ebb… |
  | `CLIFFORD-RECIPES.json` | d0768f21… |
  | `CLIFFORD-REVIEW.json` | cb0e10a8… |
  | `LOCAL-PROGRAMS.json.gz` | 241fde27… |

- **The template.** Its gauge44 provider names the same recipes, word and programs, the same ports and centres, and (R, h, v) = (480, 9, 112).
- **SLOT-PINS-k8.** It is listed in the selected source manifest and pins the same recipes, programs and word.
- **Two digests for one word.** 16bc0ebb is the gz-byte digest; the word's payload digest is 4ddb29fb. Each comparison uses the right one.
- **The producer's review** is checked for consistency only, never used as evidence.
- **Canonical encodings** are checked.
- **The global8 twin** is byte-identical. This is informational and never read.
- **Decoys are rejected.** The `split-centres` recipe and word files share the gauge44 files' basenames, so a lookup by basename would pick them up; only the digest binding rejects them.

## Inventory (checks I1–I7)

- **Frames.** There are 1,004 independent row lists. Frame 0 is empty and frame 1 is the full frame.
- **Children.**
  - The 2,896 child records are exactly the word's directed edges, which include both centre directions, sorted.
  - Ranks: 1928 at rank 1, 380 at rank 2, 408 at rank 3, 124 at rank 4, 40 at rank 5 and 16 at rank 8.
  - All spans are nested. The only descending records are the 8 centre reversals `(f, 0)`.
- **Relabel coverage.** The climb and centre events of **both** emitted orientations (3,486 climbs and 8 centres each) name exactly these 2,896 keys, with matching ranks. So every climb and centre relabel of the programs has exactly one record.
- **Adapters.**
  - The 224 endpoint adapters are ordered (port, source/target).
  - Each adapter's `q` is the word's port mask, of weight 3 or 7.
  - Source frames are `[q]`; target frames have dimension 8.
  - The program's adapter events point to the same frames.
- **Monomials.** All 6,016 monomial records are well formed: fields, ranges, symmetric `Q`, diagonal parity and an invertible `G`.

## Operator semantics ([clifford.py](clifford.py), written from scratch)

The kernel imports only the standard library. It was written from the specification:
- the gate definitions of `HyperplaneEnd/Clifford.lean` and `Exact.lean`;
- the producer's code, read only as a specification and never imported.

**Conventions.**
- Bit i of a basis index is axis i.
- F2 matrices are lists of row bitmasks.
- A circuit is a gate list; the first gate is applied first.

**Gates.**
- `P(G)` maps |x⟩ ↦ |Gx⟩.
- `X(b)` maps |x⟩ ↦ |x⊕b⟩.
- `D(Q, α)` maps |x⟩ ↦ i^{Σα_i x_i + 2Σ_{i<j} Q_ij x_i x_j} |x⟩.
- `PH(p)` multiplies by i^p.
- `C(q, ±1)` maps v ↦ ((1 ± i)v + (1 ∓ i)v∘(⊕q))/2. So `C(q, +1)` = √(X^q).

**Derived operators.**
- `F_r` is `C(e_i, +1)` on axes 0..r−1.
- A monomial record is `D(Q, α)`, then `P(G)`, then `X(offset)`, then `PH(phase)`.
- `T_U = K⁻¹ F_r K` with `K = [P(G), D(Q, α)]`. Here G's columns extend the frame's rows to a basis, and `Q = I + G⁻ᵀG⁻¹`. The rows are used exactly as stored.

## Exact evaluation

**How each identity is run.** Each side is run on the packed identity: row y holds Σ_x N[y,x]·2^{βx}. The real and imaginary parts are exact Python integers, and N is 2^k times the operator matrix after k C gates. There is no masking or carry. The two sides are scaled to a common 2^K and compared row by row. There is no normalisation and no projective freedom, so global phase is included.

**Why the packed comparison is sound** (β = 2K + 2, Lean's `check` radix):
- P, X, D and PH only permute or negate components. A C gate at most quadruples the largest component. So after scaling, every digit of either side is at most 4^K in absolute value.
- A digit difference d therefore satisfies |d| ≤ 2·4^K < 2^β.
- A signed-digit expansion Σ d_x 2^{βx} with |d_x| < 2^β is zero only if every d_x is zero.
- So packed equality implies entrywise equality on all 512 columns. Because both sides are ℂ-linear, it implies operator equality.

The comparator refuses to run if β < 2K + 2 (control K3).

## Calibration against independent published values (FX1–FX7)

Before any record is judged, the kernel must reproduce:

1. **The Lean literals** of `HyperplaneEnd/Exact.lean` (pinned by sha256):
   - for the three certified (E, U) pairs, `canon(E)`, `canon(U)`, `L.gates` and `R.gates` equal the literal gate lists `fE/fU/wL/wR`, including every inverse matrix;
   - the three rank-7 identities hold.
2. **#1415's three operator digests** of `T_U ∘ T_E⁻¹` (in `hpe-lean-semantic-binding/RESULT.json`). These exercise the adjoint.
3. **#702's 14 frame-kernel digests** (in `cold-wrapper-amplitude-audit/EXPECTED.json`). All 14 are frames of this word: 37, 66, …, 414.
4. **Hand values and structure:**
   - hand values for `T([30])`;
   - the shortcuts for frames 0 and 1 agree with the general construction;
   - reordering a frame's rows leaves T unchanged, while a different basis of the same span changes it.

## Results ([RESULT.json](RESULT.json))

| | Count | Columns | Global phase | K (C gates per identity) |
|---|---|---|---|---|
| Children | 2,896 / 2,896 exact | 512 | included | K=1: 120, K=2: 400, K=3: 480, K=4: 254, K=5: 64, K=6: 432, K=7: 416, K=8: 476, K=9: 246, K=16: 8 |
| Endpoint adapters | 224 / 224 exact | 512 | included | 1 (source), 10 (target) |

The full run takes about 33 s of CPU on one core, including calibration and controls. Receipts can be written with `--receipts PATH`: a hash-chained JSONL file with one line per new-frame group and per adapter. `--subset` runs a partial check and refuses `--write`.

## Controls

- **Semantic mutations** (`verify.semantic_controls`, recorded in RESULT.json).
  - Each mutation is rejected on every sample record it applies to. The samples are the children (0,2), (0,174), (37,1), (0,415) and (415,0), and adapters 0 and 1.
  - Record mutations:
    - a global phase change of +1;
    - an input-character change (`linear_Z4 += 2`, invisible to column 0);
    - a CZ cross term in Q;
    - a translation of the offset.
  - Reading mutations:
    - swapping L and R;
    - reversing the direction;
    - monomial gate order (children only; see the note below);
    - the sign of F_r or C_q;
    - reading C_[r] as one gate;
    - the adapter's port mask;
    - the adapter's role.
  - Frame basis: the same span with a different basis is rejected, and the same rows reordered pass (a positive control).
  - Note on gate order: for **every** endpoint adapter, `q(Gx) = q(x)`. Evaluating D after P is therefore the same operator on all 224 adapters; `verify.py` counts this and records it in RESULT.json. So that mutation is not a control for adapters. The gate order is pinned instead by the children controls and by FX1's comparison with the Lean `Mono.gates` literals.
- **Comparator controls** (tests K1–K3). These are checks on this package's own comparator, not claims about the producer's check:
  - A projective comparator would accept the global-phase mutant, which equals the true side times i.
  - A column-0-only comparator would accept the input-character mutant on (0,2).
  - An unsound radix raises an error. The digit bound is also measured on the 16-gate centre children, and a constructed collision shows that β = 2K would be unsound.
- **More controls** in [test_package.py](test_package.py) (26 tests):
  - a rank off by one is rejected, both by the inventory check and by the evaluator;
  - swapped matrix rows are rejected;
  - an adapter phase change is rejected;
  - in every rank class, the true record passes and its phase mutant is rejected;
  - the decoy recipes and decoy word, one phase digit changed in the recipe bytes, a duplicate JSON key, a flipped archive byte and unsafe archive members are all rejected;
  - imports are restricted to the standard library;
  - a mutated child record and a mutated adapter record passed through `evaluate()` are both rejected, and the receipts list each selected pair exactly once;
  - a dropped climb event (I5), a moved adapter frame (I6), an asymmetric Q (I7) and a wrong fixture pin (FX3) are all rejected.

## What this does not show

- **The executor bridge.** The emitted or hosted program applying these records with exactly these semantics, i.e. Lean's arbitrary `rec(A, B)` being the record's circuit operator, is H1 and `check_extended_labels`. It is not checked here.
- **Residual wrappers and identity adapters.** The 36 residual wrapper recipes (`RESIDUAL-ADAPTERS.json`) and their 480 residual events per orientation, which feed Lemma A, are not checked. Neither are the 866 identity adapters per orientation:
  - 352 entries at frame 0 (240 helper + 112 target);
  - 514 exits at FULL (402 helper + 112 source).

  So this is a record-level check of `CLIFFORD-RECIPES.json`, not of every relabel in the stream.
- **Other hypotheses.** Scalar events, hosting and charts (#1255), WellLabelled/hS, the compiler and precision are inherited, unchanged.
- **For the adapters,** Lemma G treats RecipesExact as definitional under its extended labels, so the substantive statement checked is H6.
- **No Lean proof** of this instance, and **no new κ**.
- **The binding** is to the selected capsule's `global/` provider. Only `certificates/selected-result.json` or `certificates/checkpoints/frontier1094.json` may name the certificate.

## Reproduce

```sh
python3 -I -B research/frontier1094-recipes-exact-seed76/verify.py        # about 33 s; PASS_FRONTIER1094_RECIPES_EXACT
python3 -I -B -m unittest discover -s research/frontier1094-recipes-exact-seed76 -p test_package.py
python3 -I -B research/frontier1094-recipes-exact-seed76/verify.py --subset 'dim=1..2,ports=0-3'   # partial
python3 scripts/research_package.py --package research/frontier1094-recipes-exact-seed76 --check-only
python3.12 scripts/research_package.py --package research/frontier1094-recipes-exact-seed76
```

Standard-library Python 3.10 or later. It was run on Python 3.12.15 and 3.14.8 (macOS 26.5, arm64).

## Open next questions

1. **Does the emitted executor apply these records with exactly these semantics?** This is the bridge `rec(A, B)` = the record's circuit operator.
   - First step: replay the forward orientation's first 100 climb events through an independent statevector executor of the emitted program format, and compare the results with the record operators.
   - Blocked by: an independent executor for that format.
2. **Are the 36 residual wrapper recipes and their 480 residual events per orientation exact?** They are the remaining non-identity recipes of the selected word, and they feed Lemma A.
   - First step: bind `RESIDUAL-ADAPTERS.json` through the owner audit and reuse `clifford.py` on it. The Lean pairs `2:999` and `3:998` are already among them.
3. **Can the per-record packed checks be kernel-checked by Lean's `Clifford.check` for this instance?** The radix rule here is the Lean check's, so a kernel-checked version would turn this replay into a formal result for the instance.
   - First step: emit one rank class as Lean `check` terms and time `lake build`.
   - Blocked by: a Lean toolchain, which is not installed here.

## Relation to earlier work and credit

- **The Lemma G package** `e8-lemma-g-lean` (DreamingOfClouds, #509 from #484): it states `RecipesExact` and H6. Its I-tr and `check_adapters.py` checked them exhaustively on four other words. #433 (icekylinx) is the source of the data-adapter identities.
- **`HyperplaneEnd/Clifford.lean` and `Exact.lean`** (jeremykothe2, #593): the gate semantics, the literal pairs and the packed check with its radix 4^(K+1), which is β = 2K + 2. These follow DreamingOfClouds' `adapters_local.py` and the PR #458 wrapper lineage (chafreaky), and were integrated by Douglas R. Colkitt.
- **The producer:** `phases_full.py` and `clifford_exact.py` (icekylinx), adapting the exact phase lowering of PR425 (jacklightChen).
- **Seed80** (woklerx): frame ranks with no phase claim. This package adds the phases on the same edges.
- **#1262** (ours): the independent rank ledger of the same capsule. Its binding pattern is reused by copying, not importing.
- **#1415** (commdata2338) and **#702** (BigCactusLabs): their digests calibrate this kernel. Also related: **#712** (jsnider3).
- **Open #1697** (navinor): the 511 cold hyperplane operators, with phase. That is a different object.
- **Open #581** (jamesyc): one historical child, proved in Lean.
- **Re-runs of the producer's own checks:**
  - open #1646 (JosieElliston), on the #1029 (aliromman) and #662 (cbethin) engines;
  - `selected-replay-fastpath`.

  These re-execute `lower_child`'s complete tableau and column-0 assertions while reproducing the recipe bytes. That is a semantic check, but not an independent one. Our #1041 is a parallel driver; it reproduced `d0768f21` only within #1646's runs.
- **#1092** (ToikY): Clifford state reuse.
- **#1255** (bitplane): the residual-chart phase criterion.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via Claude Code. Parallel read-only scout and judge subagents selected the question. Reader subagents extracted the specification from the Lean files, the capsule and the producer code (read as specification only), and the kernel and verifier were then written fresh. No claim was posted to Discussions. New material is Apache-2.0.
