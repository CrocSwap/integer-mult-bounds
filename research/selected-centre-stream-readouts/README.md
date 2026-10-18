# Which terminal stream detects selected centre errors?

**Exact finite result in a common-frame scalar projection; no new supplier or
kappa.** Observing only final X hides **128** independent centre-error directions.
Observing only Y hides **149**, including **21 cancellations among individually
visible errors**. The complete ordinary endpoint detects all 1,152 directions,
independently corroborating [ywz65's PR2622](https://github.com/CrocSwap/integer-mult-bounds/pull/2622).

PR2622 asks which weakened final readout admits an error kernel. This answers
that question for the two terminal stream halves. A separately written reverse
adjoint compares every response coefficient with PR2622's pinned forward digest,
then certifies both quotient kernels. No predecessor implementation is imported.
The two checking methods here have the same AI-assisted author; no independent
human or subagent review is claimed.

## Model and exact result

Use the selected PR1094 **480-helper** word and complete 144-call schedule on
14,336 physical owner families. Inject an independent scalar error immediately
after each of eight literal rank-eight `center` events per call. Retain all
scalar instructions, shared helper owners, private clears, full continuations,
144 paired bridges and 16 signed terminal exchanges. Frame moves, endpoint and
residual adapters, idle factors, padding and address actions are explicitly
projected to identity, as in PR2622. This projection is not asserted to preserve
native operator rank.

Compared runs have the same arbitrary ordinary inputs. Write `R e` for the final
ordinary-owner difference caused by 1,152 error values `e`. At the **final**
endpoint, after signed exchanges, each of the sixteen replicas has four pairs
of 112 X and 112 Y owners. Define

```text
X = {owner : (owner mod 224) < 112}
Y = {owner : (owner mod 224) >= 112}.
```

These disjoint readouts each retain 7,168 actual owners.

| Final readout | Rank over Q and C | Kernel dimension | Individually invisible sites | Further dependencies among nonzero columns |
|---|---:|---:|---:|---:|
| All ordinary owners, R | 1,152 | 0 | 0 | 0 |
| X only, P_X R | 1,024 | 128 | 128 | 0 |
| Y only, P_Y R | 1,003 | 149 | 128 | 21 |

The complete X kernel is the span of the 128 coordinate directions listed in
`readouts.X.zero_columns` in [RESULT.json](RESULT.json). The Y kernel has its own
128 coordinate directions plus the 21 rational vectors in
`readouts.Y.noncoordinate_kernel_basis`. This displayed Y basis has 19 vectors
of support two, one of support four and one of support eight; these counts
describe the basis, not a minimal-support classification of the entire kernel.
Index `8*c+k` means chronological call index `c` and centre `k`, rather than the
call's time field. All kernels are recomputed and checked on every observed owner.

## Concrete cancellation and its restoration defect

Set every error to zero except:

```text
error  8: -4   (time 1, replica 8, stage 0, forward, centre 0)
error 40: +1   (time 5, replica 8, stage 1, backward, centre 0).
```

Each column individually changes Y. Their combination has **zero final Y on
all 7,168 owners**, while **111 final X owners are nonzero**. For example, final
owners 12098, 12099 and 12102 have errors `+1`, `-1` and `-2`. Every coefficient
is in the receipt. A separate numeric forward interpreter executes all
**2,835,792 scalar instructions**, every bridge and signed terminal, and checks
the entire 14,336-owner prediction and private zero at every local exit.
Arbitrary nonzero private differences are removed by the literal initial clears.
The X-only kernel has a checked singleton witness: error 0 alone changes 56 Y
owners while X remains zero. Ordinary target/helper dirt is held fixed between
runs, not assumed clean.

These witnesses expose the missing complementary endpoint in a half-readout.
They supply no centre replacement, legal consumer or cheap realization of the
chosen errors. The complete required endpoint still detects them.

## Reverse calculation and rank certificates

Reverse `dest += q*source` by adding `q*lambda_dest` to `lambda_source`.
SCALE multiplies its covector; CLEAR kills it; COPY transfers it to its source
and then kills the destination covector. These singular and invertible rules
are tested on every input/output basis coordinate, including destination dirt.

Reverse each complete local word with independent covectors on all 704 ordinary
outputs. The private covector at an insertion site gives the error's complete
local response, including helper restoration. Initial covectors verify the
oriented transvection endpoint and zero initial-private influence. In particular,
the backward response retains all 227 affected roles. Reverse the global schedule
next: at a call with endpoint A and error response B, suffix covectors lambda
give `B^T lambda`, then become `A^T lambda`. Bridge and exchange transposes use
actual owner IDs. Call hashes, chronology, unique owner injections and stream
numbering are checked. The complete no-error transpose is identity on 14,336
owners; no shared helper is cloned or reset.

Every local/global coefficient matches PR2622's receipt. The full digest is
`b5237756bf1216f7afa6a0570b8df58ce070d8c32583022b1e5aaca7fdf9f941`.
[pr2622-result.json](pr2622-result.json) preserves its byte-exact comparison data,
with commit, path, Git blob, SHA256 and credit in [SOURCES.json](SOURCES.json).
It is not executed code. Rank alone would not establish coefficient agreement.

Exact rational elimination supplies the kernel bases. Each dependency has a
distinct last nonzero error coordinate with coefficient one, proving independence.
Listed error-column/output-owner minors give matching lower bounds: a separate
field elimination with opposite pivot order obtains these nonzero determinants
modulo the prime 2,147,483,647:

| Minor | Size | Determinant modulo 2,147,483,647 |
|---|---:|---:|
| Full response | 1,152 | 1,233,411,763 |
| X readout | 1,024 | 2,019,442,023 |
| Y readout | 1,003 | 2,092,062,824 |

Original rational denominators are invertible in this field, so these minors
are nonzero over Q and C. The rational independent kernel vectors supply the
matching upper bounds over both fields. The determinant implementation is also
checked against a permutation-sum oracle on 96 small rational matrices.

Controls reverse every bridge sign: the no-error endpoint still passes, while
response coefficients differ. Duplicating one error column lowers full rank to
1,151. Export tests run without Git, verify read-only optimized replay, and reject
archive/reference corruption, bool-for-integer receipt substitution and occupied
output paths.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/selected-centre-stream-readouts
```

The registered commands run the certificate and all three test groups. Marker:

```text
PASS_SELECTED_CENTRE_STREAM_READOUTS X_rank=1024 Y_rank=1003 full_rank=1152
```

Normal replay is read-only. Regeneration requires an absent `--out NEW.json`
path. On restricted Windows hosts, set TEMP and TMP to a writable directory
for export tests. [VERIFY.json](VERIFY.json) declares the sole live external
input; uniquely named archive members are hashed before decoding. A Git-free
export needs only this package and the pinned archive.

## Scope, coordination and credit

Scientific base: current canonical main `b017900dbb94d81afec343924c1a7fa6d540a7db`,
priority revision 5. Selected PR1094 head: `0fc329d0bec93ca7cd288eaea1295172e8789810`.
This consumes the actual 480-helper archive, rather than historical 492-helper
evidence. [TASK.json](TASK.json) records selection, the declared change from
construction to a specific output-quotient audit, exact heads, overlap and
validation. [Discussion2791](https://github.com/CrocSwap/integer-mult-bounds/discussions/2791)
is the canonical investigation. Selected and frozen inputs are unchanged.

Credit **ywz65 / PR2622** at `4ffb893a08e8868057a30a065642d0b5f647f742` for
the full response, coefficient serialization and weakened-readout question.
**PR2763** at `24b985e05d77a6005e3b18cdd4a7c33da9c0d260` audits source-history
coefficients and explicitly excludes error-response injectivity. **Sagar Thakrar /
PR2199** and **Adam Gall / PR1918** supply the projection, census and output
handoff; **commdata2338 / PR2048** and **Aaron Wang / PR2391** retain the separate
native lift/counterexample credit. Rohan Arun, Jeremy Kothe, Hao Yan, icekylinx,
DreamingOfClouds, Douglas Colkitt and the retained selected construction/compiler
lineage supply the scientific inputs. No previous rank result is claimed anew.

No new paid profile, recursive-call floor, native covariance, precision/hosting
or stream compiler, full cold replay, all-size theorem or formal-kernel review
is supplied. New calculation, certificates and code by **Arham Tahir with
substantial OpenAI Codex assistance**. Apache-2.0.

## Open next questions

Can an actual caller accept one terminal quotient while consuming or restoring
the complementary outputs within a favorable complete budget? A first step is
one explicit native caller contract and a literal replay of the two-error witness
through its consumption and cleanup. The blockers are a legal consumer, native
covariance and a fully charged implementation. These ranks justify no further
subset census or construction expansion by themselves. Structured details and
the stopping rule are in TASK.json.
