# Joint entrance choices with T37 whole-owner packing

This composes PR1148's joint entrance choices (head `f1d8dc59288dcab77cae713c450d14069e7eec05`) with a new exact T37 owner flow on PR1131's wave order. The verified conditional value is **κ = 0.001675568675201533**, **0.0004611994%** above PR1148's T16 value `0.001675560947524449`.

The construction has **159,840 whole-helper roles in 333 calls**, local profile `{1:2364,2:498,3:412,4:130,5:82,8:8}`, and idle profile `{1:834,48:11374}`. It attains PR1148's exact grid upper value for this fixed local word, helper inventory, whole-helper bin family and outer recipe. This scoped packing ceiling does not cover changed local words, mixed suppliers or other recursion geometries.

Validation passed:
- Exact integer flow equations and literal bipartite matching reconstruction; every role is included and every capacity/window is checked.
- Fresh native five-stage replay of the pinned joint-entrance word, including all 704 columns and 2,904 phase edges; independent local audit and 27 entrance controls.
- Strict T37 provider binding, controller, invoice and assembly using the retained PR1129 admission engines: 69 admission, 12 bit, 15 controller and 7 independent owner controls; all 47 outer inequalities.
- Independent checks of 2,016 disjoint pending-child axis relations. Prefix bound 775 < 1024 and physical row coefficient 17,495 < 20,161.
- Portable package replay, using the explicitly supplied fresh native replay above and pinned parent geometry, returns `PASS_T37_JOINT_ENTRANCES_NATIVE_AND_STRICT_ADMISSION` at the stated κ. The fixed-family upper bound is separately recomputed with two exact engines.

Package: `research/three-demotions-t37-composition/` (directory retained from the initial three-demotion draft; latest payload uses joint entrance groups 603, 611 and 635).

```sh
python -B research/three-demotions-t37-composition/verify.py --work /absolute/new/output-directory
```

Python 3.11+, a C++ compiler and Boost headers are required. This default rebuilds the native provider. `--native-from /path/to/completed/native-replay` explicitly reuses a completed five-stage replay with word and semantic bindings checked; local controls and all T37 admission stages still rerun. Parent geometry is reused from archived pinned inputs and its actual windows are independently reconstructed. The package requires no network or optimization solver. Repository-wide hosted CI is separate from these focused local passes.

Credit: Thomas DiFiore/Codex and PR1148's full local ancestry; seslly/shipstuff PR1111's group-635 lead; Ali Romman/Codex PR1129's integer flow, matching decomposition and T37 audit; PR1131's wave order; PR1074/1018, Rohan Arun's PR987, PR1030, PR864, Hao Yan/FanPUYen's PR858, PR870, Chafik Boukhalfa's PR795/890 duals, PR942, PR1091, and the unchanged PR589 bit supplier. New composition by Rohan Arun with substantial OpenAI Codex assistance, Apache-2.0. Original notices and source pins are retained. `INDEPENDENT-DERIVATION.patch` shows the sole checker adaptation: the same inventory predicate now receives the new frozen width inventory as an input.

All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and bit H1-H5 obligations remain. No unconditional multiplication theorem, full formalization, general sphere-packing optimality or runtime improvement is claimed.
