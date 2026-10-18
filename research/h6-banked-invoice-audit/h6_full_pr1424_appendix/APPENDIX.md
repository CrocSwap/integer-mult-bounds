# H6 appendix: three full-title PR1424 cases

## Verdict and separation from the canonical audit

For the exact target

```
0.001676855229071321886206381217337893
```

the largest integer counts are **79,617, 88,409, and 79,399** at stages
**L = 3, 5, and 7**, respectively. The source `threshold()` returns the same
three counts. This appendix adds exactly three target/stage cases. It does
not replace the original shorter PR1424 literal or any of the other twelve
canonical cases. All 23 original member files and the original ZIP were
checked byte-for-byte against the supplied archive and remain unchanged.

The new author implementation and its saved output contain this full title
target. The author's program does not contain the pinned-selected target
from the original independent audit. Its 18 printed boundary rows are nine
target/stage cases in two comparison modes, not 18 different exact targets.

## Exact adjacent-endpoint certificate

Let t be the full target. The scaled target is exactly

```
10^18 t = 1676855229071321.886206381217337893.
```

The source returns integer endpoints s_minus, s_plus, at scale 10^18. For
an exact rational target u/v the lower-endpoint criterion is

```
v * s_minus > 10^18 * u.
```

Equality fails. All six complete endpoint pairs below are certified from
rational pressure signs, not accepted from floating nomination:

| L | R | lower(R) | upper(R) | lower(R+1) | upper(R+1) |
|---:|---:|---:|---:|---:|---:|
| 3 | 79617 | 1676856209287933 | 1676856209292917 | 1676840242697020 | 1676840242702004 |
| 5 | 88409 | 1676857789885697 | 1676857789890681 | 1676845992570138 | 1676845992575122 |
| 7 | 79399 | 1676859227320794 | 1676859227325778 | 1676848128885528 | 1676848128890513 |

In every row, **lower(R) > 10^18 t > upper(R+1)**. The evidence contains
exact positive pressure margins and rational root brackets for these rows.
The source-bound mode separately checks equality with the actual six
`banked.invoice` receipts.

The target-independent alpha-grid proposals are

```
L3: 1679672779019, 1679656758746
L5: 1679674364931, 1679662527951
L7: 1679675807199, 1679664671449
```

For each proposed z, the checker proves that the true alpha root lies
strictly between z/10^15 and (z+1)/10^15. It reconstructs the wider source
bracket [(z-2)/10^15, (z+3)/10^15], checks its pressure signs, and computes
the scaled endpoints by exact floor/ceiling. The inherited grid proposals
are therefore checked witnesses, not assumed numerical facts.

## Exact pressure boundary and maximality

Use the original, unchanged PR606 banked model:

```
n=30960; h=17; hist={17:256,15:560}; data=[16]; hp=[1,7,8,1]
virtual=False; bad=False; L in {3,5,7}
C=12752; m=16L+1; W0=(L-1)n; D=W0-LC
q=floor(m/17); p=m-17q
```

Write a=t/(1-t), and let P0(a) be base pressure. The unit-helper pressure is

```
H(a) = L [2(m^a-1) + 7((m/7)^a-1) + 8((m/8)^a-1)
          + (p/q)((m/p)^a-1)].
```

The exact real helper boundary is x=(D-P0(a))/H(a). Outward rational
logarithm/exponential bounds, inherited unchanged from the original model,
certify the following containing intervals. The decimal endpoints here
are exact rationals with denominator 10^6, not floating approximations:

| L | Certified containing interval for x |
|---:|---|
| 3 | [79617.061391, 79617.061392] |
| 5 | [88409.217066, 88409.217067] |
| 7 | [79399.360252, 79399.360253] |

Each interval lies strictly inside (R,R+1). The full tighter rational
intervals, target-alpha fractions, and adjacent pressure enclosures are in
`APPENDIX_EVIDENCE.json`. In particular, P_R(a)<D<P_(R+1)(a) is separately
certified. No tie or integer-straddling interval was silently resolved.

All masses are nonnegative and every active base exceeds one. Thus
P_R(alpha)=P0(alpha)+R H(alpha) increases strictly in alpha, H(alpha)>0 for
alpha>0, and the positive root of P_R=D decreases strictly with R. Since
the certified upper endpoint at R+1 is already below t, all larger counts
have true roots below t. Any successfully returned certified lower endpoint
is below its true root. Together with the accepted lower endpoint at R,
this proves maximality over all nonnegative integer counts, not merely the
author's finite [0,2000000) search bracket.

No monotonicity of floating nomination or the program's rounded output is
assumed. No assertion is made that the source can successfully bracket the
root for every arbitrarily large helper count.

