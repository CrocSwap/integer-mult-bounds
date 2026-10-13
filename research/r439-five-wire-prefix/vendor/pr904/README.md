# Four-wire prefix resynthesis for selected R439

The selected PR589 bit word admits **95 disjoint same-frame prefix rewrites**
that save **254 exported ADDs**, including the required reverse cleanup.
The full word still satisfies the original literal interface hypotheses H1–H5.
Its paid frame histogram, 439 helpers, nine copied totals, and decoder stay
unchanged. This is a finite local supplier improvement; **no new κ is claimed**.

| Quantity | PR589 baseline | Candidate |
|---|---:|---:|
| A elementary additions | 2,130 | 2,015 |
| B elementary additions | 934 | 922 |
| C elementary additions | 2,629 | 2,502 |
| D elementary additions | 18,085 | 18,085 |
| Scatter additions | 527 | 527 |
| Exported ADDs, total | **24,305** | **24,051** |
| Exported records, total | 27,234 | 26,980 |
| Paid rank mass | 5,129 | 5,129 |
| Forward positive row bound | 49,347 | 43,671 |
| Reverse positive row bound | 1,113,070 | 928,888 |
| Computed payload prefix bits | 93 | 92 |

The inherited native payload ceiling is 104 bits. No extra registers, copies,
frames, target reads, or unpriced helper initialization are introduced.
The saved additions per 5/9/11-stage word are 1,270 / 2,286 / 2,794; bridge
additions and copy counts stay unchanged. This does not reprice a full hosted
construction or improve its selected leading constant.

## Reproduce

From the repository root, with **Python 3.12+, C++17 and Boost headers**:

```sh
python3 -I -B research/r439-four-wire-prefix/verify.py
```

`CXX` selects the compiler. If Boost is outside `/usr/include`, set
`BOOST_INCLUDE` to the directory containing `boost/`. No Python packages,
network access or Git metadata are needed. The source closure comprises the
12 immutable in-tree files in [SOURCES.json](SOURCES.json).

Expected final line:

```text
PASS_R439_FOUR_WIRE_PREFIX: 95 rewrites; 254 ADDs saved; H1-H5; 5/9/11 stages; 12 controls; kappa unchanged
```

The command reproduces the bounded search, checks the certificate with a
separate column-state implementation, replays both complete words using the
unchanged PR589 checker, compiles the unchanged native checkers, and compares
the full deterministic receipt to [EXPECTED.json](EXPECTED.json). Temporary
outputs are removed by default. To retain everything:

```sh
python3 -I -B research/r439-four-wire-prefix/verify.py \
  --output /tmp/new-r439-run --receipt /tmp/new-r439-receipt.json
```

Both paths must be new. `--source-root` supports a relocated minimal source
closure; the package itself can be anywhere. Reproduced gzip files are
compared by canonical decoded JSON, including every field, rather than by
compressed bytes. The immutable baseline archive retains its exact byte pin.
For nomination alone, run `build.py --output /tmp/new-r439-build`; the
independent and native checks remain necessary to accept that output.

Eight fast package controls can also be run with
`python3 -I -B research/r439-four-wire-prefix/test_package.py -v`.
They cover source corruption/missing files, strict typed JSON, recompression,
and preservation of existing output files; the suite also runs under `-O`.

## Evidence and bounded search

The fresh OS draw was **11**, selecting the bit-supplier track. Three candidates,
overlap review, source base and stopping rule appear in [CLAIM.json](CLAIM.json).
The scan examines all **3,296 original contiguous windows of length at least
two**, confined to one frame and at most four source/helper registers in A/B.
One-gate windows cannot yield a strict saving. Of these, 275 have a shorter
canonical shortest circuit; 264 pass the participant and both-order positive
guards. Disjoint interval selection retains 85 A windows and 10 B windows.

The certificate lists each original interval, frame, physical registers and
old/new elementary words. All 95 nominated circuits attain the exact
unrestricted GL(3,2) or GL(4,2) distance for their own maps and participant
sets. The verifier independently enumerates GL(2..4,2): **6 / 168 / 20,160
states**, and checks **242,940 directed edges** of the distance potential.
It checks 190 positive-matrix inequalities, one in each order per rewrite.
The search considers one seed-11 shortest-path representative per window;
it makes no claim of a globally optimal full circuit or exhaustion of all
guard-admissible representatives. See [PROOF.md](PROOF.md).

The unchanged source checker verifies the E8 geometry, all 636 frames,
all **661 independent input columns**, arbitrary helper dirt, source/helper
restoration, target increment, retained-total ranks and literal H1–H5 for
both words. Native legality checks every exported record and copied-center
lifecycle. Native 5/9/11-stage checks cover **883 / 1,327 / 1,549 columns** per
word and reject **96 omitted-bridge controls** across the two words. Twelve
additional local/certificate controls reject incorrect maps, frames, costs,
overlap, target use, positive-growth cancellation, stale cleanup and related
failure modes. [VALIDATION.md](VALIDATION.md) records the executed environments.

## Relationship to prior work

This applies **Jeffrey Cox (@namredips)'s PR754 exact small-GL and interval
method** to the selected R439 **A/B prefix**, with paired C cleanup preserving
literal H4. PR754 optimized the historical R420 cleanup and certified the
more general semantic H4′ interface. The synthesis method itself is prior work.

PR792 certifies a different mini-node interleaving class. PR886 closes frame
retiming for the fixed selected word; this changes the elementary word.
PR827's cleanup-frame lower bound also leaves scalar circuit savings open.
PR844/873/880/884/857 and PR891 optimize or obstruct whole B blocks in other
classes. This submission claims the pinned PR589 baseline comparison only;
compositions with those other candidates are not certified here.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Selected word: PR589 `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
The selected #799 result remains `1661634653669567/10^18`.
The full compiler, recursive/tape execution, precision, hosting and analytic
obligations recorded by that construction remain separate. These finite
checks do not formalize the full multiplication theorem.

Prepared for **Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance**. One AI agent performed the work; implementation independence
refers to algorithms and retained source checkers, not separate human review.
See [NOTICE.md](NOTICE.md) for source and method attribution. Apache-2.0.
