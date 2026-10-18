# R438 bit hosting: window-respecting optimal re-hosting of the width-8 slack

**Status: bit headroom only, no new κ; conditional on PR1043 (R438, open and not admitted). Row (b) is also
conditional on the transported word built and replayed by `verify_transport.py` in this package.** The selected record is complex-bound. The bit supplier does
not bind, so nothing here changes κ. This is a finite, scoped slot-model certificate. It is not a
hosted-template emission and not a multiplication theorem.

## Question

[PR1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043) (aliromman) removes helper470 from
the PR589 R439 bit word, giving R438. Its `hosting_change` returns each freed width-8 slot to its own
host copy. Per replica, that leaves remainders `{10:5, 12:3, 14:1}` on top of the PR589 profile. Its
README says it runs no hosting search.

In the PR1023 slot model (`research/bit589-width-packing`), each replica has width-8 capacity 3996.
That leaves a slack of 3996 − 9·438 = **54** units at R438, against 45 at R439. Where should the 54
units go, and is that placement window-feasible?

## Results (all exact; `RECEIPT.json`)

| Quantity | Value |
|---|---|
| Optimal layout, S = 54 | `10×(42,5) + 1×(42,4)`: ten fully idle 42-slots and one 42-slot holding one helper (remainder 34) |
| Idle profile per replica | `{2:433, 4:444, 6:444, 7:666, 34:1, 42:10}` (1,998 idle children, as PR1043) |
| Hosted rank mass / children (local + idle) | 1,808,352 / 904,320 (unchanged from PR1043) |
| Runner-up layout | `10×(42,5) + 1×(14,1) + 1×(28,3)` |
| Runner-up gap, Σg per replica at c_a + 1e-24 | [0.007902038724851374389941593752047420, …421] |
| Same gap in moment units | [1.390420665268048703185105882609695e-7, …696e-7] |
| PR1043 in-place layout `9×(42,5)+5×(42,1)+3×(28,1)+1×(14,1)`, gap to optimum | Σg 0.116172190755053614177477242754726502…503; moment 2.0441334240402170e-6 |
| Layouts covered by exhaustive cross-check | 10,556,685 (S = 54), 3,160,688 (S = 45) |

Bit endpoints. Each is accepted at c and rejected at c + 10⁻²⁴ by both pinned engines, with the
inherited surcharge.

| Row | c | vs PR1043 | vs PR589 |
|---|---|---:|---:|
| PR589 R439 selected (positive control) | 0.001733427039589844234749 | | |
| PR1043 R438, own in-place hosting (positive control) | 0.001734176288479865766692 | 0 | +0.0432% |
| **R438 window optimum, local (a) PR1043** | **0.001734802047828389852783** | **+0.03608%** | +0.07932% |
| R438 runner-up layout, local (a) | 0.001734759469354358444809 | +0.03363% | +0.07687% |
| PR1043 in-place hosting, local (b) | 0.001734220472884893243548 | +0.00255% | +0.04577% |
| **R438 window optimum, local (b) transported word** | **0.001734846264120199151475** | **+0.03863%** | +0.08187% |

- Local (a) is `{1:1321, 2:1344, 3:78, 4:44, 5:102, 6:11, 7:18}`, read from PR1043's certificate.
- Local (b) is `{1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}`, a declared input; see Scope.
- Both scouting endpoints (0.001734802047828389852783 and 0.001734846264120199151475) are reproduced
  exactly.
- **Optimality certificate.** The DP is re-run at each profile's own next grid point c + 10⁻²⁴.
  There, the moment of the optimum exceeds one, by both engines. Every other no-bank R438 layout has
  a certified larger idle sum Σg, while the child count and local profile stay the same. Its moment is
  therefore larger, so no layout in the slot model reaches c + 10⁻²⁴.
- **Window-free equals window-respecting.** The window-free optimum is window-feasible (below).
  Windows only remove layouts, so it is also the window-respecting optimum.

## What `verify_rehost.py` checks

1. **Bindings and positive controls.**
   - The PR589 record and the PR1023 slot model are used through `packing.slot_model`.
   - PR589's c is reproduced.
   - PR1043's certificate is checked: its baseline equals the PR589 record, and the local delta is
     `{1:−2, 2:+2, 3:−1, 7:−1}` with mass 5121 = 8R + 63 + 14v.
   - PR1043's nine removed slots and its in-place remainders are **re-derived** from the frozen
     selection with seed14's `allocate`. Its hosted profile and c = 0.001734176288479865766692 are
     reproduced with `packing.endpoint`.