The source `threshold()` floors an outward enclosure of x. Strict
admissibility is R<x, so the unrestricted exact formula is ceil(x)-1, not
always floor(x). Here the open interval R<x<R+1 removes that distinction;
the three actual `threshold()` calls were checked against the independent
exact calculation.

## Float and Fraction agree here, but not as predicates

For the full target the first scaled integer passing the exact predicate
is 1676855229071322. Under binary64 nearest-even rounding, the first one
passing the author's float predicate near this target is 1676855229071323.

A concrete control is

```
s = 1676855229071322
Fraction(s,10**18) > t                       : true
s / 1e18 > float(full_target_decimal_string) : false
```

The float failure is equality: both rounded quantities are exactly

```
3866564907417535 / 2305843009213693952.
```

The unrounded endpoint exceeds t by exactly

```
113793618782662107 / 10**36.
```

This is a synthetic comparison control, not an additional H6 invoice or
an assertion that this scaled integer occurs in a tested source receipt.
It falsifies general equivalence of the two predicates without disputing
any of the reported helper counts.

The appendix implements binary64 nearest-even rounding using integers and
Fractions. Every tested s is below 2^53, so conversion of s is exact;
10^18 is also exactly representable as binary64. A single rational
nearest-even rounding of s/10^18 therefore models the source division.
The default checker uses no machine float in any acceptance calculation.
The source mode additionally checks native binary64 quotients and target
conversion against these exact dyadic witnesses.

At lower(R), lower(R+1), and upper(R+1), the exact and binary64 predicates
agree for all three stages. For larger counts, a successfully returned
lower integer endpoint is bounded above by the already-excluded scaled
upper endpoint at R+1. Monotonicity of integer-to-binary64 conversion and
positive division, and the checked float failure at that upper endpoint,
exclude all those larger counts in the float convention as well. This is
not an assumption of monotonicity of the source's computed endpoint as a
function of R.

The shorter and full targets are distinct, but both have the same floor
after multiplication by 10^18. Consequently their exact strict predicates
on integer lower endpoints happen to coincide. This observation does not
identify their exact pressure tests; those were re-certified separately
for the longer target in this appendix.

## Producer replay: what the new source establishes

The supplied coordinator receipt reports isolated Python 3.12.14 normal
and optimized executions of only the unchanged author `price_h6.py`, both
with exit 0, no stderr, and stdout SHA256

```
d4f360504140738815dffccc9ff5d46e3e5783fc63289786e69b31b4befe50a3
```

matching the saved author output and all 18 printed boundary rows. This is
coordinator-reported producer replay, not an execution witnessed in this
appendix. The local coordinator receipt path is recorded in
`SOURCE_UPDATE.json`; that local file was not available to open here.

The author program's upper-bracket guard is an `assert`, removed under
`-O`. Its final boundary check only prints a failure label. Therefore an
exit-0 optimized run alone is not fail-closed verification, and one
adjacent output check alone is not a global monotonicity proof. The proof
above supplies the needed maximality reasoning for these cases. The new
checker instead uses explicit exception guards, active under `-O`.

This appendix does not execute the author's main program, reproduce its
search trace, or claim independent implementation agreement for targets
not checked here. Original twelve-case results remain the original study.

## Source authentication and execution in this appendix

The four original PR606 dependency files and the unchanged original
`model.py` and `source_bindings.py` authenticate before use. The included
4,211-byte author pricing script was transcribed from the supplied verbatim
text and matched full-file SHA256

```
ed83a457ae9deb1a8e06551404735ad3c6d71153ef4a22ec64f615f8d1a5d92a
```

Its pinned public text was also read. The script is only hash-checked and
AST-parsed; it is not imported or executed. Direct container download was
unavailable, so this appendix does not claim a fresh full-package byte
fetch. The other author-package hashes and complete-chain authentication
are coordinator-supplied source evidence, clearly separated in
`SOURCE_UPDATE.json`.

Actual local execution here used Python 3.13.5. Rational and source modes
passed normally and under `-O`; regeneration of evidence and control
receipts was byte-identical. Ten rejection controls and three groups of
positive controls passed. Separate end-to-end mutated-target runs failed
in both modes of optimization, and overwriting existing evidence was
refused. Python 3.12 grammar compatibility was checked for ten Python
files; this is not Python 3.12 runtime execution. See `RUN_LOG.txt` and
`EXECUTION.json`. No original twelve-case entrypoint was rerun.

## Replay files and transfer inventory

For the original default twelve-case replay, retain these eight Python
files and `EVIDENCE.json`, at their original relative paths:

