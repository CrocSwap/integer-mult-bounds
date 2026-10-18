# R439 complete single-ADD omission atlas

**Finite independent verification; no new kappa.** In PR967's frozen 5,563-ADD D phase, every single elementary ADD omission changes the complete D boundary. All 5,563 resulting linear-map differences are distinct and have rank one. Observing only the 111 target outputs misses exactly **221 omissions**, all in the final helper-restoration region. Even observing every output on the single all-ones input misses **1,522 omissions**.

This package supplies an exact fault-class census, all 221 concrete helper-only witnesses, and a practical independent replay. It does not propose a new circuit or improve the selected frontier.

## Reproduce

At repository root, using Python 3.10+ and the standard library:

```sh
python -I -B research/r439-omission-atlas-seed81/verify.py
```

Expected final line:

```text
PASS_R439_OMISSION_ATLAS gates=5563 target_invisible=221 unique=5563 controls=7 no_new_kappa
```

The default command recomputes the entire census and compares every field of [CERTIFICATE.json](CERTIFICATE.json). It consumes exactly the two immutable gzip inputs in [SOURCES.json](SOURCES.json), checks their hashes and exact inventory, and binds the frozen base receipt. It does not depend on the moving root selected-result.json. It imports no predecessor Python code. Use --write-certificate only to regenerate the local certificate deliberately; the default command never writes it.

## Exact fault and observation models

The source is the incorporated PR967 candidate at base `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Its D has 1,165 grouped records. Each listed source occurrence is one chronological ADD, giving exactly 5,563 possible single omissions. Grouped records have no destination/source alias; their listed source order fixes the expansion. All gate, record, source-position and register indices here are zero based.

The input is an arbitrary vector in F2^661 at the beginning of D, including arbitrary dirty helpers. Registers 0..110 are sources, 111..221 targets, and 222..660 helpers. Full-boundary observation compares all 661 output rows as linear functions of all 661 input coordinates. Target-only observation compares just rows 111..221, still for arbitrary input. The separate all-ones experiment compares all 661 outputs for one fixed input and is a strictly weaker input test.

| D region | ADDs / omission cases | Target-visible | Target-invisible |
|---|---:|---:|---:|
| Helper preparation | 221 | 221 | 0 |
| Target preparation | 306 | 306 | 0 |
| Middle injection | 4,509 | 4,509 | 0 |
| Target restoration | 306 | 306 | 0 |
| Helper restoration | 221 | 0 | 221 |
| Total | 5,563 | 5,342 | 221 |

The full-boundary syndromes are all distinct. The 5,342 nonzero target syndromes are also distinct; the other 221 collapse to the zero target syndrome. These are identities between linear maps, not a claim that a single fixed test input distinguishes all faults.

For example, omit gate 5,342 (grouped record 944, source position 0), ADD 541,588. With input e588, only output register 541 changes. Every target output agrees. [CERTIFICATE.json](CERTIFICATE.json) supplies the same explicit singleton-input construction for each of the 221 invisible omissions, checked using a separate Boolean interpreter. Its all-ones counterexample is gate 246: its fault covector selects inputs 158 and 179, so all ones cancels; input e158 instead changes target output 174.

## Independent checks and proof

Writing the circuit around one gate as S E_ds P, with E_ds = I + e_d e_s^T, omission changes the map by

```text
S E_ds P + S P = (S e_d)(e_s^T P) = u v^T.
```

All elementary ADDs have d != s and are invertible over F2. Hence u and v are nonzero and every such fault has rank one. The implementation obtains v by forward prefix rows and u by backward suffix columns. Complete observation detects the fault for some input; target observation does so exactly when u has a target coordinate. Input e_j with v_j = 1 activates exactly the output difference u. The all-ones input misses exactly the even-weight v vectors.

The matrix replay independently starts from 661 identity rows for **each** omitted-gate program and executes all its remaining ADDs in chronological order. It neither calls the factor routine nor reuses its prefixes or suffixes. It compares all 661 resulting rows against u v^T for every omission: 30,941,406 ADD updates and 3,677,143 row comparisons. Thus a wrong suffix orientation, stage boundary or fault factor cannot be accepted merely because its formula-generated hash matches. The baseline itself is separately replayed and compared with the entire original PR589 D boundary. All non-D fields agree canonically, and source/helper restoration plus the target dependence block are checked.

Seven negative controls reject incomplete coverage, a zero factor, target-only sufficiency, all-ones sufficiency, duplicate JSON keys, nonfinite JSON, and replacing a propagated suffix effect with its unpropagated destination singleton. Canonical comparison distinguishes Boolean and integer receipt values and binds every certificate field, including the observation scope and metadata. Validation is recorded in [VALIDATION.json](VALIDATION.json).

## Relation to prior work and limits

PR967 already supplies its construction proof, whole-word endpoint replay, owning interface/geometry checks and sampled controls. This adds complete enumeration of a different, explicitly finite fault family with two observation models. It does not identify a defect in PR967's existing full-boundary verifier.

Sagar Thakrar's [PR762](https://github.com/CrocSwap/integer-mult-bounds/pull/762) studies up to three compensation-coefficient changes per target in historical R420 and proves an optimal ten-pattern test family. Its fault geometry and observation problem differ from single gate omissions in PR967's interleaved R439 helper preparation/restoration. We credit that prior fault-testing work and make no claim to invent prefix/suffix sensitivity or rank-one fault propagation. The local claim and three considered candidates are in [CLAIM.md](CLAIM.md).

There is no multi-fault, wrong-operand, whole-record omission, arbitrary circuit, whole-word frame/precision, native checker, tape/hosting, outer assembly, unrestricted minimality or practical speedup claim. The arbitrary-input domain is the D boundary, not the subset reachable from an earlier whole-word state. No new kappa follows; the selected frontier and upstream are unchanged. Native tools were not run in this environment. See [NOTICE.md](NOTICE.md) for predecessor credit and AI disclosure.
