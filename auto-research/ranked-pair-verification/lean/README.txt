Ranked-pair Lean verification

Run from the repository root:

  (cd formal/lean && lake exe cache get)
  python3 research/ranked-pair-verification/lean/check.py

The five files use the existing formal/lean project, pinned to Lean 4.21.0
and Mathlib 308445d7985027f538e281e18df29ca16ede2ba3 (v4.21.0). No separate
Lake project or toolchain is required. The checker can run from any directory;
--lake-project PATH selects another checkout of the same pinned environment.

check.py verifies the five source SHA256s, all 45 theorem declarations and
#print axioms coverage, dependency pins, and actual compiler version. It
recompiles every source and rejects missing, duplicate or unexpected theorem
rows and dependencies outside propext, Classical.choice and Quot.sound.
Logs and a fresh axiom audit go under build/ranked-pair-formal/ (ignored).
The checked-in verified-axioms.json is the completed research audit receipt;
theorem-manifest.json records the exact sources and expected theorem names.
Use --check-sources-only for a quick manifest/pin check without compilation.

Proof scope

DirtyWrapper.lean proves arbitrary dirty-workspace restoration, literal XOR
word inversion/linearity, and uniform address-reindexing commutation.
RoundedRecurrence.lean proves all-width rounded recurrence bounds and the
exact real characteristic identity, with the physical recurrence and real
characteristic inequality as explicit hypotheses. BalancedCeiling.lean proves
the two-margin assembly ceiling. ConcreteAssembly.lean derives and proves the
47 rational assembly inequalities. CappedMass.lean proves finite concave
profile comparison, checks both signed profiles, and proves strict improvement
of their real power characteristics for every saving 0<a<1.

These results do not prove compiler-to-profile binding, physical tape costs,
analytic multiplication transfer, or real-exponential certificate enclosures.
See declaration-scope-map.json and the parent contribution's proof, provenance,
and AI-assistance disclosure. Certificate success is not formal verification
of the complete multiplication theorem.

The five sources are byte-identical to the completed research version. Two
comments retain the historical artifact names outputs/independent_assembly.py
and outputs/concave-dominance.json; see the parent contribution for their
repository locations. Source changes require a reviewed manifest update.

The historical local check_lean.sh is intentionally replaced: it required
macOS toolchain paths and unrelated research clones. The existing repository
check_lean_axioms.py also assumes fully-qualified names in #print directives;
this checker handles the unchanged namespace-local directives through the
explicit theorem manifest.
