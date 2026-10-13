# Complete-word admission saves 240 further R439 ADDs

Finite bit-circuit construction; **no new kappa**. On the frozen PR952 word,
the same bounded six-wire Gaussian menu finds **no further replacement** under
its two local entrywise growth guards. Admitting candidates by their actual
complete-word precision bounds instead permits **42 replacements**, saving
120 A ADDs and their 120 literal cleanup ADDs. The complete word falls from
**23,673 to 23,433 ADDs**, or 872 fewer than selected PR589.

All 42 new programs fail at least one old local guard. Nevertheless, the final
complete bounds improve from F = 41,287, B = 833,084 to **F = 35,655,
B = 692,438**. Full-prefix admission is already used in the separate B-block
work PR857/906; this contribution supplies the same-input comparison across
all 60 six-wire A blocks and the resulting cumulative construction.

| Word | Complete ADDs | Local payload bits | Nine-stage prefix bits |
|---|---:|---:|---:|
| Selected PR589 | 24,305 | 93 | 177 |
| Frozen PR952 | 23,673 | 92 | 174 |
| This candidate | **23,433** | **91** | **172** |
| Retained ceiling | — | 104 | 192 |

The 632 inherited savings are 254 from PR904, 340 from Ross Richardson's
PR936, and 38 from PR952. Only the additional **240** belong to this pass.
Paid ranks, 439 helpers, nine copies, all 661 register frame paths and the
original H1-H5 interface are retained. D, B, scatter and every other payload
field stay exactly equal to PR952. C is the literal reverse cleanup of A+B.

## Reproduce

From the repository root, with Python 3.10+, a C++17 compiler and Boost headers:

```sh
python3 -I -B research/r439-global-prefix-admission/verify.py
```

Expected: `PASS_R439_GLOBAL_PREFIX_ADMISSION: 42 blocks; 240 further ADDs; 872 versus PR589; H1-H5; 104/192-bit caps; 5/9/11 stages; no new kappa`.
Set `BOOST_INCLUDE` for a nonstandard Boost header directory and `CXX` for a
different compiler. `--output /new/path --receipt /new/receipt.json` retains
all logs and a deterministic receipt. No network or third-party Python module
is needed. The default command regenerates both searches, checks every priced
trial and runs the native stages; it compares the full receipt to EXPECTED.json.
The seven artifact tests run with:

```sh
python3 -I -B research/r439-global-prefix-admission/test_package.py
```

## Exact domain and evidence

OS assignment seed **3**, drawn at 2026-10-13T15:07:47.395637+00:00, selects the
bit track and a single shuffled order of the 60 blocks at frames 266–325.
The nomination domain is unchanged from PR952: 720 pivot orders, row-only
or mixed row/column reduction, and the two original donor priorities
`[1,2,3,4,5,0]` and `[0,5,4,3,2,1]`. Seed 19 belongs to those inherited
priorities; they are not redrawn. Each comparison examines 172,800 nominations.

The complete-word pass deduplicates programs, retains shorter programs that
use all six existing wires, sorts them by (length, lexical program), and
retains at most 32 per block. There are 13,039 distinct shorter programs
summed over blocks. The first nominee in each of 42 nonempty blocks passes;
there are **42 complete-word prices, 42 admissions and zero budget rejections**.
The other 18 blocks have no shorter eligible nominee. One pass, no restarts.
The unchanged strict search separately returns zero admissions on this input.
Neither result is an unrestricted circuit optimum or a global fixed-point claim.

The verifier checks 2,688 local Boolean inputs and 504 positive column pairs.
It reassembles every accumulated trial independently and uses the pinned
PR952 set-valued, literal ADD/COPY/ERASE interpreter on all 661 dirty input
columns in both directions: 1,979,296 trial instructions in total. It compares
every exact price with the builder's separate macro evaluator. All 42 trials
meet both caps; the largest intermediate F is 41,291, so final F domination
alone would not certify the chosen sequence.

Fresh unchanged native checks cover PR589, PR952 and this candidate at 5/9/11
stages, with 883/1,327/1,549 formal columns per word and 144 omitted-bridge
controls. Sixteen local controls include a 103-bit local / 194-bit nine-stage
overflow, a 111-bit local overflow, corrupted Boolean maps, stale literal
cleanup, missing gates, unpaid costs and rebound-hash payload edits.

## Pins, credit and scope

Research base: **946293a3dcaa9121ef5f4be44db2e07adb7de085**. PR952 source:
**11d24706f06e95271804c9438869546724c67aab**, incorporated unchanged in that base.
SOURCES.json binds 18 runtime inputs, including both source implementations
and the exact gzip input bytes. Generated candidate equality uses its complete
decoded canonical payload, SHA-256
`6ad029fc492597ed492e87e449e3fdcfccb27400a66189976db7c7243c81dd2b`.
At refresh **bbc600db2fc15007b7c914f4f2b2ed55fa909c87**, all 18 inputs were
unchanged. That update records maintainer integration and changes no runtime
source consumed here. Selected PR942 remains conditional kappa
`1661960547713947 / 10^18`, still using PR589 for bits.

This is not a per-block record claim: our frame 267 uses 13 A ADDs, whereas
Ross Richardson's separate PR925 provides 12 for its fixed positive transfer.
That recipe is not composed here. PR941/965 and Sricharan Vagvala's concurrent
PR967 change D under a semantic interface and are separate candidates.
Cinna Davis's concurrent PR973 changes B frame 509. None of those savings
is added to this result. Queue overlap was checked through PR976.

Remaining adoption work is concrete: export and audit the complete hosted
supplier; regenerate its global invoice, supplier binding and outer assembly;
then recheck the inherited compiler, realization, common-label/mutable-source,
hosting, precision/tape/recovery and analytic obligations. This package runs
native finite stages and substitutes fresh F/B into the pinned nine-stage
formula. It does not claim a full hosted replay, a cold selected complex
replay, a full `make verify`, a practical runtime gain or a formal proof of
the multiplication theorem. The paid recursive profile is unchanged, so no
larger kappa follows from these common-frame ADD savings alone.

See PROOF.md, VALIDATION.md and NOTICE.md for the argument, executed checks,
attribution and substantial OpenAI Codex assistance disclosure.