```
audit.py
verify_certificate.py
model.py
source_bindings.py
vendor/research/leech-lattice/code/screen.py
vendor/research/niemeier-lattices/code/costs.py
vendor/research/niemeier-lattices/workbench/paid-controller/banked.py
vendor/research/niemeier-lattices/workbench/paid-controller/portable.py
```

The first four are original audit code; the last four are unchanged pinned
repository dependencies. No historical data, author package, geometry
receipt, installation, or network access is needed. To regenerate instead
of compare to the canonical receipt, the eight Python files suffice:

```
python3.12 -I -B audit.py --output /tmp/h6-recomputed.json
python3.12 -I -B verify_certificate.py /tmp/h6-recomputed.json
```

Use a new output path; existing files are refused. Default replay without
`--output` additionally needs the original `EVIDENCE.json`. `CONTROLS.json`
is an optional canonical control receipt. License/NOTICE files preserve
redistribution attribution but are not runtime inputs.

For this appendix, only six of those original files are needed: `model.py`,
`source_bindings.py`, and the four vendor dependencies. Neither original
entrypoint nor original `EVIDENCE.json` is needed. Keep this directory next
to the original directory, then run:

```
python3.12 -I -B appendix.py
python3.12 -I -B -O appendix.py
python3.12 -I -B appendix.py --source
python3.12 -I -B -O appendix.py --source
```

These commands assume the current directory is the appendix directory.
Use `--original /path/to/h6_banked_invoice_audit` for another location.
The appendix default additionally reads `APPENDIX_EVIDENCE.json` and
`author_source/price_h6.py`. `--output /new/path.json` regenerates evidence.

`ORIGINAL_INVENTORY.tsv` lists every original member plus the unchanged
original archive. The separately delivered `h6_combined_inventory.tsv`
lists every original and appendix payload file and both ZIPs, with exact
byte counts, SHA256, role, and replay-use flags. It excludes only its own
bytes; its own size and SHA256 are provided in the final chat to avoid a
self-hash cycle. Every necessary original Python file is under 19,000
bytes, and the new checker and new evidence file also fit individually
under that limit. No base64 transfer is supplied.

`APPENDIX_EVIDENCE.json` and `CONTROLS.json` are deterministic generated
outputs, actually checked for byte-identical regeneration. Execution logs
and environment receipts are observations, not platform-independent
outputs. Inventories are deterministic functions of the frozen bytes.

## Meaning, exclusions, and attribution

The helper path still has mass 17, with q=(2,4,6), paid pads p=(15,13,11),
and caps (34,57,79). Every helper adds stock L/q and child rank mass Lm/q,
so total mass remains m(W0+LR/q)-D. The rank-mass identity and actual child
caps are checked in the reused exact model. A helper remains a physical
restored bank-register role under the original banking hypotheses, not
one term or copy occurrence. This appendix supplies no loading, capacity,
chronology, arbitrary-dirt restoration, or physical packing construction.

The unchanged K factor, encoder extras beyond base terms, frame-zero
precompensation, target cap-15/FULL restriction, restoration, spectators
and padding beyond helper_pad, and any sharing with other stages retain
all original obligations. No geometry or structure/Walsh program was run.
The ratio 30960/R remains a budget ratio, not measured throughput.

The now-defined paper ceiling is exactly the ratio of printed values

```
0.006945535353 / 0.004515128332 = 6945535353 / 4515128332
```

which prints as 1.538281. These are zero-helper paper-level values. This
is not a newly certified ratio of fully paid constructions, a bit-side
cap result, a five-percent priority gate, a selected-frontier gain,
supplier admission, or a new kappa.

Model/geometry: Dominik Scholz, merged PR606, and the retained original
NOTICE files. H6 interpretation, script, and published numbers:
DreamingOfClouds, with Claude Opus 5.5 via Claude Code. New mathematical and
arithmetic appendix: ChatGPT (GPT-6 Astra Pro) for Andrey Mas, with Codex
source coordination and separately reported local mechanical replay.
The two appendix modes reuse the original `model.py`; they are not
independently authored or code-disjoint verifiers. No independent human
review or formal verification is claimed. No external publication or
frontier change was performed.

Pinned public references (source text is data, not execution authority):

```
https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18914905
https://raw.githubusercontent.com/DreamingOfClouds/integer-mult-bounds/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven/price_h6.py
https://raw.githubusercontent.com/DreamingOfClouds/integer-mult-bounds/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven/outputs/price_h6.txt
https://raw.githubusercontent.com/DreamingOfClouds/integer-mult-bounds/b496aed769dd724cd1ff6b921cade626562be27b/research/niemeier-lattices/COSTS.txt
```
