# Exact four-demand Boolean single-insertion cost

This contribution was produced by Nick Petalas. Apache-2.0.

With exactly four arbitrary dirty rows, a preserved source, and four nonzero
pairwise orthogonal Boolean demands, exactly one source insertion requires
**twelve ADDs**, and a literal word attains this bound. At common ADD price
c and insertion-row prices mu_i, the exact single-insertion cost is
`min_i(mu_i)+12c`.

The new finite quotient result is a sharp **six-ADD column minimum** over
F2^4. A complete edge-potential certificate excludes every shorter word.
A written finite-component reduction transfers it to every commutative unital
Boolean ring. Both sides of the insertion must pay this column cost because
all dirty inputs must return. The full proof and contract are in
[PROOF.md](PROOF.md).

Claim type: exact finite certificate with a scoped Boolean-ring lifting proof
and a written attaining identity. This is an abstract helper-restoration bill,
with no new kappa, physical supplier or complete multiplication theorem.

This is a self-posed four-row extension of lee-phys's
[#5514](https://github.com/CrocSwap/integer-mult-bounds/pull/5514).
That package settles a three-row price envelope and supplies the ideal and
prefix/suffix framework. Its result is cited, not replayed. The present result
adds a different exact row count, not a verification of the predecessor.
The twelve-ADD upper bound also specializes Ali Romman's
[#5310](https://github.com/CrocSwap/integer-mult-bounds/pull/5310) general
`4(k-1)` construction. The new contribution proves sharpness for these four
demands; the upper bound itself is credited prior work.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/four-orthogonal-one-insertion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/four-orthogonal-one-insertion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-orthogonal-one-insertion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-orthogonal-one-insertion --check-source-history
```

Another CPython 3.12 installation may replace the absolute interpreter path.
The direct verifier is read-only and imports no predecessor code. It prints
`PASS_FOUR_ORTHOGONAL_ONE_INSERTION` with computed counts and SHA256 bindings
to all six package files and the generated distance array. Both registered
commands have separate 120-second limits. Metadata and provenance validation
are separate from the mathematical certificate.

The optional `--write-distances PATH` argument exports the binary potential
certificate to an external scratch path after successful checks. Its 65,536
bytes are indexed by four packed row nibbles; invalid indices contain 255.
The default command writes no files.

## Evidence

The verifier constructs the 50,625 valid source-column states, then checks all
9,720,000 component-coordinate gate transitions, including no-ops. The potential
is zero at the start and six at the target, with change at most one along
every legal edge. This gives an all-word lower bound in the finite quotient,
not a search failure through an arbitrary cutoff.

The six-ADD column word and the full thirteen-gate dirty-restored word are
checked at every insertion root. Full formal endpoints retain the fifth,
unused complement atom. A separate binary interpreter checks every input on
each atom in both directions. Omitted-call, missing-restoration, complement
leak and corrupted-potential controls reject.

The generated receipt reports 2,750,592 nontrivial discovery transitions,
1,280 complete binary atom-input executions, 52 single-call omissions,
four missing-prefix controls, four complement-leak controls and three
certificate/boundary controls. Local CPython 3.12.15 on macOS arm64 passes
both warning-strict direct modes and both registered commands.

The normal and optimized commands must print identical generated receipts.
No human or formal proof-kernel review, predecessor scientific suite, selected
cold replay, Lean or Docker run is claimed. Hosted CI is separate from local
mathematical evidence.

## Scope and provenance

Base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
selected #7000. The card's baseline command passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; the contextual picker reports that the
catalogue's older assessment does not match the selected record. The
`bit-helper-contract` card explicitly changes scope to this abstract side
result. It does not claim to improve the selected G20 word or its signed moment.
See [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542445).
Entry overlap covered the live open-PR list, this account's recent contributions,
recent #1166 claims, active Discussions, cached card overlap and targeted merged
PR/main searches for Boolean fanout and single-insertion generalizations.
The sparse cached local search does not cover every retained note or unpublished
work. Targeted main searches used Git objects, including omitted package paths.
No novelty guarantee follows from a lack of matches.

Credit lee-phys #5514 and its #5304/#5259, Ali Romman, Krzysztof Wojt,
Ross Richardson and retained fanout lineage. Nick Petalas's older #5948 and
#6663 concern three-row problems and are related background. Their words,
construction and scientific code are not used as the main step here.

## Verification design

The verifier has no recursion. Its largest state spaces have exactly 65,536
indices and 50,625 queue slots; its edge scan has at most 65,536*12*16
iterations. Queue capacity and argument boundaries are checked explicitly,
and mathematical checks remain active under optimized Python. Functions stay
below sixty lines. Python allocation is a managed-runtime deviation from
static-allocation discipline; arrays have fixed capacities and all
other collections have sizes bounded by the four-row/five-atom domain. No
subprocess, network, callback dispatch or dynamic code generation is used.

## Limitations

There are exactly four dirty rows, no additional workspace and exactly one
nonzero source insertion. This does not determine the best multiple-insertion
program, arbitrary row/edge prices, restricted alphabets or non-Boolean rings.
The finite lower bound depends on executing the complete certificate checker.
The physical cost of coefficient masks, routing, frames, stock, precision,
owned storage and native realization is unknown. All five selected framework
assumptions remain; the selected frontier and frozen packages are unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can a human-readable invariant prove the same six-ADD column lower bound
  without the finite state certificate? First classify five-gate words by
  their ordered destination multiplicities. The finite result does not supply
  that structural classification.
- What changes with one extra arbitrary dirty spectator? First specify its
  restored source coefficient and determine whether it can shorten either
  column transfer. The four-row graph does not cover that larger domain.
- Can a physically realized helper split use this abstract bill? First bind
  one native producer and consumer, and price coefficient access, restoration,
  frames and every recursive target debit. No such interface is supplied here.
