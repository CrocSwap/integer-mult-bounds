# Whole-role augmenting paths on the PR2322 T74 supplier

**Conditional κ = 0.001697147064845350. Complete finite admission passes.**
The actual owner map, native suppliers, physical invoice and conditional outer
bound have been replayed. The inherited all-size and analytic assumptions remain.

The construction keeps both PR2322 native words and its complete invocation
order. It improves how whole helpers occupy the available pending fields:
43 coordinated width-7/9 exchanges and 53 subsequent width-preserving paths
concentrate the remaining idle ranks. Every helper remains on one physical
family for its entire invocation. The certificate includes all 289,044 roles,
1,332 actual event windows, distinct-family restrictions, capacities and offsets.

| Comparison | κ |
|---|---:|
| Maintainer-selected PR1094 | 0.001672660197076918 |
| Pinned pending PR2322 | 0.001697060296258836 |
| Concurrent pending PR2349 | 0.0016970659941088806668… |
| This candidate | **0.001697147064845350** |

The gain over PR2322 is `0.000000086768586514`, approximately **0.005113% of κ**.
Relative to the selected record it is approximately **1.464% of κ**. These are
exponent comparisons, not measured runtime improvements. The proposed outer
exponent is `1-κ = 0.998302852935154650`.
The final overlap check found PR2349; this result also exceeds its full
published rational, by approximately `8.10707e-8` (about **0.00478% of κ**).

The unchanged fixed-word favorable packing ceiling is below
`0.001720061111244974`; the candidate realizes about 98.6678% of that ceiling.
This is an incremental packing gain, not a global packing optimum or a new
asymptotic multiplication proof.

## Construction and complete price

[PROOF.md](PROOF.md) proves the strict power-sum reduction for every exponent
`0 < p < 1`. [MOVES.json](MOVES.json) is the explicit witness. Each of the first
43 exchanges changes the complete histogram by `-2 H7 + H14`; the following
53 paths have their two endpoint budgets recorded and checked. Unchanged
intermediate bins retain their complete width and cost. Nine rejecting controls
cover role, family, copy, width, deadline, offset and path-accounting defects.

The final complete profile is

```
{1:1576962, 2:340992, 3:292196, 4:79920, 5:28004,
 7:1, 8:5328, 23:1, 32:13, 48:24546}.
```

There are 666 calls, 434 helpers per call, dimension 73, 66,304 live families,
rank mass 4,816,512 and deficit 23,680. The final invoice follows PR2349's
conservative stock accounting: 66,826 physical fields, including 78 dedicated
cleanup buffers in addition to the 434-field private reserve, eight centers
and two coefficient fields. Allocation/release CLEARs, every warp-routing
reserve and expanded adapter work are charged explicitly.
The bit supplier's retained endpoint is `0.001733427039589844234749`.
The complex side binds.

The directed native endpoint enclosure is

```
0.001697147064845350 < b* < 0.001697147064845351.
```

The endpoint, the whole-program outer point and the published rational are
separate quantities. [CLAIM.json](CLAIM.json) and the full admission receipt
identify their bindings and final status.

## Reproduce

The bounded verifier and deterministic discovery use Python 3.12 and the
standard library. No optimizer or network is needed:

```sh
python3.12 -B research/t74-owner-augmenting-paths/verify.py
python3.12 -B research/t74-owner-augmenting-paths/search.py
python3.12 scripts/research_package.py --package research/t74-owner-augmenting-paths
```

The first command authenticates original Git blobs, runs the predecessor's
independent full owner checker on both inputs and outputs, replays every path,
checks the exact moment and inherited cap, and exercises rejecting controls.
The search reproduces the published witness but proves no optimality. Failed
CP-SAT screens are not proof dependencies; the successful search uses explicit
alternating paths and no optimization library.

Full admission also needs NumPy, SciPy, SymPy, mpmath, a C++17 compiler and
Boost headers. The tested versions and source hash are recorded in VALIDATION.md.
Export the three exact source packages from an existing Git checkout:

```sh
python3.12 -B research/t74-owner-augmenting-paths/fetch_sources.py --repo . --out /tmp/t74-path-sources
python3.12 -B research/t74-owner-augmenting-paths/full_replay.py \
  --ancestor-root /tmp/t74-path-sources/pr2288 \
  --supplier-root /tmp/t74-path-sources/pr2312 \
  --predecessor-root /tmp/t74-path-sources/pr2322 \
  --work /tmp/t74-path-cold
```

Use new output directories. Set `CPLUS_INCLUDE_PATH` if Boost headers require
it. Without reuse flags, the command rebuilds the full pinned PR2288 parent
and both PR2322 native programs before fresh changed-data admission. Optional
`--baseline`, `--base-native` and `--extra-native` accept only complete caches
that pass the inherited source and artifact bindings. They do not skip changed
owner, controller, invoice, moment or outer checks. The source-bound baseline,
native and changed-data executions are reported separately in VALIDATION.md.

## Scope and provenance

The task was explicitly assigned by the donor: beat the strongest live κ
candidate, including pending results. This changes the selected-packing card's
scientific baseline to the borrowed T74 words of PR2322. No random task or new
word search is claimed. Main was pinned to
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

The nearest predecessor is [PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322),
head `002304ef01c4416a127916169ae6d94c1bee052b`. Its coherent handoffs, width
exchange, kernels, local frames, native words and two earlier owner exchanges
are inherited. This contribution adds different whole-role alternating paths
across multiple physical ports, with the invocation order held fixed. PR2309
already demonstrates the favorable `2 H7 → H14` arithmetic in another fill;
that concavity observation is not claimed as new. The new result is its actual
repeatable realization and complete admission on the stronger PR2322 supplier,
followed by additional strictly improving transfers. Concurrent PR2349 also
finds the 17 rank-four filling moves; no priority is claimed for that overlapping
part. The stronger profile here comes from the composed alternating paths.

The full original source manifests and exact Git blob pins are in
[PREDECESSORS.json](PREDECESSORS.json). The immutable inputs are copied solely
for bounded offline replay. Source packages and the selected frontier are not
edited. The staged admission runtime substitutes four exact PR2349 pricing
files, with every original or replacement file authenticated.
See [NOTICE.md](NOTICE.md) for predecessor credit and AI disclosure.

All inherited all-size/compiler, common-label/mutable-source, whole-call
hosting, physical precision/fixed-tape, exact recovery, analytic transfer,
PR559 recurrence and bit H1–H5 obligations remain. The near-native outer also
uses the retained capped-fusion/support-routing, equal-chunk interchange,
gauge-free and per-visit, radix-union and fine-prime padding premises. Passing
finite admission does not discharge those assumptions, constitute maintainer
acceptance, or establish a complete Lean multiplication theorem. No practical
cutoff or measured speedup is claimed.

## Open next questions

The structured questions are in [TASK.json](TASK.json). A useful extension is
an explicitly priced exchange involving more than one width after these paths
are exhausted, followed by actual chronology and full admission. A larger gain
will need a different local supplier or controller: the fixed-profile cap
still rules out κ=0.002 here. PR2339's low anticipatory aliases are a separate
local construction, but the final refresh found
[PR2360](https://github.com/CrocSwap/integer-mult-bounds/pull/2360), which reports
a whole-helper cap below 0.0016870 for that full inventory on unchanged T74
bins. A partial alias subset or changed parent stock should first be screened
against whole-width pattern costs before attempting complete native admission.
