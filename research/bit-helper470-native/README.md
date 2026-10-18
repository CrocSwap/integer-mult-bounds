# Native replay of helper470's early-retirement endpoint

**Independent finite verification and scoped endpoint result; no new kappa.**
Ross Richardson's [PR1256](https://github.com/CrocSwap/integer-mult-bounds/pull/1256)
explicitly leaves native five/nine/eleven-stage replay open. Its exact frozen
patch passes the unchanged native record-geometry checker and all three bridged
F2 scalar-column checkers. Its conservative forward/reverse bounds remain
**49,347 / 1,113,070**, so the local and nine-stage bounds remain **93 / 177 bits**,
strictly below the inherited **104 / 192-bit** charges.

The original owning full-word checker still rejects its rank-seven helper
endpoint. Adding the rank-one MOVE needed to reach the old full endpoint
eliminates the rank-mass saving and strictly increases the raw child moment for
every `0 < a < 1`. Literal H4 remains false even after that MOVE. These are two
separate obligations; the successful staged scalar replay does not settle them.

## Frozen object and complete local invoice

Base: `bdd4c63ac7c5d8a46ce070ba133df8d7ba9cb92c`.
PR1256 predecessor: `d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`.
The input is the selected PR589-on-PR555 R439 word, from PR589 head
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`. At the base, the selected assembly is
PR1094, conditional `kappa = 836330098538459/500000000000000000`, and the complex
supplier binds. [SOURCES.json](SOURCES.json) has exact live-input Git/SHA256 pins
and the predecessor document hashes. No predecessor executable is imported.

After the original scatter, insert `470 ^= 77` at frame186, followed by
`444 ^= 470` and `475 ^= 470` at frame513. In C replace gate580's donor470 with77
and omit gate2343 (`470 ^= 77`). The generator checks both original instructions
before replacing them. This is **PR1256's circuit**, independently reconstructed.
The third word adds only the terminal MOVE from513 to FULL=1.

| Complete local bill | PR589 baseline | PR1256 rank-seven | With full-frame closure |
|---|---:|---:|---:|
| ADDs, including scatter | 24,305 | 24,307 | 24,307 |
| MOVEs | 2,911 | 2,912 | 2,913 |
| COPY / ERASE | 9 / 9 | 9 / 9 | 9 / 9 |
| Records | 27,234 | 27,237 | 27,238 |
| Paid children, including COPY | 2,920 | 2,921 | 2,922 |
| Paid rank mass | 5,129 | 5,128 | 5,129 |

All nine COPY ranks remain seven. The other 660 registers' entire ordered MOVE
itineraries remain identical. Helper470's ranks become `0,1,2,7` or `0,1,2,7,8`,
instead of `0,1,8`. Every preparation, source access, restoration, copy and final
frame transition in these words is included; this is a local invoice, not an
emitted hosted-supplier bill.

## Why ordinary full-frame closure cannot improve this profile

Relative to the baseline, the exact raw child histograms change by

```
rank-seven endpoint:   +H1 + H5 - H7
full-frame closure:  +2H1 + H5 - H7
```

For the closure, set `p = 1-a`, with `0<p<1`. Its unnormalized moment change is
`2 + 5^p - 7^p`. Since `u^p > u` for `0<u<1`,

`2(1/7)^p + (5/7)^p > 2/7 + 5/7 = 1`.

Multiplying by `7^p` proves the change is strictly positive. Any unchanged
positive normalization preserves the sign. At `a=0`, the rank-mass change is
zero. Thus this exact closure cannot improve the rank moment under the same
host allocation with other terms fixed; extra nonnegative charges cannot help.
This is a proof for this profile, not a general early-retirement impossibility
theorem or a comparison with alternative helper deletion or hosting mechanisms.

The pinned owning checker rejects the unclosed word with exactly
`helper final frame is not full`. The source-bound parent `global_k.py` likewise
contains `all(dims[final[i]] == H for i in range(2*V, LOCAL))`; the punctured
adapter retains that condition. The full hosted parent was **not** executed.
With closure, the owning full scalar/frame check passes, and its separate H4
flag still fails because C is not the literal reverse of the modified A/B word.
The semantic `U`, `J=I`, `K=D`, `C=U^-1` checks pass for both modified words.

## Reproduce

Python 3.12+, a C++17 compiler and Boost headers suffice for the complete replay:

```sh
BOOST_INCLUDE=/path/containing/boost python3 -I -B research/bit-helper470-native/verify.py
```

Expected last line:

```text
PASS_HELPER470_NATIVE stages=5,9,11 words=3 retired_mass=5128 closed_mass=5129 H4_open no_new_kappa
```

`CXX` accepts a compiler command. `--output NEW_DIRECTORY` retains words, raw
records, native receipts and fault logs; an existing directory is refused.
The default uses a temporary directory. The verifier compares every field of
[CERTIFICATE.json](CERTIFICATE.json), excluding only native elapsed time and the
temporary scalar-stream path. Histograms are losslessly normalized from JSON
pair arrays. Regenerated words are compared by their full canonical JSON hash;
the immutable input archive retains its exact byte hash.

For the registered fast scalar/interface checks (which make no native claim):

```sh
python3.12 scripts/research_package.py --package research/bit-helper470-native
```

The dedicated [native workflow](../../.github/workflows/bit-helper470-native.yml)
installs Boost and runs the complete command. Hosted CI status is separate from
completed local checks. [VALIDATION.md](VALIDATION.md) records the local compiler
commands, environment and prerequisite failures.

## Coverage and remaining obligations

Each word covers **661 arbitrary dirty local input columns**. Fresh native
five/nine/eleven-stage checks cover **883 / 1,327 / 1,549** formal columns, all
local ADDs, nine fresh copies per stage, and **666 / 1,998 / 2,664** bridge ADDs.
Across three words, **144 omitted-bridge controls** reject. Eight additional
on-disk native controls reject missing retirement gates, a wrong cleanup donor,
an illegal frame, an underpriced or omitted terminal MOVE, and an underpriced
COPY. The last four still pass scalar columns, demonstrating why a scalar
receipt alone is insufficient. Eight package tests exercise dirty-input
restoration, source corruption, pinned operands and the terminal-frame charge.

The inherited native legality receipt emits a `nondegeneracy_checked_by_separate_exact_bank_audit`
flag; that flag is **not evidence this package ran a bank audit**. Here the
selection/owner fixtures are empty. Whole-owner hosting, bank nondegeneracy,
actual projector routing, changed terminal/complement interfaces, complete
packed precision/tape and analytic transfer remain unrun or assumed. The
five/nine/eleven scalar checks do not certify reverse geometric routing. The
eleven-stage generic bridged coefficient expression is reported only as a
local bound; the separate hosted eleven-stage invoice is not reproduced.
No selected cold replay, full `make verify`, Lean multiplication theorem or
new supplier endpoint is claimed.

## Open next questions

1. Can the `0,79,186,513` terminal-frame path legally fit one actual rank-seven
   idle window, including its reverse complement and pending source access?
   Start with PR1256's proposed two-slot placement and an emitted owner/window
   fixture; the current full-helper parent contract and H4 adaptation block
   adoption. Adding the ordinary full-frame MOVE cannot substitute for this.
2. Can a precise terminal-aware semantic cleanup lemma replace literal H4 while
   retaining the recursive projector and signed-lift contracts? Start with the
   passing `C=U^-1` rows and explicitly state the helper's exit representation;
   physical routing and all-size transfer are the remaining blockers.

The structured questions, three candidate tasks, seed12 assignment, stopping
rule and overlap inventory are in [TASK.json](TASK.json). This has a changed
scope from the catalogue's H2/K card, because that question was already covered
by PR1194 and active discussion1290. PR1271 examines other B cuts; this package
adds the explicitly missing native replay and closure cost for PR1256's fixed
word. No synthesis search or wider optimality claim is made.

## Credit

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** in reasoning, code, checks and writing. One parent agent worked on
this contribution; separate source checkers are not independent human review.
New material is Apache-2.0.

Credit **Ross Richardson / PR1256** for the retirement circuit, its exact finite
invoice and open native-admission question; **Ali Romman / PR1128 and PR1043**
for boundary conditions and the earlier, distinct helper470 deletion with a
hosted invoice; **Sagar Thakrar / PR1023** for the width-seven hosting incentive;
and **Adam Gall / PR1179** for the separate kernel-entrance mechanism. This is
not an improvement over PR1043 or a composition with PR1179. DreamingOfClouds
/ PR589, eumemic / PR555 and PR543, Dylan Crow's native/exporter lineage,
DaysSky's bridged checker, Zhihao Chen's geometry and their preserved notices
remain credited. The harness pattern follows Sagar Thakrar's PR708 native replay
and Gareth Davidson's R439 prefix-verification packages. Frozen inputs,
their licenses/notices and the selected frontier remain unchanged.
