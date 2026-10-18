# P104 pointwise defect codes and the mutable-source boundary

The exact rounding defect of the fixed P104 lifting word admits fewer labels
than its translation quotient at small ranks. The complete images have
**3, 25 and 10,225** values at ranks one, two and three, across **4, 64 and
32,768** lattice cosets. At ranks two and three this saves **one fixed label
bit**. These are complete integer-image counts, with a separate rank-one/two
implementation and a written all-input periodicity/transversal argument.

The saving does not survive a specific proposed mutable interface. A code
that determines the defect and supports **every additive source translation
from the code alone** must distinguish the full defect-period cosets. For the
fixed rank-seven word, the credited maximal-period theorem and rerun prefix
index give an exact abstract minimum of **343 bits** under that contract.
No such bound is claimed for immutable-source recomputation, source-dependent
updates, restricted translations or other words. The static rank-seven defect
image is **not** enumerated or inferred from the small cases.

This tests a changed consumer premise, rather than seeking a larger translation
lattice or repeating PR3043's reducer and PR3046's inverse-basis work. No
favorable complete recursive cost, admitted supplier or new kappa follows.

## Result and evidence

Let `L_r` be the literal signed-floor word, `U_r` its ideal linear map,
`A_r=2^r U_r`, and `D_r(x)=2^r L_r(x)-A_r x`. The
[proof](PROOF.md) gives:

* a complete binary transversal from the sufficient prefix-parity subgroup
  chain, exact image/fiber counts and a scalar period for all signed inputs;
* an explicit repeated rank-one witness showing that equal pointwise defects
  can separate after translation, at **every positive rank**;
* the general code/period theorem, with the 343-bit corollary importing the
  exact PR3035/3037 period/index premises;
* an exact retained-source dirty-buffer consumer, with both numerator shears,
  both defect additions, two quotient reads, output/lookup work and cleanup
  still charged;
* a precise full-scan table invoice and a small structured rank-one XOR oracle.

[RESULT.json](RESULT.json) fixes every fiber multiplicity and keyed image hash.
The rank-three census covers all 32,768 transversal representatives, with
prefix and determinant checks; it is not a second independent census. The
separate [independent implementation](independent.py) covers all 65,552
rank-one/two low-bit inputs, inverse recovery, a closed ideal-matrix basis
check, 2,401 signed local pair cases and the rank-one arbitrary-target oracle.
Its assertions are deliberately compiled with `optimize=0`, including during
an optimized parent replay; the loader control tests this requirement.

The main replay compares all 32,836 small-rank representatives with the
byte-authenticated predecessor floor word; 28 signed scalar-period fixtures
include signed values containing `2^4090`. It also checks 252 arbitrary-target, signed-dirty
consumer cases and all 4,096 rank-one source/XOR-target pairs. Nine behavioral
groups reject missing transversal coverage, a bad scalar period, merged-label
source updates, omitted cleanup, dirty work, wrong signed floors, signed encoding
overflow, wrong charge/domain, a literal sign mutation, source/typed-receipt
drift and source-cache substitution. An optimized read-only Git-free export
recomputes the entire receipt.

These are finite exact computations and written proofs. The independent child
review is internal AI-assisted mathematical checking, with no independent
rank-three, human or formal-kernel proof claim. The imported maximality proof
is retained unchanged in [vendor/period-PROOF.md](vendor/period-PROOF.md).

## Complete-cost decision

An immutable retained source can support a direct defect consumer even though
the compressed label has no code-only update. The written dirty-buffer
schedule has bill `2 C_A + 2 C_defect-add + 2 C_Q`. If a clean defect vector
is produced by an XOR oracle, each defect-add pays two oracle calls, a wide
addition and the corresponding output/ancilla capacity. All source, buffer,
target, program, routing, physical restoration and recursive backend costs
remain additional or explicit obligations. The numerator needs up to
`r+ceil(r/2)+O(1)` extra source bits before dirty-buffer and carry headroom.

The specified equality-scan XOR table, **given** a precomputed 15-bit
rank-three coset address, costs 917,504 Toffolis, 1,210,752 CNOTs, 491,520 X
gates, 14 clean equality bits, a 96-bit arbitrary target and 3,145,728 explicit
table bits. Address production and integer consumption are additional. A
32-bit raw-address full scan would use 266,287,972,352 Toffolis. These chosen
scan constructions include zero-output rows and are **not** circuit lower
bounds. No large table was synthesized or executed. A structured rank-one
control costs only 16 CNOTs, four Toffolis and four X gates with two restored
clean work bits, illustrating why synthesis can change that price.

The family decision is to stop at this interface test. Pointwise compression
is real; the code-only mutable variant loses it under the stated update
contract. The retained-source alternative needs a specified fast consumer and
an actual full bill. Neither the finite image reduction nor the table price
is a recursive saving or a global obstruction.

## Reproduction

```sh
python3.12 -B scripts/research_package.py --package research/p104-pointwise-defect-consumer
```

Direct `verify.py` and `test_verify.py` replays are read only, standard-library
only, and also support optimized Python. The registered replay uses Python
3.12. Publication bytes, hosted CI, human review and scientific admission are
separate gates. No full selected cold replay is needed or claimed for this
additive local interface result.

## Provenance and credit

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6,
selected-record SHA256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
[TASK.json](TASK.json) records the changed card and stopping decision;
[PREDECESSOR.json](PREDECESSOR.json) authenticates consumed source bytes.
[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18982976).

Credit Tekalign/PR3025 and PR3033
`b12bbaeb5ca2e83f15433fc2dd0ba3b766595281` for the fixed lifting word/scalar
split; Nick Petalas/PR3035 `0cc430349a3f3dc200666bc22e997076e0a557ed` and
PR3037 `02a1c41e8e016d3d0be64c62c8b4734f9c494236` for the prefix lattice,
index and maximality theorem; Ross Richardson/PR3043
`b5cabfb02a3d8bc3121825144373b03a5648479d` for the narrow reducer/source copy;
Arham Tahir/PR3046 `5549524f7894120b7e993522eb3a59956df5c5c3` for the
complementary inverse interface; ywz65/PR2586 and the retained P104/native
lineage. The pair-error identity, period lattice, reversible lifting and
general table lookup are not claimed as new.

Ross Richardson, with substantial OpenAI Codex assistance in derivation,
implementation, independent internal checking and writing. Apache-2.0.

## Open next questions

1. Can an immutable-source direct defect consumer avoid enough actual work to
   pay label acquisition, full-vector output, exact numerator, movement and
   compute/add/uncompute? First specify one circuit and its complete tariff;
   stop if its favorable full budget fails. No rank-seven search is proposed.
2. Does a particular caller require all translations, or only a smaller
   specified set with affordable source-dependent access? First derive that
   update set from its actual word. The theorem cannot silently replace that
   boundary with all translations. Structured blockers are in `TASK.json`.
