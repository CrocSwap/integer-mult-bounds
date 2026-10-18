# Selected NODE stock, coordinates and owned return

This independent conditional audit closes the enclosing **NODE/peel/split and
MERGE/return** boundary named in
[PR3041's handoff](../residual-call-refinement/README.md#open-next-questions).
For the retained PR2809 physical caller, these operations agree with PR2753's
logical node on every complete row and spectator coordinate, under the explicit
primitive, stock and successful-execution contracts in [PROOF.md](PROOF.md).
They preserve borrowed inputs and produce a distinct owned return.

The source computes `U=R/(W*N*H)` and separately stores `leading=U*B`.
For the inherited compatible reserve `K=269241600*N*H`, this gives
`U=t*9475*K^(d-1)` from `R=t*K^d`. This binds the predecessor's stock
recurrence to an actual implementation boundary. It supplies neither a new
numerical stock coefficient nor the complete physical reserve of a bootstrap
stage. The selected kappa and all frozen sources are unchanged.

The local guard alone is insufficient: at width 128, `R=K` passes that guard,
but a rank-42 child has width 84 and receives only 9475 fresh rows, which cannot
even be divided by its 28416-family factor. The source domain requires stronger
full-depth stock. This is a checked illustration of the existing PR2753/3041
qualification, not a defect in their stated theorem.

## Evidence

Five complete small payloads check **198,336 Boolean coordinates** through the
literal NODE, peel, family split and root return. A new provenance observer
follows actual copies, and a separate mixed-radix oracle checks each intermediate
family and final output. Tests check actual Boolean values, borrowed bytes and
heads, scratch return, numerical cleanup and work-marker erasure. No predecessor
expected-output checker is used as the oracle.

The cases include nonbinary unit weights, differing weights for nonempty old
prefixes, repeated empty prefixes, nonzero remainder, multiple families,
separate spectators and high fibers. Six additional **guard-only** executions
use the literal dimension-64 caller and exact GL64(F3) cardinality; they stop
before payload execution. These small-prime fixtures do not instantiate the
selected large-prime domain. The all-width statement is the written conditional
proof, not extrapolation from these cases.

Ten behavioral groups cover the stock boundary, omitted peel, family order,
lost high fibers or high stock, spectators misused as stock, wrong old-prefix
weights, borrowed-output aliasing, three changed-source pins and typed receipt
comparison. A separate 15,625-coordinate literal q=5 peel checks the
noninvolutory unit 2 and inverse 3, with a rejecting wrong-inverse control.
Source mutation controls do not change frozen files. Verification
uses explicit exceptions and remains active under `-O`.

## Exact sources and reproduction

Scientific base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The source is the main-retained PR2809 package, including its documented
selected-record loader adaptation. The predecessor heads are:

| Contribution | Exact author head |
| --- | --- |
| Jose Manuel, PR2809 fixed-role caller | `e7d93dd0de0bb81308bc3356f65eddeeb22fd712` |
| David Arias, PR2753 logical caller | `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659` |
| Nick Petalas, PR3041 residual/CALL audit | `b89c9eef729eb1e5889e2095d59a6fbf4738447d` |
| Nick Petalas, PR2989 word-order audit | `133cd8a7c5ce16a3d66e3372c5fdd9e88067d75b` |

From the repository root, with standard-library Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/selected-node-stock-refinement --check-only
python3 -I -B scripts/research_package.py --package research/selected-node-stock-refinement
```

Primary output:

```text
PASS_SELECTED_NODE_STOCK_REFINEMENT cases=5 coordinates=198336 no_new_kappa
```

The registered run authenticates live sources, compares [RESULT.json](RESULT.json),
and runs rejecting controls with optimization enabled. Replay never rewrites
evidence. `verify.py --write-result NEW_PATH` explicitly creates a separate
receipt and refuses overwrite. [TASK.json](TASK.json) records scope, selection,
overlap and remaining obligations.

The registered replay and all ten optimized behavioral groups pass on Linux
x86_64 / CPython 3.12.3. An optimized Git-free export also passes from a
separate working directory with unchanged, read-only source/evidence files.
The optimized public CLI rejects a changed exported `macro_machine.py` before
source loading. These are local author checks; no hosted CI, human review or
formal-kernel result is claimed.

## Open next questions

1. Which remaining completed primitive and fixed-capacity assumptions can be
   independently discharged at a selected source call? Start with one reached
   weighted leaf or route, preserving the whole packet and dirty state. This
   blocks using the combined conditional node/word/residual implication as
   caller admission. The selected GL64 program remains unexecuted here.
2. What numerical reserve and movement invoice does the completed physical
   caller supply under the outer wrapper's exact lifetime contract? Start with
   the joined live/backing tape categories and existing K-stock handoff. This
   proof preserves row factors but does not price all storage, preparation, H2
   or wrapper costs. Another cutoff calculation cannot fill that gap.

This is one bounded audit, with no construction-family expansion. The claim is
in [discussion #2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19001777),
following the released PR3041 handoff and its pointer in #1166.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
The new proof, observer, oracle, controls and writing are AI-assisted; no
independent human or formal-kernel review is claimed. Apache-2.0.

Jose Manuel (`jmbarrancoml`) supplied PR2809's physical compiler and PR2234's
compatible stock, and David Arias supplied PR2753's logical caller, stock and
coordinate contracts. Nick Petalas supplied the PR2989 and PR3041 independent
ordering/residual audits and concrete handoff. Retain ywz65's parking work,
the selected PR589/PR555/source527 lineage, DreamingOfClouds and eumemic, this
account's earlier descriptor/substitution algebra, and the source packages'
unchanged notices. Adam Gall, Josie Elliston, ToikY, Aakash Thakkar and Sagar
Thakrar supplied the conditional stock, time and fit distinctions. No novelty
is claimed for their formulas or the local-versus-recursive distinction.
