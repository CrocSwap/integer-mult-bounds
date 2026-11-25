# Lift local instruction-prefix facts through typed tapes

This small Lean 4.21 module builds on the unchanged AdmissibleTypedTape dependency contributed in PR1835. It proves three generic facts: actual code lowering commutes with typed concatenation; the finite per-operation predicate splits across concatenation; and a property of every local instruction prefix lifts to every prefix of the concatenated instruction list.

The main theorem takes the actual instruction interpreter and its empty/append laws, dependent input/output domains, a predicate on each operation, initial domain membership and the initial observed property. Its local premises establish domain closure and the observed property at every prefix of that operation's actual code. The proof follows chronological execution and establishes each intermediate domain membership before continuing. Empty phase code and arbitrary prefix lengths are included. It assumes no whole-tape endpoint or whole-tape prefix conclusion and needs no inverse premise.

The exact new source compiled unchanged. Independent review accepted all three probes and the complete main theorem type: the two append facts use propext, and the prefix-lifting theorem uses propext and Quot.sound. There were no warnings or finite decisions. ACCEPTANCE.json records the public source-bound acceptance summary. Detailed original review records remain preserved with the authors. A separately checked scratch-save application is outside this minimal source closure and is not claimed here. Preserved source headers describe preparation as uncompiled; the accompanying acceptance summary records the later check of those exact bytes.

Reproduction, with Lean 4.21 already installed, from the repository root:

    set -eu
    lean --version | grep -F 'version 4.21.0,'
    unset LEAN_PATH LEAN_OPTS
    printf '%s  %s\n' 9bb5d28159cc6c4871b67e8e057ed8a9533d7d7ce5fe50866cd787712f0a9829 research/lean-typed-code-prefix/TypedCodePrefix.lean | sha256sum -c -
    build=$(mktemp -d)
    curl --fail --location --proto '=https' --tlsv1.2 \
      https://raw.githubusercontent.com/jamesyc/integer-mult-bounds/e41a160c77e559b8023a59c14af08fceeaf33c9a/research/lean-admissible-typed-tape/AdmissibleTypedTape.lean \
      -o "$build/AdmissibleTypedTape.lean"
    printf '%s  %s\n' 92cccf6c04267d79a6495c58c4dd63dac2834b53decda477511e1ac4c33be7a4 "$build/AdmissibleTypedTape.lean" | sha256sum -c -
    lean -j1 -o "$build/AdmissibleTypedTape.olean" "$build/AdmissibleTypedTape.lean"
    LEAN_PATH="$build" lean -j1 -o "$build/TypedCodePrefix.olean" research/lean-typed-code-prefix/TypedCodePrefix.lean

The dependency is fetched from the immutable public PR1835 head into the fresh temporary directory and checked before compilation. It is not included as a changed source in this PR; current main need not already contain it. No dependency object is downloaded. No Mathlib source is imported by this two-module research closure. These commands are reproduction instructions, not a claim that a fresh publication checkout was replayed. The existing native check used the accepted AdmissibleTypedTape object plus official Lean imports.

An application still supplies actual phase code, interpreter laws, finite operation constraints, initialization and local implementation facts. The accepted scratch-save application uses full-state restoration and an initial-or-one-enter invariant to reuse original-memory budgets; this uniformity cannot be inferred for components that modify those memories. Physical allocation, the size of whole metadata/data/program/control storage, compound-instruction internal workspace, rounded arithmetic and selected multiplication remain separate.

Attribution: James Chang with OpenAI assistance, Apache-2.0 under the repository LICENSE. The source reuses AdmissibleTypedTape and Lean's list prefix identities unchanged. Its dependency retains the domain-restricted dispatcher motivation of Hanson Sun (@bbMisk), PR1530, and the PR590/597 interpreter interface. Related PR896 proves a particular nonlinear commutator restoration/inverse result (Gareth Davidson / bitplane, formalizing PR628 by Chafik Boukhalfa and PR663 by 0xkilgore); PR612 supplies selected R420 Boolean helper semantics. This module addresses arbitrary typed phase-code prefix lifting, without claiming that inverse, prefix or spectator reasoning itself is new. The earlier PR896/612 comparison concerns the dependency and is not an exhaustive novelty audit of this module.

Author-checked pinned numerical context: upstream main 0b1cccf86e2f5132ed286a26ef0a681a495740ea records kappa=836330098538459/500000000000000000=0.001672660197076918, with assembly SHA256 1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045. Both selected-result and assembly fields were read and matched when this manifest was prepared. This generic theorem changes no numerical bound and does not certify the selected construction. This is pinned historical context, not a current-base publication lease.
