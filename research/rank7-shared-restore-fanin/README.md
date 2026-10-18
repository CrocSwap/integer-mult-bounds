# One shared restore covector at two consumers

R2 replaces two separated reads of `X40 - 2 X54` with one temporary
aggregation in X40. Both dirty sources are restored. It saves two rank-one
children at the cost of one rank-two child per call, without another register,
a helper-width change or an increase in scalar gate count.

R2 composes with Jeremy Kothe's R1 from [PR3015][3015]. On both of
Marius-Paul Dumitrean's [PR2979][2979] providers, their common local profile is

```text
before, R1       {1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}
after, R1 + R2   {1:2441, 2:708, 3:232, 4:108, 5:18, 8:8}
```

The original literal T74 allocation still fits the unchanged ordered widths.
Its complete complex moment root is certified in

```text
[0.0017292679803119446932163, 0.0017292679803119446932164].
```

Even this older packing beats the published T740+R1 moment in
[PR3030][3030] by about `1.15224307614e-7`. The verifier recomputes both full
profiles with their different denominators; it does not infer this comparison
from the local delta. PR3030 remains credited for its exact fixed-word packing
cap. R2 changes that word, not its allocation problem.

A fresh complete source/native/admission/modern-outer release passes at

```text
kappa = 0.001729267980311944693216 - 10^-46 - 10^-70.
```

Its exact gain over PR3030's released nomination is
`115224307613758681/10^24`. The recorded thirteen stages total 1,272.70 seconds
on Linux with CPython 3.12.15. This is an author-checked conditional finite
candidate, not a selected-frontier update or a complete multiplication theorem.
No selected-result file changes.

## Literal construction

The scientific base is canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
[SOURCES.json](SOURCES.json) binds the two original words and inherited engines.
[VENDOR.json](VENDOR.json) pins Kothe's literal R1 and the PR3030 comparison.
The [canonical investigation][discussion] gives the live scope and overlap.

Here Xr denotes the current register r, not necessarily its original input
value. In the original restore word, the relevant source-addressed gates are

```text
162  X18 += X40
163  X18 -= 2 X54
...
175  X22 += X40
176  X22 -= X45
177  X22 -= 2 X54
```

All five gates use the rank-8 frame `E42`. X40 and X54 both already have the
rank-7 frame

```text
W = span(256,128,64,34,17,11,4) = E25 intersect E42 intersect E51.
```

There are exactly four contacts with X40 or X54 from gate 162 through the
end of restore, at 162, 163, 175 and 177. In particular neither source has an
intervening observer or writer. Gate 176 only adds the X45 term
into X22, so it commutes with X22's X54 update. The rewriter checks these
literal preimages and this contact census.

Insert `X40 -= 2 X54` at W before gate 162. Retain the two X40 consumers,
remove gates 163 and 177, and append `X40 += 2 X54` at FULL after restore.
Keep every other scalar gate and frame, then rederive inverse cleanup. Apply
R1 first because its indices refer to the original word. The full source
builder receives the equivalent combined literal hunks, with exact preimages.

## Proof and complete bill

For arbitrary dirty values `a,b,u,v`, the new four-operation sequence is

```text
a -= 2b
u += a
v += a
a += 2b
```

Its endpoint is `(a,b,u+a-2b,v+a-2b)`, exactly the original two consumers.
No zero-source premise is used. Intervening original operations preserve the
identity for the reasons above. `verify.py` checks the rational four-register
matrix and the complete 704-column literal restore operator separately from
the inherited all-input auditor. Coefficient and missing-operation controls
must fail that independent equality check; they do not merely rely on a stale
cleanup being rejected.

Originally X54 climbs W to E42 to FULL, with jumps 1 and 1. After R2 it is
only used at W and FULL, so its final jump is 2. X40 still has jumps 1 and 1.
The temporary source restoration is charged at FULL, not discarded as free
cleanup. The other two registers' itineraries do not change. The independent
set-of-vectors census in `frame_trace.py` checks this directly from the literal
A/B/warp/restore chronology, without importing the inherited frame pricer:

```text
four touched registers, R1      {1:20, 2:1, 3:2, 4:1}
four touched registers, R1+R2   {1:18, 2:2, 3:2, 4:1}
```

Write `Hr(b) = r*(73/r)^b`. The per-call delta is

```text
H2(b) - 2H1(b) = 2*73^b*(2^(-b)-1) < 0, for every b > 0.
```

Thus this is a strict moment improvement, not just a scalar simplification.
Its rank mass is unchanged. All 408 ordered helper widths, 91 private zero
buffers, source cut, compensation, entrances, helper endpoints and warps stay
unchanged. R2 replaces four ADDs with four ADDs and its inverse cleanup also
has unchanged length. The source T74 fill/order/dispatch therefore remain
literal inputs. All idle children and every local child are included:

```text
T = 74; calls = 666; live = 66304
complete profile = {1:1643016, 2:471528, 3:159468, 4:71928,
                    5:13716, 8:5328, 48:28190}
rank mass = 4816512 = 74*65088
physical families = 66304 + 408 + 8 + 91 + 2 = 66813
```

The local formula proves the sign over the whole positive b interval. The
source-authenticated rational logarithm/Taylor engine supplies the numeric
root brackets. This reuses the inherited arithmetic; it is not an independent
implementation of that engine.

