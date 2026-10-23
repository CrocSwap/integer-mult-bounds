# [Lean] Selected normalized-cost bound from explicit physical suppliers

Local publication preparation. The target is independently kernel-accepted;
this relocated public reproduction has not been compiled or published.

## Author-checked scope

For the exact selected context κ = 836330098538459/500000000000000000
= 0.001672660197076918, this Lean theorem derives a finite uniform A and
cost(x) ≤ A n^(1−κ) volume(x) from the explicitly quantified complete
state/domain, positive volume, uniform base-family/local-work and exact
selected child suppliers. It supplies no unconditional operational construction
or full integer-multiplication bit-cost theorem. AUTHOR_CHECK.json records the
source author's approval of this exact wording and value.

The native endpoint bCurrent = 67018507072324140917/40000000000000000000000
is distinct from κ. The checked bridge proves the positive gap and weakens the
native power bound in the required direction for positive integer width.

The final theorem derives the genuine envelope recurrence and finite A
internally; neither a scalar recurrence nor native_bound is its premise.
Callers must provide complete actual-cost semantics, a nonempty admitted family
at each positive width, positive natural volumes, uniform bounds over entire
base families, one full non-child cost constant over the admitted precision and
state family, and the complete selected child decomposition. Child volumes are
exactly parent/14336 as real numbers; this imposes genuine divisibility and
positive-volume obligations for natural volumes. All physical operational,
precision, all-size multiplication and bit-cost transfers remain explicit.

## Smallest source-complete package

Eight included exact accepted Lean files total 55,714 bytes. Eight unchanged
prerequisites total 213,305 bytes and come from public fork commit
73ff839084f8c2761dc4213a2fd9e63a295dd8fb. The complete research closure is
16 modules / 269,019 source bytes. SOURCE_MANIFEST.json specifies every source
SHA256, Git blob, immutable provenance, ordered direct imports and reference
object identity. No import line or mathematical source is changed. The
materializer flattens exact bytes to their existing module filenames, so no
private worktree paths are needed by the resulting source layout.

The old source headers still describe their preparation-time uncompiled
status. They are retained as historical source bytes; the accepted receipt and
subsequent ledger determine current verification status.

## Source reconstruction

These are reproduction instructions, not a record that the network commands
were run for this package. Use a fresh workspace and Python3, Git, official
Lean4.21.0. With PACKAGE pointing to this directory:

```sh
(cd "$PACKAGE" && sha256sum -c SHA256SUMS)
git init public-inputs
git -C public-inputs remote add origin https://github.com/jamesyc/integer-mult-bounds.git
git -C public-inputs fetch --depth=1 origin 73ff839084f8c2761dc4213a2fd9e63a295dd8fb
python3 "$PACKAGE/materialize_sources.py" --public-repo public-inputs --output sources
```

The script itself performs no network operation, installation or compilation.
It reads all input bytes and validates their lengths, SHA256s and Git blob IDs
before creating a fresh output directory. It refuses any existing output and
never rewrites an accepted file. SOURCE_RECONSTRUCTION.json records the local
content-addressed snapshot test against every accepted hash; a fresh public
network fetch remains a separate future check.

## Pinned runtime and ordered reproduction

Use official Lean4.21.0. The accepted Linux x86-64 lean binary SHA256 is
cbf5fd536e142ef1beaccf33f788fd8a7f3f29fb214e75c11319a8d8677b4b2b.
Use Mathlib at 308445d7985027f538e281e18df29ca16ede2ba3 and its unchanged
lake-manifest.json SHA256
5143be8727ac4a7424b7b2dee862051ed9bd372ab103b495736a46239bd9a3c9.
The manifest pins Batteries8d2067bf518731a70a255d4a61b5c103922c772e and
all other packages. Do not update package revisions or mix another Lean ABI.
Official setup commands, when installation is authorized, are:

```sh
git clone https://github.com/leanprover-community/mathlib4.git mathlib4
git -C mathlib4 checkout --detach 308445d7985027f538e281e18df29ca16ede2ba3
(cd mathlib4 && lake exe cache get)
```

Resolve absolute LEAN_PREFIX, MATHLIB, SOURCE_DIR and a fresh OBJECT_DIR.
LEAN_PREFIX is the extracted official Lean root, MATHLIB the pinned checkout,
SOURCE_DIR the materialized sources. Preserve the exact package source heads.
Set LEAN_PATH in this first-match order:

1. OBJECT_DIR
2. MATHLIB/.lake/packages/Cli/.lake/build/lib/lean
3. MATHLIB/.lake/packages/batteries/.lake/build/lib/lean
4. MATHLIB/.lake/packages/Qq/.lake/build/lib/lean
5. MATHLIB/.lake/packages/aesop/.lake/build/lib/lean
6. MATHLIB/.lake/packages/proofwidgets/.lake/build/lib/lean
7. MATHLIB/.lake/packages/importGraph/.lake/build/lib/lean
8. MATHLIB/.lake/packages/LeanSearchClient/.lake/build/lib/lean
9. MATHLIB/.lake/packages/plausible/.lake/build/lib/lean
10. MATHLIB/.lake/build/lib/lean
11. LEAN_PREFIX/lib/lean

Compile serially in SOURCE_MANIFEST.json module order, from SOURCE_DIR, using
LEAN_NUM_THREADS=1 and the following command shape for each module:

```sh
"$LEAN_PREFIX/bin/lean" -j1 -o "$OBJECT_DIR/$MODULE.olean" "$MODULE.lean"
```

The order is topological and contains all16 exact research modules. Use fresh
output/log files and bounded supervision. The accepted final-root run used
60seconds/4GiB, one thread and an8GiB disk floor; the historical dependencies
have their own retained acceptance limits. This package does not claim that a
new public full-closure run meets a single aggregate time budget. Stop on a
nonzero compiler exit or resource limit; preserve all diagnostics and do not
blindly retry. Capture complete stdout/stderr and the existing axiom probes.
Inherited warnings must be checked against their exact accepted receipts,
with only justified source-path substitutions, rather than deleted or ignored.
No compiler was invoked while assembling this package.

The final two declarations are selected_child_descent and
selected_cost_bound_from_physical_suppliers. Their accepted output has exactly
two probes using only propext, Classical.choice and Quot.sound, no warnings.
The final source is1445894f and object isf9fd9436; full hashes are in the manifest
and ACCEPTED_TERMINAL_REVIEW.json. Object identity across a newly relocated
build is evidence to inspect, never assumed from source identity alone.

## Publication boundary

Candidate-specific source checks, public compiler replay, final current-main
applicability/base/head/body lease and new candidate CI remain unperformed.
Existing fork CI applies only to its old candidate. The prior PR-create403
access denial is unresolved. No PR, branch push or permission change is
included in this preparation. The earlier XOR and three-root Hosting packages
remain separate; this package has one conditional-cost scope.
