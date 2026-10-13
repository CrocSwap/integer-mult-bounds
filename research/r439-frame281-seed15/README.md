# Frame281: a 12-ADD circuit beyond PR952, and an exact 12/13 boundary

**Finite bit-supplier construction and scoped class minimum; no new kappa.**
Replace one complete six-register phase-A block in Gareth Davidson's retained
PR952 word: frame281 (quad15), `A[825:838]`, drops from **13 to 12 ADDs**.
Rebuilding its required literal reverse cleanup saves one more ADD, so the
complete local word drops **23,673 -> 23,671 ADDs**. All other PR952 changes
are inherited and credited, not claimed as new savings.

The exact minimum for this fixed positive integer transfer is **12**. If its
reverse positive matrix must also be entrywise no larger than PR952's matrix,
the exact minimum is **13**. Thus the stronger local guard excludes every
shortest circuit even though our 12-ADD witness *reduces* the complete word's
reverse bound. This is a concrete reason to price the full word after a local
guard rejects a candidate.

| Complete local resource | PR952 parent | This candidate |
|---|---:|---:|
| ADDs, including cleanup and dirty compensation | 23,673 | **23,671** |
| Exported records | 26,602 | **26,600** |
| Forward positive bound F | 41,287 | 41,287 |
| Reverse positive bound B | 833,084 | **832,712** |
| Local payload bits, allowance 104 | 92 | 92 |
| Nine-stage expression bits, allowance 192 | 174 | 174 |
| Paid rank mass | 5,129 | 5,129 |
| MOVE / COPY / ERASE records | 2,911 / 9 / 9 | unchanged |

All 661 symbolic dirty-input columns, original H1-H5 interface conditions,
per-register frame paths, and the actual exported record stream are checked.
No helper, frame, source-access operation, COPY, restoration call or recursive
child is added. The paid rank profile and decoder constant 63 are unchanged.
Neither the bit exponent nor the selected conditional kappa is improved.

## Reproduce

From the repository root, Python 3.11+ with the standard library only:

```sh
python -I -B research/r439-frame281-seed15/verify.py
```

Expected final line:

```text
PASS_R439_FRAME281 gates=13->12 local_ADDs=23673->23671 columns=661 rank_mass=5129 controls=7
```

The command checks all source pins, reruns the bounded discovery and its
complete metadata, independently proves both class minima by column-based
breadth-first searches, checks 64 Boolean inputs and exact integer matrices,
prices the whole word in both directions, checks E8 geometry/H1-H5, regenerates
records and interprets their actual bytes. Nine independent mathematical
controls plus seven local/whole-word controls must reject. The certificate is
compared by canonical JSON, not regenerated gzip container bytes. Typical local
run is about 15 seconds; timing is not part of acceptance.

Use `--output /absolute/fresh/directory` to retain both reconstructed words
(`original.json.gz` is PR952) and exported records. Outputs must be new.
`--write-certificate` explicitly regenerates only this package's certificate.
Discovery alone is `python -I -B research/r439-frame281-seed15/search.py`.

An optional native harness is provided:

```sh
BOOST_INCLUDE=/path/to/boost CXX=g++ python -I -B research/r439-frame281-seed15/native.py --write-certificate
```

**Native C++ legality and 5/9/11-stage execution were not run here.** No
`NATIVE-CERTIFICATE.json` is supplied. The environment lacks compatible
GCC/Clang and accessible Boost headers; `make verify` also stops because `make`
is unavailable. See [VALIDATION.md](VALIDATION.md). Exported-record interpretation
and scalar prefix expressions are not a substitute for that native replay.

## Pins, novelty and overlap

Exact base: **`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`**.
At that base the selected record is PR942, conditional
**kappa 0.001661960547713947**, complex-bound, retaining PR589 on PR555.
The selected assembly gives bit c `0.001733427039589844234749`.
The actual candidate parent is **PR952**, head
`11d24706f06e95271804c9438869546724c67aab`, retained under
`research/r439-six-wire-boolean/`. [SOURCES.json](SOURCES.json) binds all
consumed sources; text hashes normalize CRLF to LF, immutable gzip inputs do not.

Seed **15**, the first OS-random draw, selected quad15 within the bit-supplier
track. The initial selected-PR589 matrix proved permutation-conjugate to Ross
Richardson's PR925 frame267 matrix, so its minimum is credited to that prior
result rather than presented as a new discovery. The one evidence-driven pivot
kept frame281 but used PR952's distinct integer transfer: entry sum 42 rather
than 58 precludes permutation conjugacy. PR952's bounded pivot-order Boolean
scan did not certify an optimum for this transfer; this work exhausts the
positive-addition factorization class and a separate reverse-envelope class.

Discovery exhausts **41,235 states / 209,118 edges**, including 88 dead ends,
for the PR952 fixed transfer. The independent first-ADD column search expands
all layers below 12, visiting **41,203 states**. Its separate paired-column
search establishes the guarded minimum 13 using **735 states**. These methods
are independent implementations, not independent human review. Domain,
one-million-state stopping caps, seed and the earlier conjugate exploration
are recorded in [CLAIM.md](CLAIM.md) and [WITNESS.json](WITNESS.json).

The final overlap refresh found **Gareth Davidson's concurrent PR980**, head
`ba1cf68bef0c97dfb120add04304e2de0db6f29c`, which reports 240 further ADD savings
by full-prefix admission across 42 blocks. Its actual candidate still uses
the same **13-ADD frame281** program as PR952. [OVERLAP.json](OVERLAP.json)
records the extracted block and immutable artifact hash. Our 12-ADD factor
and exact 12/13 class boundary remain distinct evidence; no priority is claimed
for the general full-prefix admission idea, and no combined PR980 word or
additional whole-word saving on that candidate is claimed or tested.

## Scope

The minima apply only to positive elementary additions on these **six labelled
registers with the exact integer transfer fixed**; repeated destination writes
are allowed. Other Boolean lifts, subtraction, extra registers and free
permutations are outside the class. See [PROOF.md](PROOF.md) for the recurrence,
reverse guard and complete cost. The native multistage replay, hosted supplier
adoption, global invoice and outer assembly remain undone. Inherited all-size
compiler, mutable-source/common-label realization, whole-call hosting,
precision/tape and analytic transfer obligations remain. This is not a formal
proof of the full multiplication theorem or a new selected supplier.

Prepared for **@woklerx with substantial OpenAI Codex assistance**. Predecessor
credit and Apache-2.0 licensing are detailed in [NOTICE.md](NOTICE.md).
