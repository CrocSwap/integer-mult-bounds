# Frame506 two-factor bit construction

Replace the PR589 R439 phase-B frame 506 block `B[102:128)` with **21 rather than 26 singleton ADDs**. Split the original block at gate114, preserving each factor's exact INTEGER transfer map; reschedule each factor with one completed write per destination and positive integer donor multiplicities. The independently checked minima are **9 + 12**. Rebuild the required literal full-frame cleanup. The complete exported word costs **24,295 rather than 24,305 ADDs**.

This is a finite construction and a restricted search-class minimum. It makes **no new κ claim**. At base `407d52ff15b2217b6e22bce44728b4c3907b6515`, the selected result is PR942/T37, conditional κ `1661960547713947/10^18`, audited source head `1960cfa919a0945d0ca4cb14ea96237000037903`. Its bit supplier is still PR589, head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, word SHA256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`. The complex supplier binds. This package changes neither the selected inputs nor `upstream/`.

## Reproduce

From the repository root, with standard-library Python 3.11+:

```sh
python3 -I -B research/r439-frame506-two-factor/search.py --check && python3 -I -B research/r439-frame506-two-factor/verify.py
```

Expected final output:

```
PASS_R439_FRAME506 block=26->21 ADDs=24305->24295 columns=661 inputs=1024 controls=6 no_new_kappa
```

`search.py --check` recomputes all 25 internal original boundaries103–127 and compares the complete candidate JSON. OS assignment seed18 chooses the destination tie priority; it changes which equal-cost witness is emitted, not completed coverage. All25 cuts are feasible; minimum21 occurs at114,115,116, with the first chosen. The domain is exactly two fixed original factors, destination-once within each, positive integer donor multisets, ten existing registers. It excludes arbitrary interleavings, extra scratch, different factor matrices and unrestricted XOR synthesis.

`verify.py` imports no discovery implementation. A separately written direct donor-subset enumeration/backward Bellman checker establishes the 9/12 minima at the chosen binary factors, checks the integer map and signed inverses on all ten dirty basis columns, and checks all 1024 Boolean inputs. Six independent arithmetic mutations and six full-word/interface/invoice mutations reject. The owning pinned checker checks all 661 dirty-input columns, H1–H5 and frame geometry. A separate record interpreter matches every exported record byte for byte. `CERTIFICATE.json` binds the recipe, decoded words, invoices and records; comparisons use canonical decoded content rather than incidental gzip headers. Source mismatches fail before any certificate write.

The complete budget includes unchanged D/A preparation and source reads, scatter/copy operations, every B operation, literal C restoration and all final frame moves. Ten scalar ADDs are saved: five in B and five in C. No helper, frame change, COPY/ERASE or recursive child is added. All661 per-register frame paths and nine COPY/ERASE pairs remain identical. The rank profile remains `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass 5129. The forward positive bound remains 49347; reverse decreases 1113070→1107058; complete local payload remains 93 bits below 104. The positive reverse matrix is entrywise dominated, but it is not equal to the original.

## Native replay

With C++17 and Boost headers, export a fresh word and replay unchanged pinned native checkers:

```sh
python3 -I -B research/r439-frame506-two-factor/verify.py --word /tmp/frame506-word.json.gz
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r439-frame506-two-factor/native.py --word /tmp/frame506-word.json.gz --out /tmp/frame506-native --expected-saving 10
```

Both paths must be fresh. Expected native result: `PASS_R439_FRAME506_NATIVE_REPLAY saved=10`. Native legality and 5/9/11-stage replay check 883/1327/1549 formal columns on **both** baseline and candidate. All 96 omitted-bridge controls reject across the six runs. Each stage has the complete local ADD bill, every fresh center copy and signed inverse orientation; each composed prefix stays93 bits under 104. `NATIVE.json` is deterministic mathematical evidence from the executed replay; `ENVIRONMENT.json` records the toolchain and Boost 1.87 archive/header pins. This does not emit the full globally hosted supplier or reprice an outer assembly.

## Why this adds evidence

Aaron Wang's merged PR891 establishes24 as the whole-block destination-once minimum at506. Its class disallows intermediate rows followed by another write to the same destination. This two-factor witness writes some destinations in both factors and uses intermediate rows between them, so it lies outside that closed class and improves the506 component by 3 B ADDs. The distinct523 shortening in PR891 is not combined here. Ross Richardson's merged PR914 supplied the exact general-integer factor solver and verification pattern used here, on a different frame524. His PR908 and related fixed-factor work supply the scheduling lineage. Concurrent PR980 changes phaseA and explicitly preserves phaseB; its six-wire Gaussian prefix mechanism is distinct. PR827's fixed-prefix full-frame cleanup obstruction does not exclude these scalar savings. Final metadata refresh also inspected PR989 (`101103e56e3effdb268ce90110c6caa4c6885671`), which composes frames 507/508/519/524 and excludes 506. Refreshed main `8bddbee377e2f3ce1f1247196c4b290d55767d20` leaves all 18 consumed/context source pins unchanged; `OVERLAP.json` records the distinct coverage. No mechanism-priority or independent human review is claimed.

The all-size compiler, common-label and mutable-source realization, whole-call hosting, precision/tape and analytic transfer remain inherited hypotheses. Finite matrix/native checks do not formally prove the full multiplication theorem. No unrestricted21-gate optimum, new recursive bound, hosted global invoice, cold selected replay, Lean proof, measured runtime speedup or remote CI pass is asserted.

Prepared for Eva Ayala (@ToikY) with substantial OpenAI Codex assistance, including one scoped AI worker for independent arithmetic/review. Source credits and Apache-2.0 notices are in `NOTICE.md`; exact consumed/context source pins are in `SOURCES.json` and `native-source-pins.json`. The local sprint claim records the three candidate tasks, seed, base, favorable complete budget and stopping rule.
