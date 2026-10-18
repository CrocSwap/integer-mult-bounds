# Exact five-wire windows on the composed R439 bit word

**Finite construction and bounded optimality certificate; no new κ.** Starting
from Gareth Davidson's frozen PR1122, 59 disjoint A windows save 80 ADDs and
another 80 in literal cleanup: **10,652 → 10,492 complete local ADDs**.
The complete five-wire metric proves that 160 is the maximum saving from the
declared one-pass window class. This is not an unrestricted circuit optimum.
The inherited semantic-D exception remains: the original owner's **H2 and
K-equals-D predicates are false**, just as for PR1122. No supplier adoption is
claimed.

| Complete local resource | PR1122 | This word |
|---|---:|---:|
| A ADDs | 1,706 | 1,626 |
| B ADDs | 800 | 800 |
| C ADDs | 2,071 | 1,991 |
| D ADDs | 5,548 | 5,548 |
| Scatter ADDs | 527 | 527 |
| Total ADDs | 10,652 | 10,492 |
| Exported records | 13,581 | 13,421 |
| Forward positive bound F | 15,223 | 13,667 |
| Reverse positive bound B | 3,910,388 | 3,758,418 |
| Local sufficient payload bits | 92 | 91 |
| Nine-stage sufficient payload bits | 176 | 175 |

The physical 104/192-bit charges stay unchanged. So do all 661 source, target
and helper registers, the private scatter-copy lifetime, nine COPY/ERASE pairs,
2,911 MOVE records, each register's ordered frame path, and the paid histogram
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` of rank mass 5,129.
The full 5/9/11-stage ADD bills, including 666/1,998/2,664 bridge ADDs, are
**53,126 / 96,426 / 118,076**: savings of 800/1,440/1,760 from PR1122.
No helper preparation, inverse, restoration, copy, source read, or bridge is
omitted. The total reduction from selected PR589 is 13,813 ADDs, of which
13,653 belong to the credited predecessor chain.

## What changed

Assignment seed **13** selects the bit track and deterministic generator tie
order. [CLAIM.json](CLAIM.json) records the pre-computation task and alternatives.
The base is `c0e3631dc24e3c24a861f7d3d79e0608481cccec`; the exact PR1122 input is
`a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf`, preserved with its notice and license.

Ross Richardson's PR936 examines representatives of at most six ADDs on its
PR904 input. Here a complete BFS covers all **9,999,360 labelled GL(5,2)
matrices** under the 20 directed ADD generators, with no free permutations.
An independent C++ checker validates descending witnesses and all
**199,987,200 directed edges**, certifying every distance. Optimal CNOT
Cayley-graph search is established work, including Christensen, Jørgensen,
Pavlogiannis and van de Pol's
[RC2025 paper](https://cs.au.dk/~pavlogiannis/publications/papers/rc25.pdf) and
[CNOTter](https://github.com/Quantum-Software-Aarhus/CNOTter). This application
and its paid admission are the contribution; no priority for GL5 BFS is claimed.
No external CNOT implementation is imported.

On frozen PR1122 A, enumerate every contiguous same-frame window with exactly
five distinct participants and at most 12 elementary ADDs. The completed domain
has **1,203 windows and 986 distinct maps**. Of 319 shorter shortest-path
nominees, 68 need more than six ADDs; all 319 use every original participant.
Weighted interval selection saves 80 A ADDs in 59 windows, and all 59 pass
sequential full-word precision admission. Nine selected replacements have
length greater than six. There is one scan, without rescanning the output.

For example, original A indices `[634,643)` at frame 269 use physical wires
`[253,389,397,399,403]`, relabelled `[a,b,c,d,e]`:

```text
old: b+=d; a+=b; e+=b; a+=c; e+=c; d+=c; d+=a; c+=a; b+=a
new: b+=d; c+=b; a+=c; b+=a; e+=c; c+=b; d+=c
```

These are F2 ADDs. The matrix's exact length is seven, so no six-ADD replacement
exists. All 32 Boolean inputs are independently checked. Restricting this
package's same shortest representatives to length at most six gives an optimal
interval saving of only 72 A ADDs. Thus removing the ceiling adds **16 complete
ADD savings** in this comparison. It is not a replay of PR936's different input,
tie order, local guards, or alternative path representatives.

[PROOF.md](PROOF.md) states the precise bounded minimum and its limits.
All nominated paths and windows are in [WINDOWS.json.gz](WINDOWS.json.gz);
[CERTIFICATE.json](CERTIFICATE.json) records the selection, every admission
trial, exact prices, and table hashes. The 64 MiB raw metric tables are rebuilt
and checked in scratch space, not committed.

## Reproduce

From the repository root, with Python 3.10+, a C++17 compiler and Boost headers:

```sh
BOOST_INCLUDE=/path/to/boost-headers python3 -I -B research/r439-gl5-shortest/verify.py
python3 -I -O -B research/r439-gl5-shortest/test_package.py
```

Omit `BOOST_INCLUDE` when headers are in `/usr/include`; `CXX` selects a compiler.
The verifier regenerates the full metric and artifacts, checks the complete
window domain and independent truth tables/interval optimum, replays every
admission with explicit COPY/ADD/ERASE, checks both full words in both directions
on all 661 formal columns, and runs unchanged native legality and 5/9/11-stage
checkers. Twenty local failures and 96 omitted-bridge failures must be rejected.
Expected final marker:

```text
PASS_R439_GL5_SHORTEST: 59 windows; 160 ADDs saved; GL5 metric; 5/9/11 stages; 20 controls; no new kappa
```

Use `--output /absolute/new/path --receipt /absolute/new/file.json` to retain
all tables, native binaries, logs and the deterministic receipt. Verification
does not write to the source package. Source containers are byte-pinned;
regenerated compressed artifacts are compared through their complete decoded
canonical contents. [VALIDATION.md](VALIDATION.md) records the independent
environment replay and controls.

## Scope and credit

PR936 supplies the earlier five-wire method; Davidson PR904/952/980 and PR1122
supply the predecessor A and global admission/cleanup pattern. PR1122 includes
Sagar Thakrar's PR1062 B/star-D composition, Aaron Wang's PR1015 B work, Ross
Richardson's PR923, Sricharan Vagvala's PR967, and Davidson PR915/926. Selected
PR589 on PR555/543 and the native checker authors retain their credit.
[NOTICE.md](NOTICE.md) and unchanged vendored notices give the source lineage.

Nearby PR1127 performs commuting Steinberg contractions; this package does not
apply that rewrite system. PR1048's general exact-exclusion claim remains
unaccepted in the selected review and is not invoked here. Fresh overlap through
PR1178 found no complete GL5 application to this frozen word. Upstream refresh
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` leaves all 15 base inputs unchanged.
Selected PR1094 still has κ `836330098538459/500000000000000000` and retains PR589.

There is no changed hosted emitter, complete multiplication invoice, selected
record, paid recursive profile, runtime benchmark, or stronger exponent here.
All-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape and analytic obligations remain. Native finite replay does not
prove the full multiplication theorem or discharge the inherited H2/K exception.

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. No subagents or independent human reviewers were used. Apache-2.0.
