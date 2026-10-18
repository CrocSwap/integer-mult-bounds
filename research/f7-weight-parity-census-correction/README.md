# Correct the word-census parity budget; exclude length 20 at seven labels

The word-census engines retained by PR2542, PR2634 and PR2691 classify prefix
states by coordinate bit 0 but apply a collision budget calculated for the
Hamming-weight split. That rule can reject universal words. This package
demonstrates the error, supplies a corrected revisit-aware C census, and
completes every admissible length-20 weight split with zero universal words.

Within **PR943's abstract singleton prefix-walk model**, the corrected finite
exclusion and padding argument give **`22 <= f(7) <= 24`**, hence
`f(7) in {22,24}`. This is a computational exclusion with a written pruning
proof and independent controls. It does not change a supplier, tariff, kappa,
or the selected multiplication result; it is not a formal-kernel proof.

Contributor: Nicholas Stone, with substantial OpenAI Codex assistance,
including three complementary agents for implementation, independent validation
and mathematical/source-impact review. No independent human review claimed.
Base: `a23bdc1b07be96bea0101d44ae27d14de67a79ed`, priority revision 5.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2691#issuecomment-6218443989)
and [coordination pointer](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18976359).

## The error and its correction

For a closed word of even length `L`, weight parity alternates with time;
there are at most `L/2` distinct states of each weight parity. The sizes of
the bit-0 classes have no such bound. In dimension four, the canonical
simple restored word `01021323` has eight distinct prefix states and covers
all sixteen XOR masks. Its weight split is `(4,4)`, its bit-0 split `(6,2)`.
Its bit-0 collision excess is 8, exceeding the wrongly substituted balanced
budget 5; the valid actual-size bit-0 budget is 9. This disproves the generic
old prune, including within simple balanced walks, without asserting a
seven-dimensional counterexample.

The corrected engine always uses distinct **weight-parity** sets `E,O`.
For target sizes `s,t`, universality necessarily implies

```
within_E_excess + within_O_excess <= C(s,2)+C(t,2)-63
cross_excess <= s*t-64
```

Both excess counts are monotone under addition of a new distinct state;
revisits add nothing. The last step closes the walk and does not add an
extra prefix point. See [MATH.md](MATH.md) for proofs, the exact split
classification, rotation symmetry, padding, and the correction to the earlier
session's overstatement about "zero slack". Bit 0 itself remains a valid
linear functional in a set-level enumeration using its actual class sizes.

## Complete corrected enumeration

Each row is one complete restricted-growth traversal from the empty prefix,
with both necessary budgets enabled, no node cap, process exit 0 and
`complete=true`. No self-avoidance condition is imposed on repeated-state
splits. Mirrored splits follow by cyclic rotation and coordinate relabeling.

| Length | Weight split | Nodes | Universal words |
|---:|---|---:|---:|
| 20 | `(10,10)` | 590,371,593 | 0 |
| 20 | `(10,9)` | 244,301,902 | 0 |
| 20 | `(10,8)` | 14,450,133 | 0 |
| 20 | `(9,9)` | 67,643,567 | 0 |
| 20 | `(10,7)` | 35,241 | 0 |
| 18 | `(9,9)` | 951,416 | 0 |

All rows have zero candidate restored leaves: the two necessary budgets
exclude every branch before a qualifying leaf survives. This is **not** a
count of all restored words or all simple cycles. The old 6,305,209,079-node
receipt uses different, unsound filtering and is preserved only as history.

[engine/SUMMARIES.json](engine/SUMMARIES.json) binds the C source, commands,
environment and all six complete receipts. Fresh enumeration took about
63 seconds in total on the recorded Apple arm64 host; compiler and host
affect runtime, not the exact counts. The extra length-18 row repairs that
specific predecessor evidence. The new lower bound needs only the five
length-20 exclusions: a shorter restored universal word could be padded to
length 20 by appending repeated pairs of an existing label.

The existing reflected-Gray length-24 construction is retained as the explicit
word `010201030102010345464546` in [UPPER-WITNESS.json](UPPER-WITNESS.json).
The verifier checks its restoration and all 128 XOR masks directly.

## Reproduce

Python 3.12 standard library and a C11 compiler supporting `unsigned __int128`
(Clang or GCC) are required. Run from the repository root:

```sh
python3 -I -B research/f7-weight-parity-census-correction/verify.py
python3 -I -B research/f7-weight-parity-census-correction/verify.py --full
python3 scripts/research_package.py --package research/f7-weight-parity-census-correction --check-only
```

Quick mode freshly checks the mathematical controls, 164 small full-domain
C/brute comparisons (three `(n,L)` cases, every split, four budget modes),
12 input/cap/output controls, and 36 capped n=7 C/Python comparisons.
The independent Python implementation recomputes pair supports from scratch,
rather than copying the C bitsets and incremental collision counters.
Quick mode also validates stored-receipt integrity and the explicit upper
witness. Its marker is `PASS_F7_WEIGHT_PARITY_QUICK`; it does **not** claim
a fresh full n=7 enumeration.

Full mode performs those checks, compiles the source afresh, and reruns all
six complete cases, comparing exact non-timing fields. Its marker is
`PASS_F7_WEIGHT_PARITY_FULL fresh_six_case_census universal_words=0 f7_lower=22 f7_upper=24`.
All generated files use temporary directories. Aborted/capped searches
return a different exit status and are not accepted as exclusions.
See [validation/REVIEW.md](validation/REVIEW.md) and
[engine/README.md](engine/README.md) for the component audits and direct CLI.

## Historical scope and credit

Frozen predecessor packages are unchanged. Their receipts can reproduce the
old traversal, but cannot justify its pruning premise. This package supersedes
their word-census exclusion evidence within the stated domain. Later set-level
work #2773/#2870/#2911/#2933/#2961 has separate hypotheses and is not broadly
revoked; exact source heads and effects are recorded in
[math/SOURCES.json](math/SOURCES.json) and MATH.md.

Credit: Ross Richardson (PR943 model); Douglas Colkitt (PR1185 five/six-source
record); Aaron Wang with opencode (PR2542/PR2634 word model, census design,
Gray construction and the later set-level chain); Nicholas Stone (PR2691's
independent C implementation and this corrective continuation). The new C
engine derives from the prior local revisit extension and PR2691-style
restricted-growth enumeration; the validation and mathematical scripts use
separate direct computations. Apache-2.0.

## Open next questions

1. Does a restored universal length-22 seven-label word exist? Derive and
   audit its complete split domain before a bounded search. This session
   makes no length-22 exclusion.
2. Can a separate implementation replay the entire n=7 length-20 exclusion?
   The present independent controls cover small full domains and capped n=7
   traversals; the complete n=7 replay uses this C implementation.

Structured next steps and blockers are in [TASK.json](TASK.json).
