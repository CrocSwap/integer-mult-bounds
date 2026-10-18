# No extra singleton 4-to-6 B-frame change in the selected k8 word

**Status: scoped finite obstruction; no new κ.** On the exact local k8 word used by selected PR1094, every unchanged B gate with a 4D output frame has only a 4D or 5D common suffix cap. A legal replacement frame must be a 6D subspace inside that cap. Therefore none of the 22,785 possible one-gate 4D-to-6D changes can preserve the later frame chains.

The selected record remains Rohan Arun's conditional κ = 0.001672660197076918, with the complex side binding. This result does not change or independently re-review that construction.

## Exact domain and argument

The selected provider has 1,846 B gates in `F_2^9`. Exactly 147 unchanged gates have 4D output frames. The quotient of `F_2^9` by a fixed 4D frame has dimension five; its 2D subspaces number

```text
[5 choose 2]_2 = ((2^5 - 1)(2^5 - 2)) / ((2^2 - 1)(2^2 - 2)) = 155.
```

So the full candidate domain has 147 × 155 = 22,785 superspaces. For each gate, the verifier computes the intersection of every later paid B frame on both affected register chains, every later early-cleanup frame, and each terminal frame. This is a necessary condition for a monotone frame schedule. It records a basis for that common suffix cap at each gate. The dimension distribution is 122 caps of dimension four and 25 of dimension five; the maximum is five. A 6D replacement cannot fit. The dimension screen excludes all 22,785 superspaces without enumerating them gate by gate. The verifier separately enumerates all 155 extensions of a control 4D frame.

The result only covers one additional B frame changed from dimension four to dimension six on the selected word. It does not cover simultaneous frame changes, other dimensions, other local words, or changes to scalar circuits and helper inventories.

## Cost scope

The local B-frame annotations do not alter the scalar program. The selected source pins record 144 complete provider calls; the selected global paid profile equals 144 copies of the local profile plus fixed non-provider events. The eight centre charges are unchanged and no B gate accesses a centre role. A legal frame change in this class could only affect the paid rank histogram; it cannot remove a source access, copy, helper, restoration, width, or owner event. Since frame feasibility fails for every candidate, the selected histogram and complex moment remain unchanged in this scope.

## Reproduce

From the repository root, using Python 3.10+ and only the standard library:

```sh
python3 -I -B research/complex-k8-singleton-frame-cap/verify.py \
  --out /tmp/complex-k8-singleton-frame-cap.json
```

Expected stdout:

```text
PASS_NO_ADDITIONAL_4_TO_6_SINGLETON_B_FRAME gates=147 candidate_space=22785 max_cap_dimension=5 chronologically_feasible=0
```

The output JSON records all 147 gate indices, both affected roles, the old frame and the exact common suffix cap. It also pins the selected result, assembly, T16 plan, selected replay archive and decompressed local word. No optimizer or random search is used; seed 29 is the assignment seed only. Stopping rule: complete the 147-gate census and verify every cap dimension is below six.

## Sources, attribution, and limits

Exact source paths, SHA-256 values, Git blob IDs, and the selected local-word archive member are in [`SOURCES.json`](SOURCES.json). The selected record and its maintainer review identify the #1087 k8 word and #1094 owner packing. Credit Rohan Arun for #1094; Jeremy Kothe and the preceding #1050–#1087 contributors for the selected k8/owner lineage. PR1090's separate eight-frame/two-tail construction motivated a nearby comparison but is neither imported nor composed here.

This finite obstruction says nothing about a multi-gate schedule, a different paid profile, or the inherited all-size/compiler, realization, hosting, precision/tape, analytic-transfer, and bit-interface obligations. It is not a full multiplication theorem. The package contains no copied third-party implementation; new research content is under the repository's Apache-2.0 license. Prepared by Cinna Davis with substantial OpenAI Codex assistance.

## Open next questions

- **Can a simultaneous pair of B-frame extensions fit even when each single extension fails?** This matters because a joint schedule can alter the common suffix constraints. First step: enumerate pairs among the 25 gates with 5D caps and derive the joint chronology before testing any profile. Blocked by the need to maintain both gates' register-chain order and price resulting interactions.
- **Does any other dimension pair change the selected moment?** This matters because the present result only tests 4D-to-6D moves. First step: compute exact cap dimensions for 3D-to-5D and 5D-to-7D proposals on the same selected word. Blocked by the need for a separate complete candidate and cost budget for each pair.
