# Retained backing across literal interchange calls

The existing elementary interchange erases its scratch but retains its backing
arrays. This package answers [PR5188](https://github.com/CrocSwap/integer-mult-bounds/pull/5188)
open question 2 with an exact per-tape capacity theorem and a grant for any
finite successful call history. It audits the unchanged 4,589-instruction
program; it adds no new interchange implementation or multiplication bound.

A fixed-volume example shows why the grant must use separate tape maxima:

| Call `(H,A,G,S)` | Fresh owner alone | Same owner after this call |
| --- | ---: | ---: |
| `(1,64,1,1)` | 811 | 811 |
| `(1,1,64,1)` | 811 | 823 |
| `(1,1,1,64)` | 811 | 835 |

Every call has volume 256, restores private heads and erases all private data.
Different numerical roles attain their maxima in different calls. Therefore
the maximum standalone total, 811, undercounts the retained history by 24 cells.
This is a counterexample to an accounting shortcut, not a source-program bug.

## Quantified result and boundary

For each admitted call, `H>=0`, `A,G,S>=1`, `V=A*4^H*G*S`. Let `c_r` be the
exact fresh capacity of private role `r` in [PROOF.md](PROOF.md)'s table, and
let `a_r>=1` be that role's already allocated, blank entry backing after init.
For every finite successful history, including consumption or paid installation
of every output, its retained private capacity is exactly

```text
K(k) = sum_r max(a_r, c_r(call1), ..., c_r(callk)).
```

The table includes all eight numerical and seven payload roles, LEFT/RIGHT
markers, H=0's owned identity, H=1's unused B1, transient numerical writes,
repeated calls and terminal close. Erasure and close do not shrink backing.
Given maximum historical volume `Vmax>=1`, a fresh minimal bank satisfies

```text
K(k) <= 4Vmax + 8 bit_length(Vmax) + 23.
```

For arbitrary blank entry backing of total `K0`, a sufficient grant is
`K0 + 4Vmax + 8 bit_length(Vmax) + 8`. Neither bound grows with the number
of calls. A bound using only the latest call's volume is invalid after a
larger call. The private visited span has a separate conservative fresh bound
`4Vmax + 8 bit_length(Vmax) + 38`: reads/moves can reach an implicit blank
cell without allocating it. This is not an equality between visited and
allocated cells.

At the predecessor's actual CRT u/back geometry `(2,1,1024,12)`, the exact
fresh private capacity is **786,497 cells**, below the uniform grant 786,599.
This is an arithmetic application of the quantified theorem, **not a new
execution** of the 196,608-bit caller.

The theorem assumes canonical disjoint borrowed ports and successful calls.
Input descriptor production/replacement, borrowed arrays and caller-retained
old inputs remain separately owned and charged. Dirty entry storage, failures,
interruptions and rollback are excluded. These are logical tape cells, not
CPython heap capacity or metadata. The fixed instruction word is constant
program memory. Source endpoint correctness and time bounds remain inherited;
no new binary alphabet lowering, recursive/global reserve, whole raw/repair
composition, supplier admission or selected-frontier change is claimed.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/interchange-retained-backing --check-only
python3.12 -B scripts/research_package.py --package research/interchange-retained-backing
```

The registered runner executes ordinary and optimized modes. Direct portable
replay is `python3.12 -I -O -W error -B research/interchange-retained-backing/verify.py`.
It authenticates six live predecessor files before compiling their captured
source bytes; it does not import predecessor bytecode or run its full verifier.
Ordinary replay is read-only and compares the complete typed
[RESULT.json](RESULT.json). `--write-result` is explicit authoring mode.

The primary checker executes the original machine on 110 fresh geometries
(H0..3 with A/G/S1..3, plus H4/H5), every order of the three fixed-volume
calls, and shrinking-volume and preallocated-owner histories. It checks each
output against a coordinate oracle, protected inputs, private cleanup/head
return, exact per-role retained lengths and the visited-span allowance.
A capacity guard intercepts every actual allocation; omitting the OUTPUT
marker's cell makes the real H0/V1 execution fail.

The separately authored [independent checker](independent_check.py) represents
nonblank cells sparsely and retains allocation lengths separately. It imports
no geometry/cap formula or source interpreter. On fresh and warm mixed
histories, it compares all 16 entry boundaries with the original machine:
full allocated contents including blanks, lengths, heads, returned status and
exact instruction/read/write/move counts. An additional primitive probe
separates implicit-blank reads/moves from allocating writes. Executing the
same source word under wrong accounting that allocates reads or releases
erased backing is rejected. Other controls detect max-of-totals, discarded
entry backing, erased-content-only and current-volume-only grants.

Finite checks corroborate the source proof; they do not prove all histories
by enumeration. No historical suite, full source-sized caller, Lean/Docker,
selected supplier replay or physical heap benchmark was run.

## Task and overlap

[Task metadata](TASK.json) refines priority 7 `uniform-transfer-audit` to the
explicit #5188 capacity handoff. Canonical base is
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`; exact blobs/SHA256 pins are in
[SOURCES.json](SOURCES.json). The canonical claim/result is
[Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19148693).

The historical-maximum principle is already present in Ross Richardson's
[numerical-arena](../selected-numerical-arena-backing/README.md) and
[packet-backing](../selected-packet-retained-backing/README.md) audits. Those
concern different allocators/owners. The new result derives this literal
callee's exact extents and an actual mixed-history discriminator. The live
#4990 descriptor-production work, fixed-alphabet translation and complete
raw/repair composition are distinct tasks.

## Open next questions

The family decision is **narrow, then stop**. The next useful question is a
complete caller bank grant: identify one raw CRT call sequence, combine this
bank with simultaneously live borrowed/output/descriptor/ROM roles, and retain
object identities and old input ownership at every boundary. The current
private-bank theorem alone does not supply that global ledger. A fixed-block
binary translation must also charge its encoded backing; this result gives
cells in the existing five-symbol model only. [TASK.json](TASK.json) records
first steps and blockers.

## Credit

JoyboyBrian/#5188 supplies the literal program and open capacity question;
#5162, Jose Manuel's physical ordinary wrapper and the retained
PR2809/PR2753 stream/cardinality lineage supply its source context. Cinna Davis,
Hiroki KUMAZAKI, Douglas Colkitt/OpenAI and all archived notices retain their
CRT/physical-source credit. Ross Richardson's separate backing audits retain
their accounting-method credit. All predecessor bytes are unchanged.

Prepared by Hiroki KUMAZAKI (@kumagi) with substantial OpenAI Codex assistance,
including separately authored proof/interpreter checks. This is not independent
human or proof-kernel acceptance. Apache-2.0. Selected conditional kappa remains
`.00302015`.
