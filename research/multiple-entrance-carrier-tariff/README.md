# Exact price of a carrier visiting several entrance lines

This contribution was produced by Nick Petalas. Apache-2.0.

A scoped proof determines the exact paid transport tariff for one carrier
starting at zero, visiting m distinct prescribed entrance lines, and ending at
a destination C of dimension c. For every nonnegative, nondecreasing subadditive
rank tariff H with H(0)=0, the minimum for m>0 is

```
H(1) + (m-1) H(2) + H(c-1), if a required line lies in C;
H(1) + (m-1) H(2) + H(c+1), otherwise.
```

With no required lines it is H(c). In particular, two distinct entrance lines
inside C require c+2 rank units, rather than the original c. Arbitrary
intermediate frames and repeated visits cannot lower this price. The theorem
holds over every field and includes every power tariff H(r)=r^s, 0<s<=1.

[PROOF.md](PROOF.md) states the complete subspace-distance transport contract
and proves the result. This supplies a sharp obstruction to combining
shared-carrier input lifts at different entrance lines. It does not establish
the sign of a complete supplier invoice or a new kappa.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/multiple-entrance-carrier-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/multiple-entrance-carrier-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/multiple-entrance-carrier-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/multiple-entrance-carrier-tariff --check-source-history
```

Replace the interpreter path with any CPython 3.12 installation elsewhere.
The verifier is read-only. `--emit` prints a freshly computed receipt bound
to package-file hashes. No receipt is hand-written or assumed as a premise.
[VALIDATION.md](VALIDATION.md) records the local evidence and implementation
limits. Hosted CI is separate.

## Scope and credit

Claim type: scoped algebraic/metric proof with exact finite corroboration.
The full graph permits every subspace transition at its declared metric rank.
A restricted native grammar inherits a lower bound only after establishing
that its transitions cost at least this metric. Attainment in that grammar,
scalar response delivery, dirty restoration, native phases, target debits,
compiler closure, precision/tape and analytic recovery remain unproved.
No complete multiplication theorem or selected-frontier change is claimed.

DreamingOfClouds' [PR6375](https://github.com/CrocSwap/integer-mult-bounds/pull/6375)
supplies the shared-carrier construction and the extension question.
Ali Romman's [PR6349](https://github.com/CrocSwap/integer-mult-bounds/pull/6349)
supplies native input lifting, retaining the P104 and query-caller lineage.
The subspace distance and one-detour bound are credited to DreamingOfClouds'
[format-limits-corrected, section C.2](../format-limits-corrected/README.md).
Those source results are cited premises; their verifiers are not imported or
replayed. No originality is claimed for the metric or shortcut principle.
The new result is the exact tariff with multiple required entrance lines.
Independent human and formal proof-kernel review are unclaimed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358883)
records the scope. Main and merged-PR searches found the credited single-detour
result and shared-input constructions. The overlap cache and live claims were
also consulted. These searches do not cover unpublished work or guarantee
literature priority.

## Open next questions

- Can different response groups be changed to use a common entrance line?
  Start with two exact response maps and charge every basis correction and
  target debit. No changed response or complete supplier bill is supplied here.
- Can the actual native chart grammar attain the metric price between two
  prescribed entrance lines? Start with one pinned carrier and compile all
  operator columns, phases and restoration. Physical applicability is open.
