# R439 frame 519: two fixed factors save twenty local ADDs

**Finite circuit construction; no new kappa.** The selected PR589 tuned
R439 word's phase-B block `B[163:205]`, frame 519, is shortened from 42 to
32 elementary additions. Its mandatory literal reverse cleanup is rebuilt,
saving another ten additions. The complete exported local word therefore
uses **24,285 rather than 24,305 ADDs**. All twelve block registers already
exist and their full-word frame paths are identical.

| Quantity | Base PR589 word | Candidate |
|---|---:|---:|
| First fixed factor, `B[163:182]` | 19 ADDs | 16 ADDs |
| Second fixed factor, `B[182:205]` | 23 ADDs | 16 ADDs |
| Block | 42 ADDs | 32 ADDs |
| Complete local ADDs, including cleanup | 24,305 | 24,285 |
| Complete record stream | 27,234 | 27,214 |
| MOVEs / COPYs / ERASEs | 2,911 / 9 / 9 | 2,911 / 9 / 9 |
| Forward positive prefix bound | 49,347 | 49,347 |
| Reverse positive prefix bound | 1,113,070 | 1,031,082 |
| Payload prefix | 93 bits | 93 bits |
| Paid rank mass | 5,129 | 5,129 |

The local paid profile remains
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`.
The nine COPY ranks remain seven, so the decoder constant remains 63.
The exponent moment is unchanged; this contribution improves a circuit
constant and its precision envelope. It claims no larger bit exponent or kappa.

## Exact object and source pins

Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The selected record at that base is conditional kappa
`1661634653669567/10^18 = 0.001661634653669567`, PR799 with PR589.
Reviewed heads: PR589 `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`,
PR799 `80e6463157cfc80b85af09e7e2f14748fe2dac60`.
[SOURCES.json](SOURCES.json) pins the consumed word and checkers plus this
selected-record context by SHA256. Committed supplier inputs, the selected
frontier and `upstream/` are untouched.

The block registers are
`[15,23,30,41,49,53,59,70,75,82,91,96]`; each is a source register.
[CANDIDATE.json](CANDIDATE.json) contains both exact integer matrices and the
complete replacement programs. The splice is defined by `verify.py`; its
canonical JSON word digest and native record digest are in
[CERTIFICATE.json](CERTIFICATE.json). Generated streams use temporary output
directories rather than changing the selected package.

## Mechanism and complete cost

The cut is before original `B[182]`. Both factors are integer-positive
linear maps with binary entries and diagonal one. An existing register can
supply a sum after it has reached its factor output. For example, the first
factor realizes `x30 += x70+x75+x82` before `x59` consumes that entire sum;
the second realizes `x70 += x15+x59` before `x75` consumes it. The program
also reuses other realized rows. The exact factor maps, including every
register's entry value, are preserved over the integers. Their product and
the all-column F2 word endpoint are independently checked.

There is no additional helper, clean initialization, source-access operation,
frame, COPY, restoration call or recursive child. Each replaced addition reads
one existing register and writes another at the same existing frame. Every
register follows the same frame path. Cleanup is the literal reverse of all
source/helper writes in A and B, now with ten fewer gates. Thus the complete
local change is ten forward and ten cleanup additions saved, with all paid
frame and copy costs unchanged. The exporter recomputes the entire record
stream, and native legality and 5/9/11-stage checks accept it.

The local reverse positive matrix is entrywise dominated by the original:
22 entries decrease and none increases. The full exported stream's forward
and reverse cancellation-free bounds are recomputed, giving
`64 * 49347^3 * 1031082^2 = 8176146235754724278798992128 < 2^104`.
This remains 93 bits. No new global hosting or outer-assembly certificate is
claimed: unchanged rank moments cannot create an exponent gain from these
ADD savings alone.

## Bounded search and class minima

OS assignment seed **02** selected the bit-supplier track and block index 2.
The discovery algorithm itself is deterministic. It exhausts the two fixed
factors' destination-once positive-addition class: a register reaches its
final factor row once, with each other register used at most once as a donor.
Already realized donors supply their output rows; other donors supply entry
singletons. The factor matrices and cut are fixed. No arbitrary factorization,
subtraction, new register or intermediate multiple-write schedule is searched.

For state S and unrealized destination d, let
`g_d = M_d - e_d`. Available donor j is `M_j` if j is in S, and `e_j`
otherwise. Enumerating distinct donor subsets whose integer sum is exactly
`g_d` gives the edge cost. Every legal schedule in this class corresponds to
one path through realized-register subsets; conversely every such path gives
a legal schedule. Minimizing path cost therefore gives the exact class minimum.
Nonnegative rows with diagonal one ensure donors outside the support of
`g_d` cannot participate, justifying the discovery cache restriction.

`search.py` computes a forward dynamic program with a bit-mask exact-cover
solver. `verify.py` imports no discovery code: it enumerates integer subset
sums and runs a backward Bellman recurrence. Both exhaust 4,096 states and
24,576 state/destination pairs per factor. They agree on 20,352 / 19,456
feasible edges and minima **16 + 16**. Identity rows can be realized at zero
cost. The stopping rule is completion of that finite domain. These minima
do not assert unrestricted XOR optimality, or impossibility of other cuts.

## Reproduce and review

Python 3.11+ standard library, from the repository root:

```sh
python3 -I -B research/r439-frame519-seed02/verify.py
```

Expected:

```text
PASS_R439_FRAME519 adds=42->32 local_ADDs=24305->24285 minima=16+16 columns=661 boolean_inputs=4096 controls=11 reverse_bound=1031082 payload_bits=93 no_new_kappa
```

This checks source pins, exact integer maps, both class minima, all 4,096
Boolean block inputs, all 661 dirty-input columns, all register frame paths,
the pinned owning H1-H5 interface, the complete native record invoice and
eleven corruption controls. The stale-cleanup control intentionally shows
that an equal F2 endpoint alone need not satisfy H4's literal-reverse contract.
The exact certificate is checked against fresh calculations, rather than
used as the authority for those calculations. Normal and optimized Python pass.

`python3 -I -B research/r439-frame519-seed02/search.py` deterministically
regenerates `CANDIDATE.json`. To reproduce the native certificate, install a
C++17 compiler and Boost headers, then run:

```sh
python3 -I -B research/r439-frame519-seed02/native.py
```

Set `CXX` to the compiler executable and `BOOST_INCLUDE` to the directory
containing `boost/` when needed. The command first runs the Python verifier,
then compiles the unchanged legality and column checkers once for both words.
It retains every native receipt field except elapsed seconds and a temporary
stream pathname; [NATIVE-CERTIFICATE.json](NATIVE-CERTIFICATE.json) records
the results. Expected final line:

```text
PASS_R439_FRAME519_NATIVE words=2 columns=883/1327/1549 bridge_controls=96 record_controls=3 local_ADDs=24305->24285 payload_bits=93
```

[VALIDATION.md](VALIDATION.md) records the executed environment and controls.
The 883/1,327/1,549-column native replays are finite F2 checks and signed-prefix
invoices, not a formal proof of the full multiplication theorem. Full hosted
global invoices, outer assembly, selected cold replay and remote CI were not
rerun. All-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape and analytic transfer remain the selected review's inherited
assumptions. No composition with another pending circuit contribution is certified.

## Concurrent work and credit

[PR891](https://github.com/CrocSwap/integer-mult-bounds/pull/891), Aaron Wang
(@navinor), reports that frame 519 has no whole-block single-write program
in its class. This construction uses **two fixed factors**, allowing a
register to be realized again in the second factor. It supplies a concrete
new circuit outside that negative result's class, rather than rerunning its
closed search. PR891's frame-506/523 witnesses are different objects.

[PR844](https://github.com/CrocSwap/integer-mult-bounds/pull/844), Gautam Gupta
(@gautamgpt1), supplies related fixed-factor scheduling on frame 520;
[PR873](https://github.com/CrocSwap/integer-mult-bounds/pull/873), Aaron Wang,
supplies whole-block scheduling on frame 508. Their methods motivated the
class and verification obligations; neither implementation is imported.
PR880, PR884 and PR857 work on frames 507, 521 and 523. PR848's restored
copy-path sharing obstruction and PR827's cleanup-frame bound concern
different mechanisms.

The final refresh also found **Gareth Davidson (@bitplane),
[PR904](https://github.com/CrocSwap/integer-mult-bounds/pull/904)**,
head `883a0bdf7792693e57c16be660824b57aacfbe05`. Its checked-in interval
certificate contains one frame-519 replacement, `B[200:204]`, saving one
forward ADD and its cleanup counterpart. This result covers the whole
42-gate block, saving ten forward ADDs and ten cleanup ADDs, and supplies
exact fixed-factor class minima. The two contributions were developed
independently; this package imports no PR904 code and certifies no combined
saving. Its broader A/B construction has larger total savings on other
regions. The inspected PR904 certificate SHA256 is
`e29dcde966ccfffdc83b25685729a59745e8c3938af8770a38d850e5e8fc7495`.

Base construction and interfaces: **eumemic** (PR543/PR555),
**DreamingOfClouds** (PR545/PR589 and PR503/PR510). Record export and native
checking: **Dylan Crow**, **DaysSky**, **Zhihao Chen**, and the retained
construction/checker lineage. Selected assembly: **Jeremy Kothe**,
**Chafik Boukhalfa**, and the predecessors credited in its review.

Contribution by **Ross Richardson (@RossRichardson)**, prepared with
substantial **OpenAI Codex assistance** in analysis, code, verification and
writing. Apache-2.0 under the repository license. No independent human
review is claimed.
