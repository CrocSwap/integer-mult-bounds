# Compatible port flags cannot improve scalar fitting rank

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For every field K, directed zero mask Z, payload width d and prescribed
complete flag at each port, the exact minimum block fitting rank is

```text
min rank_K M = d mu_K(Z),
M_ii = I_d,  M_ij = 0 on Z,
M_ij(F_j^a) is contained in F_i^a for every i,j,a.
```

Here mu_K(Z) is the minimum scalar fitting rank for the same directed mask.
The flags may differ between ports; the blocks may be noncommuting,
nonsymmetric and nondiagonalizable. [PROOF.md](PROOF.md) gives the universal
lower bound and an attainer for every prescribed family of flags. A query
factorization through r field coordinates therefore requires r>=d mu_K(Z).

This adds a sharp exclusion to the operator-valued decoder direction.
Noncommutation alone cannot lower normalized fitting rank if compatible
flags remain. Commuting complex blocks have a common complete flag and
are included. A flag supplied only over an extension L gives the scalar
minimum over L, not automatically the minimum over K. Arbitrary
flag-breaking block fits remain open.

The block-rank and triangularization ingredients are classical. The new
step is their exact arbitrary-mask application with port-dependent flags
to this repository's decoder interface. Global literature priority is
unclaimed. The retained C5 block advantage is a hypothesis-boundary
control, not a new result or a predecessor audit.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -B research/compatible-flag-fitting-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -O -B research/compatible-flag-fitting-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/compatible-flag-fitting-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/compatible-flag-fitting-rank --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. The direct
verifier is read-only and Git-free. It generates a seven-file SHA256 receipt
on stdout, with `PASS_COMPATIBLE_FLAG_FITTING_RANK`. No hand-written receipt
or external executable is used. Normal and optimized checks use explicit
runtime guards, with warnings treated as errors.

The finite domain contains all 64 directed three-port masks over F2, and
all 531,441 mask/matrix cases with width two and upper triangular blocks.
The 729 scalar fitting cases establish each mask's actual scalar minimum;
every corresponding block minimum equals twice that minimum. All cases
also satisfy the stronger lower bound from the two scalar diagonal layers.
An independent complete row-image oracle checks all 512 binary 3-by-3
matrices and 127 selected full block matrices.

There are 90 additional charted attainers and upper-triangular extensions
over F2,F3,F5, widths 2,3,4 and five directed masks. Thirty of the 45
extensions have strictly higher rank than the optimum, illustrating that
upper-diagonal coupling can increase rank. Two further sharp examples
cover noncommuting blocks and distinct local flags with no single common
binary flag in raw coordinates. The classical C5 rank-five fixture rejects
all 243 local binary flag tuples. Nine explicit domain/semantic controls
reject bad diagonal, forbidden block, incompatible flag, singular chart,
unsupported field, invalid mask, matrix shape, chart size and capacity.
Counts are enumerated by the checker. Finite checks corroborate the written
proof rather than establish its unbounded quantifiers.

## Scope and credit

The `complex-rank-shape-decoder` card changes to a scoped algebraic boundary
result. It does not supply the card's complete native itinerary or paid
signed invoice. The first selected-source orientation command passed as
metadata only. No selected scientific replay was run. The selected frontier
and its five framework assumptions remain unchanged.

Credit ywz65 / [PR2541](https://github.com/CrocSwap/integer-mult-bounds/pull/2541)
for the strict block-fitting interface and its particular-mask 49d theorem;
Aaron Wang / navinor [PR825](https://github.com/CrocSwap/integer-mult-bounds/pull/825)
for the different framed-circuit common-flag obstruction; and Cinna Davis's
[field-line repair](../kappa01-fieldline-repair/README.md) for the scalar
query-rank bound and open operator-valued boundary. The present theorem
conditionally transfers that cited scalar bound to compatible-flag block
fits; its original proof, quantities and invoice are not rechecked.
The retained geometry/native lineages keep their credit. Bukh, Cox and
Blasiak retain the classical fractional Haemers framework, with a primary
source linked in the proof. No predecessor program or receipt is imported.

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. [SOURCES.json](SOURCES.json) pins source texts as historical
provenance; there are no external live inputs. [TASK.json](TASK.json)
records the changed scope, overlap coverage and remaining obligations.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362968)
reserved the original question. Research stopped after the first proved
and checked step, without extending to a new mechanism.

There is no efficient scalar-minimum or flag-finding algorithm, unequal
payload theorem, arbitrary flag-breaking lower bound, native implementation,
physical caller, complete paid invoice, supplier admission, new kappa or
complete multiplication theorem here. Human and formal proof-kernel review
are unclaimed. Lean, Docker and historical scientific suites were not run.

## Open next questions

Can a useful changed decoder break every compatible port-flag system and
still win after its physical costs? Start with a literal small completed
fitting matrix and its query factorization, then price source access,
payload volume, native charts and restoration. The theorem says that
noncommutation alone is insufficient; absence of a supplied flag is not
a proof that no compatible flags exist. A favorable native caller and
complete invoice remain blockers. The structured version is in TASK.json.

## Verifier constraints

The two Python modules have nonrecursive control flow, bounded domains and
functions below 60 physical lines. Matrices are at most 12-by-12 in the
main finite checks and 10-by-10 in the C5 boundary. Guards cap generic
matrix helpers at 20-by-20, chart width four, port count five, and fields
2,3,5. Binary image enumeration has at most 1,024 values. Each scalar
optimum search has at most 5^6 assignments, and the largest block search
has 8^6 assignments. Seven package file reads are each capped at 128 KiB.
One explicit package-local module import supports isolated Python mode;
there are no subprocesses, network requests or output-file writes.

Power of Ten rule 3 deviation: CPython allocates managed integers and
containers during this one-shot replay. The fixed input domains, finite
loop bounds and sequential census keep live state bounded; no census
matrix collection is retained. Rule 9 deviation: standard finite iterator
and JSON/path operations use Python runtime dispatch, with fixed argument
types and package-local targets. Both warning-strict registered modes and
static syntax/function-size inspection exercise the scoped implementation.
Larger inputs or a service implementation require a fresh resource review.
