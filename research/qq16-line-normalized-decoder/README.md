# Zero-retention QQ16 decoding with paid line normalizations

This implements PR2681's same logical decoder with **336 positive rank-one
children and no rank-eight children**. Its published two-chart implementation
uses 112 rank-one and 448 rank-eight children. A source-exact change of the
intermediate physical frame replaces those 448 upgrades/downgrades with 224
charged rank-one normalizations. All 224 original logical arrays still return
in F17, all 224 current borrowed arrays remain untouched, and no value is
retained across B1.

The new step is the dynamic frame identity at every one of the 112 actual
ports. The stage-2 route, with an explicitly computed affine translation,
takes F17 to `F16 C_q`, where F16 uses address axes 9 through 24. A paid
`C_q^-1` places the row in the common F16 frame for the query. A paid `C_q`
and inverse affine map restore F17. The complete word and each native child
occurrence are checked; the old scalar schedule is preserved.

Full-current invertibility, the logical inverse and the scalar word are
credited to [Arham Tahir's PR2681](https://github.com/CrocSwap/integer-mult-bounds/pull/2681)
at `ea96706295631be10d92ae149b63c3e24acaeabc`, which answers
[PR2540's comparison question](https://github.com/CrocSwap/integer-mult-bounds/pull/2540).
They are not claimed as new. The retained checker supplies the authenticated
source reconstruction and routed algebra. [PROOF.md](PROOF.md) proves the new
frame identity, complete word refinement and exact child-moment comparison.

| Added local charge | PR2540 | PR2681 | This word |
|---|---:|---:|---:|
| Values retained across B1 | 16 | 0 | 0 |
| Positive rank-one children | 224 | 112 | 336 |
| Positive rank-eight children | 16 | 448 | 0 |
| Native rank mass | 352 | 3696 | 336 |
| Native monomial wrappers | 480 | 1120 | 672 |
| Full-cover maps | 208 | 464 | 464 |
| Real scalar primitive allowance | 17472 | 25840 | 25840 |
| Owned eventual outputs | 224 | 224 | 224 |
| Peak owned local scratch | 16 | 16 | 16 |

Against PR2540, the child-moment difference has numerator
`112 - 16*8^(1-a)`, strictly negative for `0 <= a <= 1/16`. The proof uses
the exact integer inequality `8^15 > 7^16`. **This is a child-cost comparison**:
the extra 192 wrappers, 256 maps and 8,368 scalar allowance remain liabilities.
Physical placement, movement, precision and a complete consumer invoice are
unknown. The newer PR2651 output-bank coalescing retains sixteen early values
without a separate bank; this result uses no early values at all.

## Exact evidence

The 3,823-event [WORD.json](WORD.json) has 336 line children, 464 cover maps,
1,808 unit ADDs, 896 quarter ADDs and 312 CLEARs. All 224 input-array operators
pass both inverse orders; the intermediate inverse-B1 checkpoint, arbitrary
owned dirt, actual scalar frames, borrowed restoration and scratch disposal
are checked. The output operator digest equals the exact retained predecessor.

The new physical evidence checks:

- Full phase-polynomial entry and exit identities at all 112 ports for both
  stages, plus 1,210,496 separate literal character equalities determining
  those degree-two phase polynomials on the full 73-coordinate space.
- All 114,688 signed rank-one basis columns, including Gaussian coefficients,
  global phase, negative-child XOR wrappers and all 336 literal occurrences.
- Eleven semantic controls covering missing/wrong line normalization, wrong
  normal, old frame shifts, wrong inverse shifts, failed restoration, owned
  dirt, borrowed writes, scratch leaks, an inverse sign and a native wrapper.

```sh
python3.12 -I -O -B research/qq16-line-normalized-decoder/verify.py
python3.12 -B scripts/research_package.py --package research/qq16-line-normalized-decoder
```

The default replay is read-only. `--write` requires both output receipts to be
absent. Sources are authenticated with SHA-256 and Git blobs before compiling
the captured predecessor verifier bytes; no imported `.pyc` is trusted.
The predecessor's unchanged code, word, receipt and notices are retained in
`vendor/pr2681/`, with complete pins in [PREDECESSORS.json](PREDECESSORS.json).
Main scientific inputs are pinned in [SOURCES.json](SOURCES.json). A Git-free
export is supported with those exact files.

## Scope and expansion decision

Milestone: **local module**. This is a changed physical implementation of one
completed finite decoder. The favorable child moment reopens PR2681's local
cost decision; it does not admit a complete supplier. The full inherited
F0/B1 calls, all affine map and wrapper work, storage/ownership, rounded
precision and output consumer remain separate paid obligations. Native line
identities are ideal exact operators in the existing finite Gaussian-dyadic
alphabet; they do not prove a rounded strict-zero or physical tape contract.
No selected frontier, new kappa, optimality, formal-kernel or human-review
claim is made.

The verifier-engineering picker was preserved; TASK.json records the bounded
pivot after nearby acceptance audits were already covered. Canonical main
advanced to `1884c509efc004524786e9b7cfcc4aca572316d5` before this construction;
revision-5 guidance and the selected record were unchanged. The canonical
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2681#issuecomment-6198194973)
records the source, boundary, comparison and stopping condition. Do not expand
without a pinned consumer and favorable complete physical allowance.

## Open next questions

1. Can an actual caller host the extra affine maps and wrappers, with all
   movement, control and precision charges, within the child saving? Pin its
   owner and output-consumer contracts before attempting that comparison.
2. What precision suffices for this changed literal word under that caller's
   completed-child error contract? Existing bounds for different words do not
   transfer merely because their ideal endpoints agree.

Credit Arham Tahir/PR2681, ywz65/PR2540, Ali Romman and the QQ16 contributors,
starship-s/PR2443, thakrarsagar/PR2470, Ross Richardson/PR2480, and the retained
PR2456/2468/2492/2512 source/native lineage. New work by ywz65 with substantial
OpenAI Codex assistance. Apache-2.0. Validation and independent agent review
are recorded in TASK.json; neither is independent human review.
