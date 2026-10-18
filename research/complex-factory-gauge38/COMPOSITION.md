# PR922 and PR924 compose: 32 macros, 73 PR696 primitives

**Verified finite construction. No new κ.** At @CubeJerry's request, this
follow-up combines the two pinned contributions and compares all four cases
with fresh full raw-factory/native/primitive replays. Moving the doublings and
contracting the triples in either order yields the same literal circuit.

| Construction | Macros per block | Original Horner per real component | PR696 per real component | Full PR696 forward | Full PR696 backward |
| --- | ---: | ---: | ---: | ---: | ---: |
| PR681 baseline | 34 | 128 | 81 | 123,768 | 123,784 |
| PR922 alone | 32 | 120 | 77 | 123,544 | 123,560 |
| PR924 alone | 34 | 126 | 77 | 123,544 | 123,560 |
| Both | **32** | **118** | **73** | **123,320** | **123,336** |

Thus the combined block costs `4/77 = 5.1948%` fewer PR696 primitives than
either standalone block. The full forward raw program costs
`224/123544 = 0.181312%` fewer primitives than either standalone program.
These are operation counts, **not measured runtime speedups**. Each orientation
saves 448 primitives against the shared baseline, or 224 beyond either PR.
Original-Horner savings against baseline are 560 per orientation; these are
an alternative lowering, not an additional saving to add to 448.

## Exact compatibility argument

Use immutable labels from the original 34-gate PR681 word, before any edits.
PR922 contracts triples with labels `(0,1,2)` and `(13,14,17)` to their last
and middle members, in that order. The verifier checks each exact triple/pair
map and every crossed gate's commutation condition. It also reconstructs these
labels directly from PR922's sequential splice recipe and reproduces its
literal witness, so changed array positions are not mistaken for gate labels.

PR924 delays label 16 (doubling register 0) until label 31 and label 22
(doubling register 1) until label 32. It changes label 26's coefficient from
2 to 1 and label 30's coefficient from -1/2 to -1. The first contraction is
earlier than these changes. The second contraction acts on registers 2, 5 and
6, so crossing the register-0 doubling is unaffected by delaying it. The other
rescaling edits are later. Neither contraction deletes a moved doubling, its
destination site, or an adjusted-coefficient gate.

The checker constructs `rescale(fuse(original))` and
`fuse(rescale(original))` and requires literal equality, including labels and
frames. It then checks complete maps, positive-envelope admission and literal
primitive replay in main, cleanup, inverse-transpose and dual-cleanup
orientations, with arbitrary data and coefficient-work inputs. It separately
checks that rescaling is admitted relative to the already-fused word.

All fourteen physical windows are freshly bound to the raw PR622 constructor.
Each full word is rebuilt, including the literal inverse cleanup. The combined
PR696 saving is `14 windows * 2 (main/cleanup) * 2 real components * 8 = 448`.
All remaining source accesses, coefficient work, restores and child calls are
still charged.

## Complete local accounting and precision

The combination preserves PR922's 15,456 emitted scalar macros, 492 helpers,
716 logical registers, eight centers, 3,472 recursive children and paid profile.
Its adapter allowance is 319,104, versus the baseline's 320,000. Under the same
retained local formula used by PR924, `C = 64*74^3 = 25,934,336` and
`A = 16*(macros + children + registers + centers) + 64*73`:

| Construction | Adapter allowance | Local PR696 bound |
| --- | ---: | ---: |
| Baseline | 320,000 | 8,298,987,643,784 |
| PR922 | 319,104 | 8,275,750,478,504 |
| PR924 | 320,000 | 8,298,987,643,560 |
| Both | 319,104 | **8,275,750,478,280** |

The combination is 224 below PR922, 23,237,165,280 below PR924, and
23,237,165,504 below baseline. Most of the latter reduction is the conservative
adapter charge already removed by PR922. This is an exact local recount, not
a global invoice replay or a prediction of runtime.

The combined positive prefix bounds remain PR922's **39,090 / 1,301,331**.
Exact primitive prefix row-l1 maxima remain **124 / 107**, and fractional depth
remains two bits. The inherited precision allocation and recursive profile
are unchanged. PR924's 67-primitive optimum concerns its original fixed
28-addition topology; it is not an optimality claim for this 26-addition word.

## Reproduction and controls

From the repository root, standard-library Python:

```sh
python3 -I -B research/complex-factory-gauge38/compose_pr922.py
```

Expected final line:

```text
PASS_FACTORY_PR922_PR924_COMPOSITION macros=32 primitives=73 blocks=14 saved=448,448 extra_vs_each=224,224 controls=38 no_new_kappa
```

This compares every deterministic field with `COMPOSITION-RESULT.json`.
The eight complete primitive projections each cover 725 arbitrary input
columns, including all 492 helpers, eight private centers and coefficient work.
The fresh baseline and PR924 records must exactly match the pinned PR924
receipt. The fresh PR922 native record was also compared with PR922's retained
`RESULT.json` at its pinned head and matched exactly; that one-time comparison
does not introduce another runtime dependency.

The 38 local rejection controls delete each of the 32 combined gates, and
reject a Boolean coefficient, wrong frame, wrong rescaled sign, wrong fusion
order, endpoint-neutral extra cost and omitted private-work clears. A full
missing-cleanup mutation must fail in the unchanged native checker. Four
inherited native controls also run for each of the four complete words.

`python3 -I -B research/complex-factory-gauge38/test_composition.py` checks a
full optimized replay from a minimal offline checkout with spaces, no Git
metadata and repacked gzip inputs, plus source corruption, missing dependencies,
malformed witnesses, underpriced receipts and existing-output preservation.
Normal reproduction needs no solver, network or PR922 checkout. `--local-only`
explicitly skips full reconstruction; `--out` and `--write` require new paths.

## Pins, scope and attribution

Follow-up base and original PR924 head:
`e6f3cb8ca813dfc54c77738c9acd74a536b607fd`.
PR922 head: `efd5643c0016b6c6dac26e9ed7dee8a75295ff2a`.
Shared research base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.

`PR922-CIRCUIT.json` is a byte-identical copy of PR922's circuit certificate.
`COMPOSITION.json` pins that file and the four consumed PR924 files; the
unchanged `SOURCE-PINS.json` covers the sixteen shared predecessor inputs.
Source authors and notices are preserved. The adapted fusion admission credits
PR922, and the exact primitive interpreter/native pipeline credits PR924,
Alluri's PR681, Sagar Thakrar's PR696 and the PR622/626 source lineage.

This is a direct, deterministic composition, not a new search or optimality
claim. It completes the compatibility test that the original PR924 handoff
left open. Both source PRs are by @CubeJerry with substantial OpenAI Codex
assistance; neither standalone improvement is claimed again as new.

The scope remains the historical raw factory. The selected X4 supplier, later
provider recipes, phase lowering, whole-owner hosting, global invoice and
outer assembly are not rebuilt. Uniform compilation, realization, recursive
precision/tape and analytic assumptions remain inherited. **No new κ**;
the selected conditional value remains **0.001661634653669567**. No full
`make verify`, selected frontier799 cold replay, Lean or remote CI is claimed.

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance in
analysis, implementation, verification and writing. Apache-2.0. No independent
human or delegated-agent review is claimed.