The coverage/halving packing relaxation for the new profile has cap about
`0.001756475065598923` in this moment variable. T74 realizes about 98.4510%
of that bound. Its idle mass is 2,093 per call; placing that entire mass at the
maximum halving-legal rank 51 gives the favorable relaxation, because cost per
unit rank decreases with rank for positive b. The verifier certifies its root
and the realized fraction with rational intervals. This is the model of
`complex-local-word-ceiling/ceiling.py`, not a feasible packing, a new
fixed-inventory optimum or an application of an older outer-transfer formula.
Its slack does not justify another packing search.

## Reproduce

The bounded standard-library check rebuilds parent, R1, R2 and R1+R2 for both
providers, audits all 632 independent dirty columns forward and dual, checks
the separate frame census and both complete moments, and rejects 16 controls:

```sh
python3.12 -B scripts/research_package.py \
  --package research/rank7-shared-restore-fanin
python3.12 -B research/rank7-shared-restore-fanin/test_verify.py
```

To retain generated words and diagnostic logs, choose a fresh external path:

```sh
python3.12 -B research/rank7-shared-restore-fanin/verify.py --work "$RUN/finite"
```

The default mode removes its private temporary directory, including on failure.
Explicit `--work` refuses existing data and preserves diagnostics. No default
command writes generated words into the checkout.

The expansion decision was to continue through one complete T74 verification,
not another construction search. The proved recursive saving and unchanged
physical inventory justify that test. Prefix/magnitude costs were unknown
until the emitted-program invoice; they were not set to zero. Failure of a
source, physical or prefix gate stops the release. T740 composition stays a
separate next question.

`reproduce.py` exports the exact PR3015 package and obtains its unchanged
complete source recipe. It replaces only the declared-edit parameter directory
and the descriptive source labels. Stage programs, the literal allocation,
all native checks and every admission/outer acceptance gate remain unchanged.
The parameter directory contains the explicit R1+R2 edit list and final words;
it does not edit a frozen predecessor. The command runs all stages serially,
including a fresh retained bootstrap and both fresh native providers:

```sh
python3.12 -B research/rank7-shared-restore-fanin/reproduce.py \
  --repo . --work "$RUN/full"
```

It needs the exact objects in [GIT-SOURCES.json](GIT-SOURCES.json). Fetch them
from canonical upstream before the network-free replay:

```sh
python3 -c 'import json, subprocess; subprocess.run(["git", "fetch", "https://github.com/CrocSwap/integer-mult-bounds.git", *[x["head"] for x in json.load(open("research/rank7-shared-restore-fanin/GIT-SOURCES.json"))]], check=True)'
```

It also needs a C++ compiler and NumPy 2.4.5, SciPy 1.16.1,
SymPy 1.14.0 and mpmath 1.3.0. gmpy2 2.3.2 and psutil 7.2.1
were also installed locally. `--dry-run` performs source export and recipe
checks only. Full replay is explicit, not part of the registered cheap check.
Direct calls should use a clean checkout or a fresh `PYTHONPYCACHEPREFIX`;
`-B` alone does not prevent existing bytecode reads. The registered launcher
isolates its complete interpreter automatically.

The [retained release](evidence/RESULT.json), native receipt, source manifest,
final word containers and stage logs are bound in
[evidence/BINDINGS.json](evidence/BINDINGS.json). The registered check also runs
`verify_release.py`, which checks these bindings and rejects ten receipt/invoice
mutants. It does not rerun native execution. Frozen word hashes bind actual
released bytes; regenerated words compare by canonical decoded payload, not
compression headers.

The actual emitted-program invoice retains all 666 invocation and 666 bridge
sweeps, 91 private buffers and 66,813 physical families. It reports local/global
prefixes 93/1,475 bits, stock exponent 1,322 and reserve 1,510 below the charged
2,048-bit payload. The inherited owner's legacy `live+490` diagnostic is not
this full `live+509` charge. The actual source release and
[evidence/INVOICE.json.gz](evidence/INVOICE.json.gz) supply the complete bill.

## Limits

A conditional finite release does not prove the complete multiplication
theorem. Inherited all-size/compiler, physical realization and storage,
precision/tape, caller, analytic and universal block-energy hypotheses remain.
No independent human or formal-kernel review is claimed. Frozen sources and
the selected frontier are unchanged.

## Open next questions

1. Independently replay the exact source/native/admission chain before adoption.
   Start with the fresh external command above and compare word, manifest,
   complete profile and release bindings. Scientific dependencies remain review
   obligations even if the replay passes.
2. Compose R2 with the already published T740 allocation only after this word
   is checked. Unchanged helper widths suggest compatibility, but actual source,
   physical/prefix and complete release bindings must be regenerated. An old
   T740 receipt does not cover R2. This session does not run another packing
   search or that second release.

## Credit

Nick Petalas contributed R2, its independent frame census and this composition.
Jeremy Kothe contributed R1, the restore-rewrite handoff and the reused literal
edit builder/reviewer. Marius-Paul Dumitrean contributed PR2979's joint rank-7
words and complete allocation. Credit also Mason Hale, Jeremy Diviney, Yiyang
Lu, Tekalign, Ross Richardson, Dugongue, icekylinx, themilkman216 and the retained
geometry/native/owner lineage. Original [credits](vendor/PR3015-CREDITS.md) and
[notice](vendor/PR3015-NOTICE) are unchanged. Apache-2.0.
[ENGINEERING.md](ENGINEERING.md) records verification and runtime limits.

[3015]: https://github.com/CrocSwap/integer-mult-bounds/pull/3015
[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
[3030]: https://github.com/CrocSwap/integer-mult-bounds/pull/3030
[discussion]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18981612
