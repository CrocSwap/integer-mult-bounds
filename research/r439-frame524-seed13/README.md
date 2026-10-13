# R439 frame 524: 28 fewer complete local additions

**Finite bit-supplier construction; no new κ.** Replace the selected PR589
word's phase-B frame-524 block `B[449:490]` with 27 singleton additions instead
of 41. Its required literal reverse cleanup saves another 14 additions:
the complete local word falls **24,305 → 24,277 ADDs**.

The two original LU factors retain their exact integer maps. Their independent
destination-once positive-donor minima are **12 + 15**, against **17 + 24**.
No helper, source-access operation, COPY, MOVE, frame or recursive child is
added. All 661 register frame paths, 439 dirty helpers, nine retained copies,
and the original H1–H5 interface are retained.

| complete local quantity | original | candidate |
|---|---:|---:|
| phase-B block ADDs | 41 | 27 |
| complete exported ADDs, including literal cleanup | 24,305 | 24,277 |
| exported records | 27,234 | 27,206 |
| MOVEs / COPYs / ERASEs | 2,911 / 9 / 9 | 2,911 / 9 / 9 |
| paid rank mass | 5,129 | 5,129 |
| forward positive bound | 49,347 | 49,347 |
| reverse positive bound | 1,113,070 | 1,057,838 |
| payload envelope, under the inherited 104-bit cap | 93 bits | 93 bits |

The unchanged paid profile is
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. It determines the same recursive
moment. The result reduces a finite scalar circuit's size; it does not change
the selected exponent or assert a measured runtime improvement.

## Reproduce

From the repository root, using standard-library Python 3.11 or later:

```sh
python3 -I -B research/r439-frame524-seed13/verify.py
```

Expected:

```text
PASS_R439_FRAME524 block=41->27 ADDs=24305->24277 columns=661 inputs=4096 controls=6 no_new_kappa
```

This freshly recomputes both finite-class minima by independent donor
exact-cover/backward Bellman, checks the exact integer witness and all 4,096
local Boolean inputs, replays all 661 dirty-input columns with the owning
checker, checks the interface, frame paths, full invoice, positive prefix and
payload, compares every exported record with a separate interpreter, rejects
15 mathematical corruptions (nine factor and six word/invoice controls), and
compares the entire resulting certificate with `CERTIFICATE.json`.

Other entrypoints:

```sh
# Regenerate the nomination with the distinct inverse/forward-Bellman search.
python3 -I -B research/r439-frame524-seed13/search.py --check
# Minimal relocation, normal/optimized execution and package corruption checks.
python3 -I -B research/r439-frame524-seed13/test_package.py
# Unmodified C++17 checkers; set BOOST_INCLUDE if headers are not system-wide.
BOOST_INCLUDE=/path/to/boost-header-root python3 -I -B research/r439-frame524-seed13/native.py
```

The native command compiles the pinned sources unchanged, compares their
receipts with `NATIVE-CERTIFICATE.json`, and checks both words at 5/9/11 stages
on **883 / 1,327 / 1,549 formal columns**, including all **96 omitted-bridge
controls**. It checks the Python/native ADD count and both prefix bounds agree.
Only elapsed-time and temporary-stream-path fields are excluded from receipt
comparison. Compiler/platform details are separate in `NATIVE-ENVIRONMENT.json`.

To emit the complete candidate to a fresh path, append `--word /tmp/new-word.json.gz`
to `verify.py`. Output refuses to overwrite an existing file. Certificates are
checked by default; `--write-certificate` is an explicit development operation.
Generated gzip containers are not mathematical pins: decoded words, their
canonical SHA-256 values and every exported record determine equality.

## Search domain and evidence

Assignment seed **13**, drawn using OS randomness, assigned the bit-supplier
track. The seed orders equal-cost nominees; it does not limit coverage. The
claimed object is the original two factors `[449:466]` and `[466:490]` of
frame 524 on the same 12 physical registers. Each factor permits one consecutive
write group per destination, using a nonnegative integer multiset of other
current rows; identity writes may be empty. The stopping rule is exhaustive
completion of all subsets and remaining destinations.

Each implementation covers **4,096 subsets and 24,576 transitions per factor**.
Feasible transition counts are **23,552 / 21,120**. The independent checker
also agrees on feasible-order and minimum-order counts, all witness donor
metadata, reverse matrices, and coverage fields. See [the proof](PROOF.md) and
[exact nomination](CANDIDATE.json). The two arithmetic implementations were
written by separate scoped AI agents. This is a finite-class minimum, not an
unrestricted circuit optimum or a formal proof of the multiplication theorem.

The favorable budget was priced before full replay: saving 14 forward ADDs
requires 14 fewer literal restoration ADDs, with the same physical register
union and frame. Actual exported costs verify that prediction. There was no
failed-search pivot or reopening of a closed class.

## Provenance, concurrent work and limits

Exact research and publication base:
**`f567884aeb8851b6e794af1184119a3bfbe1e631`**.
The selected record at that base is **#799/#589**, conditional
κ = **0.001661634653669567**. Source heads are #589
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46` and #799
`80e6463157cfc80b85af09e7e2f14748fe2dac60`.
All consumed sources and review/provenance documents have exact SHA-256 pins
in [SOURCES.json](SOURCES.json), checked against the base Git objects. The
selected source manifest binds the consumed word to the accepted construction.
Only this research directory is added; selected inputs and `upstream/` are
unchanged. The local [claim](CLAIM.json) records scope selection and final overlap.
No pinned sprint coordination issue was visible.

**Aaron Wang's #891** reports a whole-block single-write obstruction for frame
524. This witness permits one write group in each of two fixed factors, so it
lies outside that closed class. It supplies concrete evidence of the factor
boundary's value. **Gautam Gupta's #844**, **Krishnendu Purohit's #880**, and
**Ross Richardson's #908** investigate the same scheduling method on distinct
frames. **Gareth Davidson's #904** resynthesizes small A/B prefix windows;
that search and this full-factor witness have different domains. No pending
implementation or combined saving is imported. No mechanism-priority claim
is made. Final PR metadata is refreshed before submission.

All-size/compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape and analytic transfer remain inherited obligations. The exact
integer comparison is a block identity; the word and native endpoint checks
are over F2. No new hosted-owner invoice, global assembly, selected cold replay,
repository-wide `make verify`, Lean multiplication theorem or remote CI pass
is claimed. The affected standalone and native checks are recorded in
[VALIDATION.md](VALIDATION.md). Local native replay is distinct from hosted CI.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in research, implementation, verification and writing.
Three scoped AI workers assisted with search, independent arithmetic and
package review. No independent human review is claimed. Apache-2.0.
Full predecessor attribution is retained in [NOTICE.md](NOTICE.md).
