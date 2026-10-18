# A paid ordinary-to-selected B2 observation at the first QQ16 cut

**Exact local witness repair and conditional profile budget. No complete controller or κ claim.**

The current selected checkpoint is unchanged at
`certificates/selected-result.json` SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Its accepted review,
source manifest, assembly certificate and reproduction target are pinned in `SOURCES.json`.
The local QQ16 words from merged PR #1969 are also pinned there. This package builds on its
reviewed selected-output witness; it does not rerun that witness or the complete local-word replay.

## Changed observation

The reviewed QQ16 witness uses the fixed F0/B1 pair and retains the ordinary schedule. It gives
eight independent lost directions

```text
h_k = (48 I - B1* B1) B2* e_k,       k = 0,...,7,
```

where `B_s = R_s iota_U`, `*` is transpose, and `e_k` is the kth centre basis vector at the
identity cover element. Its established Gram identities are

```text
B1 B1* = 48 I
B2 B2* = 48 I
identity-coefficient(B2 B1* B1 B2*) = 192 I.
```

The current query `q2 = B2 Y + ell_2,A Y_A` can vanish on these directions. The proposed changed
interface adds the distinct ordinary-to-selected read

```text
q_extra = B2 X_U
```

immediately before F0. The read does not change `X_U`. For every `k`,

```text
B1 h_k = 48 B1 B2* e_k - B1 B1* B1 B2* e_k = 0,
identity-coefficient(B2 h_k) = (48*48 - 192)e_k = 2112 e_k.
```

Thus `q_extra` distinguishes all eight directions of this fixed obstruction family. The selected
record `X_0,T` on the witness is
`P_0,T ell_0,A P_2,A B2 h_k`; the cited witness proof establishes that this factor is an invertible
map between the selected coordinate spaces. The new observation therefore carries the missing
eight-dimensional information on this witness family. It does **not** prove that the whole
controller becomes injective on arbitrary inputs.

The short verifier checks the exact 8-dimensional arithmetic consequence of these pinned Gram
identities and the profile calculations. The source route enumeration and original witness proof
remain the prior reviewed evidence; this package does not present them as an independent replay.

## Observation invoice and its limit

The proposed observation reads 96 ordinary source coordinates and returns eight independent query
coordinates. Since `B2 B2* = 48 I`, its output rank is eight. The source is read-only, so the
observation itself needs no source restoration. The eight returned values must still be hosted as
an added output state. A selected-word address/frame wrapper, output storage, helper ownership,
dirty-state restoration and recursive precision are not supplied by this changed-interface
definition. In particular, this package does not set any of those costs to zero in a supplier
claim.

For an optimistic **profile-only** screen, the merged QQ16 `B_s,t` local word has native profile
`{1:2436, 2:418, 3:432, 4:142, 5:82}` and rank mass 5,546. If the eight new outputs could be
carried together in a single rank-8 child, profile mass would be 5,554. The exact selected
ceiling model then leaves only **0.043725878%** headroom over the selected word, before any new
address, copy, helper, frame, hosting or restoration toll. With eight separate rank-one output
charges the ceiling is already **0.035543596% below** the selected word. The profile variants are
shown below; the rank-8 envelope is not a proved implementation of the observation.

| Profile | Local mass | Ceiling upper | Change from selected upper |
|---|---:|---:|---:|
| Selected `{1:2412,2:418,3:432,4:142,5:82,8:8}` | 5,586 | `169005411/100000000000` | baseline |
| QQ16 B word `{1:2436,2:418,3:432,4:142,5:82}` | 5,546 | `845992169/500000000000` | +0.114211018% |
| B word plus one ideal rank-8 output child | 5,554 | `1690793101/1000000000000` | +0.043725878% |
| B word plus eight rank-one output charges | 5,554 | `422363351/250000000000` | −0.035543596% |

With the rank-8 envelope, two additional rank-one-equivalent charges still leave a positive
ceiling difference; three put it below the selected word. This leaves essentially no budget for
the real observation's output routing and hosting. The exact query-row ADD invoice and its native
address/frame implementation are not derived here, so this is a favorable stopping screen rather
than a complete controller cost.

## Scope and predecessors

- [PR #1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969), merged at head
  `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`, supplies the local joint-query words and native
  contracts. This package adds a distinct ordinary-to-selected read of `B2 X_U` at the first cut.
- The selected-output witness and its independent review show that fixed F0/B1 loses the eight
  directions above even when the listed selected outputs and query histories are observed. This
  package uses that result as a pinned premise and asks whether one specified changed observation
  exposes those directions.
- Discussion #1976 changes swapped-chart source-code order; its source-only order obstruction is
  adjacent but does not study this first-cut observation.

Claim and handoff: [Discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074).
Contribution: [PR #2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079).

## Reproduce

From the repository root:

```sh
python3 -I -B research/joint-query-extra-b2-observation-seed3e62/verify.py
python3 scripts/research_package.py --package research/joint-query-extra-b2-observation-seed3e62 --check-only
```

Expected verifier prefix: `PASS_QQ16_EXTRA_B2_OBSERVATION_SCREEN`. The first command verifies the
exact eight-direction consequence from the pinned identities and certifies the profile brackets;
the metadata checker validates package pins and declarations only. Neither command constructs or
checks a native controller.

## Open next questions

- **Can this observation be implemented in the selected word's native interface?** The local
  ceiling leaves only two rank-one-equivalent units for every added mapping and hosting cost.
  First compile the exact `B2` read at the pre-F0 source frame and count query-row operations,
  output writes and cover maps. Blocked by the missing native address and output-storage contract.
- **Does adding `q_extra` close the full controller?** Distinguishing the reviewed eight-direction
  witness is only a subspace result. First form the full ordered map with the new output row and
  compute its kernel while preserving all 480 ordinary helpers and selected endpoints. Blocked by
  the absence of a new full controller word.

## Pins and credit

Cycle seed `3e62c004252727348ccea2dae9bbded6`, track `recursive-interfaces`, task
`joint-query-controller`, priority revision 4, exact base
`7c1e7811c730b17fe0eeef6c82ef011318b0465e`, selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. The cycle task and bounded
scope are recorded in `TASK.json`; the reviewed QQ16 and selected sources are pinned in
`SOURCES.json`. Credit Ali Romman and the PR #1969 lineage for the existing QQ16 words and
selected-output witness. Prepared by Cinna Davis with substantial OpenAI Codex assistance in
choosing the added observation, deriving its exact action on the witness family, and pricing the
conditional profile.