2. **Exact interval DP (S = 54, generalising `width8_optimality`'s hard-coded 45).**
   - It is a top-3 coin-change DP over moves (capacity, unused units u). Move bounds are built from
     `packing.g_interval`, and values are exact rationals.
   - An independent exhaustive enumeration cross-checks it: per-class partition tables, exact integer
     (dyadic) costs, and sorted branch-and-bound over all 10,556,685 layouts. The two must agree on the
     top three.
   - Uniqueness is certified as L(runner-up) > U(optimum). The runner-up is certified as
     L(third) > U(runner-up).
   - Slot-count limits are vacuous because 54 ≤ 444, and every capacity is ≢ 0 (mod 8). Each slot
     therefore keeps exactly one idle child, and the surcharge is the same for every layout.
   - **Positive control at S = 45, c0 + 10⁻²⁴.** The optimum is `9×(42,5)`, which equals PR589's
     selected remainders. The runner-up is `8×(42,5)+(14,1)+(42,4)`, with a gap in Σg of
     0.0188836568544…. PR1023's own `width8_optimality` passes, with per-unit runner-up (42,4).
3. **Stage windows.**
   - Windows come from seed72's `windows.checked_windows` (global_k anchor plus three predicates),
     cross-checked against seed14's independent `schedule/windows`:
     - child 0: stages 0–1; child 2: 0–3; child 4: 0–5;
     - child 6: 3–8; child 7: 5–8; child 8: 7–8;
     - capacity-7 children 1, 3 and 5: one stage each, and they host nothing.
   - All 22 splits of the 11 non-full 42-copies were checked. These are x idle copies in child 4,
     10 − x in child 6, and the one-residual copy in child 4 or 6. Children 0, 2, 7 and 8 stay full.
     The splits are checked with seed72's `maxflow_assign` and an independent all-subsets Hall test.
     **22/22 are feasible.**
4. **Explicit placement.** All 10 idle copies and the one-residual copy go in child 6, as in PR589,
   which leaves 9 child-6 copies empty. The stage table is in the receipt.
   - Seed14's `allocate` is run with R = 438 on the module instance only.
   - Its output must equal PR442's `hosting_core.expand` slot for slot (sha256 `1ef76bb8…`).
   - It is audited by seed14's `placement_audit`, which checks windows, owner domain, width, extent,
     cell collisions, one occurrence per (stage, helper), completeness and the host-pair-not-active
     rule.
   - It is also audited by an independent `audit_slots`, which takes active pairs from seed72's
     schedule. Seed14's `owners_for_replicas` covers all 126,144 roles across 32 replicas.
   - All three remainder histograms equal the DP optimum.

**Negative controls (29, each must be rejected for the stated reason):**
- A tampered vendored certificate (sha256 pin).
- PR1023's `width8_optimality` on the R438 model (hard-coded slack 45).
- The DP with move (42,4) dropped, which fails the exhaustive cross-check.
- The runner-up claimed optimal.
- The PR1043 in-place layout claimed optimal.
- An optimum profile with the 34-slot dropped (rank mass).
- c + 10⁻²⁴ accepted, for (a) and for (b).
- Child 4's window tightened to {0,1}, and child 6's window tightened to {7,8} (Hall violated; max-flow
  agrees).
- 439 helpers per stage into the R438 optimum.
- Placement mutations: stage outside window, cell collision, duplicate helper, missing helper, slot
  extent, helper out of domain, width-7 residual, host pair active at a stage (windows widened so that
  only this rule can fire), and auditing as R439. Each is rejected by both seed14 and the independent
  audit.

## Commands and runtime

From the repository root, after the directory is moved to `research/<slug>/`:

```sh
python3 -I -B research/<slug>/verify_rehost.py --out research/<slug>/RECEIPT.json
python3 -I -B research/<slug>/verify_rehost.py --check research/<slug>/RECEIPT.json
```

From the repository root:

```sh
python3 -I -B research/bit-r438-transport-rehost/verify_rehost.py --check research/bit-r438-transport-rehost/verify_rehost.receipt.json
```

- The last line is `PASS_R438_WINDOW_REHOST S=54 opt=10x(42,5)+1x(42,4) … controls=29 no_new_kappa`.
- `python3 -O` is refused with a `FAIL_` line and exit 2.
- The run takes about 4–7 s, standard library only, on CPython 3.14.4 (Linux x86_64) with no network.
- `--repo` defaults to three `dirname`s above the script, which is the repo root once the script sits
  in `research/<slug>/`. That default was tested in a mock tree.

## Inputs and pins

- **Main-tree files**, read from `--repo`, with sha256 and git-blob pins in `PINS`:
  - `research/bit589-width-packing/packing.py` and `research/bit589-width-packing/SOURCES.json`;
  - the PR589 record `research/e8-bit-p111-tuned/tune/EXPECTED.json` and the frozen selection
    `research/e8-bit-p111-tuned/data/selection9-p111.json`;
  - the three pinned engines in `research/native-complex-moment552/engines/`;
  - seed72's `verify.py`, `wopt.py` and `windows.py`;
  - PR442 `hosting_core.py`, `audit_hosted_k.py` and `global_k.py`;
  - seed14's `verify.py`.
- **Base.** Canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- **Vendored.** `vendor/pr1043/CERTIFICATE.json` is a byte copy from PR1043 head
  `e309e17f83f5759b1ea1fa24a76f24838784cb4d` (sha256 `32c6cd61…`, blob `56400920…`), with a NOTICE.

## Scope: checked and not checked

**Checked.**
- PR1023's slot model: 9 idle children × 222 copies, whole width-8 residuals, no banks, replica-local
  hosting.
- The frozen PR442/PR589 nine-stage recipe and its windows.
- Uniformity across replicas is optimal, because the idle sum is additive over replicas and the
  per-replica optimum is unique.
- The certificate is grid optimality at each profile's own c + 10⁻²⁴.

**Not checked.**
- No hosted template was emitted, and none of the following was rerun: `emit_k`, the full
  `audit_hosted_k` on a template, `assemble9`, or the native, C++ and NumPy pipeline of PR1043. The
  slot-level rules were checked instead.
- Local profile (a) is taken from PR1043's certificate; it is not re-derived from the word here.
- Local profile (b) is a **declared input**: the paid profile of PR1043's word after one A-transport
  (op 2027 → position 154 at frame 79). That move is from the PR1345 move class. This script does not rebuild or replay that word;
  `verify_transport.py` in this package does. Only its rank mass (5121) and child count (2918) are checked.
- Projector compatibility of mixed occupancy (#1307), owner/physical routing beyond the slot audit,
  and the H1–H5 interface were not checked.
- Out of scope: cross-replica owner maps, banks, split residuals and recipe changes.
- All inherited assumptions remain: all-size compilation, common labels and mutable sources,
  whole-call hosting, precision and tape, analytic transfer, and the bad-residue surcharge.

## Open next questions

1. Emit and audit the R438 hosted template with this selection through PR1043's pipeline (emit_k,
   audit_hosted_k, assemble9). That would turn the slot certificate into a complete hosted invoice.
2. Once the transported word (b) is replayed independently, rerun this script with its certified
   local profile.
3. Does the single 34-remainder copy pass #1307's projector check?

## Credits

- **PR1043**, Ali Romman (@aliromman), with OpenAI Codex assistance: the R438 source-boundary word, its
  local profile, `hosting_change` and the endpoint reproduced here.
- **PR1345**, hipotures: the transport atlas move class behind profile (b).
- **PR589, PR510 and PR463**, DreamingOfClouds: the bit word and the nine-stage hosted template.
- **PR555**, eumemic.
- **PR442**, DaysSky: idle-axis hosting and `hosting_core.expand`.
- **PR443/444**, chafreaky: the audit lineage. PR386/436: Zhihao Chen and eumemic.
- **PR1023** (`bit589-width-packing`), Sagar Thakrar: the slot model, `g_interval`, `endpoint` and
  `width8_optimality`.
- **seed72** (`bit589-width7-windows-seed72`), Sagar Thakrar: the checked windows and `maxflow_assign`.
- **seed14** (`bit-helper470-window-placement-seed14`), Hanson Sun (@bbMisk), with OpenAI Codex
  assistance: `allocate`, `placement_audit`, `owners_for_replicas` and the independent
  schedule/windows.
- **PR886** (`bit589-frame-optimum`, frameopt), SethBurkart123: the fixed-word frame optimum, context
  for bit-word optimality.
- PR1256, Ross Richardson: helper470 retirement context.
- The retained moment-engine authors.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via
Claude Code. Scouting and implementation were AI-assisted; no independent human review is implied.
New material is Apache-2.0.
