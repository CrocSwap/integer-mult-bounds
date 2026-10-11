# Five new p10 response kernels with source-bound assembly

**Conditional kappa = 192302424469899716975181/250000000000000000000000000 = 0.000769209697879598867900724**, a gain of 1.0725982612867900724E-8 (0.001394435%) over the latest public PR320.

| checked construction | kappa |
|---|---|
| Public PR320 parent | 0.000769198971896986 |
| Derived five-kernel program, native assembly | 0.000769209694533059 |
| Same derived program, prime threshold and finite bootstrap | 0.000769209697879598867900724 |

This package adds five compatible rank-one response kernels to the public PR320 p10 construction and regenerates its downstream restore, sink, reorder, complete banks and finite invoice. The strict source replay and final combined prime-threshold/finite-bootstrap exponent are reported in the checked receipts. It preserves all seven terminal sinks; the kernel stage has 780 entries and total entrance rank 975.

## Replay

Python >=3.11, with assertions enabled:

```sh
python -m pip install -r research/p10-five-new-kernels/requirements.txt
python -X utf8 -B research/p10-five-new-kernels/verify.py --output /tmp/p10-new-kernel-verification
```

The output directory must be new and outside the package. The portable entrypoint freshly runs every native supplier stage, including the complex supplier, before deriving the combined exponent; inspection receipts are never proof inputs in that full replay. No network access, Lean rebuild, C++ compiler or private workstation path is required. All source files and nested manifests are hash-pinned.

## Source and contribution

The public parent is PR320 at e983fea0896b2a1d7355983674db7e9bb33a9e32, with native kappa 384599485948493/(5*10^17). This package is a derived source tree: four stage selections and the observed word-pins table differ. SOURCE-PIN.json records the public parent, its original manifest, the new manifest, changed-file hashes and the candidate’s separately certified native exponent. Parent, candidate-native and combined exponents are distinct; their gains are measured relative to the public parent.

The five exact prefix relations pass an independent C++ replay on all 4800 target columns, with five omitted-donor controls, nondegenerate rank-one frames and no response escaping target coordinates. The actual complete source replay checks the additional setup/restore gates, both reflected ledgers, all source/target/dirty columns, full integer restoration, all current and retained frame determinants, exact geometry and every literal bank assignment. The helper histogram change is {1:+7,2:+3,3:-6}; its rank mass falls by 5. An accompanying sufficient theorem proves a strict helper-moment root improvement for every admissible histogram at 0<a<=0.001, explaining why four additional paid calls can still win. That theorem is explanatory evidence; complete banks, fallback and assembly are checked separately.

## Prime threshold and finite assembly

The prime threshold Q=2^127-1 is checked by 125 Lucas-Lehmer iterations. Every growing prime q>=Q remains outside the freshly checked frame and normalizer exclusions. The original all-size growing-q regime and prime-supply assumptions remain unchanged. The envelope 2m^3/Q uniformly bounds 2m^3/q, with the full 32m^2 rank-one fallback per paid child retained. The complete literal invoice is recomputed and checked below Q, so C*q^10000<q^10001 for every permitted q. Two rational engines exclude adjacent root endpoints on the 10^-27 grid.

The initial saving 384599/10^10 is strictly below the freshly verified candidate native finite leaf. Eight finite ordinary-bootstrap levels then reach the combined grid cap; each level has positive gaps and the retained explicit finite-cutoff arithmetic. All 47 strict constraints and all seven outer margins are checked at eta=10^-24 and beta=10^-9, and adjacent kappa points and undercharged invoices are rejected.

## Check origins and conditional scope

The delivery audit freshly checked the complete public parent, including its complex program, scalar/splice/precision invoices and negative controls. The candidate audit freshly checks its changed complete bit program, geometry, scalar identities, prime coverage, banks, moments and finite assembly. It reuses that same-session complex receipt only after exact equality of every complex dependency hash; this reuse is explicitly recorded. The portable verifier above fully regenerates the complex stage as well.

This establishes a sufficient conditional finite construction under the unchanged public all-size compiler, weighted-selector, common-ancestor-chart, restored-row, routing, prime-supply, recovery and complex analytic interfaces. The full asymptotic cutoff retains every inherited primitive, wrapper and preceding ordinary-level constant. No universal machine execution or Lean certificate is asserted. No separate supplier gains are summed. Original named credits and licenses remain in the upstream notices.
