# Kernel-checked Boolean basis-to-stream lifting

[Lifting.lean](Lifting.lean) proves that two finite XOR circuits agreeing on
every Boolean basis input agree on arbitrary indexed Boolean streams, and may
be substituted before any unchanged continuation. This formalizes the generic
implication used in the predecessor's
[semantic D contract](../r439-semantic-d-contract-seed10/PROOF.md).
The elementary linear-algebra argument and its application are credited to
that predecessor; the new result is its kernel-checked generic lifting step.

The retained PR589 and PR1062 D prefixes also have identical full 661-wire
matrices under two independent Python executions. **This finite instance is
external evidence, not a Lean proof of the compressed source translation or
of all 661 input columns.** No new H2/K admission, physical supplier, ADD
saving, kappa, or complete multiplication theorem is claimed. The exact
separation is recorded in [BOUNDARY.md](BOUNDARY.md).

## The proved implication

`Vec n` is `Fin n -> Bool`. A gate updates one destination by XOR with a
source. `run` executes a finite gate list chronologically, and `streamRun`
executes the same operation pointwise on `Fin n -> alpha -> Bool`.

The four audited roots are:

- `XorLift.basis_complete`: two zero-preserving XOR-linear maps equal on all
  basis vectors are equal on every vector, including dimension zero.
- `XorLift.run_linear`: every finite circuit in the declared gate language
  is such a linear map.
- `XorLift.basis_to_stream`: equality of every finite Boolean basis column
  implies equality for every stream over any index type `alpha`.
- `XorLift.continuation_substitution`: applying any identical continuation
  to the equal resulting streams preserves equality.

`check_lean.py` compiles the complete pinned source anew and appends a real
three-wire example. The two gate lists are
`[(0,1),(0,2)]` and `[(1,2),(0,1),(1,2)]`, where pairs mean destination/source.
All basis coefficients are proved with kernel `decide`, and the generic
theorem then proves stream equality. Omitting the final restoration or the
second helper read gives a false basis proposition; both compiler runs must
fail. The checker requires successful compilation and live axiom reports
for all four roots plus the example, rejecting missing reports and any
nonstandard axiom. It never accepts a supplied or stored compiler log.

Tested with Lean 4.34.1, commit
`5045d0056413266e57c625dcd7c365b10e377c52`, on Windows. All five positive
roots report only `propext` and `Quot.sound`; no `sorryAx` or custom axiom.
The two negative compilations fail at `decide` as required. Three harmless
unused-simp warnings remain. Other Lean versions were not tested.

## Source-bound finite application

[SOURCES.json](SOURCES.json) pins canonical base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, Git blobs and SHA256s. The
original PR589 compressed word and the PR1062 helper-star candidate both
have 111 sources, 111 targets and 439 arbitrary dirty helpers. Compressed
triples `[frame, destination, sources]` denote successive ordered XORs.
Both D prefixes use frame index zero, whose frame is empty, and touch only
distinct target/helper operands entering at that common frame.

The row engine starts with 661 integer basis masks and executes the flattened
ADD list. The column engine separately reads the compressed triples and
executes literal Boolean values for each of all 661 input columns. Their
436,921 coefficients agree, and the old/new matrices agree. The old D has
18,085 ADDs and the candidate D has 5,548; this reduction is predecessor work.
The matrix receipt, including its exact byte encoding, is in [RESULT.json](RESULT.json).

Omitting the candidate's first or final ADD changes the matrix. A nonzero D
frame is rejected before replay. A separate contamination gate
`target111 ^= helper222` demonstrates why source-only and zero-only tests
cannot replace all dirty-input columns. Export controls run with Git absent,
reject source-byte and Lean-source mutations, and reject a typed receipt
mutation (`true` changed to `1`). All source hashes are checked before
decompression; duplicate keys and nonfinite JSON values reject. Normal runs
do not write tracked artifacts.

## Reproduce

From repository root, Python 3.12 with standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/xor-prefix-stream-lifting --check-only
python3.12 -B scripts/research_package.py --package research/xor-prefix-stream-lifting
```

The registered hook checks the **external finite application** and its controls.
Run the separate **live kernel check** with an installed Lean compiler:

```sh
python3.12 -B research/xor-prefix-stream-lifting/check_lean.py --lean /path/to/lean
```

The direct finite verifier also works in an export containing this package and
the three paths in `PINS`, without Git. The metadata/pin wrapper itself requires
the originating Git history. Receipt regeneration is opt-in via
`verify.py --emit-result NEW_PATH` and refuses overwrite.

## Open next questions

Can a checked Lean decoder or proof-producing certificate bind the actual
compressed 661-wire sources and matrix equality? That would remove the external
translation and finite-premise boundary. Begin with a typed compressed ADD
decoder and explicit byte-to-word certificate.

Can the common-frame interpretation and unchanged continuation be integrated
into a formal physical/interleaved supplier theorem? First specify the complete
state, including frame metadata, and discharge the predecessor's chronological
interpretation. Physical realization, integer payload envelopes, tape/rounding,
hosting, and analytic multiplication obligations remain outside this result.

## Credit and task selection

The semantic contract and prose basis-to-stream argument are by @woklerx with
OpenAI Codex assistance. Credit Zhihao Chen's PR425 scalar-interface lemma,
eumemic's R420/PR555 checker adaptation, DreamingOfClouds' PR589 tuning,
Gareth Davidson's PR926 pairs, @theon199's PR967 helper stars, Sagar Thakrar's
PR1062 composition, Aaron Wang's PR1015 circuits and Ross Richardson's PR923
frame520 circuit. The nearby PR590/612/878 `BitXorTargetTranslation` work
concerns target shifts; it does not prove this all-basis stream implication.

Picker nonce `c362a20ba23bd7f28ca19cf60b7d1c82`, original `bit-helper-contract`,
changed to this formal implication with an explicit external application
boundary; details are in [TASK.json](TASK.json). New work by ywz65 with
substantial OpenAI Codex assistance, Apache-2.0. No independent human review
or complete physical proof is claimed.
