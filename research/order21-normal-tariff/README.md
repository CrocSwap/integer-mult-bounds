# Exact order-21 normal-subgroup call tariff

Scoped algebraic proof with exact finite corroboration. No new kappa.
This contribution was produced by Nick Petalas. Apache-2.0.

In the full formal algebra F2[C7 semidirect C3], any w nonidentity
normal-C7 outputs require exactly w paid rank-one idempotent calls.
This holds for any finite number of arbitrary restored dirty registers
and with arbitrary free binary scalar mixing. In particular,

```text
diag([a], [a^2], [a^4], [a], 1, ..., 1)
```

costs exactly four calls. This settles the four-register question left
by Cinna Davis's [PR2011](https://github.com/CrocSwap/integer-mult-bounds/pull/2011).
Its three-register census is a cited predecessor and is not replayed.

[PROOF.md](PROOF.md) defines the complete model. Multiplication and
Frobenius on F8 give a three-dimensional binary representation. Every
nonidentity normal-C7 target contributes rank three to the endpoint
minus identity. A normal-C7 paid label contributes rank three, while
an outside label contributes rank two. Rank telescoping therefore gives

```text
3 * normal_calls + 2 * outside_calls >= 3 * target_count.
```

Coordinate calls attain the bound in the full formal algebra. Every
optimal word uses only normal-C7 labels. The lower bound is uniform
in target count, word length and restored workspace size. The finite
checks corroborate the proof; they do not replace its induction.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/order21-normal-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/order21-normal-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/order21-normal-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/order21-normal-tariff --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
The verifier prints `PASS_ORDER21_NORMAL_TARIFF` in a generated JSON
receipt bound to the SHA256 of all six package files. It writes no files.
There is no handwritten receipt. Local checks used CPython 3.12.15 on
macOS arm64. [VERIFY.json](VERIFY.json) registers the normal and optimized
warning-strict runs, each with a 60-second limit.

The verifier performs these exact checks:

- All 441 products in the new F8 representation, with represented
  difference ranks zero, three and two on identity, the six nonidentity
  normal labels and the fourteen outside labels respectively.
- All 12,320 paid factors on four and five roles. These are all 120 and
  496 binary rank-one idempotents respectively, at all twenty paid labels.
  Every represented difference has the proved rank.
- All 1,296 four-target exponent lists from {1,...,6}, each with one
  arbitrary dirty role, plus six larger witnesses at widths 5, 8 and 12,
  each with zero or two dirty roles. All 1,302 products equal their
  required endpoints coefficient by coefficient in the full formal algebra.
- One conjugated four-target witness mixes the dirty input through free
  scalar maps and restores the full operator. A separate 105-dimensional
  faithful regular-action execution agrees with the formal result.
- Ten controls reject four call omissions, either missing free scalar map,
  a changed dirty-role operator, a wrong target exponent, reversed
  Frobenius and an incorrect outside-label rank charge. All checks remain
  active under optimized Python.

The complete four-target formal stream is hashed in the generated receipt.
The predecessor's pair census and certificate numbers are not recomputed.
No selected operator replay, Lean or Docker run is needed for this theorem,
and none was run.

## Scope and provenance

The paid alphabet contains every nonidentity group label and every binary
rank-one idempotent. Its unit call price does not account for native
realization, routing, frames, precision, stock or recursive child costs.
Those physical obligations remain unknown. Mixed order-three target
profiles and nonuniform prices are outside the exact tariff. No supplier
admission, complete multiplication theorem or selected-frontier change
follows. Independent human and formal proof-kernel review are unclaimed.

[SOURCES.json](SOURCES.json) binds historical provenance at canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
The selected-record and task-card pins are historical. The verifier uses
no predecessor files or external libraries. [TASK.json](TASK.json)
records the scope change from bit-new-register-model to this formal
obstruction. The card's current generic baseline returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. The first scientific fixture was
the four-output endpoint above with one restored dirty role.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145540)
records the question. Live open PRs, recent handoffs, merged PR searches
and main README terms were checked. The overlap helper covered 315 open
PRs and 4,392 Discussion records with complete remote pagination. Its
sparse local search covered only 170 of 6,996 HEAD notes; targeted main
searches supplement it. These checks do not establish exhaustive novelty.

Build the Lever led to the rerunnable formal and represented checks.
Prove It Works led to full dirty-operator execution and omission controls.
Power of Ten kept the replay bounded and read-only. Every function is
below 60 lines, and no recursion, dynamic evaluation or subprocess is used.
Matrices have at most 128 rows, formal words at most twelve calls and
formal executions at most fourteen roles. The faithful regular replay has
five roles and 105 rows. Loops have bounds from these fixed domains.
Python allocation is a managed-runtime deviation from static allocation;
all live collections are bounded by these limits, and input files are
limited to one MiB each. Warning-strict normal and optimized execution
provide diagnostics. No separate static analyzer is installed.

## Open next questions

1. What is the exact tariff for mixed normal-C7 and outside order-three
   target profiles? Begin with one target of each type and combine this
   represented-rank budget with the quotient C3 character. The current
   rank budget does not by itself prove that their separate calls are
   optimal. A full formal attainment or stronger lower bound is needed.
2. Can a literal native producer and consumer implement these group
   labels at a useful complete cost? First fix their address action,
   ownership, routing and restoration contracts, then charge the whole
   boundary. No physical cost model is supplied here.

The structured questions are in [TASK.json](TASK.json).

## Credit

Cinna Davis's PR2011 supplies the group, formal alphabet, three-output
problem and explicit four-output question. Its retained register-model
lineage includes eumemic's PR288 and the original bit-model work.
Cinna Davis's [PR3893](https://github.com/CrocSwap/integer-mult-bounds/pull/3893)
provides the S3 example of representation-rank telescoping. Finite-field
multiplication, Frobenius and the rank inequality are classical. The new
claim is their uniform exact tariff for normal-subgroup targets in the
order-21 model, including arbitrary restored workspace and free scalar
mixing. Every predecessor retains its attribution; no predecessor file
or credit line is changed.
