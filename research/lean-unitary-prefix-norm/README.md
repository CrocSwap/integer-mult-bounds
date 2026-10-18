# Formal unitary prefix bounds on the existing Lemma G semantics

This package proves the quantified norm implication requested by
[PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282), directly on
the existing `LemmaG.Stream.Event`, `physRun`, `S`, `RecipesExact` and
`WellLabelled`. It adds **13 core Lean theorems and 20 example theorems**,
including partial real/imaginary stores and exact witnesses showing why the
hypotheses matter. It imports the credited conjugation theorem without
introducing a replacement event model.

This is a scoped formal proof. Instantiating its hypotheses for the selected
PR1094 compiler and finite row certificate remains open. The selected bound
and production precision charge are unchanged.

## Exact statements and boundary

For any finite register type, normed field `K`, normed `K`-space `M`, finite
event word `es`, initial labels `l`, and initial values `x`, assume:

1. Every label map `T a : M ≃ₗ[K] M` preserves the norm.
2. Every relabel executes exactly `T b ∘ (T a)⁻¹` (`RecipesExact`).
3. The word satisfies the imported `WellLabelled` predicate, including matching
   source/destination frames for ADD (`Event.Admissible`).
4. `‖x j‖ ≤ budget j` for every initial register.

Then `PrefixNorm.weighted_prefix` proves, for **every natural prefix length**
`k` and register `r`,

\[
 \|\operatorname{physRun}(\mathrm{rec},\mathrm{es.take}\ k,x)_r\|
 \leq \sum_j \|S(\mathrm{es.take}\ k)_{rj}\|\,\mathrm{budget}_j.
\]

The entries of `S` are the exact scalar shadow after cancellation. Admissibility
and recipe exactness are proved to pass to prefixes. The proof uses the original
`Stream.conj_matrix`, norm preservation of inverse label maps, and the triangle
inequality. Prefix lengths beyond the word length are also covered.

`supported_prefix` restricts the sum to active initial inputs of norm at most
`B`, with every other initial register zero. Arbitrary bounded dirty inputs
belong in the active set. `supported_certificate` takes the all-prefix row
bound `L` as an **explicit hypothesis** and gives the uniform bound `L * B`
for nonnegative `B`.

For finite Euclidean vectors, `splice_sq` proves that any mixture of old and
new whole coordinates has squared norm at most `‖old‖² + ‖new‖²`. For complex
vectors, `components_sq` allows **independent real and imaginary write masks**
and proves the same inequality directly in the complex Euclidean norm.
Endpoints of norm at most `L ≥ 0` therefore give the squared bound `2 L²`;
the exact guard `2 L² < 2^(2 b)` implies a strict norm bound `2^b`.

These partial-store lemmas concern values made from the two specified
endpoints. They do not automatically bound coefficient-building scratch or
the internal instructions of a relabel recipe. Those states need their own
representation and endpoint bounds before applying these lemmas.

## Examples and hypothesis controls

All examples use the same imported event semantics and are proved in Lean.
See [THEOREMS.json](THEOREMS.json) for all 33 declarations.

| Example | Exact evidence |
| --- | --- |
| Valid two-register word with identity/negation labels | `good_prefix_bound` applies the new theorem at every prefix; an intermediate cancellation gives zero. |
| Mismatched ADD frames | Unitary exact recipes and a restored endpoint coexist with physical value `2` and scalar active-input coefficient `0` at an intermediate cut. `bad_not_labelled` proves the missing premise fails. |
| Incorrect reverse recipe | Every recipe preserves norms and the word is well labelled, but the reverse map is wrong. `wrong_recipe_not_exact` and `wrong_recipe_cut` prove the failure and the `2` versus `0` discrepancy. |
| Nonunitary labels | An exact, well-labelled relabel/inverse loop restores its input, but has physical value `8` against scalar coefficient `1` halfway through. |
| Partial complex store | Old value `3/5 + 4i/5` and new value `1` each have squared norm `1`; writing the real component first gives squared norm `41/25`. |

The verifier changes `2 L²` to `L²` in `components_uniform` in a disposable
file and requires a Lean proof failure at that inequality. This is a meaningful
failure control, not a completeness claim about proof tactics.

`forward_bits_if` and `backward_bits_if` prove only the **conditional**
arithmetic implications from endpoint bounds `131088` and `1154896` to
component-store bounds `2^18` and `2^21`. Lean does not establish those endpoint
premises for PR1094 here. Their numerical origin is PR1282 at
`851e5232f7c9e105fb6e8f3a7be7a070e7524012`.

## Reproduce and trust boundary

From the repository root, with Python 3.12+ and elan/Lake on `PATH`:

```sh
python3 -I -B research/lean-unitary-prefix-norm/verify.py --work /tmp/unitary-prefix-norm
```

