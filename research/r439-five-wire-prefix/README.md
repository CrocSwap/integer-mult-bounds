# Five-wire phase-A resynthesis on the R439 bit supplier

**Finite construction; no new kappa.** On Gareth Davidson's frozen PR904
candidate, 88 disjoint phase-A windows save **170 ADDs plus 170 literal reverse
cleanup ADDs**, reducing the complete local word from **24,051 to 23,711 ADDs**.
Relative to selected PR589, the combined reduction is **594 ADDs** (24,305 to
23,711). The 254 predecessor ADDs are credited to PR904, not rediscovered here.

| Complete local resource | PR904 input | This candidate |
| --- | ---: | ---: |
| Phase A ADDs | 2,015 | 1,845 |
| Phase B ADDs | 922 | 922 |
| Phase C ADDs | 2,502 | 2,332 |
| Phase D ADDs | 18,085 | 18,085 |
| Scatter ADDs | 527 | 527 |
| Total ADDs | 24,051 | 23,711 |
| Exported records | 26,980 | 26,640 |
| Forward positive row-sum bound | 43,671 | 41,311 |
| Reverse positive row-sum bound | 928,888 | 843,188 |
| Local payload prefix bits | 92 | 92 |
| Paid rank mass | 5,129 | 5,129 |

No helper, copy, restoration, source access or frame move is free in this bill.
All original physical registers are retained. Every register's ordered MOVE
sequence and every COPY/ERASE record agree. The nine rank-seven totals, decoder
constant 63, and paid histogram
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` agree. The 5/9/11-stage words save
1,700 / 3,060 / 3,740 ADDs respectively; all bridge and copy bills remain paid.

## Reproduce

From the repository root, with Python 3.11+, a C++17 compiler and Boost headers:

```sh
BOOST_INCLUDE=/path/to/boost-headers python3 -I -B research/r439-five-wire-prefix/verify.py
```

The include directory must contain `boost/multiprecision/cpp_int.hpp`; omit the
environment assignment when headers are in `/usr/include`. `CXX` can select a
compiler. Expected final marker:

```text
PASS_R439_FIVE_WIRE_PREFIX: 88 rewrites; 340 further ADDs saved; H1-H5; 5/9/11 stages; 17 controls; no new kappa
```

This rebuilds the entire bounded search, compares every decoded artifact field,
checks all 32 Boolean inputs of each replacement with an implementation separate
from the row-mask search, checks both positive transfers on unit columns, runs
the unchanged source geometry/frame/661-column checker on both complete words,
and compiles/runs unchanged native legality and 5/9/11-stage checks on
883/1,327/1,549 columns. Seventeen local controls and 96 omitted-bridge controls
must succeed. Use `--output /absolute/new/path --receipt /absolute/new/file.json`
to retain native binaries, logs and a deterministic receipt. Nothing is
regenerated in an existing source package.

## Exact scope and novelty

OS assignment seed **10** selects the bit track and the CNOT generator tie order.
Initial exact base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Rebased for submission onto `47481c89fd30a43f8f882eb4b391e89c29273fd0`;
all twelve upstream source/checker pins are unchanged.
PR904 dependency: `883a0bdf7792693e57c16be660824b57aacfbe05`.
Selected PR589 source: `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
[SOURCES.json](SOURCES.json) pins every source/checker and vendored PR904 file.
The PR904 snapshot includes its original notice, license and search code.

The domain is every original contiguous phase-A window on that frozen PR904 word
with exactly five distinct source/helper registers, one common frame and at most
12 elementary ADDs. **1,805 windows** (lengths 3 through 11), **1,097 distinct
maps**, are completed. Each depth-three ball contains 2,851 states: histogram
`1,20,260,2570`. A meeting of two balls supplies a circuit of length at most six.
The generator order is shuffled once with `random.Random(10)`; each ball retains
only its first BFS path to each matrix. Among the resulting distinct nominees,
the first strictly shorter one passing both growth guards and full participation
is chosen by (length, lexicographic circuit). There are 509 windows with a shorter
nominee, 461 guarded windows and 88 compatible selected windows. A weighted
interval dynamic program maximizes savings among these nominees. The stopping
rule is completion of this single scan, with no rescanning of the rewritten word.

