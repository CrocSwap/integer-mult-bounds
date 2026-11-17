# Two rigid Jordan blocks have q squared coupled optima

This contribution was produced by Nick Petalas. Apache-2.0.

For the unchanged ordinary wrapper, fix

    P=diag(J_2(lambda_1),J_2(lambda_2)),   lambda_i^2=1.

Over any odd finite field F_q, there are exactly **q^2** optimal invertible
second maps Q. In characteristic two, Q=P is the unique optimum. This is a
scoped written proof with exact finite corroboration, with no new kappa.

Nicholas Stone's [#5556](https://github.com/CrocSwap/integer-mult-bounds/pull/5556)
proves that either block alone has only one optimum and leaves coupled
blocks open. The new count shows why multiplying individual counts fails.
Its fixed-wrapper error reduction and two-dimensional square-zero count
are cited inputs. No predecessor scientific verifier is replayed.

## Complete parameterization

In odd characteristic, all optima are exactly

    Q=P+U D S V,   S^2=0,
    U=[e_0 e_2],   V=[e_1^T; e_3^T],
    D=diag(2 lambda_1,2 lambda_2).

The q^2 square-zero matrices S give distinct Q. Every such Q has determinant
one; q^2-1 have rank(Q-P)=1. For example S=E_01 adds the single cross-block
entry Q_03=2 lambda_1 without changing either diagonal Jordan block.

[PROOF.md](PROOF.md) proves completeness by forcing the perturbation into
the rank-two image/kernel support, then reducing the remaining equality to
S^2=0. The determinant filter accepts every parameter, including mixed signs.
The minimum error rank is two in odd characteristic. Agreement with exact
interchange therefore holds on q^6 of q^8 inputs, rather than on every input.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/coupled-resonant-jordan-pair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/coupled-resonant-jordan-pair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/coupled-resonant-jordan-pair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/coupled-resonant-jordan-pair --check-source-history
```

Another CPython 3.12 path may replace the prefix. The direct marker is
`PASS_COUPLED_RESONANT_JORDAN_PAIR no_new_kappa`. Each run prints a generated
JSON receipt bound to SHA256 hashes of all six package files and writes no
files. There is no handwritten receipt or predecessor executable dependency.
[VERIFY.json](VERIFY.json) registers normal and optimized commands. Explicit
exceptions keep every acceptance check active with Python -O.

The verifier builds exact fields of orders 2,3,4,5,7,8,9,11,13 and checks
their field laws. It enumerates every four-entry perturbation in the forced
support for every resonant sign pair, compares the complete accepted set
with a separately enumerated square-zero catalogue, and runs all eight
original input basis columns of every accepted wrapper. It also enumerates
all 65,536 binary four-by-four second maps and executes the literal wrapper
on every invertible one. Rejection controls cover off-support entries,
non-square-zero couplings and misuse of the odd-characteristic count.
The extension fields use polynomial coordinates, not composite-modulus
integer arithmetic.

The finite totals are 27 field/sign contexts, 215,848 supported perturbations
and 1,819 accepted wrappers. The full binary census has 20,160 invertible
second maps and exactly one optimum. Together the literal replays check
175,832 original input basis columns. Fifteen rejection controls and one
coupled positive control pass. Normal and optimized local runs on CPython
3.12.15 produce identical receipts.

## Scope and credit

The `formal-interface-lemma` card has changed scope to this algebraic side
result. No selected assumption is discharged. Native implementation,
restoration, movement, precision, stock, compiler, complete supplier costs
and outer use remain unpriced. The selected #7000 frontier is unchanged.
No larger block family, complete multiplication theorem, independent human
review or formal proof-kernel acceptance is claimed. Lean, Docker, predecessor
scientific suites and the selected cold replay are unrun.

Credit Nicholas Stone / #5556 for the multiblock question, Jordan method,
wrapper reduction and two-dimensional square-zero count; Nick Petalas /
#5228 for the general equality characterization and #6406 for the distinct
regular J3 count; Jerry Chen / CubeJerry / #2950 for the wrapper optimum;
and the retained ordinary/native lineage. Classical block elimination and
finite-field counting are not claimed as new. [SOURCES.json](SOURCES.json)
pins predecessor prose, catalogue and selected record as historical provenance.
The direct verifier imports none of them.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539400)
records the question. Base is canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Entry checks
covered live open PRs, this account's recent work, recent handoffs and local
reservations, all 10,178 current note records, cached snapshots of 488 open
PRs and 7,148 Discussion records, and targeted main/merged searches. No
matching coupled resonant-pair count surfaced. Unpublished work and arbitrary
historical diffs remain coverage limits.

## Open next questions

- Count one pair with at least one eigenvalue squared different from one.
  First fix distinct regular eigenvalues over F5 and derive the new quotient
  and determinant filter. The present singular-support reduction does not
  classify that problem.
- Price one explicit coupled map in a physically specified ordinary caller.
  Its correctness domain, native coefficients and restoration costs must be
  supplied before optimal agreement can imply a useful implementation.

The structured questions are in [TASK.json](TASK.json). The first proved pair
ended the investigation.

## Verification constraints

The standalone verifier has no recursion, subprocesses, network calls or
external scientific imports. Its domains are fixed at q<=13 and matrix sizes
two, four or eight. Candidate scans stream at most 13^4 tuples per context;
accepted sets contain at most 169 tuples. The binary scan visits 2^16 matrices.
Every function is shorter than 60 physical lines. Exceptions enforce matrix,
field, rank and endpoint invariants in both interpreter modes.

Managed CPython allocation is a Power of Ten rule 3 deviation. Fixed domains
bound live collections; no fixed-allocation runtime is claimed. Rule 10 uses
warning-strict execution and AST compilation, plus the registered replay;
no separate static analyzer is configured. Revisit these bounds before
accepting variable fields or dimensions. No shared implementation is changed.