The command pins Lean **4.21.0**, Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3` and the complete inherited
nine-package resolution in [lake-manifest.json](lake-manifest.json). It fetches
the required Mathlib cache, copies `LemmaG/Stream.lean` byte-for-byte from its
pinned source into a dedicated directory, then freshly compiles `LemmaG.Stream`,
`PrefixNorm` and `PrefixNorm.Examples`. Dependency commits and clean tracked
sources are checked before and after the build. Cached dependencies are reused;
the package's own compiled files are removed before each build.

Expected output:
`PASS_LEAN_UNITARY_PREFIX_NORM core=13 examples=20 axioms=33 semantic_mutation=rejected`.
The directory retains `TOOLCHAIN.log`, `BUILD.log`, `AXIOMS.log`, `CONTROL.log`
and `RECEIPT.json`.
Use a new empty directory or one created by this verifier. `--no-cache` uses
already prepared dependencies; `--packages PATH` explicitly shares an existing
`.lake/packages` directory into a new workspace. The frozen predecessor
directory is never used as a build directory or edited.

All 33 theorem axiom reports must match [AXIOMS.json](AXIOMS.json). Their union
is exactly `{propext, Classical.choice, Quot.sound}`; there is no `sorryAx` or
custom axiom. Acceptance relies on Lean's kernel, pinned Mathlib/dependency
libraries and those standard axioms. The source policy scan rejects placeholders
and external/native proof shortcuts as an additional guard; it is not a Lean
parser or substitute for compilation.

The generic registered hook runs **Python source/policy guards only**. Full
Lean verification has a dedicated
[workflow](../../.github/workflows/unitary-prefix-norm.yml).

```sh
python3 scripts/research_package.py --package research/lean-unitary-prefix-norm --check-only
python3.12 scripts/research_package.py --package research/lean-unitary-prefix-norm
python3 -I -B research/lean-unitary-prefix-norm/verify.py --source-only
python3 -I -B research/lean-unitary-prefix-norm/test_verifier.py
```

[VALIDATION.md](VALIDATION.md) records observed commands and unrun obligations.
[SOURCES.json](SOURCES.json) binds five live source inputs. The selected record
and task catalogue are historical provenance at base
`bdd4c63ac7c5d8a46ce070ba133df8d7ba9cb92c`. The generic metadata checker needs
full Git history; the direct source guard works on a minimal export.

## Task and overlap

Submitted as [PR1309](https://github.com/CrocSwap/integer-mult-bounds/pull/1309).

[TASK.json](TASK.json) records the independent-verification assignment,
OS nonce `0a4e57208d3517b8c57dc59d25be9445`, card `formal-interface-lemma`,
scope key `636f26dec98e26b296e8` and refinement to PR1282's formalization
follow-up. Coordination is in
[Discussion1291](https://github.com/CrocSwap/integer-mult-bounds/discussions/1291).
[OVERLAP.json](OVERLAP.json) gives fresh complete open-PR/Discussion coverage,
nearby heads and search limits. PR1282 supplies the written norm argument and
finite certificate; Lemma G supplies the formal conjugation theorem. This
package connects the two in Lean. HPE residual-identity and cleanup-reordering
formalizations address different statements. Search results do not prove novelty.

## Open next questions

1. **Bind a concrete emitted word and its row certificate to these theorems.**
   This would formally connect the quantified theorem to a supplier program.
   First encode one complete small word and prove that its imported `S` matches
   an independently replayed rational row table. The blocker is a checked
   translation of events, labels, recipes, coefficient scratch and every
   relevant cut; the selected PR1094 word is not encoded here.
2. **Connect partial stores to the full precision transfer.** This is needed
   before using a smaller production charge. First formalize the actual
   real/imaginary store schedule and establish its endpoint envelopes using
   `components_bits`. Native recipes, roundoff, hosting, physical compiler/tape
   accounting and all-size analytic transfer remain separate obligations.
   This package does not assert a new multiplication theorem.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance in proof,
code, validation and writing; no independent human review is claimed. New work
is Apache-2.0. PR1282 supplied the written norm argument and follow-up. Existing
source and license notices are retained unchanged.

The conjugation/scalar interface is credited to Zhihao Chen (PR425); the
one-helper rule and wrappers to chafreaky (PR458); virtual entrance and
normalization to Dugongue (PR471); the gauge construction, Lemma G and Python
stage to DreamingOfClouds (PR484). This relies on the existing
`research/e8-lemma-g-lean` formalization and Mathlib, with the Lean conventions
of jamesyc's PR487/488. The selected-construction lineage remains credited in
PR1282 and the selected review. The underlying conjugation theorem and norm
argument are not claimed as new discoveries here.