This extends PR904's GL(2..4,2) window domain on its **actual output**, rather than
resubmitting that construction. For context, rerunning PR904's unchanged
seed-11 algorithm once on exactly this input gives 40 A plus 2 B ADD savings,
or **84 with cleanup**; that comparison is reproduced by the command above.
The 84 and 340 are alternative passes and must not be added. This comparison is
not a four-wire saturation result or an optimality theorem. A fifth participant
is not claimed intrinsically necessary for every saving.

The search does not enumerate every circuit representation of each matrix,
all five-wire circuits, all schedules, or later fixed points. No global or local
minimum is claimed. PR886 closes fixed-order frame reassignment; this work changes
the circuit. Concurrent whole-block PR925, prefix PR904 and compensation
PR915/926 are credited as related work; only the explicit PR904 composition is
claimed here. A final refresh also found PR933 (head
`b9348c6907516e55dc07e135ad4d7a480d4f9840`): its exact relocation/reframing
and Steinberg search addresses the paid bit moment on PR589, whereas this
construction reduces native ADD counts on PR904 without changing that moment.

## Why the replacements are valid

A CNOT `d ^= s` is an invertible F2 row operation. For each selected window, the
independent checker evaluates all 32 inputs and obtains exactly the old outputs.
Thus it preserves arbitrary dirty inputs at that boundary, including all helper
dirt, with no extra workspace. A representative first window at frame 266 uses
physical registers `[226,236,238,244,247]`, renamed `[a,b,c,d,e]`:

```text
old: e ^= d; e ^= b; e ^= a; e ^= c; d ^= b; d ^= a
new: d ^= a; d ^= b; e ^= c; e ^= d
```

Both end with `d = d0+a+b`, `e = e0+d0+a+b+c`. It saves two A ADDs and two
cleanup ADDs. Each window's full old and new circuit is in CERTIFICATE.json.

All participants still occur at the same common frame, preserving their entry
climbs and exit frames; no target is touched in A. Outside the disjoint windows
A is identical, and B/D/scatter are identical. C is rebuilt as the literal
reverse of the z-destination gates of A then B at the full frame, preserving
H4 rather than substituting a weaker endpoint condition. The unchanged source
checker separately validates H1-H5 and U/J/K/U-inverse on all 661 columns.

For precision, replace XOR by addition over nonnegative integer unit vectors.
The new window transfer is entrywise bounded by the old transfer, **in each
order**. Monotonicity carries this inequality through every nonnegative incoming
bound and subsequent operation. Every intermediate coordinate is at most its
window-final value, since these positive updates only increase coordinates.
Together with the reverse guard this applies to both directions and to paired
cleanup. This does not assume cancellation over the integers. The native
checker independently recalculates the complete bounds in the table.

## Limits, attribution and review

At the initial base, the selected conditional kappa was **0.001661634653669567**.
During final refresh, maintainers selected PR890 at **0.001661957774647029**,
retaining the identical PR589 bit supplier (see the current selected record and
`docs/research/community-frontier890-review.md`). This contribution changes
neither selected record. It is a finite circuit saving: the paid profile and
bit moment are unchanged, and the complex supplier remains binding.
No changed global hosted emitter, full finite invoice, outer assembly, or stronger
kappa is supplied. The inherited all-size/compiler, common-label/mutable-source,
whole-call hosting, precision/tape and analytic obligations remain. Native
multi-stage replay is not a formal proof of the multiplication theorem.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI Codex
assistance**, including a separately tasked AI checker. No independent human
review is claimed. Credit Gareth Davidson (@bitplane), PR904, and Jeffrey Cox
(@namredips), PR754, for the predecessor exact small-circuit/positive-guard/interval
method; DreamingOfClouds PR589 on eumemic's PR555/543 and the retained source
lineage; Sagar Thakrar and the native checker authors. See [NOTICE.md](NOTICE.md)
and the preserved source notices. Apache-2.0.
