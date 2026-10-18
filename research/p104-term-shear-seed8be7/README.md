# Bounded term-basis shears do not improve the P104 delivery budget

**Scoped negative result. No physical supplier, new κ, or universal obstruction is claimed.**

This package tests whether elementary changes to the eight rank-one factors of PR717's exact P104 decoder can retain the 56-copy cost while changing its support endpoints. The tested object is pinned to PR717's `P104_HIT_flip_3a.txt` (PR717 head `4a97676294f9fa413b65986e9984fddeda71e4cc`, vendored SHA-256 `8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526`). The exact base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

## Result

The original P104 decoder has eight terms of support-pair rank 7, so `cst=56`. Under the retained 104-port, nine-stage coverage model, its favorable local-word ceiling is bracketed by

```text
1781965480167/10^15 <= a <= 222745685021/125000000000000
```

or approximately `0.001781965480167..0.001781965480168`. The selected fixed-word ceiling is `0.001690054109089`; the P104 relaxation is 1.05438 times that value. The task's 5% acceptance target is `a = 0.00177455681454345`.

The exact finite results are:

| Search | Cases | Copy-cost result |
|---|---:|---|
| One elementary shear, all 56 ordered term pairs and seven support classes | 392 | Every case has six rank-7 terms and two rank-8 terms; `cst=58` |
| Two shears whose ordered term-pair edges touch | 71,344 | 336 `cst=56` cases, all inverse moves restoring the original factors; no `cst=57` case; all other cases have `cst` 58, 59 or 60 |

The exact `cst=58` one-shear profile has ceiling bracket `[0.001684267614920, 0.001684267614921]`, below the selected fixed-word ceiling, even before actual delivery costs. More generally, exact dynamic programming over all eight-term rank profiles with each rank in `0..9` gives the most favorable possible moment at the 5% target:

| Total term rank | Most favorable rank tuple | Lower moment bound | Result |
|---:|---|---:|---|
| 56 | `(0,2,9,9,9,9,9,9)` | `0.9999745535...` | Possible under the relaxed moment; the original decoder has this total |
| 57 | `(0,3,9,9,9,9,9,9)` | `1.0001233630...` | Fails |
| 58 | `(0,4,9,9,9,9,9,9)` | `1.0002720827...` | Fails |

Rank zero is allowed in this optimization, making the bounds favorable to a changed decoder. Every factor support lies in a label space of dimension at most 9. Since each child's moment is strictly increasing with its rank, every total above 57 also fails once the `cst=57` minimum is above 1. Thus the only passing cases in the two-shear screen are the 336 inverse moves, which do not change the original decoder or its delivery problem.

The bounded result does not cover products of three or more shears, arbitrary changes of basis in `GL(8,Q)`, other P104 decoders, or new decoder terms. It does not construct a delivery schedule or replay dirty-state restoration. PR1071's 47-copy lower bound applies to the unchanged pinned decoder; the present screen rules out a nontrivial passing endpoint basis within its stated finite domain before that physical question is reached.

## Cost screen and accounting

The P104 profile is derived from the selected profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` using PR717's per-port knob. Removing eight ports subtracts eight copies of `{1:7, 4:1, 5:1}`; the decoder centre changes from eight rank-8 terms to eight rank-7 terms. This gives local profile `{1:2356, 2:418, 3:432, 4:134, 5:74, 7:8}`, 104 ports, 832 live families per replica, nine stages, centre charge 56, and idle rank cap 51. The selected and P104 ceiling values are recomputed with the pinned `complex-local-word-ceiling/ceiling.py` model.

The screen charges each changed decoder support-pair rank in the local profile and applies the unchanged coverage identity and outer rank guard. It optimistically waives any new delivery copies, frame transitions, restoration, hosting, precision and interface costs. Since every nontrivial bounded candidate already fails the local moment target under this favorable relaxation, none can become a construction by adding those costs. No κ or selected-result change follows.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -I -B research/p104-term-shear-seed8be7/verify.py
python3.12 scripts/research_package.py --package research/p104-term-shear-seed8be7 --check-only
```

The verifier checks the original 104×104 decoder identity, enumerates all 392 one-shear cases and 71,344 touching two-shear paths, validates inverse restoration for every `cst=56` case, performs the exact rank-profile moment screen, rejects a corrupted-factor control, and compares its output with `RESULT.json`. The two-shear search transcript hash is `c01fc64e1bc3e7372771bf766ce8fbc7f69902204571bb3a16496b4d64c24fb4`.

## Predecessors and limits

PR717 supplies the exact P104 hit. PR968 identifies the frame-pair decoder and the 56-copy floor. PR1071 bounds delivery for the pinned decoder, and PR1125 extends that delivery analysis across the frame-pair family while holding term supports fixed. PR1240 supplies the local packing-ceiling method. Open PR1619 prices port count and puncture depth under that model; this package recomputes its P104 screen from the pinned selected local profile and ceiling engine. These works motivate the scope and retain their original attribution.

This is a finite computational result with a direct algebraic proof that each elementary shear preserves `D T^T`: `D'=D(I+λEᵢⱼ)` and `T'=T(I−λEⱼᵢ)` imply `D'T'ᵀ=DTᵀ`. The package uses the predecessor's exact E8 line/label model and the pinned ceiling engine. No independent human review, hosted CI pass, full supplier replay, Lean result, or formal proof of the overall multiplication theorem is claimed.

## Open next questions

- Can a product of three or more elementary shears give a nontrivial `cst=56` P104 factorization with different endpoint supports? First derive a target-specific moment bound and support-cancellation alphabet before searching.
- Do other P104 frame-pair decoders admit a `cst=56` term basis with a cheaper physical delivery schedule? The 7,168-decoder family and its delivery constraints are covered by PR1125 only with original term supports fixed.

## Credit

Credit PR717 for the exact decoder input; PR968 for the frame-pair mechanism and copy floor; PR1071 and PR1125 for delivery-cost bounds; and PR1240 for the local ceiling model. Prepared with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
