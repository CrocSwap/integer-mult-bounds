# Eleven-stage cross-copy hosting with target mixing: κ = 1.347745·10⁻³ (+1.278% over #448)

Conditional **κ = 269548909542967/(2·10¹⁷) ≈ 1.347744547714835·10⁻³**, **+1.2783% over PR #448** (1.330733966732373·10⁻³).
The bit supplier binds, at **c = 1.349563·10⁻³** (+1.28% over #448's 1.332507·10⁻³); PR #448's complex supplier
(b = 1.437532·10⁻³, nine stages) has 6.5% of room.

| bit word | stages | hosting | max child | bit c (·10⁻³) | κ (·10⁻³) | over #448 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| #448 (R747 word, reference) | 9 | cross-copy | 24 | 1.332507 | 1.330734 | 0 |
| unmixed (`stacked_unmixed`) | 11 | cross-copy | 56 | 1.340476 | 1.338682 | +0.597% |
| **target-mixed (`stacked_mixed`, default)** | **11** | cross-copy | 56 | **1.349563** | **1.347745** | **+1.278%** |

Three levers stack. (1) PR #448's cross-copy idle-axis hosting; (2) the compressed eleven-stage window (m = 78; also PR #445
and #447), where the idle pairs offer 73,920 pending coordinates per replica against 63,602 residual coordinates, so
**all** 8,140 helper residuals are hosted (1,807 of them across two copies of one idle child), no bank remains and the
live stock is the data alone, 1,200 families; (3) F2 target mixing on the R740 word (46 receivers, target climb −0.72%
per invocation, R = 740 unchanged). The cross-copy tape rule leaves only 184 untouched copies of the rank-56 children and
one rank-14 child as idle remainders.

## Reproduce

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
export CXX=g++ BOOST_INCLUDE=/usr/include        # a C++17 compiler and Boost headers, as for PR #443
python -B research/e8-eleven-stage-cross-copy/verify.py /absolute/new/output [--quick] [--no-anchor] [--discover-check]
```

The script runs PR #443's and PR #448's verifiers unchanged, regenerates the nine-stage anchors (PR #443's template and PR #448's
bit template byte for byte, PR #448's result key by key), then builds, audits and prices the eleven-stage suppliers for the
unmixed and the target-mixed word. `RECEIPT.json` records the compiler version and every step; `EXPECTED.json` holds the pinned
values; `SOURCE.json` the pins of the three upstream packages and of the derived code.

## Files

- `code/geometry_k.py`, `code/global_k.py`: PR #386's geometry and PR #443's template for any odd stage count.
- `code/hosting_k.py`, `code/emit_tape_k.py`: PR #448's tape hosting for any odd stage count, with `--host-all`, `--depth`, `--redigest`.
- `code/audit_parent_k.py`, `code/audit_tape_k.py`: independent audits (15 and 20 mutation controls at eleven stages, 22 for the nine-stage anchor).
- `code/assemble_k.py`: two moments, finite invoices and the strict outer assembly at any depth, row allowance and route-factor count.
- `code/mix_target.py`, `code/mix_check.py`, `BIT-LABEL-LEMMA.md`: target mixing, its four mutants and the lemma (principal review point).
- `data/selection.json`: the frozen tape-hosting selection.

## Scope

Conditional, like its parents. Principal review points: Lemma M of `PROOF.md` (target-to-target adds at a common frame, which
extends PR #425's lemma to the F2 bit word); PR #448's cross-copy hosting lemma now applied to every residual; the compressed
window at eleven stages (checked finitely, not proved); three-level halving and a row allowance of 28,416. No Lean proof and
no unconditional integer-multiplication theorem is claimed.
