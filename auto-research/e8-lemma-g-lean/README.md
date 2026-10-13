# Lemma G (entrance gauge) of PR #484: clean proof and Lean 4 formalisation

Lemma G is the entrance-gauge lemma of PR #484. It covers three steps:
* target-side compensation at nonzero frames;
* labelled targets;
* the centre scatter along a chain.

Its value is measurable. With no-bank hosting (#496/#500), the full gauge/kernel word reaches complex `b = 1.333854e-3`. The Lemma-G-free path (kernel79 only) reaches `1.310216e-3`, so Lemma G is worth +1.80% of `b`.

This package splits Lemma G into two parts:
* **an abstract lemma, proved in Lean 4** for every semiring (in particular every field), every module and every family of invertible label operators;
* **finitely many instance hypotheses on the emitted streams**, checked exhaustively by Python.

`PROOF.md` holds the clean statement and proof. Its §5 lists what changed relative to #484's §2.

## Proved in Lean (`LemmaG/`, Lean 4.21.0 + Mathlib v4.21.0, as `formal/lean` on main)

**Main theorem.** Here `K` is any semiring, `M` any `K`-module, and `T : Λ → M ≃ₗ[K] M` any label family:

```lean
theorem LemmaG.Stream.conj_matrix (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (r : ι) :
    physRun rec es h r = T (labRun es l r) (∑ s, S es r s • (T (l s)).symm (h s))
```

In words: if a stream of relabel/add/scale/copy/clear events is well labelled and every relabel executes `T_B T_A⁻¹`, then for every input,

`h_r(final) = T_{λ¹_r}(Σ_s S_rs T_{λ⁰_s}⁻¹ h_s)`,

where `S` is the matrix of the scalar shadow. This is #425's conjugation lemma with all of its hypotheses explicit, together with the step from the rational replay to the action on the module.

| theorem | content |
| --- | --- |
| `Stream.conj`, `Stream.conj'` | operator form: physical run = `D(λ¹) ∘ scalar shadow ∘ D(λ⁰)⁻¹` |
| `Stream.conj_matrix`, `Stream.S_rowform` | matrix form. `S` is exactly what #484's `lg_lib.scalar_replay` computes: one symbolic replay, row form |
| `Stream.row_unit`, `Stream.row_pair` | the rows of the word: unit rows (helpers, so the entering-helper block is `T_{λ¹}T_{λ⁰}⁻¹`) and paired rows (targets forward, sources backward) |
| `emit_spec`, `emit_wellLabelled` | the schedule emitter is well labelled as soon as partners stay at their frames; no order condition is needed for exactness |
| `comp_segment`, `comp_segment_frames` | compensation segment. Under (b) and the rank order, every climb is a strict nested ascent and each target ends at `L_t = max ℰ_t`. Stated for an abstract order with strictly monotone rank, and for the subspaces of F₂⁹ |
| `centre_forward`, `centre_backward` | centre phase. Under (c), every step is a strict nested descent (forward) or ascent (backward) |
| `paid_telescopes` | accounting: paid ranks telescope to `rk λ¹ − rk λ⁰` |
| `Stream.labRun_untouched`, `Stream.wellLabelled_append` | frame and junction lemmas (Claim 3) |
| `Dbit_one_mul`, `Dbit_conj` | bit-side transfer of the entrance step: `D_I D_P = D_{I−P}` and `diag(g,g)ᵀ D_P diag(g,g) = D_{gᵀPg}` for `gᵀg = 1`, for every `P`. Not used by the complex word |

Every theorem is general. No instance data is enumerated in Lean, and `decide` and `native_decide` are not used. `#print axioms` gives a subset of `[propext, Classical.choice, Quot.sound]` for every theorem above (`PrintAxioms.lean`).

## Checked in Python (the instance hypotheses, PROOF.md §4)

| | hypothesis | check |
| --- | --- | --- |
| H1 | the emitted stream is well labelled (extended labels: tag × frame) | frames: #484 `code/lemmaG/lg_lib.check_labels` (G0, G2, G3). Tags: `code/check_extended_labels.py` (new; 3 adapter mutants rejected on every word, 2 wrapper mutants on the wrapper words) |
| H2 | every climb and centre step executes `T_b T_a⁻¹`; each source and target has exactly one non-identity adapter and every other adapter is the identity, at frame 0 or FULL | #484 `lg_instances` I-tr, on all 512 basis columns of every used transition (recipes are circuits of linear primitives, so 512 columns determine them; not run on the anchor). Adapter bridge: `code/check_extended_labels.py` |
| H3 | `S = (x,s,y) ↦ (x,s,y+x)` forward, `(x−y,s,y)` backward | #484 `lg_lib.scalar_replay`, exact, all 800 columns |
| H4 | endpoint labels as in W | #484 G4 |
| H5 | accounting (nested ascents, strict centre chains, mass) | #484 G2, G3, ACC |
| H6 | #433's data-adapter identities (`T_p⁻¹M_i = C_q⁻¹`, `T_FULL T_p⁻¹M_i = F C_q⁻¹`, `N_t⁻¹T_final = F C_q⁻¹`) | `code/check_adapters.py` (new), every port, all 512 columns, exact |

On all four words (anchor, kernel79, gauge80, headline), H1, H3, H4, H5 and H6 hold in both orientations, with 0 violations and 0 failures; H2 (I-tr) holds on the three gauge/kernel words, 2945/2945 on the headline. Together with Lemma A (#484 I-helper), the Lean theorem then gives the end-to-end identity of the complete emitted program **for every input with empty private registers**. #484's `lg_e2e.py` tests that identity on 814 sampled columns; here it follows from the exhaustive checks.

## Trust base

* **Lean kernel** (4.21.0), **Mathlib** v4.21.0 (`lake-manifest.json` pins rev `308445d`, the same as `formal/lean` on main), and the axioms `propext`, `Classical.choice`, `Quot.sound`.
* **The Python instance checks**, as listed above, including the reading of the emitted JSON events as Lean `Event`s (PROOF.md §4, "Extended labels").
* **Inherited interfaces outside Lemma G:**
  * #433's data-adapter endpoint: its three identities are now checked exhaustively (H6);
  * Lemma A, which turns `L_E⁻¹ Φ_E R_E⁻¹` into `C_[w] ⊗ I` (#484 I-helper, exhaustive);
  * #442's accounting model: a nested climb `A ⊆ B` is charged `|B| − |A|`.

## Run

```sh
python3 research/e8-lemma-g-lean/verify.py                                       # Lean: manifest, source scan, cache get, build, axioms
python3 research/e8-lemma-g-lean/verify.py --instances /abs/out/of/484/verify    # also the instance checks (numpy)
```

* Requirements: elan on `PATH` (`lean-toolchain` pins `leanprover/lean4:v4.21.0`), network access for `lake exe cache get`, and Python 3.9+ (with numpy for `--instances`, as #484's stage).
* A cold run downloads Mathlib's prebuilt cache, then builds this package's five modules in about a minute.
* `--instances` needs the output directory of #484's `verify.py`, which takes about 25 minutes. It checks every word present: the headline and the anchor, plus gauge80 and kernel79 when #484 ran with `--all`. For each word it confirms that #484's own checks passed on inputs equal to #484's `EXPECTED.json`, then runs H1 (tags) and H6. The #484 files it imports or compares against are pinned in `MANIFEST.json` (`external_files`).

## Files

| path | content |
| --- | --- |
| `LemmaG/Stream.lean` | events, semantics, Theorem 1, the matrix form, Corollary 2 |
| `LemmaG/Schedule.lean` | emitter, compensation segment, centre phase, telescoping (Theorems 3 and 4) |
| `LemmaG/Frames.lean` | the frames of F₂⁹ satisfy the order hypotheses |
| `LemmaG/BitEntrance.lean` | the bit-side identities |
| `PrintAxioms.lean` | the axiom probe |
| `code/check_extended_labels.py` | instance check H1: tags and the adapter/wrapper bridge, with mutants |
| `code/check_adapters.py` | instance check H6: #433's data-adapter identities |
| `verify.py`, `MANIFEST.json` | the check script and the sha256 of every file |

## Credits

* The conjugation lemma and scalar interface: #425 (Zhihao Chen).
* The one-helper rule and paid wrappers: #458 (chafreaky).
* The virtual entrance and complete-invocation normalisation: #471 (Dugongue).
* The gauge construction, Lemma G and its Python stage: #484 (DreamingOfClouds).
* Lean conventions: the toolchain and Mathlib pin of `formal/lean` on main; the standalone package layout, axiom reporting and author-check practice of #487/#488 (jamesyc).
